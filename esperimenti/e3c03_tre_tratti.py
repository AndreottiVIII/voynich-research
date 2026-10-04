# -*- coding: utf-8 -*-
"""Esperimento e3c03: per i testi che nell'e3c01 (lingue) e nell'e3c02 (generatori) hanno memoria nelle alternanze
interne, gli altri due tratti con le stesse classi: forma del calo (R, e3b96/e3b98) e consumo con le lettere (e3b80);
profilo della distanza (e3b95) come descrizione. Voynich IT e ZL come riferimento.

Preregistrazione: preregistrazioni/e3c03.md. Scrive risultati/e3c03_tre_tratti.json e .md.
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
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b80_memoria_lettere as e3b80
import e3b95_profilo_distanza as e3b95
import e3b98_forma_lingue as e3b98
import e3c01_alternanze_interne as e3c01
import e3c02_alternanze_generatori as e3c02

RISULTATI = os.path.join(QUI, '..', 'risultati')


def lettere(uu, strati, classi, rng):
    cc = OrderedDict((k, e3b80.prepara(uu, strati, f)) for k, f in classi.items())
    ins = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], ins['nullo'], rng)
    return OrderedDict([('coppie_poche', ins['coppie_vicine']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def profilo(uu, classi):
    """Profilo dell'e3b95; vuoto se non ci sono coppie lontane (8-12) da cui misurare."""
    try:
        return OrderedDict((str(d), v) for d, v in e3b95.profilo(uu, classi)[0].items())
    except TypeError:
        return OrderedDict()


def main():
    rng = np.random.default_rng(3303)
    prima = json.load(open(os.path.join(RISULTATI, 'e3c01_alternanze_interne.json'), encoding='utf-8'))
    gen = json.load(open(os.path.join(RISULTATI, 'e3c02_alternanze_generatori.json'), encoding='utf-8'))
    for k in gen['generatori_simili']:
        prima['testi'][k] = gen['testi'][k]
    scelti = list(prima['lingue_simili']) + list(gen['generatori_simili'])
    testi = OrderedDict()
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    for nome, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        uu, ss = e3b62.voynich(pd, mano)
        testi[nome] = (uu, ss, [r for u in uu for r in u])
    tt = e381.testi()
    for nome in prima['lingue_simili']:
        righe = [r for r in tt[nome + '.txt'] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        testi[nome] = (uu, [nome] * len(uu), [b for u in uu for b in u])
    if gen['generatori_simili']:
        gg = e3c02.generatori()
        for nome in gen['generatori_simili']:
            righe = gg[nome]
            uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
            testi[nome] = (uu, [nome] * len(uu), righe)
    ris = OrderedDict()
    for nome, (uu, ss, seq) in testi.items():
        scelte, _ = e3c01.alternanze(seq)
        alt = ['%s/%s' % c for c in scelte]
        assert alt == prima['testi'][nome]['alternanze'], nome
        classi = OrderedDict((a, e3c01.classe(*c)) for a, c in zip(alt, scelte))
        forma = e3b98.analizza(uu, classi, rng)
        x = OrderedDict([('alternanze', alt), ('memoria', prima['testi'][nome]['effetto']), ('memoria_IC95', prima['testi'][nome]['IC95']),
                         ('R', forma['R']), ('R_IC95', forma['R_IC95']), ('accanto', forma['accanto']), ('accanto_IC95', forma['accanto_IC95']),
                         ('lettere', lettere(uu, ss, classi, rng)), ('profilo', profilo(uu, classi))])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    vi = ris['Voynich IT']['R_IC95']
    lv = [ris[v]['lettere'] for v in ('Voynich IT', 'Voynich ZL')]
    voy_lettere = all(l['IC95'] and l['IC95'][0] > 0 for l in lv)
    rif_lettere = min(l['effetto'] for l in lv)
    esiti = OrderedDict()
    for k in scelti:
        x = ris[k]
        ic = x['R_IC95']
        x['forma_come_voynich'] = bool(x['accanto_IC95'][0] > 0 and None not in ic and None not in vi and ic[0] <= vi[1] and vi[0] <= ic[1])
        l = x['lettere']
        x['consumo_come_voynich'] = bool(voy_lettere and l['IC95'] and l['IC95'][0] > 0 and l['effetto'] >= rif_lettere / 2)
        n = x['forma_come_voynich'] + x['consumo_come_voynich']
        esiti[k] = {2: 'ha tutti e tre i tratti', 1: 'ha uno solo degli altri due tratti', 0: 'non ha gli altri due tratti'}[n]
    if not scelti:
        esito = 'nessun testo da provare'
    else:
        esito = '; '.join('%s: %s' % (k, v) for k, v in esiti.items())
    if not voy_lettere:
        esito += ' (il consumo con le lettere non si vede nel Voynich con queste classi: tratto non misurabile qui)'
    out = OrderedDict([('testi', ris), ('voynich_consumo_lettere', voy_lettere), ('esiti', esiti), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c03_tre_tratti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    def due(v):
        return '—' if v is None else '%.2f' % v
    md = ['# e3c03 — I testi con memoria nelle alternanze interne hanno anche la forma piatta e il consumo con le lettere?', '',
          'Preregistrazione: `preregistrazioni/e3c03.md`. Confronto con il Voynich nella stessa prova, con le stesse regole.', '',
          '| testo | alternanze | memoria (e3c01) | accordo accanto (IC 95%) | R (IC 95%) | consumo con le lettere (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        l = x['lettere']
        lt = '—' if l['effetto'] is None or not l['IC95'] else '%+.4f (%+.4f – %+.4f)' % (l['effetto'], l['IC95'][0], l['IC95'][1])
        ac = '%+.3f (%+.3f – %+.3f)' % (x['accanto'], x['accanto_IC95'][0], x['accanto_IC95'][1])
        md.append('| %s | %s | %+.4f | %s | %s (%s – %s) | %s |' % (k, ' '.join(x['alternanze']), x['memoria'], ac, due(x['R']), due(x['R_IC95'][0]), due(x['R_IC95'][1]), lt))
    md += ['', 'Profilo K(d) − K(8–12), descrittivo:', '', '| testo | ' + ' | '.join('d=%s' % d for d in range(1, 8)) + ' |', '|---|' + '---|' * 7]
    for k, x in ris.items():
        md.append('| %s | ' % k + ' | '.join('—' if x['profilo'].get(str(d)) is None else '%+.3f' % x['profilo'][str(d)] for d in range(1, 8)) + ' |')
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c03_tre_tratti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
