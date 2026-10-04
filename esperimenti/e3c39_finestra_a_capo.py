# -*- coding: utf-8 -*-
"""Esperimento e3c39: la finestra delle scelte passa l'a capo? Con la misura pulita (atteso stessa parola + pagina +
deriva), K fra la penultima parola di una riga e la seconda della riga seguente (distanza 3 parole contando l'ultima e la
prima, escluse come bordi) contro K a distanza 3 dentro la riga (parole interne) e contro un controllo: la penultima
parola di una riga e la seconda di due righe sotto (stesse posizioni, nessuna continuità di scrittura). Stesso paragrafo.
Classi k/t, sh/ch, -ey/-dy insieme (dove sta la finestra, e3c35) e qo/o da sola. ZL e IT.

Preregistrazione: preregistrazioni/e3c39.md. Scrive risultati/e3c39_finestra_a_capo.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
TRE = ('k/t', 'sh/ch', '-ey/-dy')
GRUPPI = ('dentro la riga, d = 3', 'a capo, d = 3', 'controllo: due righe sotto')


def raccogli(pd, mano, classi):
    """Parole delle classi con: pagina, mano, paragrafo, riga nel paragrafo, posizione, lunghezza riga, segni prima."""
    tok = []
    for p, (pg, pars) in enumerate(pd.items()):
        h = mano.get(pg)
        if not h:
            continue
        for npar, par in enumerate(pars):
            for nr, r in enumerate(par):
                ws = [tuple(e3b62.D(w)) for w in r if w]
                prima = 0
                for i, w in enumerate(ws):
                    for k, f in classi.items():
                        x = f(w)
                        if x is not None:
                            tok.append(dict(p=p, h=h, par=npar, riga=nr, pos=i, L=len(ws), x=prima, k=k, v=float(x[0]), c=x[1]))
                    prima += len(w)
    return tok


def attese(tok):
    """Atteso di ogni parola: stessa parola coperta nella mano (senza la parola) + scarto di pagina + deriva (β·(x − x̄))."""
    v = np.array([t['v'] for t in tok])
    x = np.array([t['x'] for t in tok], dtype=float)
    def somma(chiavi):
        s, n = defaultdict(float), defaultdict(int)
        for c, val in zip(chiavi, v):
            s[c] += val
            n[c] += 1
        return s, n
    st, nt = somma([(t['h'], t['k'], t['c']) for t in tok])
    sm, nm = somma([(t['h'], t['k']) for t in tok])
    sp, npg = somma([(t['p'], t['k']) for t in tok])
    sx = defaultdict(float)
    for t in tok:
        sx[(t['p'], t['k'])] += t['x']
    beta = {}
    for k in {t['k'] for t in tok}:
        idx = [j for j, t in enumerate(tok) if t['k'] == k and 0 < t['pos'] < t['L'] - 1]
        _, strato = np.unique(np.array([hash((tok[j]['h'], tok[j]['c'])) for j in idx]), return_inverse=True)
        s = e3c10.statistiche(strato, x[idx], v[idx], np.zeros(len(idx), dtype=int), 1, int(strato.max()) + 1)
        beta[k] = float(e3c10.pendenza(s.sum(0)))
    p = np.zeros(len(tok))
    for j, t in enumerate(tok):
        kt, km, kp = (t['h'], t['k'], t['c']), (t['h'], t['k']), (t['p'], t['k'])
        mano = (sm[km] - v[j]) / (nm[km] - 1)
        tipo = (st[kt] - v[j]) / (nt[kt] - 1) if nt[kt] > 1 else mano
        pag = (sp[kp] - v[j]) / (npg[kp] - 1) if npg[kp] > 1 else mano
        xm = (sx[kp] - x[j]) / (npg[kp] - 1) if npg[kp] > 1 else x[j]
        p[j] = min(max(tipo + pag - mano + beta[t['k']] * (x[j] - xm), 0.01), 0.99)
    return v, p


def somme(tok, n_p):
    v, p = attese(tok)
    idx = defaultdict(dict)
    for j, t in enumerate(tok):
        idx[(t['p'], t['par'], t['riga'], t['k'])][t['pos']] = j
    out = np.zeros((n_p, len(GRUPPI), 3))

    def aggiungi(a, b, g):
        if tok[a]['c'] == tok[b]['c'] or e3a86.una_modifica(tok[a]['c'], tok[b]['c']):
            return
        att = p[a] * p[b] + (1 - p[a]) * (1 - p[b])
        out[tok[a]['p'], g, 0] += (v[a] == v[b]) - att
        out[tok[a]['p'], g, 1] += 1 - att
        out[tok[a]['p'], g, 2] += 1
    for (pg, par, riga, k), pos in idx.items():
        for i, a in pos.items():
            L = tok[a]['L']
            if 0 < i < L - 1 and 0 < i + 3 < L - 1 and (i + 3) in pos:
                aggiungi(a, pos[i + 3], 0)
            if i == L - 2 and L >= 4:
                for g, dr in ((1, 1), (2, 2)):
                    nxt = idx.get((pg, par, riga + dr, k), {})
                    b = nxt.get(1)
                    if b is not None and tok[b]['L'] >= 4:
                        aggiungi(a, b, g)
    return out


def main():
    rng = np.random.default_rng(3339)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        for nome, chiavi in (('k/t, sh/ch, -ey/-dy', TRE), ('qo/o', ('qo/o',))):
            tok = raccogli(pd, mano, OrderedDict((k, e3b62.CV[k]) for k in chiavi))
            n_p = max(t['p'] for t in tok) + 1
            st = somme(tok, n_p)
            k = st.sum(0)[:, 0] / st.sum(0)[:, 1]
            boot = []
            for _ in range(BOOT):
                s = st[rng.integers(0, n_p, n_p)].sum(0)
                boot.append(s[:, 0] / s[:, 1])
            boot = np.array(boot)
            quota = boot[:, 1] / boot[:, 0]
            x = OrderedDict((g, OrderedDict([('K', float(k[i])), ('IC95', [float(np.percentile(boot[:, i], 2.5)), float(np.percentile(boot[:, i], 97.5))]), ('coppie', int(st.sum(0)[i, 2]))]))
                            for i, g in enumerate(GRUPPI))
            x['quota che passa (a capo / dentro)'] = OrderedDict([('valore', float(k[1] / k[0])), ('IC95', [float(np.nanpercentile(quota, 2.5)), float(np.nanpercentile(quota, 97.5))])])
            ris['%s, %s' % (q, nome)] = x
            print(q, nome, json.dumps(x), flush=True)
    esiti = OrderedDict()
    for q in ('ZL', 'IT'):
        x = ris['%s, k/t, sh/ch, -ey/-dy' % q]
        dentro, capo, ctrl = (x[g] for g in GRUPPI)
        if capo['IC95'][0] > ctrl['IC95'][1]:
            esiti[q] = 'la finestra passa l\'a capo (sopra il controllo)'
        elif capo['IC95'][0] <= ctrl['K'] <= capo['IC95'][1] and capo['K'] < dentro['K'] / 2:
            esiti[q] = 'la finestra non passa l\'a capo'
        else:
            esiti[q] = 'incerto'
    out = OrderedDict([('misure', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c39_finestra_a_capo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c39 — La finestra delle scelte passa l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3c39.md`. Atteso: stessa parola + pagina + deriva.', '',
          '| trascrizione, classi | dentro la riga, d = 3 | a capo, d = 3 | controllo (due righe sotto) | quota che passa |', '|---|---|---|---|---|']
    for k, x in ris.items():
        cel = ['%+.3f (%+.3f – %+.3f), %d coppie' % (x[g]['K'], x[g]['IC95'][0], x[g]['IC95'][1], x[g]['coppie']) for g in GRUPPI]
        qq = x['quota che passa (a capo / dentro)']
        md.append('| %s | %s | %.2f (%.2f – %.2f) |' % (k, ' | '.join(cel), qq['valore'], qq['IC95'][0], qq['IC95'][1]))
    md += [''] + ['Esito %s (k/t, sh/ch, -ey/-dy): **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c39_finestra_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
