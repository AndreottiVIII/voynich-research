# -*- coding: utf-8 -*-
"""Esperimento e3b05: statistica dell'e3b03 (spazio facoltativo e parola intera, a parita' di 4 segni e lunghezza dei
pezzi) su generatori e gibberish umano, con nullo dentro gli strati.

Preregistrazione: preregistrazioni/e3b05.md. Scrive risultati/e3b05_lessicale_generatori.json e .md.
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
import e3a99_spazio_lessicale as e3a99
import e3b01_taratura_lessicale as e3b01
import e3b03_lessicale_lunghezza as e3b03

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = mis.divisore(mis.GLIFI_EVA)


def misura(righe_parole, rnd):
    righe = e3a99.righe_testo(righe_parole)
    punti = e3b01.punti_fissi(righe)
    if len(punti) < 500:
        return OrderedDict([('punti', len(punti)), ('esito', 'n.d.')])
    ys = [p[3] for p in punti]
    lun = e3b03.lunghezze(righe, punti)
    key = [(p[2],) + l for p, l in zip(punti, lun)]
    vero = e3b03.statistica(righe, punti, ys, key)
    m, s = e3b03.nullo(righe, punti, ys, key, key, rnd)
    z = (vero - m) / s if s else 0.0
    sc = vero - m
    es = 'spazio lessicale' if sc > 1.0 and z > 3 else ('come il Voynich' if sc < 0.3 else 'in mezzo')
    return OrderedDict([('punti', len(punti)), ('differenza_vera', vero), ('nullo_media', m), ('nullo_sd', s), ('scarto', sc), ('z', z), ('esito', es)])


def main():
    rnd = random.Random(3205)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            testi[k] = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
    testi['Timm e Schinner, seme 1'] = [[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    testi['gibberish umano'] = gib
    ris = OrderedDict()
    for k, rr in testi.items():
        ris[k] = misura(rr, rnd)
        print(k, json.dumps(ris[k], ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3b05_lessicale_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b05 — Nei generatori e nel gibberish umano lo spazio segue la parola intera?', '', 'Preregistrazione: `preregistrazioni/e3b05.md`. Voynich (e3b03): +0,105 contro nullo N1 −0,090 (scarto +0,195); latino a parità di lunghezza +4,0.', '',
          '| testo | punti facoltativi | differenza vera | nullo (strati) | scarto | z | esito |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if 'differenza_vera' in x:
            md.append('| %s | %d | %+.3f | %+.3f | %+.3f | %+.1f | %s |' % (k, x['punti'], x['differenza_vera'], x['nullo_media'], x['scarto'], x['z'], x['esito']))
        else:
            md.append('| %s | %d | – | – | – | – | n.d. |' % (k, x['punti']))
    open(os.path.join(RISULTATI, 'e3b05_lessicale_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
