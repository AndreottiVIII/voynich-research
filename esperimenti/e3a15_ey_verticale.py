# -*- coding: utf-8 -*-
"""Esperimento e3a15: crescita di -ey (fra -dy/-ey) dalla meta' alta alla meta' bassa delle righe interne della pagina,
a parita' di pagina, posizione della parola nella riga e terzile di lunghezza della riga.

Preregistrazione: preregistrazioni/e3a15.md. Scrive risultati/e3a15_ey_verticale.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 10000


def diff(celle):
    num = den = 0.0
    for xs in celle:
        a = [e for b, e in xs if b]
        c = [e for b, e in xs if not b]
        if a and c:
            num += len(xs) * (sum(a) / len(a) - sum(c) / len(c))
            den += len(xs)
    return num / den if den else 0.0


def main():
    rnd = random.Random(3115)
    per_pag = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per_pag.setdefault(r.pagina, []).append(ws)
    celle = defaultdict(list)
    for pag, righe in per_pag.items():
        interne = righe[1:-1]
        if len(interne) < 4:
            continue
        lung = [sum(len(w) for w in r) for r in interne]
        ordinate = sorted(lung)
        t1, t2 = ordinate[len(ordinate) // 3], ordinate[2 * len(ordinate) // 3]
        meta = len(interne) / 2
        for i, r in enumerate(interne):
            terz = 0 if lung[i] < t1 else (1 if lung[i] < t2 else 2)
            n = len(r)
            for j, w in enumerate(r):
                if len(w) >= 2 and w[-1] == 'y' and w[-2] in ('d', 'e'):
                    pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                    celle[(pag, pos, terz)].append((i >= meta, w[-2] == 'e'))
    usate = [xs for xs in celle.values() if any(b for b, _ in xs) and any(not b for b, _ in xs)]
    vero = diff(usate)
    nul = []
    for _ in range(PERM):
        cc = []
        for xs in usate:
            et = [b for b, _ in xs]
            rnd.shuffle(et)
            cc.append([(b, e) for b, (_, e) in zip(et, xs)])
        nul.append(diff(cc))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero - m) / sd if sd else 0.0
    esito = 'la crescita verticale resta' if vero > 0 and z > 3 else ('era posizione nella riga o lunghezza della riga' if z < 2 else 'incerto')
    out = OrderedDict([('celle', len(usate)), ('parole', sum(len(x) for x in usate)), ('differenza', vero), ('z', z), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a15_ey_verticale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a15 — -ey cresce scendendo nella pagina anche a parità di posizione nella riga e di lunghezza della riga?', '', 'Preregistrazione: `preregistrazioni/e3a15.md`.', '',
          '%d celle (pagina × posizione nella riga × terzile di lunghezza), %d parole in -dy/-ey. Quota di -ey, metà bassa meno metà alta: %+.3f, z %.1f.' % (out['celle'], out['parole'], vero, z), '',
          'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a15_ey_verticale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
