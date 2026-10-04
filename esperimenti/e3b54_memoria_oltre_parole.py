# -*- coding: utf-8 -*-
"""Esperimento e3b54: memoria corta normalizzata (vicine − lontane) contro un nullo che rimescola le varianti solo fra
le occorrenze dello stesso tipo di parola nella stessa unità (tiene ferme parole, locuzioni e preferenze). Voynich e
varianti naturali (þ/ð, i/y).

Preregistrazione: preregistrazioni/e3b54.md. Scrive risultati/e3b54_memoria_oltre_parole.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b51_thorn_eth as e3b51

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000
VICINE, LONTANE = (2, 3), tuple(range(6, 11))
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
TH = ('þ', 'ð')
STORICI = OrderedDict([('Hatton Gospels', 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels.txt'),
                       ('Secreta Alberti', 'Historical - English - Technical - Secreta Alberti.txt'),
                       ('NT fiammingo', 'Historical - Flemish - Literary - NT.txt')])


# --- classi: parola -> (valore, tipo coperto) oppure None ---

def v_qo(w):
    x = e380.ini_qo(w)
    return (1 if x[1] == 'qo' else 0, ('Q',) + x[0]) if x else None


def singola(w, coppia, uno, altre_vietate=None):
    pos = [i for i, s in enumerate(w) if s in coppia]
    if len(pos) != 1:
        return None
    if altre_vietate and any(s in altre_vietate for i, s in enumerate(w) if i != pos[0]):
        return None
    return (1 if w[pos[0]] == uno else 0, w[:pos[0]] + ('*',) + w[pos[0] + 1:])


def v_kt(w):
    return singola(w, ('k', 't'), 'k', GALLOWS)


def v_shch(w):
    return singola(w, ('sh', 'ch'), 'sh')


def v_eydy(w):
    y = e380.fin_dyey(w)
    return (1 if y[1] == 'e' else 0, y[0] + ('*', 'y')) if y else None


def v_th_ini(w):
    return (1 if w[0] == 'þ' else 0, ('*',) + w[1:]) if w and w[0] in TH else None


def v_th_int(w):
    pos = [i for i, s in enumerate(w) if i and s in TH]
    return (1 if w[pos[0]] == 'þ' else 0, w[:pos[0]] + ('*',) + w[pos[0] + 1:]) if len(pos) == 1 else None


def classe_iy(righe, min_occ=3):
    c = Counter(w for r in righe for w in r)
    val = {}
    conflitti = set()
    for w, f in c.items():
        if f < min_occ:
            continue
        for i, s in enumerate(w):
            if s != 'i':
                continue
            w2 = w[:i] + ('y',) + w[i + 1:]
            if c.get(w2, 0) >= min_occ:
                cop = w[:i] + ('*',) + w[i + 1:]
                for x, v in ((w, 0), (w2, 1)):
                    if x in val and val[x] != (v, cop):
                        conflitti.add(x)
                    val[x] = (v, cop)
    for x in conflitti:
        del val[x]
    return lambda w: val.get(w)


# --- costruzione delle coppie e statistica ---

def prepara(unita, f):
    """unita: [ [sequenze di parole] ]. Ritorna dizionario di array per la classe f."""
    val, grp, gruppi = [], [], {}
    I, J, G, Tp, Up = [], [], [], [], []
    for u, seqs in enumerate(unita):
        idx_unit = []
        segn = []
        for s in seqs:
            ids = []
            for w in s:
                x = f(w)
                if x is None:
                    ids.append(None)
                    continue
                k = len(val)
                val.append(x[0])
                grp.append(gruppi.setdefault((u, x[1]), len(gruppi)))
                ids.append(k)
                idx_unit.append(k)
            segn.append((s, ids))
        T = len(idx_unit)
        U = sum(val[k] for k in idx_unit)
        for s, ids in segn:
            for i in range(len(s)):
                if ids[i] is None:
                    continue
                for d in VICINE + LONTANE:
                    j = i + d
                    if j >= len(s) or ids[j] is None:
                        continue
                    if s[i] == s[j] or e3a86.una_modifica(s[i], s[j]):
                        continue
                    if T - 2 < 5:
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if d in VICINE else 1)
                    Tp.append(T)
                    Up.append(U)
    return dict(val=np.array(val, dtype=float), grp=np.array(grp), I=np.array(I, dtype=int), J=np.array(J, dtype=int),
                G=np.array(G), T=np.array(Tp, dtype=float), U=np.array(Up, dtype=float))


def somme(c, val):
    vi, vj = val[c['I']], val[c['J']]
    p = (c['U'] - vi - vj) / (c['T'] - 2)
    att = p * p + (1 - p) * (1 - p)
    ok = (vi == vj).astype(float)
    out = []
    for g in (0, 1):
        m = c['G'] == g
        out.append((ok[m].sum(), att[m].sum(), m.sum()))
    return out


def emme(ss):
    """ss: lista di somme per classe -> M dell'insieme."""
    k = []
    for g in (0, 1):
        o = sum(s[g][0] for s in ss)
        a = sum(s[g][1] for s in ss)
        n = sum(s[g][2] for s in ss)
        if n - a <= 0:
            return None
        k.append((o - a) / (n - a))
    return k[0] - k[1]


def rimescola(c, rng):
    n = len(c['val'])
    order = np.lexsort((rng.random(n), c['grp']))
    pos = np.argsort(c['grp'], kind='stable')
    nuovo = np.empty(n)
    nuovo[pos] = c['val'][order]
    return nuovo


def prova(classi, rng):
    """classi: {nome: dati}. Ritorna risultati per classe e per l'insieme."""
    oss = {k: somme(c, c['val']) for k, c in classi.items()}
    nul = {k: [] for k in classi}
    nul_ins = []
    for _ in range(PERM):
        ss = {}
        for k, c in classi.items():
            ss[k] = somme(c, rimescola(c, rng))
            nul[k].append(emme([ss[k]]))
        nul_ins.append(emme(list(ss.values())))
    out = OrderedDict()

    def riga(m, nn, coppie):
        nn = [x for x in nn if x is not None]
        if m is None or not nn:
            return OrderedDict([('M', None), ('nullo', None), ('effetto', None), ('p', None), ('z', None), ('coppie_vicine', coppie[0]), ('coppie_lontane', coppie[1])])
        mu = float(np.mean(nn))
        return OrderedDict([('M', m), ('nullo', mu), ('effetto', m - mu), ('p', float(np.mean([x >= m for x in nn]))),
                            ('z', (m - mu) / float(np.std(nn)) if np.std(nn) > 0 else 0.0), ('coppie_vicine', coppie[0]), ('coppie_lontane', coppie[1])])
    for k in classi:
        out[k] = riga(emme([oss[k]]), nul[k], (int(oss[k][0][2]), int(oss[k][1][2])))
    out['insieme'] = riga(emme(list(oss.values())), nul_ins, (int(sum(s[0][2] for s in oss.values())), int(sum(s[1][2] for s in oss.values()))))
    return out


def esito(p, si, no):
    return si if p < 0.01 else (no if p > 0.05 else 'incerto')


def main():
    rng = np.random.default_rng(3254)
    voy = []
    for pg, pars in e341.pagine().items():
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            voy.append(rr)
    cv = OrderedDict([('qo/o', v_qo), ('k/t', v_kt), ('sh/ch', v_shch), ('-ey/-dy', v_eydy)])
    rv = prova(OrderedDict((k, prepara(voy, f)) for k, f in cv.items()), rng)
    print('Voynich', json.dumps(rv, ensure_ascii=False), flush=True)
    tt = e381.testi()
    cn = OrderedDict()
    for nome, chiave in STORICI.items():
        righe = [r for r in tt[chiave] if r]
        unita = [[b] for b in e3b51.blocchi(righe)]
        cn['%s, i/y' % nome] = prepara(unita, classe_iy(righe))
        if nome == 'Hatton Gospels':
            cn['Hatton Gospels, þ/ð a inizio parola'] = prepara(unita, v_th_ini)
            cn['Hatton Gospels, þ/ð dentro la parola'] = prepara(unita, v_th_int)
    rn = prova(cn, rng)
    print('naturali', json.dumps(rn, ensure_ascii=False), flush=True)
    e1 = esito(rv['insieme']['p'], 'memoria oltre le preferenze delle parole', 'non oltre')
    e2 = esito(rn['insieme']['p'], 'memoria anche negli scribi veri', 'non si vede negli scribi veri')
    out = OrderedDict([('Voynich', rv), ('naturali', rn), ('esito_Voynich', e1), ('esito_naturali', e2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b54_memoria_oltre_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b54 — Memoria corta oltre le preferenze delle parole', '', 'Preregistrazione: `preregistrazioni/e3b54.md`. M = K(vicine) − K(lontane); nullo = varianti rimescolate fra le occorrenze dello stesso tipo di parola nella stessa unità.', '',
          '| testo, classe | coppie vicine | M osservata | M nullo | effetto | z | p |', '|---|---|---|---|---|---|---|']
    for gruppo, r in (('Voynich', rv), ('', rn)):
        for k, x in r.items():
            nome = ('Voynich, ' + k) if gruppo else ('naturali, insieme' if k == 'insieme' else k)
            if x['M'] is None:
                md.append('| %s | %d | n.d. | | | | |' % (nome, x['coppie_vicine']))
                continue
            md.append('| %s | %d | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (nome, x['coppie_vicine'], x['M'], x['nullo'], x['effetto'], x['z'], x['p']))
    md += ['', 'Esito Voynich: **%s**. Esito varianti naturali: **%s**.' % (e1, e2)]
    open(os.path.join(RISULTATI, 'e3b54_memoria_oltre_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
