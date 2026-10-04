# -*- coding: utf-8 -*-
"""Esperimento 417: sopra la v19 (larghezza delle righe da una curva, e416b) si regola di nuovo il peso `distanza2` della
disposizione, per riportare l'alternanza nella riga (A dell'e110) che il termine di larghezza abbassa. Regolazione su
manoscritti senza messaggio; scelta su A e sulla somiglianza a distanza 2 del Voynich, non sui giudici. Scrive i parametri
della v20 e misura larghezze, sacchi e rilettura sulle 12 chiavi dell'e409 (i giudici poi con l'e409, VERSIONE=v20).

    PROCESSI=8 python esegui.py e417
    python esperimenti/e417_alternanza_larghezza.py --prova     (una chiave di regolazione, due valori, nessun giudice)

Preregistrazione: preregistrazioni/e417.md. Scrive risultati/e417_alternanza_larghezza.json e .md e
voynichizzatore/pezzi_parametri_v20.json.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e416_larghezza_righe as e416
import e416b_larghezza_curva as e416b

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRIGLIA = (None, 0.2, 0.3, 0.45, 0.65, 0.9)          # None: il valore della v19
TOLLERANZA = 0.05
NOME = 'e417_alternanza_larghezza'


def parametri(d2, versione='v19'):
    import pezzi
    x = json.load(open(pezzi.PARAMETRI % versione, encoding='utf-8'), object_pairs_hook=OrderedDict)
    if d2 is not None:
        x['pesi_disposizione'] = OrderedDict(x['pesi_disposizione'], distanza2=d2)
        x['origine'] = 'v19 con il peso della somiglianza a distanza 2 regolato di nuovo sull\'alternanza nella riga (e417)'
    return x


def di_riga(rr):
    import e410_cancello_riga as e410
    v = e410.di_riga(rr, 'G1')
    return OrderedDict([('A', v['A']), ('somiglianza a distanza 2', v['somiglianza a distanza 2']), ('S1', v['S1'])])


def lavoro(args):
    tipo, chiave, d2 = args
    import canale_sacco, pezzi
    if tipo == 'V':
        return args, di_riga(pezzi.voynich()[0])
    if tipo == 'reg':
        t, _ = canale_sacco.codifica(None, chiave, 'v19', parametri=parametri(d2))
        return args, di_riga(t)
    testo = open(e416.TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    a, _ = canale_sacco.codifica(testo, chiave, 'v17', verifica=False)
    b, _ = canale_sacco.codifica(testo, chiave, 'v19', parametri=parametri(d2), verifica=False)
    curva = tuple(tuple(c) for c in parametri(d2)['pesi_disposizione']['larghezza_curva'])
    r = OrderedDict([('larghezze', e416b.larghezze(b, curva)), ('sacchi identici', e416.sacchi(a) == e416.sacchi(b)),
                     ('rilettura esatta', canale_sacco.decodifica(b, chiave, 'v19', parametri(d2)) == testo)])
    r.update(di_riga(b))
    return args, r


def scegli(reg, voy):
    """Fra i valori con la somiglianza a distanza 2 entro il 5% sopra il Voynich, quello con A piu' vicina al Voynich."""
    ammessi = [d for d in reg if reg[d]['somiglianza a distanza 2'] <= voy['somiglianza a distanza 2'] * (1 + TOLLERANZA)]
    return min(ammessi, key=lambda d: abs(reg[d]['A'] - voy['A'])) if ammessi else None


def main(prova=False):
    d19 = parametri(None)['pesi_disposizione']['distanza2']
    griglia = [d19 if d is None else d for d in (GRIGLIA[:2] if prova else GRIGLIA)]
    chiavi_reg = e416.REGOLAZIONE[:1] if prova else e416.REGOLAZIONE
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        ris = dict(pool.imap_unordered(lavoro, [('V', '', None)] + [('reg', c, d) for d in griglia for c in chiavi_reg]))
        voy = ris[('V', '', None)]
        print('Voynich: A %.4f | somiglianza a distanza 2 %.4f' % (voy['A'], voy['somiglianza a distanza 2']), flush=True)
        reg = OrderedDict()
        for d in griglia:
            rs = [ris[('reg', c, d)] for c in chiavi_reg]
            reg[d] = OrderedDict((k, sum(r[k] for r in rs) / len(rs)) for k in rs[0])
            print('distanza2 %.3f: A %.4f | somiglianza a distanza 2 %.4f | S1 %.3f' % (d, reg[d]['A'], reg[d]['somiglianza a distanza 2'], reg[d]['S1']), flush=True)
        scelto = scegli(reg, voy)
        print('scelto: %s' % scelto, flush=True)
        if prova:
            return
        mis = []
        if scelto is not None and scelto != d19:
            m = dict(pool.imap_unordered(lavoro, [('mis', 'e409-%d' % i, scelto) for i in e416.CHIAVI]))
            mis = [m[('mis', 'e409-%d' % i, scelto)] for i in e416.CHIAVI]
    import pezzi
    sintesi = OrderedDict()
    if mis:
        with open(pezzi.PARAMETRI % 'v20', 'w', encoding='utf-8', newline='\n') as f:
            json.dump(parametri(scelto), f, ensure_ascii=False, indent=1)
        n = len(mis)
        sintesi = OrderedDict([('A', sum(m['A'] for m in mis) / n), ('A almeno 1', sum(m['A'] >= 1.0 for m in mis)),
                               ('somiglianza a distanza 2', sum(m['somiglianza a distanza 2'] for m in mis) / n),
                               ('caratteri oltre 1,25', sum(m['larghezze']['caratteri oltre 1,25'] for m in mis) / n),
                               ('caratteri oltre 1,5', sum(m['larghezze']['caratteri oltre 1,5'] for m in mis) / n),
                               ('sacchi identici', sum(bool(m['sacchi identici']) for m in mis)),
                               ('rilettura esatta', sum(bool(m['rilettura esatta']) for m in mis))])
        print(dict(sintesi), flush=True)
    json.dump(OrderedDict([('Voynich', voy), ('regolazione', OrderedDict((str(d), r) for d, r in reg.items())), ('scelto', scelto),
                           ('sintesi', sintesi), ('per chiave', mis)]),
              open(os.path.join(RISULTATI, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    nu = lambda v, d=4: ('%.*f' % (d, v)).replace('.', ',')
    pc = lambda v: ('%.1f%%' % (100 * v)).replace('.', ',')
    md = ['# e417 — Riportare l\'alternanza nella riga (A) dopo il termine di larghezza', '',
          'Preregistrazione: `preregistrazioni/e417.md`. A = somiglianza a distanza 2 nella riga divisa per quella fra parole vicine (e110).', '',
          '## Regolazione (manoscritti senza messaggio, chiavi %s)' % ' e '.join(e416.REGOLAZIONE), '',
          '| distanza2 | A | somiglianza a distanza 2 | S1 |', '|---|---|---|---|',
          '| Voynich | %s | %s | %s |' % (nu(voy['A']), nu(voy['somiglianza a distanza 2']), nu(voy['S1'], 3))]
    for d, r in reg.items():
        md.append('| %s%s%s | %s | %s | %s |' % (nu(d, 3), ' (v19)' if d == d19 else '', ' **(scelto)**' if d == scelto else '', nu(r['A']),
                                              nu(r['somiglianza a distanza 2']), nu(r['S1'], 3)))
    md += ['', 'Regola: fra i valori con la somiglianza a distanza 2 non oltre il 5%% sopra il Voynich (%s), quello con A più vicina al Voynich.'
           % nu(voy['somiglianza a distanza 2'] * (1 + TOLLERANZA)), '']
    if mis:
        md += ['## Misura: Isidoro nascosto, 12 chiavi (v20)', '',
               '- A media %s; chiavi con A almeno 1,0: %d su %d; somiglianza a distanza 2: %s.' % (nu(sintesi['A']), sintesi['A almeno 1'], len(mis), nu(sintesi['somiglianza a distanza 2'])),
               '- Righe oltre 1,25 volte la mediana: %s; oltre 1,5: %s.' % (pc(sintesi['caratteri oltre 1,25']), pc(sintesi['caratteri oltre 1,5'])),
               '- Sacchi di pagina identici alla v17: %d su %d; rilettura esatta: %d su %d.' % (sintesi['sacchi identici'], len(mis), sintesi['rilettura esatta'], len(mis)),
               '- Giudici, pagella e cancello: e409 con `VERSIONE=v20`.', '']
    else:
        md += ['Nessun valore diverso da quello della v19 passa la regola: la v20 non si fa.', '']
    open(os.path.join(RISULTATI, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))


if __name__ == '__main__':
    main(prova='--prova' in sys.argv)
