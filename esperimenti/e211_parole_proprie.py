# -*- coding: utf-8 -*-
"""Esperimento 211: raggruppamento delle parole rare (frequenza 2-5) nelle unita' (pagine d'erbario, voci di erbari
latini) rispetto alla ridistribuzione casuale.

Preregistrazione: preregistrazioni/e211.md. Scrive risultati/e211_parole_proprie.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, trascrizione
import e99_macer as e99
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
import e162b_messaggio_a_voci as e162b
import e192_generatore_misto as e192

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIDISTRIBUZIONI, MIN_PAROLE = 211, 200, 60


def confinate(unita):
    freq = Counter(w for u in unita for w in u)
    dove = defaultdict(set)
    for i, u in enumerate(unita):
        for w in u:
            dove[w].add(i)
    rare = [w for w, c in freq.items() if 2 <= c <= 5]
    return sum(len(dove[w]) == 1 for w in rare) / len(rare) if rare else None, len(rare)


def prova(unita, rnd):
    vero, n = confinate(unita)
    tutte = [w for u in unita for w in u]
    lun = [len(u) for u in unita]
    nulli = []
    for _ in range(RIDISTRIBUZIONI):
        rnd.shuffle(tutte)
        mes, i = [], 0
        for L in lun:
            mes.append(tutte[i:i + L])
            i += L
        nulli.append(confinate(mes)[0])
    m = statistics.mean(nulli)
    return OrderedDict([('unita', len(unita)), ('parole', len(tutte)), ('rare', n), ('C', vero), ('atteso', m), ('R', vero / m if m else None)])


def generatore_erbario(pagine_h):
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    rr = e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), 1, None)
    per = defaultdict(list)
    for pag, _, ps in rr:
        if pag in pagine_h:
            per[pag] += [w for w in ps if trascrizione.pulita(w)]
    return [per[p] for p in pagine_h if per[p]]


def main():
    rnd = random.Random(SEME)
    per = defaultdict(list)
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.sezione == 'H':
            per[r.pagina] += [w for w in r.parole if trascrizione.pulita(w)]
    pagine_h = [p for p, v in per.items() if len(v) >= MIN_PAROLE]
    testi = OrderedDict([('Voynich, erbario', [per[p] for p in pagine_h]),
                         ('Macer floridus, capitoli', [[w for ps in c for w in ps] for c in e99.capitoli()]),
                         ('Isidoro XVII, paragrafi', e162b.voci()),
                         ('generatore e192 (ν 0,4), erbario', generatore_erbario(set(pagine_h)))])
    ris = OrderedDict()
    for n, u in testi.items():
        ris[n] = prova(u, rnd)
        r = ris[n]
        print('%-34s unità %d parole %d rare %d | C %.4f atteso %.4f R %.2f' % (n, r['unita'], r['parole'], r['rare'], r['C'], r['atteso'], r['R'] or 0), flush=True)
    v = ris['Voynich, erbario']['R']
    lat = [ris['Macer floridus, capitoli']['R'], ris['Isidoro XVII, paragrafi']['R']]
    esito = ('pagine senza parole proprie' if v <= 1.5 and all(x >= 3 for x in lat) else ('parole proprie presenti' if v >= 3 else 'intermedio'))
    ris['esito'] = esito
    print(esito)
    with open(os.path.join(RISULTATI, 'e211_parole_proprie.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e211 — Le pagine dell\'erbario hanno parole proprie?', '', 'C = quota di parole rare (frequenza 2–5) confinate in una sola unità; R = C / atteso dalla ridistribuzione casuale. '
           'Preregistrazione: `preregistrazioni/e211.md`.', '', '| testo | unità | parole | rare | C | atteso | R |', '|---|---|---|---|---|---|---|']
    for n in testi:
        r = ris[n]
        out.append('| %s | %d | %d | %d | %.4f | %.4f | %.2f |' % (n, r['unita'], r['parole'], r['rare'], r['C'], r['atteso'], r['R'] or 0))
    out += ['', 'Esito: **%s**.' % esito]
    with open(os.path.join(RISULTATI, 'e211_parole_proprie.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
