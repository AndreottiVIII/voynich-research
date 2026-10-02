# -*- coding: utf-8 -*-
"""Esperimento 167: i cifrati Polygraphia III di Hermes (2022) mandati a capo: legame alle giunture, alternanza,
ripetizione immediata, contro il Voynich (a lettere EVA) e Plinio.

Preregistrazione: preregistrazioni/e167.md. Scrive risultati/e167_polygraphia.json e .md.
"""
import hashlib, json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e110_alternanza as e110

RISULTATI = os.path.join(QUI, '..', 'risultati')
HERMES = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni', 'hermes')
SHA = {'PIII_10_columns': '94684e8c97983b0ca44ef5a5f57a69dd1ffcfa327dbebd1914cd7543794d50fc',
       'PIII_24_columns': '1c16d94635b3f7a6ac9dc8e3b7eac89d799994068743969760e1781e1e9f2f51',
       'PIII_all_columns': '15f26531ba95968549dae29ca9b30d3e7dde0cc9b0a81ef2d64c548d8c651a81'}
SEME, RIMESCOLAMENTI = 167, 200


def ripetizione(righe, rnd):
    def conta(rr):
        return sum(a == b for ps in rr for a, b in zip(ps, ps[1:]))
    rr = [ps for ps in righe if len(ps) >= 2]
    vero = conta(rr)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for ps in rr:
            ps = ps[:]
            rnd.shuffle(ps)
            mes.append(ps)
        nulli.append(conta(mes))
    m = statistics.mean(nulli)
    return OrderedDict([('coppie_identiche', vero), ('attese', m), ('rapporto', vero / m if m else None)])


def misura(nome, righe):
    """righe: (inizio paragrafo, parole)."""
    rnd = random.Random(SEME)
    dentro, _ = e74.coppie([(None, ini, ps) for ini, ps in righe], e71.lettere)
    r = OrderedDict()
    r['a_giunture'] = e74.eccesso(dentro, rnd)
    _, a = e110.una(('x', [ps for _, ps in righe], 'lettere'))
    r['b_A'] = a['senza identiche']['A']
    r['c_ripetizione'] = ripetizione([[w for w in ps if trascrizione.pulita(w)] for _, ps in righe], rnd)
    print('%-28s (a) eccesso %.4f (z %.0f) | (b) A %.3f | (c) ripetizione %.2f' % (nome, r['a_giunture']['eccesso'], r['a_giunture']['z'] or 0,
          r['b_A'], r['c_ripetizione']['rapporto'] or 0), flush=True)
    return r


def main():
    from e36_posizione_pagina import plinio
    D = e71.D
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rv = e71.righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    testi = OrderedDict([('Voynich (lettere EVA)', rv), ('Plinio a capo', e71.a_capo([w for _, ps in plinio() for w in ps], e71.lettere, larghezze, media_voy))])
    for nome, sha in SHA.items():
        dati = open(os.path.join(HERMES, nome), 'rb').read()
        if hashlib.sha256(dati).hexdigest() != sha:
            raise SystemExit('%s diverso da quello preregistrato' % nome)
        testi['Polygraphia III, ' + nome] = e71.a_capo(dati.decode('utf-8').split(), e71.lettere, larghezze, media_voy)
    ris = OrderedDict((n, misura(n, rr)) for n, rr in testi.items())
    v = ris['Voynich (lettere EVA)']
    esiti = OrderedDict()
    for n in SHA:
        r = ris['Polygraphia III, ' + n]
        e = OrderedDict([('a', r['a_giunture']['eccesso'] >= 0.5 * v['a_giunture']['eccesso']), ('b', abs(r['b_A'] - v['b_A']) <= 0.02),
                         ('c', bool(r['c_ripetizione']['rapporto']) and 0.5 * v['c_ripetizione']['rapporto'] <= r['c_ripetizione']['rapporto'] <= 2 * v['c_ripetizione']['rapporto'])])
        esiti[n] = e
    compatibile = any(all(e.values()) for e in esiti.values())
    ris['esiti'], ris['compatibile'] = esiti, compatibile
    print('esiti:', json.dumps(esiti), '| compatibile:', compatibile)
    with open(os.path.join(RISULTATI, 'e167_polygraphia.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e167 — Polygraphia III (Hermes 2022) e le proprietà fra parole', '',
           'Cifrati di Hermes mandati a capo con le larghezze del Voynich; tutto a lettere singole. Preregistrazione: `preregistrazioni/e167.md`.', '',
           '| testo | (a) legame alle giunture (z) | (b) A | (c) ripetizione immediata / attesa |', '|---|---|---|---|']
    for n in testi:
        r = ris[n]
        out.append('| %s | %.4f (%.0f) | %.3f | %.2f |' % (n, r['a_giunture']['eccesso'], r['a_giunture']['z'] or 0, r['b_A'], r['c_ripetizione']['rapporto'] or 0))
    out += ['', 'Riprodotte (a, b, c): ' + '; '.join('%s %s' % (n, ' '.join('%s %s' % (k, 'sì' if x else 'no') for k, x in e.items())) for n, e in esiti.items()) + '.', '',
            'Compatibile: **%s**.' % ('sì' if compatibile else 'no')]
    with open(os.path.join(RISULTATI, 'e167_polygraphia.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
