# -*- coding: utf-8 -*-
"""Esperimento 418: nella disposizione i conteggi delle scelte di grafia per riga non venivano mai riempiti (v12-v20: le
righe che li inizializzano erano finite dopo un return). F1: v20 con la correzione ('conti_iniziali'). F2: F1 con i pesi
`scelte` e `scelte_sopra` regolati di nuovo (regola dell'e410) su manoscritti senza messaggio. Scrive i parametri
v21f1 e v21f2 e misura larghezze, sacchi e rilettura sulle chiavi 1-12 (i giudici poi con l'e409).

    PROCESSI=8 python esegui.py e418
    python esperimenti/e418_conti_scelte.py --prova     (una chiave di regolazione, v20 e F1, nessun giudice)

Preregistrazione: preregistrazioni/e418.md. Scrive risultati/e418_conti_scelte.json e .md e
voynichizzatore/pezzi_parametri_v21f1.json, _v21f2.json.
"""
import json, math, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import e416_larghezza_righe as e416
import e416b_larghezza_curva as e416b

RISULTATI = os.path.join(QUI, '..', 'risultati')
GIRI, VICINO = 6, 0.05
NOME = 'e418_conti_scelte'
STAT = ('varianza per riga', 'r righe consecutive', 'A', 'somiglianza a distanza 2', 'S1')


def parametri(corretto, scelte=None, sopra=None):
    import pezzi
    x = json.load(open(pezzi.PARAMETRI % 'v20', encoding='utf-8'), object_pairs_hook=OrderedDict)
    if corretto:
        p = OrderedDict(x['pesi_disposizione'], conti_iniziali=True)
        if scelte is not None:
            p['scelte'], p['scelte_sopra'] = scelte, sopra
        x['pesi_disposizione'] = p
        x['origine'] = 'v20 con i conteggi delle scelte di riga inizializzati (e418)' + (', pesi regolati di nuovo' if scelte is not None else '')
    return x


def di_riga(rr):
    import e410_cancello_riga as e410
    v = e410.di_riga(rr, 'G2')
    return OrderedDict((k, v[k]) for k in STAT)


def lavoro(args):
    tipo, chiave, conf = args
    import canale_sacco, pezzi
    if tipo == 'V':
        return args, di_riga(pezzi.voynich()[0])
    x = parametri(*conf)
    if tipo == 'reg':
        t, _ = canale_sacco.codifica(None, chiave, 'v20', parametri=x)
        return args, di_riga(t)
    testo = open(e416.TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    a, _ = canale_sacco.codifica(testo, chiave, 'v20', verifica=False)
    b, _ = canale_sacco.codifica(testo, chiave, 'v20', parametri=x, verifica=False)
    curva = tuple(tuple(c) for c in x['pesi_disposizione']['larghezza_curva'])
    r = OrderedDict([('larghezze', e416b.larghezze(b, curva)), ('sacchi identici', e416.sacchi(a) == e416.sacchi(b)),
                     ('rilettura esatta', canale_sacco.decodifica(b, chiave, 'v20', x) == testo)])
    r.update(di_riga(b))
    return args, r


def scarto(val, voy):
    return max(abs(val['varianza per riga'] / voy['varianza per riga'] - 1), abs(val['r righe consecutive'] - voy['r righe consecutive']) / 0.7)


def main(prova=False):
    chiavi_reg = e416.REGOLAZIONE[:1] if prova else e416.REGOLAZIONE
    v20 = parametri(False)['pesi_disposizione']
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        def misura(conf):
            ris = dict(pool.imap_unordered(lavoro, [('reg', c, conf) for c in chiavi_reg]))
            rs = [ris[('reg', c, conf)] for c in chiavi_reg]
            return OrderedDict((k, sum(r[k] for r in rs) / len(rs)) for k in STAT)

        def mostra(nome, val):
            print('%-28s %s' % (nome, ' | '.join('%s %.4f' % (k, val[k]) for k in STAT)), flush=True)
        voy = lavoro(('V', '', None))[1]
        mostra('Voynich', voy)
        base = misura((False, None, None))
        mostra('v20 com\'e\'', base)
        f1 = misura((True, None, None))
        mostra('F1 (corretto, stessi pesi)', f1)
        if prova:
            return
        scelte, sopra = v20['scelte'], v20['scelte_sopra']
        traccia, val = [], f1
        for g in range(GIRI):
            traccia.append(OrderedDict([('giro', g), ('scelte', scelte), ('scelte_sopra', sopra), ('valori', val), ('scarto', scarto(val, voy))]))
            if traccia[-1]['scarto'] < 0.03 or g == GIRI - 1:
                break
            scelte = min(2.0, max(0.0, scelte * math.exp(0.8 * math.log(voy['varianza per riga'] / max(val['varianza per riga'], 0.2)))))
            sopra = min(2.0, max(0.0, sopra + 0.3 * (voy['r righe consecutive'] - val['r righe consecutive'])))
            val = misura((True, scelte, sopra))
            mostra('giro %d: scelte %.4f sopra %.4f' % (g + 1, scelte, sopra), val)
        migliore = min(traccia, key=lambda t: t['scarto'])
        converge = migliore['scarto'] <= VICINO
        print('migliore: giro %d, scarto %.3f, converge %s' % (migliore['giro'], migliore['scarto'], converge), flush=True)
        conf = OrderedDict([('F1', (True, None, None)), ('F2', (True, migliore['scelte'], migliore['scelte_sopra']))])
        if migliore['giro'] == 0:
            del conf['F2']              # la regolazione non cambia i pesi: F2 coincide con F1
        m = dict(pool.imap_unordered(lavoro, [('mis', 'e409-%d' % i, c) for c in conf.values() for i in e416.CHIAVI]))
    import pezzi
    sintesi = OrderedDict()
    for nome, c in conf.items():
        with open(pezzi.PARAMETRI % ('v21' + nome.lower()), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(parametri(*c), f, ensure_ascii=False, indent=1)
        mis = [m[('mis', 'e409-%d' % i, c)] for i in e416.CHIAVI]
        n = len(mis)
        sintesi[nome] = OrderedDict([(k, sum(x[k] for x in mis) / n) for k in STAT] + [
            ('caratteri oltre 1,25', sum(x['larghezze']['caratteri oltre 1,25'] for x in mis) / n),
            ('caratteri oltre 1,5', sum(x['larghezze']['caratteri oltre 1,5'] for x in mis) / n),
            ('A almeno 1', sum(x['A'] >= 1.0 for x in mis)), ('sacchi identici', sum(bool(x['sacchi identici']) for x in mis)),
            ('rilettura esatta', sum(bool(x['rilettura esatta']) for x in mis))])
        print(nome, dict(sintesi[nome]), flush=True)
    json.dump(OrderedDict([('Voynich', voy), ('v20', base), ('F1', f1), ('traccia', traccia), ('migliore', migliore), ('converge', converge), ('sintesi', sintesi)]),
              open(os.path.join(RISULTATI, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    nu = lambda v, d=4: ('%.*f' % (d, v)).replace('.', ',')
    pc = lambda v: ('%.1f%%' % (100 * v)).replace('.', ',')
    md = ['# e418 — I conteggi delle scelte di riga nella disposizione', '',
          'Preregistrazione: `preregistrazioni/e418.md`. Dalla v12 alla v20 i conteggi delle scelte di grafia per riga partivano da zero '
          '(righe di inizializzazione finite dopo un `return`). F1: v20 con la correzione. F2: F1 con `scelte` e `scelte_sopra` regolati di nuovo.', '',
          '## Statistiche di riga (manoscritti senza messaggio, chiavi %s)' % ' e '.join(e416.REGOLAZIONE), '',
          '| | scelte | scelte_sopra | ' + ' | '.join(STAT) + ' | scarto |', '|---|---|---|' + '---|' * (len(STAT) + 1),
          '| Voynich | | | ' + ' | '.join(nu(voy[k]) for k in STAT) + ' | |',
          '| v20 com\'è | %s | %s | ' % (nu(v20['scelte']), nu(v20['scelte_sopra'])) + ' | '.join(nu(base[k]) for k in STAT) + ' | %s |' % nu(scarto(base, voy), 3)]
    for t in traccia:
        md.append('| %s%s | %s | %s | ' % ('F1' if t['giro'] == 0 else 'giro %d' % t['giro'], ' **(scelto per F2)**' if t is migliore and t['giro'] else '',
                                          nu(t['scelte']), nu(t['scelte_sopra'])) + ' | '.join(nu(t['valori'][k]) for k in STAT) + ' | %s |' % nu(t['scarto'], 3))
    md += ['', 'Scarto: il maggiore fra lo scarto relativo della varianza per riga e quello di r fra righe consecutive diviso 0,7 (come nell\'e410). '
           'Regolazione entro il 5%%: **%s**.' % ('sì' if converge else 'no'), '',
           '## Misura: Isidoro nascosto, chiavi e409-1 … e409-12', '',
           '| | ' + ' | '.join(STAT) + ' | oltre 1,25 | oltre 1,5 | A ≥ 1 | sacchi identici alla v20 | rilettura |', '|---|' + '---|' * (len(STAT) + 5)]
    for nome, r in sintesi.items():
        md.append('| %s | ' % nome + ' | '.join(nu(r[k]) for k in STAT) + ' | %s | %s | %d su 12 | %d su 12 | %d su 12 |' % (
            pc(r['caratteri oltre 1,25']), pc(r['caratteri oltre 1,5']), r['A almeno 1'], r['sacchi identici'], r['rilettura esatta']))
    md += ['', 'Giudici, pagella e cancello: e409 con `VERSIONE=v21f1` e `v21f2`, chiavi 1–12 e 13–24.', '']
    open(os.path.join(RISULTATI, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))


if __name__ == '__main__':
    main(prova='--prova' in sys.argv)
