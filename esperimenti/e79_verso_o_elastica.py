# -*- coding: utf-8 -*-
"""Esperimento 79: verso fisso o riga elastica? Legame attraverso l'a capo dopo righe corte e dopo righe piene.

Preregistrazione: preregistrazioni/e79.md. Scrive risultati/e79_verso_o_elastica.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e77_versi_sandhi as e77

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SOGLIA = 79, 0.75
D = e71.D


def righe_voynich(sezione=None):
    """(pagina, inizio paragrafo, fine paragrafo, parole)."""
    return [(r.pagina, bool(r.inizio_par), bool(r.fine_par), list(r.parole))
            for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione=sezione) if r.parole]


def larghezza(ps, dividi):
    return sum(len(dividi(w)) for w in ps) + len(ps) - 1


def gruppi(righe, dividi):
    """Coppie dentro la riga (tutte) e attraverso l'a capo, separate per riga L corta o piena."""
    pulita = trascrizione.pulita
    mediane = {}
    per_pagina = defaultdict(list)
    for pag, inizio, fine, ps in righe:
        if not fine:
            per_pagina[pag].append(larghezza(ps, dividi))
    mediane = {p: statistics.median(v) for p, v in per_pagina.items()}
    dentro, corte, piene = [], [], []
    for k, (pag, inizio, fine, ps) in enumerate(righe):
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pulita(a) and pulita(b):
                dentro.append((dividi(a)[-1], dividi(b)[0]))
        if k + 1 < len(righe) and not fine and pag in mediane:
            pag2, inizio2, _, ps2 = righe[k + 1]
            if pag2 == pag and not inizio2 and pulita(ps[-1]) and pulita(ps2[0]):
                coppia = (dividi(ps[-1])[-1], dividi(ps2[0])[0])
                (corte if larghezza(ps, dividi) < SOGLIA * mediane[pag] else piene).append(coppia)
    return dentro, corte, piene


def misura(nome, righe, dividi):
    rnd = random.Random(SEME)
    dentro, corte, piene = gruppi(righe, dividi)
    d = e74.eccesso(dentro, rnd)
    c = e74.eccesso(corte, rnd)
    p = e74.eccesso(piene, rnd)
    r = OrderedDict([('dentro', d), ('corte', c), ('piene', p),
                     ('R_corte', c['eccesso'] / d['eccesso']), ('R_piene', p['eccesso'] / d['eccesso'])])
    r['delta'] = r['R_corte'] - r['R_piene']
    print('%-44s dentro %.4f (z %.0f) | corte n %4d %.4f (z %.1f) R %.2f | piene n %4d %.4f (z %.1f) R %.2f | delta %.2f' % (
        nome, d['eccesso'], d['z'] or 0, c['n'], c['eccesso'], c['z'] or 0, r['R_corte'], p['n'], p['eccesso'],
        p['z'] or 0, r['R_piene'], r['delta']), flush=True)
    return r


def verso_limitato(versi, righe_h, media_voy):
    """Mezzi versi impaginati sulle larghezze delle righe dell'erbario: ogni mezzo verso comincia una riga;
    se non ci sta continua nella riga dopo. Un paragrafo per pagina del Voynich."""
    media = sum(len(w) for v in versi for w in v) / sum(len(v) for v in versi)
    scala = (media + 1) / (media_voy + 1)
    larghezze = [(pag, larghezza(ps, D) * scala) for pag, _, _, ps in righe_h]
    out, i, resto = [], 0, []
    for j, (pag, w) in enumerate(larghezze):
        if not resto:
            if i >= len(versi):
                break
            resto = list(versi[i])
            i += 1
        riga, usata = [resto.pop(0)], None
        usata = len(riga[0])
        while resto and usata + 1 + len(resto[0]) <= w:
            usata += 1 + len(resto[0])
            riga.append(resto.pop(0))
        primo = j == 0 or larghezze[j - 1][0] != pag
        ultimo = j + 1 == len(larghezze) or larghezze[j + 1][0] != pag
        out.append((pag, primo, ultimo, riga))
    return out


def main():
    rh = righe_voynich('H')
    voy = [w for _, _, _, ps in rh for w in ps if trascrizione.pulita(w)]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    f, sha = e77.TESTI['Manusmṛti']
    versi = e77.mezzi_versi(f, sha)
    ris = OrderedDict()
    ris['Voynich H'] = misura('Voynich H', rh, D)
    ris['Voynich, tutto (descrittivo)'] = misura('Voynich, tutto (descrittivo)', righe_voynich(), D)
    vl = verso_limitato(versi, rh, media_voy)
    ris['controllo: verso con spazio limitato'] = misura('controllo: verso con spazio limitato', vl, e71.lettere)
    libero = [(i // e77.RIGHE_PAGINA, i % e77.RIGHE_PAGINA == 0, (i + 1) % e77.RIGHE_PAGINA == 0, ps) for i, ps in enumerate(versi)]
    ris['controllo: verso senza limiti'] = misura('controllo: verso senza limiti', libero, e71.lettere)
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    ts = [(i // 29, inizio, i + 1 < len(ts) and ts[i + 1][0], ps) for i, (inizio, ps) in enumerate(ts)]
    ris['Timm e Schinner, seme 19'] = misura('Timm e Schinner, seme 19', ts, D)
    with open(os.path.join(RISULTATI, 'e79_verso_o_elastica.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e79 — Verso fisso o riga elastica?', '',
           'Legame attraverso l\'a capo dopo righe corte (< %.2f della mediana di pagina) e piene, diviso per il legame dentro '
           'la riga (R). Preregistrazione: `preregistrazioni/e79.md`.' % SOGLIA, '',
           '| testo | dentro la riga | dopo righe corte (n) | R corte | dopo righe piene (n) | R piene | Δ |',
           '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %.4f (z %.0f) | %.4f (%d) | %.2f | %.4f (%d) | %.2f | %.2f |' % (
            nome, r['dentro']['eccesso'], r['dentro']['z'] or 0, r['corte']['eccesso'], r['corte']['n'], r['R_corte'],
            r['piene']['eccesso'], r['piene']['n'], r['R_piene'], r['delta']))
    with open(os.path.join(RISULTATI, 'e79_verso_o_elastica.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
