# -*- coding: utf-8 -*-
"""Esperimento 144: le etichette dello zodiaco hanno un posto fisso nella ruota (stessa radice alla stessa ora in ruote
diverse; preferenza per un anello; famiglia yke confinata)?

Preregistrazione: preregistrazioni/e144.md. Scrive risultati/e144_ruote_zodiaco.json e .md.
"""
import json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ZL = os.path.join(QUI, '..', 'dati', 'trascrizioni', 'ZL3b-n.txt')
SEME, RIMESCOLAMENTI = 144, 2000
D = misure.divisore(misure.GLIFI_EVA)
ORA = re.compile(r'^<!(\d{1,2}):(\d{2})>')


def etichette():
    out, pagina, var, anello = [], None, {}, defaultdict(int)
    for linea in open(ZL, encoding='latin-1'):
        linea = linea.rstrip('\n')
        if not linea or linea[0] == '#':
            continue
        m = trascrizione._PAGINA.match(linea)
        if m and not trascrizione._LOCUS.match(linea):
            pagina = m.group(1)
            var = dict(trascrizione._VAR.findall(m.group(2) or ''))
            continue
        m = trascrizione._LOCUS.match(linea)
        if not m or var.get('I') != 'Z':
            continue
        pag, num, _, tipo, _, corpo = m.groups()
        if tipo.startswith('C'):
            anello[pag] += 1
            continue
        if not tipo.startswith('L'):
            continue
        o = ORA.match(corpo)
        if not o:
            continue
        ora = (int(o.group(1)) % 12) + int(o.group(2)) / 60
        parole, _, _ = trascrizione.pulisci(corpo[o.end():])
        parole = [w for w in parole if trascrizione.pulita(w)]
        if parole:
            out.append({'pagina': pag, 'numero': int(num), 'ora': ora, 'anello': max(anello[pag], 1), 'parole': parole})
    return out


def radice(w, n=3):
    u = D(w)
    return ''.join(u[:n]) if len(u) >= n + 1 else None


def distanza(a, b):
    d = abs(a - b) % 12
    return min(d, 12 - d)


def media_coppie(et, ore, chiave):
    per = defaultdict(list)
    for i, e in enumerate(et):
        r = chiave[i]
        if r:
            per[r].append(i)
    dd = []
    for idx in per.values():
        for x in range(len(idx)):
            for y in range(x + 1, len(idx)):
                i, j = idx[x], idx[y]
                if et[i]['pagina'] != et[j]['pagina']:
                    dd.append(distanza(ore[i], ore[j]))
    return (statistics.mean(dd) if dd else None), len(dd)


def mescola_ore(et, ore, rnd):
    per = defaultdict(list)
    for i, e in enumerate(et):
        per[e['pagina']].append(i)
    x = ore[:]
    for idx in per.values():
        v = [x[i] for i in idx]
        rnd.shuffle(v)
        for i, c in zip(idx, v):
            x[i] = c
    return x


def prova_settore(et, ore, chiave, rnd):
    reale, n = media_coppie(et, ore, chiave)
    nulli = [media_coppie(et, mescola_ore(et, ore, rnd), chiave)[0] for _ in range(RIMESCOLAMENTI)]
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('coppie', n), ('distanza_media_ore', reale), ('nullo', m), ('z', (reale - m) / s if s else None)])


def prova_anello(et, rnd):
    chiave = [radice(e['parole'][0]) for e in et]
    conta = Counter(c for c in chiave if c)
    idx = [i for i, c in enumerate(chiave) if c and conta[c] >= 3]
    esterno = [1 if et[i]['anello'] == 1 else 0 for i in idx]
    rad = [chiave[i] for i in idx]
    reale = misure.informazione_mutua(list(zip(rad, esterno)))
    per = defaultdict(list)
    for k, i in enumerate(idx):
        per[et[i]['pagina']].append(k)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        x = esterno[:]
        for ks in per.values():
            v = [x[k] for k in ks]
            rnd.shuffle(v)
            for k, c in zip(ks, v):
                x[k] = c
        nulli.append(misure.informazione_mutua(list(zip(rad, x))))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    per_rad = defaultdict(lambda: [0, 0])
    for r, e in zip(rad, esterno):
        per_rad[r][0] += e
        per_rad[r][1] += 1
    return OrderedDict([('etichette', len(idx)), ('radici', len(set(rad))), ('im', reale), ('nullo', m), ('z', (reale - m) / s if s else None),
                        ('quota_esterna_per_radice', {r: '%d/%d' % tuple(v) for r, v in sorted(per_rad.items(), key=lambda kv: -kv[1][1])[:15]})])


def prova_yke(et):
    tot = Counter(e['pagina'] for e in et)
    yke = Counter(e['pagina'] for e in et if D(e['parole'][0])[:3] == ['y', 'k', 'e'])
    k = sum(yke.values())
    N = sum(tot.values())
    K = tot['f73r'] + tot['f73v']
    dentro = yke['f73r'] + yke['f73v']
    p = sum(math.comb(K, x) * math.comb(N - K, k - x) for x in range(dentro, min(K, k) + 1)) / math.comb(N, k) if k else None
    return OrderedDict([('yke_per_pagina', dict(yke)), ('totale', k), ('in_scorpione_sagittario', dentro), ('etichette_scorpione_sagittario', K), ('etichette_totali', N), ('p', p)])


def main():
    rnd = random.Random(SEME)
    et = etichette()
    ore = [e['ora'] for e in et]
    print('etichette con ora: %d su %d pagine; anelli per pagina: %s' % (len(et), len({e['pagina'] for e in et}),
                                                                       dict(Counter((e['pagina'], e['anello']) for e in et))), flush=True)
    ris = OrderedDict([('etichette', len(et))])
    for n in (3, 4):
        chiave = [radice(e['parole'][0], n) for e in et]
        ris['A settore, radice di %d segni' % n] = prova_settore(et, ore, chiave, rnd)
    # controllo positivo
    chiave = [radice(e['parole'][0], 3) for e in et]
    prima = {}
    for i, c in enumerate(chiave):
        if c and c not in prima:
            prima[c] = i
    conta = Counter(c for c in chiave if c)
    r2 = random.Random(SEME + 1)
    ore_pos = [(ore[prima[c]] if c and conta[c] >= 2 and r2.random() < 0.3 else o) for o, c in zip(ore, chiave)]
    ris['controllo positivo di A'] = prova_settore(et, ore_pos, chiave, rnd)
    ris['B anello'] = prova_anello(et, rnd)
    ris['C famiglia yke'] = prova_yke(et)
    for k, v in ris.items():
        print(k, json.dumps(v, ensure_ascii=False)[:400], flush=True)
    z = lambda k: ris[k]['z'] or 0
    valido = z('controllo positivo di A') < -4
    settore = z('A settore, radice di 3 segni') < -3
    anello = z('B anello') > 3
    yke = (ris['C famiglia yke']['p'] or 1) < 0.01
    ris['valido'], ris['settore'], ris['anello'], ris['yke_confinata'] = valido, settore, anello, yke
    print('controllo valido %s | settore %s | anello %s | yke confinata %s' % (valido, settore, anello, yke))
    with open(os.path.join(RISULTATI, 'e144_ruote_zodiaco.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e144 — Le etichette dello zodiaco hanno un posto fisso nella ruota?', '', 'Etichette Lz della ZL con ora d\'orologio e anello. Preregistrazione: '
           '`preregistrazioni/e144.md`. Spunto: r/voynich (Ockanacken, 2025).', '',
           '| prova | coppie / etichette | valore | nullo | z |', '|---|---|---|---|---|']
    for k in ('A settore, radice di 3 segni', 'A settore, radice di 4 segni', 'controllo positivo di A'):
        r = ris[k]
        out.append('| %s | %d coppie | distanza media %.2f ore | %.2f | %.1f |' % (k, r['coppie'], r['distanza_media_ore'] or 0, r['nullo'], r['z'] or 0))
    r = ris['B anello']
    out.append('| B anello (esterno contro interni) | %d etichette, %d radici | IM %.4f | %.4f | %.1f |' % (r['etichette'], r['radici'], r['im'], r['nullo'], r['z'] or 0))
    c = ris['C famiglia yke']
    out += ['', 'Famiglia yke: %d etichette, %d in Scorpione e Sagittario (che hanno %d etichette su %d); per pagina %s; p = %s.' % (
        c['totale'], c['in_scorpione_sagittario'], c['etichette_scorpione_sagittario'], c['etichette_totali'], c['yke_per_pagina'],
        '%.2g' % c['p'] if c['p'] is not None else '–'),
        '', 'Controllo valido: **%s**. Settore: **%s**. Anello: **%s**. Famiglia yke confinata: **%s**.' % tuple('sì' if x else 'no' for x in (valido, settore, anello, yke))]
    with open(os.path.join(RISULTATI, 'e144_ruote_zodiaco.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
