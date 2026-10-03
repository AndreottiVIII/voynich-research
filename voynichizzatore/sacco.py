# -*- coding: utf-8 -*-
"""Il sacco di pagina: quali parole stanno in ogni pagina (e404).

Parole note (viste almeno due volte nel libro): pescate dal lessico della sezione e lingua della pagina (occorrenze delle
altre pagine), con ripetizione dentro la pagina: a ogni parola, con probabilita' n/(n+theta) si ripete una parola nota gia'
messa nella pagina (n = quante ce ne sono), altrimenti si pesca dal lessico. theta = None: nessuna ripetizione (K1).
Parole nuove: vere, oppure inventate da parole_nuove.FormeUniche (T-LPS) nei posti delle parole uniche vere.
"""
import bisect, itertools, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))


class Sacco:
    """rr: righe (pagina, inizio paragrafo, parole) del Voynich; tipo: pagina -> (sezione, lingua)."""

    def __init__(self, rr, tipo):
        self.rr, self.tipo = rr, tipo
        self.conta = Counter(w for _, _, ps in rr for w in ps)
        note = OrderedDict()
        for p, _, ps in rr:
            note.setdefault(p, []).extend(w for w in ps if self.conta[w] >= 2)
        self.pagine = list(note)
        self.lessico = {}
        for p in self.pagine:
            serb = [w for q in self.pagine if q != p and tipo[q] == tipo[p] for w in note[q]]
            if len(serb) < 500:
                serb = [w for q in self.pagine if q != p and tipo[q][0] == tipo[p][0] for w in note[q]]
            if len(serb) < 500:
                serb = [w for q in self.pagine if q != p for w in note[q]]
            self.lessico[p] = serb
        self._fu = None
        self.note = note
        self._car = {}

    # --- carattere della pagina (e404b) ---
    ALFA = 50.0

    def _segni(self, parole):
        import misure
        if not hasattr(self, '_D'):
            self._D = misure.divisore(misure.GLIFI_EVA)
            self._cache_segni = {}
        c = Counter()
        for w in parole:
            u = self._cache_segni.get(w)
            if u is None:
                u = self._cache_segni[w] = Counter(self._D(w))
            c.update(u)
        return c

    def carattere(self, p, rnd):
        """Scostamenti dei segni (logaritmo del rapporto con la sezione) di un'altra pagina vera, a caso, della stessa
        sezione e lingua; e il lessico di sezione della pagina p come (tipi, conteggi, segni per tipo)."""
        if p not in self._car:
            cs = Counter(self.lessico[p])
            tipi = sorted(cs)
            self._segni(tipi)
            fs = self._segni(self.lessico[p])
            n = sum(fs.values())
            self._car[p] = (tipi, [cs[w] for w in tipi], {g: x / n for g, x in fs.items()})
        tipi, conti, fsez = self._car[p]
        altre = [q for q in self.pagine if q != p and self.tipo[q] == self.tipo[p] and len(self.note[q]) >= 40]
        altre = altre or [q for q in self.pagine if q != p and len(self.note[q]) >= 40]
        q = altre[rnd.randrange(len(altre))]
        cq = self._segni(self.note[q])
        nq = sum(cq.values())
        delta = {g: math.log((cq[g] + self.ALFA * f) / (nq + self.ALFA) / f) for g, f in fsez.items()}
        return tipi, conti, delta

    def pesi_carattere(self, tipi, conti, delta, kappa):
        pesi = [c * math.exp(kappa * sum(delta.get(g, 0.0) * k for g, k in self._cache_segni[w].items())) for w, c in zip(tipi, conti)]
        return list(itertools.accumulate(pesi))

    def forme(self):
        if self._fu is None:
            import parole_nuove
            self._fu = parole_nuove.FormeUniche(self.rr)
        self._fu.usate = set()
        return self._fu

    def genera(self, seme, theta=None, nuove='vere', kappa=None):
        """Il testo con le parole note pescate (e, con nuove='inventate', le uniche sostituite); stessa impaginazione.
        kappa: forza del carattere della pagina (None: nessun carattere, e le parole nuove seguono il profilo della pagina
        vera, come nell'e404; con kappa le parole nuove seguono il profilo delle parole note generate)."""
        from disposizione import posizione
        rnd = random.Random(seme)
        fu = self.forme() if nuove == 'inventate' else None
        per = OrderedDict()
        for i, (p, _, _) in enumerate(self.rr):
            per.setdefault(p, []).append(i)
        out = {}
        for p, idx in per.items():
            gia = []
            serb = self.lessico[p]
            if kappa is not None:
                tipi, conti, delta = self.carattere(p, rnd)
                cum = self.pesi_carattere(tipi, conti, delta, kappa)
            righe = {}
            for i in idx:
                riga = []
                for w in self.rr[i][2]:
                    if self.conta[w] >= 2:
                        if theta is not None and gia and rnd.random() < len(gia) / (len(gia) + theta):
                            w = gia[rnd.randrange(len(gia))]
                        elif kappa is not None:
                            w = tipi[bisect.bisect(cum, rnd.random() * cum[-1])]
                        else:
                            w = serb[rnd.randrange(len(serb))]
                        gia.append(w)
                    riga.append(w)
                righe[i] = riga
            if fu:
                profilo = fu.profilo(gia if kappa is not None else [w for i in idx for w in self.rr[i][2]])
                for i in idx:
                    _, ini, ps = self.rr[i]
                    for j, w in enumerate(ps):
                        if self.conta[w] == 1:
                            righe[i][j] = fu.inventa('T-LPS', 4 * bool(ini) + posizione(j, len(ps)), profilo, rnd)
            for i in idx:
                out[i] = (p, self.rr[i][1], righe[i])
        return [out[i] for i in range(len(self.rr))]
