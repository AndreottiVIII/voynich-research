# -*- coding: utf-8 -*-
"""Esperimento e3b08: differenza vicino - lontano dell'accordo delle scelte di grafia (e3b06), con e senza le coppie di
parole simili, ZL e IT; intervalli bootstrap sulle righe.

Preregistrazione: preregistrazioni/e3b08.md. Scrive risultati/e3b08_scelte_differenza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b06_scelte_riga_distanza as e3b06
import e3b07_scelte_memoria_controlli as e3b07

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def diff(cc):
    e = e3b06.eccessi(cc)
    return e['tutte', 'vicino'][0] - e['tutte', 'lontano'][0]


def con_ic(cc, rnd):
    per_riga = defaultdict(list)
    for x in cc:
        per_riga[x[0]].append(x)
    chiavi = list(per_riga)
    b = sorted(diff([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per_riga[k]]) for _ in range(BOOT))
    return OrderedDict([('differenza', diff(cc)), ('IC95', [b[int(0.025 * BOOT)], b[int(0.975 * BOOT) - 1]])])


def main():
    rnd = random.Random(3208)
    zl = []
    for pars in e341.pagine().values():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        zl.append([r for r in righe if r])
    it = e3b07.pagine('IT')
    ris = OrderedDict()
    for nome, pg in (('ZL', zl), ('IT', it)):
        ris[nome + ', tutte le coppie'] = con_ic(e3b06.coppie(pg), rnd)
        ris[nome + ', senza parole simili'] = con_ic(e3b07.coppie_senza_simili(pg), rnd)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    sopra = [ris[k]['IC95'][0] > 0 for k in ('ZL, senza parole simili', 'IT, senza parole simili')]
    contiene = [ris[k]['IC95'][0] <= 0 <= ris[k]['IC95'][1] for k in ('ZL, senza parole simili', 'IT, senza parole simili')]
    esito = 'memoria delle scelte' if all(sopra) else ('solo ripetizione di parole' if all(contiene) else 'incerto')
    out = OrderedDict([('risultati', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b08_scelte_differenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b08 — Senza le parole ripetute, le scelte di grafia concordano più da vicino che da lontano?', '', 'Preregistrazione: `preregistrazioni/e3b08.md`. Differenza = eccesso d 2–3 − eccesso d 6–10.', '',
          '| versione | differenza vicino − lontano | IC 95% |', '|---|---|---|']
    md += ['| %s | %+.4f | %+.4f – %+.4f |' % (k, x['differenza'], x['IC95'][0], x['IC95'][1]) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b08_scelte_differenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
