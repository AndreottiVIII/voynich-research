# -*- coding: utf-8 -*-
"""Esperimento e3c77: batteria scribi sugli scribi tedeschi del 1350 – 1500 (ReF, 73 manoscritti, livello diplomatico,
righe e pagine vere), parte 1: la finestra (misura corretta dell'e3c48) e la deriva lungo la riga (e3c13) nelle scelte di
forma di lettera e nell'abbreviare. Mano = manoscritto; prime 6.000 parole di ogni manoscritto. Voynich ZL nella stessa
esecuzione.

Dati: dati/cache/ref (ReF 1.0.2, CC-BY-SA 4.0; non si committano).
Preregistrazione: preregistrazioni/e3c77.md. Scrive risultati/e3c77_ref_finestra_deriva.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b62_memoria_nullo_largo as e3b62
import e3c13_sh_lungo_la_riga as e3c13
import e3c48_finestra_corretta as e3c48
import e3c50_scribi_menota as e3c50
import e3c52_eva_per_scelta as e3c52
import e3c58_altri_scribi as e3c58
import ref_leggi

RISULTATI = os.path.join(QUI, '..', 'risultati')
TETTO = 6000
SOGLIA_DERIVA = 0.010
SCELTE = [('ſ/s', ['ſ'], ['s']), ('u/v', ['u'], ['v']), ('i/j', ['i'], ['j']), ('i/y', ['i'], ['y']), ('í/i', ['í'], ['i']),
          ('w/u', ['w'], ['u']), ('uͦ/u', ['uͦ'], ['u']), ('z/cz', ['z'], [('c', 'z')]), ('y/ÿ', ['y'], ['ÿ'])]


def abbreviata(w):
    if not w.norm:
        return None
    return int(w.abbreviata), tuple(w.norm)


def pagine_ref():
    out = []
    for sigla, h, pp in ref_leggi.manoscritti():
        n = 0
        for _, rr in pp:
            if n >= TETTO:
                break
            out.append((sigla, rr))
            n += sum(len(r) for r in rr)
    return out


def main():
    e3c48.PERM = 20
    rng = np.random.default_rng(3377)
    pagine = pagine_ref()
    print('pagine', len(pagine), 'parole', sum(len(r) for _, rr in pagine for r in rr), flush=True)
    classi = [(n, e3c58.scelta(a, b), 'lettera') for n, a, b in SCELTE] + [('abbreviata o no', abbreviata, 'abbreviazione')]
    ris = OrderedDict()
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    voy = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in e341.pagine().items() if mano.get(pg)]
    x = e3c48.misura(voy, OrderedDict((k, e3b62.CV[k]) for k in ('k/t', 'sh/ch', '-ey/-dy')), rng)
    x['deriva'] = e3c13.pendenza([rr for _, rr in voy], OrderedDict([('k/t', e3b62.CV['k/t'])]), rng)
    ris['Voynich ZL'] = x
    print('Voynich', json.dumps(x, ensure_ascii=False), flush=True)
    for nome, f, tipo in classi:
        x = e3c48.misura(pagine, OrderedDict([(nome, f)]), rng)
        x['vicine'], x['finestra'] = e3c50.giudizio(x)
        x['voce'] = e3c52.voce(x)
        d = e3c13.pendenza([rr for _, rr in pagine], OrderedDict([(nome, f)]), rng)
        d['deriva'] = d['IC95'][1] < 0 or d['IC95'][0] > 0
        d['come_voynich'] = d['deriva'] and abs(d['per_10_segni']) >= SOGLIA_DERIVA
        x['deriva'], x['tipo'] = d, tipo
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    lett = [k for k, x in ris.items() if x.get('tipo') == 'lettera']
    fin = [k for k in lett if ris[k]['finestra']]
    der = [k for k in lett if ris[k]['deriva']['come_voynich']]
    esito_f = 'gli scribi tedeschi hanno la finestra' if len(fin) >= 2 else ('nessuna scelta di lettera ha la finestra' if not fin else 'incerto')
    esito_d = 'gli scribi tedeschi hanno una deriva come il Voynich' if len(der) >= 3 else ('nessuna scelta di lettera ha una deriva come il Voynich' if not der else 'deriva come il Voynich in poche scelte (%d)' % len(der))
    out = OrderedDict([('misure', ris), ('con_finestra', fin), ('con_deriva', der), ('esito_finestra', esito_f), ('esito_deriva', esito_d)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c77_ref_finestra_deriva.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c77 — Scribi tedeschi 1350 – 1500 (ReF): finestra e deriva', '', 'Preregistrazione: `preregistrazioni/e3c77.md`. 73 manoscritti, prime %d parole di ciascuno; mano = manoscritto.' % TETTO, '',
          '| scelta | parole | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r | voce | deriva per 10 segni (IC 95%) |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        d = x['deriva']
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f | %s | %+.4f (%+.4f – %+.4f) |' % (
            k, x['parole'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1],
            x['r'], x.get('voce', '—'), d['per_10_segni'], 10 * d['IC95'][0], 10 * d['IC95'][1]))
    md += ['', 'Esito finestra (scelte di lettera): **%s**%s.' % (esito_f, (' (' + ', '.join(fin) + ')') if fin else ''),
           'Esito deriva (scelte di lettera): **%s**%s.' % (esito_d, (' (' + ', '.join(der) + ')') if der else ''), '',
           'Fonte: Referenzkorpus Frühneuhochdeutsch (ReF 1.0.2), CC-BY-SA 4.0. I file non sono nel repository.']
    open(os.path.join(RISULTATI, 'e3c77_ref_finestra_deriva.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
