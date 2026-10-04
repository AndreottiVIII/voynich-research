# -*- coding: utf-8 -*-
"""Esperimento e3c50: la "finestra" (accordo fra parole vicine della riga a 1, 2, 3 parole, misura corretta dell'e3c48)
nelle scelte libere di due scribi islandesi veri, dalle trascrizioni Menota a livello facsimile, con righe, pagine e mani
vere: AM 519 a 4to (Alexanders saga, c. 1280) e AM 677 4to (c. 1300). Scelte di forma di lettera (ꝩ/v, u/v, c/k, í/ı) e
abbreviazione sì/no.

Dati: dati/cache/menota/*.xml (Menota, CC-BY-SA 4.0; non si committano).
Preregistrazione: preregistrazioni/e3c50.md. Scrive risultati/e3c50_scribi_menota.json e .md.
"""
import json, os, re, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c48_finestra_corretta as e3c48

RISULTATI = os.path.join(QUI, '..', 'risultati')
MENOTA = os.path.join(QUI, '..', 'dati', 'cache', 'menota')
SOGLIA = 0.53
GLIFO = re.compile(r'&[A-Za-z0-9]+;|[^\s]')
EVENTO = re.compile(r'<pb [^>]*n="([^"]*)"[^>]*/>|<lb[^>]*/>|<handShift[^>]*>|<w [^>]*>.*?</w>', re.S)


class Parola(tuple):
    """Segni del livello facsimile; in più: abbreviata (il diplomatico ha <ex>) e forma normalizzata."""
    def __new__(cls, segni, abbreviata, norm):
        p = super().__new__(cls, segni)
        p.abbreviata, p.norm = abbreviata, norm
        return p


def leggi(nome):
    """[(pagina, mano, [righe di Parola])] in ordine; una parola spezzata a fine riga chiude la riga dove comincia."""
    s = open(os.path.join(MENOTA, nome + '.xml'), encoding='utf-8').read()
    b = s[s.find('<body'):]
    pagine, righe, riga, pag, mano = [], [], [], None, 0

    def chiudi_pagina():
        if pag is not None and righe:
            pagine.append((pag, mano, righe))

    for m in EVENTO.finditer(b):
        t = m.group(0)
        if t.startswith('<pb') or t.startswith('<handShift'):
            if riga:
                righe.append(riga)
            chiudi_pagina()
            righe, riga = [], []
            if t.startswith('<pb'):
                pag = m.group(1)
            else:
                mano += 1
        elif t.startswith('<lb'):
            if riga:
                righe.append(riga)
            riga = []
        else:
            fa = re.search(r'<me:facs>(.*?)</me:facs>', t, re.S)
            if not fa or not fa.group(1).strip():
                continue
            di = re.search(r'<me:dipl>(.*?)</me:dipl>', t, re.S)
            no = re.search(r'<me:norm>(.*?)</me:norm>', t, re.S)
            fac = fa.group(1)
            spezzata = '<lb' in fac
            fac = re.sub(r'<[^>]+>', '', fac)
            nor = re.sub(r'<[^>]+>', '', no.group(1)).strip().lower() if no else ''
            riga.append(Parola(GLIFO.findall(fac), bool(di and '<ex>' in di.group(1)), nor))
            if spezzata:
                righe.append(riga)
                riga = []
    if riga:
        righe.append(riga)
    chiudi_pagina()
    return pagine


def coppia(a, b):
    """Valore 1 se la prima occorrenza è la forma a, 0 se è b; parola coperta con un segnaposto al suo posto."""
    a, b = tuple(a), tuple(b)
    ordine = ((1, a), (0, b)) if len(a) >= len(b) else ((0, b), (1, a))

    def f(w):
        for i in range(len(w)):
            for val, s in ordine:
                if tuple(w[i:i + len(s)]) == s:
                    return val, tuple(w[:i]) + ('*',) + tuple(w[i + len(s):])
        return None
    return f


def abbreviata(w):
    if not w.norm:
        return None
    return int(w.abbreviata), tuple(w.norm)


SCELTE = [
    ('AM-519a-4to', 'ꝩ/v', coppia('ꝩ', 'v'), 'lettera'),
    ('AM-519a-4to', 'u/v', coppia('u', 'v'), 'lettera'),
    ('AM-519a-4to', 'c/k', coppia('c', 'k'), 'lettera'),
    ('AM-519a-4to', 'í/ı', coppia('í', 'ı'), 'lettera'),
    ('AM-677-4to', 'u/v', coppia('u', 'v'), 'lettera'),
    ('AM-519a-4to', 'abbreviata o no', abbreviata, 'abbreviazione'),
    ('AM-677-4to', 'abbreviata o no', abbreviata, 'abbreviazione'),
]


def giudizio(x):
    vicine = x['K1_IC95'][0] > 0.02
    finestra = vicine and x['K23_IC95'][0] > 0.02 and np.isfinite(x['r']) and x['r'] >= SOGLIA
    return vicine, finestra


def main():
    e3c48.PERM = 50
    rng = np.random.default_rng(3350)
    testi = {n: leggi(n) for n in sorted({s[0] for s in SCELTE})}
    ris = OrderedDict()
    for ms, nome, f, tipo in SCELTE:
        pagine = [(mano, righe) for _, mano, righe in testi[ms]]
        x = e3c48.misura(pagine, OrderedDict([(nome, f)]), rng)
        x['vicine'], x['finestra'] = giudizio(x)
        x['tipo'], x['pagine'] = tipo, len(pagine)
        ris['%s, %s' % (ms, nome)] = x
        print(ms, nome, json.dumps(x, ensure_ascii=False), flush=True)
    lettere = [k for k, x in ris.items() if x['tipo'] == 'lettera']
    con = [k for k in lettere if ris[k]['finestra']]
    if len(con) >= 2:
        esito = 'gli scribi veri hanno la finestra'
    elif not con:
        esito = 'nessuna scelta di lettera degli scribi ha la finestra'
    else:
        esito = 'incerto'
    abbr = OrderedDict((k, ('finestra' if x['finestra'] else 'accordo fra vicine senza finestra' if x['vicine'] else 'nessun accordo chiaro'))
                       for k, x in ris.items() if x['tipo'] == 'abbreviazione')
    out = OrderedDict([('misure', ris), ('soglia_r', SOGLIA), ('lettere_con_finestra', con), ('esito', esito), ('abbreviazione', abbr)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c50_scribi_menota.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c50 — La finestra nelle scelte libere di due scribi islandesi veri (Menota)', '',
          'Preregistrazione: `preregistrazioni/e3c50.md`. Voynich (e3c48, pagine intere): K corretto +0,131 / +0,093 / +0,086 (ZL), r 0,68 (0,53 – 0,84). Soglia r %.2f.' % SOGLIA, '',
          '| scelta | pagine | parole | K osservato 1/2/3 | K nullo 1/2/3 | K corretto 1 (IC 95%) | K corretto 2/3 (media, IC 95%) | r (IC 95%) | vicine / finestra |',
          '|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %d | %s | %s | %+.3f (%+.3f – %+.3f) | %+.3f / %+.3f (%+.3f – %+.3f) | %.2f (%.2f – %.2f) | %s / %s |' % (
            k, x['pagine'], x['parole'], ' '.join('%+.3f' % z for z in x['K_osservato']), ' '.join('%+.3f' % z for z in x['K_nullo']),
            x['K_corretto'][0], x['K1_IC95'][0], x['K1_IC95'][1], x['K_corretto'][1], x['K_corretto'][2], x['K23_IC95'][0], x['K23_IC95'][1],
            x['r'], x['r_IC95'][0], x['r_IC95'][1], 'sì' if x['vicine'] else 'no', 'sì' if x['finestra'] else 'no'))
    md += ['', 'Esito (scelte di lettera): **%s**%s.' % (esito, (' (' + ', '.join(con) + ')') if con else ''), '']
    md += ['Abbreviazione: ' + '; '.join('%s: **%s**' % kv for kv in abbr.items()) + '.']
    md += ['', 'Fonte dei testi: Menota (Medieval Nordic Text Archive), clarino.uib.no/menota, licenza CC-BY-SA 4.0. I file non sono nel repository.']
    open(os.path.join(RISULTATI, 'e3c50_scribi_menota.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
