# -*- coding: utf-8 -*-
"""Esperimento 196: eccesso di coppie di parole ripetute dentro la riga e attraverso l'a capo, Voynich e Plinio.

Preregistrazione: preregistrazioni/e196.md. Scrive risultati/e196_coppie_ripetute.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 196, 200


def coppie(righe):
    """righe: (pagina, inizio paragrafo, parole)."""
    dentro, a_capo = [], []
    pul = trascrizione.pulita
    for k, (pag, ini, ps) in enumerate(righe):
        ps = [w for w in ps if pul(w)]
        dentro += list(zip(ps, ps[1:]))
        if k + 1 < len(righe):
            pag2, ini2, ps2 = righe[k + 1]
            ps2 = [w for w in ps2 if pul(w)]
            if pag2 == pag and not ini2 and ps and ps2:
                a_capo.append((ps[-1], ps2[0]))
    return dentro, a_capo


def quote(d, a):
    c = Counter(d) + Counter(a)
    return sum(c[x] >= 2 for x in d) / len(d), sum(c[x] >= 2 for x in a) / len(a)


def misura(righe, rnd):
    d, a = coppie(righe)
    qd, qa = quote(d, a)
    nd, na = [], []
    for _ in range(RIMESCOLAMENTI):
        sd = [y for _, y in d]
        sa = [y for _, y in a]
        rnd.shuffle(sd)
        rnd.shuffle(sa)
        x, y = quote([(p, s) for (p, _), s in zip(d, sd)], [(p, s) for (p, _), s in zip(a, sa)])
        nd.append(x)
        na.append(y)
    ed, ea = qd - statistics.mean(nd), qa - statistics.mean(na)
    return OrderedDict([('coppie_dentro', len(d)), ('coppie_a_capo', len(a)), ('quota_dentro', qd), ('eccesso_dentro', ed),
                        ('z_dentro', ed / statistics.pstdev(nd) if statistics.pstdev(nd) else None), ('quota_a_capo', qa), ('eccesso_a_capo', ea),
                        ('z_a_capo', ea / statistics.pstdev(na) if statistics.pstdev(na) else None), ('Rrip', ea / ed if ed > 0 else None)])


def main():
    from e36_posizione_pagina import plinio
    rnd = random.Random(SEME)
    D = e71.D
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rv = [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    pl = [(None, ini, ps) for ini, ps in e71.a_capo([w for _, ps in plinio() for w in ps], e71.lettere, larghezze, media_voy)]
    ris = OrderedDict()
    for nome, rr in (('Voynich', rv), ('Plinio a capo', pl)):
        ris[nome] = misura(rr, rnd)
        r = ris[nome]
        print('%-14s dentro %.4f (z %.1f) | a capo %.4f (z %.1f, n %d) | Rrip %s' % (nome, r['eccesso_dentro'], r['z_dentro'] or 0, r['eccesso_a_capo'], r['z_a_capo'] or 0,
              r['coppie_a_capo'], '%.2f' % r['Rrip'] if r['Rrip'] is not None else '-'), flush=True)
    v, p = ris['Voynich']['Rrip'], ris['Plinio a capo']['Rrip']
    esito = ('ripetizioni chiuse nella riga' if v is not None and v < 0.2 and (p or 0) >= 0.5 else
             ('ripetizioni che attraversano l\'a capo' if (v or 0) >= 0.5 else 'misto'))
    ris['esito'] = esito
    print(esito)
    with open(os.path.join(RISULTATI, 'e196_coppie_ripetute.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e196 — Le coppie di parole ripetute attraversano l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e196.md`.', '',
           '| testo | eccesso dentro la riga (z) | eccesso attraverso l\'a capo (z) | Rrip |', '|---|---|---|---|']
    for n in ('Voynich', 'Plinio a capo'):
        r = ris[n]
        out.append('| %s | %.4f (%.1f) | %.4f (%.1f) | %s |' % (n, r['eccesso_dentro'], r['z_dentro'] or 0, r['eccesso_a_capo'], r['z_a_capo'] or 0,
                   '%.2f' % r['Rrip'] if r['Rrip'] is not None else '–'))
    out += ['', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e196_coppie_ripetute.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
