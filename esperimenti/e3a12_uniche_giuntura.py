# -*- coding: utf-8 -*-
"""Esperimento e3a12: la giuntura nelle coppie con parole uniche (forme nuove, errori) confrontata con le coppie di
parole ripetute, a parita' di numero di coppie.

Preregistrazione: preregistrazioni/e3a12.md. Scrive risultati/e3a12_uniche_giuntura.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e350_sessioni as e350
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3112)
    rr = e386.righe()
    # parole come stringhe EVA ricostruite dai segni, per riusare l'indice dell'e350
    freq = Counter(''.join(w) for st, pag, npar, ws, seps in rr for w in ws if w)
    sim = e350.simili_globali(set(freq))
    cat = {}
    for w, n in freq.items():
        if n == 1:
            cat[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
        else:
            cat[w] = 'ripetuta'
    classi = OrderedDict((k, []) for k in ('a: entrambe ripetute', 'b: destra forma nuova', 'c: sinistra forma nuova', 'd: destra errore', 'e: sinistra errore'))
    for st, pag, npar, ws, seps in rr:
        sez = st.split('-')[0]
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            ca, cb = cat[''.join(a)], cat[''.join(b)]
            x = (sez, a[-1], b[0])
            if ca == 'ripetuta' and cb == 'ripetuta':
                classi['a: entrambe ripetute'].append(x)
            if cb == 'nuova':
                classi['b: destra forma nuova'].append(x)
            if ca == 'nuova':
                classi['c: sinistra forma nuova'].append(x)
            if cb == 'errore':
                classi['d: destra errore'].append(x)
            if ca == 'errore':
                classi['e: sinistra errore'].append(x)
    base = classi['a: entrambe ripetute']
    ris = OrderedDict()
    for k, cc in classi.items():
        if k.startswith('a'):
            continue
        x = e386.prova(cc, rnd, 1000)
        pari = statistics.median(e386.prova(rnd.sample(base, len(cc)), rnd, 200)['E'] for _ in range(20))
        Q = x['E'] / pari if pari > 0 else None
        if Q is not None and Q > 0.7 and x['z'] > 3:
            es = 'rispettano la giuntura'
        elif Q is None or Q < 0.3 or x['z'] < 2:
            es = 'non la rispettano'
        else:
            es = 'in parte'
        ris[k] = OrderedDict([('coppie', len(cc)), ('E', x['E']), ('z', x['z']), ('E_ripetute_a_parita', pari), ('Q', Q), ('esito', es)])
        print(k, json.dumps(ris[k], ensure_ascii=False, default=float), flush=True)
    out = OrderedDict([('coppie_ripetute', len(base)), ('classi', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a12_uniche_giuntura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a12 — Le parole uniche rispettano la giuntura con le vicine?', '', 'Preregistrazione: `preregistrazioni/e3a12.md`. Coppie di parole ripetute: %d.' % len(base), '',
          '| classe | coppie | E | z | E ripetute a parità | Q | esito |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.4f | %.1f | %.4f | %s | %s |' % (k, x['coppie'], x['E'], x['z'], x['E_ripetute_a_parita'], '%.2f' % x['Q'] if x['Q'] is not None else '', x['esito']))
    open(os.path.join(RISULTATI, 'e3a12_uniche_giuntura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
