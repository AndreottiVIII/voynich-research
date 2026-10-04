# -*- coding: utf-8 -*-
"""Esperimento e3c31: la forma del calo alla pari (e3c28) dentro le righe di almeno 9 parole, così che le
coppie vicine e lontane vengano dalle stesse righe: R56 = [K(3) − K(5–6)] / [K(1) − K(5–6)]. Voynich IT e ZL e le lingue
dell'e3c28 (righe finte con le lunghezze del Voynich), righe senza bordi, atteso dalla stessa parola coperta.

Preregistrazione: preregistrazioni/e3c31.md. Scrive risultati/e3c31_forma_righe_medie.json e .md.
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
import e3c28_forma_alla_pari as e3c28

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE = 9


def gruppo(d):
    return 0 if d == 1 else (1 if d == 3 else (2 if d in (5, 6) else -1))


def lunghe(uu):
    return [[r for r in u if len(r) >= MIN_PAROLE] for u in uu]


def main():
    e3c28.gruppo = gruppo
    rng = np.random.default_rng(3331)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    ris = OrderedDict()
    for q, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        uu, ss = e3b62.voynich(pd, mano)
        ris[q] = e3c28.misura(e3c07.senza_bordi(lunghe(uu)), ss, e3b62.CV, rng)
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
        uu = e3c07.senza_bordi(lunghe([rr[i:i + 25] for i in range(0, len(rr), 25)]))
        x = e3c28.misura(uu, [nome] * len(uu), OrderedDict([('x', f)]), rng)
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
        esito = 'nelle righe di almeno 9 parole la forma piatta resta propria del Voynich'
    elif len(sopra) >= 3:
        esito = 'nelle righe di almeno 9 parole la forma piatta non è propria del Voynich'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('soglia', soglia), ('lingue_che_contano', len(lingue)), ('lingue_sopra', sopra), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c31_forma_righe_medie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def due(a):
        return '—' if a is None else '%.2f' % a
    md = ['# e3c31 — La forma del calo dentro le righe di almeno 9 parole', '', 'Preregistrazione: `preregistrazioni/e3c31.md`. Righe di almeno 9 parole, senza bordi; R56 = [K(3) − K(5–6)] / [K(1) − K(5–6)].', '',
          '| testo | accordo accanto (IC 95%) | R56 (IC 95%) | coppie a 5–6 | conta |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %+.3f (%s – %s) | %s (%s – %s) | %d | %s |' % (k, x['accanto'], due(x['accanto_IC95'][0]), due(x['accanto_IC95'][1]), due(x['R']), due(x['R_IC95'][0]), due(x['R_IC95'][1]),
                                                                    x['coppie_lontane'], {True: 'sì', False: 'no'}.get(x.get('conta'), 'Voynich')))
    md += ['', 'Soglia: %s. Lingue che contano: %d; sopra la soglia: %s.' % (due(soglia), len(lingue), ', '.join(sopra) or 'nessuna'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c31_forma_righe_medie.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
