# -*- coding: utf-8 -*-
"""Esperimento e3a70: valori delle lingue riscritte dalla catena (e3a69) in funzione dell'entropia h2 della lingua (e3a57);
scarto del Voynich riscritto dalla retta delle lingue. Nessun dato nuovo.

Preregistrazione: preregistrazioni/e3a70.md. Scrive risultati/e3a70_catene_entropia.json e .md.
"""
import json, os
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    c = json.load(open(os.path.join(RISULTATI, 'e3a69_catene_sintetiche.json'), encoding='utf-8'))
    h = json.load(open(os.path.join(RISULTATI, 'e3a57_forma_entropia.json'), encoding='utf-8'))
    h2_v = h['altri']['Voynich']['h2']
    ris = OrderedDict()
    for m, s in c['sintesi'].items():
        xs, ys, nomi = [], [], []
        for k, x in c['testi_sensati'].items():
            if k in h['testi_sensati'] and x['catena'][m] is not None:
                xs.append(h['testi_sensati'][k]['h2'])
                ys.append(x['catena'][m])
                nomi.append(k)
        x, y = np.array(xs), np.array(ys)
        b, a = np.polyfit(x, y, 1)
        res = y - (a + b * x)
        sd = float(np.std(res, ddof=2))
        prev = a + b * h2_v
        v = s['voynich_catena']
        z = (v - prev) / sd
        es = 'l\'entropia spiega il Voynich' if abs(z) < 2 else ('il Voynich va oltre' if z >= 2 else 'il Voynich sta sotto')
        basse = sorted(zip(xs, nomi, ys))[:3]
        ris[m] = OrderedDict([('testi', len(xs)), ('intercetta', float(a)), ('pendenza', float(b)), ('r', float(np.corrcoef(x, y)[0, 1])), ('sd_residui', sd),
                              ('h2_voynich', h2_v), ('previsto', float(prev)), ('voynich_riscritto', v), ('z', float(z)),
                              ('lingue_piu_rigide', [[n, float(hh), float(yy)] for hh, n, yy in basse]), ('esito', es)])
        print(m, json.dumps(ris[m], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a70_catene_entropia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a70 — Quanto una lingua riscritta dalla catena si avvicina al Voynich dipende dalla rigidità della catena?', '', 'Preregistrazione: `preregistrazioni/e3a70.md`. Dati: e3a69 (valori riscritti) ed e3a57 (h2). h2 del Voynich %.2f bit.' % h2_v, '',
          '| misura | r con h2 (lingue riscritte) | retta | previsto all\'h2 del Voynich | Voynich riscritto | z | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %+.3f | %.3f %+.3f × h2 | %.3f | %.3f | %+.1f | %s |' % (m, x['r'], x['intercetta'], x['pendenza'], x['previsto'], x['voynich_riscritto'], x['z'], x['esito']) for m, x in ris.items()]
    md += ['', 'Le tre lingue con la catena più rigida (h2 più basso), valore riscritto:', '']
    for m, x in ris.items():
        md.append('- %s: %s' % (m, '; '.join('%s (h2 %.2f): %.3f' % (n, hh, yy) for n, hh, yy in x['lingue_piu_rigide'])))
    open(os.path.join(RISULTATI, 'e3a70_catene_entropia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
