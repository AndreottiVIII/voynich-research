# -*- coding: utf-8 -*-
"""Esperimento e3c24: per qo/o, la caduta della q accanto al disegno (e3c23) avviene sia nella parola prima del disegno
(dove la q, a inizio parola, è lontana dal disegno: spazio pianificato) sia in quella dopo (dove la q tocca il disegno)?
Regressione dell'e3c22 (x, F, L, S, E) per la sola classe qo/o, ZL; differenza E − S sugli stessi ricampionamenti.

Preregistrazione: preregistrazioni/e3c24.md. Scrive risultati/e3c24_q_prima_dopo_disegno.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386
import e3b62_memoria_nullo_largo as e3b62
import e3c22_bordi_e_disegno as e3c22

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
NOMI = ('x', 'F', 'L', 'S', 'E')


def main():
    rng = np.random.default_rng(3324)
    obs = e3c22.osservazioni(e386.righe(), OrderedDict([('qo/o', e3b62.CV['qo/o'])]), NOMI)
    k = len(NOMI)
    n, sz, szz = e3c22.statistiche(obs, k)
    oss = e3c22.coefficienti(n.sum(0), sz.sum(0), szz.sum(0), k)
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n.shape[0], n.shape[0])
        try:
            boot.append(e3c22.coefficienti(n[idx].sum(0), sz[idx].sum(0), szz[idx].sum(0), k))
        except np.linalg.LinAlgError:
            continue
    boot = np.array(boot)
    ic = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    ris = OrderedDict((nm, OrderedDict([('coefficiente', float(oss[i])), ('IC95', ic(boot[:, i]))])) for i, nm in enumerate(NOMI))
    ris['E − S'] = OrderedDict([('coefficiente', float(oss[4] - oss[3])), ('IC95', ic(boot[:, 4] - boot[:, 3]))])
    ris['parole_S'] = int(sum(1 for o in obs if o[2][3] == 1))
    ris['parole_E'] = int(sum(1 for o in obs if o[2][4] == 1))
    e, s = ris['E']['IC95'], ris['S']['IC95']
    if e[1] < 0 and s[1] < 0:
        esito = 'la q cade sia prima sia dopo il disegno: spazio pianificato'
    elif s[1] < 0 and e[0] <= 0:
        esito = 'la q cade solo dopo il disegno, dove lo tocca'
    elif e[1] < 0:
        esito = 'la q cade solo prima del disegno'
    else:
        esito = 'incerto'
    ris['esito'] = esito
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c24_q_prima_dopo_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c24 — La q cade prima o dopo il disegno?', '', 'Preregistrazione: `preregistrazioni/e3c24.md`. ZL, classe qo/o (1 = qo), regressione dentro strati (parola coperta).', '',
          '| termine | coefficiente (IC 95%) |', '|---|---|']
    for nm in NOMI + ('E − S',):
        x = ris[nm]
        md.append('| %s | %+.4f (%+.4f – %+.4f) |' % (nm, x['coefficiente'] * (10 if nm == 'x' else 1), x['IC95'][0] * (10 if nm == 'x' else 1), x['IC95'][1] * (10 if nm == 'x' else 1)))
    md += ['', 'Parole qo/o prima del disegno: %d; dopo: %d. (x per 10 segni.)' % (ris['parole_E'], ris['parole_S']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c24_q_prima_dopo_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
