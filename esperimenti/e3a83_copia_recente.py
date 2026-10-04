# -*- coding: utf-8 -*-
"""Esperimento e3a83: posizione relativa, nella riga sopra, delle parole uguali o a una modifica (fonti), contro la
stessa misura con un'altra riga del paragrafo (nullo).

Preregistrazione: preregistrazioni/e3a83.md. Scrive risultati/e3a83_copia_recente.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NULLI = 20
BOOT = 1000


def posizioni(w, riga, sim):
    n = len(riga)
    return [k / (n - 1) for k, v in enumerate(riga) if v in sim[w]]


def paragrafo(par, rnd):
    """(somma posizioni oss., n oss., [terzi oss.], somma pos. nullo, n nullo, [terzi nullo], parole)."""
    sim = e385.simili_unita(par)
    so = no = sn = nn = 0.0
    to, tn = [0, 0, 0], [0.0, 0.0, 0.0]
    parole = 0
    for i in range(1, len(par)):
        sopra = par[i - 1]
        altre = [j for j in range(len(par)) if j not in (i, i - 1) and len(par[j]) >= 4]
        if len(sopra) < 4 or not altre:
            continue
        scelte = [rnd.choice(altre) for _ in range(NULLI)]
        for w in par[i]:
            if len(w) < 3:
                continue
            parole += 1
            for x in posizioni(w, sopra, sim):
                so += x
                no += 1
                to[min(int(x * 3), 2)] += 1
            for j in scelte:
                for x in posizioni(w, par[j], sim):
                    sn += x / NULLI
                    nn += 1 / NULLI
                    tn[min(int(x * 3), 2)] += 1 / NULLI
    return so, no, to, sn, nn, tn, parole


def sintesi(blocchi):
    so = sum(b[0] for b in blocchi)
    no = sum(b[1] for b in blocchi)
    sn = sum(b[3] for b in blocchi)
    nn = sum(b[4] for b in blocchi)
    return (so / no if no else 0.0) - (sn / nn if nn else 0.0), so / no if no else None, sn / nn if nn else None


def main():
    rnd = random.Random(3183)
    blocchi = []
    for pars in e341.pagine().values():
        for par in pars:
            pp = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            pp = [r for r in pp if r]
            if len(pp) >= 3:
                b = paragrafo(pp, rnd)
                if b[6]:
                    blocchi.append(b)
    d, mo, mn = sintesi(blocchi)
    boot = sorted(sintesi([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi])[0] for _ in range(BOOT))
    ic = [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]]
    parole = sum(b[6] for b in blocchi)
    terzi = OrderedDict()
    for t, nome in enumerate(('primo terzo', 'secondo terzo', 'ultimo terzo')):
        o = sum(b[2][t] for b in blocchi) / parole
        n = sum(b[5][t] for b in blocchi) / parole
        terzi[nome] = OrderedDict([('osservate_per_parola', o), ('nullo_per_parola', n), ('eccesso', o - n)])
    esito = 'copia di preferenza dalla fine della riga sopra' if ic[0] > 0 else ('dall\'inizio' if ic[1] < 0 else 'da tutta la riga')
    out = OrderedDict([('paragrafi', len(blocchi)), ('parole', parole), ('posizione_media_osservata', mo), ('posizione_media_nullo', mn),
                       ('differenza', d), ('IC95', ic), ('terzi', terzi), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a83_copia_recente.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a83 — Lo scriba copia di preferenza dalla fine della riga sopra?', '', 'Preregistrazione: `preregistrazioni/e3a83.md`.', '',
          'Paragrafi %d, parole %d. Posizione media delle corrispondenze nella riga sopra %.3f; nel nullo %.3f. Differenza **%+.3f**, IC 95%% %+.3f – %+.3f.' % (len(blocchi), parole, mo, mn, d, ic[0], ic[1]), '',
          '| terzo della riga sopra | corrispondenze per parola | nullo | eccesso |', '|---|---|---|---|']
    md += ['| %s | %.4f | %.4f | %+.4f |' % (k, x['osservate_per_parola'], x['nullo_per_parola'], x['eccesso']) for k, x in terzi.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a83_copia_recente.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
