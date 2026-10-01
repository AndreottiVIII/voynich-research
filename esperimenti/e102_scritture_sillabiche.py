# -*- coding: utf-8 -*-
"""Esperimento 102: abugida e sillabari (esclusi dall'e13) sull'impronta, con l'impaginazione del Voynich.

Preregistrazione: preregistrazioni/e102.md. Scrive risultati/e102_scritture_sillabiche.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e22_timm_schinner as e22
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 35000
CHIAVI = ('h2', 'spazio_spiegato', 'tipi_su_parole', 'hapax', 'identiche_vs_riga', 'somiglianza_riga',
          'somiglianza_6_righe', 'confine')
ANOMALIE = OrderedDict([('h2', -1), ('spazio_spiegato', 1), ('identiche_vs_riga', 1), ('somiglianza_riga', 1)])
RIFERIMENTI = ('Latin', 'Italian', 'English', 'German', 'French', 'Spanish', 'Hungarian', 'Finnish', 'Turkish',
               'Tagalog', 'Swahili-NT', 'Greek', 'Russian', 'Hebrew', 'Arabic', 'Basque-NT', 'Icelandic')


def struttura():
    pv = pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    return [[len(r) for r in p] for p in pv]


def impagina(parole, strut):
    out, i = [], 0
    while i < len(parole):
        for p in strut:
            pag = []
            for n in p:
                if i >= len(parole):
                    break
                pag.append(parole[i:i + n])
                i += n
            if pag:
                out.append(pag)
            if i >= len(parole):
                break
    return out


def una(args):
    chiave, strut = args
    ps = lingue.parole(chiave)[:N]
    r = e22.lista_di_controllo(impagina(ps, strut), None)
    return chiave, {k: r[k] for k in CHIAVI}


def main():
    idx = lingue.indice()
    non_alfa = [k for k, m in idx.items() if m['tipo_scrittura'] in ('abugida', 'sillabario') and k != 'Icelandic']
    strut = struttura()
    ris = OrderedDict()
    pv = pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    v = e22.lista_di_controllo(pv, misure.divisore(misure.GLIFI_EVA))
    ris['Voynich'] = {k: v[k] for k in CHIAVI}
    lavori = [(k, strut) for k in list(RIFERIMENTI) + sorted(non_alfa)]
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for k, r in pool.imap(una, lavori):
            ris[k] = r
            print('%-14s %-11s %s' % (k, idx[k]['tipo_scrittura'] if k in idx else '', ' '.join('%s %.3f' % (c, r[c]) for c in CHIAVI)), flush=True)
    med = {c: statistics.median(ris[k][c] for k in RIFERIMENTI) for c in ANOMALIE}
    conti = OrderedDict()
    for k in non_alfa:
        n = 0
        for c, segno in ANOMALIE.items():
            soglia = med[c] + (ris['Voynich'][c] - med[c]) / 2
            n += (ris[k][c] - soglia) * segno > 0
        conti[k] = n
    ris['mediana_alfabetiche'] = med
    ris['anomalie_condivise'] = conti
    print('mediana alfabetiche', {c: round(x, 3) for c, x in med.items()}, '| Voynich', {c: round(ris['Voynich'][c], 3) for c in ANOMALIE})
    print('anomalie condivise (su 4):', conti)
    with open(os.path.join(RISULTATI, 'e102_scritture_sillabiche.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e102 — Le scritture non alfabetiche sull\'impronta', '',
           'Prime %d parole, impaginate come il Voynich; un carattere Unicode per segno. Anomalie condivise: oltre metà '
           'distanza fra la mediana delle alfabetiche di riferimento e il Voynich, dalla parte del Voynich. Preregistrazione: '
           '`preregistrazioni/e102.md`.' % N, '', '| testo | scrittura | ' + ' | '.join(CHIAVI) + ' | anomalie condivise |',
           '|---|---|' + '---|' * len(CHIAVI) + '---|']
    for k, r in ris.items():
        if k in ('mediana_alfabetiche', 'anomalie_condivise'):
            continue
        tipo = 'EVA' if k == 'Voynich' else idx[k]['tipo_scrittura']
        out.append('| %s | %s | %s | %s |' % (k, tipo, ' | '.join('%.3f' % r[c] for c in CHIAVI), conti.get(k, '–')))
    with open(os.path.join(RISULTATI, 'e102_scritture_sillabiche.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
