# -*- coding: utf-8 -*-
"""Esperimento e3b96: rapporto R = K(3)/K(1) (rispetto a 8-12) con intervalli per unità, nel Voynich (IT) e in tre
testi di lingue con accordo non usati nell'e3b95.

Preregistrazione: preregistrazioni/e3b96.md. Scrive risultati/e3b96_forma_calo.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e381_parole_intere as e381
import e3a86_ripetizioni_riga as e3a86
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b91_accordo_lingue as e3b91

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
GRUPPI = {1: 'd1', 3: 'd3'}
LONTANE = range(8, 13)
LINGUE = OrderedDict([('italiano, Della Pittura', ('Historical - Italian - Technical - Della Pittura.txt', e3b91.oa)),
                      ('italiano NT moderno', ('Modern - Italian - Literary - NT.txt', e3b91.oa)),
                      ('latino, Plinio', ("Historical - Latin - Technical - Pliny's Natural History.txt", e3b91.usa))])


def somme_unita(u, classi):
    """{gruppo: [accordi, attesi, coppie]} per un'unità."""
    acc = {g: [0.0, 0.0, 0] for g in ('d1', 'd3', 'lontane')}
    for f in classi.values():
        xs_all = [[f(w) for w in s] for s in u]
        tot = sum(1 for xs in xs_all for x in xs if x)
        uno = sum(x[0] for xs in xs_all for x in xs if x)
        if tot - 2 < 5:
            continue
        for s, xs in zip(u, xs_all):
            for i in range(len(s)):
                if not xs[i]:
                    continue
                for d in [1, 3] + list(LONTANE):
                    j = i + d
                    if j >= len(s) or not xs[j]:
                        continue
                    a, b = xs[i], xs[j]
                    if a[1] == b[1] or e3a86.una_modifica(a[1], b[1]):
                        continue
                    p = (uno - a[0] - b[0]) / (tot - 2)
                    g = GRUPPI.get(d, 'lontane')
                    acc[g][0] += a[0] == b[0]
                    acc[g][1] += p * p + (1 - p) * (1 - p)
                    acc[g][2] += 1
    return acc


def rapporto(somme):
    k = {}
    for g in ('d1', 'd3', 'lontane'):
        o = sum(s[g][0] for s in somme)
        a = sum(s[g][1] for s in somme)
        n = sum(s[g][2] for s in somme)
        if n - a <= 0:
            return None
        k[g] = (o - a) / (n - a)
    den = k['d1'] - k['lontane']
    return (k['d3'] - k['lontane']) / den if den > 0 else None


def main():
    rnd = random.Random(3296)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    testi = OrderedDict()
    uu, _ = e3b62.voynich(e3b45.pagine_it(), mano)
    testi['Voynich IT'] = (uu, e3b62.CV)
    tt = e381.testi()
    for nome, (chiave, f) in LINGUE.items():
        righe = [r for r in tt[chiave] if r]
        testi[nome] = ([[b] for b in e3b51.blocchi(righe)], OrderedDict([('x', f)]))
    ris = OrderedDict()
    for nome, (u, cl) in testi.items():
        ss = [somme_unita(x, cl) for x in u]
        r = rapporto(ss)
        boot = sorted(x for x in (rapporto([ss[rnd.randrange(len(ss))] for _ in ss]) for _ in range(BOOT)) if x is not None)
        ris[nome] = OrderedDict([('R', r), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]), ('unita', len(u))])
        print(nome, json.dumps(ris[nome]), flush=True)
    v = ris['Voynich IT']['IC95']
    lingue = [ris[k]['IC95'] for k in LINGUE]
    sovrap = sum(1 for l in lingue if not (v[0] > l[1] or l[0] > v[1]))
    if all(v[0] > l[1] for l in lingue):
        esito = 'la forma distingue'
    elif sovrap >= 2:
        esito = 'forma simile'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b96_forma_calo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b96 — La forma del calo distingue la memoria del Voynich dall\'accordo grammaticale?', '', 'Preregistrazione: `preregistrazioni/e3b96.md`. R = [K(3) − K(8–12)] / [K(1) − K(8–12)]. e3b95 (ZL, descrittivo): Voynich 0,78; lingue 0,13–0,33.', '',
          '| testo | unità | R (IC 95%) |', '|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.2f (%.2f – %.2f) |' % (k, x['unita'], x['R'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b96_forma_calo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
