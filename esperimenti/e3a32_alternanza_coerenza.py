# -*- coding: utf-8 -*-
"""Esperimento e3a32: alternanza delle classi di Sukhotin al confine fra parole con la trascrizione IT, all'a capo e al
salto del disegno (ZL).

Preregistrazione: preregistrazioni/e3a32.md. Scrive risultati/e3a32_alternanza_coerenza.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386
import e395_takahashi as e395
import e3a30_sukhotin as e3a30

RISULTATI = os.path.join(QUI, '..', 'risultati')


def prova(gruppi, vocali, rnd):
    """gruppi: liste di coppie (ultimo, primo) dentro cui si rimescolano i primi."""
    def q(gg):
        alt = tot = 0
        for g in gg:
            for a, b in g:
                tot += 1
                alt += (a in vocali) != (b in vocali)
        return alt / tot
    vero = q(gruppi)
    nul = []
    for _ in range(1000):
        gg = []
        for g in gruppi:
            dx = [b for _, b in g]
            rnd.shuffle(dx)
            gg.append([(a, b) for (a, _), b in zip(g, dx)])
        nul.append(q(gg))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('coppie', sum(len(g) for g in gruppi)), ('A', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(3132)
    # 1: IT
    rr_it = e395.righe('IT')
    v_it = e3a30.sukhotin([[w for w in ws if w] for _, _, _, ws, _ in rr_it])
    righe_it = defaultdict(list)
    for st, pag, npar, ws, seps in rr_it:
        righe_it[pag] += [(a[-1], b[0]) for a, b, s in zip(ws, ws[1:], seps) if a and b and s == '.']
    ris = OrderedDict()
    # nella riga il nullo dell'e3a30 rimescola le parole nella riga; qui per uniformita' si rimescola nella pagina
    ris['1 IT, nella riga'] = prova(list(righe_it.values()), v_it, rnd)
    # 2 e 3: ZL
    rr = e386.righe()
    v = e3a30.sukhotin([[w for w in ws if w] for _, _, _, ws, _ in rr])
    capo, salto = defaultdict(list), defaultdict(list)
    for k, (st, pag, npar, ws, seps) in enumerate(rr):
        for a, b, s in zip(ws, ws[1:], seps):
            if a and b and s == '|':
                salto[st.split('-')[0]].append((a[-1], b[0]))
        if k + 1 < len(rr) and rr[k + 1][1] == pag and rr[k + 1][2] == npar and ws[-1] and rr[k + 1][3][0]:
            capo[pag].append((ws[-1][-1], rr[k + 1][3][0][0]))
    ris['2 ZL, a capo'] = prova(list(capo.values()), v, rnd)
    ris['3 ZL, al salto del disegno'] = prova(list(salto.values()), v, rnd)
    for k, x in ris.items():
        print(k, json.dumps(x), flush=True)
    prove = OrderedDict([('1', ris['1 IT, nella riga']['A'] > 1 and ris['1 IT, nella riga']['z'] > 3),
                         ('2', abs(ris['2 ZL, a capo']['z']) < 2), ('3', abs(ris['3 ZL, al salto del disegno']['z']) < 2)])
    esito = 'l\'alternanza si comporta come la giuntura' if all(prove.values()) else 'manca: ' + ', '.join(k for k, v_ in prove.items() if not v_)
    out = OrderedDict([('vocali_IT', sorted(v_it)), ('vocali_ZL', sorted(v)), ('prove', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a32_alternanza_coerenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a32 — L\'alternanza "vocale/consonante" al confine si comporta come la giuntura?', '', 'Preregistrazione: `preregistrazioni/e3a32.md`. "Vocali" IT: %s; ZL: %s.' % (', '.join(sorted(v_it)), ', '.join(sorted(v))), '',
          '| prova | coppie | A | z |', '|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.1f |' % (k, x['coppie'], x['A'], x['z']) for k, x in ris.items()]
    md += ['', 'Nota: nella prova 1 il nullo rimescola le parole di destra dentro la pagina (non dentro la riga come nell\'e3a30).', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a32_alternanza_coerenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
