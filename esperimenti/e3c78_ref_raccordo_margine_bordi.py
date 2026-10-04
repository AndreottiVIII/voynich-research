# -*- coding: utf-8 -*-
"""Esperimento e3c78: batteria scribi sugli scribi tedeschi del 1350 – 1500 (ReF), parte 2: raccordo (e3b58 / e3c60),
margine sinistro (e3a33 / e3c63), forme di bordo riga (e389 / e3c64), ripetizioni di parole vicine (e3b25 / e3c65).
Stesso campione dell'e3c77 (prime 6.000 parole di ogni manoscritto); Voynich ZL nella stessa esecuzione.

Preregistrazione: preregistrazioni/e3c78.md. Scrive risultati/e3c78_ref_raccordo_margine_bordi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e3a27_margine_robustezza as e3a27
import e3a33_margine_corretto as e3a33
import e3b25_ripetizioni_grezze as e3b25
import e3b54_memoria_oltre_parole as e3b54
import e3b58_raccordo_scriba as e3b58
import e3b62_memoria_nullo_largo as e3b62
import e389_varianti_bordo as e389
import e3c60_raccordo_scribi as e3c60
import e3c63_margine_scribi as e3c63
import e3c64_bordi_scribi as e3c64
import e3c77_ref_finestra_deriva as e3c77

RISULTATI = os.path.join(QUI, '..', 'risultati')
BORDI = [('ſ/s', 'inizio'), ('ſ/s', 'fine'), ('u/v', 'inizio'), ('u/v', 'fine'), ('i/j', 'inizio'), ('i/j', 'fine'), ('i/y', 'inizio'), ('i/y', 'fine'),
         ('í/i', 'inizio'), ('w/u', 'inizio'), ('w/u', 'fine'), ('uͦ/u', 'fine'), ('z/cz', 'inizio')]


def main():
    e3b58.PERM = 1000
    e3a33.PERM = 1000
    e389.PERM = 300
    rnd = random.Random(3378)
    rs = np.random.RandomState(3378)
    pagine = e3c77.pagine_ref()
    per_ms = OrderedDict()
    for sigla, rr in pagine:
        per_ms.setdefault(sigla, []).append(rr)
    voy_pag = [rr for rr in ([[w for w in (tuple(e3b62.D(x)) for x in r) if w] for par in pars for r in par] for pars in e341.pagine().values()) if rr]
    ris = OrderedDict()
    # 1. raccordo
    rac = OrderedDict()
    for nome, f, dove in (('Voynich ZL, qo/o a inizio parola', e3b54.v_qo, 'inizio'), ('Voynich ZL, -l/-r a fine parola', e3c60.v_lr, 'fine')):
        rac[nome] = e3b58.prova(*e3c60.eventi(voy_pag, f, dove), np.random.default_rng(rnd.randrange(1 << 30)))
    fn = {n: (a, b) for n, a, b in e3c77.SCELTE}
    for nome, dove in BORDI:
        a, b = fn[nome]
        rac['ReF, %s a %s parola' % (nome, dove)] = x = e3b58.prova(*e3c60.eventi([rr for _, rr in pagine], e3c60.ai_bordi(a, b, dove), dove), np.random.default_rng(rnd.randrange(1 << 30)))
        print('raccordo', nome, dove, json.dumps(x), flush=True)
    rif = min(rac['Voynich ZL, qo/o a inizio parola']['effetto_su_entropia'], rac['Voynich ZL, -l/-r a fine parola']['effetto_su_entropia'])
    sc = [(k, x) for k, x in rac.items() if k.startswith('ReF')]
    forti = [k for k, x in sc if x['p'] < 0.01 and x['effetto_su_entropia'] >= rif / 2]
    deboli = [k for k, x in sc if x['p'] < 0.01 and x['effetto_su_entropia'] < rif / 2]
    ris['raccordo'] = OrderedDict([('misure', rac), ('forti', forti), ('deboli', deboli),
                                   ('esito', 'almeno una scelta con un raccordo grande come il Voynich' if forti else ('raccordo più debole della metà del Voynich' if deboli else 'nessun raccordo'))])
    # 2. margine sinistro, manoscritto per manoscritto
    marg = OrderedDict()
    marg['Voynich ZL'] = e3c63.misura(e3a33.righe_utili(e3a27.paragrafi('ZL')), rnd)
    for sigla, pp in per_ms.items():
        pars = [[(r[0][0], None) for r in rr if r and r[0]] for rr in pp]
        pars = [p for p in pars if len(p) >= 2]
        if sum(len(p) for p in pars) >= 200:
            marg[sigla] = e3c63.misura(pars, rnd)
    ev = OrderedDict((k, [s for s, x in v.items() if x['esito'] == 'evitato']) for k, v in marg.items())
    gen = [k for k in ev if k != 'Voynich ZL' and len(ev[k]) >= 3]
    qual = [k for k in ev if k != 'Voynich ZL' and ev[k]]
    ris['margine'] = OrderedDict([('evitati', ev), ('manoscritti', len(ev) - 1), ('che_evitano_in_generale', gen), ('con_qualche_evitato', qual),
                                  ('esito', 'gli scribi tedeschi evitano gli inizi ripetuti come il Voynich' if len(gen) >= 2 else ('nessuno scriba evita gli inizi ripetuti' if not qual else 'in parte'))])
    print('margine', json.dumps(ris['margine']['esito']), len(gen), len(qual), flush=True)
    # 3. forme di bordo (tutti i manoscritti insieme, strato = manoscritto)
    f_v, i_v = e3c64.eventi_voynich()
    fine, inizio = [], []
    for sigla, rr in pagine:
        for r in rr:
            n = len(r)
            for j, w in enumerate(r):
                w = tuple(w)
                if len(w) < 2 or n < 2:
                    continue
                mezzo = 0 < j < n - 1
                if mezzo or j == n - 1:
                    fine.append(((sigla, w[:-1]), j == n - 1, w[-1]))
                if (mezzo or j == 0) and not e3c64.maiuscola(w[0]):
                    inizio.append(((sigla, w[1:]), j == 0, w[0]))
    bor = OrderedDict()
    bor['Voynich ZL'] = OrderedDict([('fine riga', e389.analizza(f_v, rs)), ('inizio riga', e389.analizza(i_v, rs))])
    bor['ReF'] = OrderedDict([('fine riga', e389.analizza(fine, rs)), ('inizio riga', e389.analizza(inizio, rs))])
    soglie = OrderedDict((b, e3c64.massimo(bor['Voynich ZL'][b])[0] / 2) for b in ('fine riga', 'inizio riga'))
    mx = OrderedDict((b, e3c64.massimo(bor['ReF'][b])) for b in ('fine riga', 'inizio riga'))
    forti_b = [b for b, m in mx.items() if m and m[0] >= soglie[b]]
    ris['bordi'] = OrderedDict([('misure', bor), ('soglie', soglie), ('massimi_ReF', OrderedDict((b, list(m) if m else None) for b, m in mx.items())),
                                ('esito', 'forme di bordo forti come il Voynich' if forti_b else ('forme di bordo più deboli della metà del Voynich' if any(mx.values()) else 'nessuna forma di bordo'))])
    print('bordi', json.dumps(ris['bordi']['massimi_ReF'], ensure_ascii=False, default=float), flush=True)
    # 4. ripetizioni, manoscritto per manoscritto
    rip = OrderedDict([('Voynich ZL', e3b25.quote([r for p in voy_pag for r in p]))])
    for sigla, pp in per_ms.items():
        rip[sigla] = e3b25.quote([[tuple(w) for w in r] for rr in pp for r in rr])
    v = rip['Voynich ZL']
    come = [k for k, x in rip.items() if k != 'Voynich ZL' and x['ripetizione'] is not None and x['ripetizione'] >= v['ripetizione'] / 2 and x['quasi'] >= v['quasi'] / 2]
    vals = sorted(x['ripetizione'] for k, x in rip.items() if k != 'Voynich ZL' and x['ripetizione'] is not None)
    qv = sorted(x['quasi'] for k, x in rip.items() if k != 'Voynich ZL' and x['quasi'] is not None)
    ris['ripetizioni'] = OrderedDict([('misure', rip), ('mediana', [float(np.median(vals)), float(np.median(qv))]), ('massimo', [vals[-1], qv[-1]]), ('come_voynich', come),
                                      ('esito', ('ripetono come il Voynich: ' + ', '.join(come)) if come else 'nessuno scriba tedesco ripete come il Voynich')])
    out = OrderedDict([('risultati', ris)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c78_ref_raccordo_margine_bordi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c78 — Scribi tedeschi 1350 – 1500 (ReF): raccordo, margine, bordi, ripetizioni', '', 'Preregistrazione: `preregistrazioni/e3c78.md`. Stesso campione dell\'e3c77.', '',
          '## Raccordo', '', '| testo, scelta | occorrenze | effetto / entropia | z | p |', '|---|---|---|---|---|']
    for k, x in rac.items():
        md.append('| %s | %d | %+.3f | %+.1f | %.3f |' % (k, x['occorrenze'], x['effetto_su_entropia'] or 0, x['z'], x['p']))
    md += ['', 'Esito: **%s**.' % ris['raccordo']['esito'], '', '## Margine sinistro', '',
           'Voynich ZL: evitati %s. Manoscritti tedeschi misurati: %d; con almeno tre inizi evitati: %d (%s); con almeno uno: %d.' % (
               ', '.join(ev['Voynich ZL']), len(ev) - 1, len(gen), ', '.join(gen) or 'nessuno', len(qual)), '', 'Esito: **%s**.' % ris['margine']['esito'], '',
           '## Forme di bordo riga', '']
    for b in ('fine riga', 'inizio riga'):
        mv = e3c64.massimo(bor['Voynich ZL'][b])
        mr = mx[b]
        md.append('- %s: Voynich %s %+.3f (z %.1f); ReF %s.' % (b, mv[1], mv[0], mv[2], ('%s %+.3f (z %.1f)' % (mr[1], mr[0], mr[2])) if mr else 'nessun segno con z > 3'))
    md += ['', 'Esito: **%s**.' % ris['bordi']['esito'], '', '## Ripetizioni di parole vicine', '',
           'Voynich ZL: %.4f identiche, %.4f a una modifica. Manoscritti tedeschi: mediana %.4f / %.4f, massimo %.4f / %.4f.' % (v['ripetizione'], v['quasi'], *ris['ripetizioni']['mediana'], *ris['ripetizioni']['massimo']),
           '', 'Esito: **%s**.' % ris['ripetizioni']['esito'], '', 'Fonte: ReF 1.0.2, CC-BY-SA 4.0. I file non sono nel repository.']
    open(os.path.join(RISULTATI, 'e3c78_ref_raccordo_margine_bordi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
