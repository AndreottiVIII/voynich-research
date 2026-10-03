# -*- coding: utf-8 -*-
"""Esperimento e3a08: a parita' di ultimo segno (primo segno), l'identita' della parola prima (dopo) dice ancora qualcosa
sul primo segno della parola dopo (ultimo della parola prima)? Voynich, testi sensati (parole intere), gibberish.

Preregistrazione: preregistrazioni/e3a08.md. Scrive risultati/e3a08_solo_segno.json e .md.
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


def eventi(paragrafi):
    av, ind = [], []
    for st, par in paragrafi:
        for r in par:
            for a, b in zip(r, r[1:]):
                av.append(((st, a[-1]), a, b[0]))
                ind.append(((st, b[0]), b, a[-1]))
    return av, ind


def due(paragrafi, rnd, perm):
    av, ind = eventi(paragrafi)
    return OrderedDict([('avanti', e380.prova(av, rnd, perm)), ('indietro', e380.prova(ind, rnd, perm))])


def main():
    rnd = random.Random(3108)
    voy = e380.voynich()
    ris = OrderedDict()
    ris['Voynich'] = due(voy, rnd, 1000)
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
        x = due(prese, rnd, 100)
        sub.append((x['avanti']['E'], x['indietro']['E']))
    ris['Voynich a 10.000 parole'] = OrderedDict([('avanti', [a for a, _ in sub]), ('indietro', [b for _, b in sub])])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib.append(('-', righe))
    ris['gibberish umano'] = due(gib, rnd, 100)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = due([('-', righe)], rnd, 100)
        print(k, sens[k.replace('.txt', '')]['avanti']['E'], sens[k.replace('.txt', '')]['indietro']['E'], flush=True)
    ris['testi_sensati'] = sens
    esiti = OrderedDict()
    for lato in ('avanti', 'indietro'):
        grandi = [x[lato]['E'] for x in sens.values() if x[lato]['eventi'] >= 5000]
        m = statistics.median(grandi)
        ev = statistics.median(ris['Voynich a 10.000 parole'][lato])
        if ev < 0.25 * m:
            es = 'il legame passa solo dal segno di bordo'
        elif ev >= 0.5 * m:
            es = 'anche la parola intera conta'
        else:
            es = 'una via di mezzo'
        esiti[lato] = OrderedDict([('E_voynich_10000', ev), ('mediana_lingue', m), ('lingue', len(grandi)), ('esito', es)])
    ris['esiti'] = esiti
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a08_solo_segno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    V = ris['Voynich']
    md = ['# e3a08 — Il legame con la parola dopo passa solo dall\'ultimo segno?', '', 'Preregistrazione: `preregistrazioni/e3a08.md`.', '',
          '| testo | avanti E | z | indietro E | z |', '|---|---|---|---|---|',
          '| Voynich (tutto) | %.4f | %.1f | %.4f | %.1f |' % (V['avanti']['E'], V['avanti']['z'], V['indietro']['E'], V['indietro']['z']),
          '| Voynich a 10.000 parole (mediana) | %.4f | | %.4f | |' % (esiti['avanti']['E_voynich_10000'], esiti['indietro']['E_voynich_10000']),
          '| gibberish umano | %.4f | %.1f | %.4f | %.1f |' % (ris['gibberish umano']['avanti']['E'], ris['gibberish umano']['avanti']['z'], ris['gibberish umano']['indietro']['E'], ris['gibberish umano']['indietro']['z'])]
    for k, x in sorted(sens.items(), key=lambda kv: -kv[1]['avanti']['E']):
        md.append('| %s | %.4f | %.1f | %.4f | %.1f |' % (k, x['avanti']['E'], x['avanti']['z'], x['indietro']['E'], x['indietro']['z']))
    md += ['', 'Mediana dei testi sensati con almeno 5.000 coppie: avanti %.4f, indietro %.4f.' % (esiti['avanti']['mediana_lingue'], esiti['indietro']['mediana_lingue']),
           'Esito avanti: **%s**. Esito indietro: **%s**.' % (esiti['avanti']['esito'], esiti['indietro']['esito'])]
    open(os.path.join(RISULTATI, 'e3a08_solo_segno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
