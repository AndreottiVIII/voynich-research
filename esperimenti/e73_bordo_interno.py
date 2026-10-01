# -*- coding: utf-8 -*-
"""Esperimento 73: il modello dell'e72 sulla prima/seconda e penultima/ultima parola, con riferimento
le parole dalla terza alla terzultima (righe di almeno 6 parole). Effetto proprio del bordo =
guadagno al bordo meno guadagno nella posizione accanto.

Preregistrazione: preregistrazioni/e73.md. Scrive risultati/e73_bordo_interno.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e72_bordo_meccanismo as e72

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE = 6
POSIZIONI = OrderedDict([('prima', (0, 0, True)), ('seconda', (1, 0, True)),
                         ('penultima', (-2, -1, False)), ('ultima', (-1, -1, False))])


def guadagni(righe, dividi):
    pulita = trascrizione.pulita
    utili = [(i, inizio, ps) for i, (inizio, ps) in enumerate(righe) if len(ps) >= MIN_PAROLE]
    seg = lambda w: tuple(dividi(w))
    mezzo = [seg(w) for _, _, ps in utili for w in ps[2:-2] if pulita(w)]
    ris = OrderedDict()
    for nome, (indice, lato, senza_paragrafo) in POSIZIONI.items():
        voci = [(i, ps[indice]) for i, inizio, ps in utili if pulita(ps[indice]) and not (senza_paragrafo and inizio)]
        tot = OrderedDict((m, 0.0) for m in e72.MODELLI)
        n = 0
        for k in range(e72.PARTI):
            d_add = e72.componenti([seg(w) for i, w in voci if i % e72.PARTI != k], mezzo, lato)
            d_pro = e72.componenti([seg(w) for i, w in voci if i % e72.PARTI == k], mezzo, lato)
            base = None
            for m, quali in e72.MODELLI.items():
                lp = e72.logv(d_pro, e72.em(d_add, quali))
                if base is None:
                    base = lp
                tot[m] += lp - base
            n += len(d_pro)
        ris[nome] = OrderedDict([('n', n)] + [(m, g / n) for m, g in tot.items()])
    proprio = OrderedDict()
    for lato, (bordo, accanto) in (('inizio', ('prima', 'seconda')), ('fine', ('ultima', 'penultima'))):
        proprio[lato] = OrderedDict((m, ris[bordo][m] - ris[accanto][m]) for m in ('S+N+A', 'S+N+T', 'S+N+A+T'))
    return OrderedDict([('posizioni', ris), ('proprio', proprio)])


def una(args):
    nome, righe, quale = args
    return nome, guadagni(righe, e71.lettere if quale == 'lettere' else e71.D)


def testi():
    """Gli stessi testi dell'e72, con gli stessi semi."""
    from e36_posizione_pagina import plinio
    import generatori, lingue
    D = e71.D
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rv = e71.righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    latino = [w for _, ps in plinio() for w in ps]
    codificato = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(e72.SEME))
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    rc = e71.a_capo(codificato, D, larghezze, media_voy)
    rnd = random.Random(e72.SEME)
    aggiunta = [(i, ['s' + ps[0]] + ps[1:] if rnd.random() < 0.5 else ps) for i, ps in rc]
    rnd = random.Random(e72.SEME + 1)
    sostituita = []
    for i, ps in rc:
        if rnd.random() < 0.5:
            u = D(ps[-1])
            if u[-1] != 'm':
                ps = ps[:-1] + [''.join(u[:-1]) + 'm']
        sostituita.append((i, ps))
    t = OrderedDict()
    t['Voynich'] = (rv, 'eva')
    t['Voynich A'] = (e71.righe_voynich('A'), 'eva')
    t['Voynich B'] = (e71.righe_voynich('B'), 'eva')
    t['Plinio, a capo'] = (e71.a_capo(latino, e71.lettere, larghezze, media_voy), 'lettere')
    t['Plinio codificato, a capo'] = (rc, 'eva')
    t['Naibbe, a capo'] = (e71.a_capo(naibbe[:len(voy)], D, larghezze, media_voy), 'eva')
    t['controllo: aggiunta "s" all\'inizio'] = (aggiunta, 'eva')
    t['controllo: sostituzione con "m" alla fine'] = (sostituita, 'eva')
    for s in (19, 1, 2):
        t['Timm e Schinner, seme %d' % s] = (e71.righe_file(os.path.join(e71.CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt')), 'eva')
    t['modello e51, seme 19'] = (e71.righe_file(os.path.join(e71.CACHE, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt')), 'eva')
    return t


def main():
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in testi().items()]):
            ris[nome] = r
            p, q = r['posizioni'], r['proprio']
            print('%-42s A: 1a %+.3f 2a %+.3f pen %+.3f ult %+.3f | T: 1a %+.3f 2a %+.3f pen %+.3f ult %+.3f | proprio ini A %+.3f T %+.3f fin A %+.3f T %+.3f' % (
                nome, p['prima']['S+N+A'], p['seconda']['S+N+A'], p['penultima']['S+N+A'], p['ultima']['S+N+A'],
                p['prima']['S+N+T'], p['seconda']['S+N+T'], p['penultima']['S+N+T'], p['ultima']['S+N+T'],
                q['inizio']['S+N+A'], q['inizio']['S+N+T'], q['fine']['S+N+A'], q['fine']['S+N+T']), flush=True)
    with open(os.path.join(RISULTATI, 'e73_bordo_interno.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e73 — Il bordo contro una posizione interna', '',
           'Guadagno in bit per parola sul modello S+N (dati esclusi, 5 parti), righe di almeno %d parole; riferimento: '
           'parole dalla terza alla terzultima. "Proprio" = bordo meno posizione accanto. Preregistrazione: '
           '`preregistrazioni/e73.md`.' % MIN_PAROLE, '',
           '| testo | A 1ª | A 2ª | A penult. | A ult. | T 1ª | T 2ª | T penult. | T ult. | proprio inizio A / T | proprio fine A / T |',
           '|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        p, q = r['posizioni'], r['proprio']
        out.append('| %s | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f | %+.3f / %+.3f | %+.3f / %+.3f |' % (
            nome, p['prima']['S+N+A'], p['seconda']['S+N+A'], p['penultima']['S+N+A'], p['ultima']['S+N+A'],
            p['prima']['S+N+T'], p['seconda']['S+N+T'], p['penultima']['S+N+T'], p['ultima']['S+N+T'],
            q['inizio']['S+N+A'], q['inizio']['S+N+T'], q['fine']['S+N+A'], q['fine']['S+N+T']))
    with open(os.path.join(RISULTATI, 'e73_bordo_interno.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
