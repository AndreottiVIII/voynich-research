# -*- coding: utf-8 -*-
"""Esperimento 359: le forme nuove (parole uniche non varianti di parole frequenti) si scompongono in un inizio e una fine
presenti in altre parole del proprio bifoglio piu' che in un altro bifoglio della stessa sezione?

Preregistrazione: preregistrazioni/e359.md. Scrive risultati/e359_ricombinazione.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e308_libro_fisico as e308
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
ESTR = 200


class Pezzi:
    """Inizi e fini (di almeno 2 segni) dei tipi di un insieme, con i conteggi per poter togliere una parola."""

    def __init__(self, tipi):
        self.ini, self.fin = Counter(), Counter()
        for w in tipi:
            u = tuple(D(w))
            for k in range(2, len(u) + 1):
                self.ini[u[:k]] += 1
                self.fin[u[-k:]] += 1
        self.tipi = set(tipi)

    def composta(self, w):
        u = tuple(D(w))
        togli_i, togli_f = Counter(), Counter()
        if w in self.tipi:
            for k in range(2, len(u) + 1):
                togli_i[u[:k]] += 1
                togli_f[u[-k:]] += 1
        for k in range(2, len(u) - 1):
            a, b = u[:k], u[k:]
            if self.ini[a] - togli_i[a] > 0 and self.fin[b] - togli_f[b] > 0:
                return True
        return False


def main():
    rnd = random.Random(359)
    testa = e308.intestazioni()
    tok, sez = [], {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole and testa.get(r.pagina, {}).get('Q'):
            sez.setdefault(r.pagina, r.sezione or '?')
            tok += [(r.pagina, w) for w in r.parole if trascrizione.pulita(w)]
    freq = Counter(w for _, w in tok)
    sim = e350.simili_globali(set(freq))
    bif_tok = defaultdict(list)
    for p, w in tok:
        bif_tok[(testa[p]['Q'], testa[p]['B'])].append(w)
    sez_b = {b: Counter(sez[p] for p, _ in tok if (testa[p]['Q'], testa[p]['B']) == b).most_common(1)[0][0] for b in bif_tok}
    pezzi = {b: Pezzi(set(ws)) for b, ws in bif_tok.items()}
    per_sez = defaultdict(list)
    for b in bif_tok:
        per_sez[sez_b[b]].append(b)

    def simili_per_dim(b):
        n = len(bif_tok[b])
        c = [x for x in per_sez[sez_b[b]] if x != b and 0.5 * n <= len(bif_tok[x]) <= 2 * n]
        return c or [x for x in per_sez[sez_b[b]] if x != b]
    gruppi = defaultdict(list)    # nome -> [(parola, bifoglio)]
    visti = set()
    for p, w in tok:
        b = (testa[p]['Q'], testa[p]['B'])
        if len(D(w)) < 4:
            continue
        if freq[w] == 1:
            errore = any(freq[v] >= 20 for v in sim[w] if v != w)
            gruppi['errori' if errore else 'forme nuove'].append((w, b))
        elif freq[w] >= 5 and w not in visti:
            visti.add(w)
            gruppi['parole comuni'].append((w, b))
    out = OrderedDict()
    for nome in ('forme nuove', 'errori', 'parole comuni'):
        voci = [(w, b) for w, b in gruppi[nome] if simili_per_dim(b)]
        proprio = statistics.mean(pezzi[b].composta(w) for w, b in voci)
        altri = []
        for _ in range(ESTR):
            altri.append(statistics.mean(pezzi[rnd.choice(simili_per_dim(b))].composta(w) for w, b in voci))
        m, sd = statistics.mean(altri), statistics.pstdev(altri)
        out[nome] = OrderedDict([('parole', len(voci)), ('composte_nel_proprio_bifoglio', proprio), ('in_un_altro', m), ('eccesso', proprio - m), ('z', (proprio - m) / sd if sd else 0.0)])
        print(nome, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out[nome].items()}, flush=True)
    fn, pc = out['forme nuove'], out['parole comuni']
    esito = 'le forme nuove nascono dalla sessione' if (fn['z'] > 3 and fn['eccesso'] > pc['eccesso']) else ('no' if fn['z'] < 2 else 'incerto')
    json.dump(OrderedDict([('gruppi', out), ('esito', esito)]), open(os.path.join(RISULTATI, 'e359_ricombinazione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e359 — Le forme nuove sono fatte di pezzi della stessa sessione?', '', 'Preregistrazione: `preregistrazioni/e359.md`.', '',
          '| parole | numero | composte nel proprio bifoglio | in un altro bifoglio della sezione | eccesso | z |', '|---|---|---|---|---|---|']
    for k, v in out.items():
        md.append('| %s | %d | %.3f | %.3f | %+.4f | %.1f |' % (k, v['parole'], v['composte_nel_proprio_bifoglio'], v['in_un_altro'], v['eccesso'], v['z']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e359_ricombinazione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
