# -*- coding: utf-8 -*-
"""Esperimento e3c62: la deriva lungo la riga negli scribi veri (batteria scribi, 3). Pendenza della scelta sui segni
scritti prima nella riga, a parità di parola coperta, senza prima e ultima parola (misura dell'e3c13), per le scelte di
forma di lettera entrate negli e3c50 ed e3c58 e per l'abbreviazione (AM 519 a, AM 677). Riferimento nella stessa
esecuzione: Voynich ZL, qo/o, k/t, sh/ch, -ey/-dy.

Preregistrazione: preregistrazioni/e3c62.md. Scrive risultati/e3c62_deriva_scribi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e3b62_memoria_nullo_largo as e3b62
import e3c13_sh_lungo_la_riga as e3c13
import e3c50_scribi_menota as e3c50
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOGLIA = 0.010  # metà della deriva più piccola del Voynich (qo/o, e3c13: −0,020 ogni 10 segni)


def scelte():
    fn = {nome: e3c58.scelta(aa, bb) for nome, aa, bb in e3c58.COPPIE}
    out = [(ms, nome, f, tipo) for ms, nome, f, tipo in e3c50.SCELTE]
    entrate = json.load(open(os.path.join(RISULTATI, 'e3c58_altri_scribi.json'), encoding='utf-8'))['ingresso']
    out += [(x['manoscritto'], x['scelta'], fn[x['scelta']], 'lettera') for x in entrate if x['entra']]
    return out


def main():
    rng = np.random.default_rng(3362)
    ris = OrderedDict()
    voy = [rr for rr in ([[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par] for pars in e341.pagine().values()) if rr]
    for k, f in e3b62.CV.items():
        x = e3c13.pendenza(voy, OrderedDict([(k, f)]), rng)
        x['tipo'] = 'Voynich'
        ris['Voynich ZL, ' + k] = x
        print('Voynich', k, json.dumps(x), flush=True)
    testi = {}
    for ms, nome, f, tipo in scelte():
        if ms not in testi:
            testi[ms] = [rr for _, _, rr in e3c58.leggi(ms)]
            lun = [sum(len(w) for w in r) for pp in testi[ms] for r in pp if len(r) >= 3]
            ris['_lunghezza_riga_' + ms] = float(np.median(lun))
        x = e3c13.pendenza(testi[ms], OrderedDict([(nome, f)]), rng)
        x['tipo'] = tipo
        x['deriva'] = (x['IC95'][1] < 0 or x['IC95'][0] > 0)
        x['come_voynich'] = x['deriva'] and abs(x['per_10_segni']) >= SOGLIA
        ris['%s, %s' % (ms, nome)] = x
        print(ms, nome, json.dumps(x, ensure_ascii=False), flush=True)
    lett = [k for k, x in ris.items() if isinstance(x, dict) and x.get('tipo') == 'lettera']
    come = [k for k in lett if ris[k]['come_voynich']]
    if len(come) >= 3:
        esito = 'gli scribi hanno una deriva come il Voynich'
    elif not come:
        esito = 'nessuna scelta di lettera degli scribi ha una deriva come il Voynich'
    else:
        esito = 'deriva come il Voynich in poche scelte (%d)' % len(come)
    abbr = OrderedDict((k, x) for k, x in ris.items() if isinstance(x, dict) and x.get('tipo') == 'abbreviazione')
    voy_lun = float(np.median([sum(len(w) for w in r) for pp in voy for r in pp if len(r) >= 3]))
    out = OrderedDict([('misure', ris), ('soglia_per_10_segni', SOGLIA), ('lunghezza_riga_voynich', voy_lun), ('come_voynich', come), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c62_deriva_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c62 — La deriva lungo la riga negli scribi veri', '',
          'Preregistrazione: `preregistrazioni/e3c62.md`. Pendenza della scelta sui segni scritti prima nella riga, a parità di parola coperta, senza prima e ultima parola (e3c13). Riga mediana del Voynich: %.0f segni.' % voy_lun, '',
          '| testo, scelta | tipo | parole | quota forma 1 | per 10 segni (IC 95%) | deriva / come il Voynich |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        if not isinstance(x, dict):
            continue
        md.append('| %s | %s | %d | %.3f | %+.4f (%+.4f – %+.4f) | %s |' % (k, x['tipo'], x['parole'], x['quota_1'], x['per_10_segni'], 10 * x['IC95'][0], 10 * x['IC95'][1],
                                                                           '' if x['tipo'] == 'Voynich' else ('%s / %s' % ('sì' if x['deriva'] else 'no', 'sì' if x['come_voynich'] else 'no'))))
    md += ['', 'Righe mediane degli scribi (segni): ' + ', '.join('%s %.0f' % (k[len('_lunghezza_riga_'):], v) for k, v in ris.items() if k.startswith('_lunghezza_riga_')) + '.',
           '', 'Esito (scelte di lettera): **%s**%s.' % (esito, (' (' + ', '.join(come) + ')') if come else '')]
    open(os.path.join(RISULTATI, 'e3c62_deriva_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
