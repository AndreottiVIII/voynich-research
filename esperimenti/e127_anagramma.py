# -*- coding: utf-8 -*-
"""Esperimento 127: lettere in ordine fisso dentro la parola (anagramma)? Parte 1: coerenza d'ordine dei segni e
anagrammi nel Voynich, nei generatori e nelle lingue. Parte 2: latino in segni del Voynich, ordinato e no, con la
pagella.

Preregistrazione: preregistrazioni/e127.md. Scrive risultati/e127_anagramma.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e17_ricottura as e17
import e47_vocabolario as e47
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e99_macer as e99
import e106_procedimento_versi as e106
import e110_alternanza as e110
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, GUASTO = 127, 0.03
D = misure.divisore(misure.GLIFI_EVA)


# ---------------------------------------------------------------- parte 1

def coerenza(parole_unita):
    n = defaultdict(lambda: [0, 0])
    for u in parole_unita:
        for i in range(len(u)):
            for j in range(i + 1, len(u)):
                a, b = u[i], u[j]
                if a == b:
                    continue
                if a < b:
                    n[(a, b)][0] += 1
                else:
                    n[(b, a)][1] += 1
    tot = sum(x + y for x, y in n.values())
    return sum(max(x, y) for x, y in n.values()) / tot if tot else None


def anagrammi(parole_unita):
    tipi = {tuple(u) for u in parole_unita if len(set(u)) >= 2}
    per = defaultdict(set)
    for t in tipi:
        per[tuple(sorted(t))].add(t)
    return sum(len(per[tuple(sorted(t))]) > 1 for t in tipi) / len(tipi) if tipi else None


def chiave_ordine(voy_unita):
    pos = defaultdict(list)
    for u in voy_unita:
        if len(u) >= 2:
            for i, g in enumerate(u):
                pos[g].append(i / (len(u) - 1))
    return {g: sum(v) / len(v) for g, v in pos.items()}


def guasta(parole_unita, rnd):
    out = []
    for u in parole_unita:
        u = list(u)
        if len(u) >= 2 and rnd.random() < GUASTO:
            i = rnd.randrange(len(u) - 1)
            u[i], u[i + 1] = u[i + 1], u[i]
        out.append(u)
    return out


def parte1(voy_unita, chiave):
    t = OrderedDict()
    for q in ('ZL', 'IT'):
        t['Voynich ' + q] = [D(w) for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi(q))) if trascrizione.pulita(w)]
    for s in (19, 1, 2):
        t['Timm e Schinner, seme %d' % s] = [D(w) for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt')) for w in ps]
    for k, nome in (('Latin', 'latina'), ('Italian', 'italiana'), ('Hungarian', 'ungherese'), ('Turkish', 'turca')):
        ps = lingue.parole(k)[:35000]
        t['Bibbia ' + nome] = [list(w) for w in e17.pulisci(ps, e17.alfabeto(ps))]
    lat = t['Bibbia latina']
    t['controllo: latino ordinato, %d%% guastato' % int(100 * GUASTO)] = guasta([sorted(u) for u in lat], random.Random(SEME))
    out = OrderedDict()
    for nome, pu in t.items():
        out[nome] = OrderedDict([('parole', len(pu)), ('coerenza', coerenza(pu)), ('anagrammi', anagrammi(pu))])
        print('%-36s parole %6d | coerenza d\'ordine %.4f | tipi con anagramma %.3f' % (nome, len(pu), out[nome]['coerenza'], out[nome]['anagrammi']), flush=True)
    return out


# ---------------------------------------------------------------- parte 2

def corrispondenza(testo_parole, voy_unita):
    lett = Counter(c for w in testo_parole for c in w)
    segni = [g for g, _ in Counter(g for u in voy_unita for g in u).most_common() if g not in ('c', 'h')]
    return {l: segni[k] for k, (l, _) in enumerate(lett.most_common())}


def in_segni(righe, mappa, chiave, ordina):
    out = []
    for ini, ps in righe:
        nuova = []
        for w in ps:
            u = [mappa[c] for c in w]
            if ordina:
                u = sorted(u, key=lambda g: (chiave.get(g, 0.5), g))
            nuova.append(''.join(u))
        out.append((ini, nuova))
    return out


def una(args):
    nome, righe, voy, soglia_ab, vv, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    r = e106.misura(righe, voy, soglia_ab, vv, vb)
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    r['totale'] = sum(r['esiti'].values())
    return nome, r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    voy_unita = [D(w) for w in voy if trascrizione.pulita(w)]
    chiave = chiave_ordine(voy_unita)
    ris = OrderedDict([('chiave_ordine', OrderedDict(sorted(chiave.items(), key=lambda kv: kv[1])))])
    ris['parte1'] = p1 = parte1(voy_unita, chiave)
    # parte 2
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    finestre = e47.per_finestre(voy)
    caps = e99.capitoli()
    macer = [(j == 0, ps) for c in caps for j, ps in enumerate(c)]
    bib = lingue.parole('Latin')[:35000]
    bib = e17.pulisci(bib, e17.alfabeto(bib))
    bibbia = [(k % 8 == 0, bib[i:i + 9]) for k, i in enumerate(range(0, len(bib), 9))]
    lavori = []
    for nome_t, righe in (('Macer', macer), ('Bibbia latina', bibbia)):
        mappa = corrispondenza([w for _, ps in righe for w in ps], voy_unita)
        n = sum(len(ps) for _, ps in righe)
        vv = dict(v)
        vv['hapax_34000'] = finestre[max(k for k in finestre if k <= n)]['hapax']
        for ordina in (True, False):
            lavori.append(('%s, %s' % (nome_t, 'ordinato' if ordina else 'non ordinato'), in_segni(righe, mappa, chiave, ordina), voy, soglia_ab, vv, vb))
    p2 = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, lavori):
            p2[nome] = r
            print('%-28s %d/18 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | h2 %.2f tipi %.3f uniche %.2f | %s' % (
                nome, r['totale'], r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'], r['e94_pos2'], r['A'],
                r['h2'], r['tipi_su_parole'], r['hapax_34000'], ' '.join(p for p, x in r['esiti'].items() if x)), flush=True)
    ris['parte2'] = p2
    c = lambda n: p1[n]['coerenza']
    guasto = c('controllo: latino ordinato, %d%% guastato' % int(100 * GUASTO))
    stretto_escluso = c('Voynich ZL') < guasto and c('Voynich IT') < guasto
    lingue_max = max(c(n) for n in p1 if n.startswith('Bibbia'))
    parziale = min(c('Voynich ZL'), c('Voynich IT')) >= lingue_max + 0.05
    promettenti = [t for t in ('Macer', 'Bibbia latina') if p2[t + ', ordinato']['totale'] >= 12 and p2[t + ', ordinato']['totale'] >= p2[t + ', non ordinato']['totale'] + 3]
    ris['esiti'] = OrderedDict([('ordine_stretto_escluso', stretto_escluso), ('ordine_parziale', parziale), ('promettenti', promettenti)])
    print('ordine stretto escluso', stretto_escluso, '| ordine parziale (piu rigido delle lingue)', parziale, '| promettenti', promettenti)
    with open(os.path.join(RISULTATI, 'e127_anagramma.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e127 — Lettere in ordine fisso dentro la parola?', '', 'Preregistrazione: `preregistrazioni/e127.md`.', '', '## Parte 1', '',
           '| testo | parole | coerenza d\'ordine | tipi con anagramma |', '|---|---|---|---|']
    for nome, r in p1.items():
        out.append('| %s | %d | %.4f | %.3f |' % (nome, r['parole'], r['coerenza'], r['anagrammi']))
    props = list(e61.BANDE) + ['bordo di riga']
    out += ['', '## Parte 2', '', '| testo | pagella | R | S(1) | copia 1ª / 2ª | e94 | A |', '|---|---|---|---|---|---|---|']
    for nome, r in p2.items():
        out.append('| %s | %d/18 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f |' % (nome, r['totale'], r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'], r['e94_pos2'], r['A']))
    out += ['', '| testo | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, r in p2.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if r['esiti'][p] else '· ') + ('%.3g' % r[e61.VALORI[p]] if e61.VALORI.get(p) in r else '') for p in props)))
    out += ['', 'Ordine stretto escluso: **%s**. Ordine più rigido delle lingue: **%s**. Versioni ordinate promettenti: **%s**.' % (
        'sì' if stretto_escluso else 'no', 'sì' if parziale else 'no', ', '.join(promettenti) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e127_anagramma.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
