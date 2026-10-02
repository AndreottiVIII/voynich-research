# -*- coding: utf-8 -*-
"""Esperimento 147: il testo si adatta allo spazio sulla pagina? Lunghezza delle parole e densita' dei segni nelle righe
che cominciano dopo un disegno; regolarita' del margine destro contro un riempimento simulato. Riquadri di
voynichese.com (lrozanova/voynich-units).

Preregistrazione: preregistrazioni/e147.md. Scrive risultati/e147_spazio_immagini.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure
import e34_spazi_fisici as e34

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, BOOT = 147, 2000, 2000
D = misure.divisore(misure.GLIFI_EVA)


def pagine_di_testo():
    import trascrizione
    from collections import Counter
    zl = trascrizione.leggi('ZL')
    n = Counter(r.pagina for r in zl if r.tipo and r.tipo[0] == 'P')
    sez = {r.pagina: r.sezione for r in zl}
    return {p for p, k in n.items() if k >= 8 and sez.get(p) not in ('Z', 'A', 'C')}


def pagine():
    out = OrderedDict()
    ammesse = pagine_di_testo()
    for f in sorted(os.listdir(e34.RIQUADRI)):
        if not f.endswith('.js') or f[:-3] not in ammesse:
            continue
        rq = e34.riquadri(f[:-3])
        righe = {}
        for t in rq:
            righe.setdefault(t['riga'], []).append(t)
        rr = [r for r in righe.values() if len(r) >= 3]
        if len(rr) < 8:
            continue
        inizi = [r[0]['x'] for r in rr]
        fini = [r[-1]['x'] + r[-1]['w'] for r in rr]
        L, M = float(np.percentile(inizi, 10)), float(np.percentile(fini, 95))
        if M - L <= 0:
            continue
        spazi = [b['x'] - (a['x'] + a['w']) for r in rr for a, b in zip(r, r[1:]) if b['x'] - (a['x'] + a['w']) >= 0]
        out[f[:-3]] = {'righe': rr, 'L': L, 'M': M, 'W': M - L, 'spazio': float(np.median(spazi)) if spazi else 0.0}
    return out


def lun(w):
    return len(D(w))


def classi(p):
    L, W = p['L'], p['W']
    sp, no = [], []
    for k, r in enumerate(p['righe']):
        if r[0]['x'] > L + 0.15 * W:
            sp.append(k)
        elif r[0]['x'] <= L + 0.05 * W:
            no.append(k)
    return sp, no


def diff_lunghezza(pp, parole_righe):
    num = den = 0.0
    for nome, (sp, no) in pp.items():
        ps, pn = [lun(w) for k in sp for w in parole_righe[nome][k]], [lun(w) for k in no for w in parole_righe[nome][k]]
        if ps and pn:
            n = len(ps) + len(pn)
            num += n * (statistics.mean(ps) - statistics.mean(pn))
            den += n
    return num / den if den else None


def prova1(P, rnd):
    pp = {n: classi(p) for n, p in P.items()}
    pp = {n: c for n, c in pp.items() if c[0] and c[1]}
    parole = {n: [[t['parola'] for t in r] for r in P[n]['righe']] for n in pp}
    reale = diff_lunghezza(pp, parole)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = {}
        for n, rr in parole.items():
            tutte = [w for r in rr for w in r]
            rnd.shuffle(tutte)
            it = iter(tutte)
            mes[n] = [[next(it) for _ in r] for r in rr]
        nulli.append(diff_lunghezza(pp, mes))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('pagine', len(pp)), ('righe_spostate', sum(len(c[0]) for c in pp.values())), ('righe_normali', sum(len(c[1]) for c in pp.values())),
                        ('differenza_segni', reale), ('nullo', m), ('z', (reale - m) / s if s else None)])


def prova2(P, rnd):
    per = []
    for n, p in P.items():
        sp, no = classi(p)
        if not sp or not no:
            continue
        dens = lambda ks: sum(lun(t['parola']) for k in ks for t in p['righe'][k]) / max(1, sum(t['w'] for k in ks for t in p['righe'][k]))
        per.append(dens(sp) - dens(no))
    reale = statistics.mean(per)
    bb = sorted(statistics.mean(rnd.choices(per, k=len(per))) for _ in range(BOOT))
    return OrderedDict([('pagine', len(per)), ('differenza_densita', reale), ('iv', [bb[int(0.05 * BOOT)], bb[int(0.95 * BOOT)]])])


def sd_fini(fini, L, W):
    v = [f for f in fini if f >= L + 0.6 * W]
    return statistics.pstdev(v) / W if len(v) >= 3 else None


def simula(p):
    L, M, sp = p['L'], p['M'], p['spazio']
    fini, x = [], None
    for r in p['righe']:
        for t in r:
            if x is None:
                x = L + t['w']
            elif x + sp + t['w'] <= M:
                x += sp + t['w']
            else:
                fini.append(x)
                x = L + t['w']
    if x is not None:
        fini.append(x)
    return fini


def prova3(P, rnd):
    oss, sim = [], []
    for n, p in P.items():
        o = sd_fini([r[-1]['x'] + r[-1]['w'] for r in p['righe']], p['L'], p['W'])
        s = sd_fini(simula(p), p['L'], p['W'])
        if o is not None and s:
            oss.append(o)
            sim.append(s)
    rap = statistics.mean(oss) / statistics.mean(sim)
    idx = list(range(len(oss)))
    bb = []
    for _ in range(BOOT):
        c = rnd.choices(idx, k=len(idx))
        bb.append(statistics.mean(oss[i] for i in c) / statistics.mean(sim[i] for i in c))
    bb.sort()
    return OrderedDict([('pagine', len(oss)), ('sd_osservata', statistics.mean(oss)), ('sd_simulata', statistics.mean(sim)), ('rapporto', rap),
                        ('iv', [bb[int(0.05 * BOOT)], bb[int(0.95 * BOOT)]])])


def main():
    rnd = random.Random(SEME)
    P = pagine()
    print('pagine usate: %d' % len(P), flush=True)
    ris = OrderedDict([('pagine', len(P))])
    ris['(1) lunghezza delle parole nelle righe spostate'] = p1 = prova1(P, rnd)
    ris['(2) densita dei segni nelle righe spostate'] = p2 = prova2(P, rnd)
    ris['(3) margine destro'] = p3 = prova3(P, rnd)
    for k, v in ris.items():
        print(k, json.dumps(v, ensure_ascii=False), flush=True)
    accorciate = (p1['z'] or 0) < -3
    compressione = p2['differenza_densita'] > 0 and p2['iv'][0] > 0
    allineamento = p3['rapporto'] < 0.7 and p3['iv'][1] < 0.7
    ris['parole_accorciate'], ris['compressione'], ris['allineamento_attivo'] = accorciate, compressione, allineamento
    print('parole accorciate %s | compressione %s | allineamento attivo %s' % (accorciate, compressione, allineamento))
    with open(os.path.join(RISULTATI, 'e147_spazio_immagini.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e147 — Il testo si adatta allo spazio?', '', 'Riquadri delle parole di voynichese.com (lrozanova/voynich-units). Preregistrazione: `preregistrazioni/e147.md`.', '',
           '- **(1)** %d pagine, %d righe spostate, %d normali: differenza di lunghezza media %+.3f segni (nullo %+.3f, z %.1f).' % (
               p1['pagine'], p1['righe_spostate'], p1['righe_normali'], p1['differenza_segni'], p1['nullo'], p1['z'] or 0),
           '- **(2)** %d pagine: differenza di densità (segni per pixel) %+.4f [%.4f, %.4f].' % (p2['pagine'], p2['differenza_densita'], *p2['iv']),
           '- **(3)** %d pagine: dispersione delle fini di riga %.4f osservata contro %.4f simulata; rapporto %.2f [%.2f, %.2f].' % (
               p3['pagine'], p3['sd_osservata'], p3['sd_simulata'], p3['rapporto'], *p3['iv']),
           '', 'Parole accorciate: **%s**. Compressione: **%s**. Allineamento attivo: **%s**.' % tuple('sì' if x else 'no' for x in (accorciate, compressione, allineamento))]
    with open(os.path.join(RISULTATI, 'e147_spazio_immagini.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
