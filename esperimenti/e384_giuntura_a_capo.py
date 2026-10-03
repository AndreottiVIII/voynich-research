# -*- coding: utf-8 -*-
"""Esperimento 384: la giuntura (ultimo segno -> primo segno della parola seguente) fra l'ultima parola di una riga e la
prima della riga sotto, confrontata con quella dentro la riga, con nulli dello stesso tipo. Voynich, testi sensati
(parole intere), gibberish umano.

Preregistrazione: preregistrazioni/e384.md. Scrive risultati/e384_giuntura_a_capo.json e .md.
"""
import json, math, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e377_giuntura_gibberish as e377
import e381_parole_intere as e381

RISULTATI = os.path.join(QUI, '..', 'risultati')
GB = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 200


def misura(blocchi, rnd):
    """blocchi: liste di paragrafi (liste di righe di parole come tuple di segni); si rimescola dentro il blocco, le
    coppie a capo stanno dentro il paragrafo."""
    capo = [[(r[-1][-1], s[0][0]) for par in b for r, s in zip(par, par[1:]) if r and s] for b in blocchi]
    riga = [[(a[-1], c[0]) for par in b for r in par for a, c in zip(r, r[1:])] for b in blocchi]

    def mi_di(gruppi):
        return e377.mi(Counter(x for g in gruppi for x in g))

    def mesc(gruppi):
        out = []
        for g in gruppi:
            dx = [b for _, b in g]
            rnd.shuffle(dx)
            out.append([(a, b) for (a, _), b in zip(g, dx)])
        return out
    res = OrderedDict()
    for nome, gr in (('capo', capo), ('riga', riga)):
        vero = mi_di(gr)
        nul = [mi_di(mesc(gr)) for _ in range(PERM)]
        m, sd = statistics.mean(nul), statistics.pstdev(nul)
        res[nome] = OrderedDict([('coppie', sum(len(g) for g in gr)), ('E', vero - m), ('z', (vero - m) / sd if sd else 0.0)])
    res['Q'] = res['capo']['E'] / res['riga']['E'] if res['riga']['E'] > 0 else None
    return res, capo


def eccessi(capo, rnd):
    c = Counter(x for g in capo for x in g)
    somma = Counter()
    for _ in range(PERM):
        for g in capo:
            dx = [b for _, b in g]
            rnd.shuffle(dx)
            somma.update((a, b) for (a, _), b in zip(g, dx))
    sc = sorted(((c[k] - somma[k] / PERM) / math.sqrt(somma[k] / PERM + 1), k) for k in c)[::-1][:8]
    return ['-%s / %s-' % k for _, k in sc]


def main():
    rnd = random.Random(384)
    blocchi_v = []
    for pag, pars in e341.pagine().items():
        corti = []
        for par in pars:
            rr = [[tuple(D(w)) for w in r] for r in par]
            rr = [[w for w in r if w] for r in rr]
            if len(rr) >= 4:
                blocchi_v.append([rr])
            else:
                corti.append(rr)
        if corti:
            # paragrafi corti della pagina: si rimescola nella pagina, senza coppie a capo fra paragrafi diversi
            blocchi_v.append(corti)
    ris = OrderedDict()
    v, capo_v = misura(blocchi_v, rnd)
    v['coppie_in_eccesso_a_capo'] = eccessi(capo_v, rnd)
    ris['Voynich'] = v
    print('Voynich', json.dumps(v, default=float), flush=True)
    gib = []
    with zipfile.ZipFile(os.path.join(GB, 'gibberish_transcriptions.zip')) as z:
        for n in sorted(z.namelist()):
            if n.endswith('.txt'):
                righe = [ws for ws in ([w for w in (e381.parola(p) for p in l.split()) if w] for l in z.read(n).decode('utf-8', errors='ignore').splitlines()) if ws]
                gib += [[righe[i:i + 25]] for i in range(0, len(righe), 25)]
    ris['gibberish umano'], _ = misura(gib, rnd)
    print('gibberish', json.dumps(ris['gibberish umano'], default=float), flush=True)
    for k, t in e381.testi().items():
        righe, n = [], 0
        for r in t:
            if n >= 10000:
                break
            righe.append(r)
            n += len(r)
        ris[k.replace('.txt', '')], _ = misura([[righe[i:i + 25]] for i in range(0, len(righe), 25)], rnd)
        print(k, json.dumps(ris[k.replace('.txt', '')], default=float), flush=True)
    sens = [k for k in ris if k not in ('Voynich', 'gibberish umano') and ris[k]['Q'] is not None]
    qs = sorted(ris[k]['Q'] for k in sens)
    V = ris['Voynich']
    if V['Q'] < qs[0] and V['capo']['z'] < 2:
        esito = 'la giuntura non passa a capo: la riga riparte da capo'
    elif qs[0] <= V['Q'] <= qs[-1]:
        esito = 'passa a capo come nella prosa'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('Q_sensati', [qs[0], statistics.median(qs), qs[-1]]), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e384_giuntura_a_capo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e384 — La giuntura passa da una riga all\'altra?', '', 'Preregistrazione: `preregistrazioni/e384.md`.', '',
          '| testo | coppie a capo | E a capo | z | coppie nella riga | E nella riga | z | Q |', '|---|---|---|---|---|---|---|---|']
    for k in ['Voynich', 'gibberish umano'] + sorted(sens, key=lambda k: ris[k]['Q']):
        x = ris[k]
        md.append('| %s | %d | %.4f | %.1f | %d | %.4f | %.1f | %s |' % (k, x['capo']['coppie'], x['capo']['E'], x['capo']['z'], x['riga']['coppie'], x['riga']['E'], x['riga']['z'], '%.2f' % x['Q'] if x['Q'] is not None else ''))
    md += ['', 'Q dei testi sensati (minimo, mediana, massimo): %s.' % ', '.join('%.2f' % q for q in out['Q_sensati']),
           'Coppie più in eccesso a capo nel Voynich: %s.' % ', '.join(V['coppie_in_eccesso_a_capo']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e384_giuntura_a_capo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
