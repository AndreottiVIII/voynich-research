# -*- coding: utf-8 -*-
"""Esperimento e3a57: il rho frequenza-forma dell'e3a55 contro l'entropia condizionale dei segni h2, nei testi sensati;
residuo del Voynich rispetto alla retta delle lingue.

Preregistrazione: preregistrazioni/e3a57.md. Scrive risultati/e3a57_forma_entropia.json e .md.
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


def h2(parole):
    c = defaultdict(Counter)
    for w in parole:
        s = ('^',) + tuple(w) + ('$',)
        for a, b in zip(s, s[1:]):
            c[a][b] += 1
    tot = sum(sum(x.values()) for x in c.values())
    h = 0.0
    for x in c.values():
        n = sum(x.values())
        for v in x.values():
            h -= v / tot * math.log2(v / n)
    return h


def main():
    rnd = random.Random(3157)
    voy_pag = e375.voynich()
    rr, hh = [], []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese = []
        for p in ordine:
            if len(prese) >= 10000:
                break
            prese += [w for r in p for w in r]
        rr.append(e3a55.rho(prese))
        hh.append(h2(prese))
    altri = OrderedDict([('Voynich', OrderedDict([('rho', statistics.median(rr)), ('h2', statistics.median(hh)), ('rho_sub', rr), ('h2_sub', hh)]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                gib += [w for l in z.read(nome).decode('utf-8', errors='ignore').splitlines() for w in (e381.parola(p) for p in l.split()) if w]
    altri['gibberish umano'] = OrderedDict([('rho', e3a55.rho(gib)), ('h2', h2(gib))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            rr2 = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
            p = e3a55.prime(rr2)
            altri[k] = OrderedDict([('rho', e3a55.rho(p)), ('h2', h2(p))])
    p = e3a55.prime([[tuple(D(w)) for w in r] for pg in e337.pagine_ts(1) for r in pg])
    altri['Timm e Schinner, seme 1'] = OrderedDict([('rho', e3a55.rho(p)), ('h2', h2(p))])
    sens = OrderedDict()
    for k, t in e381.testi().items():
        p = e3a55.prime(t)
        v = e3a55.rho(p)
        if v is not None:
            sens[k.replace('.txt', '')] = OrderedDict([('rho', v), ('h2', h2(p))])
    x = np.array([s['h2'] for s in sens.values()])
    y = np.array([s['rho'] for s in sens.values()])
    b, a = np.polyfit(x, y, 1)
    r = float(np.corrcoef(x, y)[0, 1])
    for s in sens.values():
        s['residuo'] = s['rho'] - (a + b * s['h2'])
    for s in altri.values():
        s['previsto'] = a + b * s['h2']
        s['residuo'] = s['rho'] - s['previsto']
    res = sorted(s['residuo'] for s in sens.values())
    rv = altri['Voynich']['residuo']
    p90 = float(np.percentile(res, 90))
    esito = 'non è solo l\'entropia' if rv > res[-1] else ('spiegato dall\'entropia' if rv < p90 else 'incerto')
    fuori = not (x.min() <= altri['Voynich']['h2'] <= x.max())
    out = OrderedDict([('retta', OrderedDict([('intercetta', a), ('pendenza', b), ('r', r)])), ('h2_lingue', [float(x.min()), float(np.median(x)), float(x.max())]),
                       ('residui_lingue', OrderedDict([('massimo', res[-1]), ('p90', p90), ('mediana', float(np.median(res)))])),
                       ('voynich_fuori_intervallo_h2', fuori), ('altri', altri), ('testi_sensati', sens), ('esito', esito)])
    print(json.dumps(OrderedDict((k, v) for k, v in out.items() if k != 'testi_sensati'), ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a57_forma_entropia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a57 — Il legame frequenza-forma è solo la bassa entropia dei segni?', '', 'Preregistrazione: `preregistrazioni/e3a57.md`.', '',
          'Retta fra i 71 testi sensati: ρ = %.3f %+.3f × h2 (r = %.3f). h2 delle lingue da %.2f a %.2f bit (mediana %.2f)%s.' % (
              a, b, r, x.min(), x.max(), float(np.median(x)), '; **il Voynich è fuori da questo intervallo: la retta è un\'estrapolazione**' if fuori else ''), '',
          'Residui dei testi sensati: massimo %.3f, 90° percentile %.3f, mediana %.3f.' % (res[-1], p90, float(np.median(res))), '',
          '| testo | h2 (bit) | ρ | previsto dalla retta | residuo |', '|---|---|---|---|---|']
    md += ['| %s | %.2f | %.3f | %.3f | %+.3f |' % (k, s['h2'], s['rho'], s['previsto'], s['residuo']) for k, s in altri.items()]
    md += ['', '| testo sensato | h2 (bit) | ρ | residuo |', '|---|---|---|---|']
    md += ['| %s | %.2f | %.3f | %+.3f |' % (k, s['h2'], s['rho'], s['residuo']) for k, s in sorted(sens.items(), key=lambda kv: -kv[1]['residuo'])]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a57_forma_entropia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
