# -*- coding: utf-8 -*-
"""Esperimento 106: il miglior generatore (e69) con regole di riga stimate sul Voynich (prima parola scelta per
classe dalla riga sopra, segno aggiunto, ch/sh per posizione): sufficienza dell'ipotesi senza messaggio?

Preregistrazione: preregistrazioni/e106.md. Serve Java. Scrive risultati/e106_procedimento_versi.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e48_composizione as e48
import e55_forma_parole as e55
import e61_pagella as e61
import e68_filtro_forma as e68
import e69_forma_quattro as e69
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e94_seconda_posizione as e94
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (19, 1, 2)
D = misure.divisore(misure.GLIFI_EVA)
FAMIGLIE = {'ch': 'B', 'sh': 'B', 'ckh': 'B', 'cth': 'B', 'k': 'G', 't': 'G', 'p': 'G', 'f': 'G', 'd': 'D', 'r': 'D', 's': 'D'}
SH = {'prima': 0.58, 'seconda': 0.43, 'interna': 0.33, 'ultima': 0.23}
RIGHE_PAGINA = 29


def classe(w):
    g = D(w)[0]
    return FAMIGLIE.get(g, g)


def stime_voynich():
    """P(classe | classe sopra) e, per classe, i primi segni a inizio riga."""
    trans = defaultdict(Counter)
    segni = defaultdict(Counter)
    for rr in e83.pagine('ZL').values():
        for (p1, i1, a), (p2, i2, b) in zip(rr, rr[1:]):
            if p1 == p2 and not i1 and not i2 and a and b:
                trans[classe(a)][classe(b)] += 1
                segni[classe(b)][D(b)[0]] += 1
    return trans, segni


def genera_base(seme):
    e68.LAVORO = os.path.join(e22.LAVORO, 'procedimento_versi')
    os.makedirs(e68.LAVORO, exist_ok=True)
    e68.LAM = 0.6
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    parole_file = os.path.join(e68.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(voy) + '\n')
    giunture = os.path.join(e68.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(giunture)
    base = [w for l in open(e68.BASE_E51 % 19, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')
            for w in l.split()]
    forma_file = os.path.join(e68.LAVORO, 'forma_2.tsv')
    e69.tabella(voy, base, e69.POSIZIONI[2], forma_file)
    if not getattr(genera_base, 'classi', None):
        genera_base.classi = e68.compila()
    e68.genera(genera_base.classi, giunture, parole_file, forma_file, 1.0, seme)
    return e71.righe_file(os.path.join(e68.LAVORO, 'eta_1_seme_%d' % seme, 'generate', 'generated_text.txt'))


def applica_regole(righe, trans, segni, rnd):
    """righe: (inizio paragrafo, parole). Restituisce le righe modificate."""
    out = []
    pagina_parole = []
    for k, (ini, ps) in enumerate(righe):
        if k % RIGHE_PAGINA == 0:
            pagina_parole = []
        ps = list(ps)
        if not ini and out and k % RIGHE_PAGINA != 0 and ps:
            sopra = out[-1][1][0] if out[-1][1] else None
            if sopra:
                cs = classe(sopra)
                if trans[cs]:
                    c = rnd.choices(list(trans[cs]), weights=list(trans[cs].values()))[0]
                    nuova = None
                    if c in ('y', 'o', 'D') and rnd.random() < 0.5:
                        cand = [w for w in pagina_parole if classe(w) != c]
                        if cand:
                            g = rnd.choices(list(segni[c]), weights=list(segni[c].values()))[0]
                            nuova = g + rnd.choice(cand)
                    if nuova is None:
                        cand = [w for w in pagina_parole if classe(w) == c and w != sopra]
                        if cand:
                            nuova = rnd.choice(cand)
                    if nuova:
                        ps[0] = nuova
        n = len(ps)
        for i, w in enumerate(ps):
            u = D(w)
            if u and u[0] in ('ch', 'sh'):
                pos = 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'
                u[0] = 'sh' if rnd.random() < SH[pos] else 'ch'
                ps[i] = ''.join(u)
        pagina_parole.extend(ps)
        out.append((ini, ps))
    return out


def misura(righe, voy, soglia_ab, vv, vb):
    pagine = [[ps for _, ps in righe[i:i + RIGHE_PAGINA]] for i in range(0, len(righe), RIGHE_PAGINA)]
    r = e61.scheda(pagine, D, voy, soglia_ab)
    esiti = OrderedDict()
    for prop, f in e61.BANDE.items():
        try:
            esiti[prop] = bool(f(r, vv))
        except (KeyError, TypeError, ZeroDivisionError):
            esiti[prop] = False
    con_pag = [(i // RIGHE_PAGINA, ini, ps) for i, (ini, ps) in enumerate(righe)]
    rnd = random.Random(106)
    d, a = e74.coppie(con_pag, D)
    x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
    r['R_riga'] = y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None
    b = e71.una(('x', righe, 'eva'))[1]
    r['bordo_inizio'], r['bordo_fine'] = b['jsd_inizio']['rapporto'], b['jsd_fine']['rapporto']
    esiti['bordo di riga'] = 0.5 * vb[0] <= r['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= r['bordo_fine'] <= 2 * vb[1]
    per = OrderedDict()
    par = 0
    for i, (ini, ps) in enumerate(righe):
        par += ini
        per.setdefault(i // RIGHE_PAGINA, []).append((par, ini, ps[0] if ps else None))
    r['S1'] = e83.misura(per, 1, e83.primo_eva, random.Random(106))['S']
    rr88 = [(i // RIGHE_PAGINA, par_i, ini, ps) for i, (par_i, (ini, ps)) in enumerate(zip(
        [sum(x[0] for x in righe[:k + 1]) for k in range(len(righe))], righe))]
    r['copia_prima'] = e88.misura(e88.colonna(rr88, 0), random.Random(106))['corpi_identici']['rapporto']
    r['copia_seconda'] = e88.misura(e88.colonna(rr88, 1), random.Random(106))['corpi_identici']['rapporto']
    r['e94_pos2'] = e94.misura(righe)['posizione 2']['rapporto']
    r['esiti'] = esiti
    return r


def main():
    e83.PERMUTAZIONI = 300
    e88.PERMUTAZIONI = 200
    e71.RIMESCOLAMENTI = 50
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    trans, segni = stime_voynich()
    ris = OrderedDict()
    for nome in ('base (e69)', 'con regole di riga'):
        ris[nome] = []
    for s in SEMI:
        base = genera_base(s)
        ris['base (e69)'].append(misura(base, voy, soglia_ab, v, vb))
        mod = applica_regole(base, trans, segni, random.Random(1060 + s))
        ris['con regole di riga'].append(misura(mod, voy, soglia_ab, v, vb))
        for nome in ris:
            r = ris[nome][-1]
            print('seme %d %-20s %d/18 | R %.2f S1 %.2f copia 1a %.2f 2a %.2f e94 %.2f | h2 %.2f rip %.2f omog %.3f forma %.2f' % (
                s, nome, sum(r['esiti'].values()), r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'], r['e94_pos2'],
                r['h2'], r['identiche_vs_riga'], r['somiglianza_riga'], r.get('V8_forma', 0)), flush=True)
    medie = OrderedDict()
    for nome, gruppo in ris.items():
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(m, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= m['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= m['bordo_fine'] <= 2 * vb[1]
        m['esiti'] = esiti
        m['sufficienza'] = (sum(esiti.values()) >= 12 and m['R_riga'] < 0.1 and m['copia_prima'] <= 1.1
                            and m['copia_seconda'] > 1.2 and m['e94_pos2'] >= 1.2)
        medie[nome] = m
        print('%-20s %d/18 | R %.2f S1 %.2f copia 1a %.2f 2a %.2f e94 %.2f | sufficienza %s | %s' % (
            nome, sum(esiti.values()), m['R_riga'], m['S1'], m['copia_prima'], m['copia_seconda'], m['e94_pos2'],
            m['sufficienza'], ' '.join(p for p, x in esiti.items() if not x)), flush=True)
    with open(os.path.join(RISULTATI, 'e106_procedimento_versi.json'), 'w', encoding='utf-8') as fo:
        json.dump({'semi': ris, 'medie': medie}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e106 — Un procedimento "a versi"', '',
           'Miglior generatore (e69) senza e con regole di riga stimate sul Voynich. Medie su tre semi. Preregistrazione: '
           '`preregistrazioni/e106.md`.', '',
           '| modello | pagella | R | S(1) | copia 1ª / 2ª colonna | e94 pos. 2 | sufficienza |', '|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %.2f | %.2f | %.2f / %.2f | %.2f | %s |' % (nome, sum(m['esiti'].values()), m['R_riga'], m['S1'],
                                                                         m['copia_prima'], m['copia_seconda'], m['e94_pos2'], 'sì' if m['sufficienza'] else 'no'))
    out += ['', '| modello | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e106_procedimento_versi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
