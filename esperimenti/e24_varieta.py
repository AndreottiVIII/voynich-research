# -*- coding: utf-8 -*-
"""Esperimento 24: un vocabolario piu' vario per l'autocitazione.

Con la regola delle giunture (esperimento 23) al generatore di Timm e Schinner
manca soprattutto la varieta' del vocabolario: le parole usate una volta sola
sono il 51%, nel Voynich il 68%, e i parametri del generatore non la cambiano.
Qui due regole in piu', eseguibili a mano come le altre
(analisi/timm_schinner/Varieta.java):

- doppio ritocco: con una certa probabilita' lo scriba ritocca una seconda
  volta la copia appena ritoccata;
- copia da lontano: con una certa probabilita' la parola da copiare viene da
  una riga qualsiasi delle pagine gia' finite, invece che dalla pagina in corso.

Prima un sondaggio su un seme, su una griglia di probabilita', con le giunture
a forza 3; poi la combinazione che si avvicina di piu' al Voynich, su cinque
semi. Con le probabilita' a zero il testo e' identico a quello
dell'esperimento 23 (controllato qui sotto). Serve Java.

Scrive risultati/e24_varieta.json e .md; con --grafico il grafico.
"""
import hashlib, json, os, re, shutil, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'varieta')
AGGIUNTE = os.path.join(QUI, '..', 'analisi', 'timm_schinner')
FORZA = 3.0
DOPPIO = (0, 30, 60, 90)
LONTANO = (0, 10, 25)

SCELTA = '''            List<GlyphGroup> sourceGroups = Varieta.daLontano(lineArrays, config.statistics.linesInPage,
                                                              config.randomNumberGenerator);
            if (sourceGroups == null) {
                sourceGroups = config.sourceGroupChooser.chooseSourceGroup(lineArrays, paragraphInitialLineArrays, glyphGroupList, config.statistics, isParagraphInitial, isLineInitial, initialLineCount);
            }'''
RITOCCO = '''                List<GlyphGroup> morphedGroups = config.groupMorpher.morphGroup(sourceGroups, lastGeneratedGroup, isParagraphInitial, isLineInitial);
                // doppio ritocco (aggiunta, vedi Varieta.java)
                if (morphedGroups.size() == 1 && Varieta.doppio(config.randomNumberGenerator)) {
                    List<GlyphGroup> seconda = config.groupMorpher.morphGroup(
                            new ArrayList<>(Arrays.asList(morphedGroups.get(0),
                                    sourceGroups.size() > 1 ? sourceGroups.get(1) : morphedGroups.get(0))),
                            lastGeneratedGroup, isParagraphInitial, isLineInitial);
                    if (seconda.size() > 0) {
                        morphedGroups = seconda;
                    }
                }'''


def compila():
    sorgente = os.path.join(LAVORO, 'java')
    shutil.rmtree(sorgente, ignore_errors=True)
    shutil.copytree(os.path.join(e22.GENERATORE, 'source', 'src', 'main', 'java'), sorgente)
    principale = os.path.join(sorgente, 'de', 'voynich', 'text', 'SelfCitationTextGenerator.java')
    testo = open(principale, encoding='utf-8').read()
    ancora = '''                    // add modified groups
                    if (useMorphedGroups || forceUsage) {'''
    assert testo.count(ancora) == 1
    testo = testo.replace(ancora, e23.CHIAMATA)
    scelta = re.search(r'^ {12}List<GlyphGroup> sourceGroups = config\.sourceGroupChooser\.chooseSourceGroup\(.*$',
                       testo, re.M)
    testo = testo[:scelta.start()] + SCELTA + testo[scelta.end():]
    ritocco = ('                List<GlyphGroup> morphedGroups = config.groupMorpher.morphGroup(sourceGroups, '
               'lastGeneratedGroup, isParagraphInitial, isLineInitial);')
    assert testo.count(ritocco) == 1
    testo = testo.replace(ritocco, RITOCCO)
    testo = testo.replace('import de.voynich.text.util.*;',
                          'import de.voynich.text.util.*;\nimport de.voynich.text.sourcechooser.Varieta;', 1)
    open(principale, 'w', encoding='utf-8').write(testo)
    shutil.copy(os.path.join(AGGIUNTE, 'Giunture.java'), os.path.join(sorgente, 'de', 'voynich', 'text'))
    shutil.copy(os.path.join(AGGIUNTE, 'Varieta.java'), os.path.join(sorgente, 'de', 'voynich', 'text', 'sourcechooser'))
    classi = os.path.join(LAVORO, 'classi')
    shutil.rmtree(classi, ignore_errors=True)
    os.makedirs(classi)
    files = [os.path.join(d, f) for d, _, fs in os.walk(sorgente) for f in fs if f.endswith('.java')]
    subprocess.run(['javac', '-nowarn', '-d', classi] + files, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return classi


def genera(classi, tabella, seme, doppio, lontano, forza=FORZA):
    cartella = os.path.join(LAVORO, 'd%d_l%d_f%g_s%d' % (doppio, lontano, forza, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    righe = []
    for riga in open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read().splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        righe.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % forza,
                    '-Dvarieta.doppio=%d' % doppio, '-Dvarieta.lontano=%d' % lontano,
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    return ([linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)],
            hashlib.md5('\n'.join(corpo).encode()).hexdigest())


def distanza(r, v):
    """Quanto un testo e' lontano dal Voynich: media degli scarti sulla scala da lingua
    tipica (0) a Voynich (1) per le proprieta' anomale, piu' lo scarto relativo di
    parole diverse e hapax."""
    scarti = [abs(e22.scala(r, v, k) - 1) for k in e22.TIPICO]
    scarti += [abs(r[k] - v[k]) / v[k] for k in ('tipi_su_parole', 'hapax')]
    return sum(scarti) / len(scarti)


def main():
    os.makedirs(LAVORO, exist_ok=True)
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = compila()
    glifi = misure.divisore(misure.GLIFI_EVA)
    ris = OrderedDict()
    v = ris['Voynich'] = e22.lista_di_controllo(pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi('ZL'))), glifi)
    # controllo: senza le regole nuove il testo e' quello dell'esperimento 23 (giunture a forza 3)
    _, impronta = genera(classi, tabella, e22.SEMI[0], 0, 0)
    _, impronta23 = e23.genera(e23.compila(), tabella, FORZA, e22.SEMI[0])
    assert impronta == impronta23, 'senza le regole nuove il testo non e\' quello dell\'esperimento 23'
    # sondaggio su un seme
    for d in DOPPIO:
        for l in LONTANO:
            pagine, _ = genera(classi, tabella, e22.SEMI[0], d, l)
            nome = 'sondaggio: doppio ritocco %d%%, copia da lontano %d%%' % (d, l)
            ris[nome] = e22.lista_di_controllo(pagine, glifi)
            ris[nome].update(doppio=d, lontano=l, distanza=distanza(ris[nome], v))
            e22.stampa('d%d l%d dist %.3f' % (d, l, ris[nome]['distanza']), ris[nome])
    sondaggi = [x for n, x in ris.items() if n.startswith('sondaggio')]
    migliore = min(sondaggi, key=lambda x: x['distanza'])
    d, l = migliore['doppio'], migliore['lontano']
    for seme in e22.SEMI:
        pagine, _ = genera(classi, tabella, seme, d, l)
        nome = 'scelta: doppio ritocco %d%%, copia da lontano %d%%, seme %d' % (d, l, seme)
        ris[nome] = e22.lista_di_controllo(pagine, glifi)
        ris[nome].update(doppio=d, lontano=l, seme=seme, distanza=distanza(ris[nome], v))
        ris[nome]['esempio'] = [' '.join(r) for r in pagine[10][:4]]
        e22.stampa('scelta seme %d' % seme, ris[nome])
    with open(os.path.join(RISULTATI, 'e24_varieta.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    v = ris['Voynich']
    son = [(n, x) for n, x in ris.items() if n.startswith('sondaggio')]
    sce = [x for n, x in ris.items() if n.startswith('scelta')]
    f = lambda k, fmt, x: e22.formato(k, fmt, x)
    out = ['# Esperimento 24: un vocabolario più vario per l\'autocitazione', '',
           'Il generatore di Timm e Schinner con la regola delle giunture a forza %g e due regole in più: doppio '
           'ritocco (la copia si ritocca una seconda volta) e copia da lontano (la parola si copia dalle pagine già '
           'finite). **Distanza**: media degli scarti dal Voynich, sulla scala da lingua tipica (0) a Voynich (1) per '
           'le proprietà anomale e in proporzione per parole diverse e hapax; 0 = uguale al Voynich.' % FORZA, '',
           '## Sondaggio su un seme (%d)' % e22.SEMI[0], '',
           '| doppio ritocco | copia da lontano | distanza | diverse | hapax | ripetute | somiglianza riga / 6 righe | '
           'legame | spazio | h2 |', '|---|---|---|---|---|---|---|---|---|---|']
    for n, x in son:
        out.append('| %d%% | %d%% | %.3f | %s | %s | %s | %s / %s | %s | %s | %s |' % (
            x['doppio'], x['lontano'], x['distanza'], f('tipi_su_parole', '%.0f%%', x['tipi_su_parole']),
            f('hapax', '%.0f%%', x['hapax']), f('identiche_vs_riga', '×%.2f', x['identiche_vs_riga']),
            f('somiglianza_riga', '%.1f%%', x['somiglianza_riga']),
            f('somiglianza_6_righe', '%.1f%%', x['somiglianza_6_righe']), f('confine', '%.3f', x['confine']),
            f('spazio_spiegato', '%.0f%%', x['spazio_spiegato']), f('h2', '%.2f', x['h2'])))
    if sce:
        out += ['', '## La combinazione più vicina (doppio ritocco %d%%, copia da lontano %d%%), su %d semi' % (
            sce[0]['doppio'], sce[0]['lontano'], len(sce)), '',
            '| proprietà | Voynich | generatore (media e intervallo) | testi naturali |', '|---|---|---|---|']
        for k, nome, fmt, nat in e22.PROPRIETA:
            valori = [x[k] for x in sce]
            out.append('| %s | %s | %s (%s – %s) | %s |' % (
                nome, f(k, fmt, v[k]), f(k, fmt, sum(valori) / len(valori)), f(k, fmt, min(valori)),
                f(k, fmt, max(valori)), nat))
        out += ['', 'Parole vicine unite che esistono, rispetto al caso: Voynich %s, generatore %s.' % (
            ('%.2f' % (v['unione_attestata'] / v['unione_caso'])).replace('.', ','),
            ('%.2f' % (sum(x['unione_attestata'] / x['unione_caso'] for x in sce) / len(sce))).replace('.', ',')),
            '', '## Un pezzo di testo generato (seme %d, pagina 11)' % sce[0]['seme'], '', '```'] + \
            sce[0]['esempio'] + ['```']
    with open(os.path.join(RISULTATI, 'e24_varieta.md'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')


def disegna(ris):
    """Parole usate una volta sola contro somiglianza nella riga: ogni punto del
    sondaggio, il generatore senza le regole nuove e il Voynich."""
    import grafici
    v = ris['Voynich']
    son = [x for n, x in ris.items() if n.startswith('sondaggio')]
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.13)
        for x in son:
            base = x['doppio'] == 0 and x['lontano'] == 0
            ax.scatter([100 * x['hapax']], [100 * x['somiglianza_riga']], s=24 + x['doppio'] * 0.9,
                       color=t['contesto'] if base else t['accento'], alpha=1.0 if base else 0.35 + 0.65 * (
                           1 - x['lontano'] / max(LONTANO)), edgecolor=t['sfondo'], linewidth=0.8, zorder=3)
        ax.scatter([100 * v['hapax']], [100 * v['somiglianza_riga']], s=90, marker='*', color=t['inchiostro'],
                   zorder=4)
        ax.annotate('Voynich', (100 * v['hapax'], 100 * v['somiglianza_riga']), xytext=(-12, 8),
                    textcoords='offset points', fontsize=9, color=t['inchiostro'], ha='right')
        for x in son:
            testo = None
            if x['doppio'] == 0 and x['lontano'] == 0:
                testo = 'generatore con le giunture'
            elif x['lontano'] == 0 and x['doppio'] in (30, 90):
                testo = 'doppio ritocco %d%%' % x['doppio']
            elif x['doppio'] == 0 and x['lontano'] == max(LONTANO):
                testo = 'copia da lontano %d%%' % x['lontano']
            if testo:
                ax.annotate(testo, (100 * x['hapax'], 100 * x['somiglianza_riga']), xytext=(8, -3),
                            textcoords='offset points', fontsize=8, color=t['secondario'])
        ax.set_xlim(45, 72)
        ax.set_ylim(0, 4.6)
        ax.set_xlabel('parole usate una volta sola (%)')
        ax.set_ylabel('somiglianza fra parole della stessa riga (%)')
        grafici.titoli(fig, ax, t, 'Più parole nuove, meno somiglianza: il Voynich ha tutte e due',
                       'Il generatore con due regole in più, in dosi diverse (punti più grandi: più doppi ritocchi;\n'
                       'più chiari: più copie da lontano). Nessuna combinazione arriva dove sta il Voynich.')
        grafici.salva(fig, RISULTATI, 'e24_varieta', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e24_varieta.json'), encoding='utf-8') as fh:
            ris = json.load(fh, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
