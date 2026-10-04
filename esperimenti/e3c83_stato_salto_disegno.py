# -*- coding: utf-8 -*-
"""Esperimento e3c83: lo stato breve delle scelte sopravvive al salto di un disegno dentro la riga? K corretto (e3c48)
per coppie della stessa scelta (qo/o, k/t, sh/ch, -ey/-dy) a distanza 1 – 3 nella riga (K di ogni gruppo = media dei
K alle tre distanze, così i gruppi si confrontano a parità di distanza): (A) con un salto del disegno in
mezzo; (B) nello stesso tratto, nelle righe che hanno un salto (stesse righe, stesse posizioni circa); (C) nelle righe
senza salto (riferimento). Rifà con la correzione l'e3b67 (misura vecchia: "passa il salto"). Salti = separatore <->
della trascrizione (e395.righe). Voynich ZL e IT.

Preregistrazione: preregistrazioni/e3c83.md. Scrive risultati/e3c83_stato_salto_disegno.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a86_ripetizioni_riga as e3a86
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33
import e3c48_finestra_corretta as e3c48
import e3c68_segno_che_azzera as e3c68

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
GRUPPI = ('A: attraverso il salto', 'B: stesso tratto (righe con salto)', 'C: righe senza salto')
PERM = 50
BOOT = 2000


def pagine_con_salti(quale, mano):
    """[(mano, [righe di parole])] e, per ogni riga nell'ordine di e3c33.raccogli, l'insieme dei salti (indici k: salto fra
    la parola k e la k+1)."""
    per, salti = OrderedDict(), []
    for st, pg, npar, ws, seps in e395.righe(quale):
        if not mano.get(pg):
            continue
        per.setdefault(pg, []).append(([w if w else () for w in ws], {k for k, s in enumerate(seps) if s == '|'}))
    pagine = []
    for pg, rr in per.items():
        pagine.append((mano[pg], [r for r, _ in rr]))
        salti += [s for _, s in rr]
    return pagine, salti


def somme(tok, n_p, salti):
    v, p = e3c68.attese(tok)
    per = defaultdict(dict)
    for j, t in enumerate(tok):
        per[(t[2], t[5])][t[3]] = j
    out = np.zeros((n_p, len(GRUPPI), 3, 2))
    for (rid, k), pos in per.items():
        ss = salti[rid - 1]
        for i, a in pos.items():
            for d in (1, 2, 3):
                b = pos.get(i + d)
                if b is None or tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                    continue
                attraverso = any(i + 1 <= g < i + d + 1 for g in ss)
                g = 0 if attraverso else (1 if ss else 2)
                att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
                out[tok[a][0], g, d - 1, 0] += (v[a] == v[b]) - att
                out[tok[a][0], g, d - 1, 1] += 1 - att
    return out


def kappa(s):
    """(..., gruppi, 3 distanze, 2) -> K per gruppo come media delle tre distanze (a parità di distanza)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.nanmean(s[..., 0] / s[..., 1], axis=-1)


def misura(pagine, salti, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    n_p = len(pagine)
    oss = somme(tok, n_p, salti)
    nul = np.mean([somme(e3c48.rimescola(tok, rng), n_p, salti) for _ in range(PERM)], axis=0)
    kc = kappa(oss.sum(0)) - kappa(nul.sum(0))
    boot = np.array([kappa(oss[i].sum(0)) - kappa(nul[i].sum(0)) for i in (rng.integers(0, n_p, n_p) for _ in range(BOOT))])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    ris = OrderedDict([('parole', len(tok))])
    for g, nome in enumerate(GRUPPI):
        ris[nome] = OrderedDict([('coppie_pesate', float(oss.sum(0)[g, :, 1].sum())), ('K_corretto', float(kc[g])), ('IC95', ic(boot[:, g]))])
    ris['A − B'] = OrderedDict([('valore', float(kc[0] - kc[1])), ('IC95', ic(boot[:, 0] - boot[:, 1]))])
    return ris


def voce(x):
    a, b = x[GRUPPI[0]], x[GRUPPI[1]]
    if a['IC95'][0] > 0.02 and a['K_corretto'] >= b['K_corretto'] / 2:
        return 'lo stato sopravvive al salto del disegno'
    if a['IC95'][0] <= 0 <= a['IC95'][1] and b['IC95'][0] > 0.02:
        return 'il salto del disegno azzera lo stato'
    return 'incerto'


def main():
    rng = np.random.default_rng(3383)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        pagine, salti = pagine_con_salti(q, mano)
        x = misura(pagine, salti, cl, rng)
        x['righe_con_salto'] = sum(1 for s in salti if s)
        x['voce'] = voce(x)
        ris[q] = x
        print(q, json.dumps(x, ensure_ascii=False), flush=True)
    a, b = ris['ZL']['voce'], ris['IT']['voce']
    esito = a if a == b else 'ZL: %s; IT: %s' % (a, b)
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c83_stato_salto_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c83 — Lo stato breve sopravvive al salto del disegno?', '', 'Preregistrazione: `preregistrazioni/e3c83.md`.', '',
          '| trascrizione | righe con salto | ' + ' | '.join(GRUPPI) + ' | A − B | voce |', '|---|---|' + '---|' * (len(GRUPPI) + 2)]
    for q, x in ris.items():
        md.append('| %s | %d | %s | %+.3f (%+.3f – %+.3f) | %s |' % (q, x['righe_con_salto'], ' | '.join('%+.3f (%+.3f – %+.3f)' % (x[g]['K_corretto'], x[g]['IC95'][0], x[g]['IC95'][1]) for g in GRUPPI),
                                                                  x['A − B']['valore'], *x['A − B']['IC95'], x['voce']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c83_stato_salto_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
