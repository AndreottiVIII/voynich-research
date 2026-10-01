# -*- coding: utf-8 -*-
"""Esperimento 100: il Macer floridus in versi, cifrato in quattro modi (verboso, codice per parola, codice per sillaba,
Naibbe) mantenendo un verso per riga: proprieta' di riga e pagella.

Preregistrazione: preregistrazioni/e100.md. Scrive risultati/e100_macer_cifrato.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e48_composizione as e48
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e99_macer as e99
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 100
D = misure.divisore(misure.GLIFI_EVA)


def cifrature(caps, voy):
    rnd = random.Random(SEME)
    out = OrderedDict()
    tutte = [w for c in caps for ps in c for w in ps]
    # 1. verboso
    glifi = [g for g, _ in Counter(u for p in voy for u in D(p)).most_common()]
    h2_v = misure.condizionate(misure.sequenza(voy, D), k_max=2)['h2']
    lung_v = sum(len(D(p)) for p in voy) / len(voy)
    _, tabella, h2, lung, k = generatori.cerca_verboso(tutte, glifi, rnd, h2_v, lung_v)
    out['verboso'] = ([[[generatori.cifra_verboso([w], tabella)[0] for w in ps] for ps in c] for c in caps],
                      {'h2_prova': h2, 'lunghezza_prova': lung, 'lettere_a_un_segno': k})
    # 2. codice per parola
    modello = generatori.ModelloParole(voy, D)
    cod = generatori.codice_per_rango(tutte, voy, modello, random.Random(SEME))
    it = iter(cod)
    out['codice per parola'] = ([[[next(it) for _ in ps] for ps in c] for c in caps], {})
    # 3. codice per sillaba
    sill = [[[s for w in ps for s in generatori.sillabe(w)] for ps in c] for c in caps]
    tutte_s = [s for c in sill for ps in c for s in ps]
    cod_s = generatori.codice_per_rango(tutte_s, voy, modello, random.Random(SEME))
    it = iter(cod_s)
    out['codice per sillaba'] = ([[[next(it) for _ in ps] for ps in c] for c in sill], {'sillabe': len(tutte_s)})
    # 4. Naibbe, verso per verso
    tab = generatori.naibbe_tabelle(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'references', 'naibbe_tables.csv'))
    rnd_n = random.Random(SEME)
    pagine_n = []
    for c in caps:
        pag = []
        for ps in c:
            lettere = generatori.naibbe_pulisci(' '.join(ps))
            parole, _ = generatori.naibbe(lettere, tab, rnd_n)
            pag.append(parole)
        pagine_n.append(pag)
    out['Naibbe'] = (pagine_n, {'tabelle': 'references/naibbe_tables.csv'})
    return out


def riga(pagine):
    righe = [(k, j == 0, ps) for k, p in enumerate(pagine) for j, ps in enumerate(p) if ps]
    rnd = random.Random(SEME)
    d, a = e74.coppie(righe, D)
    x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
    b = e71.una(('x', [(ini, ps) for _, ini, ps in righe], 'eva'))[1]
    per = OrderedDict()
    for k, ini, ps in righe:
        per.setdefault(k, []).append((k, ini, ps[0]))
    s1 = e83.misura(per, 1, e83.primo_eva, random.Random(SEME))
    return OrderedDict([('legame_dentro', x['eccesso']), ('legame_dentro_z', x['z']),
                        ('R', y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None),
                        ('bordo_inizio', b['jsd_inizio']['rapporto']), ('bordo_fine', b['jsd_fine']['rapporto']), ('S1', s1['S'])])


def main():
    e71.RIMESCOLAMENTI = 100
    e83.PERMUTAZIONI = 300
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    caps = e99.capitoli()
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    finestre_v = e48.per_finestre(voy)
    import e49_composizione_giunture as e49
    e49.validazione = e78._validazione_corta
    ris = OrderedDict()
    for nome, (pagine, info) in cifrature(caps, voy).items():
        rg = riga(pagine)
        r = e61.scheda(pagine, D, voy, soglia_ab)
        n = sum(len(ps) for p in pagine for ps in p)
        vv = dict(v)
        vv['hapax_34000'] = finestre_v[max(k for k in finestre_v if k <= n)]['hapax']
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(r, vv))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= rg['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= rg['bordo_fine'] <= 2 * vb[1]
        r['esiti'] = esiti
        ris[nome] = OrderedDict([('info', info), ('parole', n), ('riga', rg), ('pagella', r)])
        print('%-20s %d/%d | R %s legame %.3f (z %.0f) bordo %.1f/%.1f S1 %.2f | h2 %.2f tipi %.3f uniche %.2f rip %.2f omog %.3f/%.3f forma %.2f | %s' % (
            nome, sum(esiti.values()), len(esiti), '%.2f' % rg['R'] if rg['R'] is not None else '-', rg['legame_dentro'],
            rg['legame_dentro_z'] or 0, rg['bordo_inizio'], rg['bordo_fine'], rg['S1'], r['h2'], r['tipi_su_parole'],
            r['hapax_34000'], r['identiche_vs_riga'], r['somiglianza_riga'], r['somiglianza_6_righe'], r.get('V8_forma', 0),
            ' '.join(p for p, x in esiti.items() if x)), flush=True)
    with open(os.path.join(RISULTATI, 'e100_macer_cifrato.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e100 — Un erbario in versi, cifrato', '',
           '*Macer floridus*, un verso per riga, un capitolo per pagina, cifrato in quattro modi. Pagella dell\'e61 + bordo di '
           'riga. Preregistrazione: `preregistrazioni/e100.md`.', '',
           '| cifratura | totale | R | bordo ini/fin | S(1) | ' + ' | '.join(props) + ' |', '|---|---|---|---|---|' + '---|' * len(props)]
    for nome, x in ris.items():
        r, rg = x['pagella'], x['riga']
        out.append('| %s | %d/%d | %s | %.1f / %.1f | %.2f | %s |' % (
            nome, sum(r['esiti'].values()), len(props), '%.2f' % rg['R'] if rg['R'] is not None else '–', rg['bordo_inizio'],
            rg['bordo_fine'], rg['S1'], ' | '.join(('✓ ' if r['esiti'][p] else '· ') + ('%.3g' % r[e61.VALORI[p]] if e61.VALORI.get(p) in r and isinstance(r[e61.VALORI[p]], (int, float)) else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e100_macer_cifrato.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
