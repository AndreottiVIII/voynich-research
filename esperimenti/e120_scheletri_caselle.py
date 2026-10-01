# -*- coding: utf-8 -*-
"""Esperimento 120: riga per riga. Coppie di righe simili allineate (Needleman-Wunsch sulle parole), parti fisse e caselle,
legame con la pagina delle caselle rispetto alle parti fisse.

Preregistrazione: preregistrazioni/e120.md. Scrive risultati/e120_scheletri_caselle.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, BOOT = 120, 200, 50
MIN_PAROLE, ESCLUSE, CANDIDATE, GAP, SOGLIA = 5, 20, 5, -0.3, 0.5
D = misure.divisore(misure.GLIFI_EVA)


def sim(a, b, cache):
    k = (a, b) if a <= b else (b, a)
    v = cache.get(k)
    if v is None:
        v = 1.0 if a == b else 1 - misure._dist_norm(a, b)
        cache[k] = v
    return v


def allinea(x, y, ux, uy, cache):
    n, m = len(x), len(y)
    S = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        S[i][0] = i * GAP
    for j in range(1, m + 1):
        S[0][j] = j * GAP
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            S[i][j] = max(S[i - 1][j - 1] + sim(ux[i - 1], uy[j - 1], cache), S[i - 1][j] + GAP, S[i][j - 1] + GAP)
    # risalita
    i, j, coppie = n, m, []
    while i > 0 and j > 0:
        if S[i][j] == S[i - 1][j - 1] + sim(ux[i - 1], uy[j - 1], cache):
            coppie.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif S[i][j] == S[i - 1][j] + GAP:
            coppie.append((i - 1, None))
            i -= 1
        else:
            coppie.append((None, j - 1))
            j -= 1
    while i > 0:
        coppie.append((i - 1, None))
        i -= 1
    while j > 0:
        coppie.append((None, j - 1))
        j -= 1
    return S[n][m] / max(n, m), coppie[::-1]


def analizza(righe, dividi):
    """righe: (pagina, parole). Restituisce coppie simili e, per ogni riga, posizioni fisse/caselle."""
    righe = [(p, ps) for p, ps in righe if len(ps) >= MIN_PAROLE and all(trascrizione.pulita(w) for w in ps)]
    unita = [[tuple(dividi(w)) for w in ps] for _, ps in righe]
    freq = Counter(w for _, ps in righe for w in ps)
    escluse = {w for w, _ in freq.most_common(ESCLUSE)}
    indice = defaultdict(set)
    for k, (_, ps) in enumerate(righe):
        for w in set(ps) - escluse:
            indice[w].add(k)
    cache = {}
    ruolo = defaultdict(dict)        # riga -> posizione -> 'fissa' / 'casella'
    simili, stessa_pagina = set(), 0
    for k, (p, ps) in enumerate(righe):
        comuni = Counter()
        for w in set(ps) - escluse:
            for h in indice[w]:
                if h != k:
                    comuni[h] += 1
        for h, c in comuni.most_common(CANDIDATE):
            if c < 2:
                break
            punt, coppie = allinea(ps, righe[h][1], unita[k], unita[h], cache)
            if punt < SOGLIA:
                continue
            fisse = [(i, j) for i, j in coppie if i is not None and j is not None and sim(unita[k][i], unita[h][j], cache) >= 0.8]
            if len(fisse) < 3:
                continue
            simili.add(k)
            stessa_pagina += righe[h][0] == p
            for i, j in coppie:
                if i is None:
                    continue
                s = sim(unita[k][i], unita[h][j], cache) if j is not None else 0.0
                r = 'fissa' if s >= 0.8 else 'casella' if s < 0.5 else None
                if r and ruolo[k].get(i) != 'fissa':
                    ruolo[k][i] = r
    return righe, ruolo, simili, stessa_pagina


def legame(righe, ruolo, chi, rnd, rimescolamenti=RIMESCOLAMENTI):
    """Quota di parole (nel ruolo `chi`) il cui tipo compare in un'altra riga della stessa pagina, divisa per l'attesa
    con le righe rimescolate fra le pagine."""
    def quota(assegnazione):
        per_pag = defaultdict(Counter)
        for k, p in enumerate(assegnazione):
            per_pag[p].update(set(righe[k][1]))
        num = den = 0
        for k, pos in ruolo.items():
            p = assegnazione[k]
            for i, r in pos.items():
                if r != chi:
                    continue
                w = righe[k][1][i]
                den += 1
                num += per_pag[p][w] - (1 if w in righe[k][1] else 0) > 0
        return num / den if den else None
    pag = [p for p, _ in righe]
    reale = quota(pag)
    nulli = []
    for _ in range(rimescolamenti):
        q = pag[:]
        rnd.shuffle(q)
        nulli.append(quota(q))
    return reale / statistics.mean(nulli) if reale is not None else None


def una(nome, righe, dividi):
    rr, ruolo, simili, stessa = analizza(righe, dividi)
    rnd = random.Random(SEME)
    lc = legame(rr, ruolo, 'casella', rnd)
    lf = legame(rr, ruolo, 'fissa', rnd)
    # bootstrap per pagine dell'indice
    pagine = sorted({p for p, _ in rr}, key=str)
    per_pag = defaultdict(list)
    for k, (p, _) in enumerate(rr):
        per_pag[p].append(k)
    rb = random.Random(SEME + 1)
    boot = []
    for _ in range(BOOT):
        scelte = [pagine[rb.randrange(len(pagine))] for _ in pagine]
        nuove, ruolo_n, mappa = [], {}, {}
        for t, p in enumerate(scelte):
            for k in per_pag[p]:
                mappa[len(nuove)] = k
                nuove.append(('%s#%d' % (p, t), rr[k][1]))
        for nk, k in mappa.items():
            if k in ruolo:
                ruolo_n[nk] = ruolo[k]
        a = legame(nuove, ruolo_n, 'casella', random.Random(SEME), 50)
        b = legame(nuove, ruolo_n, 'fissa', random.Random(SEME), 50)
        if a and b:
            boot.append(a / b)
    boot.sort()
    n_c = sum(1 for pos in ruolo.values() for r in pos.values() if r == 'casella')
    n_f = sum(1 for pos in ruolo.values() for r in pos.values() if r == 'fissa')
    out = OrderedDict([('righe', len(rr)), ('righe_con_simile', len(simili)), ('quota_con_simile', len(simili) / len(rr)),
                       ('coppie_nella_stessa_pagina', stessa), ('parole_casella', n_c), ('parole_fisse', n_f),
                       ('legame_caselle', lc), ('legame_fisse', lf), ('indice', lc / lf if lc and lf else None),
                       ('ic', (boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]) if boot else None)])
    print('%-26s righe %5d con simile %.3f | caselle %5d fisse %5d | legame caselle %.2f fisse %.2f | indice %s %s' % (
        nome, out['righe'], out['quota_con_simile'], n_c, n_f, lc or 0, lf or 0, '%.2f' % out['indice'] if out['indice'] else '-',
        out['ic']), flush=True)
    return out, rr, ruolo


def main():
    import e99_macer as e99
    import e76_righe_piene as e76
    from e65_aperture_ricette import paragrafi_apicio
    t = OrderedDict()
    t['Voynich'] = ([(r.pagina, list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole], D)
    api = paragrafi_apicio()
    ra = e76.a_capo_per_voce(api, e71.lettere, 40)
    t['Apicio'] = ([(k, ps) for k, _, ps in ra], e71.lettere)
    t['Macer'] = ([(k, ps) for k, c in enumerate(e99.capitoli()) for ps in c], e71.lettere)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    t['Timm e Schinner'] = ([(i // 29, ps) for i, (_, ps) in enumerate(ts)], D)
    ris = OrderedDict()
    esempi = {}
    for nome, (rr, dv) in t.items():
        out, righe, ruolo = una(nome, rr, dv)
        ris[nome] = out
        if nome == 'Voynich':
            es = []
            for k in list(ruolo)[:40]:
                pos = ruolo[k]
                es.append(' '.join(('[%s]' % w if pos.get(i) == 'casella' else w) for i, w in enumerate(righe[k][1])) + '  (%s)' % righe[k][0])
            esempi['Voynich'] = es[:15]
    validita = any((ris[n]['indice'] or 0) > 1.2 for n in ('Apicio', 'Macer'))
    v = ris['Voynich']
    if v['indice'] and v['indice'] > 1.2 and v['ic'] and v['ic'][0] > 1:
        lettura = 'caselle di contenuto'
    elif v['indice'] and 0.9 <= v['indice'] <= 1.1:
        lettura = 'nessuna differenza'
    else:
        lettura = 'indeciso'
    ris['valido'], ris['lettura'], ris['esempi'] = validita, lettura, esempi
    print('metodo valido:', validita, '| lettura:', lettura)
    for e in esempi.get('Voynich', [])[:10]:
        print('   ', e)
    with open(os.path.join(RISULTATI, 'e120_scheletri_caselle.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e120 — Riga per riga: scheletri e caselle', '', 'Preregistrazione: `preregistrazioni/e120.md`.', '',
           '| testo | righe | con una riga simile | parole casella / fisse | legame caselle | legame fisse | indice (IC) |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'righe' in r:
            out.append('| %s | %d | %.1f%% | %d / %d | %.2f | %.2f | %s %s |' % (nome, r['righe'], 100 * r['quota_con_simile'], r['parole_casella'],
                                                                            r['parole_fisse'], r['legame_caselle'] or 0, r['legame_fisse'] or 0,
                                                                            '%.2f' % r['indice'] if r['indice'] else '–', r['ic']))
    out += ['', 'Metodo valido: **%s**. Lettura: **%s**.' % ('sì' if validita else 'no', lettura), '', 'Esempi (Voynich, caselle fra parentesi quadre):', '']
    out += ['    ' + e for e in esempi.get('Voynich', [])]
    with open(os.path.join(RISULTATI, 'e120_scheletri_caselle.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
