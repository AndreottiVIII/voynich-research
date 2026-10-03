# -*- coding: utf-8 -*-
"""Esperimento e3a05: giuntura nella riga e a capo con la trascrizione di Glen Claston (alfabeto v101, un carattere = un
segno).

Preregistrazione: preregistrazioni/e3a05.md. Scrive risultati/e3a05_glen_claston.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e390_scomposizione as e390

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3105)
    righe, npar = [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('GC')):
        if r.inizio_par:
            npar += 1
        ws = [tuple(w) if trascrizione.pulita(w) else None for w in r.parole]
        if ws:
            righe.append((r.pagina, npar, ws))
    riga, capo = defaultdict(list), defaultdict(list)
    for k, (pag, npar, ws) in enumerate(righe):
        for a, b in zip(ws, ws[1:]):
            if a and b:
                riga[pag].append((a[-1], b[0]))
        if k + 1 < len(righe) and righe[k + 1][0] == pag and righe[k + 1][1] == npar and ws[-1] and righe[k + 1][2][0]:
            capo[pag].append((ws[-1][-1], righe[k + 1][2][0][0]))
    g = e390.prova(riga, rnd, dettaglio=True)
    c = e390.prova(capo, rnd)
    coppie_riga = [(p, x) for p, xs in riga.items() for x in xs]
    n = c['coppie']
    sub = []
    for _ in range(20):
        camp = defaultdict(list)
        for p, x in rnd.sample(coppie_riga, n):
            camp[p].append(x)
        sub.append(e390.prova(camp, rnd)['E'])
    Ep = statistics.median(sub)
    Q = c['E'] / Ep if Ep > 0 else None
    prove = OrderedDict([('1', g['z'] > 3), ('2', c['z'] < 2), ('3', Q is not None and Q < 0.3)])
    esito = 'la giuntura si ripete con Glen Claston' if all(prove.values()) else 'non si ripete: manca ' + ', '.join(k for k, v in prove.items() if not v)
    out = OrderedDict([('riga', g), ('capo', c), ('riga_a_parita_di_coppie', Ep), ('Q', Q), ('prove', prove), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a05_glen_claston.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a05 — La giuntura con la trascrizione di Glen Claston (alfabeto v101)', '', 'Preregistrazione: `preregistrazioni/e3a05.md`.', '',
          'Nella riga: E %.4f, z %.1f (%d coppie). A capo: E %.4f, z %.1f (%d coppie). Nella riga a parità di coppie: E %.4f. Q = %s.' % (
              g['E'], g['z'], g['coppie'], c['E'], c['z'], c['coppie'], Ep, '%.2f' % Q if Q is not None else 'n.d.'), '',
          '## Coppie (v101) che contano di più', '', '| coppia | contributo | quante |', '|---|---|---|']
    md += ['| %s | %+.5f | %d |' % tuple(x) for x in g['contributi'][:10]]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a05_glen_claston.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
