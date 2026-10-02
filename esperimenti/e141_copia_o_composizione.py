# -*- coding: utf-8 -*-
"""Esperimento 141: le regole d'inizio riga valgono anche dopo le righe accorciate (da un disegno)? Segno d'inizio,
evitamento e giuntura dopo righe corte e dopo righe piene.

Preregistrazione: preregistrazioni/e141.md. Scrive risultati/e141_copia_o_composizione.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e74_legame_a_capo as e74

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, BOOT = 141, 1000
D = misure.divisore(misure.GLIFI_EVA)
INIZI = {'y', 'd', 's'}


def lunghezza(ps):
    return sum(len(D(w)) for w in ps) + len(ps) - 1


def paragrafi():
    out, cur, pag = [], [], None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = list(r.parole)
        if not ps:
            continue
        if r.inizio_par or r.pagina != pag:
            if cur:
                out.append(cur)
            cur, pag = [], r.pagina
        cur.append((r.pagina, ps))
    if cur:
        out.append(cur)
    return [p for p in out if p]


def spezza(pars, rnd):
    out = []
    for p in pars:
        q = []
        for j, (pag, ps) in enumerate(p):
            if j < len(p) - 1 and len(ps) >= 5 and rnd.random() < 0.10:
                k = max(1, int(round(0.4 * len(ps))))
                q.append((pag, ps[:k]))
                q.append((pag, ps[k:]))
            else:
                q.append((pag, ps))
        out.append(q)
    return out


def coppie(pars):
    mediane = defaultdict(list)
    for p in pars:
        for j, (pag, ps) in enumerate(p[:-1]):
            mediane[pag].append(lunghezza(ps))
    med = {pag: statistics.median(l) for pag, l in mediane.items()}
    gruppi = {'dopo riga corta': [], 'dopo riga piena': []}
    for p in pars:
        for j in range(len(p) - 1):
            pag, a = p[j]
            _, b = p[j + 1]
            if len(a) < 2 or len(b) < 2 or not all(trascrizione.pulita(w) for w in (a[0], a[-1], b[0])):
                continue
            L = lunghezza(a) / med[pag]
            if L < 0.6:
                gruppi['dopo riga corta'].append((a, b))
            elif L >= 0.9:
                gruppi['dopo riga piena'].append((a, b))
    return gruppi


def misura(cc, rnd):
    inizio = [1 if D(b[0])[0] in INIZI else 0 for a, b in cc]
    uguale = [1 if D(b[0])[0] == D(a[0])[0] else 0 for a, b in cc]

    def boot(x):
        m = [statistics.mean(rnd.choices(x, k=len(x))) for _ in range(BOOT)]
        m.sort()
        return [m[int(0.05 * BOOT)], m[int(0.95 * BOOT)]]
    dentro = [(D(x)[-1], D(y)[0]) for a, b in cc for ps in (a, b) for x, y in zip(ps[1:-2], ps[2:-1]) if trascrizione.pulita(x) and trascrizione.pulita(y)]
    attraverso = [(D(a[-1])[-1], D(b[0])[0]) for a, b in cc]
    x, y = e74.eccesso(dentro, rnd), e74.eccesso(attraverso, rnd)
    return OrderedDict([('coppie', len(cc)), ('segno_inizio', statistics.mean(inizio)), ('segno_inizio_iv', boot(inizio)),
                        ('stesso_primo_segno', statistics.mean(uguale)), ('stesso_primo_segno_iv', boot(uguale)),
                        ('giuntura_dentro', x['eccesso']), ('giuntura_attraverso', y['eccesso']), ('z_attraverso', y['z']),
                        ('R', y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None)])


def main():
    rnd = random.Random(SEME)
    pars = paragrafi()
    ris = OrderedDict()
    for nome, pp in (('Voynich ZL', pars), ('controllo positivo: 10% delle righe piene spezzate', spezza(pars, random.Random(SEME + 1)))):
        g = coppie(pp)
        ris[nome] = OrderedDict((k, misura(v, rnd)) for k, v in g.items())
        for k, r in ris[nome].items():
            print('%-52s %-16s coppie %4d | inizio y/d/s %.3f [%.3f-%.3f] | stesso primo segno %.3f | R %.2f (z attraverso %.1f)' % (
                nome, k, r['coppie'], r['segno_inizio'], *r['segno_inizio_iv'], r['stesso_primo_segno'], r['R'] or 0, r['z_attraverso'] or 0), flush=True)
    rap = lambda n: ris[n]['dopo riga corta']['segno_inizio'] / ris[n]['dopo riga piena']['segno_inizio']
    c = 'controllo positivo: 10% delle righe piene spezzate'
    valido = rap(c) < 0.7 or (ris[c]['dopo riga corta']['R'] or 0) > 0.5
    v = ris['Voynich ZL']['dopo riga corta']
    if rap('Voynich ZL') >= 0.8 and (v['R'] or 0) < 0.3:
        esito = 'composto sul posto'
    elif rap('Voynich ZL') < 0.6 or ((v['R'] or 0) > 0.5 and (v['z_attraverso'] or 0) > 3):
        esito = 'copiato con a capo diversi'
    else:
        esito = 'indeciso'
    ris['rapporto_inizio_Voynich'], ris['rapporto_inizio_controllo'] = rap('Voynich ZL'), rap(c)
    ris['valido'], ris['esito'] = valido, esito
    print('rapporto segno d\'inizio corta/piena: Voynich %.2f, controllo %.2f | valido %s | esito: %s' % (rap('Voynich ZL'), rap(c), valido, esito))
    with open(os.path.join(RISULTATI, 'e141_copia_o_composizione.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e141 — Copiato con a capo diversi o composto sul posto?', '', 'Riga corta: < 60% della mediana della pagina (non ultima di paragrafo); piena: ≥ 90%. '
           'Preregistrazione: `preregistrazioni/e141.md`.', '',
           '| testo | gruppo | coppie | inizio y/d/s [90%] | stesso primo segno | R giuntura (z) |', '|---|---|---|---|---|---|']
    for nome in ('Voynich ZL', c):
        for k, r in ris[nome].items():
            out.append('| %s | %s | %d | %.3f [%.3f–%.3f] | %.3f | %.2f (%.1f) |' % (nome, k, r['coppie'], r['segno_inizio'], *r['segno_inizio_iv'],
                                                                              r['stesso_primo_segno'], r['R'] or 0, r['z_attraverso'] or 0))
    out += ['', 'Rapporto segno d\'inizio (dopo corta / dopo piena): Voynich %.2f, controllo %.2f. Controllo valido: **%s**. Esito: **%s**.' % (
        rap('Voynich ZL'), rap(c), 'sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e141_copia_o_composizione.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
