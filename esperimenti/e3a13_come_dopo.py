# -*- coding: utf-8 -*-
"""Esperimento e3a13: le iniziali a inizio riga, dopo un disegno e nelle etichette somigliano a quelle che seguono quale
finale della parola prima?

Preregistrazione: preregistrazioni/e3a13.md. Scrive risultati/e3a13_come_dopo.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e374_bordi_gibberish as e374
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def main():
    rnd = random.Random(3113)
    rr = e386.righe()
    dopo = defaultdict(Counter)
    generale = Counter()
    casi = OrderedDict([('inizio riga', []), ('dopo un disegno', []), ('etichetta', [])])
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        nuovo_par = k == 0 or rr[k - 1][1] != pag or rr[k - 1][2] != npar
        if ws[0] and not nuovo_par:
            casi['inizio riga'].append(ws[0][0])
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b:
                continue
            if seps[j] == '.':
                dopo[a[-1]][b[0]] += 1
                generale[b[0]] += 1
            elif seps[j] == '|':
                casi['dopo un disegno'].append(b[0])
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] == trascrizione.ETICHETTA:
            ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            ws = [w for w in ws if w]
            if ws:
                casi['etichetta'].append(ws[0][0])
    finali = [f for f, c in dopo.items() if sum(c.values()) >= 300]
    ris = OrderedDict()
    for nome, xs in casi.items():
        c = Counter(xs)
        div = {f: e374.jsd(c, dopo[f]) for f in finali}
        dg = e374.jsd(c, generale)
        fmin = min(div, key=div.get)
        boot = []
        for _ in range(1000):
            cb = Counter(xs[rnd.randrange(len(xs))] for _ in xs)
            dv = {f: e374.jsd(cb, dopo[f]) for f in finali}
            boot.append(min(dv.values()) / e374.jsd(cb, generale) if e374.jsd(cb, generale) > 0 else float('inf'))
        boot.sort()
        ic = [boot[25], boot[974]]
        esito = 'come dopo -%s' % fmin if ic[1] < 0.5 else 'né come una finale né come il generale'
        ris[nome] = OrderedDict([('parole', len(xs)), ('JSD_dal_generale', dg), ('finale_piu_vicina', fmin), ('JSD_minima', div[fmin]),
                                 ('rapporto', div[fmin] / dg if dg > 0 else None), ('IC95_rapporto', ic),
                                 ('JSD_per_finale', OrderedDict(sorted(div.items(), key=lambda kv: kv[1]))), ('iniziali_piu_frequenti', c.most_common(6)), ('esito', esito)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False, default=float)[:600], flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a13_come_dopo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a13 — Inizio riga, dopo un disegno, etichetta: come se venissero dopo quale finale?', '', 'Preregistrazione: `preregistrazioni/e3a13.md`. Finali considerate: %s.' % ', '.join(sorted(finali)), '',
          '| caso | parole | JSD dal generale | finale più vicina | JSD minima | rapporto (IC 95%) | tre finali più vicine | iniziali più frequenti | esito |', '|---|---|---|---|---|---|---|---|---|']
    for nome, x in ris.items():
        tre = ', '.join('-%s %.3f' % kv for kv in list(x['JSD_per_finale'].items())[:3])
        ini = ', '.join('%s %d' % kv for kv in x['iniziali_piu_frequenti'])
        md.append('| %s | %d | %.3f | -%s | %.3f | %.2f (%.2f – %.2f) | %s | %s | %s |' % (nome, x['parole'], x['JSD_dal_generale'], x['finale_piu_vicina'], x['JSD_minima'], x['rapporto'], x['IC95_rapporto'][0], x['IC95_rapporto'][1], tre, ini, x['esito']))
    open(os.path.join(RISULTATI, 'e3a13_come_dopo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
