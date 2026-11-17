# -*- coding: utf-8 -*-
"""Esperimento e3c95: quanto è imparabile il testo del Voynich per un modello linguistico minuscolo, rispetto alle
lingue naturali, ai generatori pubblicati, ai cifrati e ai controlli.

Un modello a caratteri (GRU con un solo strato di 128 unità, circa 67.000 parametri con 30 segni) impara da capo
ogni testo. Per ogni testo e seme: 40.000 segni di addestramento, 5.000 di validazione e 10.000 di prova, in blocchi
diversi. Ogni 20 passi (circa 0,9 letture dell'addestramento) si misura l'entropia incrociata in bit per segno (BPC)
sulla validazione e sulla prova; ci si ferma quando la validazione non migliora da 10 valutazioni (al massimo 2.000
passi). Il punto scelto è quello con la validazione più bassa; le misure si leggono sulla prova in quel punto:
- H1: entropia incrociata del modello a un segno (frequenze dell'addestramento, più 0,5 su ogni segno);
- BPC: la BPC della prova nel punto scelto;
- G = 1 - BPC / H1: quanto il contesto aiuta, in frazione di H1;
- E90: letture dell'addestramento (epoche) necessarie per avere il 90% del guadagno H1 - BPC (velocità);
- scarto: BPC della prova meno BPC dell'addestramento nel punto scelto (quanto il modello ha imparato a memoria);
- D = BPC(parole rimescolate dentro la riga) - BPC(originale), seme per seme, stessi segni, righe e blocchi: quanto
  conta l'ordine delle parole;
- T: il modello addestrato su X, nel punto scelto, misurato sulla prova di Y, meno la BPC del modello addestrato su Y
  (Voynich A e B; testo tecnico e letterario della stessa lingua).

Segni: per il Voynich e i generatori in EVA, i glifi EVA fusi di analisi/misure.py (cth ckh cph cfh ch sh); per le
lingue, lettera più segni combinanti (e381.parola); spazio e a capo sono segni. Le parole con ? o * del Voynich si
tolgono (come in trascrizione.righe_di_parole). In ogni gruppo di testi (un testo o una coppia per il trasferimento)
i segni sotto lo 0,1% diventano un solo segno raro.

Blocchi: pagine per il Voynich e il libro del voynichizzatore; 29 righe per gli altri testi (dentro lo stesso testo
d'origine per il gibberish). Per ogni seme i blocchi si mettono in ordine casuale e riempiono, uno dopo l'altro,
addestramento, validazione e prova; poi i tre flussi si tagliano esattamente a 40.000, 5.000 e 10.000 segni.

Preregistrazione: preregistrazioni/e3c95.md. Scrive risultati/e3c95_imparabilita.json e .md e, una riga per corsa,
risultati/e3c95_corse.jsonl (con RIPRENDI=1 le corse già fatte non si rifanno).
SOLO_CONTROLLI=1: solo testi che non sono il Voynich né imitazioni in EVA (lingue, gibberish, latino cifrato), per
provare il codice. Per le prove rapide: PASSI, OGNI, PAZIENZA, SEMI, LUNG, LOTTO, NASCOSTO, CADUTA; TESTI (sottostringhe
separate da |, "=Nome" per il nome esatto); USCITA cambia la cartella d'uscita. I valori usati finiscono nel .json.
PROCESSI: numero di processi in parallelo (non cambia i risultati).
"""
import json, math, os, random, statistics, sys, time
from collections import OrderedDict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)

N_ADD = 40000
N_VAL = 5000
N_PROVA = 10000
RIGHE_BLOCCO = 29
PASSI = int(os.environ.get('PASSI', 2000))
OGNI = int(os.environ.get('OGNI', 20))
PAZIENZA = int(os.environ.get('PAZIENZA', 10))
SEMI = tuple(int(s) for s in os.environ.get('SEMI', '1,2,3,4,5,6,7,8,9,10').split(','))
LUNG = int(os.environ.get('LUNG', 64))
LOTTO = int(os.environ.get('LOTTO', 32))
EMB, NASCOSTO, CADUTA = 32, int(os.environ.get('NASCOSTO', 128)), float(os.environ.get('CADUTA', 0.3))
LR, DECADIMENTO, TAGLIO = 2e-3, 0.01, 1.0
SOGLIA_POSITIVO = 0.02   # bit per segno: circa 4,5 errori standard della differenza appaiata nella prova sui controlli
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
NOME = 'e3c95_imparabilita'


# ---------------------------------------------------------------- testi
# Ogni testo è una lista di blocchi; un blocco è una lista di righe; una riga è una lista di parole; una parola è una
# tupla di segni (stringhe).

def blocchi_di(righe, n=RIGHE_BLOCCO):
    return [righe[i:i + n] for i in range(0, len(righe), n)]


def voynich_pagine(lingua=None, fusi=True):
    import trascrizione, misure
    dividi = misure.divisore(misure.GLIFI_EVA) if fusi else list
    pagine = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        ps = [tuple(dividi(p)) for p in r.parole if trascrizione.pulita(p)]
        if ps:
            pagine.setdefault(r.pagina, []).append(ps)
    return list(pagine.values())


def libro_v21():
    import misure
    dividi = misure.divisore(misure.GLIFI_EVA)
    pagine = OrderedDict()
    percorso = os.path.join(QUI, '..', 'white_paper', 'en', 'figure', 'libro_esempio_v21.txt')
    for l in open(percorso, encoding='utf-8'):
        l = l.strip()
        if not l or l.startswith('#') or '>' not in l:
            continue
        locus, corpo = l.split('>', 1)
        pagina = locus.lstrip('@<').split('.')[0]
        ps = [tuple(dividi(w)) for w in corpo.strip().split('.') if w]
        if ps:
            pagine.setdefault(pagina, []).append(ps)
    return list(pagine.values())


def timm_schinner():
    import misure, e337_posizione as e337
    dividi = misure.divisore(misure.GLIFI_EVA)
    return [[[tuple(dividi(w)) for w in r] for r in p] for p in e337.pagine_ts(1)]


def naibbe():
    import misure, e134_generatori_esterni as e134
    dividi = misure.divisore(misure.GLIFI_EVA)
    return blocchi_di([[tuple(dividi(w)) for w in ps] for _, ps in e134.naibbe_righe()])


def gibberish():
    import e375_coppie as e375
    out = []
    for righe in e375.testi_zip('gibberish_transcriptions.zip', lambda n: True).values():
        out += blocchi_di([[tuple(w) for w in r] for r in righe])
    return out


# Per ogni lingua naturale di Gaskell e Bowern si prende un testo, nel primo di questi gruppi che ne ha uno abbastanza
# lungo (il più lungo del gruppo): prima i testi storici (più vicini al Voynich nel tempo), e fra questi i tecnici
# (più vicini nel genere).
PRIORITA = (('Historical', 'Technical'), ('Historical', 'Literary'), ('Modern', 'Technical'), ('Modern', 'Literary'))


def lingue():
    """Testi di Gaskell e Bowern per lingua: {lingua: {(categoria, genere): [(segni, chiave), ...]}}."""
    import e381_parole_intere as e381
    tt = e381.testi()
    per = OrderedDict()
    for k, righe in tt.items():
        parti = k.split(' - ')
        if parti[0] == 'Conlangs':
            continue
        n = sum(sum(len(w) for w in r) + len(r) for r in righe)
        per.setdefault(parti[1], {}).setdefault((parti[0], parti[2]), []).append((n, k))
    return tt, per


def frequenti(liste_di_blocchi, quota=0.001):
    """Segni con frequenza almeno 0,1% nei testi dati; gli altri diventano un solo segno raro."""
    conti = {}
    for blocchi in liste_di_blocchi:
        for b in blocchi:
            for r in b:
                for w in r:
                    for s in w:
                        conti[s] = conti.get(s, 0) + 1
    tot = sum(conti.values())
    return {s for s, c in conti.items() if c / tot >= quota}


RARO = '¤'


def segni(blocchi):
    return {s for b in blocchi for r in b for w in r for s in w}


def flusso(righe):
    out = []
    for r in righe:
        for j, w in enumerate(r):
            if j:
                out.append(' ')
            out.extend(w)
        out.append('\n')
    return out


def lunghezza(blocchi):
    return sum(len(flusso(b)) for b in blocchi)


def dividi_blocchi(blocchi, seme):
    """Righe di addestramento, validazione e prova per un seme (vedi la docstring del modulo); None se il testo è
    corto. I blocchi in ordine casuale riempiono, uno dopo l'altro, addestramento, validazione e prova."""
    ordine = list(range(len(blocchi)))
    random.Random(1000 + seme).shuffle(ordine)
    parti, quote, k = ([], [], []), (N_ADD, N_VAL, N_PROVA), 0
    n = [0, 0, 0]
    for i in ordine:
        while k < 3 and n[k] >= quote[k]:
            k += 1
        if k == 3:
            break
        parti[k].extend(blocchi[i])
        n[k] += len(flusso(blocchi[i]))
    if n[2] < N_PROVA:
        return None
    return parti


def rimescola_parole(righe, rnd):
    out = []
    for r in righe:
        r = list(r)
        rnd.shuffle(r)
        out.append(r)
    return out


def rimescola_lettere(righe, rnd):
    """Segni rimescolati fra tutte le parole, lunghezze delle parole e righe invariate."""
    tutti = [s for r in righe for w in r for s in w]
    rnd.shuffle(tutti)
    out, i = [], 0
    for r in righe:
        nr = []
        for w in r:
            nr.append(tuple(tutti[i:i + len(w)]))
            i += len(w)
        out.append(nr)
    return out


def cifra(blocchi, alfabeto, seme=95):
    """Sostituzione semplice: una permutazione casuale fissa dei segni (controllo positivo). Si permuta l'alfabeto
    di tutto il gruppo del testo in chiaro, così il modello cifrato ha lo stesso numero di segni."""
    alfabeto = sorted(alfabeto)
    immagine = alfabeto[:]
    random.Random(seme).shuffle(immagine)
    m = dict(zip(alfabeto, immagine))
    return [[[tuple(m[s] for s in w) for w in r] for r in b] for b in blocchi], m


def vigenere(blocchi, periodo=7, seme=96, quota=0.001):
    """Cifrario polialfabetico (Vigenère) con chiave casuale fissa di 7 spostamenti. L'alfabeto del cifrario sono i
    segni del testo con frequenza almeno 0,1% (le lettere comuni); i segni rari, gli spazi e gli a capo restano come
    sono. Il contatore corre sui segni cifrati nell'ordine originale del testo."""
    conti = {}
    for b in blocchi:
        for r in b:
            for w in r:
                for s in w:
                    conti[s] = conti.get(s, 0) + 1
    tot = sum(conti.values())
    alfabeto = sorted(s for s, c in conti.items() if c / tot >= quota)
    n, pos = len(alfabeto), {s: i for i, s in enumerate(alfabeto)}
    rnd = random.Random(seme)
    chiave = [rnd.randrange(1, n) for _ in range(periodo)]
    out, k = [], 0
    for b in blocchi:
        nb = []
        for r in b:
            nr = []
            for w in r:
                nw = []
                for s in w:
                    if s in pos:
                        nw.append(alfabeto[(pos[s] + chiave[k % periodo]) % n])
                        k += 1
                    else:
                        nw.append(s)
                nr.append(tuple(nw))
            nb.append(nr)
        out.append(nb)
    return out


def catalogo():
    """Testi dell'esperimento: nome -> dict(blocchi, gruppo, trasforma, ruolo)."""
    t = OrderedDict()

    def metti(nome, blocchi, ruolo, gruppo=None, trasforma=None):
        t[nome] = dict(blocchi=blocchi, ruolo=ruolo, gruppo=gruppo or nome, trasforma=trasforma)

    if not SOLO_CONTROLLI:
        tutto, a, b = voynich_pagine(), voynich_pagine('A'), voynich_pagine('B')
        metti('Voynich', tutto, 'voynich')
        metti('Voynich A', a, 'voynich', gruppo='Voynich A/B')
        metti('Voynich B', b, 'voynich', gruppo='Voynich A/B')
        metti('Voynich, parole rimescolate nella riga', tutto, 'rimescolato', gruppo='Voynich', trasforma='parole')
        metti('Voynich A, parole rimescolate nella riga', a, 'rimescolato', gruppo='Voynich A/B', trasforma='parole')
        metti('Voynich B, parole rimescolate nella riga', b, 'rimescolato', gruppo='Voynich A/B', trasforma='parole')
        metti('Voynich, segni rimescolati (controllo negativo)', tutto, 'controllo', gruppo='Voynich',
              trasforma='lettere')
        metti('Voynich in lettere EVA non fuse (sensibilità)', voynich_pagine(fusi=False), 'sensibilita')
        for nome, bl in (('Timm e Schinner (seme 1)', timm_schinner()), ('Voynichizzatore v21 (libro d\'esempio)',
                                                                           libro_v21()), ('Naibbe', naibbe())):
            metti(nome, bl, 'generatore')
            metti(nome + ', parole rimescolate nella riga', bl, 'rimescolato', gruppo=nome, trasforma='parole')
    metti('Gibberish (Gaskell e Bowern)', gibberish(), 'generatore')
    metti('Gibberish (Gaskell e Bowern), parole rimescolate nella riga', t['Gibberish (Gaskell e Bowern)']['blocchi'],
          'rimescolato', gruppo='Gibberish (Gaskell e Bowern)', trasforma='parole')
    tt, per = lingue()
    soglia = N_ADD + N_PROVA
    for l, d in per.items():
        scelto = None
        for cg in PRIORITA:
            cand = sorted((x for x in d.get(cg, []) if x[0] >= soglia), reverse=True)
            if cand:
                scelto = (cg, cand[0][1])
                break
        if not scelto:
            continue
        (cat, gen), k = scelto
        # per il trasferimento: il testo dell'altro genere, stessa lingua e stessa categoria, se è abbastanza lungo
        altro = 'Literary' if gen == 'Technical' else 'Technical'
        cand = sorted((x for x in d.get((cat, altro), []) if x[0] >= soglia), reverse=True)
        gruppo = l + ' (letterario/tecnico)' if cand else l
        bl = blocchi_di(tt[k])
        metti(l, bl, 'lingua', gruppo=gruppo)
        metti(l + ', parole rimescolate nella riga', bl, 'rimescolato', gruppo=gruppo, trasforma='parole')
        for x in (l, l + ', parole rimescolate nella riga'):
            t[x].update(sorgente=k, dominio=gen)
        if cand:
            k2 = cand[0][1]
            nome2 = '%s, %s' % (l, 'letterario' if altro == 'Literary' else 'tecnico')
            metti(nome2, blocchi_di(tt[k2]), 'trasferimento', gruppo=gruppo)
            t[nome2].update(sorgente=k2, dominio=altro)
    if 'Latin' in t:
        # il cifrato ha come alfabeto l'immagine dei segni frequenti del gruppo del latino: stesso numero di segni
        g = t['Latin']['gruppo']
        freq = frequenti([v['blocchi'] for v in t.values() if v['gruppo'] == g])
        bl, mappa = cifra(t['Latin']['blocchi'], segni(t['Latin']['blocchi']) | freq)
        metti('Latin, cifrato con una sostituzione (controllo positivo)', bl, 'controllo')
        t['Latin, cifrato con una sostituzione (controllo positivo)']['alfabeto'] = {mappa[s] for s in freq}
        vig = 'Latin, cifrato con Vigenère (periodo 7)'
        metti(vig, vigenere(t['Latin']['blocchi']), 'cifrato')
        metti(vig + ', parole rimescolate nella riga', t[vig]['blocchi'], 'rimescolato', gruppo=vig, trasforma='parole')
    filtro = [s for s in os.environ.get('TESTI', '').split('|') if s]
    if filtro:
        # "=Nome" vuol dire esattamente quel testo; altrimenti basta che il nome contenga la stringa
        t = OrderedDict((k, v) for k, v in t.items()
                        if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro))
    return t


# ---------------------------------------------------------------- modello

def prepara(t):
    """Flussi di segni per ogni (testo, seme), con l'alfabeto del gruppo; aggiunge le prove degli altri testi del
    gruppo (per il trasferimento)."""
    alfabeti = {}
    for g in {v['gruppo'] for v in t.values()}:
        membri = [v for v in t.values() if v['gruppo'] == g]
        esplicito = [v['alfabeto'] for v in membri if v.get('alfabeto')]
        alfabeti[g] = esplicito[0] if esplicito else frequenti([v['blocchi'] for v in membri])
    lavori, scarti = [], []
    divisi = {}
    for nome, v in t.items():
        for seme in SEMI:
            d = dividi_blocchi(v['blocchi'], seme)
            if d is None:
                scarti.append(nome)
                break
            if v['trasforma']:
                rnd = random.Random(7919 * seme + 1)
                f = rimescola_parole if v['trasforma'] == 'parole' else rimescola_lettere
                d = [f(x, rnd) for x in d]
            divisi[nome, seme] = tuple(flusso(x)[:q] for x, q in zip(d, (N_ADD, N_VAL, N_PROVA)))
    for nome, v in t.items():
        if nome in scarti:
            continue
        voc = sorted(alfabeti[v['gruppo']] | {' ', '\n', RARO})
        idx = {s: i for i, s in enumerate(voc)}

        def cod(seq):
            return [idx.get(s, idx[RARO]) for s in seq]
        compagni = [x for x, w in t.items() if w['gruppo'] == v['gruppo'] and x != nome and x not in scarti
                    and w['ruolo'] in ('voynich', 'lingua', 'trasferimento') and v['ruolo'] in
                    ('voynich', 'lingua', 'trasferimento')]
        for seme in SEMI:
            add, val, prova = divisi[nome, seme]
            altre = {x: cod(divisi[x, seme][2]) for x in compagni}
            lavori.append(dict(testo=nome, seme=seme, V=len(voc), add=cod(add), val=cod(val), prova=cod(prova),
                               altre=altre))
    return lavori, scarti


def avvia_processo():
    import torch
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)


def h1(add, prova, V):
    conti = [0.5] * V
    for s in add:
        conti[s] += 1
    tot = sum(conti)
    return -sum(math.log2(conti[s] / tot) for s in prova[1:]) / (len(prova) - 1)


def corsa(lavoro):
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class Modello(nn.Module):
        def __init__(self, V):
            super().__init__()
            self.emb = nn.Embedding(V, EMB)
            self.gru = nn.GRU(EMB, NASCOSTO, batch_first=True)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(NASCOSTO, V)

        def forward(self, x):
            y, _ = self.gru(self.emb(x))
            return self.out(self.caduta(y))

    inizio = time.time()
    seme, V = lavoro['seme'], lavoro['V']
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = Modello(V)
    opt = torch.optim.AdamW(m.parameters(), lr=LR, weight_decay=DECADIMENTO)
    add = torch.tensor(lavoro['add'], dtype=torch.long)
    # '' è la prova del testo, '@val' la sua validazione, le altre chiavi le prove degli altri testi del gruppo
    prove = OrderedDict([('@val', lavoro['val']), ('', lavoro['prova'])] + sorted(lavoro['altre'].items()))
    prove_t = {k: torch.tensor(v, dtype=torch.long) for k, v in prove.items()}
    finestra = torch.arange(LUNG + 1)

    def valuta(p):
        m.eval()
        with torch.no_grad():
            logit = m(p[None, :-1])[0]
            bpc = F.cross_entropy(logit, p[1:]).item() / math.log(2)
        m.train()
        return round(bpc, 5)

    curve = {k: [] for k in prove}
    perdita, perdite = 0.0, []
    for passo in range(1, PASSI + 1):
        partenze = torch.from_numpy(rng.integers(0, len(add) - LUNG - 1, size=LOTTO))
        xb = add[partenze[:, None] + finestra]
        logit = m(xb[:, :-1])
        loss = F.cross_entropy(logit.reshape(-1, V), xb[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        perdita += loss.item()
        if passo % OGNI == 0:
            for k, p in prove_t.items():
                curve[k].append(valuta(p))
            perdite.append(round(perdita / OGNI / math.log(2), 5))
            perdita = 0.0
            # arresto anticipato: la validazione non migliora da PAZIENZA valutazioni
            v = curve['@val']
            if len(v) - 1 - v.index(min(v)) >= PAZIENZA:
                break
    return dict(testo=lavoro['testo'], seme=seme, V=V, parametri=sum(p.numel() for p in m.parameters()),
                h1=round(h1(lavoro['add'], lavoro['prova'], V), 5), validazione=curve['@val'], curva=curve[''],
                curve_altre={k: v for k, v in curve.items() if k not in ('', '@val')}, addestramento=perdite,
                passi=passo, segni_per_valutazione=OGNI * LOTTO * LUNG, segni_addestramento=len(lavoro['add']),
                secondi=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- misure

def scelta(c):
    """Indice della valutazione scelta: quella con la validazione più bassa."""
    v = c['validazione']
    return v.index(min(v))


def bpc_scelta(c):
    return c['curva'][scelta(c)]


def misure_corsa(c):
    i, curva = scelta(c), c['curva']
    bpc = curva[i]
    guad = c['h1'] - bpc
    epoca = c['segni_per_valutazione'] / c['segni_addestramento']      # epoche fra due valutazioni
    e90 = None
    if guad > 0:
        e90 = next((j + 1) * epoca for j, x in enumerate(curva[:i + 1]) if c['h1'] - x >= 0.9 * guad)
    return dict(bpc=bpc, bpc_min_prova=min(curva), epoche_scelte=(i + 1) * epoca, h1=c['h1'], G=1 - bpc / c['h1'],
                E90=e90, scarto=bpc - c['addestramento'][i])


def media_ds(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(media=statistics.mean(xs), ds=statistics.stdev(xs) if len(xs) > 1 else 0.0, n=len(xs))


def posizione(x, valori):
    """Dove cade x fra i valori delle lingue: dentro/sotto/sopra l'intervallo e frazione di lingue sotto x."""
    if x is None or not valori:
        return None
    lo, hi = min(valori), max(valori)
    return dict(dentro='dentro' if lo <= x <= hi else ('sotto' if x < lo else 'sopra'),
                frazione_sotto=sum(1 for v in valori if v < x) / len(valori), minimo=lo, massimo=hi)


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
        tab[nome]['corse_al_limite'] = sum(1 for c in cs if c['passi'] >= PASSI)
    # D: rimescolato meno originale, seme per seme
    for nome, v in t.items():
        if v['trasforma'] != 'parole' or nome not in per:
            continue
        orig = nome.replace(', parole rimescolate nella riga', '')
        if orig not in per:
            continue
        bo = {c['seme']: bpc_scelta(c) for c in per[orig]}
        ds = [bpc_scelta(c) - bo[c['seme']] for c in per[nome] if c['seme'] in bo]
        rel = [(bpc_scelta(c) - bo[c['seme']]) / bo[c['seme']] for c in per[nome] if c['seme'] in bo]
        tab[orig]['D'] = media_ds(ds)
        tab[orig]['D_relativo'] = media_ds(rel)
    # T: trasferimento fra i due domini dello stesso gruppo
    trasf = OrderedDict()
    for nome, cs in per.items():
        for altro in cs[0]['curve_altre']:
            if altro not in per:
                continue
            # il modello di X, nel punto scelto sulla sua validazione, misurato sulla prova di Y
            bo = {c['seme']: bpc_scelta(c) for c in per[altro]}
            ts = [c['curve_altre'][altro][scelta(c)] - bo[c['seme']] for c in cs if c['seme'] in bo]
            trasf['%s -> %s' % (nome, altro)] = dict(T=media_ds(ts), gruppo=t[nome]['gruppo'])
    # confronti con le lingue
    lingue_n = [n for n in tab if tab[n]['ruolo'] == 'lingua']
    confronti = OrderedDict()
    for k in ('G', 'E90', 'D', 'D_relativo', 'bpc', 'h1', 'scarto'):
        valori = [tab[n][k]['media'] for n in lingue_n if tab[n].get(k)]
        confronti[k] = OrderedDict()
        for nome in tab:
            if tab[nome]['ruolo'] in ('voynich', 'generatore', 'controllo', 'cifrato', 'sensibilita') and \
                    tab[nome].get(k):
                confronti[k][nome] = posizione(tab[nome][k]['media'], valori)
    t_lingue = [v['T']['media'] for k, v in trasf.items() if not k.startswith('Voynich') and v['T']]
    confronti['T'] = OrderedDict((k, posizione(v['T']['media'], t_lingue)) for k, v in trasf.items()
                                 if k.startswith('Voynich') and v['T'])
    # quanto G dipende dal numero di segni dell'alfabeto, fra le lingue (Spearman)
    confronti['G_e_alfabeto_spearman'] = spearman([tab[n]['V'] for n in lingue_n],
                                                  [tab[n]['G']['media'] for n in lingue_n])
    # profilo (G, S, D): ogni misura divisa per la deviazione standard fra le lingue; distanza dal Voynich
    profilo = ('G', 'E90', 'D')
    ds_l = {}
    for k in profilo:
        vs = [tab[n][k]['media'] for n in lingue_n if tab[n].get(k)]
        if len(vs) > 2:
            ds_l[k] = statistics.stdev(vs)
    vicini, rispetto = OrderedDict(), OrderedDict()
    for v in ('Voynich', 'Voynich A', 'Voynich B'):
        if v not in tab or len(ds_l) < len(profilo) or not all(tab[v].get(k) for k in profilo):
            continue
        dist = []
        for n in tab:
            if tab[n]['ruolo'] in ('rimescolato', 'voynich', 'sensibilita') or not all(tab[n].get(k) for k in profilo):
                continue
            d = math.sqrt(sum(((tab[n][k]['media'] - tab[v][k]['media']) / ds_l[k]) ** 2 for k in profilo))
            dist.append((d, n))
        vicini[v] = [dict(testo=n, ruolo=tab[n]['ruolo'], distanza=d) for d, n in sorted(dist)]
    # generatori, cifrati e controlli rispetto al Voynich intero: "vicino" se la differenza è al massimo un decimo
    # dell'intervallo delle lingue
    if 'Voynich' in tab:
        for n in tab:
            if tab[n]['ruolo'] not in ('generatore', 'cifrato', 'controllo', 'sensibilita'):
                continue
            rispetto[n] = OrderedDict()
            for k in profilo:
                vs = [tab[x][k]['media'] for x in lingue_n if tab[x].get(k)]
                if tab[n].get(k) and tab['Voynich'].get(k) and vs:
                    diff = tab[n][k]['media'] - tab['Voynich'][k]['media']
                    rispetto[n][k] = dict(differenza=diff, vicino=abs(diff) <= 0.1 * (max(vs) - min(vs)))
    return tab, trasf, confronti, dict(vicini=vicini, rispetto_al_voynich=rispetto, ds_lingue=ds_l)


def spearman(xs, ys):
    if len(xs) < 3:
        return None

    def ranghi(v):
        ordine = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[ordine[j + 1]] == v[ordine[i]]:
                j += 1
            for k in range(i, j + 1):
                r[ordine[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranghi(xs), ranghi(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def controlli(tab):
    out = OrderedDict()
    if 'Latin' in tab and 'Latin, cifrato con una sostituzione (controllo positivo)' in tab:
        a = tab['Latin']['bpc']['media']
        b = tab['Latin, cifrato con una sostituzione (controllo positivo)']['bpc']['media']
        out['positivo'] = dict(differenza_bpc=b - a, soglia=SOGLIA_POSITIVO, superato=abs(b - a) <= SOGLIA_POSITIVO)
    neg = 'Voynich, segni rimescolati (controllo negativo)'
    if neg in tab and 'Voynich' in tab:
        g_lingue = [v['G']['media'] for v in tab.values() if v['ruolo'] == 'lingua']
        gn, gv = tab[neg]['G'], tab['Voynich']['G']
        out['negativo'] = dict(G_rimescolato=gn['media'], G_voynich=gv['media'], G_min_lingue=min(g_lingue),
                               superato=gn['media'] < min(g_lingue) and gv['media'] - gn['media'] >
                               5 * max(gn['ds'], gv['ds']))
    return out


def scrivi(t, corse, versioni):
    tab, trasf, confronti, profili = analizza(t, corse)
    ctrl = controlli(tab)
    ris = OrderedDict(esperimento='e3c95', parametri=dict(N_ADD=N_ADD, N_VAL=N_VAL, N_PROVA=N_PROVA, PASSI=PASSI, OGNI=OGNI, PAZIENZA=PAZIENZA,
                                                         SEMI=SEMI, LUNG=LUNG, LOTTO=LOTTO, EMB=EMB,
                                                         NASCOSTO=NASCOSTO, CADUTA=CADUTA, LR=LR,
                                                         DECADIMENTO=DECADIMENTO, TAGLIO=TAGLIO,
                                                         SOLO_CONTROLLI=SOLO_CONTROLLI),
                      versioni=versioni,
                      sorgenti={k: v.get('sorgente') for k, v in t.items() if v.get('sorgente')},
                      controlli=ctrl, testi=tab, trasferimento=trasf, confronti=confronti, profili=profili)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')

    def f3(d, k='media'):
        return '–' if not d else '%.3f' % d[k]

    r = ['# e3c95 — imparabilità per un modello minuscolo', '',
         'Modello a caratteri GRU (%d unità nascoste), %d segni di addestramento, %d di validazione, %d di prova, '
         'al massimo %d passi, semi %s.' % (NASCOSTO, N_ADD, N_VAL, N_PROVA, PASSI, ', '.join(map(str, SEMI))),
         'Corse arrivate al massimo dei passi: %d.' % sum(v['corse_al_limite'] for v in tab.values()),
         'Valori: media dei semi (deviazione standard fra i semi).', '', '## Controlli', '']
    for k, v in ctrl.items():
        r.append('- %s: %s' % (k, ', '.join('%s %s' % (a, ('%.4f' % b) if isinstance(b, float) else b)
                                           for a, b in v.items())))
    r += ['', '## Misure per testo', '',
          '| testo | ruolo | segni | H1 | BPC | G | E90 | D | scarto | epoche | s/corsa |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, v in tab.items():
        if v['ruolo'] == 'rimescolato':
            continue
        r.append('| %s | %s | %d | %s | %s | %s (%s) | %s (%s) | %s (%s) | %s | %s | %.0f |' % (
            nome, v['ruolo'], v['V'], f3(v['h1']), f3(v['bpc']), f3(v['G']), f3(v['G'], 'ds'), f3(v['E90']),
            f3(v['E90'], 'ds'), f3(v.get('D')), f3(v.get('D'), 'ds'), f3(v['scarto']), f3(v['epoche_scelte']),
            v['secondi']))
    r += ['', '## Trasferimento (T, bit per segno)', '', '| da -> a | T |', '|---|---|']
    for k, v in trasf.items():
        r.append('| %s | %s (%s) |' % (k, f3(v['T']), f3(v['T'], 'ds')))
    r += ['', '## Posizione rispetto alle lingue', '']
    for k, d in confronti.items():
        if not isinstance(d, dict):
            r.append('- %s: %s' % (k, '–' if d is None else '%.3f' % d))
            continue
        for nome, p in d.items():
            if not p:
                continue
            valore = trasf[nome]['T']['media'] if k == 'T' else tab[nome][k]['media']
            r.append('- %s, %s: %.3f, %s l\'intervallo delle lingue [%.3f, %.3f], lingue sotto: %.0f%%' % (
                k, nome, valore, p['dentro'], p['minimo'], p['massimo'], 100 * p['frazione_sotto']))
    r += ['', '## Testi più vicini al Voynich sul profilo (G, E90, D)', '',
          'Ogni misura divisa per la sua deviazione standard fra le lingue; distanza euclidea.', '']
    for v, lista in profili['vicini'].items():
        r.append('- %s: %s' % (v, '; '.join('%s (%s) %.2f' % (x['testo'], x['ruolo'], x['distanza'])
                                            for x in lista[:6])))
    r += ['', '## Generatori, cifrati e controlli rispetto al Voynich', '',
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
    t = catalogo()
    print('testi: %d' % len(t), flush=True)
    for nome, v in t.items():
        print('  %-70s %-13s blocchi %4d segni %7d' % (nome, v['ruolo'], len(v['blocchi']), lunghezza(v['blocchi'])),
              flush=True)
    lavori, scarti = prepara(t)
    if scarti:
        print('troppo corti, esclusi: %s' % ', '.join(scarti), flush=True)
    percorso = os.path.join(USCITA, 'e3c95_corse.jsonl')
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
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        for i, c in enumerate(pool.imap_unordered(corsa, da_fare), 1):
            corse.append(c)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
            m = misure_corsa(c)
            print('[%d/%d %.0f min] %s seme %d: H1 %.3f BPC %.3f G %.3f epoche %.1f (%d passi, %.0f s)' % (
                i, len(da_fare), (time.time() - inizio) / 60, c['testo'], c['seme'], m['h1'], m['bpc'], m['G'],
                m['epoche_scelte'], c['passi'], c['secondi']), flush=True)
    ris = scrivi(t, corse, versioni)
    for k, v in ris['controlli'].items():
        print('controllo %s: %s' % (k, v), flush=True)


if __name__ == '__main__':
    main()
