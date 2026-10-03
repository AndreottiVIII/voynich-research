# -*- coding: utf-8 -*-
"""Esperimento 371: la dispersione fra i bifogli della quota di forme nuove (e357) resta con le sole parole in mezzo alla
riga, nelle righe che non sono prime di paragrafo?

Preregistrazione: preregistrazioni/e371.md. Scrive risultati/e371_inventiva_centro.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e308_libro_fisico as e308
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 1000


def main():
    rnd = random.Random(371)
    testa = e308.intestazioni()
    tok = []    # (bifoglio, strato, in mezzo e non prima riga, parola)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole or not testa.get(r.pagina, {}).get('Q'):
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w)]
        b = (testa[r.pagina]['Q'], testa[r.pagina]['B'])
        st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
        n = len(ws)
        tok += [(b, st, (0 < j < n - 1) and not r.inizio_par, w) for j, w in enumerate(ws)]
    freq = Counter(t[3] for t in tok)
    sim = e350.simili_globali(set(freq))
    nuova = {w for w, n in freq.items() if n == 1 and not any(freq[v] >= 20 for v in sim[w] if v != w)}
    tutti = defaultdict(list)
    for b, st, centro, w in tok:
        tutti[b].append((st, centro, w in nuova))
    grandi = [b for b, xs in tutti.items() if len(xs) >= 150]
    st_b = {b: Counter(x[0] for x in tutti[b]).most_common(1)[0][0] for b in grandi}
    per_st = defaultdict(list)
    for b in grandi:
        per_st[st_b[b]].append(b)
    etich = {b: [x[2] for x in tutti[b] if x[1]] for b in grandi}

    def var(e):
        tot = []
        for st, bs in per_st.items():
            bs = [b for b in bs if e[b]]
            if len(bs) < 2:
                continue
            q = {b: sum(e[b]) / len(e[b]) for b in bs}
            m = statistics.mean(q.values())
            tot += [q[b] - m for b in bs]
        return statistics.mean(x * x for x in tot)
    vero = var(etich)
    nul = []
    for _ in range(PERM):
        e2 = {}
        for st, bs in per_st.items():
            tutte = [c for b in bs for c in etich[b]]
            rnd.shuffle(tutte)
            i = 0
            for b in bs:
                n = len(etich[b])
                e2[b] = tutte[i:i + n]
                i += n
        nul.append(var(e2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero - m) / sd if sd else 0.0
    esito = 'l\'inventiva regge senza i bordi' if z > 3 else ('era un effetto dei bordi' if z < 2 else 'incerto')
    out = OrderedDict([('bifogli', len(grandi)), ('parole_in_mezzo', sum(len(e) for e in etich.values())), ('varianza_scarti', vero), ('nullo', m),
                       ('rapporto', vero / m if m else None), ('z', z), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e371_inventiva_centro.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e371 — L\'inventiva delle sessioni regge senza i bordi della riga?', '', 'Preregistrazione: `preregistrazioni/e371.md`.', '',
          '%d bifogli, %d parole in mezzo alla riga (righe non prime di paragrafo). Dispersione della quota di forme nuove: rapporto sul nullo %.2f, z %.1f. Esito: **%s**.' % (
              len(grandi), out['parole_in_mezzo'], out['rapporto'], z, esito)]
    open(os.path.join(RISULTATI, 'e371_inventiva_centro.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
