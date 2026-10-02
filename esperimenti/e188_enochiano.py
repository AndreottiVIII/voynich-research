# -*- coding: utf-8 -*-
"""Esperimento 188: regole di riga (chiusura R, evitamento dell'inizio S, alternanza A, ripetizione) nell'enochiano di
Sloane MS 3188 (trascrizione di Boxer), contro Voynich e Plinio a capo.

Preregistrazione: preregistrazioni/e188.md. Scrive risultati/e188_enochiano.json e .md.
"""
import csv, hashlib, json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e110_alternanza as e110
import e167_polygraphia as e167

RISULTATI = os.path.join(QUI, '..', 'risultati')
FILE = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni', 'boxer', 'ms3188.csv')
SHA = '006b17f1323e8e86456ccb784db714f0962a68c509b4c304402edf5122b7ff1a'
SEME, RIMESCOLAMENTI = 188, 500


def enochiano():
    if hashlib.sha256(open(FILE, 'rb').read()).hexdigest() != SHA:
        raise SystemExit('ms3188.csv diverso da quello preregistrato')
    out, nuovo = [], True
    with open(FILE, encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['call']:
                nuovo = True
            ps = [r['w%d' % i].replace('-', '').strip().lower() for i in range(1, 21) if r.get('w%d' % i)]
            ps = [w for w in ps if w]
            if ps:
                out.append((nuovo, ps))
                nuovo = False
    return out


def evitamento(righe, rnd):
    paragrafi, cur = [], []
    for ini, ps in righe:
        if ini and cur:
            paragrafi.append(cur)
            cur = []
        cur.append(ps[0][0])
    if cur:
        paragrafi.append(cur)

    def uguali(pp):
        return sum(a == b for p in pp for a, b in zip(p, p[1:]))
    vero = uguali(paragrafi)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for p in paragrafi:
            p = p[:]
            rnd.shuffle(p)
            mes.append(p)
        nulli.append(uguali(mes))
    m = statistics.mean(nulli)
    return OrderedDict([('uguali', vero), ('attese', m), ('S', vero / m if m else None), ('p', (1 + sum(n <= vero for n in nulli)) / (1 + RIMESCOLAMENTI))])


def misura(nome, righe, rnd):
    dentro, a_capo = e74.coppie([(None, ini, ps) for ini, ps in righe], e71.lettere)
    d, a = e74.eccesso(dentro, rnd), e74.eccesso(a_capo, rnd)
    r = OrderedDict([('righe', len(righe)), ('dentro', d), ('a_capo', a), ('R', a['eccesso'] / d['eccesso'] if d['eccesso'] > 0 else None)])
    r['S'] = evitamento(righe, rnd)
    _, al = e110.una(('x', [ps for _, ps in righe], 'lettere'))
    r['A'] = al['senza identiche']['A']
    r['ripetizione'] = e167.ripetizione([[w for w in ps if trascrizione.pulita(w)] for _, ps in righe], rnd)['rapporto']
    print('%-28s righe %d | dentro %.4f (z %.1f) a capo %.4f (z %.1f) R %s | S %.2f (p %.4f) | A %.3f | ripetizione %.2f' % (
        nome, len(righe), d['eccesso'], d['z'] or 0, a['eccesso'], a['z'] or 0, '%.2f' % r['R'] if r['R'] is not None else '-',
        r['S']['S'] or 0, r['S']['p'], r['A'], r['ripetizione'] or 0), flush=True)
    return r


def main():
    from e36_posizione_pagina import plinio
    rnd = random.Random(SEME)
    D = e71.D
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rv = e71.righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    testi = OrderedDict([('enochiano (Sloane 3188)', enochiano()), ('Voynich (lettere EVA)', rv),
                         ('Plinio a capo', e71.a_capo([w for _, ps in plinio() for w in ps], e71.lettere, larghezze, media_voy))])
    ris = OrderedDict((n, misura(n, rr, rnd)) for n, rr in testi.items())
    e = ris['enochiano (Sloane 3188)']
    chiusura = (e['R'] is not None and e['R'] < 0.2 and (e['dentro']['z'] or 0) > 3)
    inizio = (e['S']['S'] or 9) <= 0.7 and e['S']['p'] < 0.01
    ris['enochiano_chiusura'], ris['enochiano_evitamento'] = chiusura, inizio
    ris['esito'] = 'ha le regole di riga del Voynich' if chiusura and inizio else 'non ha le regole di riga del Voynich'
    print('enochiano: chiusura %s, evitamento %s | %s' % (chiusura, inizio, ris['esito']))
    with open(os.path.join(RISULTATI, 'e188_enochiano.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e188 — L\'enochiano di Dee e Kelley ha le regole di riga del Voynich?', '', 'Tutto a lettere singole. Preregistrazione: `preregistrazioni/e188.md`.', '',
           '| testo | righe | giunture dentro (z) | attraverso l\'a capo (z) | R | S (p) | A | ripetizione |', '|---|---|---|---|---|---|---|---|']
    for n in testi:
        r = ris[n]
        out.append('| %s | %d | %.4f (%.1f) | %.4f (%.1f) | %s | %.2f (%.4f) | %.3f | %.2f |' % (n, r['righe'], r['dentro']['eccesso'], r['dentro']['z'] or 0,
                   r['a_capo']['eccesso'], r['a_capo']['z'] or 0, '%.2f' % r['R'] if r['R'] is not None else '–', r['S']['S'] or 0, r['S']['p'], r['A'], r['ripetizione'] or 0))
    out += ['', 'Enochiano: chiusura **%s**, evitamento dell\'inizio **%s**. Esito: **%s**.' % ('sì' if chiusura else 'no', 'sì' if inizio else 'no', ris['esito'])]
    with open(os.path.join(RISULTATI, 'e188_enochiano.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
