# -*- coding: utf-8 -*-
"""Esperimento 137b: la dipendenza di ordine 2 degli inizi di riga (e137) resta con catene del primo ordine stimate per
gruppo (sezione + mano; fascicolo)?

Preregistrazione: preregistrazioni/e137b.md. Scrive risultati/e137b_eterogeneita.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e71_bordo_riga as e71
import e106_procedimento_versi as e106
import e137_ciclo_inizi as e137

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, SIMULAZIONI = 1372, 1000


def sequenze_gruppi(q, chiave):
    seq, gr, cur, pag, g = [], [], [], None, None
    for r in trascrizione.testo_corrente(trascrizione.leggi(q)):
        if not r.parole:
            continue
        if r.inizio_par or r.pagina != pag:
            if len(cur) >= 2:
                seq.append(cur)
                gr.append(g)
            cur, pag, g = ['P'], r.pagina, chiave(r)
            continue
        w = r.parole[0]
        cur.append(e106.classe(w) if trascrizione.pulita(w) else '?')
    if len(cur) >= 2:
        seq.append(cur)
        gr.append(g)
    return seq, gr


def ts_gruppi():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    seq, gr, cur, g = [], [], [], None
    for i, (ini, ps) in enumerate(rr):
        if ini or i % 29 == 0:
            if len(cur) >= 2:
                seq.append(cur)
                gr.append(g)
            cur, g = ['P'], i // (29 * 10)
            continue
        cur.append(e106.classe(ps[0]) if ps else '?')
    if len(cur) >= 2:
        seq.append(cur)
        gr.append(g)
    return seq, gr


def markov_gruppi(seq, gr, rnd):
    per = defaultdict(list)
    for s, g in zip(seq, gr):
        per[g].append(s)
    tab = {}
    for g, ss in per.items():
        tr = defaultdict(Counter)
        for s in ss:
            for a, b in zip(s, s[1:]):
                tr[a][b] += 1
        tab[g] = {a: (list(c), list(c.values())) for a, c in tr.items()}
    out = []
    for s, g in zip(seq, gr):
        x = ['P']
        t = tab[g]
        for _ in range(len(s) - 1):
            st, w = t.get(x[-1], t['P'])
            x.append(rnd.choices(st, w)[0])
        out.append(x)
    return out


def valuta(seq, gr, rnd):
    reale = e137.cmi(seq)
    nulli = [e137.cmi(markov_gruppi(seq, gr, rnd)) for _ in range(SIMULAZIONI)]
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('gruppi', len(set(gr))), ('cmi', reale), ('nullo', m), ('z', (reale - m) / s if s else None)])


def main():
    rnd = random.Random(SEME)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        for nome_n, chiave in (('N1 sezione + mano', lambda r: (r.sezione, r.mano)), ('N2 fascicolo', lambda r: r.quire)):
            seq, gr = sequenze_gruppi(q, chiave)
            ris['Voynich %s, %s' % (q, nome_n)] = valuta(seq, gr, rnd)
    seq, gr = sequenze_gruppi('ZL', lambda r: (r.sezione, r.mano))
    ris['controllo positivo (ciclo di 4), N1'] = valuta(e137.ciclo(seq, random.Random(SEME + 1)), gr, rnd)
    seq, gr = ts_gruppi()
    ris['Timm e Schinner, blocchi di 10 pagine'] = valuta(seq, gr, rnd)
    for k, r in ris.items():
        print('%-44s gruppi %3d | CMI %.4f nullo %.4f z %.1f' % (k, r['gruppi'], r['cmi'], r['nullo'], r['z'] or 0), flush=True)
    z = lambda k: ris[k]['z'] or 0
    valido = z('controllo positivo (ciclo di 4), N1') > 10
    conferma = all(z('Voynich %s, %s' % (q, n)) > 4 for q in ('ZL', 'IT') for n in ('N1 sezione + mano', 'N2 fascicolo'))
    artefatto = any(z('Voynich %s, %s' % (q, n)) < 2 for q in ('ZL', 'IT') for n in ('N1 sezione + mano', 'N2 fascicolo'))
    esito = 'numerazione confermata' if conferma else 'artefatto di eterogeneita' if artefatto else 'indeciso'
    ris['valido'], ris['esito'] = valido, esito
    print('controllo valido:', valido, '| esito:', esito)
    with open(os.path.join(RISULTATI, 'e137b_eterogeneita.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e137b — La dipendenza di ordine 2 degli inizi viene dall\'eterogeneità?', '', 'CMI I(c_i ; c_i−2 | c_i−1) contro %d catene del primo ordine stimate per gruppo. '
           'Preregistrazione: `preregistrazioni/e137b.md`.' % SIMULAZIONI, '', '| testo e nullo | gruppi | CMI | nullo | z |', '|---|---|---|---|---|']
    for k, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.4f | %.4f | %.1f |' % (k, r['gruppi'], r['cmi'], r['nullo'], r['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e137b_eterogeneita.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
