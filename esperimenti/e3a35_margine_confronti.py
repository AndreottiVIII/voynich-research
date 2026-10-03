# -*- coding: utf-8 -*-
"""Esperimento e3a35: inizi uguali fra righe consecutive (primi 2 segni, primo segno) contro l'ordine delle righe
rimescolato: Voynich, gibberish umano, testi sensati.

Preregistrazione: preregistrazioni/e3a35.md. Scrive risultati/e3a35_margine_confronti.json e .md.
"""
import json, os, random, statistics, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e381_parole_intere as e381
import e3a25_inizi_evitati as e3a25

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)


def due(blocchi, rnd, perm=1000):
    return OrderedDict([('primi 2 segni', e3a25.prova([e3a25.inizi(b, 2) for b in blocchi], rnd, perm)),
                        ('primo segno', e3a25.prova([e3a25.inizi(b, 1) for b in blocchi], rnd, perm))])


def main():
    rnd = random.Random(3135)
    voy = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par][1:]
            if len(rr) >= 3:
                voy.append(rr)
    ris = OrderedDict([('Voynich', due(voy, rnd))])
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(nome).decode('utf-8', errors='ignore').splitlines()) if ws]
                if len(righe) >= 4:
                    gib.append(righe[1:])
    ris['gibberish umano'] = due(gib, rnd)
    for k in ris:
        print(k, json.dumps(ris[k]), flush=True)
    sens = OrderedDict()
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        sens[k.replace('.txt', '')] = due([righe[i:i + 25][1:] for i in range(0, len(righe), 25)], rnd, 200)
    ris['testi_sensati'] = sens
    G = ris['gibberish umano']['primi 2 segni']
    if G['rapporto'] is not None and G['rapporto'] < 0.8 and G['z'] < -3:
        esito = 'anche il gibberish umano evita'
    elif abs(G['z']) < 2:
        esito = 'il gibberish umano no'
    else:
        esito = 'incerto'
    rv = ris['Voynich']['primi 2 segni']['rapporto']
    rs = [x['primi 2 segni']['rapporto'] for x in sens.values() if x['primi 2 segni']['coppie'] >= 300 and x['primi 2 segni']['rapporto']]
    ris['sensati'] = OrderedDict([('n', len(rs)), ('min', min(rs)), ('mediana', statistics.median(rs)), ('max', max(rs)), ('sotto_il_voynich', sum(1 for r in rs if r < rv))])
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a35_margine_confronti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a35 — Chi scrive gibberish a mano evita anche lui di cominciare due righe allo stesso modo?', '', 'Preregistrazione: `preregistrazioni/e3a35.md`.', '',
          '| testo | misura | coppie | osservata | nullo | rapporto | z |', '|---|---|---|---|---|---|---|']
    for k in ('Voynich', 'gibberish umano'):
        for m, x in ris[k].items():
            md.append('| %s | %s | %d | %.3f | %.3f | %.2f | %.1f |' % (k, m, x['coppie'], x['osservata'], x['nullo'], x['rapporto'], x['z']))
    s = ris['sensati']
    md += ['', 'Testi sensati con almeno 300 coppie (%d): rapporto (primi 2 segni) da %.2f a %.2f, mediana %.2f; sotto il Voynich: %d.' % (s['n'], s['min'], s['max'], s['mediana'], s['sotto_il_voynich']), '',
           'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a35_margine_confronti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
