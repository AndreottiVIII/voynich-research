# -*- coding: utf-8 -*-
"""Supporto di ia21 (modulo, non e' un esperimento): l'ALLIEVO, cioe' il generatore che si allena a giri.

L'allievo predefinito e' la GRU 2 x 256 di ia07 (pieghe per foglio, stessa disposizione, stesse teste di pagina e di riga, stesse
regole di scrittura). Qui ci sono:
  - `AllievoGRU`: carica il modello di una piega, scrive pagine (in parallelo, piu' copie della stessa pagina), si rifinisce su
    pagine date (vere e scelte, con un peso per pagina), calcola i bit per segno su pagine vere, si salva e si ricarica;
  - `scrittore_pagine`: la scrittura a lotto (stesse regole di `ia07.Penna`, campionamento ordinario a temperatura 1 con numpy);
  - le funzioni che trasformano una pagina scritta in sequenza di addestramento, tenendo le teste (tipo di riga, posizione, fascia
    di lunghezza) della disposizione vera con cui e' stata scritta.

CONTRATTO DELL'ALLIEVO (per usare un altro modello di partenza, per esempio quello di ia20: `MODELLO_PARTENZA=modulo:funzione`; la
funzione `funzione(piega, replica)` deve restituire un oggetto con questi metodi; tutto il resto di ia21 usa solo questi):
    scrivi_pagine(nomi, B, seme) -> {nome pagina: [righe_0, ..., righe_{B-1}]}   con righe = [(inizio_paragrafo, [parola, ...]), ...]
        (stessa disposizione della pagina vera `nome`; B copie indipendenti, deterministiche dato il seme)
    affina(vere, scelte, peso_scelte, epoche, lr, seme) -> dict di numeri
        vere = nomi di pagine vere su cui rifinirsi (fogli di addestramento della piega, mai quelli tenuti fuori);
        scelte = [(nome pagina, righe)] pagine scritte da lui stesso e scelte, con peso `peso_scelte` rispetto alle vere (1.0)
    bpc(nomi) -> bit per segno sulle pagine vere (validazione)
    salva(percorso)   e   Classe.da_file(percorso, piega)
    parametri (numero)
Il modulo che offre `funzione` deve funzionare anche con SOLO_CONTROLLI=1 se si vogliono i controlli; altrimenti i controlli partono
dalla GRU.
Nessun risultato e' scritto qui e nessuna parola del manoscritto compare in questo file.
"""
import copy
import math
import os
import sys
import time
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402


# ---------------------------------------------------------------- segni ammessi, con memoria

class Ammessi:
    """Gli stessi segni ammessi di `I7.Penna.ammessi`, ma con una cache: dipende dallo stato (inizio di riga o dopo uno spazio / riga
    troppo lunga / dentro la parola) e, dentro la parola, solo dalle ultime tre unita' (un segno puo' fondersi solo con le ultime).
    L'equivalenza con la versione di ia07 e' controllata nelle prove (`controlla_ammessi`)."""

    def __init__(self, penna):
        self.p = penna
        self.cache = {}
        self.A0 = np.array(penna.senza_sp, dtype=np.int64)
        self.A1 = np.array([penna.EOL], dtype=np.int64)

    def get(self, parola, lung, prima):
        if prima in ('inizio', 'spazio'):
            return self.A0
        if lung >= self.p.voc['lmax']:
            return self.A1
        k = tuple(parola[-3:])
        a = self.cache.get(k)
        if a is None:
            # la versione di ia07 sull'ultima parte della parola: stesse regole, stessi segni
            a = self.cache[k] = np.array(self.p.ammessi(list(k), 0, 'segno'), dtype=np.int64)
        return a


def controlla_ammessi(n=2000, seme=1):
    """Prova: su passeggiate a caso, `Ammessi` ridà esattamente gli insiemi di `Penna.ammessi` (parola intera). Restituisce il numero
    di casi diversi (deve essere 0)."""
    import random
    voc = I7.vocabolario()
    penna = I7.Penna(None, voc)
    ca = Ammessi(penna)
    rnd = random.Random(seme)
    diversi = 0
    for _ in range(n):
        parola, lung, prima = [], 0, 'inizio'
        for _ in range(rnd.randint(1, 14)):
            a = ca.get(parola, lung, prima)
            b = penna.ammessi(parola, lung, prima)
            if list(a) != list(b):
                diversi += 1
            s = rnd.choice(list(b))
            if s in (penna.SP, penna.EOL):
                break
            parola.append(penna.unita[s])
            lung += 1
            prima = 'segno'
    return diversi


# ---------------------------------------------------------------- scrivere pagine a lotto

def _pagina_a_lotto(rete, rp, B, rng, voc, D, ca, registra=None):
    """Scrive B copie indipendenti della pagina con la disposizione `rp` (righe vere della pagina). Come `I7.percorri_pagina` (stesse
    teste, stesse regole), ma le B copie avanzano insieme nella rete; chi ha finito la riga aspetta (il suo stato non si muove).
    `registra`: lista di B numeri a cui si somma il log della probabilita' (ristretta ai segni ammessi) del segno scelto (prove)."""
    import torch
    penna = ca.p
    SP, EOL = penna.SP, penna.EOL
    stato = [None]

    def avanza(toks, attivi=None):
        x = torch.tensor(toks, dtype=torch.long).view(B, 1)
        logit, h2 = rete(x, stato[0])
        if attivi is not None and stato[0] is not None and not all(attivi):
            h2 = torch.where(torch.tensor(attivi).view(1, B, 1), h2, stato[0])
        stato[0] = h2
        return logit[:, -1, :].numpy()

    with torch.inference_mode():
        for t in I7.testa_pagina(rp, voc):
            lg = avanza([t] * B)
        uscita = [[] for _ in range(B)]
        for j, x in enumerate(rp):
            for t in I7.testa_riga(x, j, voc, D):
                lg = avanza([t] * B)
            parola = [[] for _ in range(B)]
            parole = [[] for _ in range(B)]
            lung = [0] * B
            prima = ['inizio'] * B
            attivi = [True] * B
            while any(attivi):
                toks = [0] * B
                fine = []
                for b in range(B):
                    if not attivi[b]:
                        continue
                    a = ca.get(parola[b], lung[b], prima[b])
                    z = lg[b][a].astype(np.float64)
                    z -= z.max()
                    e = np.exp(z)
                    c = np.cumsum(e)
                    i = int(np.searchsorted(c, rng.random() * c[-1], side='right'))
                    if i >= len(a):
                        i = len(a) - 1
                    s = int(a[i])
                    if registra is not None:
                        registra[b] += math.log(e[i] / c[-1])
                    toks[b] = s
                    if s == EOL:
                        parole[b].append(''.join(parola[b]))
                        fine.append(b)
                    else:
                        lung[b] += 1
                        if s == SP:
                            parole[b].append(''.join(parola[b]))
                            parola[b], prima[b] = [], 'spazio'
                        else:
                            parola[b].append(penna.unita[s])
                            prima[b] = 'segno'
                lg = avanza(toks, list(attivi))
                for b in fine:
                    attivi[b] = False
            for b in range(B):
                uscita[b].append((x['ini'], parole[b]))
    return uscita


def scrittore_pagine(rete, nomi, B, seme, registra=None):
    """{nome pagina: [righe_0 ... righe_{B-1}]} con righe = [(inizio_paragrafo, [parole])]. Deterministico dato il seme (un solo thread)."""
    import torch
    voc, D = I7.vocabolario(), I7.divisore()
    pp = I7.per_pagina(I7.libro_vero())
    penna = I7.Penna(None, voc)
    ca = Ammessi(penna)
    rng = np.random.default_rng(seme)
    rete.eval()
    out = OrderedDict()
    for nome in nomi:
        reg = [0.0] * B if registra is not None else None
        out[nome] = _pagina_a_lotto(rete, pp[nome], B, rng, voc, D, ca, reg)
        if registra is not None:
            registra[nome] = reg
    return out


# ---------------------------------------------------------------- sequenze di addestramento

def sequenza_vera(nome):
    voc, D = I7.vocabolario(), I7.divisore()
    return I7.sequenza(I7.per_pagina(I7.libro_vero())[nome], voc, D)


def sequenza_scritta(nome, righe):
    """La pagina scritta come sequenza di addestramento: teste di pagina e di riga della disposizione vera con cui e' stata scritta
    (non ricalcolate dalle righe scritte), poi i segni scritti e la fine riga."""
    voc, D = I7.vocabolario(), I7.divisore()
    i = voc['idx']
    rp = I7.per_pagina(I7.libro_vero())[nome]
    seq = I7.testa_pagina(rp, voc)
    for j, x in enumerate(rp):
        seq += I7.testa_riga(x, j, voc, D)
        for k, w in enumerate(righe[j][1]):
            if k:
                seq.append(i[' '])
            seq += [i[u] for u in D(w)]
        seq.append(i['\n'])
    return seq


# ---------------------------------------------------------------- l'allievo

class AllievoGRU:
    nome = 'gru'

    def __init__(self, piega, rete, info=None):
        self.piega, self.rete, self.info = piega, rete, dict(info or {})

    @property
    def parametri(self):
        return sum(p.numel() for p in self.rete.parameters())

    @classmethod
    def da_file(cls, percorso, piega):
        import torch
        d = torch.load(percorso, weights_only=False)
        voc = I7.vocabolario()
        assert d['segni'] == voc['segni'], 'vocabolario diverso da quello del modello'
        m = I7.costruisci_rete(len(voc['segni']), d['strati'], d['nascosto'])
        m.load_state_dict(d['stato'])
        m.eval()
        return cls(piega, m, d.get('info'))

    @classmethod
    def da_partenza(cls, piega, replica=0):
        """Il modello di ia07 della piega (cartella `I7.MODELLI`): per il Voynich quelli gia' fatti, per i controlli quelli addestrati da ia21."""
        return cls.da_file(I7.percorso_modello(I7.nome_modello(piega, replica), '.pt'), piega)

    def salva(self, percorso):
        import torch
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        voc = I7.vocabolario()
        torch.save(dict(stato=self.rete.state_dict(), segni=voc['segni'], strati=self.rete.gru.num_layers, nascosto=self.rete.gru.hidden_size,
                        info=self.info), percorso + '.tmp')
        os.replace(percorso + '.tmp', percorso)

    def copia(self):
        return AllievoGRU(self.piega, copy.deepcopy(self.rete), self.info)

    # -- scrivere
    def scrivi_pagine(self, nomi, B, seme):
        return scrittore_pagine(self.rete, nomi, B, seme)

    # -- misurare
    def bpc(self, nomi):
        voc = I7.vocabolario()
        return float(I7.bpc(self.rete, [sequenza_vera(n) for n in nomi], voc['primo_contenuto']))

    # -- rifinirsi
    def affina(self, vere, scelte, peso_scelte, epoche, lr, seme):
        """Rifinitura: `epoche` passate su (pagine vere con peso 1) + (pagine scelte con peso `peso_scelte`). Lotti di LOTTO pagine
        intere, retropropagazione a tratti di TRONCO segni (lo stato passa al tratto dopo), AdamW (passo `lr`, decadimento di ia07,
        taglio del gradiente 1,0), perdita solo sui segni da indovinare, pesata per pagina. Stato dell'ottimizzatore nuovo a ogni chiamata."""
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
        inizio = time.time()
        voc = I7.vocabolario()
        primo, V = voc['primo_contenuto'], len(voc['segni'])
        dati = [(sequenza_vera(n), 1.0) for n in vere] + [(sequenza_scritta(n, r), float(peso_scelte)) for n, r in scelte]
        torch.manual_seed(seme)
        rng = np.random.default_rng(seme)
        m = self.rete
        m.train()
        opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=I7.DECADIMENTO)
        perdite = []
        for _ in range(epoche):
            chiavi = [len(s) * (1 + 0.3 * u) for (s, _), u in zip(dati, rng.uniform(size=len(dati)))]
            ordine = sorted(range(len(dati)), key=lambda i: chiavi[i])
            lotti = [ordine[a:a + I7.LOTTO] for a in range(0, len(ordine), I7.LOTTO)]
            rng.shuffle(lotti)
            tot, conti = 0.0, 0.0
            for lotto in lotti:
                X, Y, M = I7._tensori([dati[i][0] for i in lotto], primo)
                W = torch.tensor([dati[i][1] for i in lotto], dtype=torch.float32).view(-1, 1)
                h = None
                for t0 in range(0, X.shape[1], I7.TRONCO):
                    x, y, mk = X[:, t0:t0 + I7.TRONCO], Y[:, t0:t0 + I7.TRONCO], M[:, t0:t0 + I7.TRONCO]
                    logit, h = m(x, h)
                    h = h.detach()
                    mw = mk * W
                    if float(mw.sum()) == 0:
                        continue
                    ce = F.cross_entropy(logit.reshape(-1, V), y.reshape(-1), reduction='none')
                    loss = (ce * mw.reshape(-1)).sum() / mw.sum()
                    opt.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(m.parameters(), I7.TAGLIO)
                    opt.step()
                    tot += loss.item() * float(mw.sum())
                    conti += float(mw.sum())
            perdite.append(round(tot / max(conti, 1.0) / math.log(2), 5))
        m.eval()
        return OrderedDict([('pagine_vere', len(vere)), ('pagine_scelte', len(scelte)), ('perdita_bit', perdite), ('secondi', round(time.time() - inizio, 1))])


def allievo_di_partenza(piega, replica=0):
    return AllievoGRU.da_partenza(piega, replica)
