# -*- coding: utf-8 -*-
"""Esperimenti 331, 332, 333. (e331) l'ultimo blocco di righe del recto somiglia al primo del verso piu' dei blocchi
lontani, su tutti i fogli? (e332) nell'erbario in lingua A gli argomenti dei paragrafi (LDA sulle forme normalizzate)
sono locali nel libro o tornano lontano? (e333) dentro la pagina l'abitudine di grafia cambia sempre nella stessa
direzione dall'alto in basso?

Preregistrazione: preregistrazioni/e331.md. Scrive risultati/e331_tempo.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e308_libro_fisico as e308
import e327_stato_pagina as e327
import e328_livelli as e328

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000
NOMI_SCELTE = ['ch/sh', 'k/t (gallows)', '-l/-r', 'o-/qo-', '-dy/-ey']


def standard(pag):
    pp = [p for p in pag if sum(len(ws) for par in pag[p] for _, ws in par) >= 60]
    vals = [e327.somma([e327.riga_stat(ws) for par in pag[p] for _, ws in par])[0] for p in pp]
    mu = {k: statistics.mean(v[k] for v in vals) for k in vals[0]}
    sd = {k: statistics.pstdev(v[k] for v in vals) for k in vals[0]}
    return lambda v: (v['e'] - mu['e']) / sd['e'] + (v['fy'] - mu['fy']) / sd['fy'] - (v['a'] - mu['a']) / sd['a'] - (v['n'] - mu['n']) / sd['n'] - (v['fn'] - mu['fn']) / sd['fn']


def segno_flip(diffs, rnd):
    vero = statistics.mean(diffs)
    nul = []
    for _ in range(PERM):
        nul.append(statistics.mean(d * rnd.choice((-1, 1)) for d in diffs))
    return vero, (vero - statistics.mean(nul)) / (statistics.pstdev(nul) or 1)


def e331(pag, testa, punt, rnd):
    righe = {p: [ws for par in pars for _, ws in par] for p, pars in pag.items()}
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seg = dict(zip(ordine, ordine[1:]))
    fogli, aperture = [], []
    for p in pag:
        h, q = testa.get(p), seg.get(p)
        if not h or not q or q not in pag:
            continue
        if h['lato'] == 'r' and testa[q]['lato'] == 'v' and testa[q]['F'] == h['F']:
            fogli.append((p, q))
        elif h['lato'] == 'v' and testa[q]['lato'] == 'r':
            aperture.append((p, q))

    def dist(b1, b2):
        s1, c1 = e327.somma([e327.riga_stat(ws) for ws in b1])
        s2, c2 = e327.somma([e327.riga_stat(ws) for ws in b2])
        l1 = Counter(e328.normalizza(w) for ws in b1 for w in ws)
        l2 = Counter(e328.normalizza(w) for ws in b2 for w in ws)
        return e327.jsd(c1, c2), abs(punt(s1) - punt(s2)), e328.jsd_counter(l1, l2)

    def prova(coppie, k):
        diffs = []
        for a, b in coppie:
            ra, rb = righe[a], righe[b]
            if len(ra) < 2 * k or len(rb) < 2 * k:
                continue
            vic = dist(ra[-k:], rb[:k])
            lon = dist(ra[:k], rb[-k:])
            diffs.append([lon[j] - vic[j] for j in range(3)])
        if len(diffs) < 5:
            return OrderedDict([('coppie', len(diffs))])
        out = OrderedDict([('coppie', len(diffs))])
        for j, nome in enumerate(('segni', 'asse', 'lessico')):
            v, z = segno_flip([d[j] for d in diffs], rnd)
            out['lontana_meno_vicina_' + nome] = v
            out['z_' + nome] = z
        return out
    r = OrderedDict([('fogli, blocchi di 4', prova(fogli, 4)), ('aperture, blocchi di 4', prova(aperture, 4)),
                     ('fogli, blocchi di 8', prova(fogli, 8)), ('aperture, blocchi di 8', prova(aperture, 8))])
    z = r['fogli, blocchi di 4'].get('z_segni', 0)
    esito = 'scritto di seguito girando il foglio' if z > 3 else ('no' if z < 2 else 'incerto')
    return OrderedDict([('prove', r), ('esito', esito)])


def e332(pag, rnd):
    from sklearn.decomposition import LatentDirichletAllocation
    meta = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        meta.setdefault(r.pagina, (r.sezione or '?', r.lingua or '?', r.quire or '?'))
    pos = {p: i for i, p in enumerate(pag)}
    par = []
    for p, pars in pag.items():
        if meta.get(p, ('?', '?'))[:2] != ('H', 'A'):
            continue
        for x in pars:
            ws = [e328.normalizza(w) for _, r_ in x for w in r_]
            if len(ws) >= 20:
                par.append((p, ws))
    cnt = Counter(w for _, ws in par for w in ws)
    frequenti = {w for w, _ in cnt.most_common(30)}
    voc = sorted(w for w, n in cnt.items() if n >= 5 and w not in frequenti)
    idx = {w: k for k, w in enumerate(voc)}
    M = np.zeros((len(par), len(voc)))
    for i, (_, ws) in enumerate(par):
        for w in ws:
            if w in idx:
                M[i, idx[w]] += 1
    lda = LatentDirichletAllocation(n_components=6, random_state=332, learning_method='batch', max_iter=100).fit(M)
    dom = lda.transform(M).argmax(1)
    pp = [p for p, _ in par]

    P_ = np.array([pos[p] for p in pp])
    G_ = np.array([pos[p] for p in pp])

    def dist_media(lab):
        lab = np.asarray(lab)
        tot = n = 0
        for t in np.unique(lab):
            i = np.where(lab == t)[0]
            d = np.abs(P_[i][:, None] - P_[i][None, :])
            m = np.triu(G_[i][:, None] != G_[i][None, :], 1)
            tot += d[m].sum()
            n += m.sum()
        return float(tot / n)
    vero = dist_media(list(dom))
    nul = []
    for _ in range(PERM):
        lab = list(dom)
        rnd.shuffle(lab)
        nul.append(dist_media(lab))
    z = (vero - statistics.mean(nul)) / statistics.pstdev(nul)
    argomenti = OrderedDict()
    for t in range(6):
        fasc = Counter(meta[pp[i]][2] for i in range(len(pp)) if dom[i] == t)
        argomenti[t] = OrderedDict([('paragrafi', int((dom == t).sum())), ('parole', [voc[j] for j in np.argsort(-lda.components_[t])[:8]]),
                                    ('fascicoli', dict(fasc))])
    tutti3 = all(len(a['fascicoli']) >= 3 for a in argomenti.values() if a['paragrafi'] > 0)
    esito = 'argomenti locali' if z < -3 else ('argomenti che tornano lontano' if (abs(z) < 2 and tutti3) else 'incerto')
    return OrderedDict([('paragrafi', len(par)), ('vocabolario', len(voc)), ('distanza_media_stesso_argomento', vero), ('nullo', statistics.mean(nul)), ('z', z),
                        ('esito', esito), ('argomenti', argomenti)])


def e333(pag, punt, rnd):
    diffs = defaultdict(list)
    for p, pars in pag.items():
        interne = [ws for par in pars for t, ws in par if t == 'interna']
        if len(interne) < 12:
            continue
        h = len(interne) // 2
        alta, bassa = interne[:h], interne[h:]
        ca, cb = e328.scelte([w for ws in alta for w in ws]), e328.scelte([w for ws in bassa for w in ws])
        for j, nome in enumerate(NOMI_SCELTE):
            if ca[j][0] >= 5 and cb[j][0] >= 5:
                diffs[nome].append(cb[j][1] / cb[j][0] - ca[j][1] / ca[j][0])
        sa = e327.somma([e327.riga_stat(ws) for ws in alta])[0]
        sb = e327.somma([e327.riga_stat(ws) for ws in bassa])[0]
        diffs['punteggio dell\'asse'].append(punt(sb) - punt(sa))
    out = OrderedDict()
    for nome, d in diffs.items():
        v, z = segno_flip(d, rnd)
        out[nome] = OrderedDict([('pagine', len(d)), ('bassa_meno_alta', v), ('z', z)])
    costanti = [n for n, v in out.items() if abs(v['z']) > 3]
    esito = 'direzione costante per: ' + ', '.join(costanti) if costanti else ('nessuna direzione' if all(abs(v['z']) < 2 for v in out.values()) else 'incerto')
    return OrderedDict([('misure', out), ('esito', esito)])


def main():
    pag = e328.carica()
    testa = e308.intestazioni()
    punt = standard(pag)
    r331 = e331(pag, testa, punt, random.Random(331))
    print('e331', r331['esito'], {k: {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()} for k, v in r331['prove'].items()}, flush=True)
    r332 = e332(pag, random.Random(332))
    print('e332', r332['esito'], round(r332['distanza_media_stesso_argomento'], 1), round(r332['nullo'], 1), round(r332['z'], 1), flush=True)
    r333 = e333(pag, punt, random.Random(333))
    print('e333', r333['esito'], {k: (v['pagine'], round(v['bassa_meno_alta'], 4), round(v['z'], 1)) for k, v in r333['misure'].items()}, flush=True)
    json.dump(OrderedDict([('e331', r331), ('e332', r332), ('e333', r333)]), open(os.path.join(RISULTATI, 'e331_tempo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e331, e332, e333 — Girando il foglio; gli argomenti dei paragrafi; la direzione dell\'abitudine', '', 'Preregistrazione: `preregistrazioni/e331.md`.', '',
          '## e331', '', '| prova | coppie | lontana − vicina (segni) | z | (asse) | z | (lessico) | z |', '|---|---|---|---|---|---|---|---|']
    for k, v in r331['prove'].items():
        if 'z_segni' in v:
            md.append('| %s | %d | %+.4f | %.1f | %+.3f | %.1f | %+.4f | %.1f |' % (k, v['coppie'], v['lontana_meno_vicina_segni'], v['z_segni'], v['lontana_meno_vicina_asse'], v['z_asse'],
                                                                                v['lontana_meno_vicina_lessico'], v['z_lessico']))
        else:
            md.append('| %s | %d | – | – | – | – | – | – |' % (k, v['coppie']))
    md += ['', 'Esito e331: **%s**.' % r331['esito'], '', '## e332 — erbario in lingua A, %d paragrafi, vocabolario %d forme' % (r332['paragrafi'], r332['vocabolario']), '',
           'Distanza media nel libro fra paragrafi con lo stesso argomento: %.1f pagine contro %.1f del nullo, z %.1f. Esito: **%s**.' % (
               r332['distanza_media_stesso_argomento'], r332['nullo'], r332['z'], r332['esito']), '']
    for t, a in r332['argomenti'].items():
        md.append('- Argomento %d (%d paragrafi): %s; fascicoli %s.' % (t, a['paragrafi'], ', '.join(a['parole']), a['fascicoli']))
    md += ['', '## e333', '', '| misura | pagine | metà bassa − metà alta | z |', '|---|---|---|---|']
    for k, v in r333['misure'].items():
        md.append('| %s | %d | %+.4f | %.1f |' % (k, v['pagine'], v['bassa_meno_alta'], v['z']))
    md += ['', 'Esito e333: **%s**.' % r333['esito']]
    open(os.path.join(RISULTATI, 'e331_tempo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
