# -*- coding: utf-8 -*-
"""Esperimento 228b: come l'e228 (parola fisicamente sopra contro parola di pari indice), ma confrontato con un nullo di
200 basi neutre (righe sopra prese da altre pagine), che assorbe la distorsione dovuta alla lunghezza delle parole.

Preregistrazione: preregistrazioni/e228b.md. Scrive risultati/e228b_verticale_nullo.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e228_verticale_fisica as e228

RISULTATI = os.path.join(QUI, '..', 'risultati')
BASI, SEME_BASI, SEME_CONTROLLI = 200, 228000, 228999


def misura(coppie):
    cs = e228.casi(coppie)
    con = [(a, b, m) for a, b, m in cs if m is not None]
    return OrderedDict([('casi', len(cs)), ('delta', statistics.mean(a - b for a, b, _ in cs)),
                        ('E_P', statistics.mean(a - m for a, _, m in con)), ('E_I', statistics.mean(b - m for _, b, m in con))])


def confronta(r, nullo):
    out = OrderedDict(r)
    for k in ('delta', 'E_P', 'E_I'):
        xs = [n[k] for n in nullo]
        m, s = statistics.mean(xs), statistics.pstdev(xs)
        out['nullo_' + k] = m
        out['z_' + k] = (r[k] - m) / s if s else None
    xs = [n['delta'] for n in nullo]
    m = statistics.mean(xs)
    out['p_delta'] = (1 + sum(abs(x - m) >= abs(r['delta'] - m) for x in xs)) / (len(xs) + 1)
    return out


def main():
    pagine = e228.righe_con_riquadri()
    unita = sorted({x for rr in pagine.values() for r in rr for w, _ in r if trascrizione.pulita(w) for x in e228.D(w)})
    nullo = []
    for i in range(BASI):
        nullo.append(misura(e228.base_neutra(pagine, random.Random(SEME_BASI + i))))
        if i % 20 == 19:
            print('basi neutre: %d' % (i + 1), flush=True)
    base = e228.base_neutra(pagine, random.Random(SEME_CONTROLLI))
    ris = OrderedDict()
    for nome, cp in (('controllo nullo (base neutra)', base),
                     ('controllo fisico (5% di varianti di P)', e228.inietta(base, 'fisico', unita, random.Random(SEME_CONTROLLI + 1))),
                     ('controllo indice (5% di varianti di I)', e228.inietta(base, 'indice', unita, random.Random(SEME_CONTROLLI + 2))),
                     ('Voynich', e228.coppie_di_righe(pagine))):
        ris[nome] = confronta(misura(cp), nullo)
        r = ris[nome]
        print('%s: casi %d, delta %+.4f (nullo %+.4f) z %.1f; z_P %.1f, z_I %.1f' % (
            nome, r['casi'], r['delta'], r['nullo_delta'], r['z_delta'], r['z_E_P'], r['z_E_I']), flush=True)
    n0, nf, ni, v = (ris[k] for k in list(ris))
    valido = nf['z_delta'] > 3 and ni['z_delta'] < -3 and abs(n0['z_delta']) < 2 and v['casi'] >= e228.MIN_CASI
    esito = ('non valido' if not valido else 'copia a vista (fisica)' if v['z_delta'] > 3
             else 'colonne logiche (indice)' if v['z_delta'] < -3 else 'non distinguibile')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e228b_verticale_nullo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e228b — Copia verticale: fisica o per indice, contro %d basi neutre' % BASI, '',
          'Δ = somiglianza con la parola fisicamente sopra (P) meno quella con la parola di pari indice (I); E = eccesso sulla '
          'media delle altre parole interne della riga sopra; z rispetto alle basi neutre (righe sopra da altre pagine). '
          'Preregistrazione: `preregistrazioni/e228b.md`.', '',
          '| testo | casi | Δ | Δ nullo | z_Δ | z_P | z_I |', '|---|---|---|---|---|---|---|']
    for nome in list(ris)[:4]:
        r = ris[nome]
        md.append('| %s | %d | %+.4f | %+.4f | %.1f | %.1f | %.1f |' % (nome, r['casi'], r['delta'], r['nullo_delta'], r['z_delta'],
                                                                      r['z_E_P'], r['z_E_I']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e228b_verticale_nullo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
