# -*- coding: utf-8 -*-
"""Esperimento e3c34: il rapporto R0 = K(3) / K(1) con l'atteso completo (stessa parola + pagina + deriva, e3c33) su tutte le
righe di almeno 6 parole (senza la prima e l'ultima): Voynich ZL e IT con le classi scelte a mano; ZL, IT e GC (v101) con
le classi automatiche dell'e3c01; le lingue dell'e3c28 in righe finte con le lunghezze del Voynich.

Preregistrazione: preregistrazioni/e3c34.md. Scrive risultati/e3c34_finestra_tre_parole.json e .md.
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
import e3c01_alternanze_interne as e3c01
import e3c05_terza_trascrizione as e3c05
import e3c28_forma_alla_pari as e3c28
import e3c33_riga_o_memoria as e3c33

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def erre(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        k = s[..., 0] / s[..., 1]
        return k, k[..., 2] / k[..., 0]


def misura(pagine, classi, rng):
    e3c33.MIN_PAROLE, e3c33.DMAX = 6, 3
    tok = e3c33.raccogli(pagine, classi)
    st = e3c33.somme(tok, len(pagine))
    k, r = erre(st.sum(0))
    boot = [erre(st[rng.integers(0, len(pagine), len(pagine))].sum(0)) for _ in range(BOOT)]
    bk1 = np.array([b[0][0] for b in boot])
    br = np.array([b[1] for b in boot])
    ic = lambda a: [float(np.nanpercentile(a, 2.5)), float(np.nanpercentile(a, 97.5))]
    return OrderedDict([('K', [float(z) for z in k]), ('K1_IC95', ic(bk1)), ('R0', float(r)), ('R0_IC95', ic(br)), ('parole', len(tok))])


def main():
    rng = np.random.default_rng(3334)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    voy = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        voy[q] = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
    uu, ss = e3c05.unita_gc(mano)
    voy['GC (v101)'] = list(zip(ss, uu))
    for q in ('ZL', 'IT'):
        ris['Voynich %s, classi a mano' % q] = misura(voy[q], e3b62.CV, rng)
        print(q, json.dumps(ris['Voynich %s, classi a mano' % q]), flush=True)
    for q, pagine in voy.items():
        scelte, _ = e3c01.alternanze([r for _, rr in pagine for r in rr])
        classi = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
        nome = 'Voynich %s, classi automatiche (%s)' % (q, ', '.join(classi))
        ris[nome] = misura(pagine, classi, rng)
        print(nome, json.dumps(ris[nome]), flush=True)
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
        x = misura([('x', rr[i:i + 25]) for i in range(0, len(rr), 25)], OrderedDict([('x', f)]), rng)
        x['conta'] = x['K1_IC95'][0] > 0.02
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    vv = [k for k in ris if k.startswith('Voynich')]
    soglia = min(ris[k]['R0_IC95'][0] for k in vv[:2])
    lingue = [k for k in ris if not k.startswith('Voynich') and ris[k]['conta']]
    sopra = [k for k in lingue if ris[k]['R0'] >= soglia]
    if not sopra:
        esito = 'la finestra di tre parole resta propria del Voynich'
    elif len(sopra) >= 3:
        esito = 'la finestra di tre parole non è propria del Voynich'
    else:
        esito = 'incerto'
    auto = [ris[k]['R0_IC95'][0] for k in vv[2:]]
    out = OrderedDict([('testi', ris), ('soglia', soglia), ('lingue_sopra', sopra), ('esito', esito),
                       ('classi_automatiche_estremo_basso', auto)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c34_finestra_tre_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c34 — La "finestra di tre parole": replica su tutte le righe, classi automatiche, terza trascrizione e lingue', '',
          'Preregistrazione: `preregistrazioni/e3c34.md`. Righe di almeno 6 parole senza bordi; atteso: stessa parola + pagina + deriva; R0 = K(3)/K(1).', '',
          '| testo | parole | K(1) (IC 95%) | K(2) | K(3) | R0 (IC 95%) | conta |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f | %+.3f | %.2f (%.2f – %.2f) | %s |' % (k, x['parole'], x['K'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K'][1], x['K'][2],
                                                                                         x['R0'], x['R0_IC95'][0], x['R0_IC95'][1], {True: 'sì', False: 'no'}.get(x.get('conta'), 'Voynich')))
    md += ['', 'Soglia (estremo basso di R0 più piccolo fra ZL e IT con le classi a mano): %.2f. Lingue sopra: %s.' % (soglia, ', '.join(sopra) or 'nessuna'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c34_finestra_tre_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
