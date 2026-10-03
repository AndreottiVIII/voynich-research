# -*- coding: utf-8 -*-
"""Esperimento 374: la prima e l'ultima parola della riga sono diverse dalle altre (primo e ultimo segno, lunghezza)
nel Voynich, nel gibberish scritto a mano (Gaskell e Bowern 2022), nei testi sensati e nel generatore di Timm e Schinner?

Preregistrazione: preregistrazioni/e374.md. Scrive risultati/e374_bordi_gibberish.json e .md.
"""
import json, math, os, random, re, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e337_posizione as e337

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)


def leggi_zip(nome, filtro, max_righe=None):
    out = OrderedDict()
    with zipfile.ZipFile(os.path.join(GB, nome)) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt') and filtro(n):
                righe = []
                for l in z.read(n).decode('utf-8', errors='ignore').splitlines():
                    ws = re.findall(r'[^\W\d_]+', l.lower())
                    if ws:
                        righe.append([tuple(w) for w in ws])
                    if max_righe and len(righe) >= max_righe:
                        break
                out[os.path.basename(n)] = righe
    return out


def voynich():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            ws = [w for w in ws if w]
            if ws:
                out.append(ws)
    return out


def jsd(a, b):
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb:
        return 0.0
    tot = 0.0
    for k in set(a) | set(b):
        p, q = a[k] / na, b[k] / nb
        m = (p + q) / 2
        if p:
            tot += p * math.log(p / m) / 2
        if q:
            tot += q * math.log(q / m) / 2
    return tot


def misure4(righe):
    f1, f2, mid1, mid2 = Counter(), Counter(), Counter(), Counter()
    l1 = l2 = lm = 0
    nm = 0
    for r in righe:
        f1[r[0][0]] += 1
        f2[r[-1][-1]] += 1
        l1 += len(r[0])
        l2 += len(r[-1])
        for w in r[1:-1]:
            mid1[w[0]] += 1
            mid2[w[-1]] += 1
            lm += len(w)
            nm += 1
    n = len(righe)
    return [jsd(f1, mid1), jsd(f2, mid2), l1 / n - lm / nm, l2 / n - lm / nm], (f1, f2, mid1, mid2)


def z_testo(righe, rnd, perm):
    righe = [r for r in righe if len(r) >= 3]
    vero, cont = misure4(righe)
    nul = [misure4([rnd.sample(r, len(r)) for r in righe])[0] for _ in range(perm)]
    zs = []
    for k in range(4):
        xs = [x[k] for x in nul]
        m, sd = statistics.mean(xs), statistics.pstdev(xs)
        zs.append((vero[k] - m) / sd if sd else 0.0)
    return vero, zs, cont


def eccessi(cont, k=3):
    f1, f2, mid1, mid2 = cont
    def top(a, b):
        na, nb = sum(a.values()), sum(b.values())
        r = sorted(((a[s] / na) / ((b[s] + 1) / (nb + 1)), s) for s in a if a[s] >= 5)
        return [''.join(s) if isinstance(s, tuple) else s for _, s in r[::-1][:k]]
    return top(f1, mid1), top(f2, mid2)


def main():
    rnd = random.Random(374)
    gib = leggi_zip('gibberish_transcriptions.zip', lambda n: True)
    sens = leggi_zip('meaningful.zip', lambda n: '/texts/' in n or n.startswith('texts/'), max_righe=60)
    voy = voynich()
    corpora = OrderedDict([('Voynich', voy), ('gibberish umano', [r for t in gib.values() for r in t]),
                           ('testi sensati', [r for t in sens.values() for r in t])])
    for cat in ('Historical', 'Modern', 'Conlangs'):
        corpora['testi sensati: %s' % cat] = [r for k, t in sens.items() if k.startswith(cat) for r in t]
    for s in (1, 19):
        corpora['Timm e Schinner, seme %d' % s] = [[tuple(D(w)) for w in r] for p in e337.pagine_ts(s) for r in p]
    per_autore = defaultdict(list)
    for k, t in gib.items():
        m = re.search(r'-\s*([A-Za-z]{2})', k)
        per_autore[m.group(1) if m else '?'] += t
    for a in sorted(per_autore):
        corpora['gibberish, autore %s' % a] = per_autore[a]
    n_gib = sum(len(r) >= 3 for r in corpora['gibberish umano'])
    ris = OrderedDict()
    for nome, righe in corpora.items():
        vero, zs, cont = z_testo(righe, rnd, 1000)
        e1, e2 = eccessi(cont)
        x = OrderedDict([('righe', sum(len(r) >= 3 for r in righe)), ('F1', vero[0]), ('F2', vero[1]), ('L1', vero[2]), ('L2', vero[3]),
                         ('z', zs), ('inizio_in_eccesso', e1), ('fine_in_eccesso', e2)])
        if nome in ('Voynich', 'testi sensati', 'Timm e Schinner, seme 1', 'Timm e Schinner, seme 19'):
            buone = [r for r in righe if len(r) >= 3]
            sub = [z_testo(rnd.sample(buone, n_gib), rnd, 100)[1] for _ in range(20)]
            x['z_a_parita'] = [statistics.median(s[k] for s in sub) for k in range(4)]
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    g = ris['gibberish umano']['z']
    v = ris['Voynich']['z_a_parita']
    if g[0] > 3 or g[1] > 3:
        esito = 'i bordi della riga ci sono anche nel gibberish umano'
    elif g[0] < 2 and g[1] < 2 and max(v[0], v[1]) > 3:
        esito = 'i bordi della riga sono propri del Voynich'
    else:
        esito = 'incerto'
    out = OrderedDict([('righe_gibberish', n_gib), ('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e374_bordi_gibberish.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e374 — I bordi della riga nel gibberish scritto a mano', '', 'Preregistrazione: `preregistrazioni/e374.md`. Righe con almeno 3 parole.', '',
          '| testo | righe | F1 (primo segno) | z | F2 (ultimo segno) | z | L1 | z | L2 | z | z a parità (F1, F2, L1, L2) | inizio in eccesso | fine in eccesso |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        zp = ', '.join('%.1f' % t for t in x['z_a_parita']) if 'z_a_parita' in x else ''
        md.append('| %s | %d | %.4f | %.1f | %.4f | %.1f | %+.2f | %.1f | %+.2f | %.1f | %s | %s | %s |' % (
            k, x['righe'], x['F1'], x['z'][0], x['F2'], x['z'][1], x['L1'], x['z'][2], x['L2'], x['z'][3], zp,
            ' '.join(x['inizio_in_eccesso']), ' '.join(x['fine_in_eccesso'])))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e374_bordi_gibberish.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
