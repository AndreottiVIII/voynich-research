# -*- coding: utf-8 -*-
"""Esperimento 22: l'algoritmo completo di Timm e Schinner alla prova.

Timm e Schinner (2020, Cryptologia 44(1), doi:10.1080/01611194.2019.1596999)
propongono che il Voynich sia stato scritto senza un messaggio, con un
procedimento che uno scriba del Quattrocento poteva seguire a mano
("autocitazione"): ogni parola e' la copia di una parola gia' scritta, di
solito nella stessa pagina e spesso nella stessa posizione di una riga sopra,
ritoccata sostituendo segni simili, aggiungendo o togliendo pezzi, unendo o
dividendo parole. Il loro generatore (Java, licenza MIT,
github.com/TorstenTimm/SelfCitationTextgenerator) si usa qui cosi' com'e',
con i parametri pubblicati (conf.properties del repository); cambiano solo la
lunghezza, 4000 righe come il testo in paragrafi del Voynich, e il seme del
generatore casuale, per vedere quanto variano i risultati.

Misure: tutte quelle della lista di controllo, piu' quelle dell'esperimento
18 (ordine dei segni, anagrammi). Il Voynich si misura allo stesso modo, sulle
sue righe e pagine vere; il testo generato ha pagine da 29 righe.

Serve Java. Scrive risultati/e22_timm_schinner.json e .md; con --grafico il
grafico.
"""
import json, os, random, shutil, subprocess, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e18_anagrammi as e18
from e07_codifiche import impronta, pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
GENERATORE = os.path.join(lingue.SORGENTI, 'SelfCitationTextgenerator')
LAVORO = os.path.join(QUI, '..', 'dati', 'cache', 'timm_schinner')
SEMI = (19, 1, 2, 3, 4)          # 19 e' il seme dei parametri pubblicati
RIGHE = 4000
RIGHE_PAGINA = 29                 # text.lines_per_page dei parametri pubblicati


def genera(seme, righe=RIGHE):
    """Fa girare il generatore originale; restituisce le pagine (liste di righe di parole)."""
    cartella = os.path.join(LAVORO, 'seme_%d' % seme)
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read().splitlines()
    nuova = []
    for riga in conf:
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % righe
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        nuova.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(nuova) + '\n')
    jar = os.path.join(GENERATORE, 'executable', 'text-generator.jar')
    subprocess.run(['java', '-jar', os.path.abspath(jar)], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    linee = [l.split() for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    return [linee[i:i + RIGHE_PAGINA] for i in range(0, len(linee), RIGHE_PAGINA)]


def lista_di_controllo(pagine, dividi):
    righe = [r for p in pagine for r in p]
    r = impronta(pagine, dividi)
    r['spazio_spiegato'] = misure.spazi(righe, dividi)['spiegata']
    r['confine'] = misure.confine(righe, dividi, solo_interne=True)['im_confine_eccesso']
    # due parole vicine unite danno una parola che il testo usa altrove? (esperimento 12)
    vocabolario = Counter(p for rr in righe for p in rr)
    coppie = [(a, b) for rr in righe for a, b in zip(rr, rr[1:])]
    prime = [a for a, _ in coppie]
    rnd = random.Random(12)
    r['unione_attestata'] = sum(1 for a, b in coppie if vocabolario[a + b]) / len(coppie)
    r['unione_caso'] = sum(1 for a, b in coppie if vocabolario[rnd.choice(prime) + b]) / len(coppie)
    # ordine dei segni e anagrammi (esperimento 18), sulle prime 35.000 parole
    parole = [dividi(p) if dividi else list(p) for rr in righe for p in rr][:e18.PAROLE]
    r['ordine_rispettato'] = e18.ordine_migliore(e18.coppie(parole), random.Random(18))[0]
    r['anagrammi'] = e18.anagrammi(parole)
    return r


# le proprieta' della lista di controllo, con i valori dei testi naturali dal rapporto
PROPRIETA = [
    ('h2', 'incertezza sul segno successivo (h2, bit)', '%.2f', '2,6–3,3 a parità di alfabeto'),
    ('spazio_spiegato', 'spazio prevedibile dal segno precedente', '%.0f%%', '6–100%, mediana 17%'),
    ('tipi_su_parole', 'parole diverse ogni 30.000', '%.0f%%', '3–33%'),
    ('hapax', 'parole usate una volta sola (hapax)', '%.0f%%', '12–72%'),
    ('identiche_vs_riga', 'parola identica alla precedente, rispetto alla riga', '×%.2f', '×0,01–1,9, mediana ×0,12'),
    ('somiglianza_riga', 'somiglianza fra parole della stessa riga', '%.1f%%', 'da −0,4% a 1,5%'),
    ('somiglianza_6_righe', 'la stessa somiglianza a 6 righe di distanza', '%.1f%%', 'vicino a 0'),
    ('confine', 'legame fine parola → inizio parola seguente (bit)', '%.3f', '0,02–0,40, mediana 0,07'),
    ('unione_attestata', 'due parole vicine unite danno una parola esistente', '%.1f%%', '0,1–0,7%, pari al caso'),
    ('lung_media', 'lunghezza delle parole (segni)', '%.2f', ''),
    ('ordine_rispettato', 'coppie di segni nell\'ordine migliore', '%.1f%%', '60–96%, mediana 66%'),
    ('anagrammi', 'parole con un anagramma nel testo', '%.1f%%', '1–27%, mediana 5%'),
]
PERCENTUALI = {'spazio_spiegato', 'tipi_su_parole', 'hapax', 'somiglianza_riga', 'somiglianza_6_righe',
               'unione_attestata', 'ordine_rispettato', 'anagrammi'}


def formato(k, fmt, x):
    return (fmt % (100 * x if k in PERCENTUALI else x)).replace('.', ',')


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    ris = OrderedDict()
    ris['Voynich'] = lista_di_controllo(pagine_voynich(corrente), glifi)
    stampa('Voynich', ris['Voynich'])
    naibbe = os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
    ris['Naibbe (Plinio cifrato da Greshko)'] = lista_di_controllo(
        misure.pagine_finte(open(naibbe, encoding='utf-8').read().split()), glifi)
    stampa('Naibbe', ris['Naibbe (Plinio cifrato da Greshko)'])
    for seme in SEMI:
        pagine = genera(seme)
        nome = 'Timm e Schinner, seme %d' % seme
        ris[nome] = lista_di_controllo(pagine, glifi)
        ris[nome]['parole'] = sum(len(r) for p in pagine for r in p)
        ris[nome]['esempio'] = [' '.join(r) for r in pagine[10][:4]]
        stampa(nome, ris[nome])
    with open(os.path.join(RISULTATI, 'e22_timm_schinner.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, r):
    print('%-28s ' % nome + '  '.join('%s %s' % (k[:10], formato(k, fmt, r[k])) for k, _, fmt, _ in PROPRIETA),
          flush=True)


def scrivi_tabella(ris):
    gen = [v for k, v in ris.items() if k.startswith('Timm')]
    v = ris['Voynich']
    nai = ris['Naibbe (Plinio cifrato da Greshko)']
    out = ['# Esperimento 22: l\'algoritmo completo di Timm e Schinner', '',
           'Il generatore originale (github.com/TorstenTimm/SelfCitationTextgenerator, commit a6ede22) con i '
           'parametri pubblicati, %d semi, %d righe ciascuno (circa %s parole). Il Voynich misurato allo stesso '
           'modo, sulle righe e pagine vere del testo in paragrafi (trascrizione ZL, segni composti fusi).' % (
               len(gen), RIGHE, '{:,}'.format(int(round(sum(g['parole'] for g in gen) / len(gen), -2))).replace(',', '.')),
           '',
           '| proprietà | Voynich | generatore (media e intervallo sui semi) | Naibbe | testi naturali |',
           '|---|---|---|---|---|']
    for k, nome, fmt, nat in PROPRIETA:
        valori = [g[k] for g in gen]
        media = sum(valori) / len(valori)
        out.append('| %s | %s | %s (%s – %s) | %s | %s |' % (
            nome, formato(k, fmt, v[k]), formato(k, fmt, media), formato(k, fmt, min(valori)),
            formato(k, fmt, max(valori)), formato(k, fmt, nai[k]), nat))
    out += ['', 'Unione attestata per caso (la stessa seconda parola dopo una prima parola qualsiasi): Voynich %s, '
            'generatore %s.' % (formato('unione_attestata', '%.1f%%', v['unione_caso']),
                                formato('unione_attestata', '%.1f%%',
                                        sum(g['unione_caso'] for g in gen) / len(gen))), '',
            '## Un pezzo di testo generato (seme %d, pagina 11)' % SEMI[0], '', '```'] + gen[0]['esempio'] + ['```']
    with open(os.path.join(RISULTATI, 'e22_timm_schinner.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


# per il grafico: il valore tipico delle lingue (mediana dei testi naturali, dagli esperimenti 1, 9, 11, 12
# e 18), cosi' ogni proprieta' si mette su una scala da 0 (lingua tipica) a 1 (Voynich). Le parole vicine
# unite si contano rispetto al caso (attestate / attestate con una prima parola qualsiasi): nelle lingue
# dell'esperimento 12 il rapporto va da 0,2 a 1,0, mediana circa 0,54
TIPICO = OrderedDict([
    ('h2', ('prevedibilità del segno (h2)', 3.106)),
    ('spazio_spiegato', ('spazio prevedibile', 0.1667)),
    ('identiche_vs_riga', ('ripetizioni immediate', 0.122)),
    ('somiglianza_riga', ('somiglianza nella riga', 0.0021)),
    ('somiglianza_6_righe', ('somiglianza a 6 righe', 0.0)),
    ('unione_sul_caso', ('parole vicine unite esistenti,\nrispetto al caso', 0.54)),
    ('anagrammi', ('anagrammi', 0.053)),
    ('confine', ('legame fine-inizio parola', 0.071)),
])


def scala(r, v, k):
    valore = lambda x: x['unione_attestata'] / x['unione_caso'] if k == 'unione_sul_caso' else x[k]
    return (valore(r) - TIPICO[k][1]) / (valore(v) - TIPICO[k][1])


def disegna(ris):
    import grafici
    v = ris['Voynich']
    gen = [x for k, x in ris.items() if k.startswith('Timm')]
    nai = ris['Naibbe (Plinio cifrato da Greshko)']
    chiavi = list(TIPICO)
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=4.9)
        fig.subplots_adjust(left=0.27, right=0.97, top=0.80, bottom=0.14)
        for x, etichetta in ((0, 'lingua tipica'), (1, 'Voynich')):
            ax.axvline(x, color=t['muto'], linewidth=1.2, zorder=1)
            ax.text(x, -0.85, etichetta, ha='center', va='bottom', fontsize=8, color=t['secondario'])
        for i, k in enumerate(chiavi):
            ax.scatter([scala(nai, v, k)], [i], s=36, color=t['contesto'], edgecolor=t['sfondo'], linewidth=0.8,
                       label='Naibbe (Plinio cifrato)' if i == 0 else None, zorder=2)
            ax.scatter([scala(g, v, k) for g in gen], [i] * len(gen), s=30, color=t['accento'],
                       edgecolor=t['sfondo'], linewidth=0.8,
                       label='Timm e Schinner (%d semi)' % len(gen) if i == 0 else None, zorder=3)
        ax.set_yticks(range(len(chiavi)))
        ax.set_yticklabels([TIPICO[k][0] for k in chiavi], fontsize=8.5)
        ax.set_ylim(len(chiavi) - 0.4, -1.1)
        ax.set_xlim(-1.0, 2.0)
        ax.set_xlabel('0 = il valore tipico delle lingue, 1 = il valore del Voynich')
        ax.legend(loc='lower right', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Il generatore di Timm e Schinner rifà gran parte del Voynich',
                       'Ogni proprietà della lista di controllo su una scala da 0 (una lingua tipica) a 1 (il Voynich).\n'
                       'Il generatore arriva al Voynich o gli si avvicina quasi ovunque; il legame fra parole vicine gli manca.')
        grafici.salva(fig, RISULTATI, 'e22_timm_schinner', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e22_timm_schinner.json'), encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
