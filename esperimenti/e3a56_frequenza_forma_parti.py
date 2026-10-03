# -*- coding: utf-8 -*-
"""Esperimento e3a56: e3a55 (la frequenza segue la forma) con le trascrizioni IT e GC, per lingua A e B e per le mani di
Davis 1, 2, 3.

Preregistrazione: preregistrazioni/e3a56.md. Scrive risultati/e3a56_frequenza_forma_parti.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
MAX_E3A55 = 0.278


def pagine(quale, segni, filtro=lambda r: True):
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi(quale)):
        if not filtro(r):
            continue
        ws = [segni(w) for w in r.parole if trascrizione.pulita(w)]
        ws = [w for w in ws if w]
        if ws:
            per.setdefault(r.pagina, []).append(ws)
    return list(per.values())


def mediana_sub(pp, n_par, rnd):
    sub = []
    for _ in range(5):
        ordine = rnd.sample(pp, len(pp))
        prese = []
        for p in ordine:
            if len(prese) >= n_par:
                break
            prese += [w for r in p for w in r]
        v = e3a55.rho(prese)
        if v is not None:
            sub.append(v)
    return sub, (statistics.median(sub) if sub else None)


def esito(m, soglia, med):
    if m is None:
        return 'n.d.'
    return 'regge' if m > soglia else ('non regge' if m < med else 'incerto')


def main():
    rnd = random.Random(3156)
    sens5 = []
    for k, t in e381.testi().items():
        v = e3a55.rho(e3a55.prime(t, 5000))
        if v is not None:
            sens5.append(v)
    s5 = (max(sens5), statistics.median(sens5))
    print('testi sensati a 5.000 parole: massimo %.3f, mediana %.3f' % s5, flush=True)
    ris = OrderedDict()
    for nome, quale, segni in (('IT (Takahashi)', 'IT', lambda w: tuple(D(w))), ('GC (Glen Claston, v101)', 'GC', lambda w: tuple(w))):
        pp = pagine(quale, segni)
        sub, m = mediana_sub(pp, 10000, rnd)
        ris[nome] = OrderedDict([('parole', sum(len(r) for p in pp for r in p)), ('rho_sub', sub), ('mediana', m), ('dimensione', 10000),
                                 ('soglia', MAX_E3A55), ('esito', esito(m, MAX_E3A55, 0.110))])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    parti = OrderedDict([('lingua A', lambda r: r.lingua == 'A'), ('lingua B', lambda r: r.lingua == 'B'),
                         ('mano 1', lambda r: r.mano == '1'), ('mano 2', lambda r: r.mano == '2'), ('mano 3', lambda r: r.mano == '3')])
    for nome, f in parti.items():
        pp = pagine('ZL', lambda w: tuple(D(w)), f)
        sub, m = mediana_sub(pp, 5000, rnd)
        ris[nome] = OrderedDict([('parole', sum(len(r) for p in pp for r in p)), ('rho_sub', sub), ('mediana', m), ('dimensione', 5000),
                                 ('soglia', s5[0]), ('esito', esito(m, s5[0], s5[1]))])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    out = OrderedDict([('parti', ris), ('testi_sensati_5000', OrderedDict([('massimo', s5[0]), ('mediana', s5[1])]))])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a56_frequenza_forma_parti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a56 — La frequenza segue la forma anche con altre trascrizioni, in lingua A e B e per ogni scriba?', '',
          'Preregistrazione: `preregistrazioni/e3a56.md`. Testi sensati: a 10.000 parole massimo 0,278, mediana 0,110 (e3a55); a 5.000 parole massimo %.3f, mediana %.3f.' % s5, '',
          '| parte | parole | dimensione | ρ dei sottoinsiemi | mediana | soglia | esito |', '|---|---|---|---|---|---|---|']
    md += ['| %s | %d | %d | %s | %s | %.3f | %s |' % (k, x['parole'], x['dimensione'], ', '.join('%.3f' % v for v in x['rho_sub']),
                                                   '%.3f' % x['mediana'] if x['mediana'] is not None else 'n.d.', x['soglia'], x['esito']) for k, x in ris.items()]
    open(os.path.join(RISULTATI, 'e3a56_frequenza_forma_parti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
