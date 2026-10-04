# -*- coding: utf-8 -*-
"""Esperimento e3a95: evitamento degli inizi uguali sul margine sinistro (e3a35) nei generatori.

Preregistrazione: preregistrazioni/e3a95.md. Scrive risultati/e3a95_margine_generatori.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure as mis
import e134_generatori_esterni as e134
import e337_posizione as e337
import e3a35_margine_confronti as e3a35
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = mis.divisore(mis.GLIFI_EVA)


def esito(x):
    r, z = x['rapporto'], x['z']
    if r is None:
        return 'n.d.'
    if r < 0.8 and z < -3:
        return 'evita come il Voynich'
    if abs(z) < 2:
        return 'non evita'
    if r > 1.2 and z > 3:
        return 'ripete'
    return 'incerto'


def main():
    rnd = random.Random(3195)
    ris = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            righe = [r for r in e3a58.righe_prime([[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]) if r]
            ris[k] = e3a35.due([righe[i:i + 25][1:] for i in range(0, len(righe), 25)], rnd)
    ts = [[[tuple(D(w)) for w in r] for r in p][1:] for p in e337.pagine_ts(1)]
    ris['Timm e Schinner, seme 1'] = e3a35.due(ts, rnd)
    for k, x in ris.items():
        for m in x.values():
            m['esito'] = esito(m)
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a95_margine_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a95 — I generatori evitano di cominciare la riga come la precedente?', '', 'Preregistrazione: `preregistrazioni/e3a95.md`. Voynich: rapporto 0,51 (primi 2 segni); gibberish umano 1,32; lingue mediana 0,95.', '',
          '| testo | misura | coppie | rapporto | z | esito |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        for m, y in x.items():
            md.append('| %s | %s | %d | %s | %.1f | %s |' % (k, m, y['coppie'], '%.2f' % y['rapporto'] if y['rapporto'] is not None else 'n.d.', y['z'], y['esito']))
    open(os.path.join(RISULTATI, 'e3a95_margine_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
