# -*- coding: utf-8 -*-
"""Esperimento e3a23: giuntura nella prima coppia, nell'ultima e in mezzo alla riga, a parita' di numero di coppie.

Preregistrazione: preregistrazioni/e3a23.md. Scrive risultati/e3a23_giuntura_posizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3123)
    prima, ultima, mezzo = [], [], []
    for st, pag, npar, ws, seps in e386.righe():
        n = len(ws)
        if n < 4:
            continue
        sez = st.split('-')[0]
        for j in range(n - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            x = (sez, a[-1], b[0])
            if j == 0:
                prima.append(x)
            elif j == n - 2:
                ultima.append(x)
            else:
                mezzo.append(x)
    ris = OrderedDict()
    for nome, cc in (('prima coppia', prima), ('ultima coppia', ultima)):
        x = e386.prova(cc, rnd, 1000)
        pari = statistics.median(e386.prova(rnd.sample(mezzo, len(cc)), rnd, 200)['E'] for _ in range(20))
        Q = x['E'] / pari if pari > 0 else None
        es = 'giuntura piena anche al bordo' if Q is not None and Q > 0.8 else ('giuntura più debole al bordo: forme decise dalla posizione' if Q is None or Q < 0.5 else 'un po\' più debole')
        ris[nome] = OrderedDict([('coppie', len(cc)), ('E', x['E']), ('z', x['z']), ('E_mezzo_a_parita', pari), ('Q', Q), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    out = OrderedDict([('coppie_in_mezzo', len(mezzo)), ('bordi', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a23_giuntura_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a23 — La giuntura ha la stessa forza lungo tutta la riga?', '', 'Preregistrazione: `preregistrazioni/e3a23.md`. Righe di almeno 4 parole; coppie in mezzo: %d.' % len(mezzo), '',
          '| coppia | quante | E | z | E in mezzo a parità | Q | esito |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.4f | %.1f | %.4f | %.2f | %s |' % (k, x['coppie'], x['E'], x['z'], x['E_mezzo_a_parita'], x['Q'], x['esito']))
    open(os.path.join(RISULTATI, 'e3a23_giuntura_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
