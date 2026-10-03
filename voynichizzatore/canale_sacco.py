# -*- coding: utf-8 -*-
"""Il messaggio nel sacco (e409): il testo cifrato sceglie, pagina per pagina, quante volte compare ogni parola nota.

Il sacco delle parole note di una pagina e' un campione multinomiale dal lessico di sezione pesato dal carattere della
pagina (sacco.py). Dato il numero n di posti per parole note, i conteggi si estraggono tipo per tipo, in ordine fisso, come
catena di binomiali; ogni binomiale e' codificata una decisione alla volta ("ancora una?") con la codifica aritmetica
binaria di v1 (Nasconditore sceglie dai bit del messaggio, Rilettore rilegge i bit dai conteggi).
Dalla chiave, e non dal messaggio, vengono: la pagina tipo di ogni pagina, i posti delle parole nuove, le parole nuove, la
disposizione. Ogni pagina e ogni uso ha un generatore suo, cosi' la decodifica ricalcola solo le distribuzioni.

    codifica(testo, chiave, versione) -> righe, informazioni        decodifica(righe, chiave, versione) -> testo
"""
import json, math, os, random, sys, zlib
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import pezzi, v0, v1

SCALA = 1 << 40          # i pesi dei tipi diventano interi su questa scala


def generatore(chiave, pagina, uso):
    return random.Random(v0.numero(chiave, 'sacco|%s|%s' % (uso, pagina)))


def distribuzione(s, pagina, chiave, kappa):
    """I tipi del lessico della pagina, dal piu' pesante, con i pesi interi; e la pagina tipo scelta dalla chiave."""
    tipi, conti, delta = s.carattere(pagina, generatore(chiave, pagina, 'carattere'))
    tipo_pagina = s.pagina_tipo
    cum = s.pesi_carattere(tipi, conti, delta, kappa)
    pesi = [cum[0]] + [b - a for a, b in zip(cum, cum[1:])]
    tot = cum[-1]
    interi = [max(1, int(round(x / tot * SCALA))) for x in pesi]
    ordine = sorted(range(len(tipi)), key=lambda i: (-interi[i], tipi[i]))
    return [tipi[i] for i in ordine], [interi[i] for i in ordine], tipo_pagina


def _passi(n, p):
    """Per una binomiale(n, p): le frequenze f0 (su v1.TOT) di 'mi fermo a j' dato che sono arrivato a j, j = 0, 1, ..."""
    q = 1.0 - p
    pmf = math.exp(n * math.log(q)) if q > 0 else 0.0
    resto = 1.0
    j = 0
    while j < n:
        h = pmf / resto if resto > 0 else 1.0
        yield min(v1.TOT - 1, max(1, int(round(h * v1.TOT))))
        resto -= pmf
        pmf = pmf * (n - j) / (j + 1) * (p / q) if q > 0 else 0.0
        j += 1
        if resto <= 0:
            resto = 1e-300


def conteggi_dai_bit(nasc, interi, n):
    """I conteggi dei tipi (stesso ordine dei pesi) estratti dai bit del messaggio; la somma e' n."""
    out, resta, W = [], n, sum(interi)
    for k, w in enumerate(interi):
        if resta == 0:
            out.append(0)
            continue
        if k == len(interi) - 1:
            out.append(resta)
            resta = 0
            continue
        c = 0
        for f0 in _passi(resta, w / W):
            if nasc.simbolo(f0) == 0:
                break
            c += 1
        out.append(c)
        resta -= c
        W -= w
    return out


def bit_dai_conteggi(ril, interi, conteggi):
    resta, W = sum(conteggi), sum(interi)
    for k, (w, c) in enumerate(zip(interi, conteggi)):
        if resta == 0 or k == len(interi) - 1:
            break
        j = 0
        for f0 in _passi(resta, w / W):
            if j == c:
                ril.simbolo(0, f0)
                break
            ril.simbolo(1, f0)
            j += 1
        resta -= c
        W -= w


class Conta:
    """Conta i bit consumati dal Nasconditore."""
    def __init__(self, bit):
        self.bit, self.n = iter(bit), 0

    def __iter__(self):
        return self

    def __next__(self):
        self.n += 1
        return next(self.bit)


def codifica(testo, chiave, versione='v9', parametri=None, verifica=True):
    """Il manoscritto con il testo nascosto nei conteggi delle parole note. testo=None: soli bit di riempimento."""
    from disposizione import posizione
    x = parametri or json.load(open(pezzi.PARAMETRI % versione, encoding='utf-8'))
    s, d = pezzi.pezzi()
    s.FORME = dict(x['forme'])
    s.POSIZIONALE = x.get('carattere') == 'posizionale'
    fu = s.forme()
    if testo is None:
        cifrati, riempitivo, nbyte = [], v0.flusso_chiave(600000, chiave), 0
    else:
        cifrati, riempitivo, nbyte = v1.bit_del_messaggio(testo, chiave)
    flusso = Conta(cifrati + riempitivo)
    nasc = v1.Nasconditore(flusso)
    per = OrderedDict()
    for i, (p, _, _) in enumerate(s.rr):
        per.setdefault(p, []).append(i)
    out, consumati = {}, []
    for p, idx in per.items():
        tipi, interi, tipo_pagina = distribuzione(s, p, chiave, x['kappa'])
        rm = generatore(chiave, p, 'posti')
        m = s.molt_pagina[tipo_pagina]
        nuovo = {}
        for i in idx:
            _, ini, ps = s.rr[i]
            nuovo[i] = [rm.random() < min(0.95, s.quota_posto[4 * bool(ini) + posizione(j, len(ps))] * m) for j in range(len(ps))]
        n = sum(not b for i in idx for b in nuovo[i])
        conteggi = conteggi_dai_bit(nasc, interi, n)
        note = [w for w, c in zip(tipi, conteggi) for _ in range(c)]
        generatore(chiave, p, 'ordine').shuffle(note)
        rn = generatore(chiave, p, 'nuove')
        profilo = fu.profilo(note)
        per_lung = None
        if fu.unioni:
            s._segni(set(note))
            per_lung = {}
            for w in sorted(set(note)):
                per_lung.setdefault(sum(s._cache_segni[w].values()), []).append(w)
        k = 0
        for i in idx:
            _, ini, ps = s.rr[i]
            riga = []
            for j in range(len(ps)):
                if nuovo[i][j]:
                    riga.append(fu.inventa('T-LPS', 4 * bool(ini) + posizione(j, len(ps)), profilo, rn, per_lung))
                else:
                    riga.append(note[k])
                    k += 1
            out[i] = (p, ini, riga)
        consumati.append(flusso.n)
    righe = d.disponi([out[i] for i in range(len(s.rr))], v0.numero(chiave, 'sacco|disposizione') % (1 << 31), 'D3', pesi=x['pesi_disposizione'])
    capacita = flusso.n - v1.PREC
    info = OrderedDict([('bit_messaggio', len(cifrati)), ('capacita_bit', capacita), ('byte_compressi', nbyte),
                        ('byte_testo', len(testo.encode('utf-8')) if testo is not None else 0),
                        ('pagine_usate', sum(c - v1.PREC < len(cifrati) for c in [0] + consumati[:-1]) if cifrati else 0), ('pagine', len(per))])
    if testo is not None:
        if len(cifrati) > capacita:
            raise SystemExit('testo troppo lungo per questo libro: servono %d bit, il libro ne porta %d' % (len(cifrati), capacita))
        if verifica and decodifica(righe, chiave, versione, parametri) != testo:
            raise SystemExit('errore: la decodifica di controllo non restituisce il testo')
    return righe, info


def decodifica(righe, chiave, versione='v9', parametri=None):
    x = parametri or json.load(open(pezzi.PARAMETRI % versione, encoding='utf-8'))
    s, _ = pezzi.pezzi()
    s.POSIZIONALE = x.get('carattere') == 'posizionale'
    per = OrderedDict()
    for p, _, ps in righe:
        per.setdefault(p, []).extend(ps)
    ril = v1.Rilettore()
    for p in OrderedDict((q, 1) for q, _, _ in s.rr):
        tipi, interi, _ = distribuzione(s, p, chiave, x['kappa'])
        noti = set(tipi)
        c = Counter(w for w in per.get(p, []) if w in noti)
        bit_dai_conteggi(ril, interi, [c[w] for w in tipi])
    bit = ril.bit
    ks = v0.flusso_chiave(len(bit), chiave)
    testa = [b ^ k for b, k in zip(bit[:32], ks[:32])]
    n = int.from_bytes(v0.da_bit(testa), 'big')
    if not 0 < n <= (len(bit) - 32) // 8:
        raise ValueError('chiave sbagliata o manoscritto senza messaggio')
    corpo = [b ^ k for b, k in zip(bit[32:32 + 8 * n], ks[32:32 + 8 * n])]
    return zlib.decompress(v0.da_bit(corpo)).decode('utf-8')
