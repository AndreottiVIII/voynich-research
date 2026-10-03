# -*- coding: utf-8 -*-
"""Esperimento e3a37: quota dell'incertezza su qo-/o- e -l/-r tolta dalla parola stessa (nucleo o tronco), dal contesto
(e3a36) e dai due insieme (combinati come quote indipendenti), pagine pari contro dispari.

Preregistrazione: preregistrazioni/e3a37.md. Scrive risultati/e3a37_parola_e_contesto.json e .md.
"""
import json, math, os, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e380_sandhi as e380
import e3a36_prevedibili as e3a36

RISULTATI = os.path.join(QUI, '..', 'risultati')


def eventi_con_parola():
    """Come e3a36.eventi, ma con la parola: (pagina, contesto, esito, nucleo)."""
    qo, lr = e3a36.eventi()
    # e3a36.eventi non conserva la parola: la ricostruiamo rileggendo nello stesso ordine
    parole_qo, parole_lr = [], []
    for r in trascrizione.leggi('ZL'):
        ws, seps = e3a36.parse(r)
        for w in ws:
            if not w:
                continue
            q = e380.ini_qo(w)
            if q:
                parole_qo.append(q[0])
            f = e380.fin_lr(w)
            if f:
                parole_lr.append(f[0])
    assert len(parole_qo) == len(qo) and len(parole_lr) == len(lr)
    return [e + (p,) for e, p in zip(qo, parole_qo)], [e + (p,) for e, p in zip(lr, parole_lr)]


def valuta(ev, chiavi):
    pagine = sorted({e[0] for e in ev})
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    ris = {m: [0.0, 0, 0] for m in ('parola', 'contesto', 'insieme')}
    hb_tot = 0.0
    okb = n = 0
    for prova in (0, 1):
        tp, tc, base = defaultdict(lambda: [1, 1]), defaultdict(lambda: [1, 1]), [1, 1]
        for p, ctx, y, w in ev:
            if meta[p] != prova:
                tp[w][y] += 1
                tc[tuple(ctx[k] for k in chiavi)][y] += 1
                base[y] += 1
        pb = base[1] / sum(base)
        ob = pb / (1 - pb)
        for p, ctx, y, w in ev:
            if meta[p] != prova:
                continue
            pw = tp[w][1] / sum(tp[w]) if w in tp else pb
            c = tc[tuple(ctx[k] for k in chiavi)]
            pc = c[1] / sum(c)
            o = (pw / (1 - pw)) * (pc / (1 - pc)) / ob
            pi = o / (1 + o)
            for m, pm in (('parola', pw), ('contesto', pc), ('insieme', pi)):
                ris[m][0] -= math.log2(pm if y else 1 - pm)
                ris[m][1] += (pm >= 0.5) == y
            hb_tot -= math.log2(pb if y else 1 - pb)
            okb += (pb >= 0.5) == y
            n += 1
    out = OrderedDict()
    for m, (h, ok, _) in ris.items():
        out[m] = OrderedDict([('incertezza_tolta', 1 - h / hb_tot), ('accuratezza', ok / n)])
    out['accuratezza_base'] = okb / n
    out['eventi'] = n
    return out


def main():
    qo, lr = eventi_con_parola()
    ris = OrderedDict([('qo-/o-', valuta(qo, ['posto', 'prima', 'sopra', 'lingua'])), ('-l/-r', valuta(lr, ['posto', 'dopo', 'lingua']))])
    for k, x in ris.items():
        t = x['insieme']['incertezza_tolta']
        x['esito'] = 'scelta in gran parte decisa' if t > 0.5 else ('in gran parte libera' if t < 0.25 else 'in parte decisa')
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a37_parola_e_contesto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a37 — Quanto aggiunge la parola stessa alla scelta qo-/o- e -l/-r?', '', 'Preregistrazione: `preregistrazioni/e3a37.md`.', '',
          '| scelta | eventi | modello | incertezza tolta | accuratezza | scelta più frequente |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        for m in ('parola', 'contesto', 'insieme'):
            md.append('| %s | %d | %s | %.1f%% | %.1f%% | %.1f%% |' % (k, x['eventi'], m, 100 * x[m]['incertezza_tolta'], 100 * x[m]['accuratezza'], 100 * x['accuratezza_base']))
    md += ['', 'Esito: *qo*-/*o*- **%s**; -*l*/-*r* **%s**.' % (ris['qo-/o-']['esito'], ris['-l/-r']['esito'])]
    open(os.path.join(RISULTATI, 'e3a37_parola_e_contesto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
