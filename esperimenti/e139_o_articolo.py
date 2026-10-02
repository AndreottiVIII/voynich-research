# -*- coding: utf-8 -*-
"""Esperimento 139: "o-" (e y-, d-, s-) davanti a una parola dipende dalla posizione nella riga? Quota di PX su
PX + X per posizione, rapporto prima/interna contro il rimescolamento dentro la riga.

Preregistrazione: preregistrazioni/e139.md. Scrive risultati/e139_o_articolo.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 139, 1000
D = misure.divisore(misure.GLIFI_EVA)
PREFISSI = ('o', 'y', 'd', 's')
POSIZIONI = ('prima', 'prima di paragrafo', 'ultima', 'interna')


def righe():
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            out.append((r.pagina, bool(r.inizio_par), list(r.parole)))
    return out


def coppie(rr, p):
    tipi = Counter(w for _, _, ps in rr for w in ps if trascrizione.pulita(w))
    base = {w for w in tipi if len(D(w)) >= 2 and D(w)[0] != p and (p + w) in tipi and D(p + w)[0] == p}
    return base


def posizione(i, n, ini):
    if i == 0:
        return 'prima di paragrafo' if ini else 'prima'
    return 'ultima' if i == n - 1 else 'interna'


def quote(rr, p, base):
    c = {pos: [0, 0] for pos in POSIZIONI}
    for _, ini, ps in rr:
        n = len(ps)
        for i, w in enumerate(ps):
            pos = posizione(i, n, ini)
            if w in base:
                c[pos][1] += 1
            elif D(w)[0] == p and ''.join(D(w)[1:]) in base:
                c[pos][0] += 1
    return {pos: (a / (a + b) if a + b else None, a + b) for pos, (a, b) in c.items()}


def main():
    rr = righe()
    rnd = random.Random(SEME)
    ris = OrderedDict()
    for p in PREFISSI:
        base = coppie(rr, p)
        q = quote(rr, p, base)
        rap = q['prima'][0] / q['interna'][0] if q['interna'][0] else None
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            mes = []
            for pag, ini, ps in rr:
                ps = ps[:]
                rnd.shuffle(ps)
                mes.append((pag, ini, ps))
            qq = quote(mes, p, base)
            nulli.append(qq['prima'][0] / qq['interna'][0] if qq['interna'][0] else 0)
        m, s = statistics.mean(nulli), statistics.pstdev(nulli)
        ris[p + '-'] = OrderedDict([('coppie', len(base)), ('quote', {k: v[0] for k, v in q.items()}), ('occorrenze', {k: v[1] for k, v in q.items()}),
                                    ('rapporto_prima_interna', rap), ('nullo', m), ('z', (rap - m) / s if s else None),
                                    ('posizionale', rap is not None and rap > 1.5 and s and (rap - m) / s > 4),
                                    ('anche_fuori_posizione', (q['interna'][0] or 0) > 0.2)])
        r = ris[p + '-']
        print('%s-: coppie %4d | quote %s | rapporto prima/interna %.2f (nullo %.2f, z %.1f) | posizionale %s | anche fuori posizione %s' % (
            p, r['coppie'], ' '.join('%s %.3f (%d)' % (k, r['quote'][k] or 0, r['occorrenze'][k]) for k in POSIZIONI),
            r['rapporto_prima_interna'] or 0, m, r['z'] or 0, r['posizionale'], r['anche_fuori_posizione']), flush=True)
    tolor = []
    for pag, ini, ps in rr:
        for i, w in enumerate(ps):
            if 'tolor' in w:
                tolor.append((pag, w, posizione(i, len(ps), ini)))
    zl = trascrizione.leggi('ZL')
    tolor += [(r.pagina, w, 'etichetta o testo non in paragrafo') for r in zl if r.tipo and r.tipo[0] != 'P' for w in r.parole if 'tolor' in w]
    ris['tolor'] = tolor
    print('tolor:', tolor)
    with open(os.path.join(RISULTATI, 'e139_o_articolo.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e139 — "o-" è un articolo o un segno di posizione?', '', 'Quota di PX fra PX + X per posizione nella riga; rapporto prima/interna contro %d rimescolamenti '
           'dentro la riga. Preregistrazione: `preregistrazioni/e139.md`.' % RIMESCOLAMENTI, '',
           '| prefisso | coppie X/PX | ' + ' | '.join(POSIZIONI) + ' | prima / interna (z) | posizionale | anche fuori posizione |', '|---|---|' + '---|' * len(POSIZIONI) + '---|---|---|']
    for p in PREFISSI:
        r = ris[p + '-']
        out.append('| %s- | %d | %s | %.2f (%.1f) | %s | %s |' % (p, r['coppie'], ' | '.join('%.3f (n %d)' % (r['quote'][k] or 0, r['occorrenze'][k]) for k in POSIZIONI),
                                                         r['rapporto_prima_interna'] or 0, r['z'] or 0, 'sì' if r['posizionale'] else 'no', 'sì' if r['anche_fuori_posizione'] else 'no'))
    out += ['', 'Occorrenze di "tolor": ' + '; '.join('%s %s (%s)' % t for t in tolor) + '.']
    with open(os.path.join(RISULTATI, 'e139_o_articolo.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
