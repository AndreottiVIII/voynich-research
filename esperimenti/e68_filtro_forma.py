# -*- coding: utf-8 -*-
"""Esperimento 68: il filtro di forma. Sul modello e51, ogni parola copiata e ritoccata si accetta
con probabilita' proporzionale a (r_inizio * r_fine)^eta, dove r = P_Voynich / P_modello per il
primo e l'ultimo segno. Con eta = 0 il testo e' identico al modello e51 (validita').

Preregistrazione: preregistrazioni/e68.md. Serve Java. Scrive risultati/e68_filtro_forma.json e .md.
"""
import hashlib, json, os, shutil, subprocess, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e50_recenza_novita as e50
import e55_forma_parole as e55
import e61_pagella as e61
e48 = e50.e48
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'filtro_forma')
FORMA = os.path.join(QUI, '..', 'analisi', 'timm_schinner', 'Forma.java')
BASE_E51 = os.path.join(e22.LAVORO, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_%d', 'generate', 'generated_text.txt')
ETA = (0.0, 0.5, 1.0)
SEMI = (19, 1, 2)
Q, LAM, K = 0.10, 0.75, 0
D = misure.divisore(misure.GLIFI_EVA)
BERSAGLI = ('forma parole', 'spazio')
FUORI = ('profilo pagina', 'lunghezze vicine', 'Zipf', 'verticale', 'formule', 'deriva', 'unioni')


def compila():
    e48.LAVORO = LAVORO
    e50.LAVORO = LAVORO
    classi = e50.compila()
    sorgente = os.path.join(LAVORO, 'java')
    principale = os.path.join(sorgente, 'de', 'voynich', 'text', 'SelfCitationTextGenerator.java')
    testo = open(principale, encoding='utf-8').read()
    ancora = '                    // add modified groups\n                    if (useMorphedGroups || forceUsage) {'
    nuovo = ('                    // filtro di forma (aggiunta, vedi Forma.java)\n'
             '                    if (useMorphedGroups && !forceUsage && Forma.attiva() && !Forma.accetta(firstGroup.glyphGroup)) {\n'
             '                        useMorphedGroups = false;\n'
             '                    }\n\n' + ancora)
    assert testo.count(ancora) == 1
    open(principale, 'w', encoding='utf-8').write(testo.replace(ancora, nuovo))
    shutil.copy(FORMA, os.path.join(sorgente, 'de', 'voynich', 'text'))
    shutil.rmtree(classi, ignore_errors=True)
    os.makedirs(classi)
    files = [os.path.join(d, f) for d, _, fs in os.walk(sorgente) for f in fs if f.endswith('.java')]
    r = subprocess.run(['javac', '-nowarn', '-d', classi] + files, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-3000:])
    return classi


def tabella_forma(voy, base, percorso):
    righe = []
    for etichetta, pos in (('i', 0), ('f', -1)):
        cv = Counter(D(w)[pos] for w in voy)
        cb = Counter(D(w)[pos] for w in base)
        nv, nb = sum(cv.values()), sum(cb.values())
        for g in sorted(set(cv) | set(cb)):
            pv, pb = cv[g] / nv, cb[g] / nb
            r = (pv + 1e-4) / (pb + 1e-4)
            righe.append('%s\t%s\t%.5f' % (etichetta, g, r))
    with open(percorso, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(righe) + '\n')


def genera(classi, tabella, parole_file, forma_file, eta, seme):
    cartella = os.path.join(LAVORO, 'eta_%g_seme_%d' % (eta, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read()
    righe = []
    for riga in conf.splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        righe.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % e48.FORZA,
                    '-Dcomposizione.file=' + parole_file, '-Dcomposizione.quota=%g' % Q,
                    '-Dcomposizione.pagina=%g' % LAM, '-Dcomposizione.seme=%d' % (48 + seme),
                    '-Dcomposizione.giunture=1', '-Dcomposizione.nuove=1', '-Drecente.paragrafi=%d' % K,
                    '-Dforma.file=' + forma_file, '-Dforma.eta=%g' % eta, '-Dforma.seme=%d' % (68 + seme),
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    return [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)], \
        hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def main():
    os.makedirs(LAVORO, exist_ok=True)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    parole_file = os.path.join(LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(voy) + '\n')
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    base = [w for l in open(BASE_E51 % 19, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')
            for w in l.split()]
    forma_file = os.path.join(LAVORO, 'forma.tsv')
    tabella_forma(voy, base, forma_file)
    classi = compila()
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    ris = OrderedDict()
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    ris['Voynich'] = v
    ris['validita'] = {}
    medie = OrderedDict()
    for eta in ETA:
        gruppo = []
        for s in SEMI:
            pagine, imp = genera(classi, tabella, parole_file, forma_file, eta, s)
            if eta == 0:
                corpo = [l for l in open(BASE_E51 % s, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
                ris['validita']['seme %d' % s] = imp == hashlib.md5('\n'.join(corpo).encode()).hexdigest()
            r = e61.scheda(pagine, D, voy, soglia_ab)
            ris['eta %.1f, seme %d' % (eta, s)] = r
            gruppo.append(r)
        chiavi = [c for c, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(c), (int, float)) for g in gruppo)]
        m = {c: sum(g[c] for g in gruppo) / len(gruppo) for c in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(m, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        m['esiti'] = esiti
        medie['eta %.1f' % eta] = m
        print('eta %.1f: %d/17 | bersagli %s | fuori campione %d/%d | h2 %.2f spazio %.2f rip %.2f omog %.3f forma %.2f R %.2f lungh %.3f zipf %.2f' % (
            eta, sum(esiti.values()), ''.join('✓' if esiti[p] else '·' for p in BERSAGLI),
            sum(esiti[p] for p in FUORI), len(FUORI), m['h2'], m['spazio_spiegato'], m['identiche_vs_riga'],
            m['somiglianza_riga'], m.get('V8_forma', 0), m['V3_R'] or 0, m['V6_autocorrelazione_lunghezze'], m['V7_zipf']),
            flush=True)
    print('validita', ris['validita'])
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e68_filtro_forma.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE)
    out = ['# e68 — Il filtro di forma', '',
           'Modello e51 con filtro di forma sui segni iniziali e finali (η). Medie su tre semi. Validità (η = 0 uguale '
           'a e51): %s. Bersagli: %s; fuori campione: %s. Preregistrazione: `preregistrazioni/e68.md`.' % (
               'sì' if all(ris['validita'].values()) else 'NO', ', '.join(BERSAGLI), ', '.join(FUORI)), '',
           '| η | totale | ' + ' | '.join(props) + ' |', '|---|---|' + '---|' * len(props)]
    for nome, m in medie.items():
        out.append('| %s | %d/17 | %s |' % (nome, sum(m['esiti'].values()), ' | '.join(
            ('✓ ' if m['esiti'][p] else '· ') + ('%.3g' % m[e61.VALORI[p]] if e61.VALORI.get(p) in m else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e68_filtro_forma.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
