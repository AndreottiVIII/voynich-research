# -*- coding: utf-8 -*-
"""Esperimento e3c28: la forma del calo (R = [K(3) − K(8–12)] / [K(1) − K(8–12)]) misurata alla pari nel Voynich e nelle
lingue: le lingue tagliate in righe finte con le stesse lunghezze (in parole) delle righe del Voynich, unità di 25 righe;
per tutti righe senza la prima e l'ultima parola, coppie solo dentro la riga, atteso dalla stessa parola coperta
(lasciando fuori la parola stessa). Voynich IT e ZL (classi scelte a mano), le 16 lingue dell'e3b98 (classe generica) e
le 5 dell'e3b92 (-o/-a, -us/-a).

Preregistrazione: preregistrazioni/e3c28.md. Scrive risultati/e3c28_forma_alla_pari.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b98_forma_lingue as e3b98
import e3c07_lettere_parole_bilanciate as e3c07
import e3c09_regressione_lettere_parole as e3c09

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
GRUPPI = ('d1', 'd3', 'lontane')


def gruppo(d):
    return 0 if d == 1 else (1 if d == 3 else (2 if d >= 8 else -1))


def somme(cc, n_u):
    """(unità, gruppo, [accordi, attesi, coppie]) con l'atteso dalla stessa parola coperta."""
    out = np.zeros((n_u, 3, 3))
    for k, c in cc.items():
        val, grp = c['val'], c['grp']
        G = np.bincount(grp, weights=val)
        N = np.bincount(grp).astype(float)
        gen = (val.sum() - val) / (len(val) - 1)
        p = np.where(N[grp] > 1, (G[grp] - val) / np.maximum(N[grp] - 1, 1), gen)
        pi, pj = p[c['I']], p[c['J']]
        att = pi * pj + (1 - pi) * (1 - pj)
        ok = (val[c['I']] == val[c['J']]).astype(float)
        g = np.array([gruppo(d) for d in c['d']])
        u = c['uni'][c['I']]
        for gg in range(3):
            m = g == gg
            for col, w in enumerate((ok, att, np.ones_like(ok))):
                out[:, gg, col] += np.bincount(u[m], weights=w[m], minlength=n_u)
    return out


def erre(s):
    o, a, n = s[..., 0], s[..., 1], s[..., 2]
    with np.errstate(divide='ignore', invalid='ignore'):
        k = (o - a) / (n - a)
        acc = k[..., 0] - k[..., 2]
        return np.where(acc > 0, (k[..., 1] - k[..., 2]) / acc, np.nan), acc


def misura(uu, ss, classi, rng):
    e3c09.DIST = range(1, 13)
    cc = OrderedDict((k, e3c09.prepara(uu, ss, f)) for k, f in classi.items())
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
    st = somme(cc, len(uu))
    r, acc = erre(st.sum(0))
    bs = [erre(st[rng.integers(0, len(uu), len(uu))].sum(0)) for _ in range(BOOT)]
    br = np.array([b[0] for b in bs])
    ba = np.array([b[1] for b in bs])
    br = br[np.isfinite(br)]
    ic = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))] if len(a) > BOOT / 2 else [None, None]
    n_l = int(st[:, 2, 2].sum())
    return OrderedDict([('R', float(r) if np.isfinite(r) else None), ('R_IC95', ic(br)), ('accanto', float(acc)), ('accanto_IC95', ic(ba)), ('coppie_lontane', n_l)])


def lunghezze_voynich():
    """Numero di parole delle righe del Voynich (ZL), in ordine."""
    out = []
    for pars in e341.pagine().values():
        for par in pars:
            for r in par:
                out.append(len(r))
    return out


def righe_finte(parole, lunghezze):
    out, i, k = [], 0, 0
    while i < len(parole):
        n = lunghezze[k % len(lunghezze)]
        out.append(parole[i:i + n])
        i += n
        k += 1
    return [r for r in out if r]


def main():
    rng = np.random.default_rng(3328)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        uu, ss = e3b62.voynich(pd, mano)
        ris[q] = misura(e3c07.senza_bordi(uu), ss, e3b62.CV, rng)
        print(q, json.dumps(ris[q]), flush=True)
    lung = lunghezze_voynich()
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
        rr = righe_finte(parole, lung)
        uu = e3c07.senza_bordi([rr[i:i + 25] for i in range(0, len(rr), 25)])
        x = misura(uu, [nome] * len(uu), OrderedDict([('x', f)]), rng)
        x['conta'] = x['accanto_IC95'][0] is not None and x['accanto_IC95'][0] > 0.02
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    v = [ris[q]['R_IC95'][0] for q in ('Voynich IT', 'Voynich ZL')]
    soglia = min(x for x in v if x is not None) if any(x is not None for x in v) else None
    lingue = [k for k in ris if not k.startswith('Voynich') and ris[k]['conta'] and ris[k]['R'] is not None]
    sopra = [k for k in lingue if soglia is not None and ris[k]['R'] >= soglia]
    if soglia is None:
        esito = 'R del Voynich non definito'
    elif not sopra:
        esito = 'alla pari la forma piatta resta propria del Voynich'
    elif len(sopra) >= 3:
        esito = 'alla pari la forma piatta non è propria del Voynich'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('soglia', soglia), ('lingue_che_contano', len(lingue)), ('lingue_sopra', sopra), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c28_forma_alla_pari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def due(a):
        return '—' if a is None else '%.2f' % a
    md = ['# e3c28 — La forma del calo alla pari: Voynich e lingue in righe della stessa lunghezza', '', 'Preregistrazione: `preregistrazioni/e3c28.md`. Righe senza bordi, coppie dentro la riga, atteso dalla stessa parola coperta.', '',
          '| testo | accordo accanto (IC 95%) | R (IC 95%) | coppie lontane | conta |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %+.3f (%s – %s) | %s (%s – %s) | %d | %s |' % (k, x['accanto'], due(x['accanto_IC95'][0]), due(x['accanto_IC95'][1]), due(x['R']), due(x['R_IC95'][0]), due(x['R_IC95'][1]),
                                                                    x['coppie_lontane'], {True: 'sì', False: 'no'}.get(x.get('conta'), 'Voynich')))
    md += ['', 'Soglia (estremo basso di R più piccolo fra i due Voynich): %s. Lingue che contano: %d; sopra la soglia: %s.' % (due(soglia), len(lingue), ', '.join(sopra) or 'nessuna'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c28_forma_alla_pari.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
