# -*- coding: utf-8 -*-
"""Esperimento 76: righe piene e chiuse? Riempimento (CV delle larghezze delle righe non finali di
paragrafo) e chiusura (R dell'e74) nella sezione delle ricette, con Apicio, voci indipendenti e il
generatore come confronto.

Preregistrazione: preregistrazioni/e76.md. Scrive risultati/e76_righe_piene.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 76
D = e71.D


def righe_sezione(sezione):
    """(pagina, inizio paragrafo, parole) della sezione."""
    return [(r.pagina, bool(r.inizio_par), list(r.parole))
            for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione=sezione) if r.parole]


def paragrafi(righe):
    out, cur, pag = [], [], None
    for p, inizio, ps in righe:
        if (inizio or p != pag) and cur:
            out.append(cur)
            cur = []
        cur.append(ps)
        pag = p
    if cur:
        out.append(cur)
    return out


def riempimento(righe, dividi):
    valori = []
    for par in paragrafi(righe):
        if len(par) < 3:
            continue
        larg = [sum(len(dividi(w)) for w in ps) + len(ps) - 1 for ps in par[:-1]]
        m = statistics.median(larg)
        valori.extend(x / m for x in larg)
    media = statistics.mean(valori)
    return OrderedDict([('righe', len(valori)), ('cv', statistics.pstdev(valori) / media),
                        ('corte', sum(x < 0.75 for x in valori) / len(valori))])


def a_capo_per_voce(voci, dividi, larghezza):
    out = []
    for k, voce in enumerate(voci):
        riga, usata, primo = [], 0, True
        for w in voce:
            l = len(dividi(w))
            if riga and usata + 1 + l > larghezza:
                out.append((k, primo, riga))
                primo, riga, usata = False, [], 0
            usata += (1 if riga else 0) + l
            riga.append(w)
        if riga:
            out.append((k, primo, riga))
    return out


def una(nome, righe, dividi):
    r = riempimento(righe, dividi)
    rnd = random.Random(SEME)
    dentro, a_capo = e74.coppie(righe, dividi)
    y = e74.eccesso(dentro, rnd)   # dentro la riga
    x = e74.eccesso(a_capo, rnd)   # attraverso l'a capo
    r['dentro'] = y
    r['a_capo'] = x
    r['R'] = x['eccesso'] / y['eccesso'] if y['eccesso'] > 0 else None
    print('%-36s righe %4d | CV %.3f corte %.1f%% | dentro %.4f (z %.0f) a capo %.4f (z %.1f) R %s' % (
        nome, r['righe'], r['cv'], 100 * r['corte'], y['eccesso'], y['z'] or 0, x['eccesso'], x['z'] or 0,
        '%.2f' % r['R'] if r['R'] is not None else '-'), flush=True)
    return r


def main():
    from e36_posizione_pagina import plinio
    from e65_aperture_ricette import paragrafi_apicio
    s = righe_sezione('S')
    larg_s = []
    for par in paragrafi(s):
        larg_s.extend(sum(len(D(w)) for w in ps) + len(ps) - 1 for ps in par[:-1])
    larghezza_s = statistics.median(larg_s)
    voy = [w for _, _, ps in s for w in ps if trascrizione.pulita(w)]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    ris = OrderedDict()
    ris['larghezza_mediana_S'] = larghezza_s
    ris['Voynich S'] = una('Voynich S', s, D)
    ris['Voynich H (descrittivo)'] = una('Voynich H (descrittivo)', righe_sezione('H'), D)
    apicio = paragrafi_apicio()
    media_a = sum(len(w) for v in apicio for w in v) / sum(len(v) for v in apicio)
    righe_a = a_capo_per_voce(apicio, e71.lettere, larghezza_s * (media_a + 1) / (media_voy + 1))
    ris['Apicio, una ricetta per paragrafo'] = una('Apicio, una ricetta per paragrafo', righe_a, e71.lettere)
    latino = [w for _, ps in plinio() for w in ps]
    rnd = random.Random(SEME)
    voci = []
    for i in range(4000):
        n = rnd.randint(3, 12)
        a = rnd.randrange(len(latino) - n)
        voci.append(latino[a:a + n])
    righe_v = [(i // 8, i % 8 == 0, v) for i, v in enumerate(voci)]
    ris['voci indipendenti (Plinio)'] = una('voci indipendenti (Plinio)', righe_v, e71.lettere)
    for seme in (19, 1, 2):
        rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_%d' % seme, 'generate', 'generated_text.txt'))
        nome = 'Timm e Schinner, seme %d' % seme
        ris[nome] = una(nome, [(None, i, ps) for i, ps in rr], D)
    with open(os.path.join(RISULTATI, 'e76_righe_piene.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e76 — Righe piene e chiuse? (sezione delle ricette)', '',
           'Riempimento: CV delle larghezze (segni + spazi) delle righe non finali, divise per la mediana del paragrafo; '
           '"corte" < 0,75. Chiusura: R = eccesso d\'informazione mutua attraverso l\'a capo / dentro la riga. '
           'Preregistrazione: `preregistrazioni/e76.md`.', '',
           '| testo | righe | CV | corte | dentro la riga | a capo | R |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if not isinstance(r, dict):
            continue
        out.append('| %s | %d | %.3f | %.1f%% | %.4f (z %.0f) | %.4f (z %.1f) | %s |' % (
            nome, r['righe'], r['cv'], 100 * r['corte'], r['dentro']['eccesso'], r['dentro']['z'] or 0,
            r['a_capo']['eccesso'], r['a_capo']['z'] or 0, '%.2f' % r['R'] if r['R'] is not None else '–'))
    with open(os.path.join(RISULTATI, 'e76_righe_piene.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
