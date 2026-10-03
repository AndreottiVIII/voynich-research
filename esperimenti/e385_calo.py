# -*- coding: utf-8 -*-
"""Esperimento 385: eccesso di ripresa (parola uguale o a una modifica) dalla riga a distanza L = 1..6, con l'atteso
calcolato esattamente su tutte le altre righe dell'unita'; forma del calo C = media(e3..e6) / e1. Voynich (paragrafi),
testi sensati (parole intere, pagine di 25 righe), gibberish umano.

Preregistrazione: preregistrazioni/e385.md. Scrive risultati/e385_calo.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
LAG = range(1, 7)


def simili_unita(righe):
    tipi = {w for r in righe for w in r}
    jolly, canc = defaultdict(set), defaultdict(set)
    for w in tipi:
        for i in range(len(w)):
            jolly[w[:i] + ('*',) + w[i + 1:]].add(w)
            canc[w[:i] + w[i + 1:]].add(w)
    sim = {}
    for w in tipi:
        s = {w} | canc.get(w, set())
        for i in range(len(w)):
            s |= jolly[w[:i] + ('*',) + w[i + 1:]]
            if w[:i] + w[i + 1:] in tipi:
                s.add(w[:i] + w[i + 1:])
        sim[w] = s
    return sim


def unita(righe):
    """Per un'unita': {L: (osservati, attesi, bersagli)}."""
    n = len(righe)
    sim = simili_unita(righe)
    insiemi = [set(r) for r in righe]
    bers = [[w for w in r if len(w) >= 3] for r in righe]
    colpi = [[sum(1 for w in bers[i] if sim[w] & insiemi[j]) if i != j else 0 for j in range(n)] for i in range(n)]
    out = {}
    for L in LAG:
        o = a = t = 0.0
        for i in range(L, n):
            if not bers[i]:
                continue
            o += colpi[i][i - L]
            a += sum(colpi[i][j] for j in range(n) if j != i) / (n - 1)
            t += len(bers[i])
        out[L] = (o, a, t)
    return out


def profilo(us):
    e = OrderedDict()
    for L in LAG:
        o = sum(u[L][0] for u in us)
        a = sum(u[L][1] for u in us)
        t = sum(u[L][2] for u in us)
        e[L] = (o - a) / t if t else 0.0
    C = statistics.mean(e[L] for L in range(3, 7)) / e[1] if e[1] > 0 else float('nan')
    return e, C


def gruppo(unita_righe, rnd):
    us = [unita(r) for r in unita_righe if len(r) >= 2]
    e, C = profilo(us)
    boot = sorted(profilo([us[rnd.randrange(len(us))] for _ in us])[1] for _ in range(1000))
    return OrderedDict([('unita', len(us)), ('parole', sum(len(w) for r in unita_righe for w in r)), ('e', e), ('C', C), ('IC95_C', [boot[25], boot[974]])])


def main():
    rnd = random.Random(385)
    voy = []
    for pars in e341.pagine().values():
        for par in pars:
            rr = [[tuple(D(w)) for w in r] for r in par]
            voy.append([[w for w in r if w] for r in rr])
    sens = e381.testi()
    pag = {k: [t[:500][i:i + 25] for i in range(0, len(t[:500]), 25)] for k, t in sens.items()}
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(n).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib += [righe[i:i + 25] for i in range(0, len(righe), 25)]
    corpi = OrderedDict([('Voynich', voy), ('gibberish umano', gib), ('testi sensati', [p for pp in pag.values() for p in pp])])
    for cat in ('Historical', 'Modern', 'Conlangs'):
        corpi['testi sensati: %s' % cat] = [p for k, pp in pag.items() if k.startswith(cat) for p in pp]
    ris = OrderedDict()
    for nome, uu in corpi.items():
        ris[nome] = gruppo(uu, rnd)
        print(nome, json.dumps(ris[nome], default=float), flush=True)
    V, S = ris['Voynich']['IC95_C'], ris['testi sensati']['IC95_C']
    if V[1] < S[0]:
        esito = 'il Voynich cala più in fretta delle lingue (copia a corto raggio)'
    elif V[0] > S[1]:
        esito = 'il Voynich cala più piano'
    else:
        esito = 'stessa forma'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e385_calo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e385 — La ripresa del Voynich cala con la distanza come nelle lingue?', '', 'Preregistrazione: `preregistrazioni/e385.md`. e_L = eccesso di parole (3+ segni) con una parola uguale o a una modifica nella riga a distanza L; C = media(e3..e6)/e1.', '',
          '| testo | unità | e1 | e2 | e3 | e4 | e5 | e6 | C | IC 95% di C |', '|---|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %s | %.2f | %.2f – %.2f |' % (k, x['unita'], ' | '.join('%+.4f' % x['e'][L] for L in LAG), x['C'], x['IC95_C'][0], x['IC95_C'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e385_calo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
