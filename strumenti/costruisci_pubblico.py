# -*- coding: utf-8 -*-
"""Costruisce in pubblico/voynichizzatore/ il pacchetto da pubblicare (la versione VERSIONE del registro), a partire
dai sorgenti di questo repo: copia i moduli del generatore a pezzi, estrae dagli esperimenti le poche funzioni che
servono, scrive il testo del Voynich ripulito (trascrizione ZL 3b, pubblico dominio / CC0) in un file di dati, e
aggiunge lo strumento da riga di comando. Il pacchetto non dipende da nient'altro in questo repo.

    .venv/Scripts/python strumenti/costruisci_pubblico.py

Non pubblica niente: prepara solo la cartella. Vedi voynichizzatore/PUBBLICAZIONE.md.
"""
import json, os, re, shutil, sys

RADICE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(RADICE, 'analisi'))
VERSIONE = 'v17'      # v14 + cifratura robusta (v15) + gabbia delle pagine estratta dalle statistiche (e415)
USCITA = os.path.join(RADICE, 'pubblico', 'voynichizzatore')


def leggi(*percorso):
    return open(os.path.join(RADICE, *percorso), encoding='utf-8').read().replace('\r\n', '\n')


def scrivi(nome, testo):
    with open(os.path.join(USCITA, nome), 'w', encoding='utf-8', newline='\n') as f:
        f.write(testo)


def blocco(sorgente, inizio):
    """Il blocco di primo livello che comincia con la riga `inizio` (una def, una classe), fino al prossimo."""
    righe = sorgente.split('\n')
    i = next(k for k, r in enumerate(righe) if r.startswith(inizio))
    j = i + 1
    while j < len(righe) and (righe[j] == '' or righe[j][0] in ' \t#' or righe[j].startswith(')')):
        j += 1
    return '\n'.join(righe[i:j]).rstrip() + '\n'


def dati():
    import trascrizione
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)] if r.parole else []
        if ps:
            out.append([r.pagina, bool(r.inizio_par), ps, r.sezione, r.lingua or '?'])
    return {'fonte': 'Trascrizione ZL (Zandbergen-Landini) del manoscritto Voynich, versione 3b del 13/05/2025, da https://www.voynich.nu/ '
                     '(pubblico dominio, messa a disposizione con licenza Creative Commons CC0). Qui: solo il testo corrente in paragrafi, '
                     'parole senza segni illeggibili, con pagina, inizio di paragrafo, sezione e lingua di Currier.',
            'righe': out}


TRASCRIZIONE = '''# -*- coding: utf-8 -*-
"""Il testo del Voynich usato dal voynichizzatore: lo legge da voynich_zl3b.json (vedi il campo "fonte" del file)."""
import json, os
from collections import namedtuple

Riga = namedtuple('Riga', 'pagina inizio_par parole sezione lingua')
_QUI = os.path.dirname(os.path.abspath(__file__))


def leggi(nome='ZL'):
    d = json.load(open(os.path.join(_QUI, 'voynich_zl3b.json'), encoding='utf-8'))
    return [Riga(p, ini, ps, sez, lin) for p, ini, ps, sez, lin in d['righe']]


def testo_corrente(righe, **filtri):
    return righe


def pulita(parola):
    return '?' not in parola and '*' not in parola
'''

STRUMENTO = '''# -*- coding: utf-8 -*-
"""Voynichizzatore: un testo normale diventa un manoscritto "alla Voynich" (in EVA) con il testo nascosto nella scelta delle
parole di ogni pagina; con la parola chiave il testo torna esatto.

    python voynichizzatore.py codifica testo.txt --chiave PAROLA --uscita manoscritto.txt
    python voynichizzatore.py decodifica manoscritto.txt --chiave PAROLA --uscita testo.txt
    python voynichizzatore.py vuoto --chiave PAROLA --uscita manoscritto.txt      (manoscritto senza messaggio)
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
VERSIONE = '%s'


def main():
    ap = argparse.ArgumentParser(description='Voynichizzatore')
    ap.add_argument('azione', choices=('codifica', 'decodifica', 'vuoto'))
    ap.add_argument('file', nargs='?')
    ap.add_argument('--chiave', required=True)
    ap.add_argument('--uscita')
    a = ap.parse_args()
    import canale_sacco, v0
    if a.azione == 'decodifica':
        try:
            testo = canale_sacco.decodifica(v0.carica(a.file), a.chiave, VERSIONE)
        except Exception as e:
            raise SystemExit('niente da leggere: %%s' %% e)
        if a.uscita:
            open(a.uscita, 'w', encoding='utf-8', newline='\\n').write(testo)
            print('testo scritto in %%s (%%d caratteri)' %% (a.uscita, len(testo)))
        else:
            sys.stdout.reconfigure(encoding='utf-8', newline='\\n')
            sys.stdout.write(testo + '\\n')
        return
    testo = None
    if a.azione == 'codifica':
        testo = open(a.file, encoding='utf-8').read().replace('\\r\\n', '\\n')
    righe, info = canale_sacco.codifica(testo, a.chiave, VERSIONE)
    v0.salva(righe, a.uscita or 'manoscritto.txt')
    print('scritto %%s: %%d righe; messaggio %%d bit su %%d disponibili' %% (a.uscita or 'manoscritto.txt', len(righe), info['bit_messaggio'], info['capacita_bit']))


if __name__ == '__main__':
    main()
''' % VERSIONE


LICENZA = """MIT License

Copyright (c) 2026 Davide Caniatti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

CHIAVE_PROVA = 'prova di rilettura su un altro computer'
TESTO_PROVA = """Questo è il testo di prova del voynichizzatore.

Se stai leggendo queste righe dopo averle tirate fuori da un manoscritto scritto su un altro computer, la rilettura
funziona anche fra macchine diverse: il carattere di ogni pagina, i pesi delle parole e la codifica aritmetica hanno dato
gli stessi numeri qui e là. Il testo contiene lettere accentate (à, è, é, ì, ò, ù), numeri (1404, 1438, 240 fogli) e
qualche segno (—, «», ’), per controllare che torni tutto, byte per byte.

Un erbario, un cielo di stelle, donne in vasche verdi, radici in barattoli: nessuno sa che cosa dica il libro, né se
dica qualcosa.
"""

PROVA = '''# -*- coding: utf-8 -*-
"""Prova di rilettura su un altro computer. Usa: python prova.py
1. rilegge prova/manoscritto_di_prova.txt (scritto sul computer che ha preparato il pacchetto) e lo confronta con
   prova/testo_di_prova.txt;
2. scrive qui un manoscritto nuovo con lo stesso testo e la stessa chiave e lo rilegge;
3. dice se il manoscritto scritto qui coincide con quello incluso (non serve che coincida)."""
import os, platform, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
CHIAVE = %r


def main():
    import canale_sacco, v0, voynichizzatore
    import numpy, scipy, sklearn
    v = voynichizzatore.VERSIONE
    testo = open(os.path.join(QUI, 'prova', 'testo_di_prova.txt'), encoding='utf-8').read()
    print('Python %%s su %%s %%s; numpy %%s, scipy %%s, scikit-learn %%s' %% (platform.python_version(), platform.system(), platform.machine(),
                                                                       numpy.__version__, scipy.__version__, sklearn.__version__))
    incluso = v0.carica(os.path.join(QUI, 'prova', 'manoscritto_di_prova.txt'))
    try:
        uno = canale_sacco.decodifica(incluso, CHIAVE, v) == testo
    except Exception as e:
        uno = False
        print('   errore nella rilettura: %%s' %% e)
    print('1. il manoscritto scritto altrove si rilegge qui: %%s' %% ('SI' if uno else 'NO'))
    print('   (ora scrivo un manoscritto nuovo: un paio di minuti)')
    rifatto, _ = canale_sacco.codifica(testo, CHIAVE, v, verifica=False)
    v0.salva(rifatto, os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt'))
    due = canale_sacco.decodifica(v0.carica(os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt')), CHIAVE, v) == testo
    print('2. un manoscritto scritto qui si rilegge qui: %%s' %% ('SI' if due else 'NO'))
    a = open(os.path.join(QUI, 'prova', 'manoscritto_di_prova.txt'), encoding='utf-8').read()
    b = open(os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt'), encoding='utf-8').read()
    print('3. il manoscritto scritto qui coincide con quello incluso: %%s (non serve che coincida)' %% ('SI' if a == b else 'NO'))


if __name__ == '__main__':
    main()
''' % CHIAVE_PROVA


def prova():
    """Scrive in prova/ il testo, il manoscritto fatto su questo computer con il pacchetto appena costruito, e prova.py."""
    import subprocess
    os.makedirs(os.path.join(USCITA, 'prova'))
    scrivi(os.path.join('prova', 'testo_di_prova.txt'), TESTO_PROVA)
    scrivi('prova.py', PROVA)
    env = dict(os.environ, PYTHONPATH='', PYTHONIOENCODING='utf-8')
    subprocess.run([sys.executable, 'voynichizzatore.py', 'codifica', os.path.join('prova', 'testo_di_prova.txt'), '--chiave', CHIAVE_PROVA,
                    '--uscita', os.path.join('prova', 'manoscritto_di_prova.txt')], cwd=USCITA, env=env, check=True)


LEGGIMI = """# Voynichizzatore

Prende un testo qualsiasi e una parola chiave e scrive un manoscritto "alla Voynich", in EVA (l'alfabeto con cui si
trascrive il manoscritto Voynich, Beinecke MS 408). Con la stessa chiave il testo torna fuori esatto.

    python voynichizzatore.py codifica testo.txt --chiave "una frase lunga" --uscita manoscritto.txt
    python voynichizzatore.py decodifica manoscritto.txt --chiave "una frase lunga" --uscita testo.txt
    python voynichizzatore.py vuoto --chiave "una frase lunga" --uscita manoscritto.txt

Serve Python 3.12 con `numpy`, `scipy` e `scikit-learn` (`pip install -r requirements.txt`). Scrivere un manoscritto
prende un paio di minuti, rileggerlo pochi secondi.

## Che cosa esce

- Un libro intero di 207 pagine e circa 4.200 righe, qualunque sia la lunghezza del testo; una riga del file per riga del
  manoscritto, `<pagina.riga> parole.separate.da.punti`, con `@` davanti alle righe che aprono un paragrafo.
- È testo in EVA, non un'immagine delle pagine.
- Ci stanno circa 80.000 bit, cioè circa 20.000 caratteri di testo dopo la compressione. Se il testo è più lungo il
  programma lo dice. Se è più corto, il resto del libro è riempito in modo che non si veda dove finisce il messaggio.

## Come funziona, in breve

- **Le parole di ogni pagina** vengono dal lessico della sezione del Voynich a cui la pagina corrisponde, con una
  preferenza per certi segni ("carattere" della pagina) presa da un'altra pagina; in più ci sono parole nuove, inventate
  con la forma delle parole che nel Voynich compaiono una volta sola.
- **Il messaggio** (compresso e cifrato con la chiave) decide quante volte compare ogni parola nota in ogni pagina. Non
  c'è corrispondenza fra le parole del manoscritto e quelle del testo: non c'è niente da tradurre parola per parola.
- **La disposizione** delle parole nelle righe segue la forma delle parole (inizio e fine riga, prime righe dei
  paragrafi) e pochi legami deboli fra parole vicine. Non porta informazione: per rileggere il messaggio bastano le
  parole di ogni pagina e la chiave.
- **La gabbia** di ogni pagina (quante righe, quante parole per riga, dove iniziano i paragrafi) è estratta dalle
  statistiche del Voynich: nessuna pagina ha la gabbia di una pagina vera.

## Quanto somiglia al Voynich (misure fatte, con i loro limiti)

Misurato nascondendo lo stesso testo latino con 12 chiavi diverse. I "giudici" sono due classificatori che provano a
distinguere le pagine generate da quelle vere guardando circa 220 statistiche di pagina: 0,5 vuol dire che tirano a
indovinare, 1 che non sbagliano mai.

| misura | valore |
|---|---|
| giudice 1 (statistiche di segni, parole, righe) | 0,56 ± 0,01 |
| giudice 2 (in più: coppie di parole, posizione nella riga, prime righe, profilo della pagina) | 0,60 ± 0,01 |
| pagella a 18 proprietà del testo (17 raggiungibili: una la perde anche il Voynich misurato allo stesso modo) | 15 |
| altre 8 proprietà | circa 6 |
| il testo torna esatto | 12 volte su 12 |
| chiave sbagliata respinta | 12 volte su 12 |

Un manoscritto con un messaggio e uno senza non si distinguono fra loro con queste misure.

**Che cosa NON vuol dire.** Non è "indistinguibile dal Voynich":

- il secondo giudice lo riconosce ancora un po' (circa una chiave su due dà un manoscritto sopra 0,60);
- alcune proprietà note non tornano mai: il profilo di pagina, le scelte di grafia concordi nella riga misurate su 12
  classi, la somiglianza fra parole della stessa riga (un po' troppo alta);
- il modello è stato regolato sulle stesse statistiche che questi giudici guardano; un giudice costruito in modo
  indipendente non è stato provato;
- quasi tutte le parole sono parole del Voynich: chi conosce il programma capisce che il manoscritto è fatto con il
  programma. Quello che non può capire è se dentro c'è un messaggio.

## Sicurezza

- La chiave passa per scrypt, il testo è cifrato con un flusso SHAKE-256 e porta un'etichetta HMAC-SHA256: con la chiave
  sbagliata il programma risponde "chiave errata".
- Sono mattoni standard, ma l'insieme **non è stato verificato da un esperto**: non usarlo per segreti veri. La sicurezza
  dipende dalla chiave: una frase lunga, non una parola del dizionario.
- Scrittura e rilettura usano calcoli in virgola mobile: usa la stessa versione del programma per scrivere e per
  rileggere. La rilettura su un computer diverso da quello che ha scritto il manoscritto non è stata ancora provata.

## Fonti

- **Testo del Voynich** (`voynich_zl3b.json`): dalla trascrizione ZL di René Zandbergen e Gabriel Landini, versione 3b del
  13/05/2025, pubblicata su https://www.voynich.nu/ , dove le trascrizioni sono dichiarate di pubblico dominio e messe a
  disposizione con licenza Creative Commons CC0. Qui c'è solo il testo corrente in paragrafi, con le parole leggibili.
- Il manoscritto è conservato alla Beinecke Rare Book and Manuscript Library dell'Università di Yale (MS 408).

## Licenza

Il programma è sotto licenza MIT (file `LICENSE`). Il testo del Voynich in `voynich_zl3b.json` è di pubblico dominio (CC0).

## Prova di rilettura su un altro computer

    python prova.py

Rilegge il manoscritto di prova incluso (scritto su un altro computer), poi ne scrive uno nuovo e lo rilegge. Alla fine
stampa tre righe con l'esito: se la prima dice "sì", un manoscritto scritto altrove si rilegge anche qui.
"""


def main():
    if os.path.isdir(USCITA):
        shutil.rmtree(USCITA)
    os.makedirs(USCITA)
    # 1. moduli copiati tali e quali
    for cartella, nome in (('analisi', 'misure.py'), ('voynichizzatore', 'disposizione.py'), ('voynichizzatore', 'sacco.py'), ('voynichizzatore', 'parole_nuove.py'),
                           ('voynichizzatore', 'pezzi.py'), ('voynichizzatore', 'canale_sacco.py'), ('voynichizzatore', 'v0.py'), ('voynichizzatore', 'v1.py'),
                           ('voynichizzatore', 'pezzi_parametri_%s.json' % VERSIONE)):
        scrivi(nome, traduci(leggi(cartella, nome)))
    # 2. i pezzi di parola e i legami fra vicine (da e249, e285 e modello.py)
    e249, e285, modello = leggi('esperimenti', 'e249_pezzi_simboli.py'), leggi('esperimenti', 'e285_pezzi_contesto.py'), leggi('voynichizzatore', 'modello.py')
    legami = blocco(modello, 'def legami(')
    legami = re.sub(r' *import e249_pezzi_simboli as e249\n *import e285_pezzi_contesto as e285\n', '', legami)
    legami = legami.replace('e249.segmentatore', 'segmentatore').replace('e285.parti', 'parti_di')
    assert 'e249.' not in legami and 'e285.' not in legami and 'import e2' not in legami
    scrivi('modello.py', '# -*- coding: utf-8 -*-\n"""Pezzi di parola (prefisso, centro, finale) e legami ai bordi fra parole vicine, imparati dal testo del Voynich."""\n'
           'import math\nfrom collections import Counter\n\nimport misure, trascrizione\n\nLESSICO, N_MAX, PENALITA = 150, 4, 2.0\nG = misure.divisore(misure.GLIFI_EVA)\n\n\n'
           + blocco(e249, 'def segmentatore(') + '\n\n' + blocco(e285, 'def parti(').replace('def parti(', 'def parti_di(') + '\n\n_LEG = {}\n\n\n' + legami)
    # 3. le cinque scelte di grafia (da e135 ed e145)
    e135 = leggi('esperimenti', 'e135_stato_riga.py')
    scrivi('e135_stato_riga.py', '# -*- coding: utf-8 -*-\n"""Le scelte di grafia di una parola (ch/sh, k/t, -l/-r, e/ee, qo-/o-, ain/aiin, -dy/-ey)."""\nimport misure, trascrizione\n\n'
           "D = misure.divisore(misure.GLIFI_EVA)\nGALLOWS = {'k', 't', 'p', 'f'}\nBANCHI = {'ch', 'sh', 'k', 't', 'ckh', 'cth'}\n\n\n"
           + blocco(e135, 'def pos_riga(') + '\n\n' + blocco(e135, 'def occorrenze('))
    scrivi('e145_abitudini.py', '# -*- coding: utf-8 -*-\n"""Le cinque scelte usate nel cancello della riga (indici dell\'e135)."""\nSCELTE = (0, 1, 2, 4, 6)\n')
    # 4. il testo del Voynich e chi lo legge
    d = dati()
    d['fonte'] = FONTE
    with open(os.path.join(USCITA, 'voynich_zl3b.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    scrivi('trascrizione.py', TRASCRIZIONE)
    scrivi('voynichizzatore.py', STRUMENTO)
    scrivi('requirements.txt', 'numpy\nscipy\nscikit-learn\n')
    scrivi('README.md', LEGGIMI)
    scrivi('LICENSE', LICENZA)
    scrivi('.gitignore', '__pycache__/\n*.pyc\nprova/manoscritto_rifatto.txt\n')
    prova()
    print('pacchetto in %s: %d file, %d righe di testo del Voynich' % (os.path.relpath(USCITA, RADICE), len(os.listdir(USCITA)), len(d['righe'])))


# i testi per chi usa il pacchetto sono in inglese (richiesta di Davide del 4/10): stanno in pubblico_testi.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pubblico_testi as _T
CHIAVE_PROVA, TESTO_PROVA, FONTE = _T.TEST_KEY, _T.TEST_TEXT, _T.SOURCE
LEGGIMI, STRUMENTO, PROVA = _T.README, _T.TOOL % VERSIONE, _T.TEST % _T.TEST_KEY


def traduci(testo):
    for it, en in _T.MESSAGES:
        testo = testo.replace(it, en)
    return testo


if __name__ == '__main__':
    main()
