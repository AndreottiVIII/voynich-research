# -*- coding: utf-8 -*-
"""Esperimento e3c10: la memoria (o l'accordo) cala con le lettere o con le parole? Pendenze dentro strati esatti,
che non dipendono dalla forma del calo (sostituisce la regressione lineare dell'e3c09):

- "lettere a parità di parole": pendenza dell'accordo in eccesso sulle lettere in mezzo L dentro ogni strato
  (classe, distanza in parole d);
- "parole a parità di lettere": pendenza sulla distanza d dentro ogni strato (classe, L).

Coppie a distanza 1-7 (nella riga per il Voynich; nel blocco di 25 righe per le lingue). Nullo largo (rimescolamento
dentro il tipo coperto, e3b62), intervalli ricampionando unità intere. Voynich ZL e IT (classi scelte a mano, con e senza
la prima e l'ultima parola della riga) e le 21 misure su lingue dell'e3c08.

Preregistrazione: preregistrazioni/e3c10.md. Scrive risultati/e3c10_strati_lettere_parole.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91
import e3b98_forma_lingue as e3b98
import e3c07_lettere_parole_bilanciate as e3c07
import e3c09_regressione_lettere_parole as e3c09

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 500
BOOT = 2000
MISURE = OrderedDict([('lettere_a_parita_di_parole', ('d', 'L')), ('parole_a_parita_di_lettere', ('L', 'd'))])


def pendenza(st):
    """st (..., strati, 5) = [n, Σx, Σy, Σx², Σxy] -> pendenza dentro gli strati."""
    n, sx, sy, sxx, sxy = (st[..., k] for k in range(5))
    with np.errstate(divide='ignore', invalid='ignore'):
        cov = np.where(n > 0, sxy - sx * sy / n, 0.0).sum(-1)
        var = np.where(n > 0, sxx - sx * sx / n, 0.0).sum(-1)
        return cov / var


def statistiche(strato, x, y, un, n_u, n_s):
    """Somme per (unità, strato)."""
    out = np.zeros((n_u, n_s, 5))
    chiave = un * n_s + strato
    for k, w in enumerate((np.ones_like(x), x, y, x * x, x * y)):
        out[..., k] = np.bincount(chiave, weights=w, minlength=n_u * n_s).reshape(n_u, n_s)
    return out


def misura(uu, ss, classi, rng):
    cc = OrderedDict((k, e3c09.prepara(uu, ss, f)) for k, f in classi.items())
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
    if not cc:
        return None
    n_u = len(uu)
    un = np.concatenate([c['uni'][c['I']] for c in cc.values()])
    cl = np.concatenate([np.full(len(c['I']), n) for n, c in enumerate(cc.values())])
    var = {'d': np.concatenate([c['d'] for c in cc.values()]), 'L': np.concatenate([c['L'] for c in cc.values()])}
    y = np.concatenate([e3c09.eccesso(c, c['val']) for c in cc.values()])
    strati = OrderedDict()
    for nome, (sv, xv) in MISURE.items():
        _, strato = np.unique(cl * 1000 + var[sv].astype(int), return_inverse=True)
        strati[nome] = (strato, var[xv])
    nul = {nome: [] for nome in MISURE}
    for _ in range(PERM):
        yn = np.concatenate([e3c09.eccesso(c, e3b54.rimescola(c, rng)) for c in cc.values()])
        for nome, (strato, x) in strati.items():
            nul[nome].append(pendenza(statistiche(strato, x, yn, un, n_u, int(strato.max()) + 1).sum(0)))
    out = OrderedDict([('coppie', int(len(y)))])
    for nome, (strato, x) in strati.items():
        n_s = int(strato.max()) + 1
        st = statistiche(strato, x, y, un, n_u, n_s)
        oss = float(pendenza(st.sum(0)))
        mu = float(np.mean(nul[nome]))
        boot = []
        for _ in range(BOOT):
            idx = rng.integers(0, n_u, n_u)
            boot.append(pendenza(st[idx].sum(0)) - mu)
        boot = np.array(boot)
        boot = boot[np.isfinite(boot)]
        out[nome] = OrderedDict([('osservato', oss), ('nullo', mu), ('effetto', oss - mu),
                                 ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])])
    return out


def tipo(x):
    l, p = x['lettere_a_parita_di_parole']['IC95'], x['parole_a_parita_di_lettere']['IC95']
    if p[1] < 0:
        return 'cala con le parole'
    if l[1] < 0:
        return 'cala con le lettere, non con le parole'
    return 'nessuno dei due'


def main():
    rng = np.random.default_rng(3310)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    voy = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        for bordi, u in (('senza i bordi', e3c07.senza_bordi(uu)), ('con i bordi', uu)):
            x = misura(u, ss, e3b62.CV, rng)
            x['tipo'] = tipo(x)
            voy['Voynich %s, %s' % (q, bordi)] = x
            print('Voynich', q, bordi, json.dumps(x, ensure_ascii=False), flush=True)
    prima = json.load(open(os.path.join(RISULTATI, 'e3b98_forma_lingue.json'), encoding='utf-8'))['lingue']
    tt = e381.testi()
    testi = OrderedDict()
    for nome in (k for k, x in prima.items() if x['conta'] and x['R'] is not None):
        righe = [r for r in tt[nome + '.txt'] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        f, _ = e3b98.classe_generica([b for u in uu for b in u])
        testi[nome + ' (classe generica)'] = (uu, f)
    for nome, (chiave, t) in e3b91.TESTI.items():
        righe = [r for r in tt[chiave] if r]
        testi[nome + ' (' + ('-o/-a' if t == 'romanzo' else '-us/-a') + ')'] = ([[b] for b in e3b51.blocchi(righe)], e3b91.oa if t == 'romanzo' else e3b91.usa)
    lin = OrderedDict()
    for nome, (uu, f) in testi.items():
        x = misura(uu, [nome] * len(uu), OrderedDict([('x', f)]), rng)
        if x is None:
            print(nome, 'misura non definita', flush=True)
            continue
        x['tipo'] = tipo(x)
        lin[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    t_zl, t_it = voy['Voynich ZL, senza i bordi']['tipo'], voy['Voynich IT, senza i bordi']['tipo']
    esito_v = t_zl if t_zl == t_it else 'incerto (ZL: %s; IT: %s)' % (t_zl, t_it)
    n = len(lin)
    parole = sum(1 for x in lin.values() if x['tipo'] == 'cala con le parole')
    lettere = sum(1 for x in lin.values() if x['tipo'].startswith('cala con le lettere'))
    if parole >= 2 * n / 3 and lettere <= 2:
        esito_l = 'le lingue calano con le parole'
    elif lettere >= n / 3:
        esito_l = 'anche le lingue calano con le lettere'
    else:
        esito_l = 'incerto'
    out = OrderedDict([('voynich', voy), ('lingue', lin), ('lingue_parole', parole), ('lingue_lettere', lettere), ('esito_voynich', esito_v), ('esito_lingue', esito_l)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c10_strati_lettere_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c10 — La memoria cala con le lettere o con le parole? Pendenze dentro strati esatti', '',
          'Preregistrazione: `preregistrazioni/e3c10.md`. Pendenza dell\'accordo in eccesso per una lettera in più a parità di parole e classe, e per una parola in più a parità di lettere e classe, meno il nullo largo; IC 95% per unità.', '',
          '| testo | coppie | per lettera, a parità di parole (IC 95%) | per parola, a parità di lettere (IC 95%) | tipo |', '|---|---|---|---|---|']
    for k, x in list(voy.items()) + list(lin.items()):
        a, b = x['lettere_a_parita_di_parole'], x['parole_a_parita_di_lettere']
        md.append('| %s | %d | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) | %s |' % (k, x['coppie'], a['effetto'], a['IC95'][0], a['IC95'][1], b['effetto'], b['IC95'][0], b['IC95'][1], x['tipo']))
    md += ['', 'Voynich (senza i bordi, ZL e IT): **%s**. Lingue: %d testi, %d calano con le parole, %d con le lettere e non con le parole: **%s**.' % (esito_v, n, parole, lettere, esito_l)]
    open(os.path.join(RISULTATI, 'e3c10_strati_lettere_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
