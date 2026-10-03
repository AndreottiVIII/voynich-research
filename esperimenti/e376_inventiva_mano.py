# -*- coding: utf-8 -*-
"""Esperimento 376: la sovradispersione fra i bifogli della quota di forme nuove (e357, e371) resta dentro la stessa mano
di Davis? Tre stratificazioni: sezione x lingua, sezione x lingua x mano, mano. Controllo: gli errori.

Preregistrazione: preregistrazioni/e376.md. Scrive risultati/e376_inventiva_mano.json e .md.
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


def dispersione(etich, strato_b, rnd):
    per_st = defaultdict(list)
    for b, s in strato_b.items():
        per_st[s].append(b)
    per_st = {s: bs for s, bs in per_st.items() if len(bs) >= 2}

    def var(e):
        tot = []
        for bs in per_st.values():
            q = {b: sum(e[b]) / len(e[b]) for b in bs}
            m = statistics.mean(q.values())
            tot += [q[b] - m for b in bs]
        return statistics.mean(x * x for x in tot)
    vero = var(etich)
    nul = []
    for _ in range(PERM):
        e2 = {}
        for bs in per_st.values():
            tutte = [c for b in bs for c in etich[b]]
            rnd.shuffle(tutte)
            i = 0
            for b in bs:
                n = len(etich[b])
                e2[b] = tutte[i:i + n]
                i += n
        nul.append(var(e2))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('strati', len(per_st)), ('bifogli', sum(len(v) for v in per_st.values())), ('varianza', vero), ('nullo', m),
                        ('rapporto', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(376)
    testa = e308.intestazioni()
    tok = []    # (bifoglio, sezione-lingua, mano, parola)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole or not testa.get(r.pagina, {}).get('Q'):
            continue
        b = (testa[r.pagina]['Q'], testa[r.pagina]['B'])
        for w in r.parole:
            if trascrizione.pulita(w):
                tok.append((b, '%s-%s' % (r.sezione or '?', r.lingua or '?'), r.mano or '?', w))
    freq = Counter(t[3] for t in tok)
    sim = e350.simili_globali(set(freq))
    cat = {}
    for w, n in freq.items():
        if n == 1:
            cat[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
    per_b = defaultdict(list)
    for t in tok:
        per_b[t[0]].append(t)
    grandi = [b for b, xs in per_b.items() if len(xs) >= 150]
    sl = {b: Counter(t[1] for t in per_b[b]).most_common(1)[0][0] for b in grandi}
    ma = {b: Counter(t[2] for t in per_b[b]).most_common(1)[0][0] for b in grandi}
    strat = OrderedDict([('(a) sezione x lingua', sl), ('(b) sezione x lingua x mano', {b: (sl[b], ma[b]) for b in grandi}), ('(c) mano', ma)])
    ris = OrderedDict()
    for tipo in ('nuova', 'errore'):
        etich = {b: [cat.get(t[3]) == tipo for t in per_b[b]] for b in grandi}
        ris[tipo] = OrderedDict((k, dispersione(etich, s, rnd)) for k, s in strat.items())
        for k, x in ris[tipo].items():
            print(tipo, k, json.dumps(x, default=float), flush=True)
    zb = ris['nuova']['(b) sezione x lingua x mano']['z']
    esito = 'l\'inventiva è della sessione' if zb > 3 else ('l\'inventiva è dello scriba' if zb < 2 else 'incerto')
    a, b_ = ris['nuova']['(a) sezione x lingua'], ris['nuova']['(b) sezione x lingua x mano']
    eccesso_a, eccesso_b = a['varianza'] - a['nullo'], b_['varianza'] - b_['nullo']
    quota_mano = 1 - eccesso_b / eccesso_a if eccesso_a > 0 else None
    controllo = all(x['z'] < 2 for x in ris['errore'].values())
    out = OrderedDict([('bifogli', len(grandi)), ('mani', dict(Counter(ma.values()))), ('risultati', ris), ('quota_spiegata_dalla_mano', quota_mano),
                       ('controllo_errori_uniformi', controllo), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e376_inventiva_mano.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e376 — L\'inventiva è della sessione o dello scriba?', '', 'Preregistrazione: `preregistrazioni/e376.md`. %d bifogli; mani: %s.' % (len(grandi), dict(sorted(Counter(ma.values()).items()))), '',
          '| parole | stratificazione | strati | bifogli | rapporto sul nullo | z |', '|---|---|---|---|---|---|']
    for tipo, d in ris.items():
        for k, x in d.items():
            md.append('| %s | %s | %d | %d | %.2f | %.1f |' % ('forme nuove' if tipo == 'nuova' else 'errori', k, x['strati'], x['bifogli'], x['rapporto'], x['z']))
    md += ['', 'Quota dell\'eccesso di dispersione delle forme nuove spiegata dalla mano: %s.' % ('%.0f%%' % (100 * quota_mano) if quota_mano is not None else 'n.d.'),
           'Controllo (errori uniformi in tutte le stratificazioni): %s.' % ('sì' if controllo else 'no'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e376_inventiva_mano.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
