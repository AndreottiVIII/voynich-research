# -*- coding: utf-8 -*-
"""Esperimento e3c22: le parole accanto al salto di un disegno si comportano come quelle ai bordi della riga? Regressione
della scelta (1 = qo, k, sh, -ey) dentro strati (classe, parola coperta) su x (segni prima nella riga), F (prima parola
della riga), L (ultima), S (prima dopo un salto), E (ultima prima di un salto), con tutte le parole della riga. ZL (con
i salti) e IT (senza segni di salto: solo x, F, L). Righe senza parole incerte; intervalli ricampionando pagine, con le
differenze E − L e S − F sugli stessi ricampionamenti.

Preregistrazione: preregistrazioni/e3c22.md. Scrive risultati/e3c22_bordi_e_disegno.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e386_salto_disegno as e386
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def osservazioni(righe, classi, nomi):
    out = []
    for _, pag, _, ws, seps in righe:
        if any(w is None for w in ws) or len(ws) < 3:
            continue
        prima = 0
        for i, w in enumerate(ws):
            v = {'x': float(prima), 'F': float(i == 0), 'L': float(i == len(ws) - 1),
                 'S': float(i > 0 and seps[i - 1] == '|'), 'E': float(i < len(ws) - 1 and seps[i] == '|')}
            for k, f in classi.items():
                x = f(w)
                if x is not None:
                    out.append((pag, (k, x[1]), [v[n] for n in nomi], float(x[0])))
            prima += len(w)
    return out


def statistiche(obs, k):
    pagine = sorted({o[0] for o in obs})
    ip = {p: i for i, p in enumerate(pagine)}
    strati = {}
    for o in obs:
        strati.setdefault(o[1], len(strati))
    n = np.zeros((len(pagine), len(strati)))
    sz = np.zeros((len(pagine), len(strati), k + 1))
    szz = np.zeros((len(pagine), len(strati), k + 1, k + 1))
    for p, s, xs, y in obs:
        z = np.array(xs + [y])
        u, t = ip[p], strati[s]
        n[u, t] += 1
        sz[u, t] += z
        szz[u, t] += np.outer(z, z)
    return n, sz, szz


def coefficienti(n, sz, szz, k):
    ok = n > 0
    media = sz[ok] / n[ok, None]
    C = (szz[ok] - n[ok, None, None] * media[:, :, None] * media[:, None, :]).sum(0)
    return np.linalg.solve(C[:k, :k], C[:k, k])


def misura(righe, nomi, rng):
    obs = osservazioni(righe, e3b62.CV, nomi)
    k = len(nomi)
    n, sz, szz = statistiche(obs, k)
    oss = coefficienti(n.sum(0), sz.sum(0), szz.sum(0), k)
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n.shape[0], n.shape[0])
        try:
            boot.append(coefficienti(n[idx].sum(0), sz[idx].sum(0), szz[idx].sum(0), k))
        except np.linalg.LinAlgError:
            continue
    boot = np.array(boot)
    ic = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    out = OrderedDict((nm, OrderedDict([('coefficiente', float(oss[i]) * (10 if nm == 'x' else 1)), ('IC95', [v * (10 if nm == 'x' else 1) for v in ic(boot[:, i])])])) for i, nm in enumerate(nomi))
    if 'S' in nomi:
        i = {nm: j for j, nm in enumerate(nomi)}
        out['E − L'] = OrderedDict([('coefficiente', float(oss[i['E']] - oss[i['L']])), ('IC95', ic(boot[:, i['E']] - boot[:, i['L']]))])
        out['S − F'] = OrderedDict([('coefficiente', float(oss[i['S']] - oss[i['F']])), ('IC95', ic(boot[:, i['S']] - boot[:, i['F']]))])
    out['parole'] = len(obs)
    return out


def righe_it():
    out = []
    for pg, pars in e3b45.pagine_it().items():
        for par in pars:
            for r in par:
                ws = [tuple(e3b62.D(w)) for w in r]
                if ws:
                    out.append(('IT', pg, 0, ws, ['.'] * (len(ws) - 1)))
    return out


def main():
    rng = np.random.default_rng(3322)
    ris = OrderedDict()
    ris['ZL'] = misura(e386.righe(), ('x', 'F', 'L', 'S', 'E'), rng)
    print('ZL', json.dumps(ris['ZL'], ensure_ascii=False), flush=True)
    ris['IT'] = misura(righe_it(), ('x', 'F', 'L'), rng)
    print('IT', json.dumps(ris['IT'], ensure_ascii=False), flush=True)
    z = ris['ZL']
    el = z['E − L']['IC95'][0] <= 0 <= z['E − L']['IC95'][1]
    sf = z['S − F']['IC95'][0] <= 0 <= z['S − F']['IC95'][1]
    if el and sf:
        esito = 'le parole accanto al disegno si comportano come quelle ai bordi della riga'
    elif el:
        esito = "prima del disegno come a fine riga; dopo il disegno non come a inizio riga"
    elif sf:
        esito = "dopo il disegno come a inizio riga; prima del disegno non come a fine riga"
    else:
        esito = 'le parole accanto al disegno non si comportano come quelle ai bordi'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c22_bordi_e_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c22 — Le parole accanto al disegno si comportano come quelle ai bordi della riga?', '', 'Preregistrazione: `preregistrazioni/e3c22.md`. Scelta 1 = qo, k, sh, -ey; regressione dentro strati (classe, parola coperta); x per 10 segni.', '',
          '| termine | ZL (IC 95%) | IT (IC 95%) |', '|---|---|---|']
    for nm in ('x', 'F', 'L', 'S', 'E', 'E − L', 'S − F'):
        a = z.get(nm)
        b = ris['IT'].get(nm)
        f = lambda t: '—' if t is None else '%+.4f (%+.4f – %+.4f)' % (t['coefficiente'], t['IC95'][0], t['IC95'][1])
        md.append('| %s | %s | %s |' % (nm, f(a), f(b)))
    md += ['', 'Parole: ZL %d, IT %d. Esito (ZL): **%s**.' % (z['parole'], ris['IT']['parole'], esito)]
    open(os.path.join(RISULTATI, 'e3c22_bordi_e_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
