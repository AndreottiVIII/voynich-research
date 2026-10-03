# -*- coding: utf-8 -*-
"""Esperimento e3a28: parole nella stessa colonna di due righe consecutive (posizioni 1-4 da sinistra e ultima) hanno
gli stessi primi 2 segni (o sono uguali) piu' o meno del caso? Nullo: ordine delle parole rimescolato dentro le righe.

Preregistrazione: preregistrazioni/e3a28.md. Scrive risultati/e3a28_colonne.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
COLONNE = [0, 1, 2, 3, -1]


def quote(coppie, chiave):
    out = []
    for c in COLONNE:
        s = sum(chiave(a[c]) == chiave(b[c]) for a, b in coppie)
        out.append(s / len(coppie))
    return out


def main():
    rnd = random.Random(3128)
    coppie = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            for i in range(2, len(rr)):
                if len(rr[i]) >= 5 and len(rr[i - 1]) >= 5:
                    coppie.append((rr[i], rr[i - 1]))
    ris = OrderedDict()
    for nome, chiave in (('stessi primi 2 segni', lambda w: w[:2]), ('parola uguale', lambda w: w)):
        vero = quote(coppie, chiave)
        nul = [quote([(rnd.sample(a, len(a)), rnd.sample(b, len(b))) for a, b in coppie], chiave) for _ in range(1000)]
        x = OrderedDict()
        for k, c in enumerate(COLONNE):
            xs = [n[k] for n in nul]
            m, sd = statistics.mean(xs), statistics.pstdev(xs)
            r = vero[k] / m if m else None
            z = (vero[k] - m) / sd if sd else 0.0
            es = 'evita la stessa colonna' if r is not None and r < 0.8 and z < -3 else ('ripete nella stessa colonna' if r is not None and r > 1.2 and z > 3 else 'indifferente')
            x['colonna %s' % ('ultima' if c == -1 else c + 1)] = OrderedDict([('osservata', vero[k]), ('nullo', m), ('rapporto', r), ('z', z), ('esito', es)])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    p2 = ris['stessi primi 2 segni']
    solo = p2['colonna 1']['esito'] == 'evita la stessa colonna' and all(p2['colonna %d' % c]['esito'] != 'evita la stessa colonna' for c in (2, 3, 4))
    out = OrderedDict([('coppie_di_righe', len(coppie)), ('misure', ris), ('solo_margine_sinistro', solo)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a28_colonne.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a28 — Lo scriba evita di ripetere lo stesso inizio nella stessa colonna?', '', 'Preregistrazione: `preregistrazioni/e3a28.md`. %d coppie di righe consecutive con almeno 5 parole.' % len(coppie), '']
    for nome, x in ris.items():
        md += ['## %s' % nome, '', '| colonna | osservata | nullo | rapporto | z | esito |', '|---|---|---|---|---|---|']
        md += ['| %s | %.3f | %.3f | %.2f | %.1f | %s |' % (k, v['osservata'], v['nullo'], v['rapporto'], v['z'], v['esito']) for k, v in x.items()]
        md.append('')
    md.append('Solo il margine sinistro: **%s**.' % ('sì' if solo else 'no'))
    open(os.path.join(RISULTATI, 'e3a28_colonne.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
