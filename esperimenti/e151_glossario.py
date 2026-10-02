# -*- coding: utf-8 -*-
"""Esperimento 151: i paragrafi della sezione delle ricette (S) sono in ordine da glossario? Prefissi condivisi fra le
prime parole di paragrafi consecutivi, contro rimescolamenti nella pagina; controllo positivo: Alphita.

Preregistrazione: preregistrazioni/e151.md. Scrive risultati/e151_glossario.json e .md.
"""
import hashlib, json, os, random, re, statistics, sys, unicodedata
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e30_elenchi_medievali as e30

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, BLOCCO = 151, 2000, 10
D = misure.divisore(misure.GLIFI_EVA)
G = {'p', 't', 'k', 'f'}


def prime_voynich(sezione):
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione=sezione):
        if r.inizio_par and r.parole and trascrizione.pulita(r.parole[0]):
            u = D(r.parole[0])
            if len(u) >= 3 and u[0] in G:
                u = u[1:]
            out.append((r.pagina, u))
    return out


def lemmi_alphita():
    nome, sha, da, a = e30.OCR['Alphita (glossario, XIII sec.)']
    percorso = os.path.join(e30.ELENCHI, nome)
    if hashlib.sha256(open(percorso, 'rb').read()).hexdigest() != sha:
        raise SystemExit('OCR diverso')
    righe = open(percorso, encoding='utf-8', errors='replace').read().splitlines()[da - 1:a - 1]
    out, vuota = [], True
    for l in righe:
        s = l.strip()
        if not s:
            vuota = True
            continue
        if vuota:
            m = re.match(r'^([A-Z][a-zA-Z]+)', s)
            if m:
                w = unicodedata.normalize('NFD', m.group(1).lower())
                w = ''.join(c for c in w if c.isalpha() and not unicodedata.combining(c))
                if len(w) >= 3:
                    out.append((len(out) // BLOCCO, list(w)))
        vuota = False
    return out


def quota(seq, k):
    cc = [(a, b) for (pa, a), (pb, b) in zip(seq, seq[1:])]
    return sum(a[:k] == b[:k] for a, b in cc) / len(cc)


def valuta(seq, rnd):
    out = OrderedDict([('voci', len(seq))])
    per = defaultdict(list)
    for i, (p, _) in enumerate(seq):
        per[p].append(i)
    for k in (2, 1):
        reale = quota(seq, k)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
            x = seq[:]
            for idx in per.values():
                v = [x[i] for i in idx]
                rnd.shuffle(v)
                for i, c in zip(idx, v):
                    x[i] = c
            nulli.append(quota(x, k))
        m, s = statistics.mean(nulli), statistics.pstdev(nulli)
        out['primi_%d' % k] = OrderedDict([('osservata', reale), ('nullo', m), ('rapporto', reale / m if m else None), ('z', (reale - m) / s if s else None)])
    return out


def main():
    rnd = random.Random(SEME)
    ris = OrderedDict()
    for nome, seq in (('Voynich, ricette (S)', prime_voynich('S')), ('Voynich, erbario (H)', prime_voynich('H')),
                      ('controllo positivo: Alphita', lemmi_alphita())):
        ris[nome] = r = valuta(seq, rnd)
        print('%-30s voci %4d | primi 2: %.3f vs %.3f (x%.2f, z %.1f) | primo: %.3f vs %.3f (x%.2f, z %.1f)' % (
            nome, r['voci'], r['primi_2']['osservata'], r['primi_2']['nullo'], r['primi_2']['rapporto'] or 0, r['primi_2']['z'] or 0,
            r['primi_1']['osservata'], r['primi_1']['nullo'], r['primi_1']['rapporto'] or 0, r['primi_1']['z'] or 0), flush=True)
    z = lambda n: ris[n]['primi_2']['z'] or 0
    valido = z('controllo positivo: Alphita') > 4
    s = ris['Voynich, ricette (S)']['primi_2']
    glossario = z('Voynich, ricette (S)') > 4 and (s['rapporto'] or 0) > 1.5 and z('Voynich, ricette (S)') > z('Voynich, erbario (H)')
    ris['valido'], ris['ordine_da_glossario'] = valido, glossario
    print('controllo valido:', valido, '| ordine da glossario:', glossario)
    with open(os.path.join(RISULTATI, 'e151_glossario.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e151 — I paragrafi delle ricette sono in ordine da glossario?', '', 'Prefissi condivisi fra le prime parole di paragrafi consecutivi (gallow iniziale tolto); nullo: '
           'rimescolamento nella pagina (Alphita: blocchi di %d voci). Preregistrazione: `preregistrazioni/e151.md`.' % BLOCCO, '',
           '| testo | voci | primi 2 segni: osservata / nullo (×, z) | primo segno: osservata / nullo (×, z) |', '|---|---|---|---|']
    for n, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.3f / %.3f (×%.2f, %.1f) | %.3f / %.3f (×%.2f, %.1f) |' % (
                n, r['voci'], r['primi_2']['osservata'], r['primi_2']['nullo'], r['primi_2']['rapporto'] or 0, r['primi_2']['z'] or 0,
                r['primi_1']['osservata'], r['primi_1']['nullo'], r['primi_1']['rapporto'] or 0, r['primi_1']['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Ordine da glossario: **%s**.' % ('sì' if valido else 'no', 'sì' if glossario else 'no')]
    with open(os.path.join(RISULTATI, 'e151_glossario.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
