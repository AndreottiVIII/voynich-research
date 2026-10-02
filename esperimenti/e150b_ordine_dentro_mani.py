# -*- coding: utf-8 -*-
"""Esperimento 150b: l'ordine ricostruito batte la rilegatura anche dentro i gruppi di stessa mano e lingua?

Preregistrazione: preregistrazioni/e150b.md. Scrive risultati/e150b_ordine_dentro_mani.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e148_bifogli as e148
import e150_ordine_scrittura as e150

RISULTATI = os.path.join(QUI, '..', 'risultati')
MINIMO = 6


def main():
    U = e150.unita()
    gruppi = defaultdict(list)
    for n, u in U.items():
        gruppi[(u['mano'], u['lingua'])].append(n)
    gruppi = OrderedDict((k, v) for k, v in sorted(gruppi.items(), key=lambda kv: -len(kv[1])) if len(v) >= MINIMO)
    print('gruppi:', {('%s/%s' % k): len(v) for k, v in gruppi.items()}, flush=True)
    ris = OrderedDict([('gruppi', {('mano %s, lingua %s' % k): len(v) for k, v in gruppi.items()}), ('divisioni', OrderedDict())])
    vitt_tot, vitt_grande = 0, 0
    grande = next(iter(gruppi))
    for s in e150.DIVISIONI:
        tot_r = tot_l = pesi = 0.0
        per = OrderedDict()
        for k, nomi in gruppi.items():
            sub = OrderedDict((n, U[n]) for n in nomi)
            nn, SA, SB = e150.matrice(sub, None, s)
            rileg = sorted(range(len(nn)), key=lambda i: sub[nn[i]]['primo'])
            ric = e150.ricostruisci(SA)
            vr, vl = e150.valore(ric, SB), e150.valore(rileg, SB)
            w = len(nn) - 1
            tot_r += w * vr
            tot_l += w * vl
            pesi += w
            per['mano %s, lingua %s' % k] = (vr, vl)
            if k == grande:
                vitt_grande += vr > vl
        vitt_tot += tot_r > tot_l
        ris['divisioni'][s] = OrderedDict([('ricostruito', tot_r / pesi), ('rilegatura', tot_l / pesi), ('per_gruppo', per)])
        print('divisione %2d | ricostruito %.4f rilegatura %.4f | %s' % (s, tot_r / pesi, tot_l / pesi,
                                                                        ' '.join('%s %.3f/%.3f' % (g.replace('mano ', 'm').replace(', lingua ', '/'), a, b) for g, (a, b) in per.items())), flush=True)
    esito = vitt_tot >= 18 and vitt_grande >= 18
    ris['vittorie_totali'], ris['vittorie_gruppo_grande'], ris['ordine_dentro_i_gruppi'] = vitt_tot, vitt_grande, esito
    print('vittorie totali %d/20, gruppo piu\' grande %d/20 | ordine dentro i gruppi: %s' % (vitt_tot, vitt_grande, esito))
    with open(os.path.join(RISULTATI, 'e150b_ordine_dentro_mani.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e150b — Ordine di scrittura dentro la stessa mano e lingua?', '', 'Gruppi (mano, lingua) con almeno %d unità: %s. Preregistrazione: `preregistrazioni/e150b.md`.' % (
        MINIMO, ', '.join('%s (%d)' % kv for kv in ris['gruppi'].items())), '', '| divisione | ricostruito (B) | rilegatura (B) |', '|---|---|---|']
    for s, r in ris['divisioni'].items():
        out.append('| %d | %.4f | %.4f |' % (s, r['ricostruito'], r['rilegatura']))
    out += ['', 'Vittorie del ricostruito: **%d su 20** in totale, **%d su 20** nel gruppo più grande. Ordine dentro i gruppi: **%s**.' % (
        vitt_tot, vitt_grande, 'sì' if esito else 'no')]
    with open(os.path.join(RISULTATI, 'e150b_ordine_dentro_mani.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
