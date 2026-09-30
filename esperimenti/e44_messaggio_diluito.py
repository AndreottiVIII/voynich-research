# -*- coding: utf-8 -*-
"""Esperimento 44: un messaggio diluito nel generatore di Timm e Schinner (con le giunture).

Il sorgente pubblicato si compila con Giunture.java (e23, forza 3) e Messaggio.java: a ogni
posto di parola nuovo, con probabilita' m, si scrive la parola successiva di un messaggio
vero (Plinio, libri 20-27, codice parola per parola sul vocabolario del Voynich). Con m = 0
il testo deve essere identico a quello dell'e23 (controllo di validita').

Preregistrazione: preregistrazioni/e44.md. Serve Java.
Scrive risultati/e44_messaggio_diluito.json e .md.
"""
import hashlib, json, os, random, shutil, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
from e07_codifiche import pagine_voynich
from e36_posizione_pagina import plinio

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'messaggio')
AGGIUNTA = os.path.join(QUI, '..', 'analisi', 'timm_schinner', 'Messaggio.java')
QUOTE = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5)
SEMI = (19, 1, 2)
FORZA = 3.0

DICHIARAZIONE = '''        GlyphGroup lastGeneratedGroup = null;
        boolean postoDiMessaggio = false;   // aggiunta, vedi Messaggio.java'''
INSERIMENTO = '''            // messaggio diluito (aggiunta, vedi Messaggio.java): a ogni posto di parola nuovo,
            // con probabilita' messaggio.quota, si scrive la parola successiva del messaggio
            if (count == 1 && Messaggio.attivo()) {
                postoDiMessaggio = Messaggio.scegli();
            }
            if (postoDiMessaggio) {
                GlyphGroup parolaMessaggio = Messaggio.prossima();
                if (availablePlaceInLine - parolaMessaggio.length() - (isLineInitial ? 0 : 1) >= 0) {
                    if (isLineInitial) {
                        isLineInitial = false;
                    } else {
                        line.append(" ");
                        availablePlaceInLine -= 1;
                    }
                    glyphGroupList.add(parolaMessaggio);
                    config.statistics.remember(parolaMessaggio);
                    lastGeneratedGroup = parolaMessaggio;
                    line.append(parolaMessaggio.glyphGroup);
                    availablePlaceInLine -= parolaMessaggio.length();
                    Messaggio.consumata();
                    postoDiMessaggio = false;
                    count = 0;
                    tries = 0;
                    continue;
                }
                postoDiMessaggio = false;   // non entra nella riga: il posto torna al generatore
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
    subprocess.run(['javac', '-nowarn', '-d', classi] + files, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return classi


def genera(classi, tabella, messaggio, quota, seme):
    cartella = os.path.join(LAVORO, 'quota_%g_seme_%d' % (quota, seme))
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
                    '-Dmessaggio.file=' + messaggio, '-Dmessaggio.quota=%g' % quota, '-Dmessaggio.seme=%d' % (44 + seme),
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    usate = os.path.join(cartella, 'generate', 'messaggio_usato.txt')
    n_usate = int(open(usate).read().strip()) if quota > 0 and os.path.exists(usate) else 0
    pagine = [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]
    return pagine, hashlib.md5('\n'.join(corpo).encode()).hexdigest(), n_usate


def compatibile(r):
    return (r['identiche_vs_riga'] >= 0.7 and r['somiglianza_riga'] >= 0.03
            and r['somiglianza_6_righe'] < r['somiglianza_riga'] and r['h2'] <= 2.40 and r['confine'] >= 0.15)


def main():
    os.makedirs(LAVORO, exist_ok=True)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    messaggio = os.path.join(LAVORO, 'messaggio.txt')
    latino = [w for _, ps in plinio() for w in ps]
    codice = generatori.codice_per_rango(latino, parole_v, generatori.ModelloParole(parole_v, glifi), random.Random(44))
    with open(messaggio, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(codice) + '\n')
    classi_e23 = e23.compila()
    classi = compila()
    ris = OrderedDict()
    ris['Voynich'] = e22.lista_di_controllo(pagine_voynich(corrente), glifi)
    e22.stampa('Voynich', ris['Voynich'])
    ris['validita'] = {}
    for quota in QUOTE:
        for seme in SEMI:
            pagine, impronta, usate = genera(classi, tabella, messaggio, quota, seme)
            if quota == 0:
                _, impronta_e23 = e23.genera(classi_e23, tabella, FORZA, seme, nome='per_e44_seme_%d' % seme)
                ris['validita']['seme %d' % seme] = {'e44': impronta, 'e23': impronta_e23, 'uguali': impronta == impronta_e23}
                assert impronta == impronta_e23, 'con quota 0 il testo non e\' quello dell\'e23'
            nome = 'm %.2f, seme %d' % (quota, seme)
            r = e22.lista_di_controllo(pagine, glifi)
            r.update({'quota': quota, 'seme': seme, 'parole_del_messaggio': usate,
                      'parole': sum(len(x) for p in pagine for x in p)})
            ris[nome] = r
            e22.stampa(nome, r)
    # medie sui semi e criterio
    medie = OrderedDict()
    chiavi = [k for k, v in ris['m 0.00, seme 19'].items() if isinstance(v, (int, float)) and k not in ('quota', 'seme')]
    for quota in QUOTE:
        gruppo = [ris['m %.2f, seme %d' % (quota, s)] for s in SEMI]
        medie[quota] = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        medie[quota]['compatibile'] = compatibile(medie[quota])
    ris['medie'] = {str(k): v for k, v in medie.items()}
    compatibili = [q for q in QUOTE if medie[q]['compatibile']]
    ris['m_massimo_compatibile'] = max(compatibili) if compatibili else None
    print('m massimo compatibile:', ris['m_massimo_compatibile'])
    with open(os.path.join(RISULTATI, 'e44_messaggio_diluito.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    v = ris['Voynich']
    out = ['# e44 — Un messaggio diluito nel generatore di Timm e Schinner (con le giunture)', '',
           'm = probabilità che un posto di parola vada al messaggio (Plinio, libri 20–27, codice parola per parola '
           'sul vocabolario del Voynich). Medie su tre semi (19, 1, 2); giunture a forza 3. Compatibile = ripetizione '
           '≥ 0,7, somiglianza nella riga ≥ 3% e calante a 6 righe, h2 ≤ 2,40, legame fine–inizio ≥ 0,15. '
           'Validità: con m = 0 il testo è identico a quello dell\'e23 (%s). Preregistrazione: '
           '`preregistrazioni/e44.md`.' % ('sì' if all(x['uguali'] for x in ris['validita'].values()) else 'NO'), '',
           '| testo | parole del messaggio | h2 | spazio | parole uniche | tipi/parole | ripetizione | somigl. riga | 6 righe | confine | compatibile |',
           '|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | — | %.2f | %.0f%% | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | |' % (
               v['h2'], 100 * v['spazio_spiegato'], v['hapax'], v['tipi_su_parole'], v['identiche_vs_riga'],
               100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'])]
    for q, r in medie.items():
        out.append('| m = %.2f | %.0f (%.0f%%) | %.2f | %.0f%% | %.2f | %.3f | %.2f | %.1f%% | %.1f%% | %.3f | %s |' % (
            q, r['parole_del_messaggio'], 100 * r['parole_del_messaggio'] / r['parole'], r['h2'], 100 * r['spazio_spiegato'],
            r['hapax'], r['tipi_su_parole'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'],
            100 * r['somiglianza_6_righe'], r['confine'], 'sì' if r['compatibile'] else 'no'))
    out += ['', 'm massimo compatibile: %s.' % ris['m_massimo_compatibile']]
    with open(os.path.join(RISULTATI, 'e44_messaggio_diluito.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
