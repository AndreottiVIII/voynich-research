# -*- coding: utf-8 -*-
"""Esperimento 114: accordo delle terminazioni a distanza k nella riga (IM fra ultimi 2 segni di parole a distanza k),
contro il rimescolamento dentro la riga.

Preregistrazione: preregistrazioni/e114.md. Scrive risultati/e114_accordo_terminazioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_PAROLE, KK = 114, 200, 6, (1, 2, 3, 4)
D = misure.divisore(misure.GLIFI_EVA)


def terminazioni(righe, dividi):
    out = []
    for ps in righe:
        if len(ps) >= MIN_PAROLE and all(trascrizione.pulita(w) for w in ps):
            out.append([''.join(dividi(w)[-2:]) for w in ps])
    return out


def im_k(righe, k):
    return misure.informazione_mutua([(r[i], r[i + k]) for r in righe for i in range(len(r) - k)])


def una(args):
    nome, righe, quale = args
    rr = terminazioni(righe, e71.lettere if quale == 'lettere' else D)
    rnd = random.Random(SEME)
    reale = {k: im_k(rr, k) for k in KK}
    nulli = {k: [] for k in KK}
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in rr:
            r = r[:]
            rnd.shuffle(r)
            mes.append(r)
        for k in KK:
            nulli[k].append(im_k(mes, k))
    out = OrderedDict([('righe', len(rr))])
    for k in KK:
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out['k%d' % k] = OrderedDict([('eccesso', reale[k] - m), ('z', (reale[k] - m) / s if s else None)])
    return nome, out


def testi():
    import e98_versi_latini as e98
    C = e71.CACHE
    t = OrderedDict()
    for q in ('ZL', 'IT'):
        t['Voynich ' + q] = ([list(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi(q)) if r.parole], 'eva')
    for l in ('A', 'B'):
        t['Voynich, lingua ' + l] = ([list(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=l) if r.parole], 'eva')
    for s in (19, 1, 2):
        t['Timm e Schinner, seme %d' % s] = ([ps for _, ps in e71.righe_file(os.path.join(C, 'seme_%d' % s, 'generate', 'generated_text.txt'))], 'eva')
    t['+ giunture (e23)'] = ([ps for _, ps in e71.righe_file(os.path.join(C, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt'))], 'eva')
    t['e51'] = ([ps for _, ps in e71.righe_file(os.path.join(C, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt'))], 'eva')
    for chiave, nome in (('Latin', 'latina'), ('Italian', 'italiana'), ('German', 'tedesca'), ('Hungarian', 'ungherese'), ('Turkish', 'turca')):
        ps = lingue.parole(chiave)[:35000]
        t['Bibbia ' + nome] = ([ps[i:i + 9] for i in range(0, len(ps), 9)], 'lettere')
    t['Ovidio'] = (e98.versi(e98.TESTI['Ovidio, Metamorfosi'])[:5000], 'lettere')
    return t


def main():
    t = testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, q) for n, (rr, q) in t.items()]):
            ris[nome] = r
            print('%-26s righe %5d | %s' % (nome, r['righe'], ' | '.join('k%d %+.4f (z %.1f)' % (k, r['k%d' % k]['eccesso'], r['k%d' % k]['z'] or 0) for k in KK)), flush=True)
    voy = all(any((ris[n]['k%d' % k]['z'] or 0) > 4 and ris[n]['k%d' % k]['eccesso'] > 0 for k in (2, 3)) for n in ('Voynich ZL', 'Voynich IT'))
    gen = [n for n in ris if n.startswith(('Timm', '+ giunture', 'e51'))]
    gen_no = all(all((ris[n]['k%d' % k]['z'] or 0) < 2 for k in (2, 3)) for n in gen)
    ris['accordo_voynich'], ris['generatori_senza'] = voy, gen_no
    print('accordo a distanza nel Voynich:', voy, '| generatori senza:', gen_no)
    with open(os.path.join(RISULTATI, 'e114_accordo_terminazioni.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e114 — Le terminazioni si accordano a distanza?', '', 'Eccesso d\'IM fra gli ultimi 2 segni di parole a distanza k nella riga, '
           'contro %d rimescolamenti dentro la riga; z fra parentesi. Preregistrazione: `preregistrazioni/e114.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | k = 1 | k = 2 | k = 3 | k = 4 |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %s |' % (nome, r['righe'], ' | '.join('%+.4f (%.1f)' % (r['k%d' % k]['eccesso'], r['k%d' % k]['z'] or 0) for k in KK)))
    out += ['', 'Accordo a distanza nel Voynich: **%s**; generatori senza: **%s**.' % ('sì' if voy else 'no', 'sì' if gen_no else 'no')]
    with open(os.path.join(RISULTATI, 'e114_accordo_terminazioni.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
