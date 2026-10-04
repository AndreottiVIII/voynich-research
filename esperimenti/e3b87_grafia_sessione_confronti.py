# -*- coding: utf-8 -*-
"""Esperimento e3b87: misura dell'e3b86 (grafia di sessione) su generatori e scribi veri, con blocchi di 25 righe.

Preregistrazione: preregistrazioni/e3b87.md. Scrive risultati/e3b87_grafia_sessione_confronti.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e134_generatori_esterni as e134
import e337_posizione as e337
import e381_parole_intere as e381
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b75_marianus as e3b75
import e3b86_grafia_sessione as e3b86

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
BLOCCO = 25


def analisi(righe, classi, rnd):
    blocchi = [righe[i:i + BLOCCO] for i in range(0, len(righe), BLOCCO)]
    dentro, pagine = [], []
    for b in blocchi:
        tot_d = [0, 0, 0, 0]
        tot_t = defaultdict(lambda: [0, 0])
        for c, f in classi.items():
            d, t = e3b86.dati_pagina([b], f)
            tot_d = [x + y for x, y in zip(tot_d, d)]
            for k, v in t.items():
                tot_t[(c, k)][0] += v[0]
                tot_t[(c, k)][1] += v[1]
        dentro.append(tot_d)
        pagine.append(('testo', dict(tot_t)))
    n = len(pagine)
    uno = [1] * n
    dw, db = e3b86.d_dentro(dentro, uno), e3b86.fra_pagine(pagine, uno)
    boot = []
    for _ in range(BOOT):
        cnt = Counter(rnd.randrange(n) for _ in range(n))
        pesi = [cnt[i] for i in range(n)]
        a, b = e3b86.d_dentro(dentro, pesi), e3b86.fra_pagine(pagine, pesi)
        if a is not None and b is not None:
            boot.append(a - b)
    boot.sort()
    return OrderedDict([('blocchi', n), ('D_dentro', dw), ('D_fra', db), ('contrasto', dw - db if dw is not None and db is not None else None),
                        ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]] if boot else None),
                        ('coppie_dentro_stesso_tipo', sum(d[1] for d in dentro))])


def main():
    rnd = random.Random(3287)
    testi = OrderedDict()
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            testi[k] = ([r for r in ([w for w in (tuple(e3b62.D(x)) for x in ps) if w] for _, ps in v) if r], e3b62.CV)
    testi['Timm e Schinner, seme 1'] = ([r for r in ([tuple(e3b62.D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r], e3b62.CV)
    tt = e381.testi()
    testi['Hatton Gospels, þ/ð a inizio parola'] = ([r for r in tt[e3b54.STORICI['Hatton Gospels']] if r], OrderedDict([('th', e3b54.v_th_ini)]))
    testi['Codex Marianus, и/ꙇ a inizio parola'] = ([r for r in tt[e3b75.CHIAVE] if r], OrderedDict([('i', e3b75.i_iniziale)]))
    ris, es = OrderedDict(), OrderedDict()
    for nome, (righe, classi) in testi.items():
        ris[nome] = analisi(righe, classi, rnd)
        ic = ris[nome]['IC95']
        es[nome] = 'n.d.' if not ic else ('grafia di sessione' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'no'))
        print(nome, es[nome], json.dumps(ris[nome], ensure_ascii=False), flush=True)
    out = OrderedDict([('testi', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b87_grafia_sessione_confronti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b87 — La "grafia di sessione" c\'è anche nei generatori e negli scribi veri?', '', 'Preregistrazione: `preregistrazioni/e3b87.md`. Voynich (e3b86): contrasto +0,045 (ZL), +0,046 (IT).', '',
          '| testo | blocchi | D dentro | D fra | contrasto (IC 95%) | coppie stessa parola dentro | esito |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        if x['contrasto'] is None or not x['IC95']:
            md.append('| %s | %d | — | — | n.d. | %d | n.d. |' % (k, x['blocchi'], x['coppie_dentro_stesso_tipo']))
            continue
        md.append('| %s | %d | %+.4f | %+.4f | %+.4f (%+.4f – %+.4f) | %d | %s |' % (k, x['blocchi'], x['D_dentro'], x['D_fra'], x['contrasto'], x['IC95'][0], x['IC95'][1], x['coppie_dentro_stesso_tipo'], es[k]))
    open(os.path.join(RISULTATI, 'e3b87_grafia_sessione_confronti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
