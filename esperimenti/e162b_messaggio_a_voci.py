# -*- coding: utf-8 -*-
"""Esperimento 162b: come l'e162, ma il testo in chiaro e' a voci (Isidoro, Etymologiae XVII, un paragrafo per pagina).
Tornano le proprieta' di pagina? Il messaggio resta invisibile?

Preregistrazione: preregistrazioni/e162b.md. Scrive risultati/e162b_messaggio_a_voci.json e .md.
"""
import json, os, random, re, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e162.D


def voci():
    with open(os.path.join(lingue.LATIN_LIBRARY, 'isidore', '17.txt'), encoding='utf-8') as f:
        testo = f.read()
    testo = testo[testo.find('[1]'):]
    pezzi = [lingue.normalizza(p).split() for p in re.split(r'\[\d+\]', testo)]
    return [p for p in pezzi if p]


def genera_voci(P, starts, q, L, mod, seme, vv):
    """Come e162.genera, ma la pagina i prende i temi dalla voce i (3 parole consecutive per riga, ciclicamente)."""
    rnd = random.Random(seme)
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for i, (pag, d) in enumerate(P.items()):
        voce, j = vv[i % len(vv)], 0
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        prima_sopra = None
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            tema = []
            for _ in range(e153.K):
                tema.append(voce[j % len(voce)])
                j += 1
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or D(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            for pos in range(1, len(ps)):
                cand = [e153.variante(rnd.choice(tema) if rnd.random() < e162.THETA else rnd.choice(pool), e153.MU, mod, rnd) for _ in range(e152.CANDIDATE)]
                ultimo = D(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, D(x)[0]), 0.05) ** e153.LAM) if ultimo else 1.0
                    if pos == 1 and D(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga, h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = D(riga[0])[0]
            righe.append((pag, ini, riga))
    return righe


def una(args):
    e162.genera = genera_voci
    return e162.una(args)


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    vv = voci()
    piatto = [w for p in vv for w in p]
    codice = generatori.codice_per_rango(piatto, voy, generatori.ModelloParole(voy, D), random.Random(162))
    cod, k = [], 0
    for p in vv:
        cod.append(codice[k:k + len(p)])
        k += len(p)
    print('voci (paragrafi): %d, parole %d; pagine %d' % (len(cod), len(piatto), len(P)), flush=True)
    nome = 'temi da voci, una per pagina (Isidoro XVII codificato)'
    lavori = [(nome, s, cod, P, starts, q, L, voy, soglia_ab, v, vb) for s in e162.SEMI]
    gruppo = []
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for _, r in pool.imap(una, lavori):
            gruppo.append(r)
    chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
    mm = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
    esiti = OrderedDict()
    for prop, f in e61.BANDE.items():
        try:
            esiti[prop] = bool(f(mm, v))
        except (KeyError, TypeError, ZeroDivisionError):
            esiti[prop] = False
    esiti['bordo di riga'] = 0.5 * vb[0] <= mm['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= mm['bordo_fine'] <= 2 * vb[1]
    mm['esiti'] = esiti
    R = mm['R_riga'] if mm.get('R_riga') is not None else 1
    mm['riga_riprodotta'] = (mm['S1'] <= 0.7 and R < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3 and abs(mm['r_righe_consecutive'] - e145.VOY_R1) <= 0.07)
    prec = json.load(open(os.path.join(RISULTATI, 'e162_messaggio_nei_temi.json'), encoding='utf-8'))['medie']
    rif = prec['temi a caso (riferimento e153)']
    misure_t = [k for k in mm if k.startswith(('grezzo', 'ripulito'))]
    visibile = any((mm[k] or 0) > 4 and (mm[k] or 0) - (rif.get(k) or 0) >= 3 for k in misure_t)
    pagina = sum(esiti.values()) >= 9 and mm['riga_riprodotta']
    medie = OrderedDict([(nome, mm), ('temi dal flusso continuo (e162)', prec['temi dal messaggio (latino codificato)']), ('temi a caso (riferimento e153, e162)', rif)])
    esito = OrderedDict([('a_pagina_recuperata', pagina), ('b_messaggio_visibile', visibile)])
    for n, m in medie.items():
        print('%-58s %d/18 | riga %s | %s' % (n, sum(m['esiti'].values()), m['riga_riprodotta'], ' '.join('%s %.1f' % (k, m.get(k) or 0) for k in misure_t)), flush=True)
    print('(a) pagina recuperata: %s | (b) messaggio visibile: %s' % (pagina, visibile))
    with open(os.path.join(RISULTATI, 'e162b_messaggio_a_voci.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'esito': esito, 'voci': len(cod)}, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e162b — Un messaggio nei temi, con una voce per pagina', '', 'Generatore e153 (θ 0,3); temi di riga dal paragrafo di Isidoro XVII assegnato alla pagina, '
           'codificato parola per parola. Medie su tre semi; i confronti vengono dall\'e162. Preregistrazione: `preregistrazioni/e162b.md`.', '',
           '| generatore | pagella | S(1) | A | scelte | r | riga | ' + ' | '.join(misure_t) + ' |', '|---|---|---|---|---|---|---|' + '---|' * len(misure_t)]
    for n, m in medie.items():
        out.append('| %s | %d/18 | %.2f | %.3f | %.1f | %.3f | %s | %s |' % (n, sum(m['esiti'].values()), m['S1'], m['A'], m['scelte_per_riga'], m['r_righe_consecutive'],
                                                                     'sì' if m['riga_riprodotta'] else 'no', ' | '.join('%.1f' % (m.get(k) or 0) for k in misure_t)))
    out += ['', 'Proprietà della pagella: ' + ', '.join('%s %s' % (k, 'sì' if x else 'no') for k, x in esiti.items()) + '.', '',
            '(a) Pagina recuperata: **%s**. (b) Messaggio visibile: **%s**.' % ('sì' if pagina else 'no', 'sì' if visibile else 'no')]
    with open(os.path.join(RISULTATI, 'e162b_messaggio_a_voci.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
