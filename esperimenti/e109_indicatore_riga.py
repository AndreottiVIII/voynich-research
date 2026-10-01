# -*- coding: utf-8 -*-
"""Esperimento 109: il primo segno di riga e' un indicatore di chiave per il resto della riga?

Preregistrazione: preregistrazioni/e109.md. Scrive risultati/e109_indicatore_riga.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, MIN_RIGHE = 109, 500, 100
D = misure.divisore(misure.GLIFI_EVA)
FAMIGLIE = {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'k': 'G', 't': 'G', 'p': 'G', 'f': 'G', 'd': 'D', 'r': 'D', 's': 'D'}


def fam(g):
    return FAMIGLIE.get(g, g)


def voci(righe, dividi, classe_di):
    """righe: (pagina, inizio, parole) -> (pagina, classe d'inizio, segni del resto, classe 2a parola, lungh. media resto)."""
    out = []
    for pag, ini, ps in righe:
        if ini or len(ps) < 4 or not all(trascrizione.pulita(w) for w in ps):
            continue
        c = classe_di(dividi(ps[0])[0])
        resto = [g for w in ps[1:] for g in dividi(w)]
        out.append([pag, c, resto, classe_di(dividi(ps[1])[0]), sum(len(dividi(w)) for w in ps[1:]) / (len(ps) - 1)])
    conta = Counter(v[1] for v in out)
    tenute = {c for c, n in conta.items() if n >= MIN_RIGHE}
    out = [v for v in out if v[1] in tenute]
    terzili = sorted(v[4] for v in out)
    t1, t2 = terzili[len(terzili) // 3], terzili[2 * len(terzili) // 3]
    for v in out:
        v[4] = 0 if v[4] <= t1 else 1 if v[4] <= t2 else 2
    return out


def statistiche(vv, classe_di):
    # 1. diagonale
    stessa = sum(sum(classe_di(g) == v[1] for g in v[2]) for v in vv)
    tot = sum(len(v[2]) for v in vv)
    # 2. fuori diagonale: coppie (classe d'inizio, segno del resto non della stessa classe), pesate per riga
    coppie = [(v[1], g) for v in vv for g in v[2] if classe_di(g) != v[1]]
    im2 = misure.informazione_mutua(coppie)
    # 3. seconda parola, esclusa la stessa classe
    im3 = misure.informazione_mutua([(v[1], v[3]) for v in vv if v[3] != v[1]])
    # 4. lunghezza
    im4 = misure.informazione_mutua([(v[1], v[4]) for v in vv])
    return {'diagonale': stessa / tot, 'fuori_diagonale': im2, 'seconda_parola': im3, 'lunghezza': im4}


def misura(vv, classe_di, rnd):
    reale = statistiche(vv, classe_di)
    per = defaultdict(list)
    for i, v in enumerate(vv):
        per[v[0]].append(i)
    nulli = defaultdict(list)
    for _ in range(PERMUTAZIONI):
        cl = [v[1] for v in vv]
        for idx in per.values():
            x = [cl[i] for i in idx]
            rnd.shuffle(x)
            for i, c in zip(idx, x):
                cl[i] = c
        for k, val in statistiche([[v[0], c] + v[2:] for v, c in zip(vv, cl)], classe_di).items():
            nulli[k].append(val)
    out = OrderedDict([('righe', len(vv)), ('classi', dict(Counter(v[1] for v in vv)))])
    for k, val in reale.items():
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('reale', val), ('nullo', m), ('eccesso', val - m), ('z', (val - m) / s if s else None)])
    return out


def con_tavole(vv, classe_di, rnd, forte):
    """Controllo positivo: per ogni classe d'inizio una tavola sui segni del resto della riga."""
    frequenti = [g for g, _ in Counter(g for v in vv for g in v[2]).most_common(10)]
    tavole = {}
    for c in sorted({v[1] for v in vv}):
        if forte:
            perm = frequenti[:8][:]
            rnd.shuffle(perm)
            tavole[c] = dict(zip(frequenti[:8], perm))
        else:
            a = frequenti[:]
            rnd.shuffle(a)
            t = {}
            for x, y in ((a[0], a[1]), (a[2], a[3])):
                t[x], t[y] = y, x
            tavole[c] = t
    return [[v[0], v[1], [tavole[v[1]].get(g, g) for g in v[2]], v[3], v[4]] for v in vv], tavole


def main():
    righe = [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    vv = voci(righe, D, fam)
    ris = OrderedDict()
    ris['Voynich'] = misura(vv, fam, random.Random(SEME))
    rnd = random.Random(SEME)
    forte, tav_f = con_tavole(vv, fam, rnd, True)
    debole, tav_d = con_tavole(vv, fam, rnd, False)
    ris['controllo positivo forte'] = misura(forte, fam, random.Random(SEME))
    ris['controllo positivo debole'] = misura(debole, fam, random.Random(SEME))
    ris['tavole del controllo debole'] = {c: t for c, t in tav_d.items()}
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    ris['Timm e Schinner, seme 19'] = misura(voci([(i // 29, ini, ps) for i, (ini, ps) in enumerate(ts)], D, fam), fam, random.Random(SEME))
    import e99_macer as e99
    caps = e99.capitoli()
    rm = [(k, j == 0, ps) for k, c in enumerate(caps) for j, ps in enumerate(c)]
    ris['Macer in versi (lettere)'] = misura(voci(rm, e71.lettere, lambda g: g), lambda g: g, random.Random(SEME))
    for nome, r in ris.items():
        if 'righe' not in r:
            continue
        print('%-28s righe %4d | diagonale %+.4f (z %.1f) | fuori diagonale %+.4f (z %.1f) | seconda parola %+.4f (z %.1f) | lunghezza %+.4f (z %.1f)' % (
            nome, r['righe'], r['diagonale']['eccesso'], r['diagonale']['z'] or 0, r['fuori_diagonale']['eccesso'], r['fuori_diagonale']['z'] or 0,
            r['seconda_parola']['eccesso'], r['seconda_parola']['z'] or 0, r['lunghezza']['eccesso'], r['lunghezza']['z'] or 0), flush=True)
    v, d = ris['Voynich']['fuori_diagonale'], ris['controllo positivo debole']['fuori_diagonale']
    valido = (d['z'] or 0) > 5
    if (v['z'] or 0) > 4 and v['eccesso'] >= 0.25 * d['eccesso']:
        lettura = 'indicatore non escluso'
    elif (v['z'] or 0) < 2:
        lettura = 'indicatore escluso (alla sensibilità del controllo debole)'
    else:
        lettura = 'indeciso'
    ris['valido'], ris['lettura'] = valido, lettura
    print('valido', valido, '|', lettura)
    with open(os.path.join(RISULTATI, 'e109_indicatore_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e109 — Il primo segno di riga è un indicatore di chiave?', '',
           'Eccesso rispetto a %d rimescolamenti delle classi d\'inizio fra le righe della stessa pagina; z fra parentesi. '
           'Preregistrazione: `preregistrazioni/e109.md`.' % PERMUTAZIONI, '',
           '| testo | righe | diagonale (stessa classe) | fuori diagonale (indicatore) | seconda parola | lunghezza |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'righe' in r:
            out.append('| %s | %d | %s |' % (nome, r['righe'], ' | '.join('%+.4f (%.1f)' % (r[k]['eccesso'], r[k]['z'] or 0)
                                                                    for k in ('diagonale', 'fuori_diagonale', 'seconda_parola', 'lunghezza'))))
    out += ['', 'Controllo valido: **%s**. Lettura: **%s**.' % ('sì' if valido else 'no', lettura)]
    with open(os.path.join(RISULTATI, 'e109_indicatore_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
