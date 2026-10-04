# -*- coding: utf-8 -*-
"""Esperimento e3b46: e3a74 (la copia dalla riga sopra porta con sé gli spazi facoltativi) con la trascrizione di
Takahashi, e confronto fra la riga subito sopra e quella a distanza 2 (controllo della deriva), con ZL e IT.

Preregistrazione: preregistrazioni/e3b46.md. Scrive risultati/e3b46_copia_spazi_repliche.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3a58_spazi_prevedibili as e3a58
import e3a60_spazi_due_trascrittori as e3a60
import e3a74_copia_spazi as e3a74

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 1000


def coppie_di(quale, rnd):
    """{'lontana': [...], 'due': [...]}: coppie (pagina, tratto, 'sopra'|tipo, accordo) per i due confronti."""
    pulite = e3a60.righe(quale)
    ordine = defaultdict(list)
    npar = 0
    for r in trascrizione.leggi(quale):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        if r.inizio_par:
            npar += 1
        ordine[r.pagina].append((r.numero, npar))
    pos = []
    for segni, sep in pulite.values():
        pos += [(segni[i - 1], segni[i], sep.get(i, '') == '.') for i in range(1, len(segni)) if sep.get(i, '') in ('.', '')]
    reg = e3a58.Regola(pos)
    out = {'lontana': [], 'due': []}
    for pg, righe in ordine.items():
        for k, (num, par) in enumerate(righe):
            if (pg, num) not in pulite:
                continue
            segni, sep = pulite[(pg, num)]
            sopra = due = None
            if k >= 1 and righe[k - 1][1] == par and (pg, righe[k - 1][0]) in pulite:
                sopra = pulite[(pg, righe[k - 1][0])]
            if k >= 2 and righe[k - 2][1] == par and (pg, righe[k - 2][0]) in pulite:
                due = pulite[(pg, righe[k - 2][0])]
            lontane = [pulite[(pg, n2)] for k2, (n2, _) in enumerate(righe) if abs(k2 - k) >= 3 and (pg, n2) in pulite]
            for i in range(2, len(segni) - 1):
                y = e3a74.scelta(sep, i)
                if y is None or not 0.2 <= reg.p(segni[i - 1], segni[i]) <= 0.8:
                    continue
                tratto = tuple(segni[i - 2:i + 2])
                if len(tratto) < 4:
                    continue
                acc_sopra = None
                if sopra is not None:
                    j = e3a74.trova(sopra[0], tratto)
                    if j is not None:
                        y2 = e3a74.scelta(sopra[1], j)
                        if y2 is not None:
                            acc_sopra = int(y == y2)
                if acc_sopra is not None:
                    out['lontana'].append((pg, tratto, 'sopra', acc_sopra))
                    out['due'].append((pg, tratto, 'sopra', acc_sopra))
                cand = [(l, e3a74.trova(l[0], tratto)) for l in lontane]
                cand = [(l, j) for l, j in cand if j is not None and e3a74.scelta(l[1], j) is not None]
                if cand:
                    l, j = rnd.choice(cand)
                    out['lontana'].append((pg, tratto, 'lontana', int(y == e3a74.scelta(l[1], j))))
                if due is not None:
                    j = e3a74.trova(due[0], tratto)
                    if j is not None:
                        y3 = e3a74.scelta(due[1], j)
                        if y3 is not None:
                            out['due'].append((pg, tratto, 'lontana', int(y == y3)))
    return out


def stima(coppie, rnd):
    d, peso = e3a74.differenza(coppie)
    per_pg = defaultdict(list)
    for c in coppie:
        per_pg[c[0]].append(c)
    pagine = sorted(per_pg)
    boot = sorted(e3a74.differenza([c for pg in (rnd.choice(pagine) for _ in pagine) for c in per_pg[pg]])[0] for _ in range(BOOT))
    n = {t: sum(1 for c in coppie if c[2] == t) for t in ('sopra', 'lontana')}
    return OrderedDict([('coppie_sopra', n['sopra']), ('coppie_confronto', n['lontana']), ('differenza', d), ('peso', peso),
                        ('IC95', [boot[int(0.025 * BOOT)], boot[int(0.975 * BOOT) - 1]])])


def main():
    rnd = random.Random(3246)
    ris = OrderedDict()
    for quale in ('ZL', 'IT'):
        cc = coppie_di(quale, rnd)
        ris[quale] = OrderedDict([('sopra_contro_lontana', stima(cc['lontana'], rnd)), ('sopra_contro_due', stima(cc['due'], rnd))])
        print(quale, json.dumps(ris[quale], ensure_ascii=False), flush=True)
    it = ris['IT']['sopra_contro_lontana']['IC95']
    es1 = 'si ritrova con Takahashi' if it[0] > 0 else ('al contrario' if it[1] < 0 else 'non si ritrova')
    dd = [ris[q]['sopra_contro_due'] for q in ('ZL', 'IT')]
    if all(x['differenza'] > 0 for x in dd) and any(x['IC95'][0] > 0 for x in dd):
        es2 = 'non è una deriva'
    elif all(x['IC95'][0] <= 0 <= x['IC95'][1] for x in dd):
        es2 = 'può essere una deriva'
    else:
        es2 = 'incerto'
    out = OrderedDict([('trascrizioni', ris), ('esito_1', es1), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b46_copia_spazi_repliche.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b46 — La copia porta con sé gli spazi: Takahashi e controllo della deriva', '', 'Preregistrazione: `preregistrazioni/e3b46.md`. ZL nell\'e3a74: sopra − lontana +0,049 (IC +0,009 – +0,089).', '',
          '| trascrizione | confronto | coppie sopra | coppie confronto | differenza pesata (IC 95%) |', '|---|---|---|---|---|']
    for q, x in ris.items():
        for nome, et in (('sopra_contro_lontana', 'sopra − lontana (3+)'), ('sopra_contro_due', 'sopra − distanza 2')):
            y = x[nome]
            md.append('| %s | %s | %d | %d | %+.3f (%+.3f – %+.3f) |' % (q, et, y['coppie_sopra'], y['coppie_confronto'], y['differenza'], y['IC95'][0], y['IC95'][1]))
    md += ['', 'Esito 1: **%s**. Esito 2: **%s**.' % (es1, es2)]
    open(os.path.join(RISULTATI, 'e3b46_copia_spazi_repliche.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
