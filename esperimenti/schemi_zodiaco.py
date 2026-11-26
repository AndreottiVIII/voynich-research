# -*- coding: utf-8 -*-
"""IA44, ricerche (b) e (c): lo zodiaco, contro le divisioni note dei segni e le tavole note dei gradi.

(b) SEGNI. Per ogni parola presente in almeno 2 e al massimo 6 dei 10 segni (per presenza), quanto la sua presenza segue una
    divisione nota dei segni (elemento, modalita', caldo/freddo, secco/umido, pianeta). Misura esatta: T = numero di coppie di segni
    della parola che stanno nella stessa classe; p esatta = quota dei sottoinsiemi di segni della stessa taglia con T uguale o piu'
    grande (si enumerano tutti: 2^10). Due testi: b1 = solo etichette, b2 = tutto il testo dei fogli (etichette, cerchi, raggi).
    Statistiche: per ogni (testo, divisione): il massimo di -log10(p) sulle parole e la somma (omnibus). Ognuna si standardizza con
    il proprio nullo; la statistica della ricerca e' il massimo degli z. Nullo: le classi si assegnano ai segni con una permutazione
    a caso (tutte le parole restano uguali).
(c) GRADI. Le etichette di un segno (circa 30 righe) si mettono sui 30 gradi: la riga i del segno (in ordine di locus, n righe)
    cade sul grado d = floor(30 i / n); poi una rotazione r (0-29) e un verso (+1/-1) COMUNI a tutti i segni: grado = (verso d + r)
    mod 30. Per ogni parola con almeno 4 occorrenze in almeno 2 segni e ognuna delle 7 tavole binarie: z = (k - somma q_s) /
    radice(somma q_s (1-q_s)), con k = occorrenze in gradi di classe 1, q_s = quota di classe 1 del segno nella tavola (i gradi
    esclusi non contano). Per ogni tavola: massimo di |z| su parole, rotazioni, versi. Ognuna si standardizza con il proprio
    nullo; statistica = massimo degli z. Nullo: ogni segno ruota per conto suo di uno scarto a caso e prende un verso a caso
    (la sequenza delle etichette resta intera: i vicini restano vicini).
"""
import os
import sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import schemi_tavole as TV   # noqa: E402
import schemi_dati as D      # noqa: E402

MIN_SEGNI_B, MAX_SEGNI_B = 2, 6
MIN_OCC_C = 4
MIN_SEGNI_C = 2
K_NULLO = int(os.environ.get('K_ZODIACO44', 9999))
RUOTA_SEGNI = [D.RUOTA[s] for s in D.ORDINE_SEGNI]          # indice sulla ruota dei 10 segni presenti


# ---------------------------------------------------------------- (b) segni

def _tabelle_b():
    """Per ogni divisione e ogni maschera di segni (10 bit): -log10 p esatta (0 se la taglia e' fuori da 2-6)."""
    div = TV.divisioni()
    n = len(D.ORDINE_SEGNI)
    popc = np.array([bin(m).count('1') for m in range(1 << n)])
    tab = OrderedDict()
    for nome, classi12 in div.items():
        classi = [classi12[r] for r in RUOTA_SEGNI]
        T = np.zeros(1 << n, dtype=int)
        for m in range(1 << n):
            c = {}
            for j in range(n):
                if m >> j & 1:
                    c[classi[j]] = c.get(classi[j], 0) + 1
            T[m] = sum(k * (k - 1) // 2 for k in c.values())
        mlp = np.zeros(1 << n)
        for s in range(MIN_SEGNI_B, MAX_SEGNI_B + 1):
            sel = popc == s
            Ts = T[sel]
            for t in np.unique(Ts):
                p = (Ts >= t).mean()
                mlp[sel & (T == t)] = -np.log10(p)
        tab[nome] = mlp
    return tab


_TAB_B = {}


def tabelle_b():
    if not _TAB_B:
        _TAB_B.update(_tabelle_b())
    return _TAB_B


def presenze(parole_per_segno):
    """parole_per_segno: lista (nell'ordine di D.ORDINE_SEGNI) di liste di parole. Ritorna matrice booleana [W, 10] per le parole
    presenti in MIN_SEGNI_B-MAX_SEGNI_B segni."""
    insiemi = [set(ps) for ps in parole_per_segno]
    tutte = sorted(set().union(*insiemi))
    P = np.array([[w in s for s in insiemi] for w in tutte], dtype=bool) if tutte else np.zeros((0, len(insiemi)), dtype=bool)
    n = P.sum(1)
    return P[(n >= MIN_SEGNI_B) & (n <= MAX_SEGNI_B)]


def statistiche_b(P_per_testo, permutazione=None):
    """Vettore delle statistiche (testi x divisioni x {max, omnibus}); `permutazione` = array di 10 posizioni nuove dei segni."""
    tab = tabelle_b()
    out = []
    for P in P_per_testo:
        if permutazione is None:
            pesi = 2 ** np.arange(P.shape[1])
        else:
            pesi = 2 ** np.asarray(permutazione)
        masche = P.astype(np.int64) @ pesi if len(P) else np.zeros(0, dtype=np.int64)
        for nome in tab:
            ml = tab[nome][masche] if len(masche) else np.zeros(1)
            out += [float(ml.max()), float(ml.sum())]
    return np.array(out)


def nomi_statistiche_b():
    return ['%s|%s|%s' % (t, d, k) for t in ('b1', 'b2') for d in TV.divisioni() for k in ('max', 'omnibus')]


def ricerca_b(parole_et, parole_tutto, k=K_NULLO, seme=44, solo=None):
    """parole_et, parole_tutto: liste (10 segni) di liste di parole. `solo`: elenco di divisioni ammesse (le altre non entrano nel
    massimo). Ritorna dict(p, stat, nome, ...)."""
    Ps = [presenze(parole_et), presenze(parole_tutto)]
    oss = statistiche_b(Ps)
    rng = np.random.default_rng(seme)
    nulli = np.array([statistiche_b(Ps, rng.permutation(len(D.ORDINE_SEGNI))) for _ in range(k)])
    nomi = nomi_statistiche_b()
    ok = [i for i, n in enumerate(nomi) if solo is None or n.split('|')[1] in solo]
    return _esito(oss, nulli, nomi, extra=dict(parole_b1=int(len(Ps[0])), parole_b2=int(len(Ps[1]))), ok=ok)


def _esito(oss, nulli, nomi, extra=None, ok=None):
    ok = list(range(len(nomi))) if ok is None else list(ok)
    if not ok:
        return dict(p=1.0, stat=0.0, nome='', nullo_p95=0.0, K=int(len(nulli)))
    oss, nulli = oss[ok], nulli[:, ok]
    nomi = [nomi[i] for i in ok]
    mu = nulli.mean(0)
    sd = np.maximum(nulli.std(0, ddof=1), 1e-9)
    z = (oss - mu) / sd
    zn = ((nulli - mu) / sd).max(1)
    j = int(np.argmax(z))
    p = (1 + int((zn >= z[j]).sum())) / (len(nulli) + 1)
    out = dict(p=p, stat=float(z[j]), nome=nomi[j], nullo_p95=float(np.quantile(zn, 0.95)), K=int(len(nulli)))
    if extra:
        out.update(extra)
    return out


# ---------------------------------------------------------------- (c) gradi

class Gradi:
    """Le righe di etichetta dei 10 segni e le configurazioni (tavola, rotazione, verso)."""

    def __init__(self, etichette_per_segno, tutte=False):
        """etichette_per_segno: lista (nell'ordine di D.ORDINE_SEGNI) di liste di righe (liste di parole)."""
        self.tav = TV.tavole(tutte)
        self.nomi_tav = list(self.tav)
        self.n_seg = [len(e) for e in etichette_per_segno]
        self.L = sum(self.n_seg)
        self.inizio = np.cumsum([0] + self.n_seg)
        righe = [set(r) for e in etichette_per_segno for r in e]
        conta, segni = {}, {}
        for li, ins in enumerate(righe):
            s = int(np.searchsorted(self.inizio, li, side='right') - 1)
            for w in ins:
                conta[w] = conta.get(w, 0) + 1
                segni.setdefault(w, set()).add(s)
        self.parole = sorted(w for w in conta if conta[w] >= MIN_OCC_C and len(segni[w]) >= MIN_SEGNI_C)
        idx = {w: i for i, w in enumerate(self.parole)}
        self.O = np.zeros((len(self.parole), self.L), dtype=np.float32)
        for li, ins in enumerate(righe):
            for w in ins:
                if w in idx:
                    self.O[idx[w], li] = 1.0
        # classi per configurazione: [tavola, rotazione, verso] x righe
        gradi = np.concatenate([np.floor(np.arange(n) * 30 / n).astype(int) for n in self.n_seg])
        segno_riga = np.concatenate([[s] * n for s, n in enumerate(self.n_seg)])
        nt = len(self.nomi_tav)
        self.conf = [(t, r, v) for t in range(nt) for v in (1, -1) for r in range(30)]
        CL = np.zeros((len(self.conf), self.L), dtype=np.int8)
        Qc = np.zeros((len(self.conf), self.L), dtype=np.float32)
        for c, (t, r, v) in enumerate(self.conf):
            tav = self.tav[self.nomi_tav[t]]
            grado = (v * gradi + r) % 30
            for s, nome in enumerate(D.ORDINE_SEGNI):
                sel = segno_riga == s
                vett = np.array(tav[nome])
                CL[c, sel] = vett[grado[sel]]
                validi = vett[vett >= 0]
                Qc[c, sel] = validi.mean() if len(validi) else 0.0
        self.valid = (CL >= 0).astype(np.float32)
        self.Mx = ((CL == 1).astype(np.float32) - self.valid * Qc)
        self.Mv = self.valid * Qc * (1 - Qc)
        self.tav_di_conf = np.array([t for t, _, _ in self.conf])

    def per_tavola(self, O=None):
        """Per ogni tavola il massimo di |z| su parole, rotazioni, versi (vettore di lunghezza = numero di tavole)."""
        O = self.O if O is None else O
        if len(O) == 0:
            return np.zeros(len(self.nomi_tav))
        num = O @ self.Mx.T
        den2 = O @ self.Mv.T
        z = np.where(den2 > 0.5, np.abs(num) / np.sqrt(np.maximum(den2, 1e-9)), 0.0)          # [W, conf]
        zmax = z.max(0)                                                                       # per configurazione
        return np.array([zmax[self.tav_di_conf == t].max() for t in range(len(self.nomi_tav))])

    def rimescola(self, rng):
        """Nullo: ogni segno ruota di uno scarto a caso e prende un verso a caso."""
        cols = []
        for s, n in enumerate(self.n_seg):
            v = rng.choice([1, -1])
            sc = int(rng.integers(0, max(n, 1)))
            cols.append(self.inizio[s] + (v * np.arange(n) + sc) % n)
        return self.O[:, np.concatenate(cols)]


def ricerca_c(etichette_per_segno, k=K_NULLO, seme=45, tutte=False, solo=None):
    """`solo`: elenco di nomi di tavola ammesse (le altre non entrano nel massimo)."""
    G = Gradi(etichette_per_segno, tutte)
    oss = G.per_tavola()
    rng = np.random.default_rng(seme)
    nulli = np.array([G.per_tavola(G.rimescola(rng)) for _ in range(k)])
    ok = [i for i, n in enumerate(G.nomi_tav) if solo is None or n in solo]
    return _esito(oss, nulli, G.nomi_tav, extra=dict(parole=int(len(G.parole))), ok=ok)


# ---------------------------------------------------------------- dati sintetici per i controlli (nessun testo del manoscritto)

def _zipf(rnd, n_voc, size, esponente=1.0):
    p = 1.0 / np.arange(1, n_voc + 1) ** esponente
    p /= p.sum()
    return rnd.choice(n_voc, size=size, p=p)


def sintetico(layout, seme, famiglia='iid', eco=0.2, n_voc=120):
    """Zodiaco finto con la layout del manoscritto (righe di etichetta, parole per riga, parole di cerchi e raggi) e parole 'w<k>'.
    famiglia 'iid': Zipf uguale per tutti i segni; 'tema': ogni segno pesca in una finestra di vocabolario che scivola di 6 parole
    segno dopo segno (i segni vicini si somigliano: le abitudini di grafia). `eco`: probabilita' di ripetere una parola della
    stessa riga o della riga prima. Ritorna (etichette_per_segno, altro_per_segno)."""
    rnd = np.random.default_rng(seme)
    et_tot, altro_tot = [], []
    for i, nome in enumerate(D.ORDINE_SEGNI):
        lay = layout[nome]
        off = 6 * i if famiglia == 'tema' else 0
        et, prima = [], []
        for nw in lay['n_parole_et']:
            riga = []
            for _ in range(nw):
                if prima and rnd.random() < eco:
                    riga.append(prima[rnd.integers(len(prima))])
                else:
                    riga.append('w%d' % (off + int(_zipf(rnd, n_voc, 1)[0])))
            et.append(riga)
            prima = riga
        altro = []
        for _ in range(lay['n_altro']):
            if altro and rnd.random() < eco:
                altro.append(altro[rnd.integers(len(altro))])
            else:
                altro.append('w%d' % (off + int(_zipf(rnd, n_voc, 1)[0])))
        et_tot.append(et)
        altro_tot.append(altro)
    return et_tot, altro_tot


def pianta_segni(et, altro, seme, divisione, parole_per_classe=5, quota=0.8):
    """Pianta (b): per ogni classe della `divisione` (nome) con almeno 2 segni, `parole_per_classe` parole di classe che compaiono
    (due volte) in ognuno dei segni della classe con probabilita' `quota`, in nessun altro segno. Ritorna (et, altro) modificati."""
    rnd = np.random.default_rng(seme)
    classi12 = TV.divisioni()[divisione]
    classi = [classi12[r] for r in RUOTA_SEGNI]
    et = [[list(r) for r in e] for e in et]
    altro = [list(a) for a in altro]
    for c in sorted(set(classi)):
        membri = [j for j, x in enumerate(classi) if x == c]
        if len(membri) < 2:
            continue
        for g in range(parole_per_classe):
            w = 'cw%s_%d_%d' % (divisione[:3], c, g)
            for j in membri:
                if rnd.random() < quota:
                    for _ in range(2):
                        if rnd.random() < 0.5 and et[j]:
                            r = et[j][rnd.integers(len(et[j]))]
                            r[rnd.integers(len(r))] = w
                        elif altro[j]:
                            altro[j][rnd.integers(len(altro[j]))] = w
    return et, altro


def pianta_gradi(et, seme, tavola, frazione, parole_per_classe=3, rotazioni_per_segno=False):
    """Pianta (c): una rotazione r0 e un verso v0 COMUNI (a caso); per ogni riga di etichetta, con probabilita' `frazione`, la sua
    prima parola diventa una parola di classe (una fra `parole_per_classe` per classe 1 e altrettante per classe 0) secondo la
    `tavola` (nome) al suo grado; i gradi esclusi non cambiano. Con `rotazioni_per_segno` ogni segno ha la sua rotazione (schema che
    la ricerca non puo' vedere: serve a dichiararne il limite). Ritorna (et modificato, (r0, v0))."""
    rnd = np.random.default_rng(seme)
    tav = TV.tavole(True)[tavola]
    r0 = int(rnd.integers(0, 30))
    v0 = int(rnd.choice([1, -1]))
    out = []
    for nome, righe in zip(D.ORDINE_SEGNI, et):
        n = len(righe)
        r = int(rnd.integers(0, 30)) if rotazioni_per_segno else r0
        righe = [list(x) for x in righe]
        for i in range(n):
            d = int(np.floor(i * 30 / n))
            cl = tav[nome][(v0 * d + r) % 30]
            if cl >= 0 and righe[i] and rnd.random() < frazione:
                righe[i][0] = 'gw%d_%d' % (cl, rnd.integers(parole_per_classe))
        out.append(righe)
    return out, (r0, v0)
