# -*- coding: utf-8 -*-
"""Esperimento e3a62: misura dell'e3a14 (legame dell'identita' della parola con il segno di bordo della vicina, a
parita' di segno di bordo e di pagina) su Naibbe, U2, U3, Timm e Schinner e gibberish umano.

Preregistrazione: preregistrazioni/e3a62.md. Scrive risultati/e3a62_legame_parole_generatori.json e .md.
"""
import json, os, random, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e381_parole_intere as e381
import e3a14_resto_pagina as e3a14
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
VOY = {'avanti': 0.02627527222556214, 'indietro': 0.017610590578446716}
LINGUE = {'avanti': 0.11104056800557016, 'indietro': 0.09545672637939706}


def main():
    rnd = random.Random(3162)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            testi[k] = e3a58.righe_prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v])
    testi['Timm e Schinner, seme 1'] = e3a58.righe_prime([[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p])
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    testi['gibberish umano'] = e3a58.righe_prime(gib)
    ris = OrderedDict()
    for k, righe in testi.items():
        righe = [r for r in righe if r]
        x = e3a14.due([(i, righe[i:i + 25]) for i in range(0, len(righe), 25)], rnd, 100)
        for lato in ('avanti', 'indietro'):
            soglia = (VOY[lato] + LINGUE[lato]) / 2
            x[lato]['soglia'] = soglia
            x[lato]['esito'] = 'come le lingue' if x[lato]['E'] > soglia else 'come il Voynich'
        ris[k] = x
        print(k, json.dumps(x, default=float, ensure_ascii=False), flush=True)
    out = OrderedDict([('riferimenti_e3a14', OrderedDict([('Voynich_10000', VOY), ('mediana_lingue', LINGUE)])), ('testi', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a62_legame_parole_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a62 — Il legame fra parole intere: un cifrario verboso come Naibbe somiglia al Voynich o a una lingua?', '', 'Preregistrazione: `preregistrazioni/e3a62.md`. Misura dell\'e3a14; riferimenti: Voynich a 10.000 parole 0,0263 avanti e 0,0176 indietro; mediana delle lingue 0,1110 e 0,0955.', '',
          '| testo | eventi | avanti E | z | esito | indietro E | z | esito |', '|---|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %.4f | %.1f | %s | %.4f | %.1f | %s |' % (k, x['avanti']['eventi'], x['avanti']['E'], x['avanti']['z'], x['avanti']['esito'], x['indietro']['E'], x['indietro']['z'], x['indietro']['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a62_legame_parole_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
