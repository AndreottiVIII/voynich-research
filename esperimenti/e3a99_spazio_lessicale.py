# -*- coding: utf-8 -*-
"""Esperimento e3a99: nei punti in cui lo spazio e' facoltativo, la scelta dipende dalla preferenza lessicale (pezzi piu'
comuni della parola unita) a parita' dei 4 segni attorno? Voynich (ZL) e controllo positivo su tre testi sensati.

Preregistrazione: preregistrazioni/e3a99.md. Scrive risultati/e3a99_spazio_lessicale.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 1000
CONTROLLI = ('Historical - Latin - Literary - NT (Vulgate)', 'Historical - English - Technical - Secreta Alberti', 'Historical - Italian - Technical - Della Pittura')


def parole_di(segni, confini):
    """Parole della riga dati i confini (posizioni di spazio)."""
    tagli = [0] + sorted(confini) + [len(segni)]
    return [tuple(segni[a:b]) for a, b in zip(tagli, tagli[1:]) if b > a]


def analizza(righe):
    """righe: [(segni, {pos: '.'|','|'|'})]. Restituisce [(id riga, strato, y, Lambda)]."""
    f = Counter()
    for segni, sep in righe:
        f.update(parole_di(segni, [i for i, t in sep.items() if t in ('.', ',', '|')]))
    N, V = sum(f.values()), len(f)
    reg = e3a58.Regola([(s[i - 1], s[i], sep.get(i, '') == '.') for s, sep in righe for i in range(1, len(s)) if sep.get(i, '') in ('.', '')])

    def lp(x, togli=0):
        return math.log((f[x] - togli + 0.5) / (N + 0.5 * V))
    out = []
    for k, (s, sep) in enumerate(righe):
        confini = sorted(i for i, t in sep.items() if t in ('.', ',', '|'))
        for i in range(2, len(s) - 1):
            t = sep.get(i, '')
            if t not in ('.', '') or not 0.2 <= reg.p(s[i - 1], s[i]) <= 0.8:
                continue
            a = max([c for c in confini if c < i], default=0)
            b = min([c for c in confini if c > i], default=len(s))
            if t == '.':
                L, R = tuple(s[a:i]), tuple(s[i:b])
                lam = lp(L, 1) + lp(R, 1) - lp(L + R)
                y = 1
            else:
                W = tuple(s[a:b])
                W1, W2 = tuple(s[a:i]), tuple(s[i:b])
                lam = lp(W1) + lp(W2) - lp(W, 1)
                y = 0
            out.append((k, tuple(s[i - 2:i + 2]), y, lam))
    return out


def differenza(punti):
    per = defaultdict(lambda: ([], []))
    for _, st, y, lam in punti:
        per[st][y].append(lam)
    num = den = 0.0
    for l0, l1 in per.values():
        if l0 and l1:
            w = len(l0) * len(l1) / (len(l0) + len(l1))
            num += w * (sum(l1) / len(l1) - sum(l0) / len(l0))
            den += w
    return num / den if den else None


def prova(righe, rnd):
    punti = analizza(righe)
    d = differenza(punti)
    per_riga = defaultdict(list)
    for p in punti:
        per_riga[p[0]].append(p)
    chiavi = list(per_riga)
    boot = []
    for _ in range(BOOT):
        bb = [p for k in (rnd.choice(chiavi) for _ in chiavi) for p in per_riga[k]]
        v = differenza(bb)
        if v is not None:
            boot.append(v)
    boot.sort()
    ic = [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]
    return OrderedDict([('punti', len(punti)), ('con_spazio', sum(p[2] for p in punti)), ('differenza', d), ('IC95', ic)])


def righe_testo(t):
    out = []
    for r in e3a58.righe_prime(t):
        segni, sep = [], {}
        for w in r:
            if segni:
                sep[len(segni)] = '.'
            segni += list(w)
        if segni:
            out.append((tuple(segni), sep))
    return out


def main():
    rnd = random.Random(3199)
    testi = e381.testi()
    ctl = OrderedDict()
    for nome in CONTROLLI:
        k = nome + '.txt'
        ctl[nome] = prova(righe_testo(testi[k]), rnd)
        print(nome, json.dumps(ctl[nome]), flush=True)
    passa = sum(1 for x in ctl.values() if x['IC95'][0] > 0) >= 2
    voy = prova(list(e3a60.righe('ZL').values()), rnd)
    print('Voynich', json.dumps(voy), flush=True)
    if not passa:
        esito = 'test non informativo'
    else:
        ic = voy['IC95']
        esito = 'lo spazio dipende anche dalla parola intera' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'solo dai segni vicini')
    med = sorted(x['differenza'] for x in ctl.values())[1]
    out = OrderedDict([('controlli', ctl), ('controllo_passa', passa), ('Voynich', voy), ('rapporto_voynich_su_mediana_controlli', voy['differenza'] / med if med else None), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a99_spazio_lessicale.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a99 — Lo spazio facoltativo dipende dalla parola intera o solo dai segni vicini?', '', 'Preregistrazione: `preregistrazioni/e3a99.md`. Differenza = Λ medio dove c\'è lo spazio − dove non c\'è, a parità dei 4 segni attorno.', '',
          '| testo | punti facoltativi | con spazio | differenza | IC 95% |', '|---|---|---|---|---|']
    md += ['| %s (controllo) | %d | %d | %+.3f | %+.3f – %+.3f |' % (k, x['punti'], x['con_spazio'], x['differenza'], x['IC95'][0], x['IC95'][1]) for k, x in ctl.items()]
    md.append('| **Voynich (ZL)** | %d | %d | %+.3f | %+.3f – %+.3f |' % (voy['punti'], voy['con_spazio'], voy['differenza'], voy['IC95'][0], voy['IC95'][1]))
    md += ['', 'Controllo positivo: **%s**. Rapporto Voynich / mediana dei controlli: %.2f.' % ('passa' if passa else 'non passa', out['rapporto_voynich_su_mediana_controlli']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a99_spazio_lessicale.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
