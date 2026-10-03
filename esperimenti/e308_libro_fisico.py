# -*- coding: utf-8 -*-
"""Esperimenti 308, 309, 312: le pagine e il libro fisico. (e308) quale unita' fisica condivide l'identita' di pagina
(stesso foglio, apertura, bifoglio); (e309) l'asse -edy/-aiin: due modi o un continuo, e come si muove lungo il libro;
(e312) ricostruire l'ordine delle pagine dalle somiglianze.

Preregistrazione: preregistrazioni/e308.md. Scrive risultati/e308_libro_fisico.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e307_identita_pagine as e307

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000


def intestazioni():
    """{pagina: {'Q':..., 'F':..., 'B':..., 'lato': 'r'/'v', 'ordine': n}} dalle intestazioni di pagina della ZL."""
    percorso = os.path.join(trascrizione.CARTELLA, trascrizione.FILE['ZL'])
    out = OrderedDict()
    for linea in open(percorso, encoding='latin-1'):
        m = re.match(r'^<(f\w+)>\s+<!(.*)>', linea)
        if m:
            p = m.group(1)
            var = dict(re.findall(r'\$(\w)=(\S+)', m.group(2)))
            lato = re.match(r'^f\d+([rv])', p)
            out[p] = {'Q': var.get('Q'), 'F': var.get('F'), 'B': var.get('B'), 'lato': lato.group(1) if lato else '?', 'ordine': len(out)}
    return out


def profili():
    """Come l'e307: Testo del Voynich, caratteristiche grezze X, profili P (scarti dallo strato / deviazione del nullo)."""
    rnd = random.Random(307)
    pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            x = pag.setdefault(r.pagina, {'nome': r.pagina, 'strato': (r.sezione or '?', r.lingua or '?'), 'mano': r.mano or '?', 'fascicolo': r.quire or '?', 'parole': []})
            x['parole'] += [w for w in r.parole if trascrizione.pulita(w)]
    for k, x in enumerate(pag.values()):
        x['posizione'] = k
    voy = e307.Testo(list(pag.values()), e307.D, e307.INIZIALI_V, e307.FINALI_V)
    S, W, N = voy.somme(voy.parola)
    X, nomi = voy.caratteristiche(S, N)
    R = voy.scarti(X)
    vn = []
    for _ in range(e307.NULLI):
        S2, _, N2 = voy.somme(voy.rimescola(rnd))
        vn.append(voy.scarti(voy.caratteristiche(S2, N2)[0]).var(0))
    sd = np.sqrt(np.array(vn).mean(0))
    return voy, X, nomi, R / np.maximum(sd, 1e-12)


def permutazione_strati(voy, rnd):
    pi = np.arange(len(voy.pagine))
    for idx in voy.strati.values():
        x = list(idx)
        rnd.shuffle(x)
        pi[idx] = x
    return pi


def e308(voy, P, testa):
    n = len(voy.pagine)
    info = [testa.get(p['nome'], {}) for p in voy.pagine]
    ordine_file = sorted(testa, key=lambda p: testa[p]['ordine'])
    seguente = {a: b for a, b in zip(ordine_file, ordine_file[1:])}
    nomi = [p['nome'] for p in voy.pagine]
    classi = defaultdict(list)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = info[i], info[j]
            if not a or not b or a['Q'] is None or b['Q'] is None:
                continue
            if a['Q'] == b['Q'] and a['F'] == b['F']:
                classi['stesso foglio' if a['lato'] != b['lato'] else 'stesso foglio, stesso lato (pannelli)'].append((i, j))
            elif (seguente.get(nomi[i]) == nomi[j] and a['lato'] == 'v' and b['lato'] == 'r') or (seguente.get(nomi[j]) == nomi[i] and b['lato'] == 'v' and a['lato'] == 'r'):
                classi['apertura'].append((i, j))
            elif a['Q'] == b['Q'] and a['B'] == b['B']:
                prima, seconda = (a, b) if a['ordine'] < b['ordine'] else (b, a)
                stessa = (prima['lato'], seconda['lato']) in (('r', 'v'), ('v', 'r'))
                classi['bifoglio, stessa faccia' if stessa else 'bifoglio, facce opposte'].append((i, j))
            elif a['Q'] == b['Q']:
                classi['stesso fascicolo, altro'].append((i, j))
    C = np.corrcoef(P)
    coppie = {k: (np.array([x for x, _ in v]), np.array([y for _, y in v])) for k, v in classi.items() if v}
    rnd = random.Random(308)
    nulli = defaultdict(list)
    diff_null = []
    for _ in range(PERM):
        pi = permutazione_strati(voy, rnd)
        m = {k: C[pi[I], pi[J]].mean() for k, (I, J) in coppie.items()}
        for k, v in m.items():
            nulli[k].append(v)
        if 'stesso foglio' in m and 'apertura' in m:
            diff_null.append(m['stesso foglio'] - m['apertura'])
    out = OrderedDict()
    for k, (I, J) in coppie.items():
        v = float(C[I, J].mean())
        mu, sd = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('coppie', len(I)), ('correlazione', v), ('nullo', mu), ('z', (v - mu) / sd if sd else 0.0)])
    d = None
    if 'stesso foglio' in out and 'apertura' in out:
        dv = out['stesso foglio']['correlazione'] - out['apertura']['correlazione']
        d = OrderedDict([('differenza', dv), ('z', (dv - statistics.mean(diff_null)) / statistics.pstdev(diff_null))])
    unita = [k for k, v in out.items() if v['z'] > 3]
    return OrderedDict([('classi', out), ('foglio_contro_apertura', d), ('unita_fisiche', unita)])


def e309(voy, X, nomi):
    from sklearn.mixture import GaussianMixture
    col = {n: k for k, n in enumerate(nomi)}
    Z = (X - X.mean(0)) / np.maximum(X.std(0), 1e-12)
    s = Z[:, col['segno e']] + Z[:, col['finale y']] - Z[:, col['segno a']] - Z[:, col['segno n']] - Z[:, col['finale n']]
    bic = []
    for k in (1, 2):
        g = GaussianMixture(n_components=k, random_state=309).fit(s.reshape(-1, 1))
        bic.append(g.bic(s.reshape(-1, 1)))
    lingua = [p['strato'][1] for p in voy.pagine]
    a = np.array([x for x, l in zip(s, lingua) if l == 'A'])
    b = np.array([x for x, l in zip(s, lingua) if l == 'B'])
    sov_a = float((a > np.percentile(b, 25)).mean())
    sov_b = float((b < np.percentile(a, 75)).mean())
    if (bic[1] < bic[0] - 10) and sov_a < 0.05 and sov_b < 0.05:
        modi = 'due modi'
    elif sov_a > 0.20 or sov_b > 0.20 or bic[0] <= bic[1]:
        modi = 'continuo'
    else:
        modi = 'intermedio'
    # nel tempo, dentro lo strato
    res = s.copy()
    seq = []
    for st, idx in voy.strati.items():
        idx = sorted(idx, key=lambda i: voy.pagine[i]['posizione'])
        res[idx] = s[idx] - s[idx].mean()
        seq.append(idx)

    def autocorr(vals, lag):
        xs, ys = [], []
        for idx in seq:
            for i in range(len(idx) - lag):
                xs.append(vals[idx[i]])
                ys.append(vals[idx[i + lag]])
        return float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 2 else 0.0
    rnd = random.Random(309)
    passi = (1, 2, 3, 5, 10)
    vero = {L: autocorr(res, L) for L in passi}
    nulli = defaultdict(list)
    for _ in range(PERM):
        r2 = res.copy()
        for idx in seq:
            x = r2[idx].copy()
            rnd.shuffle(x)
            r2[idx] = x
        for L in passi:
            nulli[L].append(autocorr(r2, L))
    ac = OrderedDict((L, OrderedDict([('autocorrelazione', vero[L]), ('z', (vero[L] - statistics.mean(nulli[L])) / statistics.pstdev(nulli[L]))])) for L in passi)
    if ac[1]['z'] < 2:
        tempo = 'nessuna traccia'
    elif ac[1]['z'] > 3 and ac[5]['autocorrelazione'] >= ac[1]['autocorrelazione'] / 2:
        tempo = 'deriva lenta'
    elif ac[1]['z'] > 3:
        tempo = 'coppie di pagine'
    else:
        tempo = 'incerto'
    lungo = [(voy.pagine[i]['nome'], voy.pagine[i]['strato'][1], round(float(s[i]), 2)) for i in sorted(range(len(s)), key=lambda i: voy.pagine[i]['posizione'])]
    return OrderedDict([('BIC_1_2', bic), ('sovrapposizione_A_verso_B', sov_a), ('sovrapposizione_B_verso_A', sov_b), ('modi', modi),
                        ('media_A', float(a.mean())), ('media_B', float(b.mean())), ('autocorrelazione', ac), ('tempo', tempo), ('punteggi_nell_ordine', lungo)])


def e312(voy, P):
    from scipy.stats import spearmanr
    C = np.corrcoef(P)

    def fiedler(idx, Pm):
        Cm = np.corrcoef(Pm[idx])
        Sm = np.maximum(Cm, 0)
        np.fill_diagonal(Sm, 0)
        L = np.diag(Sm.sum(1)) - Sm
        w, v = np.linalg.eigh(L)
        return v[:, 1]
    rnd = random.Random(312)
    strati = OrderedDict()
    zz = []
    for st, idx in voy.strati.items():
        if len(idx) < 15:
            continue
        idx = sorted(idx, key=lambda i: voy.pagine[i]['posizione'])
        pos = [voy.pagine[i]['posizione'] for i in idx]
        rho = abs(spearmanr(fiedler(idx, P), pos).correlation)
        nulli = []
        for _ in range(200):
            x = list(idx)
            rnd.shuffle(x)
            Pp = P.copy()
            Pp[idx] = P[x]
            nulli.append(abs(spearmanr(fiedler(idx, Pp), pos).correlation))
        z = (rho - statistics.mean(nulli)) / statistics.pstdev(nulli)
        strati['%s-%s' % st] = OrderedDict([('pagine', len(idx)), ('rho', rho), ('nullo', statistics.mean(nulli)), ('z', z)])
        zz.append(z)
    Z = sum(zz) / np.sqrt(len(zz)) if zz else 0.0
    esito = 'l\'ordine del libro si ritrova' if Z > 3 else ('no' if Z < 2 else 'incerto')
    cand = []
    pos_di = {i: p['posizione'] for i, p in enumerate(voy.pagine)}
    per_pos = {p['posizione']: i for i, p in enumerate(voy.pagine)}
    for st, idx in voy.strati.items():
        for i in idx:
            altri = sorted((j for j in idx if j != i), key=lambda j: -C[i, j])[:3]
            lontani = all(abs(pos_di[j] - pos_di[i]) > 20 for j in altri)
            vic = [per_pos[pos_di[i] + d] for d in (-1, 1) if pos_di[i] + d in per_pos]
            mv = statistics.mean(C[i, j] for j in vic) if vic else None
            if lontani and mv is not None and mv < 0:
                cand.append(OrderedDict([('pagina', voy.pagine[i]['nome']), ('simili', [voy.pagine[j]['nome'] for j in altri]),
                                         ('correlazione_con_le_vicine', round(float(mv), 3))]))
    return OrderedDict([('strati', strati), ('Z', Z), ('esito', esito), ('candidate_fuori_posto', cand)])


def main():
    testa = intestazioni()
    voy, X, nomi, P = profili()
    print('pagine %d' % len(voy.pagine), flush=True)
    r308 = e308(voy, P, testa)
    print('e308', {k: (v['coppie'], round(v['correlazione'], 3), round(v['z'], 1)) for k, v in r308['classi'].items()}, r308['foglio_contro_apertura'], flush=True)
    r309 = e309(voy, X, nomi)
    print('e309', r309['modi'], r309['BIC_1_2'], round(r309['sovrapposizione_A_verso_B'], 2), round(r309['sovrapposizione_B_verso_A'], 2), r309['tempo'],
          {L: (round(v['autocorrelazione'], 3), round(v['z'], 1)) for L, v in r309['autocorrelazione'].items()}, flush=True)
    r312 = e312(voy, P)
    print('e312', r312['esito'], round(r312['Z'], 1), {k: (round(v['rho'], 2), round(v['z'], 1)) for k, v in r312['strati'].items()}, len(r312['candidate_fuori_posto']), flush=True)
    json.dump(OrderedDict([('e308', r308), ('e309', r309), ('e312', r312)]), open(os.path.join(RISULTATI, 'e308_libro_fisico.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1, default=str)
    md = ['# e308, e309, e312 — Le pagine e il libro fisico', '', 'Preregistrazione: `preregistrazioni/e308.md`. %d pagine (come l\'e307).' % len(voy.pagine), '',
          '## e308 — Quale unità fisica condivide l\'identità', '', '| coppie | numero | correlazione | nullo | z |', '|---|---|---|---|---|']
    for k, v in r308['classi'].items():
        md.append('| %s | %d | %.3f | %.3f | %.1f |' % (k, v['coppie'], v['correlazione'], v['nullo'], v['z']))
    d = r308['foglio_contro_apertura']
    md += ['', 'Stesso foglio contro apertura: %s.' % ('differenza %+.3f, z %.1f' % (d['differenza'], d['z']) if d else 'non calcolabile'),
           'Unità fisiche (z > 3): **%s**.' % (', '.join(r308['unita_fisiche']) or 'nessuna'), '', '## e309 — L\'asse -edy/-aiin', '',
           'BIC 1 componente %.1f, 2 componenti %.1f; media A %.2f, B %.2f; pagine A con punteggio sopra il 25° percentile delle B %.0f%%, pagine B sotto il 75° delle A %.0f%%. Esito: **%s**.' % (
               r309['BIC_1_2'][0], r309['BIC_1_2'][1], r309['media_A'], r309['media_B'], 100 * r309['sovrapposizione_A_verso_B'], 100 * r309['sovrapposizione_B_verso_A'], r309['modi']),
           '', '| passo | autocorrelazione | z |', '|---|---|---|']
    for L, v in r309['autocorrelazione'].items():
        md.append('| %d | %.3f | %.1f |' % (L, v['autocorrelazione'], v['z']))
    md += ['', 'Nel tempo: **%s**.' % r309['tempo'], '', '## e312 — L\'ordine dalle somiglianze', '', '| strato | pagine | ρ | nullo | z |', '|---|---|---|---|---|']
    for k, v in r312['strati'].items():
        md.append('| %s | %d | %.2f | %.2f | %.1f |' % (k, v['pagine'], v['rho'], v['nullo'], v['z']))
    md += ['', 'Z complessivo %.1f: **%s**.' % (r312['Z'], r312['esito']), '',
           'Pagine candidate fuori posto (più simili a pagine lontane che alle vicine): %s.' % ('; '.join('%s (simili: %s; con le vicine %.2f)' % (
               c['pagina'], ', '.join(c['simili']), c['correlazione_con_le_vicine']) for c in r312['candidate_fuori_posto']) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e308_libro_fisico.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
