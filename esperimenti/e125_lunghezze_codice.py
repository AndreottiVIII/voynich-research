# -*- coding: utf-8 -*-
"""Esperimento 125: un messaggio nelle lunghezze delle parole? Statistica della sequenza delle lunghezze e decifrazione
con il risolutore dell'e17.

Preregistrazione: preregistrazioni/e125.md. Scrive risultati/e125_lunghezze_codice.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e17_ricottura as e17
import e71_bordo_riga as e71
import e119_acrostico as e119

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, MAX = 125, 8
D = misure.divisore(misure.GLIFI_EVA)


def lung(n):
    return 'L%d' % min(n, MAX)


def sequenza_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        for w in r.parole:
            per.setdefault(r.pagina, []).append(lung(len(D(w))) if trascrizione.pulita(w) else None)
    return e17.in_unita(list(per.values()), lambda x: [x])


def sequenza_parole(parole, dividi, per=200):
    s = [lung(len(dividi(w))) for w in parole]
    return [s[i:i + per] for i in range(0, len(s), per)]


def main():
    voy = sequenza_voynich()
    L = sum(map(len, voy))
    simboli = len({u for r in voy for u in r})
    print('lunghezze del Voynich: %d simboli, lunghezza %d' % (simboli, L), flush=True)
    rnd = random.Random(SEME)
    seq = OrderedDict()
    seq['lunghezze del Voynich'] = voy
    seq['lunghezze delle parole latine'] = sequenza_parole(lingue.parole('Latin')[:L], list)
    lett = e119.lettere_righe('Latin', L)
    cif, _ = e17.cifra_abbinata([[''.join(r)] for r in lett], simboli, random.Random(SEME))
    seq['latino cifrato con %d simboli (controllo)' % simboli] = cif
    ts = [w for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')) for w in ps][:L]
    seq['lunghezze di Timm e Schinner'] = sequenza_parole(ts, D)
    stat = OrderedDict()
    for nome, rr in seq.items():
        stat[nome] = e119.statistiche(rr, rnd)
        s = stat[nome]
        print('%-44s lungh %5d simboli %2d | h1 %.2f h2 %.2f (h2/h1 %.2f) | IM1 %.3f (z %.1f) IM2 %.3f (z %.1f) | S1 %.2f S2 %.2f' % (
            nome, s['lunghezza'], s['simboli'], s['h1'], s['h2'], s['h2_su_h1'], s['im1']['eccesso'], s['im1']['z'] or 0,
            s['im2']['eccesso'], s['im2']['z'] or 0, s['S1'], s['S2']), flush=True)
    dec = OrderedDict()
    for chiave_l, nome in (('Latin', 'latino'), ('Italian', 'italiano')):
        r = e119.una_lingua(chiave_l, nome, voy)
        dec[nome] = r
        for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
            x = r[k]
            print('%-10s %-20s punteggio %.3f copertura %.1f%% (6+: %.1f%%) %s' % (nome, k, x['punteggio'], 100 * x['copertura'], 100 * x['copertura_6'],
                                                                         'chiave giusta %.0f%%' % (100 * x['chiave_giusta']) if 'chiave_giusta' in x else ''), flush=True)
        print('   posizione del Voynich %.2f | decifrato: %s' % (r['posizione'], ' / '.join(r['Voynich']['esempio'][:3])[:200]), flush=True)
    valido = any(dec[n]['controllo positivo'].get('chiave_giusta', 0) >= 0.5 for n in dec)
    aperto = any(dec[n]['posizione'] >= 0.5 and dec[n]['Voynich']['copertura_6'] >= 0.10 for n in dec)
    print('controllo valido:', valido, '| messaggio non escluso:', aperto)
    ris = OrderedDict([('statistica', stat), ('decifrazione', dec), ('valido', valido), ('messaggio_non_escluso', aperto)])
    with open(os.path.join(RISULTATI, 'e125_lunghezze_codice.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e125 — Un messaggio nelle lunghezze delle parole?', '', 'Preregistrazione: `preregistrazioni/e125.md`.', '', '## Statistica', '',
           '| sequenza | lunghezza | simboli | h2/h1 | IM1 (z) | IM2 (z) | S(1) | S(2) |', '|---|---|---|---|---|---|---|---|']
    for nome, s in stat.items():
        out.append('| %s | %d | %d | %.2f | %.3f (%.1f) | %.3f (%.1f) | %.2f | %.2f |' % (nome, s['lunghezza'], s['simboli'], s['h2_su_h1'], s['im1']['eccesso'],
                                                                              s['im1']['z'] or 0, s['im2']['eccesso'], s['im2']['z'] or 0, s['S1'], s['S2']))
    out += ['', '## Decifrazione', '', '| lingua | prova | punteggio | copertura 6+ | chiave giusta |', '|---|---|---|---|---|']
    for nome, r in dec.items():
        for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
            x = r[k]
            out.append('| %s | %s | %.3f | %.1f%% | %s |' % (nome, k, x['punteggio'], 100 * x['copertura_6'], '%.0f%%' % (100 * x['chiave_giusta']) if 'chiave_giusta' in x else '–'))
        out.append('| %s | posizione del Voynich | %.2f | | |' % (nome, r['posizione']))
    out += ['', 'Controllo valido: **%s**. Messaggio non escluso: **%s**.' % ('sì' if valido else 'no', 'sì' if aperto else 'no')]
    with open(os.path.join(RISULTATI, 'e125_lunghezze_codice.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
