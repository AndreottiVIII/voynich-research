# -*- coding: utf-8 -*-
"""Esperimento 47: da dove viene il vocabolario aperto del Voynich? Locale o ricambio fra sezioni.

Parole uniche in finestre contigue di dimensione crescente e ricambio del vocabolario con la
distanza nel testo; Voynich (tutto, Currier A, Currier B), generatore di Timm e Schinner con
giunture (e23, forza 3), Bibbia latina e Plinio.

Preregistrazione: preregistrazioni/e47.md. Serve Java. Scrive risultati/e47_vocabolario.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e23_giunture as e23
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
FINESTRE = (1000, 2000, 5000, 10000, 20000, 34000)
BLOCCO, DISTANZE = 1000, range(1, 21)


def per_finestre(parole):
    out = {}
    for n in FINESTRE:
        pezzi = [parole[i:i + n] for i in range(0, len(parole) - n + 1, n)]
        if not pezzi:
            continue
        hap, ttr = [], []
        for p in pezzi:
            c = Counter(p)
            hap.append(sum(1 for v in c.values() if v == 1) / len(c))
            ttr.append(len(c) / len(p))
        out[n] = {'finestre': len(pezzi), 'hapax': sum(hap) / len(hap), 'tipi_su_parole': sum(ttr) / len(ttr)}
    return out


def ricambio(parole):
    blocchi = [parole[i:i + BLOCCO] for i in range(0, len(parole) - BLOCCO + 1, BLOCCO)]
    tipi = [set(b) for b in blocchi]
    out = {}
    for k in DISTANZE:
        v = [sum(1 for w in blocchi[i + k] if w in tipi[i]) / BLOCCO for i in range(len(blocchi) - k)]
        if v:
            out[k] = sum(v) / len(v)
    return out


def voynich(lingua=None):
    return trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua))


def main():
    testi = OrderedDict([('Voynich', voynich()), ('Voynich, Currier A', voynich('A')),
                         ('Voynich, Currier B', voynich('B'))])
    os.makedirs(e23.LAVORO, exist_ok=True)
    tabella = os.path.join(e23.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = e23.compila()
    for seme in (19, 1, 2):
        pagine, _ = e23.genera(classi, tabella, 3.0, seme, nome='per_e47_seme_%d' % seme)
        testi['Timm e Schinner + giunture, seme %d' % seme] = [w for p in pagine for r in p for w in r]
    testi['Bibbia latina'] = lingue.parole('Latin')[:36000]
    testi['Plinio, libri 20-27'] = [w for _, ps in plinio() for w in ps]
    ris = OrderedDict()
    for nome, parole in testi.items():
        ris[nome] = {'parole': len(parole), 'finestre': per_finestre(parole), 'ricambio': ricambio(parole)}
        f = ris[nome]['finestre']
        print('%-38s %s' % (nome, '  '.join('n%d %.2f' % (n, f[n]['hapax']) for n in FINESTRE if n in f)), flush=True)
    ts = [k for k in ris if k.startswith('Timm')]
    divario = {n: ris['Voynich']['finestre'][n]['hapax'] - sum(ris[k]['finestre'][n]['hapax'] for k in ts) / len(ts)
               for n in FINESTRE if n in ris['Voynich']['finestre'] and all(n in ris[k]['finestre'] for k in ts)}
    rapporto = divario[FINESTRE[0]] / divario[max(divario)] if divario[max(divario)] else None
    ris['divario_hapax_voynich_meno_generatore'] = divario
    ris['rapporto_piccola_su_grande'] = rapporto
    ris['esito'] = 'T (ricambio)' if rapporto < 0.5 else ('L (locale)' if rapporto > 2 / 3 else 'misto')
    print('divario', divario, 'rapporto', rapporto, ris['esito'])
    with open(os.path.join(RISULTATI, 'e47_vocabolario.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e47 — Da dove viene il vocabolario aperto del Voynich', '',
           'Parole uniche (quota dei tipi che compaiono una volta) in finestre contigue di n parole, media sulle '
           'finestre. Ricambio: quota delle parole di un blocco di 1.000 il cui tipo compare in un blocco a '
           'distanza k. Preregistrazione: `preregistrazioni/e47.md`.', '',
           '| testo | ' + ' | '.join('n = %d' % n for n in FINESTRE) + ' | in comune k=1 | k=5 | k=20 |',
           '|---|' + '---|' * (len(FINESTRE) + 3)]
    for nome, r in ris.items():
        if not isinstance(r, dict) or 'finestre' not in r:
            continue
        f, c = r['finestre'], r['ricambio']
        out.append('| %s | %s | %s | %s | %s |' % (
            nome, ' | '.join('%.2f' % f[n]['hapax'] if n in f else '—' for n in FINESTRE),
            '%.2f' % c[1] if 1 in c else '—', '%.2f' % c[5] if 5 in c else '—', '%.2f' % c[20] if 20 in c else '—'))
    out += ['', 'Divario di parole uniche, Voynich − generatore (media dei tre semi): %s. Rapporto fra il divario a '
            'n = %d e quello a n = %d: %.2f → esito preregistrato: **%s**.' % (
                ', '.join('n=%d: %+.3f' % kv for kv in divario.items()), FINESTRE[0], max(divario), rapporto, ris['esito'])]
    with open(os.path.join(RISULTATI, 'e47_vocabolario.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
