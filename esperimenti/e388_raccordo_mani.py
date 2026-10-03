# -*- coding: utf-8 -*-
"""Esperimento 388: la regola di raccordo dell'e380 (qo-/o- secondo la parola prima, -l/-r secondo la parola dopo) per
ogni mano di Davis, con intervalli bootstrap sulle pagine.

Preregistrazione: preregistrazioni/e388.md. Scrive risultati/e388_raccordo_mani.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}
A, K = {'a'}, {'k', 't', 'd', 'l', 's', 'q'}
MIN = 50


def main():
    rnd = random.Random(388)
    mano_pag, info = {}, defaultdict(Counter)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        mano_pag.setdefault(r.pagina, r.mano or '?')
        info[r.mano or '?']['%s-%s' % (r.sezione or '?', r.lingua or '?')] += len(r.parole)
    # per mano -> pagina -> contatori
    qo = defaultdict(lambda: defaultdict(Counter))
    lr = defaultdict(lambda: defaultdict(Counter))
    for st, pag, par, ws, seps in e386.righe():
        h = mano_pag.get(pag, '?')
        for j in range(len(ws) - 1):
            a, b = ws[j], ws[j + 1]
            if not a or not b or seps[j] != '.':
                continue
            x = e380.ini_qo(b)
            if x:
                cl = 'V' if a[-1] in V else ('C' if a[-1] in C else None)
                if cl:
                    qo[h][pag][(cl, x[1] == 'qo')] += 1
            y = e380.fin_lr(a)
            if y:
                cl = 'K' if b[0] in K else ('A' if b[0] in A else None)
                if cl:
                    lr[h][pag][(cl, y[1] == 'l')] += 1

    def delta(pagine, alta, bassa):
        c = Counter()
        for p in pagine:
            c.update(p)
        na, nb = c[(alta, True)] + c[(alta, False)], c[(bassa, True)] + c[(bassa, False)]
        if not na or not nb:
            return None, na, nb
        return c[(alta, True)] / na - c[(bassa, True)] / nb, na, nb
    ris = OrderedDict()
    for nome, dati, alta, bassa in (('qo', qo, 'V', 'C'), ('l', lr, 'K', 'A')):
        per = OrderedDict()
        for h in sorted(dati):
            pagine = list(dati[h].values())
            d, na, nb = delta(pagine, alta, bassa)
            if d is None or na < MIN or nb < MIN:
                per[h] = OrderedDict([('eventi', [na, nb]), ('usabile', False)])
                continue
            boot = []
            for _ in range(1000):
                b = delta([pagine[rnd.randrange(len(pagine))] for _ in pagine], alta, bassa)[0]
                if b is not None:
                    boot.append(b)
            boot.sort()
            k = len(boot)
            per[h] = OrderedDict([('eventi', [na, nb]), ('usabile', True), ('pagine', len(pagine)), ('delta', d), ('IC95', [boot[int(0.025 * k)], boot[int(0.975 * k) - 1]])])
        ris[nome] = per
        print(nome, json.dumps(per, default=float), flush=True)
    usabili = [(n, h, x) for n, per in ris.items() for h, x in per.items() if x['usabile']]
    condivisa = all(x['IC95'][0] > 0 for _, _, x in usabili) and all(any(x['usabile'] for x in ris[n].values()) for n in ris)
    esito = 'regola condivisa da tutte le mani' if condivisa else 'regola di alcune mani'
    out = OrderedDict([('regole', ris), ('mani', {h: dict(c.most_common(4)) for h, c in info.items()}), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e388_raccordo_mani.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e388 — La regola di raccordo è la stessa per tutti gli scribi?', '', 'Preregistrazione: `preregistrazioni/e388.md`.', '',
          '| regola | mano | eventi (classi) | pagine | Δ | IC 95% | strati principali della mano |', '|---|---|---|---|---|---|---|']
    for n, per in ris.items():
        for h, x in per.items():
            strati = ', '.join('%s %d' % kv for kv in info[h].most_common(3))
            if x['usabile']:
                md.append('| %s | %s | %d / %d | %d | %+.3f | %+.3f – %+.3f | %s |' % ('qo-/o-' if n == 'qo' else '-l/-r', h, x['eventi'][0], x['eventi'][1], x['pagine'], x['delta'], x['IC95'][0], x['IC95'][1], strati))
            else:
                md.append('| %s | %s | %d / %d | — | (pochi eventi) | | %s |' % ('qo-/o-' if n == 'qo' else '-l/-r', h, x['eventi'][0], x['eventi'][1], strati))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e388_raccordo_mani.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
