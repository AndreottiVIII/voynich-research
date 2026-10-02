# -*- coding: utf-8 -*-
"""Esperimento 155: le parole di una riga si raccolgono in poche famiglie di varianti (un tema) piu' di quanto spieghi il
vocabolario della pagina? Copertura delle k famiglie migliori contro rimescolamenti fra righe della pagina.

Preregistrazione: preregistrazioni/e155.md. Scrive risultati/e155_tema_di_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from functools import lru_cache
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, SOGLIA, MIN_PAROLE = 155, 200, 0.25, 5
D = misure.divisore(misure.GLIFI_EVA)


@lru_cache(maxsize=2000000)
def vicine(a, b):
    return a == b or misure._dist_norm(a, b) <= SOGLIA


def copertura(riga, k):
    resto = list(range(len(riga)))
    coperte = 0
    for _ in range(k):
        if not resto:
            break
        migliore = max(set(riga[i] for i in resto), key=lambda c: sum(vicine(c, riga[i]) for i in resto))
        prese = [i for i in resto if vicine(migliore, riga[i])]
        coperte += len(prese)
        resto = [i for i in resto if i not in prese]
    return coperte / len(riga)


def stat(pagine):
    out = {}
    for k in (1, 2):
        out[k] = statistics.mean(copertura(r, k) for p in pagine for r in p)
    return out


def una(args):
    nome, pagine = args
    pagine = [[r for r in p if len(r) >= MIN_PAROLE - 1] for p in pagine]
    pagine = [p for p in pagine if len(p) >= 2]
    rnd = random.Random(SEME)
    reale = stat(pagine)
    nulli = {1: [], 2: []}
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for p in pagine:
            tutte = [w for r in p for w in r]
            rnd.shuffle(tutte)
            it = iter(tutte)
            mes.append([[next(it) for _ in r] for r in p])
        s = stat(mes)
        for k in (1, 2):
            nulli[k].append(s[k])
    out = OrderedDict([('righe', sum(map(len, pagine)))])
    for k in (1, 2):
        m, sd = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out['C%d' % k] = OrderedDict([('osservata', reale[k]), ('nullo', m), ('rapporto', reale[k] / m if m else None), ('z', (reale[k] - m) / sd if sd else None)])
    return nome, out


def pagine_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole[1:] if trascrizione.pulita(w)]
        if ps:
            per.setdefault(r.pagina, []).append(ps)
    return list(per.values())


def pagine_e152():
    import e131_procedimento_riga as e131
    import e145_abitudini as e145
    import e152_righe_in_ordine as e152
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rr = e152.genera(e145.pagine(), e131.inizi(), e145.quote(), e152.lift(), 2, 0.5, 1.0, generatori.Modifiche(voy, D), 1)
    per = OrderedDict()
    for pag, _, ps in rr:
        per.setdefault(pag, []).append([w for w in ps[1:] if trascrizione.pulita(w)])
    return list(per.values())


def pagine_righe(righe, n=29):
    return [righe[i:i + n] for i in range(0, len(righe), n)]


def main():
    ts = [ps[1:] for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))]
    lat = lingue.parole('Latin')[:35000]
    testi = OrderedDict([('Voynich ZL', pagine_voynich()), ('controllo positivo: generatore e152', pagine_e152()),
                         ('Timm e Schinner, seme 19', pagine_righe(ts)), ('Bibbia latina', pagine_righe([lat[i + 1:i + 9] for i in range(0, len(lat), 9)]))])
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, list(testi.items())):
            ris[nome] = r
            print('%-38s righe %5d | C1 %.3f vs %.3f (x%.2f, z %.1f) | C2 %.3f vs %.3f (x%.2f, z %.1f)' % (
                nome, r['righe'], r['C1']['osservata'], r['C1']['nullo'], r['C1']['rapporto'], r['C1']['z'] or 0,
                r['C2']['osservata'], r['C2']['nullo'], r['C2']['rapporto'], r['C2']['z'] or 0), flush=True)
    z = lambda n, k: ris[n]['C%d' % k]['z'] or 0
    valido = z('controllo positivo: generatore e152', 1) > 10
    v = ris['Voynich ZL']
    tema = any((v['C%d' % k]['z'] or 0) > 4 and (v['C%d' % k]['rapporto'] or 0) > 1.1 for k in (1, 2))
    ris['valido'], ris['righe_a_tema'] = valido, tema
    print('controllo valido:', valido, '| righe a tema:', tema)
    with open(os.path.join(RISULTATI, 'e155_tema_di_riga.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e155 — Ogni riga ha un "tema"?', '', 'Copertura delle k famiglie di varianti migliori (distanza ≤ %.2f) nella riga, senza la prima parola; nullo: %d rimescolamenti '
           'fra righe della pagina. Preregistrazione: `preregistrazioni/e155.md`.' % (SOGLIA, RIMESCOLAMENTI), '',
           '| testo | righe | C1 osservata / nullo (×, z) | C2 osservata / nullo (×, z) |', '|---|---|---|---|']
    for n, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.3f / %.3f (×%.2f, %.1f) | %.3f / %.3f (×%.2f, %.1f) |' % (
                n, r['righe'], r['C1']['osservata'], r['C1']['nullo'], r['C1']['rapporto'], r['C1']['z'] or 0,
                r['C2']['osservata'], r['C2']['nullo'], r['C2']['rapporto'], r['C2']['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Righe a tema: **%s**.' % ('sì' if valido else 'no', 'sì' if tema else 'no')]
    with open(os.path.join(RISULTATI, 'e155_tema_di_riga.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
