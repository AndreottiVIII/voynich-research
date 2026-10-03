# -*- coding: utf-8 -*-
"""Esperimento 350: il bifoglio come sessione di scrittura. Parole rare condivise (Jaccard sui tipi con 2-5 occorrenze) e
ripresa (parole uguali o a una modifica) fra coppie di pagine della stessa sezione, per classe fisica (stesso foglio,
stesso bifoglio, apertura, stesso fascicolo, altro fascicolo), con permutazioni delle pagine dentro la sezione.

Preregistrazione: preregistrazioni/e350.md. Scrive risultati/e350_sessioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000
CLASSI = ['stesso foglio', 'stesso bifoglio, fogli diversi', 'apertura', 'stesso fascicolo, altro', 'altro fascicolo']


def simili_globali(tipi):
    """{tipo: insieme dei tipi uguali o a una modifica} con indici per chiavi (jolly, cancellazione)."""
    U = {w: tuple(D(w)) for w in tipi}
    piano, jolly, canc = defaultdict(set), defaultdict(set), defaultdict(set)
    for w, u in U.items():
        piano[u].add(w)
        for i in range(len(u)):
            jolly[u[:i] + ('*',) + u[i + 1:]].add(w)
            canc[u[:i] + u[i + 1:]].add(w)
    out = {}
    for w, u in U.items():
        s = set(piano[u]) | canc[u]
        for i in range(len(u)):
            s |= jolly[u[:i] + ('*',) + u[i + 1:]]
            s |= piano.get(u[:i] + u[i + 1:], set())
        out[w] = s
    return out


def main():
    rnd = random.Random(350)
    testa = e308.intestazioni()
    pag, sez = OrderedDict(), {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                pag.setdefault(r.pagina, []).extend(ws)
                sez.setdefault(r.pagina, r.sezione or '?')
    freq = Counter(w for ws in pag.values() for w in ws)
    pp = [p for p, ws in pag.items() if len(ws) >= 60 and testa.get(p, {}).get('Q')]
    per_sez = defaultdict(list)
    for p in pp:
        per_sez[sez[p]].append(p)
    pp = [p for p in pp if len(per_sez[sez[p]]) >= 8]
    n = len(pp)
    ix = {p: i for i, p in enumerate(pp)}
    rare = [{w for w in pag[p] if 2 <= freq[w] <= 5} for p in pp]
    lunghe = [[w for w in pag[p] if len(D(w)) >= 3] for p in pp]
    tipi = {w for ws in lunghe for w in ws}
    sim = simili_globali(tipi)
    pagine_di = defaultdict(set)
    for i, ws in enumerate(lunghe):
        for w in set(ws):
            pagine_di[w].add(i)
    J = np.zeros((n, n))
    R = np.zeros((n, n))
    for i in range(n):
        cnt = Counter()
        for w in lunghe[i]:
            ys = set()
            for v in sim[w]:
                ys |= pagine_di.get(v, set())
            for y in ys:
                cnt[y] += 1
        for y, c in cnt.items():
            R[i, y] = c / len(lunghe[i])
        for j in range(n):
            un = rare[i] | rare[j]
            J[i, j] = len(rare[i] & rare[j]) / len(un) if un else 0.0
    R = (R + R.T) / 2
    # classi sulle posizioni
    ordine = sorted(testa, key=lambda p: testa[p]['ordine'])
    seg = dict(zip(ordine, ordine[1:]))
    classi = defaultdict(list)
    for a in range(n):
        for b in range(a + 1, n):
            x, y = pp[a], pp[b]
            if sez[x] != sez[y]:
                continue
            hx, hy = testa[x], testa[y]
            if hx['Q'] == hy['Q'] and hx['F'] == hy['F']:
                c = 'stesso foglio'
            elif hx['Q'] == hy['Q'] and hx['B'] == hy['B']:
                c = 'stesso bifoglio, fogli diversi'
            elif (seg.get(x) == y and hx['lato'] == 'v' and hy['lato'] == 'r') or (seg.get(y) == x and hy['lato'] == 'v' and hx['lato'] == 'r'):
                c = 'apertura'
            elif hx['Q'] == hy['Q']:
                c = 'stesso fascicolo, altro'
            else:
                c = 'altro fascicolo'
            classi[c].append((a, b))
    coppie = {c: (np.array([a for a, _ in v]), np.array([b for _, b in v])) for c, v in classi.items() if v}
    gruppi = defaultdict(list)
    for i, p in enumerate(pp):
        gruppi[sez[p]].append(i)

    def medie(pi):
        return {c: (float(J[pi[A], pi[B]].mean()), float(R[pi[A], pi[B]].mean())) for c, (A, B) in coppie.items()}
    vero = medie(np.arange(n))
    nul = defaultdict(list)
    for _ in range(PERM):
        pi = np.arange(n)
        for idx in gruppi.values():
            x = list(idx)
            rnd.shuffle(x)
            pi[idx] = x
        for c, v in medie(pi).items():
            nul[c].append(v)
    out = OrderedDict()
    for c in CLASSI:
        if c not in vero:
            continue
        r = OrderedDict([('coppie', len(classi[c]))])
        for k, nome in enumerate(('rare_condivise', 'ripresa')):
            m = statistics.mean(x[k] for x in nul[c])
            sd = statistics.pstdev(x[k] for x in nul[c])
            r[nome] = OrderedDict([('media', vero[c][k]), ('nullo', m), ('z', (vero[c][k] - m) / (sd or 1))])
        out[c] = r
    b = out.get('stesso bifoglio, fogli diversi')
    ap = out.get('apertura')

    def esito(k):
        if not b:
            return 'non calcolabile'
        z = b[k]['z']
        if z > 3 and (not ap or b[k]['media'] > ap[k]['media']):
            return 'il bifoglio è una sessione'
        return 'nessuna sessione di bifoglio' if z < 2 else 'incerto'
    res = OrderedDict([('pagine', n), ('classi', out), ('esito_rare', esito('rare_condivise')), ('esito_ripresa', esito('ripresa'))])
    json.dump(res, open(os.path.join(RISULTATI, 'e350_sessioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e350 — Il bifoglio come sessione di scrittura', '', 'Preregistrazione: `preregistrazioni/e350.md`. %d pagine, coppie nella stessa sezione.' % n, '',
          '| classe | coppie | rare condivise | nullo | z | ripresa | nullo | z |', '|---|---|---|---|---|---|---|---|']
    for c, r in out.items():
        md.append('| %s | %d | %.4f | %.4f | %.1f | %.4f | %.4f | %.1f |' % (c, r['coppie'], r['rare_condivise']['media'], r['rare_condivise']['nullo'], r['rare_condivise']['z'],
                                                                         r['ripresa']['media'], r['ripresa']['nullo'], r['ripresa']['z']))
    md += ['', 'Esito (rare): **%s**. Esito (ripresa): **%s**.' % (res['esito_rare'], res['esito_ripresa'])]
    open(os.path.join(RISULTATI, 'e350_sessioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
