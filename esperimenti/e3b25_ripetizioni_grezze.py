# -*- coding: utf-8 -*-
"""Esperimento e3b25: quota grezza di parole vicine identiche (e quasi identiche) nella stessa riga; Voynich, lingue,
gibberish, generatori.

Preregistrazione: preregistrazioni/e3b25.md. Scrive risultati/e3b25_ripetizioni_grezze.json e .md.
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
import e3a86_ripetizioni_riga as e3a86

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def quote(righe):
    rip = [0, 0]
    quasi = [0, 0]
    for r in righe:
        r = [tuple(w) for w in r]
        for a, b in zip(r, r[1:]):
            if len(a) >= 2 and len(b) >= 2:
                rip[0] += a == b
                rip[1] += 1
            if len(a) >= 3 and len(b) >= 3:
                quasi[0] += e3a86.una_modifica(a, b)
                quasi[1] += 1
    return OrderedDict([('ripetizione', rip[0] / rip[1] if rip[1] else None), ('quasi', quasi[0] / quasi[1] if quasi[1] else None), ('coppie', rip[1])])


def main():
    rnd = random.Random(3225)
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
        sub.append(quote(prese))
    ris = OrderedDict([('Voynich', OrderedDict([('ripetizione', statistics.median(s['ripetizione'] for s in sub)), ('quasi', statistics.median(s['quasi'] for s in sub))]))])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    ris['gibberish umano'] = quote(e3a58.righe_prime(gib))
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            ris[k] = quote(e3a58.righe_prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]))
    ris['Timm e Schinner, seme 1'] = quote(e3a58.righe_prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]))
    sens = OrderedDict((k.replace('.txt', ''), quote(e3a58.righe_prime(t))) for k, t in e381.testi().items())
    vals = sorted(x['ripetizione'] for x in sens.values())
    qv = sorted(x['quasi'] for x in sens.values())
    v = ris['Voynich']['ripetizione']
    p90 = float(np.percentile(vals, 90))
    esito = 'ripete subito più di tutte le lingue' if v > vals[-1] else ('come le lingue più ripetitive' if v > p90 else 'come le lingue')
    top = sorted(sens.items(), key=lambda kv: -kv[1]['ripetizione'])[:3]
    out = OrderedDict([('altri', ris), ('lingue', OrderedDict([('mediana', float(np.median(vals))), ('p90', p90), ('massimo', vals[-1]), ('quasi_mediana', float(np.median(qv))), ('quasi_massimo', qv[-1]),
                                                               ('piu_ripetitive', [[k, x['ripetizione']] for k, x in top])])), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b25_ripetizioni_grezze.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b25 — Quanto spesso una parola ripete subito la precedente?', '', 'Preregistrazione: `preregistrazioni/e3b25.md`.', '',
          '| testo | parole vicine identiche | quasi identiche (a una modifica) |', '|---|---|---|']
    md += ['| %s | %.4f | %.4f |' % (k, x['ripetizione'], x['quasi']) for k, x in ris.items()]
    md += ['| testi sensati: mediana / 90° perc. / massimo | %.4f / %.4f / %.4f | %.4f / – / %.4f |' % (out['lingue']['mediana'], p90, vals[-1], out['lingue']['quasi_mediana'], out['lingue']['quasi_massimo']),
           '', 'Testi sensati più ripetitivi: ' + '; '.join('%s %.4f' % (k, x) for k, x in out['lingue']['piu_ripetitive']) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b25_ripetizioni_grezze.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
