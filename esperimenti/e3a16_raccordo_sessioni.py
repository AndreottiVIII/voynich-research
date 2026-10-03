# -*- coding: utf-8 -*-
"""Esperimento e3a16: dispersione fra i bifogli (a parita' di strato) della forza della regola di qo-
(Delta = P(qo | V) - P(qo | C)), contro un nullo che rimescola gli esiti fra bifogli dello stesso strato e classe.

Preregistrazione: preregistrazioni/e3a16.md. Scrive risultati/e3a16_raccordo_sessioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e308_libro_fisico as e308
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
MIN = 15


def main():
    rnd = random.Random(3116)
    testa = e308.intestazioni()
    ev = defaultdict(lambda: {'V': [], 'C': []})
    strati = defaultdict(Counter)
    for st, pag, npar, ws, seps in e386.righe():
        h = testa.get(pag, {})
        if not h.get('Q'):
            continue
        b_id = (h['Q'], h['B'])
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            q = e380.ini_qo(b)
            if q and (a[-1] in V or a[-1] in C):
                ev[b_id]['V' if a[-1] in V else 'C'].append(q[1] == 'qo')
                strati[b_id][st] += 1
    usati = [b for b, d in ev.items() if len(d['V']) >= MIN and len(d['C']) >= MIN]
    st_b = {b: strati[b].most_common(1)[0][0] for b in usati}
    per_st = defaultdict(list)
    for b in usati:
        per_st[st_b[b]].append(b)
    per_st = {s: bs for s, bs in per_st.items() if len(bs) >= 2}

    def disp(dati):
        sc = []
        for bs in per_st.values():
            d = {b: sum(dati[b]['V']) / len(dati[b]['V']) - sum(dati[b]['C']) / len(dati[b]['C']) for b in bs}
            m = statistics.mean(d.values())
            sc += [x - m for x in d.values()]
        return statistics.mean(x * x for x in sc)
    vero = disp(ev)
    nul = []
    for _ in range(1000):
        d2 = {}
        for bs in per_st.values():
            for cl in ('V', 'C'):
                tutte = [x for b in bs for x in ev[b][cl]]
                rnd.shuffle(tutte)
                i = 0
                for b in bs:
                    n = len(ev[b][cl])
                    d2.setdefault(b, {})[cl] = tutte[i:i + n]
                    i += n
        nul.append(disp(d2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero - m) / sd if sd else 0.0
    esito = 'la regola varia fra le sessioni' if z > 3 else ('uniforme fra le sessioni, come una regola fissa' if z < 2 else 'incerto')
    delta = {'%s-%s' % b: sum(ev[b]['V']) / len(ev[b]['V']) - sum(ev[b]['C']) / len(ev[b]['C']) for bs in per_st.values() for b in bs}
    out = OrderedDict([('bifogli', sum(len(b) for b in per_st.values())), ('strati', len(per_st)), ('varianza', vero), ('nullo', m), ('rapporto', vero / m if m else None), ('z', z),
                       ('delta_per_bifoglio', OrderedDict(sorted(delta.items(), key=lambda kv: kv[1]))), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:1500], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a16_raccordo_sessioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    ds = list(out['delta_per_bifoglio'].values())
    md = ['# e3a16 — La regola di raccordo varia da una sessione all\'altra?', '', 'Preregistrazione: `preregistrazioni/e3a16.md`.', '',
          '%d bifogli in %d strati. Δ per bifoglio da %+.2f a %+.2f (mediana %+.2f). Dispersione degli scarti dallo strato: %.4f contro %.4f del nullo (rapporto %.2f), z %.1f.' % (
              out['bifogli'], out['strati'], min(ds), max(ds), statistics.median(ds), vero, m, out['rapporto'], z), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a16_raccordo_sessioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
