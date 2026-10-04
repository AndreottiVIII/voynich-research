# -*- coding: utf-8 -*-
"""Esperimento e3c21: dopo il salto di un disegno in mezzo alla riga, le scelte "marcate" (qo, k, sh, -ey) ripartono come a
inizio riga, o la deriva continua? Regressione dentro strati (classe, parola coperta) della scelta su x (segni scritti
prima nella riga), S (prima parola dopo un salto) ed E (ultima parola prima di un salto). Righe di paragrafo della ZL
(i salti sono segnati solo lì) senza parole incerte, senza la prima e l'ultima parola della riga; intervalli
ricampionando pagine.

Preregistrazione: preregistrazioni/e3c21.md. Scrive risultati/e3c21_deriva_salto_disegno.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
NOMI = ('x', 'S', 'E')


def osservazioni(righe, classi):
    """(pagina, strato, [x, S, E], valore) per le parole interne delle righe senza parole incerte."""
    out = []
    for _, pag, _, ws, seps in righe:
        if any(w is None for w in ws) or len(ws) < 3:
            continue
        prima = 0
        for i, w in enumerate(ws):
            if 0 < i < len(ws) - 1:
                s = 1.0 if seps[i - 1] == '|' else 0.0
                e = 1.0 if seps[i] == '|' else 0.0
                for k, f in classi.items():
                    x = f(w)
                    if x is not None:
                        out.append((pag, (k, x[1]), [float(prima), s, e], float(x[0])))
            prima += len(w)
    return out


def statistiche(obs):
    """Per (pagina, strato): n, Σz, Σzzᵀ con z = (x, S, E, y)."""
    pagine = sorted({o[0] for o in obs})
    ip = {p: i for i, p in enumerate(pagine)}
    strati = {}
    for o in obs:
        strati.setdefault(o[1], len(strati))
    n_u, n_s, k = len(pagine), len(strati), len(NOMI) + 1
    n = np.zeros((n_u, n_s))
    sz = np.zeros((n_u, n_s, k))
    szz = np.zeros((n_u, n_s, k, k))
    for p, s, xs, y in obs:
        z = np.array(xs + [y])
        u, t = ip[p], strati[s]
        n[u, t] += 1
        sz[u, t] += z
        szz[u, t] += np.outer(z, z)
    return n, sz, szz


def coefficienti(n, sz, szz):
    """Regressione dentro gli strati; n (strati,), sz (strati, k+1), szz (strati, k+1, k+1), già sommati sulle unità."""
    ok = n > 0
    media = sz[ok] / n[ok, None]
    C = (szz[ok] - n[ok, None, None] * media[:, :, None] * media[:, None, :]).sum(0)
    k = len(NOMI)
    return np.linalg.solve(C[:k, :k], C[:k, k])


def main(righe=None, classi=None, uscita=True):
    rng = np.random.default_rng(3321)
    righe = e386.righe() if righe is None else righe
    obs = osservazioni(righe, e3b62.CV if classi is None else classi)
    n, sz, szz = statistiche(obs)
    oss = coefficienti(n.sum(0), sz.sum(0), szz.sum(0))
    n_u = n.shape[0]
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n_u, n_u)
        try:
            boot.append(coefficienti(n[idx].sum(0), sz[idx].sum(0), szz[idx].sum(0)))
        except np.linalg.LinAlgError:
            continue
    boot = np.array(boot)
    ris = OrderedDict()
    for i, nome in enumerate(NOMI):
        ris[nome] = OrderedDict([('coefficiente', float(oss[i])), ('IC95', [float(np.percentile(boot[:, i], 2.5)), float(np.percentile(boot[:, i], 97.5))])])
    S_obs = [o for o in obs if o[2][1] == 1]
    x_s = float(np.mean([o[2][0] for o in S_obs])) if S_obs else 0.0
    riparte = -oss[0] * x_s
    ris['x_medio_prima_parola_dopo_il_salto'] = x_s
    ris['salto_atteso_se_riparte'] = float(riparte)
    ris['parole'] = len(obs)
    ris['parole_dopo_un_salto'] = len(S_obs)
    ic = ris['S']['IC95']
    if ic[0] > 0:
        esito = 'dopo il salto del disegno le forme marcate ripartono'
    elif ic[0] <= 0 <= ic[1] and ic[1] < riparte / 2:
        esito = 'dopo il salto del disegno la deriva continua (nessuna ripartenza)'
    else:
        esito = 'incerto'
    ris['esito'] = esito
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    if not uscita:
        return ris
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c21_deriva_salto_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c21 — Dopo il salto di un disegno le forme marcate ripartono?', '', 'Preregistrazione: `preregistrazioni/e3c21.md`. ZL, regressione dentro strati (classe, parola coperta); 1 = qo, k, sh, -ey.', '',
          '| termine | coefficiente (IC 95%) |', '|---|---|',
          '| x, per 10 segni scritti prima | %+.4f (%+.4f – %+.4f) |' % (10 * ris['x']['coefficiente'], 10 * ris['x']['IC95'][0], 10 * ris['x']['IC95'][1]),
          '| S, prima parola dopo un salto | %+.4f (%+.4f – %+.4f) |' % (ris['S']['coefficiente'], ris['S']['IC95'][0], ris['S']['IC95'][1]),
          '| E, ultima parola prima di un salto | %+.4f (%+.4f – %+.4f) |' % (ris['E']['coefficiente'], ris['E']['IC95'][0], ris['E']['IC95'][1]),
          '', 'Parole: %d, di cui %d prime dopo un salto (x medio %.1f segni). Salto atteso se la deriva ripartisse del tutto: %+.3f.' % (ris['parole'], ris['parole_dopo_un_salto'], x_s, riparte),
          '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c21_deriva_salto_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
