# -*- coding: utf-8 -*-
"""Esperimento e3c58: la finestra (misura corretta dell'e3c48) nelle scelte di forma di lettera di altri quattro scribi
(Menota, livello facsimile): AM 60 4to (norvegese, c. 1320), AM 242 fol (Codex Wormianus, islandese, c. 1350), Holm A 10
(svedese, c. 1500 – 1550), AM 302 fol (norvegese, c. 1300). Le scelte entrano con la regola dell'e3c50 (almeno 300
occorrenze della forma meno usata dentro parole coperte che usano tutte e due le forme), da una lista fissa di coppie.

Dati: dati/cache/menota/*.xml (Menota, CC-BY-SA 4.0; non si committano).
Preregistrazione: preregistrazioni/e3c58.md. Scrive risultati/e3c58_altri_scribi.json e .md.
"""
import json, os, re, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c48_finestra_corretta as e3c48
import e3c50_scribi_menota as e3c50
import e3c52_eva_per_scelta as e3c52

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANOSCRITTI = OrderedDict([('AM-60-4to', 'norvegese, c. 1320'), ('AM-242-fol', 'islandese, c. 1350'),
                           ('Holm-A-10', 'svedese, c. 1500 – 1550'), ('AM-302-fol', 'norvegese, c. 1300')])
MINIMO = 300
EVENTO = re.compile(r'<pb [^>]*n="([^"]*)"[^>]*/>|<lb[^>]*/>|<handShift[^>]*>|<w(?: [^>]*)?>.*?</w>', re.S)
COPPIE = [
    ('ꝛ/r', ['ꝛ', '&rrot;'], ['r']),
    ('ꝺ/d', ['ꝺ', '&drot;'], ['d']),
    ('ꝼ/f', ['ꝼ', '&fins;'], ['f']),
    ('ꞇ/t', ['ꞇ', '&trot;'], ['t']),
    ('ſ/s', ['ſ', '&slong;'], ['s']),
    ('ꝩ/v', ['ꝩ', '&vins;'], ['v']),
    ('u/v', ['u'], ['v']),
    ('w/v', ['w'], ['v']),
    ('c/k', ['c'], ['k']),
    ('ı/i', ['ı', '&inodot;'], ['i']),
    ('í/i senza accento', ['í', '&iacute;'], ['i', 'ı', '&inodot;']),
    ('á/a', ['á', '&aacute;'], ['a']),
    ('ð/þ', ['ð', '&eth;'], ['þ', '&thorn;']),
    ('ę/æ', ['ę', '&eogon;'], ['æ', '&aelig;']),
    ('ʀ/rr', ['ʀ', '&rscap;'], [('r', 'r')]),
    ('ɴ/nn', ['ɴ', '&nscap;'], [('n', 'n')]),
    ('ɢ/gg', ['ɢ', '&gscap;'], [('g', 'g')]),
    ('ᴍ/mm', ['ᴍ', '&mscap;'], [('m', 'm')]),
    ('ꜳ/aa', ['ꜳ'], [('a', 'a')]),
    ('ẏ/y', ['ẏ'], ['y']),
]


def leggi(nome):
    """Come e3c50.leggi, ma accetta anche <w> senza attributi (testi con il solo livello facsimile)."""
    vecchio = e3c50.EVENTO
    e3c50.EVENTO = EVENTO
    try:
        return e3c50.leggi(nome)
    finally:
        e3c50.EVENTO = vecchio


def scelta(aa, bb):
    """Valore 1 se la prima occorrenza è una delle forme aa, 0 se una delle bb; parola coperta con un segnaposto."""
    forme = [(1, tuple(a) if isinstance(a, tuple) else (a,)) for a in aa] + [(0, tuple(b) if isinstance(b, tuple) else (b,)) for b in bb]
    forme.sort(key=lambda z: -len(z[1]))

    def f(w):
        for i in range(len(w)):
            for val, s in forme:
                if tuple(w[i:i + len(s)]) == s:
                    return val, tuple(w[:i]) + ('*',) + tuple(w[i + len(s):])
        return None
    return f


def minoritarie(pagine, f):
    xs = [f(w) for _, _, rr in pagine for r in rr if len(r) >= 6 for w in r[1:-1]]
    xs = [x for x in xs if x]
    per = defaultdict(set)
    for v, t in xs:
        per[t].add(v)
    mi = [v for v, t in xs if len(per[t]) == 2]
    return len(xs), min(sum(mi), len(mi) - sum(mi))


def ingresso():
    testi = OrderedDict((m, leggi(m)) for m in MANOSCRITTI)
    tab = []
    for m, pp in testi.items():
        for nome, aa, bb in COPPIE:
            n, mino = minoritarie(pp, scelta(aa, bb))
            if n:
                tab.append((m, nome, n, mino, mino >= MINIMO))
    return testi, tab


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3358)
    testi, tab = ingresso()
    fn = {nome: scelta(aa, bb) for nome, aa, bb in COPPIE}
    ris = OrderedDict()
    for m, nome, n, mino, entra in tab:
        if not entra:
            continue
        pagine = [(h, rr) for _, h, rr in testi[m]]
        x = e3c48.misura(pagine, OrderedDict([(nome, fn[nome])]), rng)
        x['vicine'], x['finestra'] = e3c50.giudizio(x)
        x['voce'], x['pagine'], x['minoritarie_nei_misti'] = e3c52.voce(x), len(pagine), mino
        ris['%s, %s' % (m, nome)] = x
        print(m, nome, json.dumps(x, ensure_ascii=False), flush=True)
    con = [k for k, x in ris.items() if x['finestra']]
    vic = [k for k, x in ris.items() if x['vicine']]
    esito = 'gli scribi veri hanno la finestra' if len(con) >= 2 else ('nessuna scelta di lettera degli scribi ha la finestra' if not con else 'incerto')
    out = OrderedDict([('ingresso', [OrderedDict([('manoscritto', a), ('scelta', b), ('parole', c), ('minoritarie_nei_misti', d), ('entra', e)]) for a, b, c, d, e in tab]),
                       ('misure', ris), ('con_finestra', con), ('con_accordo_fra_vicine', vic), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c58_altri_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c58 — La finestra nelle scelte di forma di lettera di altri quattro scribi (Menota)', '',
          'Preregistrazione: `preregistrazioni/e3c58.md`. Voynich (e3c48, ZL): K corretto +0,131 / +0,093 / +0,086, r 0,68; con il nullo che conserva la posizione (e3c57) +0,113 / +0,080.', '',
          '| manoscritto, scelta | pagine | parole | minoritarie nei tipi misti | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r | voce |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %d | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f | %s |' % (
            k, x['pagine'], x['parole'], x['minoritarie_nei_misti'], x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1],
            x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1], x['r'], x['voce']))
    md += ['', 'Esito: **%s**%s.' % (esito, (' (' + ', '.join(con) + ')') if con else ''),
           'Scelte con accordo fra parole accanto: %s.' % (', '.join(vic) or 'nessuna'), '',
           'Fonte dei testi: Menota (Medieval Nordic Text Archive), clarino.uib.no/menota, licenza CC-BY-SA 4.0. I file non sono nel repository.']
    open(os.path.join(RISULTATI, 'e3c58_altri_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
