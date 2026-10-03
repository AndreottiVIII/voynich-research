# -*- coding: utf-8 -*-
"""Esperimento e3a27: e3a26 (qo- a inizio riga evita il qo- della riga subito sopra) con la trascrizione IT e, nella ZL,
separatamente in lingua A e B.

Preregistrazione: preregistrazioni/e3a27.md. Scrive risultati/e3a27_margine_robustezza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e380_sandhi as e380
import e3a26_margine_sinistro as e3a26

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def paragrafi(quale, lingua=None):
    out, cur, pag = [], None, None
    for r in trascrizione.testo_corrente(trascrizione.leggi(quale)):
        if lingua and r.lingua != lingua:
            continue
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if r.inizio_par or cur is None or r.pagina != pag:
            cur = []
            out.append(cur)
        cur.append(ws)
        pag = r.pagina
    return out


def eventi(pars):
    ev = []
    for k, rr in enumerate(pars):
        for i in range(2, len(rr)):
            if not rr[i] or not rr[i - 1]:
                continue
            q = e380.ini_qo(rr[i][0])
            if q:
                ev.append((k, rr[i - 1][0][:2] == ('q', 'o'), q[1] == 'qo'))
    return ev


def main():
    rnd = random.Random(3127)
    ris = OrderedDict()
    for nome, pars in (('IT (Takahashi)', paragrafi('IT')), ('ZL, lingua A', paragrafi('ZL', 'A')), ('ZL, lingua B', paragrafi('ZL', 'B'))):
        ev = eventi(pars)
        x = e3a26.prova(ev, rnd)
        if x['eventi'][0] < 20:
            es = 'pochi dati'
        elif x['delta'] < 0 and x['z'] < -3:
            es = 'regge'
        elif x['z'] > -2:
            es = 'non regge'
        else:
            es = 'incerto'
        x['esito'] = es
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a27_margine_robustezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a27 — Il qo- evitato sul margine sinistro regge con Takahashi e in lingua A e B?', '', 'Preregistrazione: `preregistrazioni/e3a27.md`. Righe dalla seconda del paragrafo in poi; condizione: la riga subito sopra comincia con qo-.', '',
          '| prova | eventi (sì / no) | Δ P(qo) | z | esito |', '|---|---|---|---|---|']
    md += ['| %s | %d / %d | %+.3f | %.1f | %s |' % (k, x['eventi'][0], x['eventi'][1], x['delta'], x['z'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a27_margine_robustezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
