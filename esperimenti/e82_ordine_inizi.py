# -*- coding: utf-8 -*-
"""Esperimento 82: i primi segni delle righe consecutive dipendono l'uno dall'altro (ordine, numerazione)?

Preregistrazione: preregistrazioni/e82.md. Scrive risultati/e82_ordine_inizi.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 82, 500
D = e71.D


def coppie(righe, posizione):
    """Per pagina: lista ordinata dei primi segni della parola in `posizione` (None se manca), con il flag
    d'inizio paragrafo. Le coppie si formano fra righe consecutive (nell'ordine reale o rimescolato)."""
    per = OrderedDict()
    for pag, inizio, ps in righe:
        x = None
        if len(ps) > posizione and trascrizione.pulita(ps[posizione]):
            x = D(ps[posizione])[0]
        per.setdefault(pag, []).append((inizio, x))
    return per


def accoppia(per, ordine=None):
    out = []
    for pag, rr in per.items():
        seq = rr if ordine is None else [rr[i] for i in ordine[pag]]
        for (inizio1, a), (inizio2, b) in zip(seq, seq[1:]):
            if a is not None and b is not None and not inizio1 and not inizio2:
                out.append((a, b))
    return out


def eccesso(per, rnd):
    """D-014: il nullo rimescola l'ordine delle righe dentro la pagina (una riga non si accoppia con se stessa).
    Le righe d'inizio paragrafo sono escluse da entrambi i lati, nel reale e nel nullo."""
    per = OrderedDict((p, rr) for p, rr in per.items())
    reale = accoppia(per)
    vera = misure.informazione_mutua(reale)
    nulli = []
    for _ in range(PERMUTAZIONI):
        ordine = {}
        for p, rr in per.items():
            idx = [i for i, (inizio, _) in enumerate(rr) if not inizio]
            rnd.shuffle(idx)
            ordine[p] = idx
        nulli.append(misure.informazione_mutua(accoppia(per, ordine)))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', len(reale)), ('eccesso', vera - m), ('z', (vera - m) / s if s else None)])


def main():
    import e73_bordo_interno as e73
    base = e73.testi()
    t = OrderedDict()
    t['Voynich'] = e74.righe_voynich()
    t['Voynich A'] = e74.righe_voynich('A')
    t['Voynich B'] = e74.righe_voynich('B')
    for s in (19, 1, 2):
        rr = base['Timm e Schinner, seme %d' % s][0]
        t['Timm e Schinner, seme %d' % s] = [(i // 29, inizio, ps) for i, (inizio, ps) in enumerate(rr)]
    rc = base['Plinio codificato, a capo'][0]
    marcatori = ('s', 'y', 'd')
    t['controllo positivo: marcatore a ciclo'] = [(i // 20, False, [marcatori[(i % 20) % 3] + ps[0]] + ps[1:]) for i, (_, ps) in enumerate(rc)]
    t['controllo negativo: senza marcatore'] = [(i // 20, False, ps) for i, (_, ps) in enumerate(rc)]
    ris = OrderedDict()
    for nome, righe in t.items():
        rnd = random.Random(SEME)
        prima = eccesso(coppie(righe, 0), rnd)
        seconda = eccesso(coppie(righe, 1), rnd)
        ris[nome] = OrderedDict([('prima_parola', prima), ('seconda_parola', seconda)])
        print('%-40s prima: n %5d eccesso %.4f (z %.1f) | seconda: n %5d eccesso %.4f (z %.1f)' % (
            nome, prima['n'], prima['eccesso'], prima['z'] or 0, seconda['n'], seconda['eccesso'], seconda['z'] or 0), flush=True)
    with open(os.path.join(RISULTATI, 'e82_ordine_inizi.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e82 — I segni d\'inizio riga seguono un ordine?', '',
           'Eccesso d\'informazione mutua fra il primo segno della prima (o seconda) parola di righe consecutive, contro %d '
           'permutazioni dentro la pagina. Preregistrazione: `preregistrazioni/e82.md`.' % PERMUTAZIONI, '',
           '| testo | prima parola: n | eccesso (z) | seconda parola: n | eccesso (z) |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        a, b = r['prima_parola'], r['seconda_parola']
        out.append('| %s | %d | %.4f (%.1f) | %d | %.4f (%.1f) |' % (nome, a['n'], a['eccesso'], a['z'] or 0, b['n'], b['eccesso'], b['z'] or 0))
    with open(os.path.join(RISULTATI, 'e82_ordine_inizi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
