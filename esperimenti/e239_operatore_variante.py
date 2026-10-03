# -*- coding: utf-8 -*-
"""Esperimento 239 (descrittivo): l'operazione (sostituzione, inserzione, cancellazione, con posizione) che porta da una
parola gia' sulla pagina alla sua variante (classe V dell'e237), nel Voynich e nel generatore "copia e modifica".

Preregistrazione: preregistrazioni/e239.md. Scrive risultati/e239_operatore_variante.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e224_generatore_completo as e224
import e227d_prefissi_staccati as e227d
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e237_riuso_pagina as e237

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def posizione(i, n):
    return 'iniziale' if i == 0 else ('finale' if i == n - 1 else 'interna')


def operazione(s, u):
    if len(s) == len(u):
        i = next(t for t in range(len(s)) if s[t] != u[t])
        return 'sostituzione', '%s→%s %s' % (s[i], u[i], posizione(i, len(s)))
    if len(u) == len(s) + 1:
        i = next(t for t in range(len(u)) if u[:t] == s[:t] and u[t + 1:] == s[t:])
        return 'inserzione', '+%s %s' % (u[i], posizione(i, len(u)))
    i = next(t for t in range(len(s)) if s[:t] == u[:t] and s[t + 1:] == u[t:])
    return 'cancellazione', '−%s %s' % (s[i], posizione(i, len(s)))


def operatore(pagine):
    tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
    inventario = sorted({x for w in tutte for x in D(w)})
    tipi, ops = Counter(), Counter()
    for rr in pagine.values():
        sulla = OrderedDict()
        for k, r in enumerate(rr):
            for w in r:
                u = tuple(D(w))
                if sulla and u not in sulla:
                    vic = e237.vicini(u, inventario)
                    fonti = [x for x in sulla if x in vic]
                    if fonti:
                        m = max(sulla[x] for x in fonti)
                        s = next(x for x in fonti if sulla[x] == m)
                        t, o = operazione(s, u)
                        tipi[t] += 1
                        ops[o] += 1
                sulla[u] = k
                sulla.move_to_end(u)
    n = sum(ops.values())
    prime = ops.most_common(25)
    return OrderedDict([('varianti', n), ('tipi', OrderedDict((t, tipi[t] / n) for t in ('sostituzione', 'inserzione', 'cancellazione'))),
                        ('prime_25', [(o, c / n) for o, c in prime]), ('copertura_10', sum(c for _, c in prime[:10]) / n),
                        ('copertura_25', sum(c for _, c in prime) / n)])


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = OrderedDict((p, rr) for p, (_, rr) in e231.voynich().items())
    conf = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2)
    gp = e232.pagine_di(e233.genera(c, conf, 2))
    nomi = list(gp)
    gpag = OrderedDict(zip(nomi, e227d.trasforma([gp[p] for p in nomi], freq, e233.SIGMA_POST, e233.PI_POST, random.Random(2272 + 102))))
    ris = OrderedDict()
    for nome, pag in (('Voynich', vpag), ('copia e modifica (e233/e235), seme 2', gpag)):
        ris[nome] = operatore(pag)
        r = ris[nome]
        print(nome, r['varianti'], dict(r['tipi']), 'copertura 10 %.2f 25 %.2f' % (r['copertura_10'], r['copertura_25']), r['prime_25'][:10], flush=True)
    v = ris['Voynich']
    ris['lettura'] = 'concentrato' if v['copertura_25'] >= 0.6 else 'diffuso'
    json.dump(ris, open(os.path.join(RISULTATI, 'e239_operatore_variante.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e239 — Com\'è fatta una variante nel Voynich (descrittivo)', '',
          "Operazione dalla fonte più recente sulla pagina alla variante (classe V dell'e237), in unità di segni. Preregistrazione: "
          '`preregistrazioni/e239.md`.', '', '| testo | varianti | sostituzioni | inserzioni | cancellazioni | prime 10 | prime 25 |', '|---|---|---|---|---|---|---|']
    for nome in ('Voynich', 'copia e modifica (e233/e235), seme 2'):
        r = ris[nome]
        md.append('| %s | %d | %s | %.0f%% | %.0f%% |' % (nome, r['varianti'], ' | '.join('%.0f%%' % (100 * r['tipi'][t]) for t in r['tipi']),
                                                       100 * r['copertura_10'], 100 * r['copertura_25']))
    g = dict(ris['copia e modifica (e233/e235), seme 2']['prime_25'])
    md += ['', 'Le 25 operazioni più frequenti nel Voynich (fra parentesi la quota nel generatore):', '']
    md += ['%d. %s — %.1f%% (%.1f%%)' % (i + 1, o, 100 * q, 100 * g.get(o, 0)) for i, (o, q) in enumerate(v['prime_25'])]
    md += ['', 'Lettura: operatore **%s** (prime 25 operazioni: %.0f%% delle varianti).' % (ris['lettura'], 100 * v['copertura_25'])]
    open(os.path.join(RISULTATI, 'e239_operatore_variante.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
