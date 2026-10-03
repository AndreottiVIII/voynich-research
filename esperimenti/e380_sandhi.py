# -*- coding: utf-8 -*-
"""Esperimento 380: legame fra l'ultimo segno di una parola e il primo della seguente (e fra il primo e l'ultimo della
precedente) a parita' del resto della parola, come nel sandhi; scelte di grafia ai bordi e segno vicino.
Voynich, testi sensati (parole intere), gibberish umano, Timm e Schinner.

Preregistrazione: preregistrazioni/e380.md. Scrive risultati/e380_sandhi.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e337_posizione as e337
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
GALL = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}


def voynich():
    """[(strato, paragrafo)], paragrafo = lista di righe di parole (tuple di segni)."""
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if not ws:
            continue
        st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
        if r.inizio_par or not out or out[-1][0] != st or out[-1][2] != r.pagina:
            out.append((st, [], r.pagina))
        out[-1][1].append(ws)
    return [(s, p) for s, p, _ in out]


def eventi(paragrafi, scelta_destra, scelta_sinistra):
    """Liste di (gruppo, scelta, segno vicino) per i due lati, togliendo le coppie copiate dalle 2 righe sopra."""
    dx, sx = [], []
    for st, par in paragrafi:
        for i, r in enumerate(par):
            sopra = set()
            for q in par[max(0, i - 2):i]:
                sopra |= set(zip(q, q[1:]))
            n = len(r)
            for j in range(n - 1):
                a, b = r[j], r[j + 1]
                if (a, b) in sopra:
                    continue
                pa = 0 if j == 0 else (2 if j == n - 2 else 1)
                x = scelta_destra(a)
                if x:
                    dx.append(((st, x[0], pa), x[1], b[0]))
                pb = 2 if j + 1 == n - 1 else (0 if j + 1 == 1 else 1)
                y = scelta_sinistra(b)
                if y:
                    sx.append(((st, y[0], pb), y[1], a[-1]))
    return dx, sx


def mi_cond(ev):
    per = defaultdict(list)
    for g, c, v in ev:
        per[g].append((c, v))
    n = len(ev)
    tot = 0.0
    for xs in per.values():
        m = len(xs)
        cc, cv, cj = Counter(c for c, _ in xs), Counter(v for _, v in xs), Counter(xs)
        if len(cc) < 2 or len(cv) < 2:
            continue
        tot += sum(k / n * math.log2(k * m / (cc[c] * cv[v])) for (c, v), k in cj.items())
    return tot


def prova(ev, rnd, perm):
    vero = mi_cond(ev)
    per = defaultdict(list)
    for g, c, v in ev:
        per[g].append((c, v))
    attivi = {g: xs for g, xs in per.items() if len({c for c, _ in xs}) > 1 and len({v for _, v in xs}) > 1}
    fissi = [(g, c, v) for g, xs in per.items() if g not in attivi for c, v in xs]
    nul = []
    for _ in range(perm):
        e2 = list(fissi)
        for g, xs in attivi.items():
            vs = [v for _, v in xs]
            rnd.shuffle(vs)
            e2 += [(g, c, v) for (c, _), v in zip(xs, vs)]
        nul.append(mi_cond(e2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('eventi', len(ev)), ('I', vero), ('nullo', m), ('E', vero - m), ('z', (vero - m) / sd if sd else 0.0)])


def tronco(w):
    return (w[:-1], w[-1]) if len(w) >= 2 else None


def corpo(w):
    return (w[1:], w[0]) if len(w) >= 2 else None


def fin_lr(w):
    return (w[:-1], w[-1]) if len(w) >= 2 and w[-1] in ('l', 'r') else None


def fin_dyey(w):
    return (w[:-2], w[-2]) if len(w) >= 3 and w[-1] == 'y' and w[-2] in ('d', 'e') else None


def ini_qo(w):
    if len(w) >= 3 and w[0] == 'q' and w[1] == 'o' and w[2] in GALL:
        return (w[2:], 'qo')
    if len(w) >= 2 and w[0] == 'o' and w[1] in GALL:
        return (w[1:], 'o')
    return None


def ini_chsh(w):
    return (w[1:], w[0]) if len(w) >= 2 and w[0] in ('ch', 'sh') else None


def main():
    rnd = random.Random(380)
    voy = voynich()
    corpi = OrderedDict([('Voynich', voy)])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(n).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib.append(('-', righe))
    corpi['gibberish umano'] = gib
    corpi['Timm e Schinner, seme 1'] = [('-', [[tuple(D(w)) for w in r] for r in p]) for p in e337.pagine_ts(1)]
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        corpi[k.replace('.txt', '')] = [('-', righe)]
    ris = OrderedDict()
    for nome, pars in corpi.items():
        dx, sx = eventi(pars, tronco, corpo)
        perm = 1000 if nome == 'Voynich' else 200
        ris[nome] = OrderedDict([('destra', prova(dx, rnd, perm)), ('sinistra', prova(sx, rnd, perm))])
        print(nome, json.dumps(ris[nome], default=float), flush=True)
    parte2 = OrderedDict()
    for nome, fd, fs in (('-l/-r finale', fin_lr, None), ('-dy/-ey', fin_dyey, None), ('qo-/o- davanti a gallows', None, ini_qo), ('ch-/sh- iniziale', None, ini_chsh)):
        dx, sx = eventi(voy, fd or (lambda w: None), fs or (lambda w: None))
        parte2[nome] = prova(dx if fd else sx, rnd, 1000)
        print(nome, json.dumps(parte2[nome], default=float), flush=True)
    sanscrito = [ris[k]['destra']['z'] for k in ris if 'Sanskrit' in k]
    controllo = any(z > 3 for z in sanscrito)
    V = ris['Voynich']

    sensati = [k for k in ris if k not in ('Voynich', 'gibberish umano', 'Timm e Schinner, seme 1')]
    posto = OrderedDict((lato, sum(ris[k][lato]['E'] > V[lato]['E'] for k in sensati)) for lato in ('destra', 'sinistra'))

    def esito(lato, cosa):
        z = V[lato]['z']
        if z > 3:
            return cosa + (', più forte di tutte le lingue' if posto[lato] == 0 else ', nella gamma delle lingue')
        if z < 2:
            return 'no' if controllo else 'no, ma non si legge (controllo positivo fallito)'
        return 'incerto'
    out = OrderedDict([('testi', ris), ('parte2', parte2), ('controllo_sanscrito_z', sanscrito), ('controllo_positivo', controllo),
                       ('testi_sensati_con_E_maggiore', posto), ('n_testi_sensati', len(sensati)),
                       ('esito_destra', esito('destra', 'il segno finale porta da solo un legame con la parola dopo')),
                       ('esito_sinistra', esito('sinistra', 'il primo segno porta da solo un legame con la parola prima')),
                       ('scelte_legate', [k for k, x in parte2.items() if x['z'] > 3])])
    json.dump(out, open(os.path.join(RISULTATI, 'e380_sandhi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e380 — Il segno di bordo porta da solo il legame con la parola vicina? (sandhi)', '', 'Preregistrazione: `preregistrazioni/e380.md`. E = informazione mutua condizionata oltre il nullo (bit).', '',
          '## Parte 1', '', '| testo | eventi destra | E destra | z | eventi sinistra | E sinistra | z |', '|---|---|---|---|---|---|---|']
    ordine = ['Voynich', 'gibberish umano', 'Timm e Schinner, seme 1'] + sorted(sensati, key=lambda k: -ris[k]['destra']['E'])
    for k in ordine:
        x = ris[k]
        md.append('| %s | %d | %.4f | %.1f | %d | %.4f | %.1f |' % (k, x['destra']['eventi'], x['destra']['E'], x['destra']['z'], x['sinistra']['eventi'], x['sinistra']['E'], x['sinistra']['z']))
    md += ['', 'Controllo positivo (sanscrito, z a destra): %s → %s.' % (', '.join('%.1f' % z for z in sanscrito), 'superato' if controllo else 'fallito'),
           'Testi sensati con E maggiore del Voynich: a destra %d, a sinistra %d, su %d.' % (posto['destra'], posto['sinistra'], len(sensati)), '',
           '## Parte 2 (Voynich)', '', '| scelta | eventi | E | z |', '|---|---|---|---|']
    for k, x in parte2.items():
        md.append('| %s | %d | %.4f | %.1f |' % (k, x['eventi'], x['E'], x['z']))
    md += ['', 'Esito a destra: **%s**. Esito a sinistra: **%s**. Scelte legate al vicino: %s.' % (out['esito_destra'], out['esito_sinistra'], ', '.join(out['scelte_legate']) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e380_sandhi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
