# -*- coding: utf-8 -*-
"""Esperimento 89: le etichette somigliano alle prime parole di riga (intestazioni), alle fini (abitudine di bordo)
o alle parole interne?

Preregistrazione: preregistrazioni/e89.md. Scrive risultati/e89_etichette_prime_parole.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RICAMPIONI = 89, 1000
D = e71.D


def classi():
    ini, inte, fin = [], [], []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = r.parole
        if not ps:
            continue
        if not r.inizio_par and trascrizione.pulita(ps[0]):
            ini.append(ps[0])
        if trascrizione.pulita(ps[-1]) and len(ps) >= 2:
            fin.append(ps[-1])
        if len(ps) >= 5:
            inte.extend(w for w in ps[2:-2] if trascrizione.pulita(w))
    return {'iniziale': ini, 'interna': inte, 'finale': fin}


def etichette():
    return [w for r in trascrizione.leggi('ZL') if r.tipo[0] == trascrizione.ETICHETTA
            for w in r.parole if trascrizione.pulita(w)]


def distr(parole, pos):
    return Counter(D(w)[pos] for w in parole)


def distanze(et, cl):
    out = {}
    for nome, pos in (('ini', 0), ('fin', -1)):
        de = distr(et, pos)
        out[nome] = {c: e71.jsd(de, distr(ws, pos)) for c, ws in cl.items()}
    return out


ORDINI = OrderedDict([
    ('abitudine di bordo', [('ini', 'iniziale', 'interna'), ('fin', 'finale', 'iniziale'), ('fin', 'finale', 'interna')]),
    ('intestazione', [('ini', 'iniziale', 'interna'), ('fin', 'iniziale', 'finale'), ('fin', 'iniziale', 'interna')]),
    ('nessuna relazione', [('ini', 'interna', 'iniziale'), ('ini', 'interna', 'finale'), ('fin', 'interna', 'iniziale'), ('fin', 'interna', 'finale')]),
])


def vale(d, ordine):
    return all(d[m][a] < d[m][b] for m, a, b in ordine)


def main():
    cl = classi()
    et = etichette()
    d = distanze(et, cl)
    rnd = random.Random(SEME)
    conti = Counter()
    for _ in range(RICAMPIONI):
        campione = [et[rnd.randrange(len(et))] for _ in et]
        dd = distanze(campione, cl)
        for nome, ordine in ORDINI.items():
            conti[nome] += vale(dd, ordine)
    ris = OrderedDict([('etichette', len(et)), ('classi', {c: len(w) for c, w in cl.items()}), ('distanze', d),
                       ('quota_ricampioni', {n: conti[n] / RICAMPIONI for n in ORDINI}),
                       ('ordine_osservato', {n: vale(d, o) for n, o in ORDINI.items()})])
    print('etichette %d | classi %s' % (len(et), ris['classi']))
    for m in ('ini', 'fin'):
        print('  D_%s: %s' % (m, ', '.join('%s %.4f' % (c, x) for c, x in d[m].items())))
    print('  ordine osservato', ris['ordine_osservato'], '| quota ricampioni', ris['quota_ricampioni'])
    # descrittivo: segni piu' frequenti
    for m, pos in (('primo', 0), ('ultimo', -1)):
        print('  %s segno etichette' % m, distr(et, pos).most_common(6))
        for c, ws in cl.items():
            print('     %s %s' % (c, distr(ws, pos).most_common(6)))
    with open(os.path.join(RISULTATI, 'e89_etichette_prime_parole.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e89 — Le etichette somigliano alle prime parole di riga?', '',
           'JSD fra il primo (ultimo) segno delle %d etichette e quello delle parole iniziali, interne e finali dei paragrafi. '
           'Bootstrap delle etichette (%d). Preregistrazione: `preregistrazioni/e89.md`.' % (len(et), RICAMPIONI), '',
           '| misura | iniziale | interna | finale |', '|---|---|---|---|']
    for m, nome in (('ini', 'primo segno (D_ini)'), ('fin', 'ultimo segno (D_fin)')):
        out.append('| %s | %s |' % (nome, ' | '.join('%.4f' % d[m][c] for c in ('iniziale', 'interna', 'finale'))))
    out += ['', '| lettura | ordine osservato | quota dei ricampioni |', '|---|---|---|']
    for n in ORDINI:
        out.append('| %s | %s | %.3f |' % (n, 'sì' if ris['ordine_osservato'][n] else 'no', ris['quota_ricampioni'][n]))
    with open(os.path.join(RISULTATI, 'e89_etichette_prime_parole.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
