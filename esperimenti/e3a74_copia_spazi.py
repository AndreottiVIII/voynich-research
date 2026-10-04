# -*- coding: utf-8 -*-
"""Esperimento e3a74: nei punti facoltativi, accordo della scelta di spazio fra una riga e la riga sopra che contiene lo
stesso tratto di 4 segni, contro una riga lontana della stessa pagina che lo contiene; dentro gli strati del tratto.

Preregistrazione: preregistrazioni/e3a74.md. Scrive risultati/e3a74_copia_spazi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 1000


def scelta(sep, i):
    """'s' spazio, 'n' niente, None se virgola o salto."""
    t = sep.get(i, '')
    return 's' if t == '.' else ('n' if t == '' else None)


def trova(segni, tratto):
    for j in range(len(segni) - 3):
        if tuple(segni[j:j + 4]) == tratto:
            return j + 2
    return None


def differenza(coppie):
    """coppie: [(pagina, tratto, tipo, accordo)]."""
    per = defaultdict(lambda: {'sopra': [], 'lontana': []})
    for _, t, tipo, acc in coppie:
        per[t][tipo].append(acc)
    num = den = 0.0
    for x in per.values():
        a, f = x['sopra'], x['lontana']
        if a and f:
            w = len(a) * len(f) / (len(a) + len(f))
            num += w * (sum(a) / len(a) - sum(f) / len(f))
            den += w
    return num / den if den else 0.0, den


def main():
    rnd = random.Random(3174)
    pulite = e3a60.righe('ZL')
    ordine = defaultdict(list)
    npar = 0
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        if r.inizio_par:
            npar += 1
        ordine[r.pagina].append((r.numero, npar))
    pos = []
    for segni, sep in pulite.values():
        pos += [(segni[i - 1], segni[i], sep.get(i, '') == '.') for i in range(1, len(segni)) if sep.get(i, '') in ('.', '')]
    reg = e3a58.Regola(pos)
    coppie = []
    for pg, righe in ordine.items():
        for k, (num, par) in enumerate(righe):
            if (pg, num) not in pulite:
                continue
            segni, sep = pulite[(pg, num)]
            sopra = None
            if k >= 1 and righe[k - 1][1] == par and (pg, righe[k - 1][0]) in pulite:
                sopra = pulite[(pg, righe[k - 1][0])]
            lontane = [pulite[(pg, n2)] for k2, (n2, _) in enumerate(righe) if abs(k2 - k) >= 3 and (pg, n2) in pulite]
            for i in range(2, len(segni) - 1):
                if i + 2 > len(segni):
                    continue
                y = scelta(sep, i)
                if y is None or not 0.2 <= reg.p(segni[i - 1], segni[i]) <= 0.8:
                    continue
                tratto = tuple(segni[i - 2:i + 2])
                if len(tratto) < 4:
                    continue
                if sopra is not None:
                    j = trova(sopra[0], tratto)
                    if j is not None:
                        y2 = scelta(sopra[1], j)
                        if y2 is not None:
                            coppie.append((pg, tratto, 'sopra', int(y == y2)))
                cand = [(l, trova(l[0], tratto)) for l in lontane]
                cand = [(l, j) for l, j in cand if j is not None and scelta(l[1], j) is not None]
                if cand:
                    l, j = rnd.choice(cand)
                    coppie.append((pg, tratto, 'lontana', int(y == scelta(l[1], j))))
    d, peso = differenza(coppie)
    pagine = sorted({c[0] for c in coppie})
    per_pg = defaultdict(list)
    for c in coppie:
        per_pg[c[0]].append(c)
    boot = []
    for _ in range(BOOT):
        cc = [c for pg in (rnd.choice(pagine) for _ in pagine) for c in per_pg[pg]]
        boot.append(differenza(cc)[0])
    boot.sort()
    ic = [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]]
    esito = 'lo scriba ricopia anche gli spazi' if ic[0] > 0 else ('la copia cambia gli spazi più del caso' if ic[1] < 0 else 'lo spazio si decide di nuovo')
    grezzo = OrderedDict()
    for tipo in ('sopra', 'lontana'):
        xs = [c[3] for c in coppie if c[2] == tipo]
        grezzo[tipo] = OrderedDict([('coppie', len(xs)), ('accordo', sum(xs) / len(xs) if xs else None)])
    out = OrderedDict([('grezzo', grezzo), ('differenza_pesata', d), ('peso_totale', peso), ('IC95', ic), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a74_copia_spazi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a74 — Quando ripete un pezzo della riga sopra, lo scriba ricopia anche gli spazi facoltativi?', '', 'Preregistrazione: `preregistrazioni/e3a74.md`.', '',
          '| confronto | coppie | accordo grezzo |', '|---|---|---|']
    md += ['| %s | %d | %s |' % (k, x['coppie'], '%.3f' % x['accordo'] if x['accordo'] is not None else 'n.d.') for k, x in grezzo.items()]
    md += ['', 'Differenza pesata dentro gli strati del tratto (sopra − lontana): **%+.3f**, IC 95%% %+.3f – %+.3f (peso totale %.1f).' % (d, ic[0], ic[1], peso), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a74_copia_spazi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
