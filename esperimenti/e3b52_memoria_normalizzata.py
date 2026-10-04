# -*- coding: utf-8 -*-
"""Esperimento e3b52: memoria corta normalizzata (accordo in più come quota dello spazio disponibile), vicine − lontane,
senza parole simili: Voynich (ZL, classi dell'e3b20, nella stessa riga) contro Hatton Gospels (þ/ð, testo continuo).

Preregistrazione: preregistrazioni/e3b52.md. Scrive risultati/e3b52_memoria_normalizzata.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b20_memoria_segni as e3b20
import e3b51_thorn_eth as e3b51

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000
VICINE, LONTANE = (2, 3), tuple(range(6, 11))


def eventi(unita, classi, forma):
    """unita: [lista di sequenze di parole]; forma(w) -> tupla di segni per la somiglianza.
    Ritorna [(unità, classe, gruppo, accordo, atteso)]."""
    out = []
    for u, seqs in enumerate(unita):
        for c, f in classi.items():
            vv = [[f(w) for w in s] for s in seqs]
            T = sum(1 for v in vv for x in v if x is not None)
            U = sum(1 for v in vv for x in v if x == 1)
            for s, v in zip(seqs, vv):
                for i in range(len(s)):
                    if v[i] is None:
                        continue
                    for d in VICINE + LONTANE:
                        j = i + d
                        if j >= len(s) or v[j] is None:
                            continue
                        a, z = forma(s[i]), forma(s[j])
                        if a == z or e3a86.una_modifica(a, z):
                            continue
                        t, uu = T - 2, U - v[i] - v[j]
                        if t < 5:
                            continue
                        p = uu / t
                        out.append((u, c, 'vicine' if d in VICINE else 'lontane', int(v[i] == v[j]), p * p + (1 - p) * (1 - p)))
    return out


def memoria(ev):
    acc = defaultdict(lambda: [0.0, 0.0, 0])
    for _, _, g, ok, att in ev:
        acc[g][0] += ok
        acc[g][1] += att
        acc[g][2] += 1
    k = {}
    for g in ('vicine', 'lontane'):
        o, a, n = acc[g]
        if not n or n - a <= 0:
            return None, {}
        k[g] = (o - a) / (n - a)
    return k['vicine'] - k['lontane'], {g: (k[g], acc[g][2]) for g in k}


def boot(ev, rnd):
    per = defaultdict(list)
    for x in ev:
        per[x[0]].append(x)
    chiavi = list(per)
    return [v for v in (memoria([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])[0] for _ in range(BOOT)) if v is not None]


def ic(xs):
    xs = sorted(xs)
    return [xs[int(0.025 * len(xs))], xs[int(0.975 * len(xs)) - 1]]


def main():
    rnd = random.Random(3252)
    voy = []
    for pg, pars in e341.pagine().items():
        righe = [[w for w in r if trascrizione.pulita(w)] for par in pars for r in par]
        righe = [r for r in righe if r]
        if righe:
            voy.append(righe)
    ev_v = eventi(voy, e3b20.CLASSI, lambda w: tuple(D(w)))
    righe_h = [r for r in e381.testi()[e3b51.TESTI['Hatton Gospels']] if r]
    ev_h = eventi([[b] for b in e3b51.blocchi(righe_h)], e3b51.CLASSI, lambda w: w)
    ris = OrderedDict()
    bb = {}
    for nome, ev in (('Voynich (ZL)', ev_v), ('Hatton Gospels (þ/ð)', ev_h)):
        m, dett = memoria(ev)
        bb[nome] = boot(ev, rnd)
        per_classe = OrderedDict()
        for c in sorted({x[1] for x in ev}):
            per_classe[c] = memoria([x for x in ev if x[1] == c])[0]
        ris[nome] = OrderedDict([('memoria', m), ('dettaglio', dett), ('IC95', ic(bb[nome])), ('per_classe', per_classe)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    a, b = bb['Voynich (ZL)'], bb['Hatton Gospels (þ/ð)']
    n = min(len(a), len(b))
    contr = [a[i] - b[i] for i in range(n)]
    c = ris['Voynich (ZL)']['memoria'] - ris['Hatton Gospels (þ/ð)']['memoria']
    ci = ic(contr)
    esito = "il Voynich ha più memoria dello scriba anglosassone" if ci[0] > 0 else ('il Voynich ne ha meno' if ci[1] < 0 else 'memoria comparabile')
    out = OrderedDict([('testi', ris), ('contrasto', c), ('IC95_contrasto', ci), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b52_memoria_normalizzata.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b52 — Memoria corta normalizzata: Voynich contro lo scriba anglosassone', '', 'Preregistrazione: `preregistrazioni/e3b52.md`. K = accordo in più come quota dello spazio disponibile; memoria = K(vicine) − K(lontane); senza parole simili.', '',
          '| testo | K vicine (coppie) | K lontane (coppie) | memoria (IC 95%) | per classe |', '|---|---|---|---|---|']
    for nome, x in ris.items():
        v, l = x['dettaglio']['vicine'], x['dettaglio']['lontane']
        md.append('| %s | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) | %s |' % (nome, v[0], v[1], l[0], l[1], x['memoria'], x['IC95'][0], x['IC95'][1],
                                                                             ', '.join('%s %+.3f' % (k, y) for k, y in x['per_classe'].items() if y is not None)))
    md += ['', 'Contrasto Voynich − Hatton: **%+.4f** (IC 95%% %+.4f – %+.4f). Esito: **%s**.' % (c, ci[0], ci[1], esito)]
    open(os.path.join(RISULTATI, 'e3b52_memoria_normalizzata.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
