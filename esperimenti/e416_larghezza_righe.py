# -*- coding: utf-8 -*-
"""Esperimento 416: la larghezza delle righe in caratteri. La v17 fissa le parole per riga ma non lo spazio: ha piu' righe
"troppo lunghe" del Voynich. Si aggiunge alla disposizione un termine che avvicina la larghezza di ogni riga (caratteri EVA
piu' uno spazio per parola) a quella attesa, proporzionale a n ** beta (n parole; beta misurato sul Voynich). Il peso si
regola sulla deviazione dei residui, non sui giudici. Scrive i parametri della v18 e misura le larghezze di v17 e v18
sulle 12 chiavi dell'e409 (i giudici si misurano poi con l'e409, VERSIONE=v18).

    PROCESSI=10 python esegui.py e416
    python esperimenti/e416_larghezza_righe.py --prova     (una chiave di regolazione, due pesi, nessun giudice)

Preregistrazione: preregistrazioni/e416.md. Scrive risultati/e416_larghezza_righe.json e .md e
voynichizzatore/pezzi_parametri_v18.json.
"""
import json, math, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
PESI = (0.0, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5)
REGOLAZIONE = ('e416-reg-1', 'e416-reg-2')
CHIAVI = tuple(range(1, 13))
NOME, VERS, TITOLO, PREREG = 'e416_larghezza_righe', 'v18', 'e416 — La larghezza delle righe in caratteri', 'preregistrazioni/e416.md'


def pagine_di(rr):
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, []).append(ps)
    return [r for r in per.values() if len(r) >= 5]


def punti(rr):
    """Per ogni riga delle pagine con almeno 5 righe: (log parole su mediana di pagina, log caratteri su mediana di pagina)."""
    out = []
    for righe in pagine_di(rr):
        n = [len(ps) for ps in righe]
        L = [sum(len(w) + 1 for w in ps) for ps in righe]
        mn, mL = statistics.median(n), statistics.median(L)
        out.extend((math.log(a / mn), math.log(b / mL)) for a, b in zip(n, L))
    return out


def pendenza(rr):
    pt = punti(rr)
    mx, my = sum(x for x, _ in pt) / len(pt), sum(y for _, y in pt) / len(pt)
    return sum((x - mx) * (y - my) for x, y in pt) / sum((x - mx) ** 2 for x, _ in pt)


def larghezze(rr, beta):
    """Le statistiche di larghezza: quote di righe oltre 1,25 e 1,5 volte la mediana della pagina (in caratteri e in
    parole) e deviazione standard dei residui log caratteri - beta * log parole."""
    pt = punti(rr)
    res = [y - beta * x for x, y in pt]
    m = sum(res) / len(res)
    return OrderedDict([('righe', len(pt)),
                        ('caratteri oltre 1,25', sum(y > math.log(1.25) for _, y in pt) / len(pt)),
                        ('caratteri oltre 1,5', sum(y > math.log(1.5) for _, y in pt) / len(pt)),
                        ('parole oltre 1,5', sum(x > math.log(1.5) for x, _ in pt) / len(pt)),
                        ('residui', math.sqrt(sum((r - m) ** 2 for r in res) / len(res))),
                        ('pendenza propria', pendenza(rr))])


def modello(voy):
    """Il modello della larghezza attesa misurato sul Voynich (qui: la pendenza beta; nell'e416b una curva)."""
    return pendenza(voy)


def descrivi(beta):
    return 'beta %.3f' % beta


def parametri(w, beta):
    import pezzi
    x = json.load(open(pezzi.PARAMETRI % 'v17', encoding='utf-8'), object_pairs_hook=OrderedDict)
    if w:
        x['pesi_disposizione'] = OrderedDict(x['pesi_disposizione'], larghezza=w, larghezza_beta=beta)
        x['origine'] = 'v17 con la larghezza delle righe in caratteri nella disposizione (e416)'
    return x


def sacchi(rr):
    per = OrderedDict()
    for p, _, ps in rr:
        per.setdefault(p, Counter()).update(ps)
    return per


def lavoro(args):
    tipo, chiave, w, beta = args
    import canale_sacco
    if tipo == 'reg':
        t, _ = canale_sacco.codifica(None, chiave, 'v17', parametri=parametri(w, beta))
        return args, larghezze(t, beta)
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n')
    a, _ = canale_sacco.codifica(testo, chiave, 'v17', parametri=parametri(0.0, beta), verifica=False)
    b, _ = canale_sacco.codifica(testo, chiave, 'v17', parametri=parametri(w, beta), verifica=False)
    return args, OrderedDict([('v17', larghezze(a, beta)), ('v18', larghezze(b, beta)), ('sacchi identici', sacchi(a) == sacchi(b)),
                              ('gabbia identica', [(p, i, len(ps)) for p, i, ps in a] == [(p, i, len(ps)) for p, i, ps in b]),
                              ('rilettura esatta', canale_sacco.decodifica(b, chiave, 'v17', parametri(w, beta)) == testo)])


def media(rs, k):
    return sum(r[k] for r in rs) / len(rs)


def scegli(reg, bersaglio):
    """Il peso con la deviazione dei residui (media sulle chiavi di regolazione) piu' vicina al Voynich; a parita', il minore."""
    return min(sorted(reg), key=lambda w: (round(abs(reg[w]['residui'] - bersaglio), 4), w))


def main(prova=False):
    import pezzi
    voy, _ = pezzi.voynich()
    beta = modello(voy)
    vero = larghezze(voy, beta)
    print('Voynich: %s | oltre 1,25 %.3f | oltre 1,5 %.3f | parole oltre 1,5 %.3f | residui %.4f' % (
        descrivi(beta), vero['caratteri oltre 1,25'], vero['caratteri oltre 1,5'], vero['parole oltre 1,5'], vero['residui']), flush=True)
    pesi, chiavi_reg = ((0.0, 0.1), REGOLAZIONE[:1]) if prova else (PESI, REGOLAZIONE)
    proc = max(1, int(os.environ.get('PROCESSI', '1')))
    with Pool(proc) as pool:
        lavori = [('reg', c, w, beta) for w in pesi for c in chiavi_reg]
        ris = dict(pool.imap_unordered(lavoro, lavori))
        reg = OrderedDict()
        for w in pesi:
            rs = [ris[('reg', c, w, beta)] for c in chiavi_reg]
            reg[w] = OrderedDict((k, media(rs, k)) for k in rs[0])
            print('w %-5s oltre 1,25 %.3f | oltre 1,5 %.3f | residui %.4f | pendenza propria %.3f' % (
                w, reg[w]['caratteri oltre 1,25'], reg[w]['caratteri oltre 1,5'], reg[w]['residui'], reg[w]['pendenza propria']), flush=True)
        scelto = scegli(reg, vero['residui'])
        print('peso scelto: %s' % scelto, flush=True)
        if prova:
            return
        mis = dict(pool.imap_unordered(lavoro, [('mis', 'e409-%d' % i, scelto, beta) for i in CHIAVI]))
    mis = [mis[('mis', 'e409-%d' % i, scelto, beta)] for i in CHIAVI]
    sintesi = OrderedDict((v, OrderedDict((k, media([m[v] for m in mis], k)) for k in mis[0][v])) for v in ('v17', 'v18'))
    conti = OrderedDict((k, sum(bool(m[k]) for m in mis)) for k in ('sacchi identici', 'gabbia identica', 'rilettura esatta'))
    for v in sintesi:
        print('%s: oltre 1,25 %.3f | oltre 1,5 %.3f | residui %.4f' % (v, sintesi[v]['caratteri oltre 1,25'], sintesi[v]['caratteri oltre 1,5'], sintesi[v]['residui']), flush=True)
    print(dict(conti), flush=True)
    x = parametri(scelto, beta)
    if scelto:
        with open(pezzi.PARAMETRI % VERS, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(x, f, ensure_ascii=False, indent=1)
    json.dump(OrderedDict([('beta', beta), ('Voynich', vero), ('regolazione', OrderedDict((str(w), r) for w, r in reg.items())), ('peso', scelto),
                           ('sintesi', sintesi), ('conti', conti), ('per chiave', mis)]),
              open(os.path.join(RISULTATI, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    pc = lambda v: ('%.1f%%' % (100 * v)).replace('.', ',')
    nu = lambda v, d=3: ('%.*f' % (d, v)).replace('.', ',')
    md = ['# ' + TITOLO, '',
          'Preregistrazione: `' + PREREG + '`. Larghezza di una riga: caratteri EVA delle sue parole più uno spazio per parola. '
          'Pagine con almeno 5 righe.', '',
          '## Sul Voynich', '',
          '- Larghezza attesa (log larghezza su log parole, entrambe rispetto alla mediana della pagina): **%s**.' % descrivi(beta).replace('.', ','),
          '- Righe oltre 1,25 volte la mediana: %s; oltre 1,5: %s; deviazione dei residui: %s.' % (
              pc(vero['caratteri oltre 1,25']), pc(vero['caratteri oltre 1,5']), nu(vero['residui'], 4)), '',
          '## Regolazione del peso (manoscritti senza messaggio, chiavi %s)' % ' e '.join(REGOLAZIONE), '',
          '| peso | oltre 1,25 | oltre 1,5 | residui | pendenza propria |', '|---|---|---|---|---|']
    for w, r in reg.items():
        md.append('| %s%s | %s | %s | %s | %s |' % (str(w).replace('.', ','), ' **(scelto)**' if w == scelto else '', pc(r['caratteri oltre 1,25']),
                                                  pc(r['caratteri oltre 1,5']), nu(r['residui'], 4), nu(r['pendenza propria'])))
    md += ['', 'Scelto il peso con la deviazione dei residui più vicina a quella del Voynich (%s).' % nu(vero['residui'], 4), '',
           '## Misura: Isidoro nascosto, 12 chiavi (e409-1 … e409-12)', '',
           '| | oltre 1,25 | oltre 1,5 | parole oltre 1,5 | residui |', '|---|---|---|---|---|']
    for nome, r in (('Voynich', vero), ('v17', sintesi['v17']), (VERS, sintesi['v18'])):
        md.append('| %s | %s | %s | %s | %s |' % (nome, pc(r['caratteri oltre 1,25']), pc(r['caratteri oltre 1,5']), pc(r['parole oltre 1,5']), nu(r['residui'], 4)))
    md += ['', '- Sacchi di pagina identici fra v17 e la versione nuova: %d su %d; gabbia identica: %d su %d; rilettura esatta: %d su %d.' % (
        conti['sacchi identici'], len(mis), conti['gabbia identica'], len(mis), conti['rilettura esatta'], len(mis)),
           '- I giudici, la pagella e il cancello si misurano con l\'e409 (`VERSIONE=%s`), stesse chiavi.' % VERS, '']
    open(os.path.join(RISULTATI, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))


if __name__ == '__main__':
    main(prova='--prova' in sys.argv)
