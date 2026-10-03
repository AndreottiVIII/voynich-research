# -*- coding: utf-8 -*-
"""Esperimento e3a67: si tolgono gli spazi e si rimettono a caso con la regola dell'e3a58; quota dei pezzi "sbagliati"
(che non coincidono con una parola originale, almeno 3 segni) che sono parole attestate nel testo.

Preregistrazione: preregistrazioni/e3a67.md. Scrive risultati/e3a67_spazi_rifatti.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict

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
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
RISCRITTURE = 5
MIN_SEGNI = 3


def attestazione(righe, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    tipi = {w for r in righe for w in r}
    reg = e3a58.Regola(e3a58.posizioni(righe))
    qq = []
    for _ in range(RISCRITTURE):
        sb = att = 0
        for r in righe:
            s, orig = [], set()
            for w in r:
                orig.add((len(s), len(s) + len(w)))
                s += list(w)
            tagli = [0] + [i for i in range(1, len(s)) if rnd.random() < reg.p(s[i - 1], s[i])] + [len(s)]
            for a, b in zip(tagli, tagli[1:]):
                if (a, b) in orig or b - a < MIN_SEGNI:
                    continue
                sb += 1
                att += tuple(s[a:b]) in tipi
        qq.append(att / sb if sb else None)
    qq = [q for q in qq if q is not None]
    return (statistics.median(qq) if qq else None), sb


def main():
    rnd = random.Random(3167)
    voy_pag = e375.voynich()
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(r) for r in p)
        sub.append(attestazione(prese, rnd)[0])
    ris = OrderedDict([('Voynich', OrderedDict([('attestazione', statistics.median(sub)), ('sottoinsiemi', sub)]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    altri = OrderedDict([('gibberish umano', e3a58.righe_prime(gib))])
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            altri[k] = e3a58.righe_prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v])
    altri['Timm e Schinner, seme 1'] = e3a58.righe_prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])
    for k, rr in altri.items():
        q, n = attestazione(rr, rnd)
        ris[k] = OrderedDict([('attestazione', q), ('pezzi_sbagliati_ultima', n)])
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        q, n = attestazione(e3a58.righe_prime(t), rnd)
        if q is not None:
            sens[k.replace('.txt', '')] = q
    vals = sorted(sens.values())
    m = ris['Voynich']['attestazione']
    p10, p90 = float(np.percentile(vals, 10)), float(np.percentile(vals, 90))
    sotto = sum(1 for v in vals if v < m) / len(vals)
    esito = 'anche i tagli sbagliati danno parole vere' if m > p90 else ('come le lingue' if m >= p10 else 'meno')
    lingue = OrderedDict([('testi', len(vals)), ('minimo', vals[0]), ('p10', p10), ('mediana', float(np.median(vals))), ('p90', p90), ('massimo', vals[-1]), ('quota_sotto_il_voynich', sotto)])
    out = OrderedDict([('altri', ris), ('lingue', lingue), ('testi_sensati', OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]))), ('esito', esito)])
    print(json.dumps(lingue), esito, flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a67_spazi_rifatti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a67 — Rifacendo gli spazi a caso con la regola, i pezzi sbagliati sono ancora parole vere?', '', 'Preregistrazione: `preregistrazioni/e3a67.md`. Attestazione = quota dei pezzi sbagliati (almeno 3 segni) che sono parole del testo.', '',
          'Testi sensati: minimo %.3f, 10° percentile %.3f, mediana %.3f, 90° percentile %.3f, massimo %.3f. Il Voynich supera il %.0f%% dei testi sensati.' % (vals[0], p10, float(np.median(vals)), p90, vals[-1], 100 * sotto), '',
          '| testo | attestazione |', '|---|---|']
    md += ['| %s | %s%s |' % (k, '%.3f' % x['attestazione'] if x['attestazione'] is not None else 'n.d.', ' (sottoinsiemi: %s)' % ', '.join('%.3f' % v for v in x['sottoinsiemi']) if 'sottoinsiemi' in x else '') for k, x in ris.items()]
    md += ['', '| testo sensato | attestazione |', '|---|---|'] + ['| %s | %.3f |' % kv for kv in out['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a67_spazi_rifatti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
