# -*- coding: utf-8 -*-
"""Esperimento 101: codice per sillaba con omofoni, scelti a caso o fissati per pagina, sul Macer in versi.

Preregistrazione: preregistrazioni/e101.md. Scrive risultati/e101_sillabe_pagina.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e48_composizione as e48
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e78_versi_pagella as e78
import e99_macer as e99

RISULTATI = os.path.join(QUI, '..', 'risultati')
C = (40, 20, 10, 5)
MODI = ('casuale', 'per pagina')
SEMI = (1, 2, 3)
D = misure.divisore(misure.GLIFI_EVA)


def costruisci(sill, voy, c, modo, seme):
    rnd = random.Random(seme)
    freq = Counter(s for p in sill for r in p for s in r)
    ordine = [s for s, _ in freq.most_common()]
    disponibili = list(generatori.vocabolario_voynich(voy))
    usate = set(disponibili)
    modello = generatori.ModelloParole(voy, D)

    def nuova():
        if disponibili:
            return disponibili.pop(0)
        while True:
            w = modello.inventa(rnd)
            if w and w not in usate:
                usate.add(w)
                return w
    codici = {s: [nuova() for _ in range(1 + freq[s] // c)] for s in ordine}
    pagine = []
    for p in sill:
        fissati = {}
        pag = []
        for r in p:
            riga = []
            for s in r:
                if modo == 'per pagina':
                    if s not in fissati:
                        fissati[s] = rnd.choice(codici[s])
                    riga.append(fissati[s])
                else:
                    riga.append(rnd.choice(codici[s]))
            pag.append(riga)
        pagine.append(pag)
    return pagine


def una(args):
    c, modo, seme, sill, voy, soglia_ab, v, vb, finestre = args
    import e49_composizione_giunture as e49
    e49.validazione = e78._validazione_corta
    pagine = costruisci(sill, voy, c, modo, seme)
    r = e61.scheda(pagine, D, voy, soglia_ab)
    righe = [(k, j == 0, ps) for k, p in enumerate(pagine) for j, ps in enumerate(p) if ps]
    rnd = random.Random(seme)
    d, a = e74.coppie(righe, D)
    x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
    r['R_riga'] = y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None
    e71.RIMESCOLAMENTI = 50
    b = e71.una(('x', [(ini, ps) for _, ini, ps in righe], 'eva'))[1]
    r['bordo_inizio'], r['bordo_fine'] = b['jsd_inizio']['rapporto'], b['jsd_fine']['rapporto']
    return (c, modo, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    from e07_codifiche import pagine_voynich
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    finestre = e48.per_finestre(voy)
    caps = e99.capitoli()
    sill = [[[s for w in ps for s in generatori.sillabe(w)] for ps in cap] for cap in caps]
    n = sum(len(r) for p in sill for r in p)
    vv = dict(v)
    vv['hapax_34000'] = finestre[max(k for k in finestre if k <= n)]['hapax']
    lavori = [(c, m, s, sill, voy, soglia_ab, v, vb, finestre) for c in C for m in MODI for s in SEMI]
    per = {}
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(una, lavori):
            per.setdefault(k[:2], []).append(r)
    ris = OrderedDict([('parole', n)])
    props = list(e61.BANDE) + ['bordo di riga']
    for c in C:
        for m in MODI:
            gruppo = per[(c, m)]
            chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
            med = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
            esiti = OrderedDict()
            for prop, f in e61.BANDE.items():
                try:
                    esiti[prop] = bool(f(med, vv))
                except (KeyError, TypeError, ZeroDivisionError):
                    esiti[prop] = False
            esiti['bordo di riga'] = 0.5 * vb[0] <= med['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= med['bordo_fine'] <= 2 * vb[1]
            med['esiti'] = esiti
            nome = 'c %d, %s' % (c, m)
            ris[nome] = med
            print('%-20s %d/18 | h2 %.2f tipi %.3f uniche %.2f rip %.2f omog %.3f/%.3f legame %.3f R %s forma %.2f | %s' % (
                nome, sum(esiti.values()), med['h2'], med['tipi_su_parole'], med['hapax_34000'], med['identiche_vs_riga'],
                med['somiglianza_riga'], med['somiglianza_6_righe'], med['confine'],
                '%.2f' % med['R_riga'] if 'R_riga' in med else '-', med.get('V8_forma', 0), ' '.join(p for p, x in esiti.items() if x)), flush=True)
    with open(os.path.join(RISULTATI, 'e101_sillabe_pagina.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e101 — Codice per sillaba con convenzioni di pagina', '',
           '*Macer floridus* in versi, una parola per sillaba, 1 + ⌊f/c⌋ codici per sillaba, scelti a caso o fissati per '
           'pagina. Medie su tre semi. Preregistrazione: `preregistrazioni/e101.md`.', '',
           '| combinazione | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in ris.items():
        if not isinstance(m, dict):
            continue
        out.append('| %s | %d/18 | %s |' % (nome, sum(m['esiti'].values()), ' | '.join(
            ('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e101_sillabe_pagina.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
