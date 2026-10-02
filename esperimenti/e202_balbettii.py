# -*- coding: utf-8 -*-
"""Esperimento 202: nelle coppie adiacenti a distanza di modifica 1, la seconda parola e' piu' frequente della prima
(auto-correzione) o meno (copia modificata)?

Preregistrazione: preregistrazioni/e202.md. Scrive risultati/e202_balbettii.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e169_tema_e_vicini as e169
import e186_nulli_acrostici as e186

RISULTATI = os.path.join(QUI, '..', 'risultati')


def binomiale_due_code(k, n):
    def logc(n, k):
        return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    oss = abs(k - n / 2)
    return min(1.0, sum(math.exp(logc(n, i) - n * math.log(2)) for i in range(n + 1) if abs(i - n / 2) >= oss))


def misura(righe):
    """righe: liste di parole."""
    pul = trascrizione.pulita
    freq = Counter(w for ps in righe for w in ps if pul(w))
    su = giu = 0
    hap1 = hap2 = tot = 0
    for ps in righe:
        for a, b in zip(ps[1:-2], ps[2:-1]):
            if pul(a) and pul(b) and a != b and e169.vicine(a, b):
                tot += 1
                hap1 += freq[a] == 1
                hap2 += freq[b] == 1
                if freq[b] > freq[a]:
                    su += 1
                elif freq[b] < freq[a]:
                    giu += 1
    n = su + giu
    return OrderedDict([('coppie', tot), ('con_frequenze_diverse', n), ('quota_seconda_piu_frequente', su / n if n else None),
                        ('p_binomiale', binomiale_due_code(su, n) if n else None), ('hapax_prima', hap1 / tot if tot else None), ('hapax_seconda', hap2 / tot if tot else None)])


def main():
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    testi = OrderedDict([('Voynich', [list(r.parole) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]),
                         ('generatore e180', [ps for _, _, ps in e186.generatore(voy)]),
                         ('Timm e Schinner (seme 19)', [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))])])
    ris = OrderedDict((n, misura(r)) for n, r in testi.items())
    for n, r in ris.items():
        print('%-28s coppie %d (diverse %d) | seconda più frequente %.3f (p %.2g) | hapax prima %.3f seconda %.3f' % (
            n, r['coppie'], r['con_frequenze_diverse'], r['quota_seconda_piu_frequente'] or 0, r['p_binomiale'] or 1, r['hapax_prima'] or 0, r['hapax_seconda'] or 0), flush=True)
    v = ris['Voynich']
    q, p = v['quota_seconda_piu_frequente'], v['p_binomiale']
    altri = [ris[k]['quota_seconda_piu_frequente'] or 0.5 for k in testi if k != 'Voynich']
    if q >= 0.6 and p < 0.001 and all(q - a >= 0.05 for a in altri):
        esito = 'auto-correzione'
    elif q <= 0.4 and p < 0.001:
        esito = 'copia modificata'
    else:
        esito = 'nessun verso'
    ris['esito'] = esito
    print(esito)
    with open(os.path.join(RISULTATI, 'e202_balbettii.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e202 — I "balbettii" sono auto-correzioni o copie modificate?', '', 'Coppie adiacenti interne a distanza di modifica 1. Preregistrazione: `preregistrazioni/e202.md`.', '',
           '| testo | coppie | seconda più frequente | p | hapax fra le prime | hapax fra le seconde |', '|---|---|---|---|---|---|']
    for n in testi:
        r = ris[n]
        out.append('| %s | %d | %.3f | %.2g | %.3f | %.3f |' % (n, r['coppie'], r['quota_seconda_piu_frequente'] or 0, r['p_binomiale'] or 1, r['hapax_prima'] or 0, r['hapax_seconda'] or 0))
    out += ['', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e202_balbettii.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
