# -*- coding: utf-8 -*-
"""Il "voynichizzatore": trasforma un testo qualsiasi in voynichese, e lo ritrasforma con la chiave.

Non nasconde il messaggio in un angolo: e' il messaggio a scegliere ogni parola. Il testo e' un campione del
modello generativo senza messaggio (e192/e224), reso esplicito:
- struttura di pagine, paragrafi e lunghezze di riga presa dalle pagine vere, nell'ordine;
- prima parola di riga dalle parole d'inizio del Voynich (di riga o di paragrafo, per lingua A/B), con
  l'evitamento del primo segno della riga sopra;
- parole successive dal serbatoio della pagina (pesi frequenza^ALFA), con un tema di pagina, varianti
  (attestate o nuove ben formate), copia dalla parola della riga sopra, peso di giuntura con la parola
  precedente, ch/sh favoriti in seconda posizione, regola di fine riga;
- le cinque scelte di grafia (ch/sh, k/t, -l/-r, qo-/o-, -dy/-ey) con le abitudini di riga (memoria fra
  righe, ripartenza a pagina), applicate a ogni parola candidata.

La scelta di ogni parola si fa con la codifica aritmetica: il messaggio, compresso e cifrato con la chiave
(quindi indistinguibile da bit casuali), fa da "dado". Chi ha la chiave rifa' lo stesso modello passo per passo,
ricostruisce gli intervalli e quindi i bit. Senza chiave il testo e' un campione del modello come un altro
(steganografia per codifica aritmetica: Ziegler, Deng e Rush 2019).

Uso:
    python analisi/voynichizzatore.py codifica "testo" [chiave]   -> voynichese (righe; riga vuota fra pagine)
    python analisi/voynichizzatore.py decodifica file.txt [chiave] -> testo
"""
import hashlib, math, os, random, sys, zlib
from collections import Counter, OrderedDict
from fractions import Fraction

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))

TOT = 1 << 16                 # precisione delle frequenze intere
TEMA, MASSA_TEMA, MASSA_VAR, MASSA_SOPRA = 3, 0.3, 0.15, 0.1
VARIANTI, ALFA, LAM, ETA, BANCO = 2, 1.0, 1.5, 2.0, 2.0
RHO, SIGMA = 0.6, 0.8
_C = {}


# ---------------------------------------------------------------- contesto (dal Voynich)

def contesto():
    if _C:
        return _C
    import generatori, misure, trascrizione
    import e71_bordo_riga as e71
    import e131_procedimento_riga as e131
    import e145_abitudini as e145
    import e152_righe_in_ordine as e152
    D = misure.divisore(misure.GLIFI_EVA)
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    fine, dentro = Counter(), Counter()
    for _, ps in e71.righe_voynich():
        pp = [w for w in ps if trascrizione.pulita(w)]
        if len(pp) >= 3:
            fine[D(pp[-1])[-1]] += 1
            dentro.update(D(w)[-1] for w in pp[1:-1])
    nf, nd, k = sum(fine.values()), sum(dentro.values()), len(set(fine) | set(dentro))
    rapporto = {g: ((fine[g] + 1) / (nf + k)) / ((dentro[g] + 1) / (nd + k)) for g in set(fine) | set(dentro)}
    _C.update(D=D, pulita=trascrizione.pulita, att=set(voy), mod=generatori.Modifiche(voy, D), P=list(e145.pagine().items()),
              starts=e131.inizi(), q=e145.quote(), L=e152.lift(), rapporto=rapporto, riscrivi=e145.riscrivi, scelte=e145.SCELTE)
    return _C


def rng(chiave, *parti):
    h = hashlib.sha256(('%s|' % chiave + '|'.join(map(str, parti))).encode()).digest()
    return random.Random(int.from_bytes(h[:8], 'big'))


# ---------------------------------------------------------------- messaggio <-> bit (compresso e cifrato)

def _flusso(chiave, n):
    out, i = b'', 0
    while len(out) < n:
        out += hashlib.sha256(('flusso|%s|%d' % (chiave, i)).encode()).digest()
        i += 1
    return out[:n]


def a_bit(testo, chiave):
    grezzo = testo.encode('utf-8')
    compresso = zlib.compress(grezzo, 9)
    dati = (b'\x01' + compresso) if len(compresso) < len(grezzo) else (b'\x00' + grezzo)
    dati = len(dati).to_bytes(4, 'big') + dati
    cif = bytes(a ^ b for a, b in zip(dati, _flusso(chiave, len(dati))))
    return [(b >> i) & 1 for b in cif for i in range(7, -1, -1)]


def da_numero(lo, chiave):
    """lo: estremo inferiore dell'intervallo finale (Fraction in [0,1))."""
    def byte_da(k):          # i primi k byte del messaggio cifrato
        return int(lo * (1 << (8 * k))).to_bytes(k, 'big')
    testa = bytes(a ^ b for a, b in zip(byte_da(4), _flusso(chiave, 4)))
    n = int.from_bytes(testa, 'big')
    cif = byte_da(4 + n)
    dati = bytes(a ^ b for a, b in zip(cif, _flusso(chiave, 4 + n)))[4:]
    return (zlib.decompress(dati[1:]) if dati[:1] == b'\x01' else dati[1:]).decode('utf-8')


# ---------------------------------------------------------------- il modello

def _variante(w, c, r):
    u = tuple(c['D'](w))
    for _ in range(1 + (r.random() < 0.3)):
        x = c['mod'].modifica(u, r)
        if ''.join(x) in c['att'] or c['mod'].valida(x):
            u = x
    return ''.join(u)


def _riscrivi(w, i, n, h, c, chiave, pag, k):
    righe = ['*'] * n
    righe[i] = w
    return c['riscrivi'](righe, h, c['q'], rng(chiave, 'grafia', pag, k, i, w))[i]


def _quantizza(pesi):
    """pesi: OrderedDict parola -> peso > 0. -> (parole, frequenze intere che sommano a TOT, cumulate)."""
    parole = list(pesi)
    tot = sum(pesi.values())
    f = [max(1, int(TOT * pesi[w] / tot)) for w in parole]
    d = TOT - sum(f)
    i = max(range(len(f)), key=lambda j: f[j])
    f[i] += d
    if f[i] < 1:
        raise ValueError('quantizzazione impossibile')
    cum = [0]
    for x in f:
        cum.append(cum[-1] + x)
    return parole, f, cum


class Pagina:
    def __init__(self, c, chiave, ip, pag, d):
        self.c, self.chiave, self.ip, self.pag = c, chiave, ip, pag
        D = c['D']
        pool = [w for _, ps in d['righe'] for w in ps[1:] if c['pulita'](w)] or [w for _, ps in d['righe'] for w in ps if c['pulita'](w)]
        cnt = Counter(pool)
        self.base = OrderedDict((w, cnt[w] ** ALFA) for w in sorted(cnt))
        r = rng(chiave, 'tema', ip)
        tipi = list(self.base)
        self.tema = set(r.choices(tipi, [self.base[t] for t in tipi], k=TEMA))
        self.varianti = OrderedDict()
        for w in tipi:
            rv = rng(chiave, 'var', ip, w)
            for _ in range(VARIANTI):
                v = _variante(w, c, rv)
                if v != w and c['pulita'](v):
                    self.varianti[v] = self.varianti.get(v, 0) + self.base[w]
        self.lingua = d['lingua'] if d['lingua'] in c['starts'] else 'B'
        self.righe = d['righe']

    def distribuzione(self, k, i, n, ini, riga, sopra, prima_sopra, h):
        """Distribuzione (dopo le abitudini di grafia) della parola in posizione i della riga k."""
        c, D = self.c, self.c['D']
        pesi = OrderedDict()
        if i == 0:
            parole, cont = c['starts'][self.lingua][1 if ini else 0]
            for w, x in zip(parole, cont):
                p = float(x)
                if prima_sopra is not None and D(w)[0] == prima_sopra:
                    p *= 0.5
                pesi[w] = pesi.get(w, 0) + p
        else:
            Wb = sum(self.base.values())
            Wt = sum(self.base[t] for t in self.tema) or 1.0
            Wv = sum(self.varianti.values()) or 1.0
            m_sopra = MASSA_SOPRA if sopra is not None and i < len(sopra) and c['pulita'](sopra[i]) else 0.0
            for w, x in self.base.items():
                pesi[w] = (1 - MASSA_TEMA - MASSA_VAR - m_sopra) * x / Wb + (MASSA_TEMA * x / Wt if w in self.tema else 0)
            for w, x in self.varianti.items():
                pesi[w] = pesi.get(w, 0) + MASSA_VAR * x / Wv
            if m_sopra:
                pesi[sopra[i]] = pesi.get(sopra[i], 0) + m_sopra
            ultimo = D(riga[-1])[-1]
            for w in list(pesi):
                u = D(w)
                p = pesi[w] * c['L'].get((ultimo, u[0]), 0.05) ** LAM
                if i == 1 and u[0] in ('ch', 'sh'):
                    p *= BANCO
                if i == n - 1:
                    p *= c['rapporto'].get(u[-1], 1.0) ** ETA
                pesi[w] = p
        finali = OrderedDict()
        for w, p in pesi.items():
            if p > 0:
                f = _riscrivi(w, i, n, h, c, self.chiave, self.ip, k)
                finali[f] = finali.get(f, 0) + p
        return _quantizza(finali)


def _abitudini(c, chiave):
    return {f: 0.0 for f in c['scelte']}


def _passo_abitudini(h, c, chiave, ip, k, pagina_nuova):
    r = rng(chiave, 'abitudini', ip, k)
    for f in c['scelte']:
        h[f] = (RHO / 2 if pagina_nuova else RHO) * h[f] + r.gauss(0, SIGMA)


# ---------------------------------------------------------------- codifica e decodifica

def codifica(testo, chiave='voynich'):
    c = contesto()
    bit = a_bit(testo, chiave)
    n = len(bit)
    M = int(''.join(map(str, bit)), 2)
    basso, alto = Fraction(M, 1 << n), Fraction(M + 1, 1 << n)
    x = Fraction(2 * M + 1, 1 << (n + 1))
    lo, w = Fraction(0), Fraction(1)
    pagine, finito = [], False
    h = _abitudini(c, chiave)
    ip = 0
    while not finito:
        pag, d = c['P'][ip % len(c['P'])]
        pg = Pagina(c, chiave, ip, pag, d)
        righe_out, sopra, prima_sopra = [], None, None
        for k, (ini, ps) in enumerate(d['righe']):
            _passo_abitudini(h, c, chiave, ip, k, k == 0)
            n_par = len(ps)
            riga = []
            for i in range(n_par):
                parole, f, cum = pg.distribuzione(k, i, n_par, ini, riga, sopra, prima_sopra, h)
                t = (x - lo) * TOT / w
                s = next(j for j in range(len(parole)) if cum[j] <= t < cum[j + 1])
                lo, w = lo + w * Fraction(cum[s], TOT), w * Fraction(f[s], TOT)
                riga.append(parole[s])
            righe_out.append(riga)
            prima_sopra = c['D'](riga[0])[0]
            sopra = riga
            if lo >= basso and lo + w <= alto:
                finito = True       # si completa comunque la pagina
        pagine.append(righe_out)
        ip += 1
    return pagine


def decodifica(pagine, chiave='voynich'):
    c = contesto()
    lo, w = Fraction(0), Fraction(1)
    h = _abitudini(c, chiave)
    for ip, righe_in in enumerate(pagine):
        pag, d = c['P'][ip % len(c['P'])]
        pg = Pagina(c, chiave, ip, pag, d)
        sopra, prima_sopra = None, None
        for k, ((ini, ps), riga_in) in enumerate(zip(d['righe'], righe_in)):
            _passo_abitudini(h, c, chiave, ip, k, k == 0)
            n_par = len(ps)
            riga = []
            for i in range(n_par):
                parole, f, cum = pg.distribuzione(k, i, n_par, ini, riga, sopra, prima_sopra, h)
                s = parole.index(riga_in[i])
                lo, w = lo + w * Fraction(cum[s], TOT), w * Fraction(f[s], TOT)
                riga.append(riga_in[i])
            prima_sopra = c['D'](riga[0])[0]
            sopra = riga
    return da_numero(lo, chiave)


def a_testo(pagine):
    return '\n\n'.join('\n'.join(' '.join(r) for r in p) for p in pagine) + '\n'


def da_testo(s):
    return [[r.split() for r in blocco.split('\n') if r.strip()] for blocco in s.strip().split('\n\n')]


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'codifica':
        print(a_testo(codifica(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'voynich')), end='')
    elif len(sys.argv) >= 3 and sys.argv[1] == 'decodifica':
        print(decodifica(da_testo(open(sys.argv[2], encoding='utf-8').read()), sys.argv[3] if len(sys.argv) > 3 else 'voynich'))
    else:
        print(__doc__)
