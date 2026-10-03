# -*- coding: utf-8 -*-
"""Esperimento 358: passaggi di ripresa (fine di P -> inizio di Q, meno il contrario) fra le quattro pagine dei bifogli,
per distinguere una scrittura a bifoglio piegato (recto -> verso dello stesso foglio) da una a bifoglio aperto (pagine
della stessa faccia della pergamena).

Preregistrazione: preregistrazioni/e358.md. Scrive risultati/e358_ordine_bifoglio.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e308_libro_fisico as e308
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
PASSAGGI = [('Xr', 'Xv'), ('Yr', 'Yv'), ('Xv', 'Yr'), ('Yv', 'Xr'), ('Xv', 'Xr'), ('Yv', 'Yr'), ('Yr', 'Xv'), ('Xr', 'Yv')]


def main():
    rnd = random.Random(358)
    testa = e308.intestazioni()
    pag = e341.pagine()
    righe = {p: [r for par in pars for r in par] for p, pars in pag.items()}
    bif = defaultdict(dict)
    for p, h in testa.items():
        if h['Q'] and h['B'] and p in righe and len(righe[p]) >= 6 and h['lato'] in ('r', 'v'):
            bif[(h['Q'], h['B'])].setdefault(h['F'], {})[h['lato']] = p
    casi = []
    for b, fogli in bif.items():
        if len(fogli) != 2:
            continue
        f1, f2 = sorted(fogli, key=lambda f: min(testa[p]['ordine'] for p in fogli[f].values()))
        if all(l in fogli[f1] for l in 'rv') and all(l in fogli[f2] for l in 'rv'):
            casi.append((b, {'Xr': fogli[f1]['r'], 'Xv': fogli[f1]['v'], 'Yr': fogli[f2]['r'], 'Yv': fogli[f2]['v']}))

    def passaggio(P, Q):
        a, b = righe[P], righe[Q]
        return e341.ripresa(a[-3:], b[:3]) - e341.ripresa(a[:3], b[-3:])
    out = OrderedDict()
    for p, q in PASSAGGI:
        d = [passaggio(c[p], c[q]) for _, c in casi]
        v, z = e341.segno_flip(d, rnd)
        out['%s→%s' % (p, q)] = OrderedDict([('bifogli', len(d)), ('media', v), ('z', z)])
    piegato = [out['Xr→Xv']['z'], out['Yr→Yv']['z']]
    aperto = [out['Xv→Yr']['z'], out['Yv→Xr']['z']]
    zp = sum(piegato) / 2 ** 0.5
    za = sum(aperto) / 2 ** 0.5
    if zp > 3 and za <= 3:
        esito = 'scritto piegato'
    elif za > 3 and zp <= 3:
        esito = 'scritto aperto'
    elif max(zp, za) < 2:
        esito = 'nessun ordine visibile'
    else:
        esito = 'incerto'
    res = OrderedDict([('bifogli', len(casi)), ('passaggi', out), ('z_piegato', zp), ('z_aperto', za), ('esito', esito)])
    json.dump(res, open(os.path.join(RISULTATI, 'e358_ordine_bifoglio.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e358 — In che ordine sono state scritte le quattro pagine di un bifoglio?', '', 'Preregistrazione: `preregistrazioni/e358.md`. %d bifogli completi.' % len(casi), '',
          '| passaggio | media (fine→inizio meno inizio→fine) | z |', '|---|---|---|']
    for k, v in out.items():
        md.append('| %s | %+.4f | %.1f |' % (k, v['media'], v['z']))
    md += ['', 'Piegato (Xr→Xv e Yr→Yv insieme): z %.1f. Aperto (Xv→Yr e Yv→Xr insieme): z %.1f. Esito: **%s**.' % (zp, za, esito)]
    open(os.path.join(RISULTATI, 'e358_ordine_bifoglio.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
