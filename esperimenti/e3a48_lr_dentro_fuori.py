# -*- coding: utf-8 -*-
"""Esperimento e3a48: preferenza l/r secondo il segno seguente (K contro A) dentro le parole comuni e fra parole separate.

Preregistrazione: preregistrazioni/e3a48.md. Scrive risultati/e3a48_lr_dentro_fuori.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
K, A = {'k', 't', 'd', 'l', 's', 'q'}, {'a', 'o', 'y'}


def delta(conti):
    """conti: Counter con chiavi (classe, l?)."""
    nk = conti[('K', True)] + conti[('K', False)]
    na = conti[('A', True)] + conti[('A', False)]
    if not nk or not na:
        return None
    return conti[('K', True)] / nk - conti[('A', True)] / na


def main():
    rnd = random.Random(3148)
    rr = e386.righe()
    freq = Counter(w for st, pag, npar, ws, seps in rr for w in ws if w)
    dentro, fra = defaultdict(Counter), defaultdict(Counter)
    for st, pag, npar, ws, seps in rr:
        for w in ws:
            if w and freq[w] >= 5:
                for a, b in zip(w[:-1], w[1:]):
                    if a in ('l', 'r') and (b in K or b in A):
                        dentro[pag][('K' if b in K else 'A', a == 'l')] += 1
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if a and b and seps[j] == '.' and len(a) >= 2 and a[-1] in ('l', 'r') and (b[0] in K or b[0] in A):
                fra[pag][('K' if b[0] in K else 'A', a[-1] == 'l')] += 1
    ris = OrderedDict()
    for nome, d in (('dentro le parole comuni', dentro), ('fra parole separate', fra)):
        tot = Counter()
        for c in d.values():
            tot.update(c)
        pagine = list(d.values())
        boot = []
        for _ in range(2000):
            c = Counter()
            for _ in pagine:
                c.update(pagine[rnd.randrange(len(pagine))])
            v = delta(c)
            if v is not None:
                boot.append(v)
        boot.sort()
        n = len(boot)
        ris[nome] = OrderedDict([('eventi', sum(tot.values())), ('P_l_K', tot[('K', True)] / (tot[('K', True)] + tot[('K', False)])),
                                 ('P_l_A', tot[('A', True)] / (tot[('A', True)] + tot[('A', False)])), ('delta', delta(tot)), ('IC95', [boot[int(0.025 * n)], boot[int(0.975 * n) - 1]])])
        print(nome, json.dumps(ris[nome]), flush=True)
    di, fr = ris['dentro le parole comuni'], ris['fra parole separate']
    r = di['delta'] / fr['delta'] if fr['delta'] else None
    if di['IC95'][0] > 0 and fr['delta'] > 0 and r is not None and 0.5 <= r <= 2:
        esito = 'stessa regola dentro e fra le parole'
    elif (di['IC95'][1] < 0 and fr['delta'] > 0) or (di['IC95'][0] > 0 and fr['delta'] < 0):
        esito = 'regole diverse'
    else:
        esito = 'in parte'
    out = OrderedDict([('misure', ris), ('rapporto', r), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a48_lr_dentro_fuori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a48 — La regola -l/-r fra parole è la stessa che dentro le parole?', '', 'Preregistrazione: `preregistrazioni/e3a48.md`.', '',
          '| dove | eventi | P(l | segno dopo in K) | P(l | in A) | Δ | IC 95% |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.3f | %+.3f | %+.3f – %+.3f |' % (k, x['eventi'], x['P_l_K'], x['P_l_A'], x['delta'], x['IC95'][0], x['IC95'][1]) for k, x in ris.items()]
    md += ['', 'Rapporto Δ dentro / Δ fra: %s. Esito: **%s**.' % ('%.2f' % r if r is not None else 'n.d.', esito)]
    open(os.path.join(RISULTATI, 'e3a48_lr_dentro_fuori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
