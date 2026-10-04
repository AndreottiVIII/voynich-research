# -*- coding: utf-8 -*-
"""Esperimento e3c68: c'è un segno o una parola dopo cui lo stato delle scelte "riparte"? (idea dell'indice di alfabeto
del disco di Alberti: una lettera-indice nel testo dice "da qui cambia alfabeto"). Coppie della stessa scelta (k/t,
sh/ch, -ey/-dy, qo/o) a distanza 2 nella riga, con in mezzo una parola che non fa quella scelta; per ogni caratteristica
della parola in mezzo (le 40 parole più frequenti; ogni segno presente almeno 300 volte; tre classi di lunghezza),
Δ = K delle coppie con la caratteristica − K delle altre. Significatività con il massimo |z| su tutte le caratteristiche
(1.000 permutazioni delle parole in mezzo fra le coppie della stessa scelta). Voynich ZL e IT.

Preregistrazione: preregistrazioni/e3c68.md. Scrive risultati/e3c68_segno_che_azzera.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
PERM = 1000
TIPI = 40
MIN_SEGNO = 300


def attese(tok):
    v, x, tipo, mano, sp, npg, sx, beta = e3c33.preparazione(tok)
    p = np.empty(len(tok))
    for j, t in enumerate(tok):
        ch = (t[0], t[5])
        if npg[ch] > 1:
            off = (sp[ch] - v[j]) / (npg[ch] - 1)
            xm = (sx[ch] - x[j]) / (npg[ch] - 1)
            p[j] = tipo[j] + off - mano[j] + beta[t[5]] * (x[j] - xm)
        else:
            p[j] = tipo[j]
    return v, np.clip(p, 0.01, 0.99)


def coppie(pagine, classi):
    """[(classe, parola in mezzo, accordo, atteso, pagina)] per coppie a distanza 2 con la parola in mezzo fuori classe."""
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    v, p = attese(tok)
    righe = []
    for h, rr in pagine:
        for r in rr:
            righe.append(r)
    idx = defaultdict(dict)
    for j, t in enumerate(tok):
        idx[(t[2], t[5])][t[3]] = j
    out = []
    for (rid, k), pos in idx.items():
        riga = righe[rid - 1]
        for i, a in pos.items():
            b = pos.get(i + 2)
            if b is None or tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                continue
            m = riga[i + 2]  # parola interna i+1 = riga[i+2]
            if classi[k](m) is not None:
                continue
            att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
            out.append((k, m, float(v[a] == v[b]), att, tok[a][0]))
    return out


def caratteristiche(cc):
    tipi = [w for w, _ in Counter(c[1] for c in cc).most_common(TIPI)]
    segni = [g for g, n in Counter(g for c in cc for g in set(c[1])).most_common() if n >= MIN_SEGNO]
    nomi = ['parola ' + ''.join(w) for w in tipi] + ['contiene ' + g for g in segni] + ['lunghezza ≤ 3', 'lunghezza 4–5', 'lunghezza ≥ 6']
    F = np.zeros((len(cc), len(nomi)), dtype=bool)
    for r, c in enumerate(cc):
        m = c[1]
        for j, w in enumerate(tipi):
            F[r, j] = m == w
        s = set(m)
        for j, g in enumerate(segni):
            F[r, len(tipi) + j] = g in s
        L = len(m)
        F[r, len(tipi) + len(segni) + (0 if L <= 3 else (1 if L <= 5 else 2))] = True
    return nomi, F


def delta(F, num, den):
    sf, df = F.T.astype(float) @ num, F.T.astype(float) @ den
    st, dt = num.sum(), den.sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        return sf / df - (st - sf) / (dt - df), sf / df


def misura(pagine, classi, rng):
    cc = coppie(pagine, classi)
    nomi, F = caratteristiche(cc)
    num = np.array([c[2] - c[3] for c in cc])
    den = np.array([1 - c[3] for c in cc])
    d_oss, k_con = delta(F, num, den)
    gruppi = defaultdict(list)
    for r, c in enumerate(cc):
        gruppi[c[0]].append(r)
    nul = []
    for _ in range(PERM):
        perm = np.arange(len(cc))
        for rr in gruppi.values():
            rr = np.array(rr)
            perm[rr] = rr[rng.permutation(len(rr))]
        nul.append(delta(F[perm], num, den)[0])
    nul = np.array(nul)
    mu, sd = np.nanmean(nul, 0), np.nanstd(nul, 0)
    z = (d_oss - mu) / np.where(sd > 0, sd, np.nan)
    zmax = np.nanmax(np.abs((nul - mu) / np.where(sd > 0, sd, np.nan)), axis=1)
    p_fw = np.array([float(np.mean(zmax >= abs(zz))) if np.isfinite(zz) else 1.0 for zz in z])
    k_tot = float(num.sum() / den.sum())
    zn = (nul - mu) / np.where(sd > 0, sd, np.nan)
    eterogeneita = OrderedDict()
    for nome_g, sel in (('parole', [j for j, n in enumerate(nomi) if n.startswith('parola ')]), ('segni', [j for j, n in enumerate(nomi) if n.startswith('contiene ')])):
        q_oss = float(np.nansum(z[sel] ** 2))
        q_nul = np.nansum(zn[:, sel] ** 2, axis=1)
        eterogeneita[nome_g] = OrderedDict([('Q', q_oss), ('Q_nullo_medio', float(q_nul.mean())), ('p', float(np.mean(q_nul >= q_oss)))])
    righe = []
    for j in np.argsort(np.nan_to_num(z, nan=0.0)):
        righe.append(OrderedDict([('caratteristica', nomi[j]), ('coppie', int(F[:, j].sum())), ('K_con', float(k_con[j])), ('delta', float(d_oss[j])), ('z', float(z[j])), ('p_famiglia', p_fw[j])]))
    azzera = [x for x in righe if x['p_famiglia'] < 0.01 and x['delta'] < 0 and x['K_con'] <= (k_tot - 0) / 2]
    rinforza = [x for x in righe if x['p_famiglia'] < 0.01 and x['delta'] > 0]
    return OrderedDict([('coppie', len(cc)), ('K_tutte', k_tot), ('eterogeneita', eterogeneita), ('caratteristiche', righe), ('azzera', azzera), ('rinforza', rinforza)])


def main():
    rng = np.random.default_rng(3368)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        x = misura(pagine, cl, rng)
        ris[q] = x
        print(q, x['coppie'], x['K_tutte'], json.dumps(x['azzera'], ensure_ascii=False), json.dumps(x['rinforza'], ensure_ascii=False), flush=True)
    az = {q: set(y['caratteristica'] for y in x['azzera']) for q, x in ris.items()}
    comuni = sorted(az['ZL'] & az['IT'])
    et = all(any(e['p'] < 0.01 for e in x['eterogeneita'].values()) for x in ris.values())
    if comuni:
        esito = 'c\'è un segno che azzera lo stato: ' + ', '.join(comuni)
    elif et:
        esito = 'le parole in mezzo contano nel loro insieme (eterogeneità), senza un segno singolo'
    elif az['ZL'] or az['IT']:
        esito = 'incerto (solo in una trascrizione: %s)' % ', '.join(sorted(az['ZL'] | az['IT']))
    else:
        esito = 'nessun segno che azzera lo stato (entro la potenza della prova)'
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c68_segno_che_azzera.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c68 — C\'è un segno dopo cui lo stato riparte?', '', 'Preregistrazione: `preregistrazioni/e3c68.md`. Coppie della stessa scelta a distanza 2 con la parola in mezzo fuori dalla scelta; Δ = K con la caratteristica − K senza.', '']
    for q, x in ris.items():
        md += ['## %s (%d coppie, K di tutte %+.3f)' % (q, x['coppie'], x['K_tutte']), '', '| caratteristica della parola in mezzo | coppie | K con | Δ | z | p (famiglia) |', '|---|---|---|---|---|---|']
        sel = x['caratteristiche'][:8] + x['caratteristiche'][-5:]
        for y in sel:
            md.append('| %s | %d | %+.3f | %+.3f | %.1f | %.3f |' % (y['caratteristica'], y['coppie'], y['K_con'], y['delta'], y['z'], y['p_famiglia']))
        md += ['', 'Eterogeneità: ' + '; '.join('%s Q %.1f (nullo %.1f), p %.3f' % (g, e['Q'], e['Q_nullo_medio'], e['p']) for g, e in x['eterogeneita'].items()) + '.']
        md += ['', 'Azzerano (p di famiglia < 0,01, Δ < 0, K con ≤ metà): %s.' % (', '.join(y['caratteristica'] for y in x['azzera']) or 'nessuna'),
               'Rinforzano (p < 0,01, Δ > 0): %s.' % (', '.join(y['caratteristica'] for y in x['rinforza']) or 'nessuna'), '']
    md += ['Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c68_segno_che_azzera.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
