# -*- coding: utf-8 -*-
"""Esperimento e3a90: misure dell'e3a89 (calo della ripetizione nella riga, ecc.) su generatori e gibberish umano.

Preregistrazione: preregistrazioni/e3a90.md. Scrive risultati/e3a90_ripresa_generatori.json e .md.
"""
import json, os, random, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure as mis
import e134_generatori_esterni as e134
import e337_posizione as e337
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58
import e3a89_ripresa_lingue as e3a89

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = mis.divisore(mis.GLIFI_EVA)


def main():
    rnd = random.Random(3190)
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
    for k, rr in testi.items():
        righe = [[tuple(w) for w in r] for r in rr if r]
        pagine = [[righe[i:i + 25]] for i in range(0, len(righe), 25)]
        x = e3a89.misure(pagine, rnd)
        c = x['calo']
        if x['coppie_stessa_d7_10'] < 500 or c is None:
            es = 'n.d.'
        else:
            es = 'ripete subito come il Voynich' if c < 0.5 else ('come le lingue' if c > 1.10 else 'in mezzo')
        x['esito'] = es
        ris[k] = x
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a90_ripresa_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = lambda v: 'n.d.' if v is None else '%+.4f' % v
    md = ['# e3a90 — La ripetizione ravvicinata dentro la riga c\'è nei generatori e nel gibberish umano?', '', 'Preregistrazione: `preregistrazioni/e3a90.md`. Voynich: calo 0,12; lingue: mediana 2,86, 10° percentile 1,10.', '',
          '| testo | eccesso stessa riga d 1–4 | d 7–10 | calo | piattezza dalla riga sopra | coppie d 7–10 | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %s | %s | %s | %s | %d | %s |' % (k, f(x['stessa_d1_4']), f(x['stessa_d7_10']), f(x['calo']), f(x['piattezza']), x['coppie_stessa_d7_10'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a90_ripresa_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
