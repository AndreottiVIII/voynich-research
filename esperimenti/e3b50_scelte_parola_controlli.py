# -*- coding: utf-8 -*-
"""Esperimento e3b50: e3b49 con la trascrizione di Takahashi, e taratura della sensibilità sulla ZL con un legame con la
parola aggiunto apposta (quota f di scelte sostituite con la scelta più frequente per quella parola).

Preregistrazione: preregistrazioni/e3b50.md. Scrive risultati/e3b50_scelte_parola_controlli.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3b45_raccordo_a_capo as e3b45
import e3b49_scelte_parola as e3b49

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
QUOTE = (0.1, 0.2, 0.3)


def a_segni(pagine_str):
    out = []
    for pars in pagine_str:
        pp = [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if pp:
            out.append(pp)
    return out


def misura_iniettata(pagine, f, rnd):
    """Come e3b49.misura, ma con una quota f di scelte sostituite dalla scelta più frequente per la parola."""
    per = {c: ([], []) for c in e3b49.CLASSI}
    for k, pars in enumerate(pagine):
        for par in pars:
            for r in par:
                for c, ctx, par_, v in e3b49.eventi_riga(r):
                    per[c][k % 2].append((ctx, par_, v))
    out = OrderedDict()
    for c in e3b49.CLASSI:
        tutti = per[c][0] + per[c][1]
        if not per[c][0] or not per[c][1]:
            out[c] = (None, 0)
            continue
        cont = defaultdict(Counter)
        for _, par_, v in tutti:
            cont[par_][v] += 1
        magg = {p: cc.most_common(1)[0][0] for p, cc in cont.items() if sum(cc.values()) >= 3}
        nuove = []
        for meta in per[c]:
            nuove.append([(ctx, p, magg[p] if p in magg and rnd.random() < f else v) for ctx, p, v in meta])
        s1, n1 = e3b49.risparmio(nuove[0], nuove[1])
        s2, n2 = e3b49.risparmio(nuove[1], nuove[0])
        out[c] = ((s1 + s2) / (n1 + n2), n1 + n2)
    return out


def main():
    rnd = random.Random(3250)
    it = a_segni(list(e3b45.pagine_it().values()))
    voy_it = e3b49.misura(it)
    print('IT', json.dumps(voy_it), flush=True)
    tab = e3a71.catena([r for pars in it for par in pars for r in par], e3a78.ORDINE)
    catene_it = []
    for k in range(5):
        catene_it.append(e3b49.misura(e3a78.riscrivi(it, tab, rnd)))
        print('catena IT', k, json.dumps(catene_it[-1]), flush=True)
    rep = OrderedDict()
    sopra = sotto = 0
    for c in e3b49.CLASSI:
        cs = [x[c][0] for x in catene_it]
        mx, mm = max(cs), sum(cs) / len(cs)
        v = voy_it[c][0]
        rep[c] = OrderedDict([('IT', v), ('occorrenze', voy_it[c][1]), ('catena_media', mm), ('catena_max', mx)])
        sopra += v - mx >= 0.01
        sotto += v - mx < 0.005
    es1 = 'si ritrova con Takahashi' if sotto >= 3 else ('non si ritrova' if sopra >= 3 else 'incerto')
    zl = a_segni([[[r for r in par] for par in pars] for pars in e341.pagine().values()])
    prima = json.load(open(os.path.join(RISULTATI, 'e3b49_scelte_parola.json'), encoding='utf-8'))['confronto']
    tar = OrderedDict()
    for f in QUOTE:
        tar[str(f)] = e3b49.misura(zl) if f == 0 else misura_iniettata(zl, f, rnd)
        print('taratura', f, json.dumps(tar[str(f)]), flush=True)
    sens = sum(1 for c in e3b49.CLASSI if tar['0.2'][c][0] - prima[c]['catena_max'] >= 0.01)
    es2 = 'la prova è sensibile' if sens >= 3 else 'poco sensibile'
    out = OrderedDict([('replica_IT', rep), ('catene_IT', catene_it), ('esito_1', es1), ('taratura_ZL', tar), ('catena_ZL_e3b49', prima), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b50_scelte_parola_controlli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b50 — Scelte legate solo ai segni vicini: Takahashi e taratura', '', 'Preregistrazione: `preregistrazioni/e3b50.md`. Risparmio in bit per occorrenza, fuori campione.', '',
          '## Replica con Takahashi', '', '| classe | occorrenze | IT | catena IT: media (massimo) |', '|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.4f (%+.4f) |' % (c, x['occorrenze'], x['IT'], x['catena_media'], x['catena_max']) for c, x in rep.items()]
    md += ['', 'Esito 1: **%s**.' % es1, '', '## Taratura (ZL con legame con la parola aggiunto)', '',
           '| classe | ZL vera (e3b49) | catena ZL massimo (e3b49) | ' + ' | '.join('f = %s' % f for f in QUOTE) + ' |', '|---|---|---|' + '---|' * len(QUOTE)]
    md += ['| %s | %+.4f | %+.4f | ' % (c, prima[c]['voynich'], prima[c]['catena_max']) + ' | '.join('%+.4f' % tar[str(f)][c][0] for f in QUOTE) + ' |' for c in e3b49.CLASSI]
    md += ['', 'Esito 2: **%s**.' % es2]
    open(os.path.join(RISULTATI, 'e3b50_scelte_parola_controlli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
