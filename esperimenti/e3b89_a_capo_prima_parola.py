# -*- coding: utf-8 -*-
"""Esperimento e3b89: e3b66 con e senza le coppie in cui la seconda parola è la prima della riga nuova.

Preregistrazione: preregistrazioni/e3b89.md. Scrive risultati/e3b89_a_capo_prima_parola.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a86_ripetizioni_riga as e3a86
import e3b62_memoria_nullo_largo as e3b62
import e3b64_memoria_salto as e3b64
import e3b65_a_capo_controllo as e3b65
import e3b66_a_capo_potenza as e3b66

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000


def coppie_senza_prima(a, b):
    """Come e3b66.coppie_cavallo, ma la seconda parola non può essere la prima del tratto dopo l'a capo."""
    seq = a + b
    n = len(a)
    out = []
    for i in range(n):
        for d in e3b66.DIST:
            j = i + d
            if j <= n or j >= len(seq) or not e3b64.classe(seq[i]) or not e3b64.classe(seq[j]):
                continue
            if any(seq[k] == e3b64.ILL for k in range(i + 1, j)):
                continue
            if seq[i][1] == seq[j][1] or e3a86.una_modifica(seq[i][1], seq[j][1]):
                continue
            out.append((seq[i][0], seq[j][0]))
    return out


def somme(per_pagina, quote, chiave, funz):
    out = {}
    for pg, cc in per_pagina.items():
        o = a = n = 0.0
        for c, f in e3b62.CV.items():
            if (c, pg) not in quote:
                continue
            p = quote[(c, pg)]
            for prima, altri in cc:
                if altri.get(chiave) is None:
                    continue
                s = e3b64.somma_pagina(funz(e3b64.valori(prima, f), e3b64.valori(altri[chiave], f)), p)
                o, a, n = o + s[0], a + s[1], n + s[2]
        out[pg] = (o, a, n)
    return out


def analisi(casi, quote, funz, rnd):
    sm = {k: somme(casi, quote, k, funz) for k in ('sotto', 'sopra', 'due')}
    pagine = list(casi)

    def dd(pp):
        ks = {k: e3b64.kappa([sm[k][pg] for pg in pp])[0] for k in sm}
        if None in ks.values():
            return None
        return ks['sotto'] - (ks['sopra'] + ks['due']) / 2
    d = dd(pagine)
    boot = sorted(x for x in (dd([rnd.choice(pagine) for _ in pagine]) for _ in range(BOOT)) if x is not None)
    return OrderedDict([('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]),
                        ('coppie_continuazione', int(sum(sm['sotto'][pg][2] for pg in pagine)))])


def main():
    rnd = random.Random(3289)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    dentro = {'ZL': 0.0880, 'IT': 0.0814}
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(q) if sezione.get(pg) != 'T']
        quote = e3b64.quote_pagine(righe, e3b62.CV)
        casi = e3b65.casi_capo(righe)
        x = OrderedDict()
        x['tutte'] = analisi(casi, quote, e3b66.coppie_cavallo, rnd)
        x['senza la prima parola'] = analisi(casi, quote, coppie_senza_prima, rnd)
        x['K_dentro_e3b66'] = dentro[q]
        ris[q] = x
        print(q, json.dumps(x), flush=True)
    z = ris['ZL']['senza la prima parola']
    if z['D'] >= 0.8 * dentro['ZL'] and z['IC95'][0] > 0:
        esito = 'il dimezzamento viene dalla prima parola'
    elif z['D'] < 0.6 * dentro['ZL']:
        esito = "calo vero all'a capo"
    else:
        esito = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b89_a_capo_prima_parola.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b89 — La memoria si dimezza all\'a capo per colpa della prima parola della riga?', '', 'Preregistrazione: `preregistrazioni/e3b89.md`. K dentro i tratti (e3b66): ZL +0,088, IT +0,081.', '',
          '| trascrizione | coppie | D (IC 95%) | coppie di continuazione | D / K dentro |', '|---|---|---|---|---|']
    for q, x in ris.items():
        for k in ('tutte', 'senza la prima parola'):
            y = x[k]
            md.append('| %s | %s | %+.4f (%+.4f – %+.4f) | %d | %.2f |' % (q, k, y['D'], y['IC95'][0], y['IC95'][1], y['coppie_continuazione'], y['D'] / x['K_dentro_e3b66']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b89_a_capo_prima_parola.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
