# -*- coding: utf-8 -*-
"""Esperimento e3b94: memoria (metodo finale) con e senza le 20 parole coperte più frequenti di ogni classe, nel
Voynich e nelle lingue con accordo (italiano, spagnolo, latino).

Preregistrazione: preregistrazioni/e3b94.md. Scrive risultati/e3b94_parole_frequenti.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b91_accordo_lingue as e3b91

RISULTATI = os.path.join(QUI, '..', 'risultati')
N_FREQ = 20


def senza_frequenti(f, unita):
    c = Counter(x[1] for u in unita for s in u for w in s for x in [f(w)] if x)
    via = {t for t, _ in c.most_common(N_FREQ)}
    return lambda w: (lambda x: x if x and x[1] not in via else None)(f(w))


def misura(unita, strati, classi, rng):
    cc = OrderedDict((k, e3b62.prepara(unita, strati, f)) for k, f in classi.items())
    pr = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
    return OrderedDict([('coppie_vicine', pr['coppie_vicine']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def main():
    rng = np.random.default_rng(3294)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    testi = OrderedDict()
    uu, ss = e3b62.voynich(e341.pagine(), mano)
    testi['Voynich ZL'] = (uu, ss, e3b62.CV)
    tt = e381.testi()
    for nome in ('italiano NT (Diodati)', 'spagnolo NT', 'latino NT (Vulgata)'):
        chiave, tipo = e3b91.TESTI[nome]
        righe = [r for r in tt[chiave] if r]
        u = [[b] for b in e3b51.blocchi(righe)]
        testi[nome] = (u, [nome] * len(u), OrderedDict([('x', e3b91.oa if tipo == 'romanzo' else e3b91.usa)]))
    ris = OrderedDict()
    for nome, (u, s, classi) in testi.items():
        tutte = misura(u, s, classi, rng)
        ridotte = OrderedDict((k, senza_frequenti(f, u)) for k, f in classi.items())
        senza = misura(u, s, ridotte, rng)
        ris[nome] = OrderedDict([('tutte', tutte), ('senza_frequenti', senza), ('tenuta', senza['effetto'] / tutte['effetto'] if tutte['effetto'] else None)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    tv = ris['Voynich ZL']['tenuta']
    tl = [ris[k]['tenuta'] for k in ris if k != 'Voynich ZL']
    ml = sum(tl) / len(tl)
    if ml < 0.5 and tv >= 0.75:
        esito = "l'accordo delle lingue dipende dalle parole frequenti, la memoria del Voynich no"
    elif (ml >= 0.75 and tv >= 0.75) or (ml < 0.5 and tv < 0.5):
        esito = 'nessuna differenza'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('tenuta_media_lingue', ml), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b94_parole_frequenti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b94 — La "memoria" dipende dalle parole più frequenti?', '', 'Preregistrazione: `preregistrazioni/e3b94.md`.', '',
          '| testo | effetto con tutte (IC 95%) | effetto senza le 20 più frequenti (IC 95%) | tenuta |', '|---|---|---|---|']
    for k, x in ris.items():
        a, b = x['tutte'], x['senza_frequenti']
        md.append('| %s | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) | %.2f |' % (k, a['effetto'], a['IC95'][0], a['IC95'][1], b['effetto'], b['IC95'][0], b['IC95'][1], x['tenuta']))
    md += ['', 'Tenuta media delle lingue %.2f. Esito: **%s**.' % (ml, esito)]
    open(os.path.join(RISULTATI, 'e3b94_parole_frequenti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
