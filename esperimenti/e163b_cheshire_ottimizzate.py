# -*- coding: utf-8 -*-
"""Esperimento 163b: la chiave di Cheshire contro chiavi della stessa forma ottimizzate sul lessico (addestramento sui
fogli dispari, verifica sui pari). Controllo: italiano scritto con l'inverso della chiave.

Preregistrazione: preregistrazioni/e163b.md. Scrive risultati/e163b_cheshire_ottimizzate.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e163_cheshire as e163

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PARTENZE, SCAMBI = 1631, 20, 3000


def m1(tipi, chiave, lex, minimo=0):
    num = den = 0
    for u, n in tipi.items():
        s = ''.join(chiave[x] for x in u)
        if len(s) >= minimo:
            den += n
            if s in lex:
                num += n
    return num / den if den else 0.0


def ottimizza(tipi, lex, rnd):
    k = e163.casuale(rnd)
    voc = [u for u in e163.CHIAVE if u in e163.VOCALICHE]
    con = [u for u in e163.CHIAVE if u not in e163.VOCALICHE]
    attuale = m1(tipi, k, lex)
    for _ in range(SCAMBI):
        g = voc if rnd.random() < len(voc) / len(e163.CHIAVE) else con
        a, b = rnd.sample(g, 2)
        k[a], k[b] = k[b], k[a]
        nuovo = m1(tipi, k, lex)
        if nuovo >= attuale:
            attuale = nuovo
        else:
            k[a], k[b] = k[b], k[a]
    return k, attuale


def prova(nome, addestra, verifica, lex, rnd):
    ottime = []
    for i in range(PARTENZE):
        k, a = ottimizza(addestra, lex, rnd)
        ottime.append(OrderedDict([('addestramento', a), ('verifica', m1(verifica, k, lex)), ('verifica_4', m1(verifica, k, lex, 4)),
                                   ('chiave', ' '.join('%s>%s' % (u, k[u]) for u in e163.CHIAVE))]))
        print('  %s partenza %2d: addestramento %.3f verifica %.3f (>=4: %.3f)' % (nome, i + 1, a, ottime[-1]['verifica'], ottime[-1]['verifica_4']), flush=True)
    v = [o['verifica'] for o in ottime]
    v4 = [o['verifica_4'] for o in ottime]
    r = OrderedDict([('cheshire_addestramento', m1(addestra, e163.CHIAVE, lex)), ('cheshire_verifica', m1(verifica, e163.CHIAVE, lex)),
                     ('cheshire_verifica_4', m1(verifica, e163.CHIAVE, lex, 4)),
                     ('ottimizzate_verifica_mediana', statistics.median(v)), ('ottimizzate_verifica_max', max(v)),
                     ('ottimizzate_verifica_4_mediana', statistics.median(v4)), ('ottimizzate_verifica_4_max', max(v4)), ('ottimizzate', ottime)])
    print('%-24s Cheshire verifica %.3f (>=4 %.3f) | ottimizzate mediana %.3f max %.3f (>=4 mediana %.3f max %.3f)' % (
        nome, r['cheshire_verifica'], r['cheshire_verifica_4'], r['ottimizzate_verifica_mediana'], r['ottimizzate_verifica_max'],
        r['ottimizzate_verifica_4_mediana'], r['ottimizzate_verifica_4_max']), flush=True)
    return r


def main():
    rnd = random.Random(SEME)
    zl = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    dispari, pari = Counter(), Counter()
    for r in zl:
        if not e163.fuori_campione(r.pagina):
            continue
        n = int(re.match(r'f(\d+)', r.pagina).group(1))
        for w in r.parole:
            u = e163.unita(w) if trascrizione.pulita(w) else None
            if u:
                (dispari if n % 2 else pari)[u] += 1
    ita = lingue.parole('Italian', max_caratteri=e163.CONTROLLO_CARATTERI)
    cod = []
    for w in ita:
        e = ''.join(e163.INVERSA.get(c, '') for c in e163.piatta(w))
        u = e163.unita(e) if e else None
        if u:
            cod.append(u)
    meta = len(cod) // 2
    ris = OrderedDict()
    ris['controllo italiano'] = prova('controllo italiano', Counter(cod[:meta]), Counter(cod[meta:]), e163.lessico(escludi_italiano=e163.CONTROLLO_CARATTERI), rnd)
    ris['Voynich'] = prova('Voynich', dispari, pari, e163.lessico(), rnd)
    c, v = ris['controllo italiano'], ris['Voynich']
    valido = c['ottimizzate_verifica_max'] >= 0.8 * c['cheshire_verifica']
    if v['ottimizzate_verifica_mediana'] >= v['cheshire_verifica']:
        esito = 'vantaggio spiegato dall\'adattamento'
    elif v['cheshire_verifica'] > v['ottimizzate_verifica_max']:
        esito = 'Cheshire oltre l\'adattamento'
    else:
        esito = 'intermedio'
    ris['controllo_valido'], ris['esito'] = valido, esito
    print('controllo valido:', valido, '| esito:', esito)
    with open(os.path.join(RISULTATI, 'e163b_cheshire_ottimizzate.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e163b — La chiave di Cheshire contro chiavi ottimizzate sul lessico', '',
           '%d chiavi della stessa forma ottimizzate (%d scambi ciascuna) su metà del testo, misurate sull\'altra metà. '
           'Preregistrazione: `preregistrazioni/e163b.md`.' % (PARTENZE, SCAMBI), '',
           '| testo | M1 Cheshire (verifica) | M1 ottimizzate (mediana / max) | M1 ≥ 4 Cheshire | M1 ≥ 4 ottimizzate (mediana / max) |', '|---|---|---|---|---|']
    for n in ('controllo italiano', 'Voynich'):
        r = ris[n]
        out.append('| %s | %.3f | %.3f / %.3f | %.3f | %.3f / %.3f |' % (n, r['cheshire_verifica'], r['ottimizzate_verifica_mediana'], r['ottimizzate_verifica_max'],
                                                                  r['cheshire_verifica_4'], r['ottimizzate_verifica_4_mediana'], r['ottimizzate_verifica_4_max']))
    out += ['', 'Nel controllo italiano "Cheshire" è la chiave vera.', '', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e163b_cheshire_ottimizzate.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
