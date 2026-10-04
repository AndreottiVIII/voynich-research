# -*- coding: utf-8 -*-
"""Esperimento e3a75: entropia di posizione dei segni (iniziale, interno, finale, da solo) nel Voynich, nelle lingue, nel
gibberish e nei generatori; regressione dei valori delle lingue riscritte dalla catena (e3a69) su entropia di posizione e
h2 (e3a57), con il Voynich.

Preregistrazione: preregistrazioni/e3a75.md. Scrive risultati/e3a75_posizione_segni.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MIN_OCC = 50


def entropia_posizione(parole):
    c = defaultdict(Counter)
    for w in parole:
        if len(w) == 1:
            c[w[0]]['solo'] += 1
            continue
        c[w[0]]['inizio'] += 1
        c[w[-1]]['fine'] += 1
        for x in w[1:-1]:
            c[x]['dentro'] += 1
    num = den = 0.0
    for s, cc in c.items():
        n = sum(cc.values())
        if n < MIN_OCC:
            continue
        h = -sum(v / n * math.log2(v / n) for v in cc.values())
        num += n * h
        den += n
    return num / den


def main():
    rnd = random.Random(3175)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        sub.append(entropia_posizione(prese))
    altri = OrderedDict([('Voynich', OrderedDict([('Hpos', statistics.median(sub)), ('sottoinsiemi', sub)]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [w for l in z.read(nome).decode('utf-8', errors='ignore').splitlines() for w in (e381.parola(p) for p in l.split()) if w]
    altri['gibberish umano'] = OrderedDict([('Hpos', entropia_posizione(gib))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            altri[k] = OrderedDict([('Hpos', entropia_posizione(e3a55.prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v])))])
    altri['Timm e Schinner, seme 1'] = OrderedDict([('Hpos', entropia_posizione(e3a55.prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])))])
    sens = OrderedDict((k.replace('.txt', ''), entropia_posizione([tuple(w) for w in e3a55.prime(t)])) for k, t in e381.testi().items())
    vals = sorted(sens.values())
    hv = altri['Voynich']['Hpos']
    q = sum(1 for v in vals if v < hv) / len(vals)
    es1 = 'segni più legati al posto che in tutte le lingue' if hv < vals[0] else 'percentile %.0f%% fra le lingue' % (100 * q)
    for k, x in altri.items():
        print(k, json.dumps(x), flush=True)
    c69 = json.load(open(os.path.join(RISULTATI, 'e3a69_catene_sintetiche.json'), encoding='utf-8'))
    h57 = json.load(open(os.path.join(RISULTATI, 'e3a57_forma_entropia.json'), encoding='utf-8'))
    h2v = h57['altri']['Voynich']['h2']
    reg = OrderedDict()
    for m in ('rho frequenza-forma (e3a55)', 'riempimento (e3a61)', 'tagli sbagliati che sono parole (e3a67)'):
        X, y = [], []
        for k, hp in sens.items():
            if k in h57['testi_sensati'] and k in c69['testi_sensati'] and c69['testi_sensati'][k]['catena'][m] is not None:
                X.append([1.0, hp, h57['testi_sensati'][k]['h2']])
                y.append(c69['testi_sensati'][k]['catena'][m])
        X, y = np.array(X), np.array(y)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        res = y - X @ beta
        sd = float(np.sqrt(np.sum(res ** 2) / (len(y) - 3)))
        prev = float(beta @ np.array([1.0, hv, h2v]))
        v = c69['sintesi'][m]['voynich_catena']
        z = (v - prev) / sd
        es = 'la rigidità di posizione spiega il Voynich' if abs(z) < 2 else ('il Voynich va ancora oltre' if z >= 2 else 'sta sotto')
        r_hpos = float(np.corrcoef(X[:, 1], y)[0, 1])
        reg[m] = OrderedDict([('testi', len(y)), ('coefficienti', [float(b) for b in beta]), ('r_con_Hpos', r_hpos), ('sd_residui', sd), ('previsto', prev),
                              ('voynich_riscritto', v), ('z', float(z)), ('esito', es)])
        print(m, json.dumps(reg[m], ensure_ascii=False), flush=True)
    fuori = hv < vals[0] or hv > vals[-1]
    out = OrderedDict([('altri', altri), ('lingue', OrderedDict([('minimo', vals[0]), ('mediana', float(np.median(vals))), ('massimo', vals[-1]), ('quota_sotto_il_voynich', q)])),
                       ('esito_1', es1), ('regressione', reg), ('voynich_fuori_intervallo', fuori), ('testi_sensati', OrderedDict(sorted(sens.items(), key=lambda kv: kv[1])))])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a75_posizione_segni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a75 — I segni del Voynich hanno un posto fisso nella parola? E questo spiega l\'e3a70?', '', 'Preregistrazione: `preregistrazioni/e3a75.md`. Entropia di posizione in bit (massimo 2; più bassa = segni più legati al posto).', '',
          'Testi sensati: minimo %.3f, mediana %.3f, massimo %.3f.' % (vals[0], float(np.median(vals)), vals[-1]), '', '| testo | entropia di posizione |', '|---|---|']
    md += ['| %s | %.3f%s |' % (k, x['Hpos'], ' (sottoinsiemi: %s)' % ', '.join('%.3f' % s for s in x['sottoinsiemi']) if 'sottoinsiemi' in x else '') for k, x in altri.items()]
    md += ['', 'Esito (1): **%s**.' % es1, '', '| misura (lingue riscritte, e3a69) | r con l\'entropia di posizione | previsto al Voynich (posizione e h2) | Voynich riscritto | z | esito |', '|---|---|---|---|---|---|']
    md += ['| %s | %+.3f | %.3f | %.3f | %+.1f | %s |' % (m, x['r_con_Hpos'], x['previsto'], x['voynich_riscritto'], x['z'], x['esito']) for m, x in reg.items()]
    if fuori:
        md += ['', '**Il Voynich sta fuori dall\'intervallo delle lingue per l\'entropia di posizione: le previsioni sono estrapolazioni.**']
    md += ['', '| testo sensato (dal più rigido) | entropia di posizione |', '|---|---|'] + ['| %s | %.3f |' % kv for kv in out['testi_sensati'].items()]
    open(os.path.join(RISULTATI, 'e3a75_posizione_segni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
