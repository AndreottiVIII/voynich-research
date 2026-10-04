# -*- coding: utf-8 -*-
"""Esperimento e3a80: e3a78 (che cosa spiega da sola una catena di segni per riga) con la trascrizione IT.

Preregistrazione: preregistrazioni/e3a80.md. Scrive risultati/e3a80_catena_takahashi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEI = ('giuntura', 'chiusura della riga', '-m a fine riga', 'y/s/d a inizio riga', 'catena dentro/fra le parole', 'frequenza-forma')
DUE = ('ripresa dalla riga sopra', 'margine sinistro')


def pagine_it():
    per = OrderedDict()
    cur = None
    for r in trascrizione.testo_corrente(trascrizione.leggi('IT')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        pars = per.setdefault(r.pagina, [])
        if r.inizio_par or not pars:
            pars.append([])
        if ws:
            pars[-1].append(ws)
    return [[par for par in pars if par] for pars in per.values() if any(pars)]


def main():
    rnd = random.Random(3180)
    pagine = pagine_it()
    vero = e3a78.proprieta(pagine, rnd)
    print('vero', json.dumps(vero, ensure_ascii=False), flush=True)
    tab = e3a71.catena([r for pars in pagine for par in pars for r in par], e3a78.ORDINE)
    risc = []
    for v in range(e3a78.RISCRITTURE):
        risc.append(e3a78.proprieta(e3a78.riscrivi(pagine, tab, rnd), rnd))
        print('riscritto', v, json.dumps(risc[-1], ensure_ascii=False), flush=True)
    sintesi = OrderedDict()
    cambiano = []
    for n in e3a78.NOMI:
        rv = statistics.mean(x[n] for x in risc)
        R = rv / vero[n] if vero[n] else None
        es = 'n.d.' if R is None else ('la catena la riproduce' if R >= 0.75 else ('in parte' if R >= 0.25 else 'la catena non la riproduce: serve un meccanismo in più'))
        sintesi[n] = OrderedDict([('vero', vero[n]), ('riscritto_media', rv), ('R', R), ('esito', es)])
        if (n in SEI and (R is None or R < 0.75)) or (n in DUE and (R is None or R >= 0.25)):
            cambiano.append(n)
    esito = 'la sintesi regge' if not cambiano else 'cambiano: ' + ', '.join(cambiano)
    out = OrderedDict([('sintesi', sintesi), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a80_catena_takahashi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a80 — La sintesi dell\'e3a78 regge con la trascrizione di Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3a80.md`.', '',
          '| proprietà | IT vera | riscritta (media) | R | esito |', '|---|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %s | %s |' % (n, x['vero'], x['riscritto_media'], '%.2f' % x['R'] if x['R'] is not None else 'n.d.', x['esito']) for n, x in sintesi.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a80_catena_takahashi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
