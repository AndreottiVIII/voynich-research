# -*- coding: utf-8 -*-
"""Esperimento 160: il testo ripulito dall'involucro di riga (segno d'inizio, scelte di grafia, varianti) mostra la
struttura di un codice a parole? Con controllo: latino cifrato parola per parola, con e senza involucro.

Preregistrazione: preregistrazioni/e160.md. Scrive risultati/e160_testo_ripulito.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e114_accordo_terminazioni as e114
import e115_ordine_parole as e115
import e126_trasposizione_riga as e126
import e145_abitudini as e145
import e156_lingue_ab as e156

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI_T4, RP = 160, 100, 29
D = misure.divisore(misure.GLIFI_EVA)


def ripulisci(pagine):
    """pagine: liste di (inizio paragrafo, parole)."""
    out = []
    for p in pagine:
        q = []
        for ini, ps in p:
            ps = list(ps)
            if ps and not ini and trascrizione.pulita(ps[0]):
                u = D(ps[0])
                if len(u) >= 3 and u[0] in ('y', 'd', 's'):
                    ps[0] = ''.join(u[1:])
            q.append((ini, [e156.n2(w) if trascrizione.pulita(w) else w for w in ps]))
        out.append(q)
    return out


def t4(righe, rnd):
    def mi(rr):
        return misure.informazione_mutua([(a, b) for r in rr for a, b in zip(r, r[1:])])
    rr = [[w for w in r if trascrizione.pulita(w)] for r in righe]
    rr = [r for r in rr if len(r) >= 2]
    reale = mi(rr)
    nulli = []
    for _ in range(RIMESCOLAMENTI_T4):
        mes = []
        for r in rr:
            r = r[:]
            rnd.shuffle(r)
            mes.append(r)
        nulli.append(mi(mes))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('eccesso', reale - m), ('z', (reale - m) / s if s else None)])


def una(args):
    nome, pagine = args
    rnd = random.Random(SEME)
    righe = [ps for p in pagine for _, ps in p]
    out = OrderedDict()
    _, r1 = e115.una(('x', righe))
    out['T1'] = OrderedDict([('z', r1['nullo_riga']['z'])])
    _, r2 = e114.una(('x', righe, 'eva'))
    out['T2'] = OrderedDict([('z', r2['k2']['z'])])
    _, r3 = e126.una(('x', [[ps for _, ps in p] for p in pagine], 'eva'))
    out['T3'] = OrderedDict([('z', r3['accordo']['z'])])
    out['T4'] = t4(righe, rnd)
    return nome, out


def pagine_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            per.setdefault(r.pagina, []).append((bool(r.inizio_par), list(r.parole)))
    return list(per.values())


def controllo():
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rnd = random.Random(SEME)
    lat = lingue.parole('Latin')[:35000]
    codice = generatori.codice_per_rango(lat, voy, generatori.ModelloParole(voy, D), rnd)
    righe = [codice[i:i + 9] for i in range(0, len(codice), 9)]
    tetto = [[(k % 8 == 0, r) for k, r in enumerate(righe[i:i + RP])] for i in range(0, len(righe), RP)]
    q = e145.quote()
    h = {f: 0.0 for f in e145.SCELTE}
    con = []
    for p in tetto:
        for f in e145.SCELTE:
            h[f] = 0.3 * h[f] + rnd.gauss(0, 0.8)
        nuova, sopra = [], None
        for ini, ps in p:
            for f in e145.SCELTE:
                h[f] = 0.6 * h[f] + rnd.gauss(0, 0.8)
            ps = list(ps)
            if not ini and ps and rnd.random() < 0.45:
                g = rnd.choice([x for x in ('y', 'd', 's') if x != sopra])
                ps[0] = g + ps[0]
                sopra = g
            else:
                sopra = None
            nuova.append((ini, e145.riscrivi(ps, h, q, rnd)))
        con.append(nuova)
    return tetto, con


def main():
    voy = pagine_voynich()
    tetto, con = controllo()
    testi = OrderedDict([('Voynich, grezzo', voy), ('Voynich, ripulito', ripulisci(voy)), ('controllo: latino cifrato, senza involucro (tetto)', tetto),
                         ('controllo: con involucro (grezzo)', con), ('controllo: ripulito', ripulisci(con))])
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, list(testi.items())):
            ris[nome] = r
            print('%-52s %s' % (nome, ' | '.join('%s z %.1f' % (k, x['z'] or 0) for k, x in r.items())), flush=True)
    z = lambda n, t: ris[n][t]['z'] or 0
    valido = z('controllo: ripulito', 'T4') >= 0.5 * z('controllo: latino cifrato, senza involucro (tetto)', 'T4') and z('controllo: ripulito', 'T4') > z('controllo: con involucro (grezzo)', 'T4')
    vr, vg = 'Voynich, ripulito', 'Voynich, grezzo'
    riemersa = z(vr, 'T4') > 4 and any(z(vr, t) > 3 and z(vr, t) - z(vg, t) >= 3 for t in ('T1', 'T2'))
    ris['valido'], ris['struttura_riemersa'] = valido, riemersa
    print('controllo valido:', valido, '| struttura riemersa nel Voynich:', riemersa)
    with open(os.path.join(RISULTATI, 'e160_testo_ripulito.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e160 — Sotto l\'involucro: il testo ripulito ha la struttura di un codice a parole?', '', 'T1 ordine delle parole frequenti (e115); T2 accordo a distanza 2 (e114); '
           'T3 accordo nella composizione della riga (e126); T4 informazione fra parole adiacenti. z contro i rimescolamenti. Preregistrazione: `preregistrazioni/e160.md`.', '',
           '| testo | T1 | T2 | T3 | T4 |', '|---|---|---|---|---|']
    for n, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %s |' % (n, ' | '.join('%.1f' % (r[t]['z'] or 0) for t in ('T1', 'T2', 'T3', 'T4'))))
    out += ['', 'Controllo valido: **%s**. Struttura riemersa nel Voynich: **%s**.' % ('sì' if valido else 'no', 'sì' if riemersa else 'no')]
    with open(os.path.join(RISULTATI, 'e160_testo_ripulito.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
