# -*- coding: utf-8 -*-
"""Esperimento 346: la ripresa dalle 2 righe sopra (parole uguali o a una modifica, di almeno 3 segni) nel Voynich, nel
gibberish scritto a mano (Gaskell e Bowern 2022) e nei testi sensati della stessa raccolta; riferimento: il generatore
di Timm e Schinner.

Preregistrazione: preregistrazioni/e346.md. Scrive risultati/e346_gibberish.json e .md.
"""
import io, json, os, random, re, statistics, sys, zipfile
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e310_inizi_etichette as e310
import e337_posizione as e337

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
NUL = 100


def da_zip(nome, filtro):
    out = OrderedDict()
    with zipfile.ZipFile(os.path.join(GB, nome)) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt') and filtro(n):
                testo = z.read(n).decode('utf-8', errors='ignore')
                righe = []
                for l in testo.splitlines():
                    ws = [w for w in re.findall(r'[^\W\d_]+', l.lower())]
                    if ws:
                        righe.append(ws)
                if len(righe) >= 10:
                    out[os.path.basename(n)] = righe
    return out


def unita_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                per.setdefault(r.pagina, []).append(ws)
    return OrderedDict((p, v) for p, v in per.items() if len(v) >= 10)


def misura_unita(righe, segni, rnd):
    """(si, tot, media nullo * tot) per un'unita'."""
    tipi = sorted({w for r in righe for w in r if len(segni(w)) >= 3})
    if not tipi:
        return None
    idx = {w: k for k, w in enumerate(tipi)}
    U = [segni(w) for w in tipi]
    M = np.zeros((len(tipi), len(tipi)), dtype=bool)
    for a in range(len(tipi)):
        M[a, a] = True
        for b in range(a + 1, len(tipi)):
            if abs(len(U[a]) - len(U[b])) <= 1 and e310.dist1(U[a], U[b]):
                M[a, b] = M[b, a] = True
    rr = [[idx[w] for w in r if w in idx] for r in righe]

    def quota(ordine):
        si = tot = 0
        x = [rr[k] for k in ordine]
        for i in range(2, len(x)):
            sopra = x[i - 1] + x[i - 2]
            for w in x[i]:
                tot += 1
                si += bool(M[w, sopra].any()) if sopra else False
        return si, tot
    si, tot = quota(list(range(len(rr))))
    if tot == 0:
        return None
    nul = [quota(rnd.sample(range(len(rr)), len(rr)))[0] for _ in range(NUL)]
    return si, tot, statistics.mean(nul)


def gruppo(unita, segni, rnd):
    vals = [v for v in (misura_unita(r, segni, rnd) for r in unita.values()) if v]
    def stima(vs):
        si = sum(v[0] for v in vs)
        tot = sum(v[1] for v in vs)
        nu = sum(v[2] for v in vs)
        return (si - nu) / tot, si / nu if nu else None
    E, R = stima(vals)
    boot = [stima([vals[rnd.randrange(len(vals))] for _ in vals])[0] for _ in range(1000)]
    boot.sort()
    return OrderedDict([('unita', len(vals)), ('parole', sum(v[1] for v in vals)), ('E', E), ('R', R), ('IC95', [boot[25], boot[974]])])


def main():
    rnd = random.Random(346)
    lettere = lambda w: tuple(w)
    voy = unita_voynich()
    gib = da_zip('gibberish_transcriptions.zip', lambda n: True)
    sens = da_zip('meaningful.zip', lambda n: '/texts/' in n or n.startswith('texts/'))
    ris = OrderedDict()
    ris['Voynich'] = gruppo(voy, lambda w: tuple(D(w)), rnd)
    ris['gibberish umano'] = gruppo(gib, lettere, rnd)
    ris['testi sensati'] = gruppo(sens, lettere, rnd)
    for cat in ('Historical', 'Modern', 'Conlangs'):
        sub = OrderedDict((k, v) for k, v in sens.items() if k.startswith(cat))
        if sub:
            ris['testi sensati: %s' % cat] = gruppo(sub, lettere, rnd)
    per_autore = defaultdict(OrderedDict)
    for k, v in gib.items():
        m = re.search(r'-\s*([A-Za-z]{2})', k)
        per_autore[m.group(1) if m else '?'][k] = v
    for a, sub in sorted(per_autore.items()):
        if len(sub) >= 2:
            ris['gibberish, autore %s' % a] = gruppo(sub, lettere, rnd)
    for s in (1, 19):
        pp = e337.pagine_ts(s)
        ris['Timm e Schinner, seme %d' % s] = gruppo(OrderedDict((str(i), p) for i, p in enumerate(pp)), lambda w: tuple(D(w)), rnd)
    for k, v in ris.items():
        print('%-34s unità %3d parole %6d E %+.4f R %.2f IC %s' % (k, v['unita'], v['parole'], v['E'], v['R'] or 0, [round(x, 4) for x in v['IC95']]), flush=True)
    V, G, S = ris['Voynich'], ris['gibberish umano'], ris['testi sensati']
    dentro = lambda x, ic: ic[0] <= x <= ic[1]
    if V['E'] > max(G['IC95'][1], S['IC95'][1]):
        esito = 'più di tutti'
    elif dentro(V['E'], G['IC95']) and not dentro(V['E'], S['IC95']):
        esito = 'come il gibberish umano'
    elif dentro(V['E'], S['IC95']) and not dentro(V['E'], G['IC95']):
        esito = 'come i testi sensati'
    elif dentro(V['E'], G['IC95']) and dentro(V['E'], S['IC95']):
        esito = 'non distinguibile'
    else:
        esito = 'fuori da tutti e due (sotto o in mezzo)'
    json.dump(OrderedDict([('gruppi', ris), ('esito', esito)]), open(os.path.join(RISULTATI, 'e346_gibberish.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e346 — La ripresa dalle righe sopra: Voynich, gibberish umano, testi sensati', '', 'Preregistrazione: `preregistrazioni/e346.md`.', '',
          '| testo | unità | parole | eccesso E | rapporto R | IC 95% di E |', '|---|---|---|---|---|---|']
    for k, v in ris.items():
        md.append('| %s | %d | %d | %+.4f | %.2f | %+.4f – %+.4f |' % (k, v['unita'], v['parole'], v['E'], v['R'] or 0, v['IC95'][0], v['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e346_gibberish.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
