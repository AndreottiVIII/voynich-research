# -*- coding: utf-8 -*-
"""Esperimento e3c61: la finestra (misura corretta dell'e3c48) nelle scelte fra simboli equivalenti (omofoni) del copista
del cifrario Copiale (manoscritto tedesco, c. 1760; trascrizione e decifrazione di Knight, Megyesi e Schaefer 2011, file
dell'Università di Stoccolma in dati/cache/copiale, non committati). La chiave simbolo → lettera si ricava allineando
riga per riga cifrato e chiaro (copiale_allinea.py). Per ogni lettera con almeno due omofoni frequenti: valore 1 se il
copista usa l'omofono più frequente, 0 se un altro; parola coperta = parola in chiaro con la posizione della lettera.

Preregistrazione: preregistrazioni/e3c61.md. Scrive risultati/e3c61_copiale_omofoni.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import copiale_allinea as ca
import e3c48_finestra_corretta as e3c48
import e3c50_scribi_menota as e3c50
import e3c52_eva_per_scelta as e3c52

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_SIMBOLO = 300
QUOTA = 0.7
MINIMO = 300


class Parola(tuple):
    """Lettere del chiaro; .simboli[i] = simbolo del cifrato che scrive la lettera i (None se scritta insieme ad altre)."""
    def __new__(cls, lettere, simboli):
        p = super().__new__(cls, lettere)
        p.simboli = simboli
        return p


def omofoni(righe, chiave):
    conta = Counter(s for _, ss, _ in righe for s in ss)
    per = defaultdict(list)
    for s, (e, q) in chiave.items():
        if len(e) == 1 and e.isalpha() and e.islower() and q >= QUOTA and conta[s] >= MIN_SIMBOLO and not ca.spazio(s):
            per[e].append(s)
    return OrderedDict((e, sorted(ss, key=lambda s: -conta[s])) for e, ss in sorted(per.items(), key=lambda z: -sum(conta[s] for s in z[1])) if len(ss) >= 2), conta


def pagine_parole(righe, allineamenti):
    """[(mano, [righe di Parola])] per pagina; si saltano le righe con il richiamo (#)."""
    per = OrderedDict()
    for (pag, simboli, unita), cp in zip(righe, allineamenti):
        if '#' in simboli:
            continue
        di = {}
        for i, j, e in cp:
            if len(e) == 1:
                di[j] = simboli[i]
        parole, lett, sim = [], [], []
        for j, u in enumerate(unita):
            if u == ' ':
                if lett:
                    parole.append(Parola(lett, sim))
                lett, sim = [], []
            else:
                lett.append(u)
                sim.append(di.get(j))
        if lett:
            parole.append(Parola(lett, sim))
        if parole:
            per.setdefault(pag, []).append(parole)
    return [('copista', rr) for rr in per.values()]


def classe(lettera, omo):
    primo, altri = omo[0], set(omo[1:])

    def f(w):
        for i, (c, s) in enumerate(zip(w, w.simboli)):
            if c == lettera and (s == primo or s in altri):
                return (1 if s == primo else 0, (''.join(w), i))
        return None
    return f


def minoritarie(pagine, f):
    xs = [f(w) for _, rr in pagine for r in rr if len(r) >= 6 for w in r[1:-1]]
    xs = [x for x in xs if x]
    per = defaultdict(set)
    for v, t in xs:
        per[t].add(v)
    mi = [v for v, t in xs if len(per[t]) == 2]
    return len(xs), min(sum(mi), len(mi) - sum(mi))


def qualita(righe, allineamenti, chiave):
    """Quota delle lettere del chiaro scritte da un simbolo la cui chiave principale è proprio quella lettera."""
    giuste = tot = 0
    for (_, simboli, unita), cp in zip(righe, allineamenti):
        for i, j, e in cp:
            if len(e) == 1 and e[0] != ' ' and len(e[0]) == 1 and e[0].isalpha():
                tot += 1
                giuste += chiave.get(simboli[i], ('', 0))[0] == e[0]
    return giuste / tot


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3361)
    righe, al, chiave = ca.carica()
    omo, conta = omofoni(righe, chiave)
    pagine = pagine_parole(righe, al)
    q = qualita(righe, al, chiave)
    print('qualità allineamento', q, 'omofoni', dict(omo), flush=True)
    ris = OrderedDict()
    cl_tutte = OrderedDict()
    ingresso = OrderedDict()
    for lettera, ss in omo.items():
        f = classe(lettera, ss)
        n, mino = minoritarie(pagine, f)
        ingresso[lettera] = OrderedDict([('parole', n), ('minoritarie_nei_misti', mino), ('entra', mino >= MINIMO)])
        if mino < MINIMO:
            continue
        cl_tutte[lettera] = f
        x = e3c48.misura(pagine, OrderedDict([(lettera, f)]), rng)
        x['vicine'], x['finestra'] = e3c50.giudizio(x)
        x['voce'] = e3c52.voce(x)
        x['omofoni'] = ['%s (%d)' % (s, conta[s]) for s in ss]
        ris[lettera] = x
        print(lettera, json.dumps(x, ensure_ascii=False), flush=True)
    x = e3c48.misura(pagine, cl_tutte, rng)
    x['voce'] = e3c52.voce(x)
    ris['tutte le lettere insieme'] = x
    print('tutte', json.dumps(x, ensure_ascii=False), flush=True)
    con = [k for k in cl_tutte if ris[k]['finestra']]
    esito = 'il copista ha la finestra' if len(con) >= 2 else ('nessuna scelta di omofoni ha la finestra' if not con else 'incerto')
    out = OrderedDict([('qualita_allineamento', q), ('omofoni', omo), ('ingresso', ingresso), ('misure', ris), ('con_finestra', con), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c61_copiale_omofoni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c61 — La finestra nelle scelte fra omofoni del copista del Copiale', '',
          'Preregistrazione: `preregistrazioni/e3c61.md`. Qualità dell\'allineamento: %.1f%% delle lettere scritte da un simbolo che vale proprio quella lettera. Voynich (e3c48 ZL): +0,131 / +0,093 / +0,086, r 0,68.' % (100 * q), '',
          '| lettera | omofoni (1 = il primo) | parole | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r | voce |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f | %s |' % (
            k, ', '.join(x.get('omofoni', [])), x['parole'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2],
            x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['voce']))
    md += ['', 'Esito: **%s**%s.' % (esito, (' (' + ', '.join(con) + ')') if con else ''), '',
           'Fonte: trascrizione e decifrazione del Copiale (K. Knight, B. Megyesi, C. Schaefer 2011), file dell\'Università di Stoccolma. I file non sono nel repository.']
    open(os.path.join(RISULTATI, 'e3c61_copiale_omofoni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
