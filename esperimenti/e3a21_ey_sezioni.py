# -*- coding: utf-8 -*-
"""Esperimento e3a21: crescita di -ey dalla meta' alta alla meta' bassa della pagina (misura dell'e3a15) per sezione; per
l'erbario anche senza le righe con un salto del disegno.

Preregistrazione: preregistrazioni/e3a21.md. Scrive risultati/e3a21_ey_sezioni.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e3a15_ey_verticale as e3a15

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
NOMI = {'H': 'erbario', 'B': 'biologia', 'S': 'ricette', 'P': 'farmacia'}


def celle_da(per_pag, salta_disegno=False):
    celle = defaultdict(list)
    for pag, righe in per_pag.items():
        interne = righe[1:-1]
        if len(interne) < 4:
            continue
        lung = [sum(len(w) for w in r[0]) for r in interne]
        ordinate = sorted(lung)
        t1, t2 = ordinate[len(ordinate) // 3], ordinate[2 * len(ordinate) // 3]
        meta = len(interne) / 2
        for i, (r, disegno) in enumerate(interne):
            if salta_disegno and disegno:
                continue
            terz = 0 if lung[i] < t1 else (1 if lung[i] < t2 else 2)
            n = len(r)
            for j, w in enumerate(r):
                if len(w) >= 2 and w[-1] == 'y' and w[-2] in ('d', 'e'):
                    pos = 0 if j == 0 else (2 if j == n - 1 else 1)
                    celle[(pag, pos, terz)].append((i >= meta, w[-2] == 'e'))
    return [xs for xs in celle.values() if any(b for b, _ in xs) and any(not b for b, _ in xs)]


def prova(usate, rnd):
    vero = e3a15.diff(usate)
    nul = []
    for _ in range(10000):
        cc = []
        for xs in usate:
            et = [b for b, _ in xs]
            rnd.shuffle(et)
            cc.append([(b, e) for b, (_, e) in zip(et, xs)])
        nul.append(e3a15.diff(cc))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    z = (vero - m) / sd if sd else 0.0
    return OrderedDict([('celle', len(usate)), ('parole', sum(len(x) for x in usate)), ('differenza', vero), ('z', z),
                        ('esito', 'cresce' if vero > 0 and z > 3 else ('non cresce' if z < 2 else 'incerto'))])


def main():
    rnd = random.Random(3121)
    per_sez = defaultdict(OrderedDict)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ws = [tuple(D(w)) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            sez = r.sezione if r.sezione in NOMI else 'altre'
            per_sez[sez].setdefault(r.pagina, []).append((ws, '<->' in r.grezza))
    ris = OrderedDict()
    for sez in ('H', 'B', 'S', 'P', 'altre'):
        ris[NOMI.get(sez, sez)] = prova(celle_da(per_sez[sez]), rnd)
        print(sez, json.dumps(ris[NOMI.get(sez, sez)], ensure_ascii=False), flush=True)
    ris['erbario senza righe con salto del disegno'] = prova(celle_da(per_sez['H'], salta_disegno=True), rnd)
    r_S = ris['ricette']
    if r_S['esito'] == 'cresce':
        esito = 'non dipende dai disegni'
    elif ris['erbario']['esito'] == 'cresce' and r_S['z'] < 2 and ris['erbario senza righe con salto del disegno']['z'] < 2:
        esito = 'forse dai disegni'
    else:
        esito = 'non deciso'
    out = OrderedDict([('sezioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a21_ey_sezioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a21 — La crescita di -ey scendendo nella pagina c\'è in ogni sezione?', '', 'Preregistrazione: `preregistrazioni/e3a21.md`.', '',
          '| sezione | celle | parole | metà bassa − metà alta | z | esito |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %+.3f | %.1f | %s |' % (k, x['celle'], x['parole'], x['differenza'], x['z'], x['esito']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a21_ey_sezioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
