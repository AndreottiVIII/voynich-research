# -*- coding: utf-8 -*-
"""Esperimento 360: controllo dell'e357. La dispersione fra i bifogli della quota di forme nuove resta togliendo le
prime righe dei paragrafi (e anche le ultime)? E' legata alla densita' di paragrafi?

Preregistrazione: preregistrazioni/e360.md. Scrive risultati/e360_paragrafi.json e .md.
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
    rnd = random.Random(360)
    testa = e308.intestazioni()
    tok = []    # (bifoglio, strato, tipo di riga, parola)
    paragrafi = Counter()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole or not testa.get(r.pagina, {}).get('Q'):
            continue
        b = (testa[r.pagina]['Q'], testa[r.pagina]['B'])
        st = '%s-%s' % (r.sezione or '?', r.lingua or '?')
        tipo = 'prima' if r.inizio_par else ('ultima' if r.fine_par else 'interna')
        paragrafi[b] += bool(r.inizio_par)
        tok += [(b, st, tipo, w) for w in r.parole if trascrizione.pulita(w)]
    freq = Counter(t[3] for t in tok)
    sim = e350.simili_globali(set(freq))
    cat = {}
    for w, n in freq.items():
        if n == 1:
            cat[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
    tutti = defaultdict(list)
    for b, st, tipo, w in tok:
        tutti[b].append((st, tipo, cat.get(w, '-')))
    grandi = [b for b, xs in tutti.items() if len(xs) >= 150]
    st_b = {b: Counter(x[0] for x in tutti[b]).most_common(1)[0][0] for b in grandi}
    per_st = defaultdict(list)
    for b in grandi:
        per_st[st_b[b]].append(b)

    def dispersione(filtro):
        etich = {b: [x[2] for x in tutti[b] if filtro(x[1])] for b in grandi}

        def var(e):
            tot = []
            for st, bs in per_st.items():
                bs = [b for b in bs if e[b]]
                if len(bs) < 2:
                    continue
                q = {b: sum(c == 'nuova' for c in e[b]) / len(e[b]) for b in bs}
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
        return OrderedDict([('varianza_scarti', vero), ('nullo', m), ('rapporto', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)]), etich
    from scipy.stats import spearmanr
    m0, et0 = dispersione(lambda t: True)
    m2, _ = dispersione(lambda t: t != 'prima')
    m3, _ = dispersione(lambda t: t == 'interna')
    dens = [100 * paragrafi[b] / len(tutti[b]) for b in grandi]
    nuove = [sum(c == 'nuova' for c in et0[b]) / len(et0[b]) for b in grandi]
    rho = spearmanr(dens, nuove).correlation
    nr = [spearmanr(dens, rnd.sample(nuove, len(nuove))).correlation for _ in range(PERM)]
    zr = (rho - statistics.mean(nr)) / statistics.pstdev(nr)
    if m2['z'] > 3 and m3['z'] > 3:
        esito = 'l\'inventiva non è un effetto dei paragrafi'
    elif m2['z'] < 2 and zr > 3:
        esito = 'è in gran parte un effetto dei paragrafi'
    else:
        esito = 'incerto'
    out = OrderedDict([('bifogli', len(grandi)), ('tutte_le_righe', m0), ('senza_prime_righe', m2), ('solo_righe_interne', m3),
                       ('spearman_densita_paragrafi_forme_nuove', rho), ('z_spearman', zr), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e360_paragrafi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e360 — L\'inventiva delle sessioni dipende dal numero di paragrafi?', '', 'Preregistrazione: `preregistrazioni/e360.md`. %d bifogli.' % len(grandi), '',
          '| righe usate | rapporto della dispersione delle forme nuove sul nullo | z |', '|---|---|---|']
    for k, v in (('tutte', m0), ('senza le prime righe dei paragrafi', m2), ('solo righe interne', m3)):
        md.append('| %s | %.2f | %.1f |' % (k, v['rapporto'], v['z']))
    md += ['', 'Spearman fra densità di paragrafi e quota di forme nuove: %.3f, z %.1f.' % (rho, zr), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e360_paragrafi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
