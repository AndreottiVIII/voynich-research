# -*- coding: utf-8 -*-
"""Esperimento 206: per ogni classe di segno "facoltativo" (coppie di parole che differiscono per un segno tolto),
accordo dentro la riga contro rimescolamento dentro la pagina.

Preregistrazione: preregistrazioni/e206.md. Scrive risultati/e206_segni_facoltativi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MIN_TIPO, MIN_OCC = 206, 500, 3, 300
D = misure.divisore(misure.GLIFI_EVA)


def classi_di(freq):
    """{parola: {classe: valore}} per le parole che stanno in almeno una coppia."""
    attestate = {w for w, c in freq.items() if c >= MIN_TIPO}
    out = defaultdict(dict)
    for w in attestate:
        u = D(w)
        for i, g in enumerate(u):
            corta = ''.join(u[:i] + u[i + 1:])
            if corta and corta in attestate:
                pos = 'iniziale' if i == 0 else ('finale' if i == len(u) - 1 else 'interna')
                c = (g, pos)
                out[w][c] = 1
                out[corta].setdefault(c, 0)
    return out


def accordo(per_riga):
    acc = tot = 0
    for v in per_riga.values():
        n1 = sum(v)
        n = len(v)
        if n >= 2:
            acc += n1 * (n1 - 1) / 2 + (n - n1) * (n - n1 - 1) / 2
            tot += n * (n - 1) / 2
    return acc / tot if tot else None


def main():
    rnd = random.Random(SEME)
    righe = [(r.pagina, [w for w in r.parole if trascrizione.pulita(w)]) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    freq = Counter(w for _, ps in righe for w in ps)
    cl = classi_di(freq)
    occ = defaultdict(list)    # classe -> [(pagina, riga, valore)]
    for k, (pag, ps) in enumerate(righe):
        for w in ps:
            for c, v in cl.get(w, {}).items():
                occ[c].append((pag, k, v))
    ris = OrderedDict()
    for c, oo in sorted(occ.items(), key=lambda kv: -len(kv[1])):
        if len(oo) < MIN_OCC:
            continue
        per_riga = defaultdict(list)
        for pag, k, v in oo:
            per_riga[k].append(v)
        vero = accordo(per_riga)
        per_pag = defaultdict(list)
        for i, (pag, k, v) in enumerate(oo):
            per_pag[pag].append(i)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            vals = [v for _, _, v in oo]
            for idx in per_pag.values():
                x = [vals[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vals[i] = y
            pr = defaultdict(list)
            for (pag, k, _), v in zip(oo, vals):
                pr[k].append(v)
            nulli.append(accordo(pr))
        m, s = statistics.mean(nulli), statistics.pstdev(nulli)
        z = (vero - m) / s if s else None
        nome = '%s %s' % c
        ris[nome] = OrderedDict([('occorrenze', len(oo)), ('quota_lunga', sum(v for *_, v in oo) / len(oo)), ('accordo', vero), ('nullo', m), ('z', z)])
        print('%-16s occ %5d lunga %.2f | accordo %.4f nullo %.4f z %.1f' % (nome, len(oo), ris[nome]['quota_lunga'], vero or 0, m, z or 0), flush=True)
    controllo = ris.get('q iniziale', {}).get('z') or 0
    valido = controllo > 3
    di_riga = [n for n, r in ris.items() if (r['z'] or 0) > 3]
    out = {'classi': ris, 'controllo_q_iniziale_z': controllo, 'valido': valido, 'scelte_di_riga': di_riga}
    print('controllo q iniziale z %.1f valido %s | scelte di riga: %s' % (controllo, valido, di_riga))
    json.dump(out, open(os.path.join(RISULTATI, 'e206_segni_facoltativi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e206 — Segni facoltativi decisi per riga?', '', 'Accordo dentro la riga fra forme lunghe e corte, contro il rimescolamento dentro la pagina. Preregistrazione: '
          '`preregistrazioni/e206.md`.', '', '| classe | occorrenze | quota lunga | accordo | nullo | z |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %.2f | %.4f | %.4f | %.1f |' % (n, r['occorrenze'], r['quota_lunga'], r['accordo'] or 0, r['nullo'], r['z'] or 0) for n, r in ris.items()]
    md += ['', 'Controllo (q iniziale = qo-/o-): z %.1f, valido **%s**. Classi decise per riga (z > 3): %s.' % (controllo, 'sì' if valido else 'no', ', '.join(di_riga) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e206_segni_facoltativi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
