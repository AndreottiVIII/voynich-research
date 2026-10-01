# -*- coding: utf-8 -*-
"""Esperimento 61 (riepilogo, non un test): la pagella. Tutte le proprieta' misurate finora, per
ogni famiglia di modelli, confrontate con il Voynich con bande di tolleranza.

Le bande sono scelte DOPO aver visto i risultati degli esperimenti precedenti: servono a leggere
il quadro d'insieme, non a decidere un'ipotesi. Scrive risultati/e61_pagella.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
import e46_codice_accorto as e46
import e52_codice_accorto_vero as e52
import e53_scissione as e53
import e55_forma_parole as e55
import e58_parola_sopra as e58
import e60_formule as e60
from e07_codifiche import pagine_voynich
from e30_elenchi_medievali import OCR, pulisci_ocr
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
C = e22.LAVORO


def verticale(pagine, dividi):
    """Rapporto dell'e58 (parole interne, posizione assoluta), senza rimescolamenti."""
    coppie = []
    for p in pagine:
        p = [[tuple(dividi(w)) if dividi else tuple(w) for w in r][1:-1] for r in p]
        coppie += [(b, a) for a, b in zip(p, p[1:]) if len(a) >= 2 and len(b) >= 2]
    return e58.statistica(e58.matrici(coppie), e58.indici(coppie, False))


def misure_lettere(pagine):
    """Le stesse misure per testi in lettere latine (senza fusione dei segni del Voynich)."""
    import e48_composizione as e48
    import e49_composizione_giunture as e49
    r = dict(e48.misura(pagine, None))
    r.update(e49.validazione(pagine))
    parole = [w for p in pagine for rr in p for w in rr]
    lung = [len(w) for w in parole]
    r['lung_media_segni'] = float(np.mean(lung))
    r['lung_dev_segni'] = float(np.std(lung))
    a, b = [], []
    for p in pagine:
        for rr in p:
            L = [len(w) for w in rr]
            a += L[:-1]
            b += L[1:]
    r['V6_autocorrelazione_lunghezze'] = float(np.corrcoef(a, b)[0, 1])
    cc = np.array(sorted(Counter(parole).values(), reverse=True)[:1000], float)
    r['V7_zipf'] = float(np.polyfit(np.log(np.arange(1, len(cc) + 1)), np.log(cc), 1)[0])
    return r


def scheda(pagine, dividi, voy_parole, soglia_ab):
    r = dict(misure_lettere(pagine)) if dividi is None else e53.misura(pagine)
    if dividi is not None:
        parole = [w for p in pagine for rr in p for w in rr]
        d = e55.distanze(parole, voy_parole)
        r['V8_forma'] = max(d[n] / soglia_ab[n] for n in e55.POS)
    r['verticale'] = verticale(pagine, dividi)
    r['formule_terne'] = e60.misura(pagine)[3]['eccesso_lontano']
    return r


BANDE = OrderedDict([
    ('h2', lambda r, v: abs(r['h2'] - v['h2']) <= 0.15),
    ('spazio', lambda r, v: abs(r['spazio_spiegato'] - v['spazio_spiegato']) <= 0.08),
    ('uniche', lambda r, v: abs(r['hapax_34000'] - v['hapax_34000']) <= 0.08),
    ('tipi', lambda r, v: abs(r['tipi_su_parole'] - v['tipi_su_parole']) <= 0.04),
    ('ripetizione', lambda r, v: abs(r['identiche_vs_riga'] - v['identiche_vs_riga']) <= 0.2),
    ('omogeneità', lambda r, v: abs(r['somiglianza_riga'] - v['somiglianza_riga']) <= 0.008),
    ('gradiente', lambda r, v: r['somiglianza_riga'] > 0 and 0.7 <= r['somiglianza_6_righe'] / r['somiglianza_riga'] <= 0.97),
    ('legame', lambda r, v: abs(r['confine'] - v['confine']) <= 0.05),
    ('unioni', lambda r, v: 1.5 <= r['unione_attestata'] / r['unione_caso'] <= 2.5),
    ('curva piatta', lambda r, v: r['hapax_1000'] - r['hapax_34000'] <= 0.10),
    ('deriva', lambda r, v: r['V2_ricambio_k1_meno_k20'] >= 0.05),
    ('profilo pagina', lambda r, v: r['V3_R'] is not None and 0.8 <= r['V3_R'] <= 1.25
     and 0.5 * v['V3_quota_media'] <= r['V3_quota_media'] <= 1.5 * v['V3_quota_media']),
    ('lunghezze vicine', lambda r, v: r['V6_autocorrelazione_lunghezze'] >= 0.08),
    ('Zipf', lambda r, v: abs(r['V7_zipf'] - v['V7_zipf']) <= 0.10),
    ('forma parole', lambda r, v: r.get('V8_forma') is not None and r['V8_forma'] <= 1.0),
    ('verticale', lambda r, v: r['verticale'] >= 1.015),
    ('formule', lambda r, v: bool(r['formule_terne']) and 0.5 * v['formule_terne'] <= r['formule_terne'] <= 1.5 * v['formule_terne']),
])
VALORI = {'h2': 'h2', 'spazio': 'spazio_spiegato', 'uniche': 'hapax_34000', 'tipi': 'tipi_su_parole',
          'ripetizione': 'identiche_vs_riga', 'omogeneità': 'somiglianza_riga', 'legame': 'confine',
          'deriva': 'V2_ricambio_k1_meno_k20', 'lunghezze vicine': 'V6_autocorrelazione_lunghezze',
          'Zipf': 'V7_zipf', 'verticale': 'verticale', 'formule': 'formule_terne', 'forma parole': 'V8_forma',
          'profilo pagina': 'V3_R'}


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    va = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A'))
    vb = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B'))
    soglia_ab = e55.distanze(va, vb)
    modello = generatori.ModelloParole(voy, D)
    latino = [w for _, ps in plinio() for w in ps]
    testi = OrderedDict()
    pv = pagine_voynich(corrente)
    testi['Voynich'] = (pv, D)
    testi['Bibbia latina (lingua)'] = (misure.pagine_finte(lingue.parole('Latin')[:35000]), None)
    testi['Plinio 20-27 (lingua, tecnico)'] = (misure.pagine_finte(latino), None)
    f, sha, a, b = OCR['Alphita (glossario, XIII sec.)']
    testi['Alphita (elenco)'] = (misure.pagine_finte(pulisci_ocr(f, sha, a, b)[0][:35000]), None)
    testi['codice parola per parola (Plinio)'] = (misure.pagine_finte(
        generatori.codice_per_rango(latino, voy, modello, random.Random(61))), D)
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    testi['Naibbe (cifrario)'] = (misure.pagine_finte(naibbe[:35000]), D)
    struttura = [[len(r) for r in p] for p in pv]
    codice = generatori.codice_per_rango(latino, voy, modello, random.Random(52))
    base = {}
    for w, c in zip(latino, codice):
        base.setdefault(w, c)
    forme = e52.forme_vere(base, voy, D)
    giunture = e46.tabella_giunture([r for p in pv for r in p], D)
    testi['codice accorto (e52)'] = (e46.scrivi(struttura, latino, forme, giunture, 20, 1.5, 0, random.Random(52)), D)
    testi['Timm e Schinner (seme 19)'] = (e58.da_file(os.path.join(C, 'seme_19', 'generate', 'generated_text.txt')), D)
    testi['+ giunture (e23, seme 19)'] = (e58.da_file(os.path.join(C, 'giunture', 'forza_3_seme_19', 'generate',
                                                                   'generated_text.txt')), D)
    testi['modello e51 (seme 19)'] = (e58.da_file(os.path.join(C, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19',
                                                               'generate', 'generated_text.txt')), D)
    base53 = e58.da_file(os.path.join(C, 'recenza_novita', 'e53_finali_0_seme_19', 'generate', 'generated_text.txt'))
    testi['modello e53, d 0,06 (seme 19)'] = (e53.scindi(base53, 0.06, e53.giunture_morbide(), random.Random(72)), D)
    ris = OrderedDict()
    for nome, (pagine, dividi) in testi.items():
        ris[nome] = scheda(pagine, dividi, voy, soglia_ab)
        print('fatto', nome, flush=True)
    v = ris['Voynich']
    nomi = [n for n in ris if n != 'Voynich']
    righe = ['# e61 — Pagella: tutte le proprietà, tutte le famiglie di modelli', '',
             '**Riepilogo, non un test**: le bande di tolleranza sono state scelte dopo aver visto i risultati. '
             '✓ = nella banda del Voynich, · = fuori. I testi in lettere latine non hanno la misura della forma '
             'delle parole.', '',
             '| proprietà | Voynich | ' + ' | '.join(nomi) + ' |', '|---|---|' + '---|' * len(nomi)]
    punti = {n: 0 for n in nomi}
    for prop, f in BANDE.items():
        celle = []
        for n in nomi:
            r = ris[n]
            try:
                ok = bool(f(r, v))
            except (KeyError, TypeError, ZeroDivisionError):
                ok = False
            punti[n] += ok
            x = r.get(VALORI.get(prop, ''))
            celle.append(('✓ ' if ok else '· ') + ('%.3g' % x if isinstance(x, (int, float)) else ''))
        xv = v.get(VALORI.get(prop, ''))
        righe.append('| %s | %s | %s |' % (prop, '%.3g' % xv if isinstance(xv, (int, float)) else '', ' | '.join(celle)))
    righe.append('| **totale su %d** | | %s |' % (len(BANDE), ' | '.join(str(punti[n]) for n in nomi)))
    with open(os.path.join(RISULTATI, 'e61_pagella.json'), 'w', encoding='utf-8') as fh:
        json.dump(ris, fh, ensure_ascii=False, indent=1, default=str)
    with open(os.path.join(RISULTATI, 'e61_pagella.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(righe) + '\n')
    print('\n'.join(righe))


if __name__ == '__main__':
    main()
