# -*- coding: utf-8 -*-
"""Esperimento 197: quota di hapax per posizione e allineamento verticale ("scala") degli hapax fra righe consecutive.

Preregistrazione: preregistrazioni/e197.md. Scrive risultati/e197_hapax_posizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 197, 500


def scala(righe, hapax):
    n = 0
    for (pag, par, ps), (pag2, par2, ps2) in zip(righe, righe[1:]):
        if pag != pag2 or par != par2:
            continue
        for i, w in enumerate(ps):
            if w in hapax:
                n += any(0 <= j < len(ps2) and ps2[j] in hapax for j in (i - 1, i, i + 1))
    return n


def main():
    rnd = random.Random(SEME)
    righe, par, prima = [], 0, set()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            par += bool(r.inizio_par)
            righe.append((r.pagina, par, [w for w in r.parole if trascrizione.pulita(w)]))
    freq = Counter(w for _, _, ps in righe for w in ps)
    hapax = {w for w, c in freq.items() if c == 1}
    pos = Counter()
    tot = Counter()
    viste = set()
    for k, (pag, p, ps) in enumerate(righe):
        nuovo_par = k == 0 or righe[k - 1][1] != p
        for i, w in enumerate(ps):
            if i == 0:
                cat = 'prima della pagina' if pag not in viste else ('prima di paragrafo' if nuovo_par else 'prima di riga')
            elif i == len(ps) - 1:
                cat = 'ultima di riga'
            elif i == 1:
                cat = 'seconda'
            else:
                cat = 'interna'
            tot[cat] += 1
            pos[cat] += w in hapax
        viste.add(pag)
    h1 = OrderedDict((c, OrderedDict([('parole', tot[c]), ('quota_hapax', pos[c] / tot[c])])) for c in
                     ('prima della pagina', 'prima di paragrafo', 'prima di riga', 'seconda', 'interna', 'ultima di riga') if tot[c])
    vero = scala(righe, hapax)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for pag, p, ps in righe:
            ps = ps[:]
            rnd.shuffle(ps)
            mes.append((pag, p, ps))
        nulli.append(scala(mes, hapax))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    z = (vero - m) / s if s else None
    p = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    esito = 'scala verticale presente' if (z or 0) > 3 and p < 0.01 else ('assente' if p > 0.05 else 'incerto')
    ris = OrderedDict([('hapax', len(hapax)), ('quota_media', sum(pos.values()) / sum(tot.values())), ('H1', h1),
                       ('H2', OrderedDict([('coppie', vero), ('nullo', m), ('z', z), ('p', p)])), ('esito_H2', esito)])
    print('hapax %d | %s | scala %d (nullo %.1f, z %.1f, p %.4f) | %s' % (len(hapax), {c: round(x['quota_hapax'], 3) for c, x in h1.items()}, vero, m, z or 0, p, esito), flush=True)
    with open(os.path.join(RISULTATI, 'e197_hapax_posizione.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e197 — Dove stanno le parole uniche?', '', 'Preregistrazione: `preregistrazioni/e197.md`.', '', '| posizione | parole | quota di hapax |', '|---|---|---|']
    out += ['| %s | %d | %.3f |' % (c, x['parole'], x['quota_hapax']) for c, x in h1.items()]
    out += ['', 'Quota media %.3f. Scala verticale: %d coppie contro %.1f attese (z %.1f, p %.4f). Esito: **%s**.' % (ris['quota_media'], vero, m, z or 0, p, esito)]
    with open(os.path.join(RISULTATI, 'e197_hapax_posizione.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
