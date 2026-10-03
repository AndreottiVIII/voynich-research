# -*- coding: utf-8 -*-
"""Esperimento 237 (descrittivo): profilo del riuso delle parole nella pagina. Ogni parola (tranne la prima della pagina)
e' ripetizione (R), variante a distanza 1 di una parola gia' sulla pagina (V), fra le 200 piu' frequenti del testo (F),
gia' scritta in pagine precedenti (A) o nuova (N). Voynich contro tre generatori.

Preregistrazione: preregistrazioni/e237.md. Scrive risultati/e237_riuso_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e236_due_fonti as e236
import e227d_prefissi_staccati as e227d

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
CLASSI = ('R', 'V', 'F', 'A', 'N')


def vicini(u, inventario):
    out = set()
    for i in range(len(u)):
        out.add(u[:i] + u[i + 1:])
        for x in inventario:
            if x != u[i]:
                out.add(u[:i] + (x,) + u[i + 1:])
    for i in range(len(u) + 1):
        for x in inventario:
            out.add(u[:i] + (x,) + u[i:])
    return out


def profilo(pagine):
    """pagine: OrderedDict nome -> righe di parole."""
    tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
    top = {w for w, _ in tutte.most_common(200)}
    inventario = sorted({x for w in tutte for x in D(w)})
    conta, dist = Counter(), {'R': [], 'V': []}
    visti_prima = set()
    for rr in pagine.values():
        sulla = {}                     # forma (tupla) -> ultima riga in cui compare sulla pagina
        primo = True
        for k, r in enumerate(rr):
            for w in r:
                u = tuple(D(w))
                if not primo:
                    if u in sulla:
                        c = 'R'
                        dist['R'].append(k - sulla[u])
                    else:
                        v = [sulla[x] for x in vicini(u, inventario) if x in sulla]
                        if v:
                            c = 'V'
                            dist['V'].append(k - max(v))
                        elif w in top:
                            c = 'F'
                        elif w in visti_prima:
                            c = 'A'
                        else:
                            c = 'N'
                    conta[c] += 1
                primo = False
                sulla[u] = k
        visti_prima |= {w for r in rr for w in r}
    n = sum(conta.values())
    out = OrderedDict((c, conta[c] / n) for c in CLASSI)
    out['distanza_R'] = statistics.median(dist['R']) if dist['R'] else None
    out['distanza_V'] = statistics.median(dist['V']) if dist['V'] else None
    out['parole'] = n
    return out


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    testi = OrderedDict([('Voynich', vpag)])
    conf = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2)
    gp = e232.pagine_di(e233.genera(c, conf, 2))
    nomi = list(gp)
    testi['copia e modifica (e233/e235), seme 2'] = OrderedDict(zip(nomi, e227d.trasforma(
        [gp[p] for p in nomi], freq, e233.SIGMA_POST, e233.PI_POST, random.Random(2272 + 102))))
    testi['due fonti (e236), seme 2'] = e232.pagine_di(e236.dopo(e236.genera(c, {'g': 0.9, 'rho': 0.9}, 2), freq, 102))
    testi['generatore e192, seme 1'] = OrderedDict((p, rr) for p, rr in e231.generatore_e192(1).items())
    ris = OrderedDict()
    for nome, pag in testi.items():
        ris[nome] = profilo(pag)
        print(nome, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in ris[nome].items()}, flush=True)
    v = ris['Voynich']
    scarti = OrderedDict()
    for nome in list(testi)[1:]:
        scarti[nome] = [cl for cl in CLASSI if v[cl] and abs(ris[nome][cl] - v[cl]) / v[cl] > 0.2]
    ris['scarti_oltre_20_percento'] = scarti
    json.dump(ris, open(os.path.join(RISULTATI, 'e237_riuso_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e237 — Come una pagina riusa le proprie parole (descrittivo)', '',
          'R ripetizione sulla pagina, V variante (distanza 1) di una parola già sulla pagina, F fra le 200 più frequenti del testo, A già '
          'scritta in pagine precedenti, N nuova; distanze mediane in righe dalla fonte sulla pagina. Preregistrazione: `preregistrazioni/e237.md`.', '',
          '| testo | R | V | F | A | N | distanza R | distanza V | scarti > 20% |', '|---|---|---|---|---|---|---|---|---|']
    for nome, r in list(ris.items())[:len(testi)]:
        md.append('| %s | %s | %s | %s | %s |' % (nome, ' | '.join('%.1f%%' % (100 * r[cl]) for cl in CLASSI),
                                                 r['distanza_R'], r['distanza_V'], ', '.join(scarti.get(nome, [])) or '—'))
    open(os.path.join(RISULTATI, 'e237_riuso_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
