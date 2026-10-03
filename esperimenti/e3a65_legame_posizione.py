# -*- coding: utf-8 -*-
"""Esperimento e3a65: legame dell'e3a14 (identita' della parola contro segno di bordo della vicina) con nulli che tengono
anche la posizione della coppia nella riga e/o il paragrafo.

Preregistrazione: preregistrazioni/e3a65.md. Scrive risultati/e3a65_legame_posizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e380_sandhi as e380
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NULLI = ('N0', 'N1', 'N2', 'N3')


def posizione(i, n):
    """Classe della coppia i (0-based) in una riga con n parole (n - 1 coppie)."""
    if n == 2:
        return 'sola'
    if i == 0:
        return 'prima'
    if i == n - 2:
        return 'ultima'
    return 'mezzo'


def eventi(unita, nullo):
    """unita: [(pagina, paragrafo, riga)]."""
    av, ind = [], []
    for pg, par, r in unita:
        for i, (a, b) in enumerate(zip(r, r[1:])):
            pos = posizione(i, len(r))
            base = {'N0': (pg,), 'N1': (pg, pos), 'N2': (par,), 'N3': (par, pos)}[nullo]
            av.append((base + (a[-1],), a, b[0]))
            ind.append((base + (b[0],), b, a[-1]))
    return av, ind


def misura(unita, nulli, rnd, perm):
    out = OrderedDict()
    for n in nulli:
        av, ind = eventi(unita, n)
        out[n] = OrderedDict([('avanti', e380.prova(av, rnd, perm)), ('indietro', e380.prova(ind, rnd, perm))])
    return out


def main():
    rnd = random.Random(3165)
    voy_pag = []
    k = 0
    for pg, pars in e341.pagine().items():
        uu = []
        for par in pars:
            k += 1
            for r in par:
                rr = [w for w in (tuple(D(x)) for x in r) if w]
                if len(rr) >= 2:
                    uu.append((pg, k, rr))
        if uu:
            voy_pag.append(uu)
    tutto = misura([u for p in voy_pag for u in p], NULLI, rnd, 1000)
    print('Voynich', json.dumps(tutto, default=float), flush=True)
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy_pag, len(voy_pag))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese += p
            n += sum(len(u[2]) for u in p)
        sub.append(misura(prese, NULLI, rnd, 100))
    med = OrderedDict((nl, OrderedDict((lato, statistics.median(s[nl][lato]['E'] for s in sub)) for lato in ('avanti', 'indietro'))) for nl in NULLI)
    print('Voynich 10.000', json.dumps(med), flush=True)
    sens = OrderedDict()
    for nome, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        unita = [(i // 25, i // 25, list(r)) for i, r in enumerate(righe) if len(r) >= 2]
        sens[nome.replace('.txt', '')] = misura(unita, ('N0', 'N1'), rnd, 100)
    lingue = OrderedDict()
    for nl in ('N0', 'N1'):
        lingue[nl] = OrderedDict()
        for lato in ('avanti', 'indietro'):
            vals = [x[nl][lato]['E'] for x in sens.values() if x[nl][lato]['eventi'] >= 5000]
            m = statistics.median(vals)
            lingue[nl][lato] = OrderedDict([('testi', len(vals)), ('mediana', m), ('rapporto_voynich', med[nl][lato] / m if m else None)])
    esiti = OrderedDict()
    for lato in ('avanti', 'indietro'):
        e0, e3, z3 = tutto['N0'][lato]['E'], tutto['N3'][lato]['E'], tutto['N3'][lato]['z']
        if e3 < 0.5 * e0 and z3 < 2:
            es = 'il resto viene da posizione e paragrafo'
        elif e3 > 2 / 3 * e0 and z3 > 3:
            es = 'resta un legame fra vicine'
        else:
            es = 'in parte'
        esiti[lato] = es
    out = OrderedDict([('Voynich', tutto), ('Voynich_10000_mediane', med), ('lingue', lingue), ('testi_sensati', sens), ('esiti', esiti)])
    print(json.dumps(lingue), json.dumps(esiti, ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a65_legame_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    desc = {'N0': '(pagina, bordo)', 'N1': '(pagina, bordo, posizione)', 'N2': '(paragrafo, bordo)', 'N3': '(paragrafo, bordo, posizione)'}
    md = ['# e3a65 — Il piccolo legame fra parole intere viene dalla posizione nella riga o dal lessico del paragrafo?', '', 'Preregistrazione: `preregistrazioni/e3a65.md`.', '',
          '| nullo | avanti E (z), tutto | indietro E (z), tutto | avanti E, 10.000 parole | indietro E, 10.000 parole | lingue avanti (mediana) | lingue indietro (mediana) |', '|---|---|---|---|---|---|---|']
    for nl in NULLI:
        t = tutto[nl]
        la = lingue.get(nl, {})
        md.append('| %s %s | %.4f (%.1f) | %.4f (%.1f) | %.4f | %.4f | %s | %s |' % (nl, desc[nl], t['avanti']['E'], t['avanti']['z'], t['indietro']['E'], t['indietro']['z'], med[nl]['avanti'], med[nl]['indietro'],
                                                                      '%.4f' % la['avanti']['mediana'] if la else '–', '%.4f' % la['indietro']['mediana'] if la else '–'))
    md += ['', 'Rapporto Voynich (10.000 parole) / mediana delle lingue con N1: avanti %.2f, indietro %.2f.' % (lingue['N1']['avanti']['rapporto_voynich'], lingue['N1']['indietro']['rapporto_voynich']),
           '', 'Esito avanti: **%s**. Esito indietro: **%s**.' % (esiti['avanti'], esiti['indietro'])]
    open(os.path.join(RISULTATI, 'e3a65_legame_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
