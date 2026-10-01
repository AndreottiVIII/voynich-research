# -*- coding: utf-8 -*-
"""Esperimento 91: forza delle giunture (misura "confine", parole interne) in tutte le lingue del corpus biblico,
nel sanscrito in versi e nel Voynich.

Preregistrazione: preregistrazioni/e91.md. Scrive risultati/e91_giunture_lingue.json e .md.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e77_versi_sandhi as e77

RISULTATI = os.path.join(QUI, '..', 'risultati')
N, RIGA, MINIMO = 35000, 8, 5000
CARTELLA = lingue.CACHE


def una(chiave):
    try:
        ps = lingue.parole(chiave)[:N]
    except Exception as e:
        return chiave, {'errore': str(e)[:200]}
    if len(ps) < MINIMO:
        return chiave, {'parole': len(ps), 'escluso': True}
    righe = [ps[i:i + RIGA] for i in range(0, len(ps), RIGA)]
    c = misure.confine(righe, None, solo_interne=True)
    return chiave, {'parole': len(ps), 'eccesso': c['im_confine_eccesso']}


def main():
    chiavi = sorted(f[:-4] for f in os.listdir(CARTELLA) if f.endswith('.txt'))
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for k, r in pool.imap(una, chiavi):
            ris['Bibbia ' + k] = r
    for nome, (f, sha) in e77.TESTI.items():
        versi = e77.mezzi_versi(f, sha)
        ris[nome + ' (versi)'] = {'parole': sum(len(v) for v in versi),
                                  'eccesso': misure.confine(versi, None, solo_interne=True)['im_confine_eccesso']}
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    righe = [[w for w in r.parole if trascrizione.pulita(w)] for r in corrente]
    ris['Voynich (ZL)'] = {'parole': sum(len(r) for r in righe),
                           'eccesso': misure.confine(righe, misure.divisore(misure.GLIFI_EVA), solo_interne=True)['im_confine_eccesso']}
    validi = [(n, r) for n, r in ris.items() if 'eccesso' in r]
    validi.sort(key=lambda x: -x[1]['eccesso'])
    for n, r in validi:
        print('%-36s %6d parole  eccesso %.4f' % (n, r['parole'], r['eccesso']))
    for n, r in ris.items():
        if 'eccesso' not in r:
            print('%-36s %s' % (n, r))
    with open(os.path.join(RISULTATI, 'e91_giunture_lingue.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e91 — Quali lingue scritte hanno giunture forti come il Voynich?', '',
           'Eccesso d\'informazione mutua fra ultimo e primo carattere di parole interne vicine (misura "confine"). Bibbie: '
           'prime %d parole in righe di %d. Preregistrazione: `preregistrazioni/e91.md`.' % (N, RIGA), '',
           '| testo | parole | eccesso (bit) |', '|---|---|---|']
    for n, r in validi:
        out.append('| %s | %d | %.4f |' % (n, r['parole'], r['eccesso']))
    with open(os.path.join(RISULTATI, 'e91_giunture_lingue.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
