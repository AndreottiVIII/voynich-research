# -*- coding: utf-8 -*-
"""Esperimento e3c53: la finestra (misura corretta dell'e3c48) nelle lingue artificiali con almeno 8.000 parole (righe
finte con le lunghezze del Voynich, unità di 25 righe) e nel gibberish scritto a mano di Gaskell e Bowern (righe vere,
unità = testo, mano = testo). Due definizioni di classe: generica (due ultime lettere più frequenti) e automatica
(e3c01, coppie di lettere interne).

Preregistrazione: preregistrazioni/e3c53.md. Scrive risultati/e3c53_artificiali_gibberish.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e346_gibberish as e346
import e381_parole_intere as e381
import e3b98_forma_lingue as e3b98
import e3c01_alternanze_interne as e3c01
import e3c28_forma_alla_pari as e3c28
import e3c48_finestra_corretta as e3c48
import e3c52_eva_per_scelta as e3c52

RISULTATI = os.path.join(QUI, '..', 'risultati')
MINIMO_PAROLE = 8000


def classi(righe):
    f, (l1, l2) = e3b98.classe_generica(righe)
    scelte, _ = e3c01.alternanze(righe)
    auto = OrderedDict(('%s/%s' % c, e3c01.classe(*c)) for c in scelte)
    return [('generica (-%s/-%s)' % (l1, l2), OrderedDict([('g', f)])), ('automatica (%s)' % ', '.join(auto), auto)]


def main():
    e3c48.PERM = 20
    rng = np.random.default_rng(3353)
    ris = OrderedDict()
    lung = e3c28.lunghezze_voynich()
    for nome, rr in e381.testi().items():
        if not nome.startswith('Conlangs - '):
            continue
        parole = [tuple(w) for r in rr if r for w in r]
        if len(parole) < MINIMO_PAROLE:
            continue
        righe = e3c28.righe_finte(parole, lung)
        for etichetta, cl in classi(righe):
            if not cl:
                continue
            x = e3c48.misura([('x', righe[i:i + 25]) for i in range(0, len(righe), 25)], cl, rng)
            x['voce'], x['gruppo'], x['parole_testo'] = e3c52.voce(x), 'lingua artificiale', len(parole)
            k = '%s, %s' % (nome[len('Conlangs - '):-len('.txt')], etichetta)
            ris[k] = x
            print(k, json.dumps(x, ensure_ascii=False), flush=True)
    gib = e346.da_zip('gibberish_transcriptions.zip', lambda n: True)
    pagine = []
    for nome, rr in gib.items():
        pagine.append((nome, [[tuple(w) for w in r] for r in rr]))
    righe = [r for _, rr in pagine for r in rr]
    for etichetta, cl in classi(righe):
        if not cl:
            continue
        x = e3c48.misura(pagine, cl, rng)
        x['voce'], x['gruppo'], x['parole_testo'] = e3c52.voce(x), 'gibberish', sum(len(r) for r in righe)
        x['non_informativo'] = x['voce'] == 'nessun accordo chiaro' and x['K1_IC95'][1] >= 0.131
        k = 'gibberish scritto a mano (%d testi), %s' % (len(pagine), etichetta)
        ris[k] = x
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    art = [k for k, x in ris.items() if x['gruppo'] == 'lingua artificiale' and x['voce'] == 'finestra']
    esito_a = 'nessuna lingua artificiale ha la finestra' if not art else 'finestra in: ' + '; '.join(art)
    esito_g = OrderedDict((k, x['voce'] + (' (non informativo)' if x['non_informativo'] else '')) for k, x in ris.items() if x['gruppo'] == 'gibberish')
    out = OrderedDict([('misure', ris), ('esito_artificiali', esito_a), ('esito_gibberish', esito_g)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c53_artificiali_gibberish.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c53 — Lingue artificiali e gibberish scritto a mano, con la misura corretta', '',
          'Preregistrazione: `preregistrazioni/e3c53.md`. Voynich (e3c48, ZL): K corretto +0,131 / +0,093 / +0,086, r 0,68; per scelta (e3c52): k/t +0,136, -ey/-dy +0,176.', '',
          '| testo, classe | parole testo | parole misurate | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) | voce |', '|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s |' % (
            k, x['parole_testo'], x['parole'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2],
            x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['r_IC95'][0], x['r_IC95'][1], x['voce']))
    md += ['', 'Esito lingue artificiali: **%s**.' % esito_a, ''] + ['Gibberish, %s: **%s**.' % kv for kv in esito_g.items()]
    open(os.path.join(RISULTATI, 'e3c53_artificiali_gibberish.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
