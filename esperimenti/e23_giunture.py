# -*- coding: utf-8 -*-
"""Esperimento 23: l'autocitazione di Timm e Schinner con la regola delle giunture.

All'algoritmo di Timm e Schinner (esperimento 22) manca una proprieta' del
Voynich: come comincia una parola dipende da come e' finita la precedente
(0,19 bit di informazione attraverso lo spazio; nel generatore 0,016). Qui gli
si aggiunge una regola sola, eseguibile a mano come le altre: quando nella
riga c'e' gia' una parola, lo scriba accetta la copia ritoccata con
probabilita' min(1, R^forza), dove R dice quanto nel Voynich il suo primo segno
segue piu' (R > 1) o meno (R < 1) del normale l'ultimo segno della parola
precedente (dopo -y volentieri q-, dopo -r volentieri a-, dopo -n quasi mai
k-...). Se la rifiuta, sceglie un'altra parola da copiare, come fa gia' con le
altre regole del generatore. Come tutte le regole del generatore, anche questa
si misura sul Voynich.

Il resto del generatore non cambia: il sorgente Java, al commit fissato in
prepara.py, si compila con la sola aggiunta (analisi/timm_schinner/Giunture.java
e una chiamata nel ciclo principale). Con forza 0 il testo generato e' identico
a quello del programma pubblicato (controllato qui sotto).

Misure: la lista di controllo completa, come nell'esperimento 22. Serve Java.
Scrive risultati/e23_giunture.json e .md; con --grafico il grafico.
"""
import hashlib, json, os, shutil, subprocess, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'giunture')
AGGIUNTA = os.path.join(QUI, '..', 'analisi', 'timm_schinner', 'Giunture.java')
FORZE = (0.0, 1.0, 2.0, 3.0)
SEMI = e22.SEMI
# il vocabolario del generatore resta meno vario di quello del Voynich: si prova se lo cambia
# qualcuno dei suoi parametri (con la regola a forza 3, un seme solo: e' un sondaggio)
VARIANTI = OrderedDict([
    ('suggerimenti al 20% invece del 40%', {'method.suggestions.probability': '20'}),
    ('suggerimenti scelti a caso', {'method.suggestions': 'random'}),
    ('niente suggerimenti', {'method.suggestions': 'none'}),
    ('aggiungi e togli al 40% invece del 20%', {'method.morph.add_remove.probability': '40'}),
    ('unisci e dividi al 50% invece del 30%', {'method.morph.combine_split.probability': '50'}),
    ('parole strane ammesse (errori 5)', {'method.canFollow.error_rate': '5'}),
    ('mai la parola appena scritta come fonte', {'method.morph.reuse_last.probability': '0'}),
])

CHIAMATA = '''                    // regola delle giunture (aggiunta, vedi Giunture.java): la parola nuova
                    // deve attaccarsi bene all'ultima parola della riga
                    if (useMorphedGroups && !forceUsage && glyphGroupList.size() > 0 && Giunture.attiva()) {
                        double p = Giunture.probabilita(glyphGroupList.get(glyphGroupList.size() - 1).glyphGroup,
                                                        firstGroup.glyphGroup);
                        if (config.randomNumberGenerator.rand(1000) >= p * 1000) {
                            useMorphedGroups = false;
                        }
                    }

                    // add modified groups
                    if (useMorphedGroups || forceUsage) {'''


def tabella_giunture(percorso):
    """R(a, b) = P(b | a) / P(b): ultimo segno a di una parola, primo segno b della
    successiva nella stessa riga, nel testo in paragrafi del Voynich."""
    glifi = misure.divisore(misure.GLIFI_EVA)
    coppie, fine, inizio = Counter(), Counter(), Counter()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        for a, b in zip(r.parole, r.parole[1:]):
            if trascrizione.pulita(a) and trascrizione.pulita(b):
                u, v = glifi(a)[-1], glifi(b)[0]
                coppie[u, v] += 1
                fine[u] += 1
                inizio[v] += 1
    tot = sum(coppie.values())
    with open(percorso, 'w', encoding='utf-8') as f:
        for (a, b), c in sorted(coppie.items()):
            f.write('%s\t%s\t%.4f\n' % (a, b, (c / fine[a]) / (inizio[b] / tot)))


def compila():
    """Il sorgente pubblicato, con l'aggiunta, compilato in LAVORO/classi."""
    sorgente = os.path.join(LAVORO, 'java')
    shutil.rmtree(sorgente, ignore_errors=True)
    shutil.copytree(os.path.join(e22.GENERATORE, 'source', 'src', 'main', 'java'), sorgente)
    principale = os.path.join(sorgente, 'de', 'voynich', 'text', 'SelfCitationTextGenerator.java')
    testo = open(principale, encoding='utf-8').read()
    ancora = '''                    // add modified groups
                    if (useMorphedGroups || forceUsage) {'''
    assert testo.count(ancora) == 1
    open(principale, 'w', encoding='utf-8').write(testo.replace(ancora, CHIAMATA))
    shutil.copy(AGGIUNTA, os.path.join(sorgente, 'de', 'voynich', 'text', 'Giunture.java'))
    classi = os.path.join(LAVORO, 'classi')
    shutil.rmtree(classi, ignore_errors=True)
    os.makedirs(classi)
    files = [os.path.join(d, f) for d, _, fs in os.walk(sorgente) for f in fs if f.endswith('.java')]
    subprocess.run(['javac', '-nowarn', '-d', classi] + files, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return classi


def genera(classi, tabella, forza, seme, cambi=None, nome=None):
    cartella = os.path.join(LAVORO, nome or 'forza_%g_seme_%d' % (forza, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read()
    righe = []
    for riga in conf.splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        elif cambi and riga.split('=')[0] in cambi:
            riga = riga.split('=')[0] + '=' + cambi[riga.split('=')[0]]
        righe.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % forza, '-cp', classi,
                    'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    pagine = [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]
    return pagine, hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def main():
    os.makedirs(LAVORO, exist_ok=True)
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    tabella_giunture(tabella)
    classi = compila()
    glifi = misure.divisore(misure.GLIFI_EVA)
    ris = OrderedDict()
    ris['Voynich'] = e22.lista_di_controllo(pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL'))), glifi)
    e22.stampa('Voynich', ris['Voynich'])
    for forza in FORZE:
        for seme in SEMI:
            pagine, impronta = genera(classi, tabella, forza, seme)
            if forza == 0:
                # senza la regola, il testo deve essere quello del programma pubblicato (esperimento 22)
                originale, impronta_originale = e22_testo(seme)
                assert impronta == impronta_originale, 'con forza 0 il testo non e\' quello originale'
            nome = 'forza %g, seme %d' % (forza, seme)
            ris[nome] = e22.lista_di_controllo(pagine, glifi)
            ris[nome]['forza'] = forza
            ris[nome]['esempio'] = [' '.join(r) for r in pagine[10][:4]]
            e22.stampa(nome, ris[nome])
    varianti(ris, classi, tabella)
    with open(os.path.join(RISULTATI, 'e23_giunture.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def varianti(ris, classi, tabella):
    glifi = misure.divisore(misure.GLIFI_EVA)
    for nome, cambi in VARIANTI.items():
        pagine, _ = genera(classi, tabella, 3.0, SEMI[0], cambi, 'variante_' + str(list(VARIANTI).index(nome)))
        ris['variante: ' + nome] = e22.lista_di_controllo(pagine, glifi)
        ris['variante: ' + nome]['forza'] = None
        e22.stampa(nome[:28], ris['variante: ' + nome])


def e22_testo(seme):
    """Il testo del programma pubblicato (jar), per il confronto con forza 0."""
    e22.genera(seme)
    percorso = os.path.join(e22.LAVORO, 'seme_%d' % seme, 'generate', 'generated_text.txt')
    corpo = [l for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    return corpo, hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def scrivi_tabella(ris):
    v = ris['Voynich']
    out = ['# Esperimento 23: l\'autocitazione con la regola delle giunture', '',
           'Il generatore di Timm e Schinner (parametri pubblicati, %d semi per forza, %d righe) con una regola in '
           'più: la parola nuova si accetta con probabilità min(1, R^forza), dove R dice quanto nel Voynich il suo '
           'primo segno segue l\'ultimo segno della parola precedente. Forza 0 = il programma originale.' % (
               len(SEMI), e22.RIGHE), '',
           '| proprietà | Voynich | ' + ' | '.join('forza %g' % f for f in FORZE) + ' | testi naturali |',
           '|---|---|' + '---|' * len(FORZE) + '---|']
    for k, nome, fmt, nat in e22.PROPRIETA:
        celle = []
        for forza in FORZE:
            valori = [x[k] for n, x in ris.items() if n != 'Voynich' and x.get('forza') == forza]
            celle.append('%s (%s – %s)' % (e22.formato(k, fmt, sum(valori) / len(valori)),
                                           e22.formato(k, fmt, min(valori)), e22.formato(k, fmt, max(valori))))
        out.append('| %s | %s | %s | %s |' % (nome, e22.formato(k, fmt, v[k]), ' | '.join(celle), nat))
    virgola = lambda x: ('%.2f' % x).replace('.', ',')
    rapporti = []
    for forza in FORZE:
        xs = [x for n, x in ris.items() if n != 'Voynich' and x.get('forza') == forza]
        rapporti.append('forza %g: %s' % (forza, virgola(sum(x['unione_attestata'] / x['unione_caso'] for x in xs)
                                                          / len(xs))))
    out += ['', 'Parole vicine unite che esistono, rispetto al caso: Voynich %s; %s.' % (
        virgola(v['unione_attestata'] / v['unione_caso']), '; '.join(rapporti)), '']
    var = [(n[len('variante: '):], x) for n, x in ris.items() if n.startswith('variante: ')]
    if var:
        base = ris['forza 3, seme %d' % SEMI[0]]
        out += ['## Il vocabolario: cambia con i parametri del generatore?', '',
                'Con la regola a forza 3 e il seme %d, cambiando un parametro alla volta. Un sondaggio: un seme solo.'
                % SEMI[0], '',
                '| variante | parole diverse | hapax | h2 | ripetute | somiglianza nella riga | legame fine-inizio |',
                '|---|---|---|---|---|---|---|']
        for nome, x in [('parametri pubblicati', base)] + var:
            out.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                nome, e22.formato('tipi_su_parole', '%.0f%%', x['tipi_su_parole']),
                e22.formato('hapax', '%.0f%%', x['hapax']), e22.formato('h2', '%.2f', x['h2']),
                e22.formato('identiche_vs_riga', '×%.2f', x['identiche_vs_riga']),
                e22.formato('somiglianza_riga', '%.1f%%', x['somiglianza_riga']),
                e22.formato('confine', '%.3f', x['confine'])))
        out += ['', 'Nel Voynich: parole diverse 21%, hapax 68%.', '']
    for forza in FORZE[1:]:
        x = ris['forza %g, seme %d' % (forza, SEMI[0])]
        out += ['## Un pezzo di testo generato con forza %g (seme %d, pagina 11)' % (forza, SEMI[0]), '', '```'] + \
            x['esempio'] + ['```', '']
    with open(os.path.join(RISULTATI, 'e23_giunture.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    """Come il grafico dell'esperimento 22: ogni proprieta' da 0 (lingua tipica) a 1
    (Voynich), la media sui semi per ogni forza della regola."""
    import grafici
    v = ris['Voynich']
    chiavi = list(e22.TIPICO)
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=4.9)
        fig.subplots_adjust(left=0.27, right=0.97, top=0.80, bottom=0.14)
        for x, etichetta in ((0, 'lingua tipica'), (1, 'Voynich')):
            ax.axvline(x, color=t['muto'], linewidth=1.2, zorder=1)
            ax.text(x, -0.85, etichetta, ha='center', va='bottom', fontsize=8, color=t['secondario'])
        for n, forza in enumerate(FORZE):
            xs = []
            for k in chiavi:
                vals = [e22.scala(x, v, k) for nome, x in ris.items() if nome != 'Voynich' and x.get('forza') == forza]
                xs.append(sum(vals) / len(vals))
            if forza == 0:
                stile = dict(color=t['contesto'], label='generatore originale')
            else:
                stile = dict(color=t['accento'], alpha=0.35 + 0.65 * forza / max(FORZE),
                             label='giunture, forza %g' % forza)
            ax.scatter(xs, range(len(chiavi)), s=42, edgecolor=t['sfondo'], linewidth=0.8, zorder=2 + n,
                       marker='o' if forza == 0 else 'D', **stile)
        ax.set_yticks(range(len(chiavi)))
        ax.set_yticklabels([e22.TIPICO[k][0] for k in chiavi], fontsize=8.5)
        ax.set_ylim(len(chiavi) - 0.4, -1.1)
        ax.set_xlim(-1.0, 2.0)
        ax.set_xlabel('0 = il valore tipico delle lingue, 1 = il valore del Voynich (media su %d semi)' % len(SEMI))
        ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.93), frameon=False, fontsize=7.5,
                  labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, TITOLO, SOTTOTITOLO)
        grafici.salva(fig, RISULTATI, 'e23_giunture', tema)


TITOLO = 'Con la regola delle giunture il legame fra parole compare'
SOTTOTITOLO = ('Lo stesso generatore, con una regola in più: la parola nuova deve attaccarsi bene alla precedente.\n'
               'Il legame fra parole vicine sale fino al Voynich; le altre proprietà restano più o meno dove erano.')


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e23_giunture.json'), encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
