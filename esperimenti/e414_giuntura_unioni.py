# -*- coding: utf-8 -*-
"""Esperimento 414: sopra la v13, messaggio nel sacco, 12 chiavi per strato. J1: le parole nuove fatte di due parole unite
si accettano solo se le due terne di segni a cavallo della giuntura hanno probabilita' almeno 0,05 nel modello dei segni
delle parole uniche. J2: anche kappa e gamma regolate di nuovo sul pannello con tre bersagli (JSD pagina-manoscritto, quota
fra le 100 piu' frequenti, tipi su parole). Riusa la misura dell'e413.

    PROCESSI=9 python esegui.py e414
    python esperimenti/e414_giuntura_unioni.py --prova     (conteggio di y+o e regolazione breve, nessun giudice)

Preregistrazione: preregistrazioni/e414.md. Scrive risultati/e414_giuntura_unioni.json e .md.
"""
import json, math, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import misure
import e404_parole_note as e404
import e404b_carattere_pagina as e404b
import e413_ritocchi_sacco as e413

GIUNTURA, GIRI = 0.05, 10
D = misure.divisore(misure.GLIFI_EVA)


def v13():
    import pezzi
    return json.load(open(pezzi.PARAMETRI % 'v13', encoding='utf-8'), object_pairs_hook=OrderedDict)


def yo_nuove(rr, conta):
    return sum(a == 'y' and b == 'o' for _, _, ps in rr for w in ps if conta.get(w, 0) < 2 for a, b in zip(D(w), D(w)[1:]))


def regola(giri=GIRI, stampa=True):
    import pezzi
    voy, _ = pezzi.voynich()
    s, _ = pezzi.pezzi()
    x = v13()
    x['forme'] = OrderedDict(x['forme'], giuntura=GIUNTURA)
    b_jsd, b_cento, b_tsp = e404b.jsd_pagina(voy), e413.cento(voy), e404.tipi_su_parole(voy)
    kappa, gamma, traccia, migliore = x['kappa'], x['gamma'], [], None
    for g in range(giri):
        s.FORME, s.POSIZIONALE, s.GAMMA = dict(x['forme']), False, gamma
        t = s.genera(e413.SEME_REGOLAZIONE, theta=None, nuove='inventate', kappa=kappa, posti='modello')
        jsd, cen, tsp = e404b.jsd_pagina(t), e413.cento(t), e404.tipi_su_parole(t)
        scarto = max(abs(jsd / b_jsd - 1), abs(cen / b_cento - 1) * 3, abs(tsp / b_tsp - 1) * 3)
        traccia.append(OrderedDict([('giro', g), ('kappa', kappa), ('gamma', gamma), ('JSD', jsd), ('fra le 100', cen), ('tipi su parole', tsp),
                                    ('y+o nelle nuove', yo_nuove(t, s.conta)), ('scarto', scarto)]))
        if stampa:
            print('giro %2d: kappa %.3f gamma %.3f | JSD %.4f (%.4f) | fra le 100 %.4f (%.4f) | tipi su parole %.4f (%.4f) | y+o nelle nuove %d | scarto %.3f' % (
                g, kappa, gamma, jsd, b_jsd, cen, b_cento, tsp, b_tsp, traccia[-1]['y+o nelle nuove'], scarto), flush=True)
        if migliore is None or scarto < migliore[0]:
            migliore = (scarto, kappa, gamma, jsd, cen, tsp)
        if scarto < 0.02:
            break
        kappa *= math.exp(1.0 * math.log(b_jsd / jsd))
        gamma = min(1.5, max(0.5, gamma + 0.25 * math.log(b_cento / cen) + 0.5 * math.log(tsp / b_tsp)))
    s.GAMMA = 1.0
    y = OrderedDict(x)
    y['kappa'], y['gamma'] = migliore[1], migliore[2]
    return x, y, OrderedDict([('JSD_Voynich', b_jsd), ('cento_Voynich', b_cento), ('tipi_Voynich', b_tsp), ('kappa', migliore[1]), ('gamma', migliore[2]),
                              ('JSD', migliore[3]), ('fra le 100', migliore[4]), ('tipi su parole', migliore[5]), ('scarto', migliore[0]), ('traccia', traccia)])


e413.NOME = 'e414_giuntura_unioni'
e413.TITOLO = 'e414 — Unioni con la giuntura probabile, e tipi su parole'
e413.RIFERIMENTO = ('Riferimento, v13 sulle stesse chiavi: 0,582 ± 0,006 / 0,605 ± 0,006, pagella 15,2, cancello 9 su 12. '
                    'Preregistrazione: `preregistrazioni/e414.md`.')
e413.STRATI = OrderedDict([('J1', 'giuntura probabile nelle unioni'), ('J2', 'J1, kappa e gamma regolate su tre bersagli')])
e413.regola = regola


def prova():
    regola(giri=2)


if __name__ == '__main__':
    if '--prova' in sys.argv:
        prova()
    else:
        e413.main()
