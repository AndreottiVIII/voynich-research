# -*- coding: utf-8 -*-
"""Esperimento 279: il test baconiano dell'e181 (indice di coincidenza dei gruppi di L bit, nullo dentro classe x riga)
sul flusso di bit delle 12 classi di riga dell'e206b, con controlli positivi di Bacone puri e mescolati.

Preregistrazione: preregistrazioni/e279.md. Scrive risultati/e279_bacone_classi.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e181_bacone as e181
import e206_segni_facoltativi as e206

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, INIZIO_LATINO = 279, 20000


def flusso(classi):
    righe = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    freq = Counter(w for r in righe for w in r)
    cl = e206.classi_di(freq)
    ordine = {c: i for i, c in enumerate(classi)}
    occ = []
    for k, r in enumerate(righe):
        for w in r:
            # dentro la parola, le classi nell'ordine fisso dell'elenco dell'e206b; fra le parole, l'ordine di lettura
            for nome, v in sorted(((('%s %s' % c), v) for c, v in cl.get(w, {}).items() if ('%s %s' % c) in ordine), key=lambda x: ordine[x[0]]):
                occ.append((nome, k, v))
    out = occ
    return out


def bacone(n_bit):
    bit = []
    for w in lingue.parole('Latin')[INIZIO_LATINO:]:
        for c in w.lower().replace('j', 'i').replace('v', 'u'):
            if c in e181.ALFABETO:
                i = e181.ALFABETO.index(c)
                bit += [(i >> s) & 1 for s in (4, 3, 2, 1, 0)]
        if len(bit) >= n_bit:
            break
    return bit[:n_bit]


def main():
    rnd = random.Random(SEME)
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    occ = flusso(classi)
    voy = [v for _, _, v in occ]
    msg = bacone(len(voy))
    testi = OrderedDict([('Voynich', voy), ('controllo: Bacone puro (π 1)', msg)])
    for p in (0.7, 0.3):
        testi['controllo: Bacone mescolato (π %.1f)' % p] = [m if rnd.random() < p else v for m, v in zip(msg, voy)]
    ris = OrderedDict([('bit', len(voy)), ('per_classe', dict(Counter(f for f, _, _ in occ))), ('quota_forme_lunghe', sum(voy) / len(voy))])
    for nome, vv in testi.items():
        ris[nome] = OrderedDict(('L%d' % L, e181.prova(occ, vv, L, rnd)) for L in (5, 4, 6, 7))
        print('%-36s ' % nome + ' | '.join('L%d z %.1f' % (L, ris[nome]['L%d' % L]['z'] or 0) for L in (5, 4, 6, 7)), flush=True)
    z = lambda n: ris[n]['L5']['z'] or 0
    valido = z('controllo: Bacone puro (π 1)') > 4
    esito = 'test non valido' if not valido else ('canale baconiano presente' if z('Voynich') > 4 else ('assente' if z('Voynich') < 2 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e279_bacone_classi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e279 — Un messaggio "alla Bacone" nelle 12 scelte di riga dell\'e206b?', '',
          'Indice di coincidenza dei gruppi di L bit consecutivi (massimo sugli sfasamenti), z contro %d rimescolamenti dentro classe × riga. '
          '%d bit, forme lunghe %.1f%%. Preregistrazione: `preregistrazioni/e279.md`.' % (e181.RIMESCOLAMENTI, len(voy), 100 * ris['quota_forme_lunghe']), '',
          '| testo | L 5 (principale) | L 4 | L 6 | L 7 |', '|---|---|---|---|---|']
    for nome in testi:
        md.append('| %s | %s |' % (nome, ' | '.join('%.4f (z %.1f)' % (ris[nome]['L%d' % L]['ioc'], ris[nome]['L%d' % L]['z'] or 0) for L in (5, 4, 6, 7))))
    md += ['', 'Bit per classe: %s.' % ', '.join('%s %d' % kv for kv in ris['per_classe'].items()), '',
           'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e279_bacone_classi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
