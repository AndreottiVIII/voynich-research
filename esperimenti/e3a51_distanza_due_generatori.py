# -*- coding: utf-8 -*-
"""Esperimento e3a51: legame a distanza 2 a parita' della parola in mezzo (e3a07 e e3a03) nei generatori pubblicati
(Naibbe, U2, U3, Timm e Schinner) e nel Voynich.

Preregistrazione: preregistrazioni/e3a51.md. Scrive risultati/e3a51_distanza_due_generatori.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e341_fonti as e341
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def terne(pagine, per_pagina):
    out = []
    for pg, righe in pagine:
        for r in righe:
            for a, b, c in zip(r, r[1:], r[2:]):
                out.append((((pg, b) if per_pagina else (b,)), a[-1], c[0]))
    return out


def main():
    rnd = random.Random(3151)
    e134.controlla()
    corpi = OrderedDict()
    voy = []
    for pg, pars in e341.pagine().items():
        voy.append((pg, [[w for w in (tuple(D(x)) for x in r) if w] for par in pars for r in par]))
    corpi['Voynich'] = voy
    for k, v in e134.testi().items():
        if k == 'Voynich':
            continue
        rr = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
        rr = [r for r in rr if r]
        corpi[k] = [(i, rr[i:i + 29]) for i in range(0, len(rr), 29)]
    for s in (1, 19):
        corpi['Timm e Schinner, seme %d' % s] = [(i, [[tuple(D(w)) for w in r] for r in p]) for i, p in enumerate(e337.pagine_ts(s))]
    ris = OrderedDict()
    for nome, pp in corpi.items():
        a = e380.prova(terne(pp, True), rnd, 1000)
        b = e380.prova(terne(pp, False), rnd, 1000)
        es = 'legame a distanza 2' if a['z'] > 3 else ('nessun legame' if abs(a['z']) < 2 else 'incerto')
        ris[nome] = OrderedDict([('terne', a['eventi']), ('E_pagina', a['E']), ('z_pagina', a['z']), ('E_senza_pagina', b['E']), ('z_senza_pagina', b['z']), ('esito', es)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    nk = [k for k in ris if 'Naibbe' in k][0]
    zn = ris[nk]['z_pagina']
    esito = 'la misura vede il cifrario verboso' if zn > 3 else ('non lo vede' if abs(zn) < 2 else 'incerto')
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a51_distanza_due_generatori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a51 — Il legame a distanza 2 nei generatori pubblicati, cifrario Naibbe compreso', '', 'Preregistrazione: `preregistrazioni/e3a51.md`.', '',
          '| testo | terne | E (nullo nella pagina) | z | E (senza pagina) | z | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %.4f | %.1f | %.4f | %.1f | %s |' % (k, x['terne'], x['E_pagina'], x['z_pagina'], x['E_senza_pagina'], x['z_senza_pagina'], x['esito']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a51_distanza_due_generatori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
