# -*- coding: utf-8 -*-
"""Esperimento e3b12: quota di spazi nei punti facoltativi, ultimo terzo della riga contro primo, dentro strati (4 segni
attorno x lunghezze dei pezzi); confronto con gli strati della sola coppia di segni.

Preregistrazione: preregistrazioni/e3b12.md. Scrive risultati/e3b12_fine_riga_lunghezza.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a60_spazi_due_trascrittori as e3a60
import e3a64_spazi_fine_riga as e3a64
import e3b01_taratura_lessicale as e3b01
import e3b03_lessicale_lunghezza as e3b03

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 2000


def prova(punti_terzi, rnd):
    """punti_terzi: [(strato, terzo, y)] con terzo in (1, 3)."""
    strati = defaultdict(list)
    for st, t, y in punti_terzi:
        strati[st].append((t, y))
    d = e3a64.differenza(strati)
    nul = []
    for _ in range(PERM):
        s2 = {}
        for k, xs in strati.items():
            tt = [t for t, _ in xs]
            rnd.shuffle(tt)
            s2[k] = list(zip(tt, [y for _, y in xs]))
        nul.append(e3a64.differenza(s2))
    p = (1 + sum(1 for v in nul if abs(v) >= abs(d))) / (1 + PERM)
    return OrderedDict([('differenza', d), ('p', p), ('punti', len(punti_terzi))])


def main():
    rnd = random.Random(3212)
    righe = list(e3a60.righe('ZL').values())
    punti = e3b01.punti_fissi(righe)
    lun = e3b03.lunghezze(righe, punti)
    con_l, solo_c = [], []
    for (k, i, st, y), l in zip(punti, lun):
        x = i / len(righe[k][0])
        t = 1 if x < 1 / 3 else (3 if x > 2 / 3 else 2)
        if t == 2:
            continue
        con_l.append(((st,) + l, t, y))
        solo_c.append(((st[1], st[2]), t, y))
    a = prova(con_l, rnd)
    b = prova(solo_c, rnd)
    if a['differenza'] < 0 and a['p'] < 0.01:
        esito = 'il calo a fine riga resta a parità di lunghezza'
    elif a['p'] >= 0.05:
        esito = "era un effetto della lunghezza"
    else:
        esito = 'incerto'
    out = OrderedDict([('con_lunghezze', a), ('solo_coppia_di_segni', b), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b12_fine_riga_lunghezza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b12 — Gli spazi facoltativi calano a fine riga anche a parità di lunghezza dei pezzi?', '', 'Preregistrazione: `preregistrazioni/e3b12.md`. e3a64: −0,043 (p 0,0005) con gli strati della coppia di segni.', '',
          '| strati | punti (primo e ultimo terzo) | differenza ultimo − primo terzo | p |', '|---|---|---|---|',
          '| 4 segni attorno × lunghezze dei pezzi | %d | %+.4f | %.4f |' % (a['punti'], a['differenza'], a['p']),
          '| sola coppia di segni (come e3a64) | %d | %+.4f | %.4f |' % (b['punti'], b['differenza'], b['p']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b12_fine_riga_lunghezza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
