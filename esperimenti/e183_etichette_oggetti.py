# -*- coding: utf-8 -*-
"""Esperimento 183: la forma delle etichette dipende dal tipo di oggetto (codici di locus IVTFF) dentro la sezione e
la pagina?

Preregistrazione: preregistrazioni/e183.md. Scrive risultati/e183_etichette_oggetti.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 183, 2000
D = misure.divisore(misure.GLIFI_EVA)
CONTRASTI = OrderedDict([('farmacia', ('P', 'Lf', 'Lc')), ('biologica', ('B', 'Ln', 'Lt')), ('astronomica', ('A', 'Ls', 'L0'))])


def caratteristiche(w):
    u = D(w)
    n = len(u)
    return (u[0], u[-1], '1-3' if n <= 3 else '4-5' if n <= 5 else '6+', u[0] == 'o')


def etichette():
    out = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo and r.tipo[0] == 'L':
            ps = [w for w in r.parole if trascrizione.pulita(w)]
            if ps:
                out.append((r.pagina, r.sezione, r.tipo, ps[0]))
    return out


def im(coppie):
    n = len(coppie)
    a, b, ab = Counter(x for x, _ in coppie), Counter(y for _, y in coppie), Counter(coppie)
    return sum(c / n * math.log2(c * n / (a[x] * b[y])) for (x, y), c in ab.items())


def statistica(dati):
    """dati: {contrasto: [(pagina, tipo, parola)]}"""
    tot = 0.0
    for v in dati.values():
        for j in range(4):
            tot += im([(caratteristiche(w)[j], t) for _, t, w in v])
    return tot


def rimescola(dati, rnd):
    out = {}
    for c, v in dati.items():
        per = defaultdict(list)
        for i, (p, _, _) in enumerate(v):
            per[p].append(i)
        tipi = [t for _, t, _ in v]
        for idx in per.values():
            x = [tipi[i] for i in idx]
            rnd.shuffle(x)
            for i, y in zip(idx, x):
                tipi[i] = y
        out[c] = [(p, t, w) for (p, _, w), t in zip(v, tipi)]
    return out


def prova(dati, rnd):
    vero = statistica(dati)
    nulli = [statistica(rimescola(dati, rnd)) for _ in range(RIMESCOLAMENTI)]
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    p = (1 + sum(n >= vero for n in nulli)) / (1 + RIMESCOLAMENTI)
    return OrderedDict([('im', vero), ('nullo', m), ('z', (vero - m) / s if s else None), ('p', p)])


def identiche(dati, rnd):
    def quota(dd):
        stesso = tot = 0
        for v in dd.values():
            per = defaultdict(list)
            for _, t, w in v:
                per[w].append(t)
            for tt in per.values():
                for i in range(len(tt)):
                    for j in range(i + 1, len(tt)):
                        tot += 1
                        stesso += tt[i] == tt[j]
        return stesso / tot if tot else None, tot
    vero, n = quota(dati)
    nulli = [quota(rimescola(dati, rnd))[0] for _ in range(500)]
    return OrderedDict([('coppie_identiche', n), ('quota_stesso_tipo', vero), ('attesa', statistics.mean(x for x in nulli if x is not None))])


def main():
    rnd = random.Random(SEME)
    tutte = etichette()
    dati = OrderedDict()
    for c, (sez, t1, t2) in CONTRASTI.items():
        dati[c] = [(p, t, w) for p, s, t, w in tutte if s == sez and t in (t1, t2)]
    lz = [w for _, s, t, w in tutte if t == 'Lz']
    potenza = OrderedDict()
    for c, (sez, t1, t2) in CONTRASTI.items():
        potenza[c] = [(p, t, rnd.choice(lz) if t == t2 else w) for p, t, w in dati[c]]
    ris = OrderedDict([('numeri', {c: dict(Counter(t for _, t, _ in v)) for c, v in dati.items()})])
    ris['Voynich'] = prova(dati, rnd)
    ris['controllo di potenza'] = prova(potenza, rnd)
    ris['per_contrasto'] = OrderedDict((c, prova({c: v}, rnd)) for c, v in dati.items())
    ris['identiche'] = identiche(dati, rnd)
    valido = (ris['controllo di potenza']['z'] or 0) > 4
    v = ris['Voynich']
    esito = 'test non valido' if not valido else ('le etichette dipendono dall\'oggetto' if (v['z'] or 0) > 3 and v['p'] < 0.01 else ('nessuna dipendenza' if v['p'] > 0.05 else 'incerto'))
    ris['valido'], ris['esito'] = valido, esito
    print('numeri %s' % ris['numeri'])
    print('Voynich IM %.3f (nullo %.3f, z %.1f, p %.4f) | potenza z %.1f | per contrasto %s | identiche %s | %s' % (
        v['im'], v['nullo'], v['z'] or 0, v['p'], ris['controllo di potenza']['z'] or 0,
        {c: round(x['z'] or 0, 1) for c, x in ris['per_contrasto'].items()}, dict(ris['identiche']), esito), flush=True)
    with open(os.path.join(RISULTATI, 'e183_etichette_oggetti.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e183 — Le etichette dipendono da che cosa etichettano?', '',
           'Informazione mutua fra forma dell\'etichetta (primo e ultimo segno, lunghezza, o-) e tipo di oggetto, dentro la sezione; nullo: rimescolamento '
           'dei tipi dentro la pagina. Preregistrazione: `preregistrazioni/e183.md`.', '',
           '| | IM | nullo | z | p |', '|---|---|---|---|---|',
           '| Voynich | %.3f | %.3f | %.1f | %.4f |' % (v['im'], v['nullo'], v['z'] or 0, v['p']),
           '| controllo di potenza | %.3f | %.3f | %.1f | %.4f |' % tuple(ris['controllo di potenza'][k] or 0 for k in ('im', 'nullo', 'z', 'p'))]
    for c, x in ris['per_contrasto'].items():
        out.append('| %s (%s) | %.3f | %.3f | %.1f | %.4f |' % (c, ', '.join('%s %d' % kv for kv in ris['numeri'][c].items()), x['im'], x['nullo'], x['z'] or 0, x['p']))
    i = ris['identiche']
    out += ['', 'Etichette identiche: %d coppie, stesso tipo %.2f contro %.2f atteso.' % (i['coppie_identiche'], i['quota_stesso_tipo'] or 0, i['attesa']), '',
            'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e183_etichette_oggetti.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
