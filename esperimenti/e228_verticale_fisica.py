# -*- coding: utf-8 -*-
"""Esperimento 228: la somiglianza verticale (e58) segue la parola fisicamente sopra (centro del riquadro piu' vicino)
o la parola con lo stesso indice nella riga sopra?

Preregistrazione: preregistrazioni/e228.md. Scrive risultati/e228_verticale_fisica.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from difflib import SequenceMatcher

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e34_spazi_fisici as e34
import e146_deriva_preferenze as e146

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEME, INVERSIONI, QUOTA, MIN_CASI = 228, 10000, 0.05, 300


def righe_con_riquadri():
    """Per pagina: righe come liste di (parola, centro x o None), nell'ordine della ZL (allineamento come e166)."""
    righe = e146.righe_voynich()
    per = defaultdict(list)
    for k, (pag, _, ps) in enumerate(righe):
        per[pag].append(k)
    out = OrderedDict()
    for pag, ks in per.items():
        percorso = os.path.join(e34.RIQUADRI, pag + '.js')
        if not os.path.exists(percorso):
            continue
        d = json.load(open(percorso, encoding='utf-8'))
        voc = [v[0] for v in d[0]]
        vt = [voc[e[0]] for e in d[1]]
        cx = [e[1] + e[3] / 2 for e in d[1]]
        zt = [(k, j, w) for k in ks for j, w in enumerate(righe[k][2])]
        sm = SequenceMatcher(a=[e34.fondi(w) for w in vt], b=[e34.fondi(w) for _, _, w in zt], autojunk=False)
        centro = {}
        for i0, j0, n in sm.get_matching_blocks():
            for t in range(n):
                centro[(zt[j0 + t][0], zt[j0 + t][1])] = cx[i0 + t]
        out[pag] = [[(w, centro.get((k, j))) for j, w in enumerate(righe[k][2])] for k in ks]
    return out


def sim(a, b):
    return 1 - misure._dist_norm(tuple(D(a)), tuple(D(b)))


def coppie_di_righe(pagine):
    """(riga, riga sopra) consecutive nella stessa pagina."""
    return [(r, s) for rr in pagine.values() for s, r in zip(rr, rr[1:])]


def casi(coppie):
    """Per ogni parola interna con riquadro: (sim con P, sim con I, media sim con le altre interne della riga sopra)."""
    out = []
    for riga, sopra in coppie:
        si = sopra[1:-1]
        if len(si) < 2 or any(c is None or not trascrizione.pulita(w) for w, c in si):
            continue
        for j in range(1, len(riga) - 1):
            w, c = riga[j]
            if c is None or not trascrizione.pulita(w) or j - 1 >= len(si):
                continue
            ip = min(range(len(si)), key=lambda t: abs(si[t][1] - c))
            ii = j - 1
            if ip == ii:
                continue
            altre = [sim(w, si[t][0]) for t in range(len(si)) if t not in (ip, ii)]
            out.append((sim(w, si[ip][0]), sim(w, si[ii][0]), statistics.mean(altre) if altre else None))
    return out


def prova(cs, rnd):
    diff = [p - i for p, i, _ in cs]
    delta = statistics.mean(diff)
    nulli = []
    for _ in range(INVERSIONI):
        nulli.append(sum(x if rnd.random() < 0.5 else -x for x in diff) / len(diff))
    s = statistics.pstdev(nulli)
    p = (1 + sum(abs(x) >= abs(delta) for x in nulli)) / (INVERSIONI + 1)
    con_altre = [(a, b, m) for a, b, m in cs if m is not None]
    return OrderedDict([('casi', len(cs)), ('delta', delta), ('z', delta / s if s else None), ('p', p),
                        ('E_P', statistics.mean(a - m for a, _, m in con_altre) if con_altre else None),
                        ('E_I', statistics.mean(b - m for _, b, m in con_altre) if con_altre else None)])


def base_neutra(pagine, rnd):
    """Ogni riga si abbina a una riga sopra presa da un'altra pagina a caso (con i suoi riquadri)."""
    nomi = list(pagine)
    out = []
    for pag, rr in pagine.items():
        for r in rr[1:]:
            altra = rnd.choice([n for n in nomi if n != pag])
            out.append((list(r), rnd.choice(pagine[altra])))
    return out


def inietta(coppie, quale, unita, rnd):
    """Con probabilita' QUOTA una parola interna diventa una variante a una modifica della sua P o della sua I."""
    out = []
    for riga, sopra in coppie:
        si = sopra[1:-1]
        nuova = list(riga)
        if len(si) >= 2 and all(c is not None and trascrizione.pulita(w) for w, c in si):
            for j in range(1, len(riga) - 1):
                w, c = riga[j]
                if c is None or not trascrizione.pulita(w) or j - 1 >= len(si) or rnd.random() >= QUOTA:
                    continue
                t = min(range(len(si)), key=lambda t: abs(si[t][1] - c)) if quale == 'fisico' else j - 1
                u = list(D(si[t][0]))
                u[rnd.randrange(len(u))] = rnd.choice(unita)
                nuova[j] = (''.join(u), c)
        out.append((nuova, sopra))
    return out


def main():
    rnd = random.Random(SEME)
    pagine = righe_con_riquadri()
    unita = sorted({x for rr in pagine.values() for r in rr for w, _ in r if trascrizione.pulita(w) for x in D(w)})
    ris = OrderedDict()
    neutra = base_neutra(pagine, random.Random(SEME))
    for nome, cp in (('controllo nullo (base neutra)', neutra),
                     ('controllo fisico (5% di varianti di P)', inietta(neutra, 'fisico', unita, random.Random(SEME + 1))),
                     ('controllo indice (5% di varianti di I)', inietta(neutra, 'indice', unita, random.Random(SEME + 2))),
                     ('Voynich', coppie_di_righe(pagine))):
        ris[nome] = prova(casi(cp), rnd)
        r = ris[nome]
        print('%s: casi %d, delta %+.4f, z %.1f, p %.4f, E_P %.4f, E_I %.4f' % (nome, r['casi'], r['delta'], r['z'], r['p'], r['E_P'], r['E_I']), flush=True)
    n0, nf, ni, v = (ris[k] for k in ris)
    valido = nf['delta'] > 0 and nf['p'] < 0.01 and ni['delta'] < 0 and ni['p'] < 0.01 and n0['p'] > 0.05 and v['casi'] >= MIN_CASI
    esito = ('non valido' if not valido else 'copia a vista (fisica)' if v['delta'] > 0 and v['p'] < 0.01
             else 'colonne logiche (indice)' if v['delta'] < 0 and v['p'] < 0.01 else 'non distinguibile')
    ris['pagine'] = len(pagine)
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e228_verticale_fisica.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e228 — Copia verticale: posizione fisica o indice nella riga?', '',
          'Δ = somiglianza con la parola fisicamente sopra (P) meno somiglianza con quella di pari indice (I), sui casi in cui '
          'P e I differiscono; E = eccesso sulla media delle altre parole interne della riga sopra. %d pagine con riquadri. '
          'Preregistrazione: `preregistrazioni/e228.md`.' % len(pagine), '',
          '| testo | casi | Δ | z | p | E_P | E_I |', '|---|---|---|---|---|---|---|']
    for nome in list(ris)[:4]:
        r = ris[nome]
        md.append('| %s | %d | %+.4f | %.1f | %.4f | %.4f | %.4f |' % (nome, r['casi'], r['delta'], r['z'], r['p'], r['E_P'], r['E_I']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e228_verticale_fisica.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
