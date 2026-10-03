# -*- coding: utf-8 -*-
"""Esperimento 375: coppie di parole vicine (diverse, non varianti) che tornano su piu' pagine, contro un nullo che scambia
le parole con lo stesso primo segno, ultimo segno e posizione nella riga dentro la pagina (giunture e lessico di pagina
intatti). Voynich, testi sensati e gibberish di Gaskell e Bowern, Timm e Schinner.

Preregistrazione: preregistrazioni/e375.md. Scrive risultati/e375_coppie.json e .md.
"""
import json, os, random, re, statistics, sys, zipfile
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e337_posizione as e337

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 200


def testi_zip(nome, filtro):
    out = OrderedDict()
    with zipfile.ZipFile(os.path.join(GB, nome)) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt') and filtro(n):
                righe = []
                for l in z.read(n).decode('utf-8', errors='ignore').splitlines():
                    ws = [tuple(w) for w in re.findall(r'[^\W\d_]+', l.lower())]
                    if ws:
                        righe.append(ws)
                out[os.path.basename(n)] = righe
    return out


def a_pagine(testi, quota=None, alt=25):
    pagine = []
    for righe in testi:
        prese, n = [], 0
        for r in righe:
            if quota is not None and n >= quota:
                break
            prese.append(r)
            n += len(r)
        pagine += [prese[i:i + alt] for i in range(0, len(prese), alt)]
    return [p for p in pagine if p]


def voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
            ws = [w for w in ws if w]
            if ws:
                per.setdefault(r.pagina, []).append(ws)
    return list(per.values())


def simili(tipi):
    """{tipo: insieme dei tipi a distanza <= 1}, con chiavi jolly e cancellazione."""
    jolly, canc, piano = defaultdict(set), defaultdict(set), {}
    for w in tipi:
        piano[w] = w
        for i in range(len(w)):
            jolly[w[:i] + ('*',) + w[i + 1:]].add(w)
            canc[w[:i] + w[i + 1:]].add(w)
    out = {}
    for w in tipi:
        s = set(canc.get(w, ()))
        for i in range(len(w)):
            s |= jolly[w[:i] + ('*',) + w[i + 1:]]
            if w[:i] + w[i + 1:] in piano:
                s.add(w[:i] + w[i + 1:])
        s.add(w)
        out[w] = s
    return out


class Corpo:
    def __init__(self, pagine):
        self.pagine = pagine
        self.sim = simili({w for p in pagine for r in p for w in r})
        self.gruppi = []    # per pagina: liste di posti (riga, j) con la stessa classe
        for p in pagine:
            g = defaultdict(list)
            for i, r in enumerate(p):
                for j, w in enumerate(r):
                    pos = 0 if j == 0 else (2 if j == len(r) - 1 else 1)
                    g[(w[0], w[-1], pos)].append((i, j))
            self.gruppi.append([v for v in g.values() if len(v) > 1])

    def coppie_per_pagina(self, pagine):
        cont = Counter()
        for p in pagine:
            s = set()
            for r in p:
                for a, b in zip(r, r[1:]):
                    if b not in self.sim[a]:
                        s.add((a, b))
            cont.update(s)
        return cont

    def scambia(self, rnd):
        out = []
        for p, gr in zip(self.pagine, self.gruppi):
            q = [list(r) for r in p]
            for posti in gr:
                ws = [p[i][j] for i, j in posti]
                rnd.shuffle(ws)
                for (i, j), w in zip(posti, ws):
                    q[i][j] = w
            out.append(q)
        return out

    def prova(self, rnd, perm=PERM, dettaglio=False):
        vero = self.coppie_per_pagina(self.pagine)
        S = sum(1 for v in vero.values() if v >= 2)
        nul, somma = [], Counter()
        for _ in range(perm):
            c = self.coppie_per_pagina(self.scambia(rnd))
            nul.append(sum(1 for v in c.values() if v >= 2))
            if dettaglio:
                somma.update(c)
        m, sd = statistics.mean(nul), statistics.pstdev(nul)
        out = OrderedDict([('pagine', len(self.pagine)), ('parole', sum(len(r) for p in self.pagine for r in p)), ('S', S), ('nullo', m),
                           ('R', S / m if m else None), ('z', (S - m) / sd if sd else 0.0)])
        if dettaglio:
            ecc = sorted(((vero[k] - somma[k] / perm, k) for k in vero), reverse=True)[:15]
            out['coppie_in_eccesso'] = [['%s %s' % ('.'.join(a), '.'.join(b)), vero[(a, b)], round(somma[(a, b)] / perm, 2)] for _, (a, b) in ecc]
        return out


def main():
    rnd = random.Random(375)
    voy = voynich()
    n_voy = sum(len(r) for p in voy for r in p)
    sens = testi_zip('meaningful.zip', lambda n: '/texts/' in n or n.startswith('texts/'))
    gib = testi_zip('gibberish_transcriptions.zip', lambda n: True)
    corpi = OrderedDict([('Voynich', voy)])
    for cat in ('Historical', 'Modern', 'Conlangs'):
        tt = [t for k, t in sens.items() if k.startswith(cat)]
        corpi['testi sensati: %s' % cat] = a_pagine(tt, quota=n_voy / len(tt))
    corpi['gibberish umano'] = a_pagine(list(gib.values()))
    corpi['Timm e Schinner, seme 1'] = [[[tuple(D(w)) for w in r] for r in p] for p in e337.pagine_ts(1)]
    ris = OrderedDict()
    for nome, pag in corpi.items():
        ris[nome] = Corpo(pag).prova(rnd, dettaglio=(nome == 'Voynich'))
        print(nome, json.dumps(ris[nome], ensure_ascii=False, default=float), flush=True)
    n_gib = ris['gibberish umano']['parole']
    sub = []
    for _ in range(20):
        ordine = rnd.sample(range(len(voy)), len(voy))
        prese, n = [], 0
        for i in ordine:
            if n >= n_gib:
                break
            prese.append(voy[i])
            n += sum(len(r) for r in voy[i])
        sub.append(Corpo(prese).prova(rnd, perm=100))
    ris['Voynich a parità col gibberish'] = OrderedDict([('R_mediana', statistics.median(x['R'] for x in sub)), ('z_mediana', statistics.median(x['z'] for x in sub))])
    print(json.dumps(ris['Voynich a parità col gibberish'], default=float), flush=True)
    V = ris['Voynich']
    sensati = [ris[k] for k in ris if k.startswith('testi sensati')]
    controllo = all(x['z'] > 3 for x in sensati)
    if not controllo:
        esito = 'la misura non funziona (controllo positivo fallito)'
    elif V['z'] < 2:
        esito = 'nessuna preferenza oltre la giuntura'
    elif V['z'] > 3:
        esito = 'preferenze oltre la giuntura, ' + ('forti come una lingua' if V['R'] >= 0.5 * min(x['R'] for x in sensati) else 'deboli')
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('controllo_positivo', controllo), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e375_coppie.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e375 — Le parole scelgono le vicine oltre la giuntura?', '', 'Preregistrazione: `preregistrazioni/e375.md`. S = tipi di coppia vicina (parole diverse, non varianti) presenti su almeno 2 pagine; nullo: scambi dentro la pagina fra parole con lo stesso primo segno, ultimo segno e posizione nella riga.', '',
          '| testo | pagine | parole | S | nullo | R | z |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if 'S' in x:
            md.append('| %s | %d | %d | %d | %.1f | %.2f | %.1f |' % (k, x['pagine'], x['parole'], x['S'], x['nullo'], x['R'], x['z']))
    P = ris['Voynich a parità col gibberish']
    md += ['', 'Voynich a parità di parole col gibberish (mediana di 20 sottoinsiemi): R %.2f, z %.1f.' % (P['R_mediana'], P['z_mediana']), '',
           'Coppie del Voynich più in eccesso (pagine osservate, attese):', '']
    md += ['- %s: %d contro %.1f' % tuple(c) for c in V['coppie_in_eccesso']]
    md += ['', 'Controllo positivo (testi sensati z > 3): %s.' % ('superato' if controllo else 'fallito'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e375_coppie.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
