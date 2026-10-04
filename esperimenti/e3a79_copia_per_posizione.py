# -*- coding: utf-8 -*-
"""Esperimento e3a79: eccesso di "fonte" nella riga subito sopra (parola uguale o a una modifica, e385) per posizione
della parola nella riga (prima, seconda, ultima, in mezzo); atteso dalle altre righe del paragrafo.

Preregistrazione: preregistrazioni/e3a79.md. Scrive risultati/e3a79_copia_per_posizione.json e .md.
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
POSTI = ('prima', 'seconda', 'in mezzo', 'ultima')
BOOT = 1000


def paragrafo(par):
    """[(posto, colpo, atteso)] per le parole di almeno 3 segni delle righe dalla seconda in poi."""
    sim = e385.simili_unita(par)
    insiemi = [set(r) for r in par]
    out = []
    for i in range(1, len(par)):
        r = par[i]
        if len(r) < 4:
            continue
        altre = [j for j in range(len(par)) if j not in (i, i - 1)]
        for k, w in enumerate(r):
            if len(w) < 3:
                continue
            posto = 'prima' if k == 0 else ('seconda' if k == 1 else ('ultima' if k == len(r) - 1 else 'in mezzo'))
            colpo = bool(sim[w] & insiemi[i - 1])
            att = sum(bool(sim[w] & insiemi[j]) for j in altre) / len(altre) if altre else None
            if att is not None:
                out.append((posto, colpo, att))
    return out


def eccessi(pars):
    out = OrderedDict()
    for p in POSTI:
        xs = [(c, a) for par in pars for (q, c, a) in par if q == p]
        out[p] = (sum(c for c, _ in xs) - sum(a for _, a in xs)) / len(xs) if xs else None
    return out


def main():
    rnd = random.Random(3179)
    pars = []
    for pars_pg in e341.pagine().values():
        for par in pars_pg:
            pp = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            pp = [r for r in pp if r]
            if len(pp) >= 3:
                x = paragrafo(pp)
                if x:
                    pars.append(x)
    e = eccessi(pars)
    n = OrderedDict((p, sum(1 for par in pars for q, _, _ in par if q == p)) for p in POSTI)
    boot = {p: [] for p in POSTI}
    diff = []
    for _ in range(BOOT):
        b = eccessi([pars[rnd.randrange(len(pars))] for _ in pars])
        for p in POSTI:
            boot[p].append(b[p])
        diff.append(b['prima'] - b['in mezzo'])
    ic = lambda xs: [sorted(xs)[int(0.025 * BOOT)], sorted(xs)[int(0.975 * BOOT) - 1]]
    d = e['prima'] - e['in mezzo']
    icd = ic(diff)
    esito = 'la prima parola si copia meno' if icd[1] < 0 else ('si copia di più' if icd[0] > 0 else 'come le altre')
    out = OrderedDict([('paragrafi', len(pars)), ('parole', n), ('eccesso', e), ('IC95', OrderedDict((p, ic(boot[p])) for p in POSTI)),
                       ('differenza_prima_meno_mezzo', d), ('IC95_differenza', icd), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a79_copia_per_posizione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a79 — Lo scriba copia dalla riga sopra anche all\'inizio della riga?', '', 'Preregistrazione: `preregistrazioni/e3a79.md`.', '',
          '| posto nella riga | parole | eccesso di fonte nella riga sopra | IC 95% |', '|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.4f – %+.4f |' % (p, n[p], e[p], out['IC95'][p][0], out['IC95'][p][1]) for p in POSTI]
    md += ['', 'Differenza prima − in mezzo: **%+.4f**, IC 95%% %+.4f – %+.4f.' % (d, icd[0], icd[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a79_copia_per_posizione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
