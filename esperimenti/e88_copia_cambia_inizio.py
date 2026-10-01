# -*- coding: utf-8 -*-
"""Esperimento 88: la prima parola di una riga e' una copia della prima parola sopra con l'inizio cambiato?

Preregistrazione: preregistrazioni/e88.md. Scrive risultati/e88_copia_cambia_inizio.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI = 88, 500
D = e71.D


def colonna(righe, pos):
    """righe: (pagina, paragrafo, inizio, parole) -> per pagina, lista di (paragrafo, inizio, parola o None)."""
    per = OrderedDict()
    for pag, par, ini, ps in righe:
        w = ps[pos] if len(ps) > pos and trascrizione.pulita(ps[pos]) else None
        per.setdefault(pag, []).append((par, ini, w))
    return per


def coppie(per):
    out = []
    for rr in per.values():
        for (p1, i1, a), (p2, i2, b) in zip(rr, rr[1:]):
            if p1 == p2 and not i1 and not i2 and a and b:
                out.append((tuple(D(a)), tuple(D(b))))
    return out


def misure_coppie(cc):
    corpi = [(a[1:], b[1:]) for a, b in cc if len(a) >= 3 and len(b) >= 3]
    return {'corpi_identici': sum(x == y for x, y in corpi) / len(corpi),
            'somiglianza_corpi': sum(1 - misure._dist_norm(x, y) for x, y in corpi) / len(corpi),
            'parole_identiche': sum(a == b for a, b in cc) / len(cc)}


def misura(per, rnd):
    v = misure_coppie(coppie(per))
    nulli = {k: [] for k in v}
    for _ in range(PERMUTAZIONI):
        nuovo = OrderedDict()
        for pag, rr in per.items():
            idx = [i for i, (_, ini, _) in enumerate(rr) if not ini]
            ws = [rr[i][2] for i in idx]
            rnd.shuffle(ws)
            n = list(rr)
            for i, w in zip(idx, ws):
                n[i] = (rr[i][0], False, w)
            nuovo[pag] = n
        for k, x in misure_coppie(coppie(nuovo)).items():
            nulli[k].append(x)
    out = OrderedDict([('n', len(coppie(per)))])
    for k in v:
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('reale', v[k]), ('atteso', m), ('rapporto', v[k] / m if m else None), ('z', (v[k] - m) / s if s else None)])
    return out


def righe_voynich(lingua=None):
    out, par = [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        if not r.parole:
            continue
        par += bool(r.inizio_par)
        out.append((r.pagina, par, bool(r.inizio_par), list(r.parole)))
    return out


def main():
    t = OrderedDict()
    rv = righe_voynich()
    t['Voynich'] = rv
    t['Voynich A'] = righe_voynich('A')
    t['Voynich B'] = righe_voynich('B')
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    rts, par = [], 0
    for i, (ini, ps) in enumerate(ts):
        par += ini
        rts.append((i // 29, par, ini, ps))
    t['Timm e Schinner, seme 19'] = rts
    rnd = random.Random(SEME)
    primi = Counter(D(ps[0])[0] for _, _, ini, ps in rv if not ini and trascrizione.pulita(ps[0]))
    segni, pesi = zip(*sorted(primi.items()))
    cp = list(rv)
    for k in range(1, len(rv)):
        pag, par, ini, ps = rv[k]
        pag0, par0, _, ps0 = rv[k - 1]
        if ini or pag0 != pag or par0 != par or rnd.random() >= 0.5 or not trascrizione.pulita(ps0[0]):
            continue
        u = D(ps0[0])
        while True:
            g = rnd.choices(segni, pesi)[0]
            if g != u[0]:
                break
        cp[k] = (pag, par, ini, [g + ''.join(u[1:])] + ps[1:])
    t['controllo positivo: copia e cambio (metà righe)'] = cp
    ris = OrderedDict()
    for nome, righe in t.items():
        r = OrderedDict()
        for etichetta, pos in (('prima', 0), ('seconda', 1)):
            r[etichetta] = misura(colonna(righe, pos), random.Random(SEME))
        ris[nome] = r
        f = lambda x: '%.2f (z %.1f)' % (x['rapporto'], x['z'] or 0)
        print('%-48s prima: corpi %s somigl. %s parole %s | seconda: corpi %s somigl. %s parole %s' % (
            nome, f(r['prima']['corpi_identici']), f(r['prima']['somiglianza_corpi']), f(r['prima']['parole_identiche']),
            f(r['seconda']['corpi_identici']), f(r['seconda']['somiglianza_corpi']), f(r['seconda']['parole_identiche'])), flush=True)
    with open(os.path.join(RISULTATI, 'e88_copia_cambia_inizio.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e88 — Copia e cambia l\'inizio?', '',
           'Rapporti con l\'atteso (%d rimescolamenti delle righe nella pagina), z fra parentesi. Corpo = parola senza il primo '
           'segno. Preregistrazione: `preregistrazioni/e88.md`.' % PERMUTAZIONI, '',
           '| testo | colonna | corpi identici | somiglianza dei corpi | parole identiche |', '|---|---|---|---|---|']
    for nome, r in ris.items():
        for col in ('prima', 'seconda'):
            x = r[col]
            out.append('| %s | %s | %s |' % (nome, col, ' | '.join('%.2f (%.1f)' % (x[k]['rapporto'], x[k]['z'] or 0)
                                                                for k in ('corpi_identici', 'somiglianza_corpi', 'parole_identiche'))))
    with open(os.path.join(RISULTATI, 'e88_copia_cambia_inizio.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
