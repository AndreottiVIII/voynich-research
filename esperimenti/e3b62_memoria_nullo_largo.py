# -*- coding: utf-8 -*-
"""Esperimento e3b62: memoria delle scelte oltre le parole con un nullo che rimescola le varianti fra le occorrenze della
stessa parola coperta in tutto lo strato (mano o testo), ricalcolando l'atteso delle unità a ogni rimescolamento.

Preregistrazione: preregistrazioni/e3b62.md. Scrive risultati/e3b62_memoria_nullo_largo.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np
from scipy.stats import chi2

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e134_generatori_esterni as e134
import e337_posizione as e337
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000
CV = OrderedDict([('qo/o', e3b54.v_qo), ('k/t', e3b54.v_kt), ('sh/ch', e3b54.v_shch), ('-ey/-dy', e3b54.v_eydy)])


def prepara(unita, strati, f):
    """unita: [ [sequenze di parole] ]; strati: [strato di ogni unità]. Gruppi = (strato, tipo coperto)."""
    val, grp, uni, gruppi = [], [], [], {}
    I, J, G = [], [], []
    for u, seqs in enumerate(unita):
        for s in seqs:
            ids, cop = [], []
            for w in s:
                x = f(w)
                if x is None:
                    ids.append(None)
                    cop.append(None)
                    continue
                ids.append(len(val))
                cop.append(x[1])
                val.append(x[0])
                grp.append(gruppi.setdefault((strati[u], x[1]), len(gruppi)))
                uni.append(u)
            for i in range(len(ids)):
                if ids[i] is None:
                    continue
                for d in e3b54.VICINE + e3b54.LONTANE:
                    j = i + d
                    if j >= len(ids) or ids[j] is None:
                        continue
                    if cop[i] == cop[j] or e3a86.una_modifica(cop[i], cop[j]):
                        continue
                    I.append(ids[i])
                    J.append(ids[j])
                    G.append(0 if d in e3b54.VICINE else 1)
    uni = np.array(uni, dtype=int)
    T = np.bincount(uni, minlength=len(unita)).astype(float)
    I, J = np.array(I, dtype=int), np.array(J, dtype=int)
    ok = (T[uni[I]] - 2 >= 5) if len(I) else np.array([], dtype=bool)
    gsize = np.bincount(np.array(grp, dtype=int)) if grp else np.array([])
    v = np.array(val, dtype=float)
    misti = 0
    if len(v):
        s1 = np.bincount(np.array(grp), weights=v)
        mix = (gsize >= 2) & (s1 > 0) & (s1 < gsize)
        misti = int(gsize[mix].sum())
    return dict(val=v, grp=np.array(grp, dtype=int), uni=uni, T=T, I=I[ok], J=J[ok], G=np.array(G)[ok] if len(G) else np.array([]),
                n_unita=len(unita), rimescolabili=misti)


def somme(c, val):
    if not len(c['I']):
        return [(0.0, 0.0, 0), (0.0, 0.0, 0)]
    U = np.bincount(c['uni'], weights=val, minlength=c['n_unita'])
    vi, vj = val[c['I']], val[c['J']]
    u = c['uni'][c['I']]
    p = (U[u] - vi - vj) / (c['T'][u] - 2)
    att = p * p + (1 - p) * (1 - p)
    okk = (vi == vj).astype(float)
    out = []
    for g in (0, 1):
        m = c['G'] == g
        out.append((okk[m].sum(), att[m].sum(), int(m.sum())))
    return out


def prova(classi, rng):
    oss = {k: somme(c, c['val']) for k, c in classi.items()}
    nul = {k: [] for k in classi}
    nul_ins = []
    for _ in range(PERM):
        ss = {}
        for k, c in classi.items():
            ss[k] = somme(c, e3b54.rimescola(c, rng) if len(c['val']) else c['val'])
            nul[k].append(e3b54.emme([ss[k]]))
        nul_ins.append(e3b54.emme(list(ss.values())))
    out = OrderedDict()

    def riga(m, nn, coppie, rim, tot):
        nn = [x for x in nn if x is not None]
        if m is None or not nn:
            return OrderedDict([('M', None), ('effetto', None), ('p', None), ('coppie_vicine', coppie)])
        mu, sd = float(np.mean(nn)), float(np.std(nn))
        return OrderedDict([('M', m), ('nullo', mu), ('effetto', m - mu), ('dev_nullo', sd), ('z', (m - mu) / sd if sd > 0 else 0.0),
                            ('p', float(np.mean([x >= m for x in nn]))), ('coppie_vicine', coppie), ('quota_rimescolabile', rim / tot if tot else None)])
    for k, c in classi.items():
        out[k] = riga(e3b54.emme([oss[k]]), nul[k], oss[k][0][2], c['rimescolabili'], len(c['val']))
    out['insieme'] = riga(e3b54.emme(list(oss.values())), nul_ins, sum(s[0][2] for s in oss.values()),
                          sum(c['rimescolabili'] for c in classi.values()), sum(len(c['val']) for c in classi.values()))
    return out


def voynich(pagine_dict, mano, solo=None):
    unita, strati = [], []
    for pg, pars in pagine_dict.items():
        h = mano.get(pg)
        if not h or (solo and h != solo):
            continue
        rr = [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        if rr:
            unita.append(rr)
            strati.append(h)
    return unita, strati


def main():
    rng = np.random.default_rng(3262)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    zl, it = e341.pagine(), e3b45.pagine_it()
    ris = OrderedDict()
    for nome, pd, solo in (('Voynich ZL, mano 1', zl, '1'), ('Voynich ZL, mano 2', zl, '2'), ('Voynich ZL, mano 3', zl, '3'),
                           ('Voynich ZL, tutto', zl, None), ('Voynich IT, tutto', it, None)):
        uu, ss = voynich(pd, mano, solo)
        ris[nome] = prova(OrderedDict((k, prepara(uu, ss, f)) for k, f in CV.items()), rng)
        print(nome, json.dumps(ris[nome]['insieme']), flush=True)
    tt = e381.testi()
    cn = OrderedDict()
    for nome, chiave in e3b54.STORICI.items():
        righe = [r for r in tt[chiave] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        ss = [nome] * len(uu)
        cn['%s, i/y' % nome] = prepara(uu, ss, e3b54.classe_iy(righe))
        if nome == 'Hatton Gospels':
            cn['Hatton Gospels, þ/ð a inizio parola'] = prepara(uu, ss, e3b54.v_th_ini)
            cn['Hatton Gospels, þ/ð dentro la parola'] = prepara(uu, ss, e3b54.v_th_int)
    ris['varianti naturali'] = prova(cn, rng)
    print('naturali', json.dumps(ris['varianti naturali']['insieme']), flush=True)
    gen = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            gen[k] = [r for r in ([w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v) if r]
    gen['Timm e Schinner, seme 1'] = [r for r in ([tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r]
    for k, righe in gen.items():
        uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
        ris[k] = prova(OrderedDict((c, prepara(uu, [k] * len(uu), f)) for c, f in CV.items()), rng)
        print(k, json.dumps(ris[k]['insieme']), flush=True)
    es = OrderedDict()
    mani = [ris['Voynich ZL, mano %s' % h]['insieme'] for h in '123']
    w = np.array([1 / x['dev_nullo'] ** 2 for x in mani])
    e = np.array([x['effetto'] for x in mani])
    media = float((w * e).sum() / w.sum())
    Q = float((w * (e - media) ** 2).sum())
    pq = float(chi2.sf(Q, 2))
    if all(x['p'] < 0.05 for x in mani):
        es['mani'] = 'in tutte le mani' + ('; le mani differiscono' if pq < 0.01 else '')
    else:
        es['mani'] = 'le mani differiscono' if pq < 0.01 else 'differenze non dimostrate'
    for k in ('Voynich ZL, tutto', 'Voynich IT, tutto'):
        es[k] = 'memoria oltre le parole' if ris[k]['insieme']['p'] < 0.01 else 'non dimostrata'
    pn = ris['varianti naturali']['insieme']['p']
    es['varianti naturali'] = 'memoria anche negli scribi veri' if pn < 0.01 else ('non si vede' if pn > 0.05 else 'incerto')
    ev = ris['Voynich ZL, tutto']['insieme']['effetto']
    for k in gen:
        x = ris[k]['insieme']
        es[k] = 'nessuna memoria' if x['p'] > 0.05 else ('memoria come il Voynich' if x['p'] < 0.01 and x['effetto'] >= ev / 2 else 'debole')
    out = OrderedDict([('gruppi', ris), ('eterogeneita_mani', OrderedDict([('media', media), ('Q', Q), ('p', pq)])), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b62_memoria_nullo_largo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b62 — Memoria oltre le parole con il nullo largo (rimescolamento nello strato)', '', 'Preregistrazione: `preregistrazioni/e3b62.md`.', '',
          '| gruppo | classe | coppie vicine | quota rimescolabile | M | M nullo | effetto | z | p |', '|---|---|---|---|---|---|---|---|---|']
    for g, r in ris.items():
        for k, x in r.items():
            if x['M'] is None:
                md.append('| %s | %s | %d | | n.d. | | | | |' % (g, k, x['coppie_vicine']))
                continue
            md.append('| %s | %s | %d | %.2f | %+.4f | %+.4f | %+.4f | %+.1f | %.3f |' % (g, k, x['coppie_vicine'], x['quota_rimescolabile'] or 0, x['M'], x['nullo'], x['effetto'], x['z'], x['p']))
    md += ['', 'Eterogeneità fra le mani 1, 2, 3: Q = %.2f, p = %.4f.' % (Q, pq), ''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b62_memoria_nullo_largo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
