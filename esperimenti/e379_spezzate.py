# -*- coding: utf-8 -*-
"""Esperimento 379: (b) le coppie parolina + parola (spazio sicuro o incerto) formano una parola del lessico piu' del
caso? nullo con scambi che conservano giuntura, lessico di pagina e posizione; (a) la misura S dell'e375 con gli spazi
incerti uniti.

Preregistrazione: preregistrazioni/e379.md. Scrive risultati/e379_spezzate.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e375_coppie as e375

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 200


def righe_con_separatori():
    """{pagina: [riga]}, riga = (parole come tuple di segni, separatori fra parole: '.' o ',')."""
    per = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        s = re.sub(r'<![^>]*>', '', r.grezza)
        s = s.replace('<%>', '').replace('<$>', '').replace('<->', '.').replace('<~>', '.')
        s = re.sub(r'<@[^>]*>', '', s)
        s = re.sub(r'<[^>]*>', '', s)
        s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
        s = s.replace('{', '').replace('}', '').replace("'", '')
        s = re.sub(r'@\d{3};', '*', s)
        pezzi = [p for p in re.split(r'([.,]+)', s) if p]
        ws, seps = [], []
        sep_prec = None
        for p in pezzi:
            if re.fullmatch(r'[.,]+', p):
                sep_prec = '.' if '.' in p else ','
                continue
            if not trascrizione.pulita(p):
                ws.append(None)
            else:
                ws.append(tuple(D(p)))
            if len(ws) > 1:
                seps.append(sep_prec or '.')
            sep_prec = None
        if ws:
            per.setdefault(r.pagina, []).append((ws, seps))
    return per


_UNITE = {}


def unisci(x, y):
    """Segni della parola unita, rifacendo la fusione dei composti attraverso il confine."""
    k = (x, y)
    if k not in _UNITE:
        _UNITE[k] = tuple(D(''.join(x) + ''.join(y)))
    return _UNITE[k]


def main():
    rnd = random.Random(379)
    per = righe_con_separatori()
    freq = Counter(w for p in per.values() for ws, _ in p for w in ws if w)
    lessico = {w for w, n in freq.items() if n >= 2}
    # posti per lo scambio: (pagina, riga, j) -> classe
    pagine = list(per)
    parole = {pg: [list(ws) for ws, _ in per[pg]] for pg in pagine}
    gruppi = {}
    for pg in pagine:
        g = defaultdict(list)
        for i, ws in enumerate(parole[pg]):
            n = len(ws)
            for j, w in enumerate(ws):
                if w:
                    pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                    g[(w[0], w[-1], pos)].append((i, j))
        gruppi[pg] = [v for v in g.values() if len(v) > 1]
    tipi_coppia = OrderedDict([('corta, spazio sicuro', lambda x, s: len(x) <= 2 and s == '.'),
                               ('corta, spazio incerto', lambda x, s: len(x) <= 2 and s == ','),
                               ('lunga (3+), spazio sicuro', lambda x, s: len(x) >= 3 and s == '.')])

    def quote(par):
        tot, si = Counter(), Counter()
        for pg in pagine:
            for (ws0, seps), ws in zip(per[pg], par[pg]):
                for j in range(len(ws) - 1):
                    x, y = ws[j], ws[j + 1]
                    if not x or not y:
                        continue
                    for k, f in tipi_coppia.items():
                        if f(x, seps[j]):
                            tot[k] += 1
                            si[k] += unisci(x, y) in lessico
        return {k: si[k] / tot[k] if tot[k] else 0.0 for k in tipi_coppia}, tot
    vero, tot = quote(parole)
    nul = defaultdict(list)
    for _ in range(PERM):
        par = {}
        for pg in pagine:
            q = [list(ws) for ws in parole[pg]]
            for posti in gruppi[pg]:
                ws = [parole[pg][i][j] for i, j in posti]
                rnd.shuffle(ws)
                for (i, j), w in zip(posti, ws):
                    q[i][j] = w
            par[pg] = q
        v, _ = quote(par)
        for k in v:
            nul[k].append(v[k])
    b = OrderedDict()
    for k in tipi_coppia:
        m, sd = statistics.mean(nul[k]), statistics.pstdev(nul[k])
        b[k] = OrderedDict([('coppie', tot[k]), ('quota', vero[k]), ('nullo', m), ('z', (vero[k] - m) / sd if sd else 0.0)])
        print(k, json.dumps(b[k], default=float), flush=True)
    unioni = Counter()
    for pg in pagine:
        for ws, seps in per[pg]:
            for j in range(len(ws) - 1):
                x, y = ws[j], ws[j + 1]
                if x and y and len(x) <= 2 and seps[j] == '.' and unisci(x, y) in lessico:
                    unioni['%s %s → %s (%d)' % (''.join(x), ''.join(y), ''.join(x + y), freq[unisci(x, y)])] += 1
    zb = b['corta, spazio sicuro']['z']
    esito_b = 'lo spazio a volte spezza le parole' if zb > 3 else ('no' if zb < 2 else 'incerto')
    # parte (a)
    per_a = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL', virgola_spazio=False)):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per_a.setdefault(r.pagina, []).append(ws)
    a = e375.Corpo(list(per_a.values())).prova(rnd)
    esito_a = 'l\'eccesso dell\'e375 viene dagli spazi incerti' if a['z'] < 2 else ('resta' if a['z'] > 3 else 'incerto')
    print('(a)', json.dumps(a, default=float), flush=True)
    out = OrderedDict([('parte_b', b), ('unioni_frequenti', unioni.most_common(15)), ('esito_b', esito_b), ('parte_a', a), ('esito_a', esito_a)])
    json.dump(out, open(os.path.join(RISULTATI, 'e379_spezzate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e379 — Parole spezzate dallo spazio?', '', 'Preregistrazione: `preregistrazioni/e379.md`.', '', '## (b) Parolina + parola = parola del lessico?', '',
          '| coppie | quante | quota con unione nel lessico | nullo | z |', '|---|---|---|---|---|']
    for k, x in b.items():
        md.append('| %s | %d | %.3f | %.3f | %.1f |' % (k, x['coppie'], x['quota'], x['nullo'], x['z']))
    md += ['', 'Unioni più frequenti con spazio sicuro (tra parentesi le occorrenze della parola unita): ' + '; '.join('%s: %d' % t for t in unioni.most_common(15)) + '.', '',
           'Esito (b): **%s**.' % esito_b, '', '## (a) La misura dell\'e375 con gli spazi incerti uniti', '',
           'S %d contro %.1f del nullo, R %.2f, z %.1f (con la virgola come spazio: R 1,03, z 2,0). Esito (a): **%s**.' % (a['S'], a['nullo'], a['R'], a['z'], esito_a)]
    open(os.path.join(RISULTATI, 'e379_spezzate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
