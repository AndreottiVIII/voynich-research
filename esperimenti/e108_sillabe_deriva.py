# -*- coding: utf-8 -*-
"""Esperimento 108: codice per sillaba sul Macer in versi, con grafia che deriva: ogni occorrenza parte dall'ultima
grafia usata per quella sillaba (ripristino alla base con probabilita' r) e riceve Poisson(mu) modifiche.

Preregistrazione: preregistrazioni/e108.md. Scrive risultati/e108_sillabe_deriva.json e .md.
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
import e78_versi_pagella as e78
import e99_macer as e99
import e104_sillabe_varianti as e104

RISULTATI = os.path.join(QUI, '..', 'risultati')
MU = (0.1, 0.2, 0.4)
R = (0.0, 0.05)
SEMI = (1, 2, 3)
D = misure.divisore(misure.GLIFI_EVA)
_MOD = None


def costruisci(sill, voy, mod, mu, r, seme):
    rnd = random.Random(seme)
    freq = Counter(s for p in sill for rr in p for s in rr)
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
    base = {s: tuple(D(nuova())) for s, _ in freq.most_common()}
    ultima = {}
    pagine = []
    for p in sill:
        pag = []
        for rr in p:
            riga = []
            for s in rr:
                u = base[s] if (s not in ultima or rnd.random() < r) else ultima[s]
                for _ in range(generatori.poisson(rnd, mu)):
                    v = mod.modifica(u, rnd)
                    if mod.valida(v):
                        u = v
                ultima[s] = u
                riga.append(''.join(u))
            pag.append(riga)
        pagine.append(pag)
    return pagine


def una(args):
    global _MOD
    mu, r, seme, sill, voy, soglia_ab = args
    import e49_composizione_giunture as e49
    e49.validazione = e78._validazione_corta
    if _MOD is None:
        _MOD = generatori.Modifiche(voy, D)
    pagine = costruisci(sill, voy, _MOD, mu, r, seme)
    res = e61.scheda(pagine, D, voy, soglia_ab)
    righe = [(j == 0, ps) for p in pagine for j, ps in enumerate(p) if ps]
    e71.RIMESCOLAMENTI = 50
    b = e71.una(('x', righe, 'eva'))[1]
    res['bordo_inizio'], res['bordo_fine'] = b['jsd_inizio']['rapporto'], b['jsd_fine']['rapporto']
    return (mu, r, seme), res


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
    n = sum(len(x) for p in sill for x in p)
    vv = dict(v)
    vv['hapax_34000'] = finestre[max(k for k in finestre if k <= n)]['hapax']
    per = {}
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, res in pool.imap(una, [(mu, r, s, sill, voy, soglia_ab) for mu in MU for r in R for s in SEMI]):
            per.setdefault(k[:2], []).append(res)
    ris = OrderedDict([('parole', n)])
    props = list(e61.BANDE) + ['bordo di riga']
    for mu in MU:
        for r in R:
            gruppo = per[(mu, r)]
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
            nome = 'mu %.1f, r %.2f' % (mu, r)
            ris[nome] = med
            print('%-16s %d/18 | h2 %.2f tipi %.3f uniche %.2f rip %.2f omog %.3f/%.3f deriva %.3f legame %.3f forma %.2f | %s' % (
                nome, sum(esiti.values()), med['h2'], med['tipi_su_parole'], med['hapax_34000'], med['identiche_vs_riga'],
                med['somiglianza_riga'], med['somiglianza_6_righe'], med['V2_ricambio_k1_meno_k20'], med['confine'],
                med.get('V8_forma', 0), ' '.join(p for p, x in esiti.items() if x)), flush=True)
    with open(os.path.join(RISULTATI, 'e108_sillabe_deriva.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e108 — Sillabe con grafia che deriva', '',
           '*Macer* in versi, una parola per sillaba; ogni occorrenza parte dall\'ultima grafia della sillaba (ripristino r) '
           'con Poisson(μ) modifiche. Medie su tre semi. Preregistrazione: `preregistrazioni/e108.md`.', '',
           '| combinazione | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in ris.items():
        if not nome.startswith('mu'):
            continue
        out.append('| %s | %d/18 | %s |' % (nome, sum(m['esiti'].values()), ' | '.join(
            ('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e108_sillabe_deriva.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
