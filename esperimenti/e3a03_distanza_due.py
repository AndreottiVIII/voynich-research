# -*- coding: utf-8 -*-
"""Esperimento e3a03: informazione mutua fra l'ultimo segno di w1 e il primo segno di w3 (terne nella riga), condizionata
alla parola in mezzo w2 e allo strato; Voynich, testi sensati (parole intere), gibberish umano.

Preregistrazione: preregistrazioni/e3a03.md. Scrive risultati/e3a03_distanza_due.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e380_sandhi as e380
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')


def terne(paragrafi):
    """paragrafi: [(strato, [righe])] -> [((strato, w2), ultimo di w1, primo di w3)]."""
    out = []
    for st, par in paragrafi:
        for r in par:
            for a, b, c in zip(r, r[1:], r[2:]):
                out.append(((st, b), a[-1], c[0]))
    return out


def main():
    rnd = random.Random(3103)
    voy = e380.voynich()
    ris = OrderedDict()
    ev = terne(voy)
    ris['Voynich'] = e380.prova(ev, rnd, 1000)
    print('Voynich', json.dumps(ris['Voynich'], default=float), flush=True)
    sub = []
    for _ in range(5):
        ordine = rnd.sample(voy, len(voy))
        prese, n = [], 0
        for p in ordine:
            if n >= 10000:
                break
            prese.append(p)
            n += sum(len(r) for r in p[1])
        sub.append(e380.prova(terne(prese), rnd, 100)['E'])
    ris['Voynich a 10.000 parole'] = OrderedDict([('E', sub), ('E_mediana', statistics.median(sub))])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib.append(('-', righe))
    ris['gibberish umano'] = e380.prova(terne(gib), rnd, 100)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = e380.prova(terne([('-', righe)]), rnd, 100)
        print(k, sens[k.replace('.txt', '')]['E'], flush=True)
    ris['testi_sensati'] = OrderedDict(sorted(sens.items(), key=lambda kv: -kv[1]['E']))
    V = ris['Voynich']
    Em = ris['Voynich a 10.000 parole']['E_mediana']
    sopra = sum(1 for x in sens.values() if x['E'] > Em)
    if V['z'] < 2:
        esito = 'nessun legame oltre la parola accanto'
    elif V['z'] > 3:
        esito = 'c\'è un legame a distanza 2 (%d lingue su %d hanno E maggiore)' % (sopra, len(sens))
    else:
        esito = 'incerto'
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a03_distanza_due.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a03 — Legame a distanza 2, a parità della parola in mezzo', '', 'Preregistrazione: `preregistrazioni/e3a03.md`. E = informazione mutua (bit) fra ultimo segno di w1 e primo di w3, a parità di w2, oltre il nullo.', '',
          'Voynich: E %.4f, z %.1f (%d terne). Voynich a 10.000 parole: %s (mediana %.4f). Gibberish umano: E %.4f, z %.1f.' % (
              V['E'], V['z'], V['eventi'], ', '.join('%.4f' % x for x in sub), Em, ris['gibberish umano']['E'], ris['gibberish umano']['z']), '',
          '| testo sensato | terne | E | z |', '|---|---|---|---|']
    md += ['| %s | %d | %.4f | %.1f |' % (k, x['eventi'], x['E'], x['z']) for k, x in ris['testi_sensati'].items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a03_distanza_due.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
