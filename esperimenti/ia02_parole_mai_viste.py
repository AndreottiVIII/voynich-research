# -*- coding: utf-8 -*-
"""Esperimento IA2 (ia02): quanto costa a una rete minuscola una parola che non ha mai visto in addestramento, rispetto a
una già vista. È la prova diretta del "niente da memorizzare" di e3c95.

Stesso modello, stessi testi, stessi semi e stesse divisioni di e3c95 (si importa e3c95_imparabilita, che non si
modifica): GRU a caratteri con 128 unità, 40.000 segni di addestramento, 5.000 di validazione, 10.000 di prova,
arresto anticipato sulla validazione. La traiettoria dell'addestramento è identica a quella di e3c95 (stessi semi, stesso
ordine dei numeri casuali); qui in più si tiene il modello del punto scelto (validazione più bassa) e si misurano:

1. COSTO DELLE PAROLE SULLA PROVA. Una parola è una sequenza di segni fra due separatori (spazio o a capo). Il suo costo
   è la somma dei bit dei suoi segni più il bit del separatore che la chiude, con il contesto portato dall'inizio della
   prova (come in e3c95). Parola "vista" se compare nell'addestramento, "mai vista" altrimenti. Si escludono: le parole
   con il segno raro ¤ (non si sa se sono uguali), la prima parola della prova (non ha il contesto) e l'ultima se
   tagliata dal bordo della prova.
   R = media, pesata sul numero di parole mai viste, dei rapporti (costo medio delle mai viste / costo medio delle viste)
   per ogni lunghezza in segni, solo per le lunghezze con almeno 10 parole viste. Se ne riporta la copertura.
2. RIFERIMENTO SENZA MEMORIA DI PAROLE: un modello a trigrammi di segni (due segni di contesto, lisciatura di
   Witten-Bell) addestrato sullo stesso addestramento; non può imparare parole intere a memoria. Stesse misure.
   R_rel = R(rete) / R(trigrammi): quanto la rete paga in più della semplice selezione "le parole viste sono quelle
   probabili".
3. PAROLE INVENTATE. Dalla rete (e dai due modelli di riferimento: unigrammi di segni e trigrammi) si campionano 1.000
   flussi di 400 segni, partendo dallo stato zero con un a capo in ingresso; di ogni flusso si scarta la prima parola e
   si tengono le 20 successive (20.000 parole). Si contano: la quota di parole nuove (non presenti nell'addestramento) e,
   fra le nuove, la quota che compare nella parte di testo non usata per l'addestramento (validazione + prova).

Preregistrazione: preregistrazioni/ia02.md. Scrive risultati/ia02_parole_mai_viste.json e .md e, una riga per corsa,
risultati/ia02_corse.jsonl (con RIPRENDI=1 le corse già fatte non si rifanno).
SOLO_CONTROLLI=1: solo testi che non sono il Voynich né imitazioni in EVA, per provare il codice. Variabili per le prove:
quelle di e3c95 (PASSI, SEMI, ...), TESTI (sottostringhe separate da |, "=Nome" per il nome esatto), USCITA. PROCESSI:
numero di processi in parallelo (non cambia i risultati).
"""
import json, math, os, random, statistics, sys, time
from collections import OrderedDict, Counter
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c95_imparabilita as e95

NOME = 'ia02_parole_mai_viste'
USCITA = e95.USCITA
MIN_VISTE = 10          # parole viste minime in una lunghezza perché il suo rapporto conti
FLUSSI = 1000           # parole inventate: flussi di segni (1.000 flussi x 20 parole = 20.000 parole per modello)
SEGNI_FLUSSO = 400      # segni per flusso
PAROLE_FLUSSO = 20      # parole tenute per flusso (dopo aver scartato la prima)
SEGNI_SINTETICI = 110000
SEME_SINTETICI = 97
LESSICO = 3000
# soglie dei controlli (fissate dopo le prove del codice; vedi la preregistrazione)
SOGLIA_POSITIVO = 1.10   # R_rel di C+ al massimo 1,10 (media dei semi)

C_POS = 'C+ solo regole (catena di Markov di ordine 2 sul latino)'
C_POS2 = 'C+2 solo regole di posizione (prefisso, corpo, suffisso)'
C_NEG = 'C- solo memoria (lessico casuale di 3.000 parole)'
RUOLI = ('voynich', 'lingua', 'generatore')


# ---------------------------------------------------------------- controlli sintetici

def _righe(blocchi):
    return [r for b in blocchi for r in b]


def testo_regole(latino, rnd):
    """C+: le parole si estraggono una per una da una catena di Markov di caratteri di ordine 2 stimata sulle parole del
    latino (occorrenze, non tipi); righe con le lunghezze (in parole) delle righe del latino. Nessuna parola intera è
    memorizzata nel testo: ogni parola nasce dalle regole di due segni di contesto."""
    righe = _righe(latino)
    cont = {}
    for r in righe:
        for w in r:
            h = (None, None)
            for s in tuple(w) + (None,):
                cont.setdefault(h, Counter())[s] += 1
                h = (h[1], s)
    tab = {}
    for h, c in cont.items():
        chiavi = sorted(c, key=lambda s: (s is None, s or ''))
        tab[h] = (chiavi, [c[k] for k in chiavi])
    lung = [len(r) for r in righe]

    def parola():
        while True:
            h, w = (None, None), []
            while len(w) <= 30:
                chiavi, pesi = tab[h]
                s = rnd.choices(chiavi, weights=pesi)[0]
                if s is None:
                    break
                w.append(s)
                h = (h[1], s)
            if 1 <= len(w) <= 30 and s is None:
                return tuple(w)
    return _blocchi_sintetici(rnd, parola, lung), tab


def testo_posizioni(latino, rnd):
    """C+2 (controllo "solo regole" più duro): ogni parola è composta da posizioni, prefisso + corpo + suffisso, scelti
    indipendentemente da piccoli inventari (8 prefissi, 12 unità di corpo, 8 suffissi, di 1-2 segni tra i 14 più frequenti
    del latino; prefisso e suffisso possono mancare); il corpo ha da 1 a 4 unità. Le regole sono di posizione e di ordine
    più alto dei due segni di C+, e nessuna parola intera è memorizzata. Righe con le lunghezze (in parole) delle righe del
    latino."""
    righe = _righe(latino)
    segni = [s for s, _ in Counter(s for r in righe for w in r for s in w).most_common(14)]

    def inventario(n, lmin, lmax):
        inv = set()
        while len(inv) < n:
            inv.add(tuple(rnd.choices(segni, k=rnd.randint(lmin, lmax))))
        return sorted(inv)
    zipf = lambda n, e: [1.0 / (i + 1) ** e for i in range(n)]
    pref, pesi_p = [()] + inventario(7, 1, 2), [0.35] + [0.65 * x / sum(zipf(7, 1)) for x in zipf(7, 1)]
    corpo, pesi_c = inventario(12, 1, 2), zipf(12, 0.8)
    suff, pesi_s = [()] + inventario(7, 1, 2), [0.30] + [0.70 * x / sum(zipf(7, 1)) for x in zipf(7, 1)]
    lung = [len(r) for r in righe]

    def parola():
        w = rnd.choices(pref, weights=pesi_p)[0]
        for _ in range(rnd.choices([1, 2, 3, 4], weights=[0.20, 0.35, 0.30, 0.15])[0]):
            w = w + rnd.choices(corpo, weights=pesi_c)[0]
        return w + rnd.choices(suff, weights=pesi_s)[0]
    return _blocchi_sintetici(rnd, parola, lung)


def costo_catena(parola, tab):
    """Bit di una parola (con la fine) sotto la catena di C+; per le prove del codice."""
    h, bit = (None, None), 0.0
    for s in tuple(parola) + (None,):
        chiavi, pesi = tab[h]
        bit -= math.log2(pesi[chiavi.index(s)] / sum(pesi))
        h = (h[1], s)
    return bit


def testo_memoria(latino, rnd):
    """C-: un lessico di 3.000 stringhe casuali (lunghezze come i tipi del latino, segni indipendenti con le
    frequenze del latino); le parole si estraggono una per una con frequenze di Zipf (1/rango); righe con le lunghezze
    delle righe del latino. Nessuna regola dentro le parole: solo lessico."""
    righe = _righe(latino)
    tipi = sorted({tuple(w) for r in righe for w in r})
    lunghezze = [len(w) for w in tipi]
    freq = Counter(s for r in righe for w in r for s in w)
    segni = sorted(freq)
    pesi_s = [freq[s] for s in segni]
    lessico, visti = [], set()
    while len(lessico) < LESSICO:
        w = tuple(rnd.choices(segni, weights=pesi_s, k=rnd.choice(lunghezze)))
        if w not in visti:
            visti.add(w)
            lessico.append(w)
    zipf = [1.0 / (i + 1) for i in range(LESSICO)]
    cum = []
    tot = 0.0
    for x in zipf:
        tot += x
        cum.append(tot)
    lung = [len(r) for r in righe]
    return _blocchi_sintetici(rnd, lambda: rnd.choices(lessico, cum_weights=cum)[0], lung)


def _blocchi_sintetici(rnd, parola, lung):
    righe, n = [], 0
    while n < SEGNI_SINTETICI:
        r = [parola() for _ in range(rnd.choice(lung))]
        righe.append(r)
        n += sum(len(w) for w in r) + len(r)
    return e95.blocchi_di(righe)


# ---------------------------------------------------------------- catalogo e lavori

def catalogo():
    """(tutti i testi di e3c95, più i tre controlli sintetici; solo quelli di questo esperimento). Il catalogo di e3c95 si legge
    senza il filtro TESTI, perché l'alfabeto di un gruppo dipende da tutti i suoi membri (come in e3c95)."""
    filtro_env = os.environ.pop('TESTI', None)
    try:
        t = e95.catalogo()
    finally:
        if filtro_env is not None:
            os.environ['TESTI'] = filtro_env
    latino = t['Latin']['blocchi']
    bl, _ = testo_regole(latino, random.Random(SEME_SINTETICI))
    t[C_POS] = dict(blocchi=bl, ruolo='controllo', gruppo=C_POS, trasforma=None)
    t[C_NEG] = dict(blocchi=testo_memoria(latino, random.Random(SEME_SINTETICI + 1)), ruolo='controllo',
                    gruppo=C_NEG, trasforma=None)
    t[C_POS2] = dict(blocchi=testo_posizioni(latino, random.Random(SEME_SINTETICI + 2)), ruolo='controllo',
                     gruppo=C_POS2, trasforma=None)
    scelti = OrderedDict((k, v) for k, v in t.items() if v['ruolo'] in RUOLI or k in (C_POS, C_POS2, C_NEG))
    filtro = [s for s in os.environ.get('TESTI', '').split('|') if s]
    if filtro:
        scelti = OrderedDict((k, v) for k, v in scelti.items()
                             if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro))
    return t, scelti


def prepara(t, scelti):
    """Come e3c95_imparabilita.prepara (stessi alfabeti, stesse divisioni), ma solo per i testi scelti, e con il
    vocabolario dei segni nel lavoro."""
    alfabeti = {}
    for g in {v['gruppo'] for v in t.values()}:
        membri = [v for v in t.values() if v['gruppo'] == g]
        esplicito = [v['alfabeto'] for v in membri if v.get('alfabeto')]
        alfabeti[g] = esplicito[0] if esplicito else e95.frequenti([v['blocchi'] for v in membri])
    lavori, scarti = [], []
    for nome, v in scelti.items():
        voc = sorted(alfabeti[v['gruppo']] | {' ', '\n', e95.RARO})
        idx = {s: i for i, s in enumerate(voc)}
        parti = []
        for seme in e95.SEMI:
            d = e95.dividi_blocchi(v['blocchi'], seme)
            if d is None:
                scarti.append(nome)
                parti = None
                break
            parti.append((seme, tuple([idx.get(s, idx[e95.RARO]) for s in e95.flusso(x)[:q]]
                                      for x, q in zip(d, (e95.N_ADD, e95.N_VAL, e95.N_PROVA)))))
        if parti is None:
            continue
        for seme, (add, val, prova) in parti:
            lavori.append(dict(testo=nome, seme=seme, V=len(voc), voc=voc, add=add, val=val, prova=prova))
    return lavori, scarti


# ---------------------------------------------------------------- parole

def parole_di(seq, delim):
    """Parole complete di un flusso: (inizio, fine) con il separatore di chiusura in posizione fine. L'ultima parola,
    se non è chiusa da un separatore, non c'è."""
    out, s = [], None
    for i, x in enumerate(seq):
        if x in delim:
            if s is not None:
                out.append((s, i))
                s = None
        elif s is None:
            s = i
    return out


def tabella_lunghezze(seq, bit, vocabolario, delim, raro):
    """{lunghezza: [n viste, bit viste, n mai viste, bit mai viste]} sulle parole della prova; bit[j] è il costo del
    segno j+1 (il primo segno della prova non ha costo)."""
    tab, n_raro, n_tot = {}, 0, 0
    for s, i in parole_di(seq, delim):
        if s == 0:
            continue
        w = tuple(seq[s:i])
        n_tot += 1
        if raro in w:
            n_raro += 1
            continue
        c = sum(bit[s - 1:i])
        cella = tab.setdefault(i - s, [0, 0.0, 0, 0.0])
        if w in vocabolario:
            cella[0] += 1
            cella[1] += c
        else:
            cella[2] += 1
            cella[3] += c
    return tab, n_raro, n_tot


def rapporto(tab, min_viste=MIN_VISTE):
    """R e copertura (quota delle parole mai viste che stanno in lunghezze con abbastanza parole viste)."""
    num = den = nu_tot = 0.0
    for ns, bs, nu, bu in tab.values():
        nu_tot += nu
        if nu > 0 and ns >= min_viste:
            num += nu * (bu / nu) / (bs / ns)
            den += nu
    return (num / den if den else None), (den / nu_tot if nu_tot else None)


# ---------------------------------------------------------------- modelli di riferimento

class Trigrammi:
    """Modello a trigrammi di segni (due segni di contesto), lisciatura di Witten-Bell, sull'addestramento. Non ha modo
    di imparare parole intere a memoria."""

    def __init__(self, add, V):
        import numpy as np
        self.np, self.V = np, V
        a = np.array(add)
        c1 = np.bincount(a, minlength=V).astype(float)
        c2 = np.zeros((V, V))
        np.add.at(c2, (a[:-1], a[1:]), 1)
        c3 = np.zeros((V, V, V), dtype=np.float32)
        np.add.at(c3, (a[:-2], a[1:-1], a[2:]), 1)
        self.c2, self.c3 = c2, c3
        t1 = float((c1 > 0).sum())
        self.p1 = (c1 + t1 / V) / (c1.sum() + t1)
        self.n2, self.t2 = c2.sum(1), (c2 > 0).sum(1)
        self.n3, self.t3 = c3.sum(2), (c3 > 0).sum(2)

    def p_uno(self):
        return self.p1

    def p_due(self, b):
        d = self.n2[b] + self.t2[b]
        return self.p1 if d == 0 else (self.c2[b] + self.t2[b] * self.p1) / d

    def p_tre(self, a, b):
        q = self.p_due(b)
        d = self.n3[a, b] + self.t3[a, b]
        return q if d == 0 else (self.c3[a, b] + self.t3[a, b] * q) / d

    def bit(self, seq):
        """bit[j] = costo del segno j+1 della sequenza."""
        np = self.np
        out = []
        for i in range(1, len(seq)):
            p = self.p_due(seq[i - 1]) if i == 1 else self.p_tre(seq[i - 2], seq[i - 1])
            out.append(-math.log2(float(p[seq[i]])))
        return out

    def campiona(self, rng, nl, flussi, passi, ordine):
        """Flussi di segni; contesto iniziale: due a capo."""
        np, V = self.np, self.V
        out = np.zeros((flussi, passi), dtype=int)
        if ordine == 1:
            cum = np.cumsum(self.p1)
            for k in range(passi):
                out[:, k] = np.minimum((cum[None, :] < rng.random(flussi)[:, None] * cum[-1]).sum(1), V - 1)
            return out
        q = np.stack([self.p_due(b) for b in range(V)])                      # q[b] = P(x | b)
        d = self.n3 + self.t3
        p3 = np.where(d[..., None] == 0, q[None, :, :],
                      (self.c3.astype(float) + self.t3[..., None] * q[None, :, :]) / np.maximum(d, 1)[..., None])
        cum = np.cumsum(p3, axis=2)                                           # cum[a, b] = distribuzione cumulata
        a = np.full(flussi, nl)
        b = np.full(flussi, nl)
        for k in range(passi):
            c = cum[a, b]
            x = np.minimum((c < rng.random(flussi)[:, None] * c[:, -1:]).sum(1), V - 1)
            out[:, k] = x
            a, b = b, x
        return out


def inventate(flussi, vocabolario, tenuto, delim, raro):
    """Conteggi sulle parole inventate: valide, nuove, nuove che compaiono nel testo non usato per l'addestramento."""
    valide = nuove = hit = 0
    tipi_nuovi, tipi_hit = set(), set()
    for riga in flussi:
        riga = [int(x) for x in riga]
        for s, i in parole_di(riga, delim)[1:1 + PAROLE_FLUSSO]:
            w = tuple(riga[s:i])
            if raro in w:
                continue
            valide += 1
            if w in vocabolario:
                continue
            nuove += 1
            tipi_nuovi.add(w)
            if w in tenuto:
                hit += 1
                tipi_hit.add(w)
    return dict(valide=valide, nuove=nuove, hit=hit, tipi_nuovi=len(tipi_nuovi), tipi_hit=len(tipi_hit))


# ---------------------------------------------------------------- corsa

def corsa(lavoro):
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Modello(nn.Module):
        def __init__(self, V):
            super().__init__()
            self.emb = nn.Embedding(V, e95.EMB)
            self.gru = nn.GRU(e95.EMB, e95.NASCOSTO, batch_first=True)
            self.caduta = nn.Dropout(e95.CADUTA)
            self.out = nn.Linear(e95.NASCOSTO, V)

        def forward(self, x):
            y, _ = self.gru(self.emb(x))
            return self.out(self.caduta(y))

    inizio = time.time()
    seme, V, voc = lavoro['seme'], lavoro['V'], lavoro['voc']
    LUNG, LOTTO, OGNI, PAZIENZA = e95.LUNG, e95.LOTTO, e95.OGNI, e95.PAZIENZA
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = Modello(V)
    opt = torch.optim.AdamW(m.parameters(), lr=e95.LR, weight_decay=e95.DECADIMENTO)
    add = torch.tensor(lavoro['add'], dtype=torch.long)
    val = torch.tensor(lavoro['val'], dtype=torch.long)
    prova = torch.tensor(lavoro['prova'], dtype=torch.long)
    finestra = torch.arange(LUNG + 1)

    def valuta(p):
        m.eval()
        with torch.no_grad():
            logit = m(p[None, :-1])[0]
            bpc = F.cross_entropy(logit, p[1:]).item() / math.log(2)
        m.train()
        return round(bpc, 5)

    # stessa traiettoria di e3c95; in più si tiene lo stato del punto scelto (validazione più bassa, la prima in caso
    # di parità)
    curva_val, curva, perdite, perdita, migliore = [], [], [], 0.0, None
    for passo in range(1, e95.PASSI + 1):
        partenze = torch.from_numpy(rng.integers(0, len(add) - LUNG - 1, size=LOTTO))
        xb = add[partenze[:, None] + finestra]
        logit = m(xb[:, :-1])
        loss = F.cross_entropy(logit.reshape(-1, V), xb[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), e95.TAGLIO)
        opt.step()
        perdita += loss.item()
        if passo % OGNI == 0:
            curva_val.append(valuta(val))
            curva.append(valuta(prova))
            perdite.append(round(perdita / OGNI / math.log(2), 5))
            perdita = 0.0
            if len(curva_val) == 1 or curva_val[-1] < min(curva_val[:-1]):
                migliore = {k: v.clone() for k, v in m.state_dict().items()}
            if len(curva_val) - 1 - curva_val.index(min(curva_val)) >= PAZIENZA:
                break
    m.load_state_dict(migliore)
    m.eval()
    scelta = curva_val.index(min(curva_val))

    sp, nl, raro = voc.index(' '), voc.index('\n'), voc.index(e95.RARO)
    delim = {sp, nl}
    seq_add, seq_val, seq_prova = lavoro['add'], lavoro['val'], lavoro['prova']
    vocab = {tuple(seq_add[s:i]) for s, i in parole_di(seq_add, delim)}
    vocab_add = {w for w in vocab if raro not in w}
    tenuto = ({tuple(seq_val[s:i]) for s, i in parole_di(seq_val, delim)} |
              {tuple(seq_prova[s:i]) for s, i in parole_di(seq_prova, delim)})
    tenuto = {w for w in tenuto if raro not in w} - vocab_add

    # costo dei segni della prova, rete e trigrammi
    with torch.no_grad():
        lp = F.log_softmax(m(prova[None, :-1])[0], dim=-1)
        bit_rete = (-lp.gather(1, prova[1:, None])[:, 0] / math.log(2)).double().tolist()
    tri = Trigrammi(seq_add, V)
    bit_tri = tri.bit(seq_prova)
    tab_rete, n_raro, n_parole = tabella_lunghezze(seq_prova, bit_rete, vocab, delim, raro)
    tab_tri, _, _ = tabella_lunghezze(seq_prova, bit_tri, vocab, delim, raro)

    # parole inventate
    g = torch.Generator().manual_seed(100000 + seme)
    x = torch.full((FLUSSI, 1), nl, dtype=torch.long)
    h, usc = None, []
    with torch.no_grad():
        for _ in range(SEGNI_FLUSSO):
            y, h = m.gru(m.emb(x), h)
            p = F.softmax(m.out(y[:, -1]), dim=-1)
            x = torch.multinomial(p, 1, generator=g)
            usc.append(x)
    flussi_rete = torch.cat(usc, dim=1).tolist()
    r = np.random.default_rng(200000 + seme)
    inv = dict(rete=inventate(flussi_rete, vocab_add, tenuto, delim, raro),
               uni=inventate(tri.campiona(r, nl, FLUSSI, SEGNI_FLUSSO, 1), vocab_add, tenuto, delim, raro),
               tri=inventate(tri.campiona(r, nl, FLUSSI, SEGNI_FLUSSO, 3), vocab_add, tenuto, delim, raro))
    inv['n_tenuto'] = len(tenuto)
    return dict(testo=lavoro['testo'], seme=seme, V=V, parametri=sum(p.numel() for p in m.parameters()),
                h1=round(e95.h1(lavoro['add'], lavoro['prova'], V), 5), validazione=curva_val, curva=curva,
                addestramento=perdite, passi=passo, scelta=scelta, bpc_rete=round(sum(bit_rete) / len(bit_rete), 5),
                bpc_tri=round(sum(bit_tri) / len(bit_tri), 5), n_parole=n_parole, n_con_raro=n_raro,
                n_vocabolario=len(vocab_add), lunghezze_rete={str(k): v for k, v in sorted(tab_rete.items())},
                lunghezze_tri={str(k): v for k, v in sorted(tab_tri.items())}, inventate=inv,
                segni_per_valutazione=OGNI * LOTTO * LUNG, segni_addestramento=len(seq_add),
                secondi=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- misure

def misure_corsa(c):
    tab_r = {int(k): v for k, v in c['lunghezze_rete'].items()}
    tab_t = {int(k): v for k, v in c['lunghezze_tri'].items()}
    R, cop = rapporto(tab_r)
    Rt, _ = rapporto(tab_t)
    nu = sum(v[2] for v in tab_r.values())
    ns = sum(v[0] for v in tab_r.values())
    segni_u = sum(L * v[2] for L, v in tab_r.items())
    segni_s = sum(L * v[0] for L, v in tab_r.items())
    out = dict(R=R, copertura=cop, R_tri=Rt, R_rel=(R / Rt if R is not None and Rt else None),
               quota_nuove=nu / (nu + ns) if nu + ns else None,
               costo_visto=sum(v[1] for v in tab_r.values()) / segni_s if segni_s else None,
               costo_nuovo=sum(v[3] for v in tab_r.values()) / segni_u if segni_u else None,
               bpc=c['curva'][c['scelta']], bpc_tri=c['bpc_tri'])
    i = c['inventate']
    for k in ('rete', 'uni', 'tri'):
        d = i[k]
        out['N_' + k] = d['nuove'] / d['valide'] if d['valide'] else None
        out['Q_' + k] = d['hit'] / d['nuove'] if d['nuove'] else None
    out['Q_tipi_rete'] = i['rete']['tipi_hit'] / i['rete']['tipi_nuovi'] if i['rete']['tipi_nuovi'] else None
    return out


def media_ds(xs):
    return e95.media_ds(xs)


MIN_HIT = 100           # hit minimi (su tutti i semi) perché Q si legga


def valore(tab, n, k):
    """Media di una misura del testo n, o None; Q si legge solo con almeno MIN_HIT hit (Q_rel anche per i trigrammi)."""
    x = tab[n].get(k)
    if not x:
        return None
    if k in ('Q_rete', 'Q_rel') and not tab[n]['Q_ok']:
        return None
    return x['media']


def analizza(t, corse):
    per = OrderedDict()
    for nome in t:
        cs = sorted((c for c in corse if c['testo'] == nome), key=lambda c: c['seme'])
        if cs:
            per[nome] = cs
    tab = OrderedDict()
    for nome, cs in per.items():
        ms = [misure_corsa(c) for c in cs]
        tab[nome] = OrderedDict((k, media_ds([m[k] for m in ms])) for k in ms[0])
        tab[nome]['ruolo'] = t[nome]['ruolo']
        tab[nome]['V'] = cs[0]['V']
        tab[nome]['secondi'] = statistics.mean(c['secondi'] for c in cs)
        tab[nome]['corse_al_limite'] = sum(1 for c in cs if c['passi'] >= e95.PASSI)
        tab[nome]['n_con_raro'] = statistics.mean(c['n_con_raro'] / c['n_parole'] for c in cs)
        somma = {k: {d: sum(c['inventate'][k][d] for c in cs) for d in ('hit', 'nuove')} for k in ('rete', 'tri')}
        tab[nome]['hit_rete'] = somma['rete']['hit']                       # in tutti i semi
        tab[nome]['nuove_rete'] = somma['rete']['nuove']
        tab[nome]['Q_ok'] = somma['rete']['hit'] >= MIN_HIT
        # Q_rel = Q_rete / Q_tri sui conteggi di tutti i semi; solo con almeno MIN_HIT hit in entrambi
        ok = (somma['rete']['hit'] >= MIN_HIT and somma['tri']['hit'] >= MIN_HIT and somma['rete']['nuove'] and
              somma['tri']['nuove'])
        tab[nome]['Q_rel'] = dict(media=(somma['rete']['hit'] / somma['rete']['nuove']) /
                                  (somma['tri']['hit'] / somma['tri']['nuove']), ds=0.0, n=1) if ok else None
    ctrl = controlli(tab)
    lingue_n = [n for n in tab if tab[n]['ruolo'] == 'lingua']
    chiavi = ('R', 'R_rel', 'R_tri', 'quota_nuove', 'N_rete', 'Q_rete', 'Q_rel', 'costo_visto', 'costo_nuovo')
    confronti = OrderedDict()
    for k in chiavi:
        valori = [valore(tab, n, k) for n in lingue_n if valore(tab, n, k) is not None]
        confronti[k] = OrderedDict()
        for nome in tab:
            if tab[nome]['ruolo'] != 'lingua' and valore(tab, nome, k) is not None:
                confronti[k][nome] = e95.posizione(valore(tab, nome, k), valori)
    # fra le lingue: R_rel e quota di parole nuove, R_rel e alfabeto (descrittivo)
    ll = [n for n in lingue_n if tab[n].get('R_rel')]
    confronti['R_rel_e_quota_nuove_spearman'] = e95.spearman([tab[n]['quota_nuove']['media'] for n in ll],
                                                             [tab[n]['R_rel']['media'] for n in ll])
    confronti['R_rel_e_alfabeto_spearman'] = e95.spearman([tab[n]['V'] for n in ll],
                                                          [tab[n]['R_rel']['media'] for n in ll])
    # profilo (R_rel, N_rete, Q_rel): ogni misura divisa per la deviazione standard fra le lingue; distanza euclidea,
    # sulle misure che il Voynich ha (Q_rel solo con abbastanza hit); i candidati devono averle tutte
    ds_l = {}
    for k in ('R_rel', 'N_rete', 'Q_rel'):
        vs = [valore(tab, n, k) for n in lingue_n if valore(tab, n, k) is not None]
        if len(vs) > 2:
            ds_l[k] = statistics.stdev(vs)
    vicini, dimensioni = OrderedDict(), OrderedDict()
    for v in ('Voynich', 'Voynich A', 'Voynich B'):
        if v not in tab:
            continue
        dim = [k for k in ('R_rel', 'N_rete', 'Q_rel') if k in ds_l and valore(tab, v, k) is not None]
        if len(dim) < 2:
            continue
        dimensioni[v] = dim
        dist = []
        for n in tab:
            if tab[n]['ruolo'] == 'voynich' or any(valore(tab, n, k) is None for k in dim):
                continue
            d = math.sqrt(sum(((valore(tab, n, k) - valore(tab, v, k)) / ds_l[k]) ** 2 for k in dim))
            dist.append((d, n))
        vicini[v] = [dict(testo=n, ruolo=tab[n]['ruolo'], distanza=d) for d, n in sorted(dist)]
    # generatori e controlli rispetto al Voynich intero: "vicino" se la differenza è al massimo un decimo
    # dell'intervallo delle lingue
    rispetto = OrderedDict()
    if 'Voynich' in tab:
        for n in tab:
            if tab[n]['ruolo'] not in ('generatore', 'controllo'):
                continue
            rispetto[n] = OrderedDict()
            for k in ('R', 'R_rel', 'quota_nuove', 'N_rete', 'Q_rel'):
                vs = [valore(tab, x, k) for x in lingue_n if valore(tab, x, k) is not None]
                a, b = valore(tab, n, k), valore(tab, 'Voynich', k)
                if a is not None and b is not None and vs:
                    rispetto[n][k] = dict(differenza=a - b, vicino=abs(a - b) <= 0.1 * (max(vs) - min(vs)))
    # letture 1, 6 e 7 della preregistrazione
    letture = OrderedDict()
    rel_l = [valore(tab, n, 'R_rel') for n in lingue_n if valore(tab, n, 'R_rel') is not None]
    rho = confronti['R_rel_e_quota_nuove_spearman']
    regole_ok = bool(ctrl.get('positivo', {}).get('superato'))
    for v in ('Voynich', 'Voynich A', 'Voynich B'):
        if v not in tab or not tab[v].get('R_rel') or not rel_l:
            continue
        rel = tab[v]['R_rel']['media']
        p = e95.posizione(rel, rel_l)
        if rel <= SOGLIA_POSITIVO:
            etichetta = ('solo regole (R_rel sotto la soglia, controlli "solo regole" riusciti)' if regole_ok else
                         'sotto la soglia, ma i controlli "solo regole" non reggono tutti: non si legge come "solo regole"')
        elif p['dentro'] == 'sotto':
            etichetta = 'sotto le lingue, sopra la soglia'
        else:
            etichetta = p['dentro'] + ' l\'intervallo delle lingue'
        scala = None
        if C_POS in tab and C_NEG in tab and tab[C_POS].get('R_rel') and tab[C_NEG].get('R_rel'):
            a, b = tab[C_POS]['R_rel']['media'], tab[C_NEG]['R_rel']['media']
            scala = (rel - a) / (b - a) if b != a else None
        cop = tab[v]['copertura']['media'] if tab[v].get('copertura') else None
        letture[v] = dict(R_rel=rel, posizione=p, scala_0_regole_1_memoria=scala, lettura=etichetta, copertura=cop,
                          avvertenza_copertura=cop is None or cop < 0.5,
                          avvertenza_vocabolario=bool(rho is not None and abs(rho) > 0.5))
    if 'Voynich A' in tab and 'Voynich B' in tab and tab['Voynich A'].get('R_rel') and tab['Voynich B'].get('R_rel'):
        a, b = tab['Voynich A']['R_rel'], tab['Voynich B']['R_rel']
        soglia = 3 * max(a['ds'], b['ds'])
        letture['A_contro_B'] = dict(R_rel_A=a['media'], R_rel_B=b['media'], differenza=abs(a['media'] - b['media']),
                                     soglia_3ds=soglia, differiscono=abs(a['media'] - b['media']) > soglia)
    return tab, confronti, dict(vicini=vicini, dimensioni_profilo=dimensioni, rispetto_al_voynich=rispetto,
                                ds_lingue=ds_l, letture=letture, controlli=ctrl)


def controlli(tab):
    """Controlli sulla misura principale, R_rel = R(rete) / R(trigrammi). Se un R_rel manca, il controllo non è superato."""
    out = OrderedDict()

    def rel(n):
        return tab[n]['R_rel']['media'] if n in tab and tab[n].get('R_rel') else None
    pos = [(n, rel(n)) for n in (C_POS, C_POS2) if n in tab]
    if pos:
        out['positivo'] = OrderedDict([('R_rel_' + n.split(' ')[0], x) for n, x in pos])
        out['positivo']['soglia'] = SOGLIA_POSITIVO
        out['positivo']['superato'] = all(x is not None and x <= SOGLIA_POSITIVO for n, x in pos)
    lingue = [rel(n) for n, v in tab.items() if v['ruolo'] == 'lingua' and rel(n) is not None]
    if C_NEG in tab and lingue:
        x = rel(C_NEG)
        piu_alto = max([y for n, y in pos if y is not None], default=None)
        ds = max([tab[n]['R_rel']['ds'] for n in (C_NEG, C_POS, C_POS2) if n in tab and tab[n].get('R_rel')], default=0)
        out['negativo'] = dict(R_rel=x, R_rel_max_lingue=max(lingue), R_rel_max_positivi=piu_alto,
                               superato=x is not None and x > max(lingue) and
                               (piu_alto is None or x - piu_alto > 5 * ds))
    return out


def scrivi(t, corse, versioni):
    tab, confronti, profili = analizza(t, corse)
    ctrl = controlli(tab)
    par = OrderedDict(N_ADD=e95.N_ADD, N_VAL=e95.N_VAL, N_PROVA=e95.N_PROVA, PASSI=e95.PASSI, OGNI=e95.OGNI,
                      PAZIENZA=e95.PAZIENZA, SEMI=e95.SEMI, LUNG=e95.LUNG, LOTTO=e95.LOTTO, EMB=e95.EMB,
                      NASCOSTO=e95.NASCOSTO, CADUTA=e95.CADUTA, LR=e95.LR, DECADIMENTO=e95.DECADIMENTO,
                      TAGLIO=e95.TAGLIO, SOLO_CONTROLLI=e95.SOLO_CONTROLLI, MIN_VISTE=MIN_VISTE, FLUSSI=FLUSSI,
                      SEGNI_FLUSSO=SEGNI_FLUSSO, PAROLE_FLUSSO=PAROLE_FLUSSO, SEGNI_SINTETICI=SEGNI_SINTETICI,
                      SEME_SINTETICI=SEME_SINTETICI, LESSICO=LESSICO, SOGLIA_POSITIVO=SOGLIA_POSITIVO)
    ris = OrderedDict(esperimento='ia02', parametri=par, versioni=versioni, controlli=ctrl, testi=tab,
                      confronti=confronti, profili=profili)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')

    def f3(d, k='media'):
        return '–' if not d else '%.3f' % d[k]

    r = ['# IA2 (ia02) — parole mai viste', '',
         'Stesso modello di e3c95: GRU a caratteri (%d unità), %d segni di addestramento, %d di validazione, %d di prova, '
         'al massimo %d passi, semi %s.' % (e95.NASCOSTO, e95.N_ADD, e95.N_VAL, e95.N_PROVA, e95.PASSI,
                                            ', '.join(map(str, e95.SEMI))),
         'Corse arrivate al massimo dei passi: %d.' % sum(v['corse_al_limite'] for v in tab.values()),
         'Valori: media dei semi (deviazione standard fra i semi).', '', '## Controlli', '']
    for k, v in ctrl.items():
        r.append('- %s: %s' % (k, ', '.join('%s %s' % (a, ('%.4f' % b) if isinstance(b, float) else b)
                                           for a, b in v.items())))
    r += ['', '## Misure per testo', '',
          'R: costo per segno delle parole mai viste / delle viste, a parità di lunghezza (rete); R_tri: lo stesso per il '
          'modello a trigrammi (nessuna memoria di parole intere); R_rel = R / R_tri. quota nuove: parole mai viste '
          'nella prova. N: quota di parole inventate non presenti nell\'addestramento; Q: fra le nuove, quota che '
          'compare in validazione+prova (rete / trigrammi / unigrammi); la Q della rete si legge solo con almeno %d hit sui '
          'semi (altrimenti "–", e il numero di hit è fra parentesi). I costi per segno (costo_visto, costo_nuovo) sommano '
          'i bit dei segni e del separatore che chiude la parola, e dividono per i soli segni.' % MIN_HIT, '',
          '| testo | ruolo | segni | BPC | quota nuove | R | R_tri | R_rel | copertura | N | Q rete (n hit) | Q tri | Q uni |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, v in tab.items():
        r.append('| %s | %s | %d | %s | %s | %s (%s) | %s | %s (%s) | %s | %s | %s (%d) | %s | %s |' % (
            nome, v['ruolo'], v['V'], f3(v['bpc']), f3(v['quota_nuove']), f3(v['R']), f3(v['R'], 'ds'),
            f3(v['R_tri']), f3(v['R_rel']), f3(v['R_rel'], 'ds'), f3(v['copertura']), f3(v['N_rete']),
            f3(v['Q_rete']) if v['Q_ok'] else '–', v['hit_rete'], f3(v['Q_tri']), f3(v['Q_uni'])))
    r += ['', '## Posizione rispetto alle lingue', '']
    for k, d in confronti.items():
        if not isinstance(d, dict):
            r.append('- %s: %s' % (k, '–' if d is None else '%.3f' % d))
            continue
        for nome, p in d.items():
            if p:
                r.append('- %s, %s: %.3f, %s l\'intervallo delle lingue [%.3f, %.3f], lingue sotto: %.0f%%' % (
                    k, nome, tab[nome][k]['media'], p['dentro'], p['minimo'], p['massimo'], 100 * p['frazione_sotto']))
    r += ['', '## Letture 1, 6 e 7', '']
    for v, d in profili['letture'].items():
        if v == 'A_contro_B':
            r.append('- A contro B: R_rel %.3f e %.3f, differenza %.3f, soglia (3 deviazioni standard) %.3f: %s' % (
                d['R_rel_A'], d['R_rel_B'], d['differenza'], d['soglia_3ds'],
                'differiscono' if d['differiscono'] else 'non distinguibili'))
            continue
        r.append('- %s: R_rel %.3f, %s; scala 0 (solo regole) - 1 (solo memoria): %s; lettura: %s%s%s' % (
            v, d['R_rel'], '%s l\'intervallo delle lingue (lingue sotto %.0f%%)' % (d['posizione']['dentro'],
                                                                                 100 * d['posizione']['frazione_sotto']),
            '–' if d['scala_0_regole_1_memoria'] is None else '%.2f' % d['scala_0_regole_1_memoria'], d['lettura'],
            '; AVVERTENZA: copertura %s sotto 0,5' % ('assente' if d['copertura'] is None else '%.2f' % d['copertura'])
            if d['avvertenza_copertura'] else '',
            '; AVVERTENZA: R_rel dipende dal vocabolario (|rho| > 0,5 fra le lingue)' if d['avvertenza_vocabolario']
            else ''))
    r += ['', '## Testi più vicini al Voynich sul profilo (R_rel, N, Q_rel)', '',
          'Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea; Q_rel = Q_rete / Q_tri, '
          'solo con almeno %d hit (altrimenti la misura manca e il profilo usa le altre).' % MIN_HIT, '']
    for v, lista in profili['vicini'].items():
        r.append('- %s (misure: %s): %s' % (v, ', '.join(profili['dimensioni_profilo'][v]),
                                            '; '.join('%s (%s) %.2f' % (x['testo'], x['ruolo'], x['distanza'])
                                                      for x in lista[:6])))
    r += ['', '## Generatori e controlli rispetto al Voynich', '',
          '"vicino": differenza al massimo un decimo dell\'intervallo delle lingue.', '']
    for n, d in profili['rispetto_al_voynich'].items():
        r.append('- %s: %s' % (n, ', '.join('%s %+.3f%s' % (k, x['differenza'], ' (vicino)' if x['vicino'] else '')
                                            for k, x in d.items())))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris


def main():
    import torch
    import numpy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    tutti, t = catalogo()
    print('testi: %d' % len(t), flush=True)
    for nome, v in t.items():
        print('  %-70s %-13s blocchi %4d segni %7d' % (nome, v['ruolo'], len(v['blocchi']),
                                                      e95.lunghezza(v['blocchi'])), flush=True)
    lavori, scarti = prepara(tutti, t)
    if scarti:
        print('troppo corti, esclusi: %s' % ', '.join(scarti), flush=True)
    percorso = os.path.join(USCITA, 'ia02_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    else:
        open(percorso, 'w').close()
    fatte = {(c['testo'], c['seme']) for c in corse}
    da_fare = [l for l in lavori if (l['testo'], l['seme']) not in fatte]
    print('corse: %d da fare, %d già fatte' % (len(da_fare), len(fatte)), flush=True)
    processi = int(os.environ.get('PROCESSI', 8))
    inizio = time.time()
    with get_context('spawn').Pool(processi, initializer=e95.avvia_processo) as pool:
        for i, c in enumerate(pool.imap_unordered(corsa, da_fare), 1):
            corse.append(c)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
            m = misure_corsa(c)
            print('[%d/%d %.0f min] %s seme %d: BPC %.3f quota nuove %.3f R %s R_tri %s N %.3f Q %s (%d passi, %.0f s)' % (
                i, len(da_fare), (time.time() - inizio) / 60, c['testo'], c['seme'], m['bpc'], m['quota_nuove'] or 0,
                '%.3f' % m['R'] if m['R'] else '–', '%.3f' % m['R_tri'] if m['R_tri'] else '–', m['N_rete'] or 0,
                '%.3f' % m['Q_rete'] if m['Q_rete'] is not None else '–', c['passi'], c['secondi']), flush=True)
    ris = scrivi(t, corse, versioni)
    for k, v in ris['controlli'].items():
        print('controllo %s: %s' % (k, v), flush=True)


if __name__ == '__main__':
    main()
