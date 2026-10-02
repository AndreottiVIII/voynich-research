# -*- coding: utf-8 -*-
"""Esperimento 121: il generatore e69 senza copia a catena (method.morph.reuse_last.probability = 0) e con le regole di
riga dell'e106; tutte le proprieta' insieme (pagella, R, S(1), copia della prima colonna, e94, alternanza A).

Preregistrazione: preregistrazioni/e121.md. Serve Java. Scrive risultati/e121_senza_catena.json e .md.
"""
import json, os, random, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e48_composizione as e48
import e50_recenza_novita as e50
import e55_forma_parole as e55
import e61_pagella as e61
import e68_filtro_forma as e68
import e69_forma_quattro as e69
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e106_procedimento_versi as e106
import e110_alternanza as e110
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI = (19, 1, 2)
D = misure.divisore(misure.GLIFI_EVA)
LAVORO = os.path.join(e22.LAVORO, 'senza_catena')


def prepara():
    e68.LAVORO = LAVORO
    os.makedirs(LAVORO, exist_ok=True)
    e68.LAM = 0.6
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    parole_file = os.path.join(LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(voy) + '\n')
    giunture = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(giunture)
    base = [w for l in open(e68.BASE_E51 % 19, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#') for w in l.split()]
    forma_file = os.path.join(LAVORO, 'forma_2.tsv')
    e69.tabella(voy, base, e69.POSIZIONI[2], forma_file)
    return e68.compila(), giunture, parole_file, forma_file


def genera(classi, giunture, parole_file, forma_file, seme, riuso):
    cartella = os.path.join(LAVORO, 'riuso_%d_seme_%d' % (riuso, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read()
    righe = []
    for riga in conf.splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        elif riga.startswith('method.morph.reuse_last.probability='):
            continue
        righe.append(riga)
    righe.append('method.morph.reuse_last.probability=%d' % riuso)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + giunture, '-Dgiunture.forza=%g' % e50.e48.FORZA,
                    '-Dcomposizione.file=' + parole_file, '-Dcomposizione.quota=%g' % e68.Q,
                    '-Dcomposizione.pagina=%g' % e68.LAM, '-Dcomposizione.seme=%d' % (48 + seme),
                    '-Dcomposizione.giunture=1', '-Dcomposizione.nuove=1', '-Drecente.paragrafi=%d' % e68.K,
                    '-Dforma.file=' + forma_file, '-Dforma.eta=1', '-Dforma.seme=%d' % (68 + seme),
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return e71.righe_file(os.path.join(cartella, 'generate', 'generated_text.txt'))


def alternanza(righe):
    _, r = e110.una(('x', [ps for _, ps in righe], 'eva'))
    return r['senza identiche']['A']


def main():
    e83.PERMUTAZIONI = 300
    e88.PERMUTAZIONI = 200
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    trans, segni = e106.stime_voynich()
    classi, giunture, parole_file, forma_file = prepara()
    modelli = OrderedDict([('base', (10, False)), ('senza catena', (0, False)), ('base + regole di riga', (10, True)),
                           ('senza catena + regole di riga', (0, True))])
    per = {m: [] for m in modelli}
    testi = {}
    for s in SEMI:
        for riuso in (10, 0):
            testi[(riuso, s)] = genera(classi, giunture, parole_file, forma_file, s, riuso)
        for nome, (riuso, regole) in modelli.items():
            rr = testi[(riuso, s)]
            if regole:
                rr = e106.applica_regole(rr, trans, segni, random.Random(1210 + s))
            r = e106.misura(rr, voy, soglia_ab, v, vb)
            r['A'] = alternanza(rr)
            per[nome].append(r)
            print('seme %2d %-30s %d/18 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | h2 %.2f rip %.2f omog %.3f tipi %.3f' % (
                s, nome, sum(r['esiti'].values()), r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'], r['e94_pos2'],
                r['A'], r['h2'], r['identiche_vs_riga'], r['somiglianza_riga'], r['tipi_su_parole']), flush=True)
    medie = OrderedDict()
    for nome, gruppo in per.items():
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
        m['completo'] = (sum(esiti.values()) >= 12 and m['R_riga'] < 0.1 and m['S1'] <= 0.7 and m['copia_prima'] <= 1.1
                         and m['copia_seconda'] > 1.15 and m['e94_pos2'] >= 1.2 and m['A'] >= 1.0)
        medie[nome] = m
        print('%-30s %d/18 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | completo %s | mancano: %s' % (
            nome, sum(esiti.values()), m['R_riga'], m['S1'], m['copia_prima'], m['copia_seconda'], m['e94_pos2'], m['A'],
            m['completo'], ', '.join(p for p, x in esiti.items() if not x)), flush=True)
    with open(os.path.join(RISULTATI, 'e121_senza_catena.json'), 'w', encoding='utf-8') as fo:
        json.dump({'semi': per, 'medie': medie}, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e121 — Un procedimento senza catena e con regole di riga', '', 'Generatore e69, medie su tre semi. Preregistrazione: '
           '`preregistrazioni/e121.md`. Voynich: R 0,006, S(1) 0,52, copia 1,03/1,47, e94 1,43, A 1,044.', '',
           '| modello | pagella | R | S(1) | copia 1ª / 2ª | e94 | A | completo |', '|---|---|---|---|---|---|---|---|']
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f | %s |' % (nome, sum(m['esiti'].values()), m['R_riga'], m['S1'], m['copia_prima'],
                                                                            m['copia_seconda'], m['e94_pos2'], m['A'], 'sì' if m['completo'] else 'no'))
    out += ['', '| modello | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e121_senza_catena.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
