# -*- coding: utf-8 -*-
"""Esperimento e3a22: la prima riga del paragrafo e' spostata sull'asse A/B (-edy/-aiin) rispetto al resto del
paragrafo? Controlli: seconda riga contro le seguenti; prima riga senza la prima parola.

Preregistrazione: preregistrazioni/e3a22.md. Scrive risultati/e3a22_prima_riga_asse.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e341_fonti as e341

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def asse(parole):
    u = [w for w in parole if w]
    if not u:
        return None
    segni = Counter(s for w in u for s in w)
    tot = sum(segni.values())
    n = len(u)
    return segni['e'] / tot + sum(w[-1] == 'y' for w in u) / n - segni['a'] / tot - segni['n'] / tot - sum(w[-1] == 'n' for w in u) / n


def flip(d, rnd):
    v = statistics.mean(d)
    nul = [statistics.mean(x * rnd.choice((-1, 1)) for x in d) for _ in range(10000)]
    sd = statistics.pstdev(nul)
    return v, (v - statistics.mean(nul)) / sd if sd else 0.0


def main():
    rnd = random.Random(3122)
    lingua = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        lingua.setdefault(r.pagina, r.lingua or '?')
    diffs = {'prima riga': [], 'seconda riga (controllo)': [], 'prima riga senza la prima parola': []}
    per_lingua = {'A': [], 'B': []}
    for pag, pars in e341.pagine().items():
        for par in pars:
            if len(par) < 3:
                continue
            rr = [[tuple(D(x)) for x in r] for r in par]
            resto = [w for r in rr[1:] for w in r]
            a1, ar = asse(rr[0]), asse(resto)
            if a1 is not None and ar is not None:
                diffs['prima riga'].append(a1 - ar)
                if lingua.get(pag) in per_lingua:
                    per_lingua[lingua[pag]].append(a1 - ar)
            a2, a3 = asse(rr[1]), asse([w for r in rr[2:] for w in r])
            if a2 is not None and a3 is not None:
                diffs['seconda riga (controllo)'].append(a2 - a3)
            a1b = asse(rr[0][1:])
            if a1b is not None and ar is not None:
                diffs['prima riga senza la prima parola'].append(a1b - ar)
    ris = OrderedDict()
    for k, d in list(diffs.items()) + [('prima riga, lingua %s' % l, v) for l, v in per_lingua.items()]:
        v, z = flip(d, rnd)
        ris[k] = OrderedDict([('paragrafi', len(d)), ('media', v), ('z', z)])
        print(k, json.dumps(ris[k]), flush=True)
    z = ris['prima riga']['z']
    m = ris['prima riga']['media']
    if m > 0 and z > 3:
        esito = 'la prima riga è spostata verso B (-edy)'
    elif m < 0 and z < -3:
        esito = 'spostata verso A (-aiin)'
    elif abs(z) < 2:
        esito = 'sulla stessa lingua del paragrafo'
    else:
        esito = 'incerto'
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a22_prima_riga_asse.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a22 — La prima riga del paragrafo sta su un\'altra "lingua"?', '', 'Preregistrazione: `preregistrazioni/e3a22.md`. Differenza sull\'asse A/B (positivo = verso B, -edy).', '',
          '| confronto | paragrafi | differenza media | z |', '|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %.1f |' % (k, x['paragrafi'], x['media'], x['z']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a22_prima_riga_asse.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
