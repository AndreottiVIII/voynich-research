# -*- coding: utf-8 -*-
"""Esperimento e3c33: l'accordo delle scelte dentro la riga è una preferenza della riga (uguale a ogni distanza) o una
memoria che si consuma (cala con la distanza)? K(d) per d = 1…8 nelle righe di almeno 11 parole (senza la prima e
l'ultima), con l'atteso dalla stessa parola coperta più lo scarto della pagina (senza le due parole della coppia) più la
deriva lungo la riga (β·(x − x̄ della pagina), β a parità di parola come nell'e3c13). P = K(6–8) / K(1), intervallo
ricampionando pagine. Voynich ZL e IT; lingue (e3c28) in righe finte con le lunghezze del Voynich, come descrizione.

Preregistrazione: preregistrazioni/e3c33.md. Scrive risultati/e3c33_riga_o_memoria.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b98_forma_lingue as e3b98
import e3c10_strati_lettere_parole as e3c10
import e3c28_forma_alla_pari as e3c28

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
MIN_PAROLE = 11
DMAX = 8


def raccogli(pagine, classi):
    """pagine: [(mano, [righe di parole come tuple])]. Parole interne delle righe lunghe:
    (pagina, mano, id riga, posizione, segni prima, classe, valore, parola coperta)."""
    tok, nr = [], 0
    for p, (h, righe) in enumerate(pagine):
        for r in righe:
            nr += 1
            if len(r) < MIN_PAROLE:
                continue
            prima = len(r[0])
            for i, w in enumerate(r[1:-1]):
                for k, f in classi.items():
                    x = f(w)
                    if x is not None:
                        tok.append((p, h, nr, i, prima, k, x[0], x[1]))
                prima += len(w)
    return tok


def preparazione(tok):
    v = np.array([t[6] for t in tok], dtype=float)
    x = np.array([t[4] for t in tok], dtype=float)
    s, n = defaultdict(float), defaultdict(int)
    for t, val in zip(tok, v):
        s[(t[1], t[5], t[7])] += val
        n[(t[1], t[5], t[7])] += 1
    sm, nm = defaultdict(float), defaultdict(int)
    for t, val in zip(tok, v):
        sm[(t[1], t[5])] += val
        nm[(t[1], t[5])] += 1
    mano = np.array([(sm[(t[1], t[5])] - val) / (nm[(t[1], t[5])] - 1) for t, val in zip(tok, v)])
    tipo = np.array([(s[(t[1], t[5], t[7])] - val) / (n[(t[1], t[5], t[7])] - 1) if n[(t[1], t[5], t[7])] > 1 else np.nan for t, val in zip(tok, v)])
    tipo = np.where(np.isnan(tipo), mano, tipo)
    sp, npg, sx = defaultdict(float), defaultdict(int), defaultdict(float)
    for t, val in zip(tok, v):
        sp[(t[0], t[5])] += val
        npg[(t[0], t[5])] += 1
        sx[(t[0], t[5])] += t[4]
    beta = {}
    for k in {t[5] for t in tok}:
        idx = [j for j, t in enumerate(tok) if t[5] == k]
        _, strato = np.unique(np.array([hash((tok[j][1], tok[j][7])) for j in idx]), return_inverse=True)
        st = e3c10.statistiche(strato, x[idx], v[idx], np.zeros(len(idx), dtype=int), 1, int(strato.max()) + 1)
        beta[k] = float(e3c10.pendenza(st.sum(0)))
    return v, x, tipo, mano, sp, npg, sx, beta


def somme(tok, n_p):
    v, x, tipo, mano, sp, npg, sx, beta = preparazione(tok)
    per_riga = defaultdict(dict)
    for j, t in enumerate(tok):
        per_riga[(t[2], t[5])][t[3]] = j
    out = np.zeros((n_p, DMAX, 2))
    for (_, k), pos in per_riga.items():
        for i, a in pos.items():
            for d in range(1, DMAX + 1):
                b = pos.get(i + d)
                if b is None or tok[a][7] == tok[b][7] or e3a86.una_modifica(tok[a][7], tok[b][7]):
                    continue
                ch = (tok[a][0], k)
                if npg[ch] > 2:
                    off = (sp[ch] - v[a] - v[b]) / (npg[ch] - 2)
                    xm = (sx[ch] - x[a] - x[b]) / (npg[ch] - 2)
                    pa = tipo[a] + off - mano[a] + beta[k] * (x[a] - xm)
                    pb = tipo[b] + off - mano[b] + beta[k] * (x[b] - xm)
                else:
                    pa, pb = tipo[a], tipo[b]
                pa, pb = min(max(pa, 0.01), 0.99), min(max(pb, 0.01), 0.99)
                att = pa * pb + (1 - pa) * (1 - pb)
                out[tok[a][0], d - 1, 0] += (v[a] == v[b]) - att
                out[tok[a][0], d - 1, 1] += 1 - att
    return out


def profilo(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        k = s[..., 0] / s[..., 1]
        lontane = s[..., 5:8, 0].sum(-1) / s[..., 5:8, 1].sum(-1)
        return k, lontane, lontane / k[..., 0]


def misura(pagine, classi, rng):
    tok = raccogli(pagine, classi)
    n_p = len(pagine)
    st = somme(tok, n_p)
    k, lont, P = profilo(st.sum(0))
    boot = [profilo(st[rng.integers(0, n_p, n_p)].sum(0)) for _ in range(BOOT)]
    bp = np.array([b[2] for b in boot])
    bl = np.array([b[1] for b in boot])
    bk1 = np.array([b[0][0] for b in boot])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    return OrderedDict([('profilo', [float(z) for z in k]), ('K1', float(k[0])), ('K1_IC95', ic(bk1)), ('K6_8', float(lont)), ('K6_8_IC95', ic(bl)),
                        ('P', float(P)), ('P_IC95', ic(bp)), ('parole', len(tok))])


def main():
    rng = np.random.default_rng(3333)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('Voynich ZL', e341.pagine()), ('Voynich IT', e3b45.pagine_it())):
        pagine = []
        for pg, pars in pd.items():
            if mano.get(pg):
                pagine.append((mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]))
        ris[q] = misura(pagine, e3b62.CV, rng)
        print(q, json.dumps(ris[q]), flush=True)
    lung = e3c28.lunghezze_voynich()
    prima = json.load(open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), encoding='utf-8'))['lingue']
    tt = e381.testi()
    testi = OrderedDict()
    for nome in (k for k, x in prima.items() if x['conta'] and x['R'] is not None):
        parole = [w for r in tt[nome + '.txt'] if r for w in r]
        f, _ = e3b98.classe_generica([parole])
        testi[nome + ' (classe generica)'] = (parole, f)
    for nome, (chiave, t) in e3b91.TESTI.items():
        parole = [w for r in tt[chiave] if r for w in r]
        testi[nome + ' (' + ('-o/-a' if t == 'romanzo' else '-us/-a') + ')'] = (parole, e3b91.oa if t == 'romanzo' else e3b91.usa)
    for nome, (parole, f) in testi.items():
        rr = e3c28.righe_finte(parole, lung)
        pagine = [('x', rr[i:i + 25]) for i in range(0, len(rr), 25)]
        ris[nome] = misura(pagine, OrderedDict([('x', f)]), rng)
        print(nome, json.dumps(ris[nome]), flush=True)
    esiti = OrderedDict()
    for q in ('Voynich ZL', 'Voynich IT'):
        x = ris[q]
        if x['K6_8_IC95'][0] > 0 and x['P'] >= 0.5:
            esiti[q] = 'preferenza della riga'
        elif x['P'] < 0.25:
            esiti[q] = 'memoria che si consuma'
        else:
            esiti[q] = 'intermedio'
    out = OrderedDict([('testi', ris), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c33_riga_o_memoria.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c33 — Preferenza della riga o memoria che si consuma?', '', 'Preregistrazione: `preregistrazioni/e3c33.md`. Righe di almeno 11 parole, senza bordi; atteso: stessa parola + pagina + deriva. P = K(6–8) / K(1).', '',
          '| testo | parole | K(1) (IC 95%) | K(6–8) (IC 95%) | P (IC 95%) | profilo d = 1…8 |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s |' % (k, x['parole'], x['K1'], x['K1_IC95'][0], x['K1_IC95'][1], x['K6_8'], x['K6_8_IC95'][0], x['K6_8_IC95'][1],
                                                                                                    x['P'], x['P_IC95'][0], x['P_IC95'][1], ' '.join('%+.3f' % z for z in x['profilo'])))
    md += [''] + ['Esito %s: **%s**.' % (q, e) for q, e in esiti.items()]
    open(os.path.join(RISULTATI, 'e3c33_riga_o_memoria.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
