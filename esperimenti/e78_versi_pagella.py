# -*- coding: utf-8 -*-
"""Esperimento 78: i versi sanscriti con sandhi (un mezzo verso per riga) sulla pagella dell'e61 (per lettere).

Preregistrazione: preregistrazioni/e78.md. Scrive risultati/e78_versi_pagella.json e .md.
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e48_composizione as e48
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e77_versi_sandhi as e77
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def bordo(righe, quale):
    b = e71.una(('x', righe, quale))[1]
    return b['jsd_inizio']['rapporto'], b['jsd_fine']['rapporto']


def main():
    from e36_posizione_pagina import plinio
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    pv = pagine_voynich(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pv, D, voy, soglia_ab)
    finestre_v = e48.per_finestre(voy)
    vb = bordo(e71.righe_voynich(), 'eva')
    testi = OrderedDict()
    for nome, (f, sha) in e77.TESTI.items():
        versi = e77.mezzi_versi(f, sha)
        testi[nome + ', un mezzo verso per riga'] = [versi[i:i + e77.RIGHE_PAGINA] for i in range(0, len(versi), e77.RIGHE_PAGINA)]
    latino = [w for _, ps in plinio() for w in ps]
    rl = e71.a_capo(latino, e71.lettere, [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in e71.righe_voynich()],
                    sum(len(D(w)) for w in voy) / len(voy))
    testi['Plinio, a capo (controllo)'] = [[ps for _, ps in rl[i:i + 20]] for i in range(0, len(rl), 20)]
    ris = OrderedDict([('Voynich', v), ('Voynich_bordo', vb)])
    props = [p for p in e61.BANDE if p != 'forma parole'] + ['bordo di riga']
    tabella = []
    for nome, pagine in testi.items():
        r = e61.scheda(pagine, None, voy, soglia_ab)
        n = sum(len(rr) for p in pagine for rr in p)
        finestra = max(k for k in finestre_v if k <= n)
        vv = dict(v)
        vv['hapax_34000'] = finestre_v[finestra]['hapax']
        r['finestra_uniche'] = finestra
        r['Voynich_uniche_stessa_finestra'] = vv['hapax_34000']
        ini, fin = bordo([(i == 0, ps) for p in pagine for i, ps in enumerate(p)], 'lettere')
        r['bordo_inizio'], r['bordo_fine'] = ini, fin
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            if prop == 'forma parole':
                continue
            try:
                esiti[prop] = bool(f(r, vv))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= ini <= 2 * vb[0] and 0.5 * vb[1] <= fin <= 2 * vb[1]
        r['esiti'] = esiti
        ris[nome] = r
        tabella.append((nome, r, esiti))
        print('%-40s %d/%d | %s' % (nome, sum(esiti.values()), len(esiti), ' '.join(
            '%s%s' % ('✓' if esiti[p] else '·', p) for p in props)), flush=True)
        print('    h2 %.2f (V %.2f) spazio %.2f (%.2f) uniche %.2f (%.2f @%d) tipi %.3f (%.3f) rip %.2f (%.2f) omog %.3f/%.3f (%.3f/%.3f) legame %.3f (%.3f) unioni %s bordo %.1f/%.1f (%.1f/%.1f)' % (
            r['h2'], v['h2'], r['spazio_spiegato'], v['spazio_spiegato'], r['hapax_34000'], vv['hapax_34000'], finestra,
            r['tipi_su_parole'], v['tipi_su_parole'], r['identiche_vs_riga'], v['identiche_vs_riga'],
            r['somiglianza_riga'], r['somiglianza_6_righe'], v['somiglianza_riga'], v['somiglianza_6_righe'],
            r['confine'], v['confine'], '%.2f' % (r['unione_attestata'] / r['unione_caso']) if r.get('unione_caso') else '-',
            ini, fin, vb[0], vb[1]), flush=True)
    with open(os.path.join(RISULTATI, 'e78_versi_pagella.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    out = ['# e78 — I versi con sandhi sulla pagella intera', '',
           'Pagella dell\'e61 per lettere (senza la forma delle parole), più il bordo di riga (D-012). Parole uniche sulla '
           'finestra più grande disponibile, confrontate col Voynich sulla stessa finestra. Preregistrazione: '
           '`preregistrazioni/e78.md`.', '',
           '| testo | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, r, esiti in tabella:
        cella = lambda p: ('✓ ' if esiti[p] else '· ') + ('%.3g' % r[e61.VALORI[p]] if e61.VALORI.get(p) in r and isinstance(r[e61.VALORI[p]], (int, float)) else '')
        out.append('| %s | %d/%d | %s |' % (nome, sum(esiti.values()), len(esiti), ' | '.join(cella(p) for p in props)))
    out.append('| Voynich | | %s |' % ' | '.join('%.3g' % v[e61.VALORI[p]] if e61.VALORI.get(p) in v and isinstance(v[e61.VALORI[p]], (int, float)) else '' for p in props))
    with open(os.path.join(RISULTATI, 'e78_versi_pagella.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
