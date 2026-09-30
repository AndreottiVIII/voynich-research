# -*- coding: utf-8 -*-
"""Esperimento 48: autocitazione piu' composizione. Il generatore di Timm e Schinner (con le
giunture, e23) che a volte compone una parola nuova segno per segno, con le regole di
combinazione dei segni del Voynich (globali) e della pagina corrente (peso lambda).

Con q = 0 il testo deve essere identico a quello dell'e23 (controllo di validita').
Preregistrazione: preregistrazioni/e48.md. Serve Java.
Scrive risultati/e48_composizione.json e .md.
"""
import hashlib, json, os, shutil, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
from e07_codifiche import pagine_voynich
from e47_vocabolario import per_finestre

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'composizione')
AGGIUNTA = os.path.join(QUI, '..', 'analisi', 'timm_schinner', 'Composizione.java')
QUOTE = (0.0, 0.05, 0.1, 0.2, 0.3)
LAMBDA = (0.0, 0.5, 0.9)
SEMI = (19, 1, 2)
FORZA = 3.0

DICHIARAZIONE = '''        GlyphGroup lastGeneratedGroup = null;
        boolean postoComposto = false;   // aggiunta, vedi Composizione.java'''
RICORDA = '''                                config.statistics.remember(morphedGroup);
                                Composizione.ricorda(morphedGroup.glyphGroup, config.statistics.linesInPage);'''
INSERIMENTO = '''            // composizione (aggiunta, vedi Composizione.java): a ogni posto di parola nuovo, con
            // probabilita' composizione.quota, la parola si compone segno per segno
            if (count == 1 && Composizione.attiva()) {
                postoComposto = Composizione.scegli();
            }
            if (postoComposto) {
                postoComposto = false;
                GlyphGroup composta = Composizione.componi(config);
                if (composta != null && availablePlaceInLine - composta.length() - (isLineInitial ? 0 : 1) >= 0) {
                    if (isLineInitial) {
                        isLineInitial = false;
                    } else {
                        line.append(" ");
                        availablePlaceInLine -= 1;
                    }
                    glyphGroupList.add(composta);
                    config.statistics.remember(composta);
                    Composizione.ricorda(composta.glyphGroup, config.statistics.linesInPage);
                    lastGeneratedGroup = composta;
                    line.append(composta.glyphGroup);
                    availablePlaceInLine -= composta.length();
                    count = 0;
                    tries = 0;
                    continue;
                }
            }

            // modify source groups'''


def compila():
    sorgente = os.path.join(LAVORO, 'java')
    shutil.rmtree(sorgente, ignore_errors=True)
    shutil.copytree(os.path.join(e22.GENERATORE, 'source', 'src', 'main', 'java'), sorgente)
    principale = os.path.join(sorgente, 'de', 'voynich', 'text', 'SelfCitationTextGenerator.java')
    testo = open(principale, encoding='utf-8').read()
    for ancora, nuovo in ((e23.CHIAMATA.split('\n')[-2] + '\n' + e23.CHIAMATA.split('\n')[-1], e23.CHIAMATA),
                          ('        GlyphGroup lastGeneratedGroup = null;', DICHIARAZIONE),
                          ('                                config.statistics.remember(morphedGroup);', RICORDA),
                          ('            // modify source groups', INSERIMENTO)):
        assert testo.count(ancora) == 1, ancora
        testo = testo.replace(ancora, nuovo)
    open(principale, 'w', encoding='utf-8').write(testo)
    for f in (e23.AGGIUNTA, AGGIUNTA):
        shutil.copy(f, os.path.join(sorgente, 'de', 'voynich', 'text'))
    classi = os.path.join(LAVORO, 'classi')
    shutil.rmtree(classi, ignore_errors=True)
    os.makedirs(classi)
    files = [os.path.join(d, f) for d, _, fs in os.walk(sorgente) for f in fs if f.endswith('.java')]
    r = subprocess.run(['javac', '-nowarn', '-d', classi] + files, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-3000:])
    return classi


def genera(classi, tabella, parole_file, quota, lam, seme):
    cartella = os.path.join(LAVORO, 'q_%g_l_%g_seme_%d' % (quota, lam, seme))
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
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % FORZA,
                    '-Dcomposizione.file=' + parole_file, '-Dcomposizione.quota=%g' % quota,
                    '-Dcomposizione.pagina=%g' % lam, '-Dcomposizione.seme=%d' % (48 + seme),
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    pagine = [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]
    return pagine, hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def compatibile(r):
    return (r['identiche_vs_riga'] >= 0.7 and r['somiglianza_riga'] >= 0.03
            and r['somiglianza_6_righe'] < r['somiglianza_riga'] and r['h2'] <= 2.40
            and r['confine'] >= 0.15 and r['hapax_34000'] >= 0.60)


def misura(pagine, glifi):
    r = e22.lista_di_controllo(pagine, glifi)
    f = per_finestre([w for p in pagine for rr in p for w in rr])
    r['hapax_1000'] = f[1000]['hapax']
    r['hapax_34000'] = f[34000]['hapax'] if 34000 in f else f[max(f)]['hapax']
    return r


def main():
    os.makedirs(LAVORO, exist_ok=True)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_file = os.path.join(LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(trascrizione.parole(corrente)) + '\n')
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi_e23 = e23.compila()
    classi = compila()
    ris = OrderedDict()
    ris['Voynich'] = misura(pagine_voynich(corrente), glifi)
    e22.stampa('Voynich', ris['Voynich'])
    ris['validita'] = {}
    combinazioni = [(0.0, 0.0)] + [(q, l) for q in QUOTE[1:] for l in LAMBDA]
    for q, lam in combinazioni:
        for seme in SEMI:
            pagine, impronta = genera(classi, tabella, parole_file, q, lam, seme)
            if q == 0:
                _, imp_e23 = e23.genera(classi_e23, tabella, FORZA, seme, nome='per_e48_seme_%d' % seme)
                ris['validita']['seme %d' % seme] = impronta == imp_e23
                assert impronta == imp_e23, 'con q = 0 il testo non e\' quello dell\'e23'
            nome = 'q %.2f, lambda %.1f, seme %d' % (q, lam, seme)
            ris[nome] = dict(misura(pagine, glifi), q=q, lam=lam, seme=seme)
            e22.stampa(nome[:28], ris[nome])
    medie = OrderedDict()
    chiavi = [k for k, v in ris['q 0.00, lambda 0.0, seme 19'].items() if isinstance(v, (int, float)) and k not in ('q', 'lam', 'seme')]
    for q, lam in combinazioni:
        g = [ris['q %.2f, lambda %.1f, seme %d' % (q, lam, s)] for s in SEMI]
        m = {k: sum(x[k] for x in g) / len(g) for k in chiavi}
        m['compatibile'] = compatibile(m)
        medie['q %.2f, lambda %.1f' % (q, lam)] = m
        print('MEDIA q %.2f lambda %.1f: rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f hapax1000 %.2f hapax34000 %.2f %s' % (
            q, lam, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
            m['confine'], m['hapax_1000'], m['hapax_34000'], 'COMPATIBILE' if m['compatibile'] else ''), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e48_composizione.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    v = ris['Voynich']
    out = ['# e48 — Autocitazione più composizione di parole nuove', '',
           'Generatore di Timm e Schinner con giunture (forza 3); con probabilità q una parola si compone segno per '
           'segno (trigrammi di segni: λ · pagina corrente + (1 − λ) · tutto il Voynich). Medie su tre semi. '
           'Validità: con q = 0 il testo è identico all\'e23 (%s). Compatibile = ripetizione ≥ 0,7, somiglianza '
           'nella riga ≥ 3%% e calante, h2 ≤ 2,40, legame ≥ 0,15, parole uniche a 34.000 ≥ 0,60. Preregistrazione: '
           '`preregistrazioni/e48.md`.' % ('sì' if all(ris['validita'].values()) else 'NO'), '',
           '| testo | h2 | spazio | uniche (1.000) | uniche (34.000) | tipi/parole | ripetizione | somigl. riga | 6 righe | legame | compatibile |',
           '|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.0f%% | %.2f | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | |' % (
               v['h2'], 100 * v['spazio_spiegato'], v['hapax_1000'], v['hapax_34000'], v['tipi_su_parole'],
               v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.0f%% | %.2f | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | %s |' % (
            nome, m['h2'], 100 * m['spazio_spiegato'], m['hapax_1000'], m['hapax_34000'], m['tipi_su_parole'],
            m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['confine'],
            'sì' if m['compatibile'] else 'no'))
    with open(os.path.join(RISULTATI, 'e48_composizione.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
