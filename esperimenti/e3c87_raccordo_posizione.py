# -*- coding: utf-8 -*-
"""Esperimento e3c87: la giuntura e le regole di raccordo vengono dalla posizione nella riga?

Feaster (2022, VOY2022 paper12) avverte che le anomalie y.q e n.q potrebbero venire in parte dalla posizione: le parole
in -n starebbero dove le parole in qo- sono rare. Qui:
(1) giuntura E con due nulli: rimescolamento delle parole nella riga (quello dell'e377) e rimescolamento della parola
    seguente fra le coppie con la stessa posizione nella riga (classe di posizione della coppia), in tutto il testo;
    E_pos conserva le distribuzioni dei segni di bordo per posizione e toglie solo il legame;
(2) regola qo-/o- davanti ai gallows: quota di qo- dopo -y/-o/-d e dopo -n/-r/-s/-m, in ogni classe di posizione;
(3) regola -l/-r: quota di -r davanti a parole che cominciano con a- e davanti a k-, t-, d-, l-, s-, q-, in ogni classe.

Classe di posizione di una coppia (w_i, w_i+1): i = 0, 1, 2, 3, 4 o più; e se w_i+1 è l'ultima parola della riga.

Preregistrazione: preregistrazioni/e3c87.md. Scrive risultati/e3c87_raccordo_posizione.json e .md.
SOLO_CONTROLLI=1: prova del codice su testi finti (legame solo da posizione; legame vero), niente Voynich.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e377_giuntura_gibberish as e377
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
PERM = 50
D = misure.divisore(misure.GLIFI_EVA)
FORTI = ('y', 'o', 'd')
DEBOLI = ('n', 'r', 's', 'm')
DAVANTI_L = ('k', 't', 'd', 'l', 's', 'q')


def classe(i, n):
    return (min(i, 4), i + 2 == n)


def coppie(righe):
    """[(classe, w_i, w_i+1)]"""
    return [(classe(i, len(r)), a, b) for r in righe for i, (a, b) in enumerate(zip(r, r[1:]))]


def mi(c):
    return e377.mi(c)


def e_riga(righe, rnd):
    oss = mi(Counter((a[-1], b[0]) for _, a, b in coppie(righe)))
    nul = [mi(Counter((a[-1], b[0]) for _, a, b in coppie([rnd.sample(r, len(r)) for r in righe]))) for _ in range(PERM)]
    return oss - statistics.mean(nul)


def e_pos(righe, rnd):
    cc = coppie(righe)
    oss = mi(Counter((a[-1], b[0]) for _, a, b in cc))
    per = defaultdict(list)
    for k, (c, a, b) in enumerate(cc):
        per[c].append(k)
    nul = []
    for _ in range(PERM):
        primi = [b[0] for _, _, b in cc]
        nuovo = list(primi)
        for idx in per.values():
            vals = [primi[k] for k in idx]
            rnd.shuffle(vals)
            for k, v in zip(idx, vals):
                nuovo[k] = v
        nul.append(mi(Counter((a[-1], f) for (_, a, _), f in zip(cc, nuovo))))
    return oss - statistics.mean(nul)


def regole(righe):
    qo = defaultdict(lambda: {'forte': [0, 0], 'debole': [0, 0]})
    lr = defaultdict(lambda: {'a': [0, 0], 'altre': [0, 0]})
    for c, a, b in coppie(righe):
        q = e380.ini_qo(b)
        if q and a[-1] in FORTI + DEBOLI:
            t = qo[c]['forte' if a[-1] in FORTI else 'debole']
            t[0] += q[1] == 'qo'
            t[1] += 1
        if a[-1] in ('l', 'r') and len(a) >= 2:
            if b[0] == 'a':
                t = lr[c]['a']
            elif b[0] in DAVANTI_L:
                t = lr[c]['altre']
            else:
                continue
            t[0] += a[-1] == 'r'
            t[1] += 1
    out = OrderedDict()
    for c in sorted(set(qo) | set(lr)):
        x, y = qo[c], lr[c]
        out[repr(c)] = OrderedDict([
            ('qo_dopo_forte', x['forte'][0] / x['forte'][1] if x['forte'][1] else None), ('n_forte', x['forte'][1]),
            ('qo_dopo_debole', x['debole'][0] / x['debole'][1] if x['debole'][1] else None), ('n_debole', x['debole'][1]),
            ('r_davanti_a', y['a'][0] / y['a'][1] if y['a'][1] else None), ('n_a', y['a'][1]),
            ('r_davanti_altre', y['altre'][0] / y['altre'][1] if y['altre'][1] else None), ('n_altre', y['altre'][1])])
    return out


# --------------------------------------------------------------------------- controlli
def finti(rnd, legame):
    """Righe di 8 parole su un alfabeto finto. legame='posizione': la fine di una parola e l'inizio della seguente
    dipendono solo dalla posizione nella riga; legame='vero': l'inizio dipende dalla fine della parola prima."""
    lettere = 'abcdefgh'
    righe = []
    for _ in range(3000):
        r = []
        prec = None
        for i in range(8):
            if legame == 'posizione':
                ini = lettere[(i + rnd.choice((0, 0, 0, 1))) % 8]
                fin = lettere[(i + 3 + rnd.choice((0, 0, 0, 1))) % 8]
            else:
                ini = lettere[(lettere.index(prec) + rnd.choice((0, 0, 0, 1))) % 8] if prec else rnd.choice(lettere)
                fin = rnd.choice(lettere)
            r.append((ini, 'x', fin))
            prec = fin
        righe.append(r)
    return righe


def main():
    rnd = random.Random(3387)
    if SOLO_CONTROLLI:
        for leg in ('posizione', 'vero'):
            rr = finti(rnd, leg)
            print(leg, 'E riga %.4f  E posizione %.4f' % (e_riga(rr, rnd), e_pos(rr, rnd)))
        return
    righe = [[w for w in (tuple(D(x)) for x in r) if w] for pp in e341.pagine().values() for par in pp for r in par]
    righe = [r for r in righe if len(r) >= 2]
    er, ep = e_riga(righe, rnd), e_pos(righe, rnd)
    reg = regole(righe)
    # criterio sulle classi con abbastanza eventi, escluse prima coppia e ultima (bordi della riga)
    medie = [(c, x) for c, x in reg.items() if not eval(c)[1] and eval(c)[0] >= 1]
    ok_qo = [x['qo_dopo_forte'] - x['qo_dopo_debole'] >= 0.20 for _, x in medie if x['n_forte'] >= 100 and x['n_debole'] >= 100]
    ok_lr = [x['r_davanti_a'] - x['r_davanti_altre'] >= 0.20 for _, x in medie if x['n_a'] >= 100 and x['n_altre'] >= 100]
    pos_ok = ep >= 0.8 * er
    esito = OrderedDict([
        ('giuntura', 'non viene dalla posizione' if pos_ok else ('in parte dalla posizione' if ep >= 0.5 * er else 'in gran parte dalla posizione')),
        ('qo/o', ('regge in tutte le posizioni interne (%d classi)' % len(ok_qo)) if ok_qo and all(ok_qo) else ('non in tutte: %d su %d' % (sum(ok_qo), len(ok_qo)))),
        ('-l/-r', ('regge in tutte le posizioni interne (%d classi)' % len(ok_lr)) if ok_lr and all(ok_lr) else ('non in tutte: %d su %d' % (sum(ok_lr), len(ok_lr))))])
    out = OrderedDict([('E_riga', er), ('E_posizione', ep), ('rapporto', ep / er), ('regole_per_posizione', reg), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c87_raccordo_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c87 — Giuntura e raccordo a parità di posizione nella riga', '', 'Preregistrazione: `preregistrazioni/e3c87.md`. Voynich ZL, testo corrente.', '',
          'Giuntura E: nullo nella riga %.4f; nullo a parità di posizione %.4f (rapporto %.2f).' % (er, ep, ep / er), '',
          '| classe (i, ultima) | qo- dopo -y/-o/-d (n) | qo- dopo -n/-r/-s/-m (n) | -r davanti ad a- (n) | -r davanti a k t d l s q (n) |', '|---|---|---|---|---|']
    f = lambda v: '%.2f' % v if v is not None else '–'
    for c, x in reg.items():
        md.append('| %s | %s (%d) | %s (%d) | %s (%d) | %s (%d) |' % (c, f(x['qo_dopo_forte']), x['n_forte'], f(x['qo_dopo_debole']), x['n_debole'], f(x['r_davanti_a']), x['n_a'], f(x['r_davanti_altre']), x['n_altre']))
    md += ['', 'Esito: giuntura **%s**; qo/o **%s**; -l/-r **%s**.' % (esito['giuntura'], esito['qo/o'], esito['-l/-r'])]
    open(os.path.join(RISULTATI, 'e3c87_raccordo_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
