# -*- coding: utf-8 -*-
"""Esperimento e3b70: intervalli bootstrap per unità intere (pagine o blocchi) dell'effetto di memoria dell'e3b62
(M − media del nullo largo).

Preregistrazione: preregistrazioni/e3b70.md. Scrive risultati/e3b70_memoria_intervalli.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e134_generatori_esterni as e134
import e337_posizione as e337
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def per_unita(c):
    """Array (unità, gruppo, [accordi, attesi, coppie]) per una classe preparata con e3b62.prepara."""
    n_u = c['n_unita']
    out = np.zeros((n_u, 2, 3))
    if not len(c['I']):
        return out
    val = c['val']
    U = np.bincount(c['uni'], weights=val, minlength=n_u)
    vi, vj = val[c['I']], val[c['J']]
    u = c['uni'][c['I']]
    p = (U[u] - vi - vj) / (c['T'][u] - 2)
    att = p * p + (1 - p) * (1 - p)
    ok = (vi == vj).astype(float)
    for g in (0, 1):
        m = c['G'] == g
        out[:, g, 0] = np.bincount(u[m], weights=ok[m], minlength=n_u)
        out[:, g, 1] = np.bincount(u[m], weights=att[m], minlength=n_u)
        out[:, g, 2] = np.bincount(u[m], minlength=n_u)
    return out


def emme(tab):
    k = []
    for g in (0, 1):
        o, a, n = tab[g]
        if n - a <= 0:
            return None
        k.append((o - a) / (n - a))
    return k[0] - k[1]


def intervallo(arrs, nullo, rng):
    """arrs: lista di array per unità (stesse unità); nullo: media del nullo (e3b62)."""
    tot = sum(arrs)
    m = emme(tot.sum(0))
    n_u = tot.shape[0]
    boot = []
    for _ in range(BOOT):
        idx = rng.integers(0, n_u, n_u)
        x = emme(tot[idx].sum(0))
        if x is not None:
            boot.append(x - nullo)
    boot.sort()
    return OrderedDict([('effetto', m - nullo if m is not None else None), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]] if boot else None)])


def main():
    rng = np.random.default_rng(3270)
    prima = json.load(open(os.path.join(RISULTATI, 'e3b62_memoria_nullo_largo.json'), encoding='utf-8'))['gruppi']
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    zl, it = e341.pagine(), e3b45.pagine_it()
    gruppi = OrderedDict()
    for nome, pd, solo in (('Voynich ZL, mano 1', zl, '1'), ('Voynich ZL, mano 2', zl, '2'), ('Voynich ZL, mano 3', zl, '3'),
                           ('Voynich ZL, tutto', zl, None), ('Voynich IT, tutto', it, None)):
        uu, ss = e3b62.voynich(pd, mano, solo)
        gruppi[nome] = OrderedDict((k, per_unita(e3b62.prepara(uu, ss, f))) for k, f in e3b62.CV.items())
    tt = e381.testi()
    nat = OrderedDict()
    for nome, chiave in e3b54.STORICI.items():
        righe = [r for r in tt[chiave] if r]
        uu = [[b] for b in e3b51.blocchi(righe)]
        ss = [nome] * len(uu)
        nat['%s, i/y' % nome] = (len(gruppi), per_unita(e3b62.prepara(uu, ss, e3b54.classe_iy(righe))))
        if nome == 'Hatton Gospels':
            nat['Hatton Gospels, þ/ð a inizio parola'] = (0, per_unita(e3b62.prepara(uu, ss, e3b54.v_th_ini)))
            nat['Hatton Gospels, þ/ð dentro la parola'] = (0, per_unita(e3b62.prepara(uu, ss, e3b54.v_th_int)))
    e134.controlla()
    gen = OrderedDict()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            gen[k] = [r for r in ([w for w in (tuple(e3b62.D(x)) for x in ps) if w] for _, ps in v) if r]
    gen['Timm e Schinner, seme 1'] = [r for r in ([tuple(e3b62.D(w)) for w in r] for p in e337.pagine_ts(1) for r in p) if r]
    for k, righe in gen.items():
        uu = [righe[i:i + 25] for i in range(0, len(righe), 25)]
        gruppi[k] = OrderedDict((c, per_unita(e3b62.prepara(uu, [k] * len(uu), f))) for c, f in e3b62.CV.items())
    ris = OrderedDict()
    for nome, cl in gruppi.items():
        ris[nome] = intervallo(list(cl.values()), prima[nome]['insieme']['nullo'], rng)
        print(nome, json.dumps(ris[nome]), flush=True)
    for k, (_, arr) in nat.items():
        ris[k] = intervallo([arr], prima['varianti naturali'][k]['nullo'], rng)
        print(k, json.dumps(ris[k]), flush=True)
    # insieme naturale: le unità dei tre testi sono diverse, quindi si concatenano per testo
    blocchi = OrderedDict()
    for k, (_, arr) in nat.items():
        testo = k.split(',')[0]
        blocchi.setdefault(testo, []).append(arr)
    concat = np.concatenate([sum(v) for v in blocchi.values()], axis=0)
    ris['varianti naturali, insieme'] = intervallo([concat], prima['varianti naturali']['insieme']['nullo'], rng)
    print('naturali insieme', json.dumps(ris['varianti naturali, insieme']), flush=True)
    es = OrderedDict()
    for k in ('Voynich ZL, tutto', 'Voynich IT, tutto'):
        es[k] = 'memoria oltre le parole' if ris[k]['IC95'][0] > 0 else 'non dimostrata'
    mani = [ris['Voynich ZL, mano %s' % h]['IC95'] for h in '123']
    separate = any(a[1] < b[0] or b[1] < a[0] for i, a in enumerate(mani) for b in mani[i + 1:])
    es['mani'] = 'le mani differiscono' if separate else 'differenze non dimostrate'
    for k in ('Hatton Gospels, þ/ð a inizio parola', 'varianti naturali, insieme'):
        es[k] = 'memoria anche nello scriba vero' if ris[k]['IC95'][0] > 0 else 'non dimostrata'
    for k in gen:
        es[k] = 'memoria' if ris[k]['IC95'][0] > 0 else 'nessuna memoria'
    out = OrderedDict([('intervalli', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b70_memoria_intervalli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b70 — Intervalli per pagine intere per la memoria oltre le parole', '', 'Preregistrazione: `preregistrazioni/e3b70.md`. Effetto = M − media del nullo largo dell\'e3b62; intervallo bootstrap per unità.', '',
          '| gruppo | effetto | IC 95% |', '|---|---|---|']
    md += ['| %s | %+.4f | %+.4f – %+.4f |' % (k, x['effetto'], x['IC95'][0], x['IC95'][1]) for k, x in ris.items() if x['effetto'] is not None and x['IC95']]
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b70_memoria_intervalli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
