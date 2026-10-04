# -*- coding: utf-8 -*-
"""Costruisce in pubblico/voynichizzatore/ il pacchetto da pubblicare (v15 = v14 con la cifratura robusta), a partire
dai sorgenti di questo repo: copia i moduli del generatore a pezzi, estrae dagli esperimenti le poche funzioni che
servono, scrive il testo del Voynich ripulito (trascrizione ZL 3b, pubblico dominio / CC0) in un file di dati, e
aggiunge lo strumento da riga di comando. Il pacchetto non dipende da nient'altro in questo repo.

    .venv/Scripts/python strumenti/costruisci_pubblico.py

Non pubblica niente: prepara solo la cartella. Vedi voynichizzatore/PUBBLICAZIONE.md.
"""
import json, os, re, shutil, sys

RADICE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(RADICE, 'analisi'))
VERSIONE = 'v15'
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


def main():
    if os.path.isdir(USCITA):
        shutil.rmtree(USCITA)
    os.makedirs(USCITA)
    # 1. moduli copiati tali e quali
    for cartella, nome in (('analisi', 'misure.py'), ('voynichizzatore', 'disposizione.py'), ('voynichizzatore', 'sacco.py'), ('voynichizzatore', 'parole_nuove.py'),
                           ('voynichizzatore', 'pezzi.py'), ('voynichizzatore', 'canale_sacco.py'), ('voynichizzatore', 'v0.py'), ('voynichizzatore', 'v1.py'),
                           ('voynichizzatore', 'pezzi_parametri_%s.json' % VERSIONE)):
        scrivi(nome, leggi(cartella, nome))
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
    with open(os.path.join(USCITA, 'voynich_zl3b.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    scrivi('trascrizione.py', TRASCRIZIONE)
    scrivi('voynichizzatore.py', STRUMENTO)
    scrivi('requirements.txt', 'numpy\nscipy\nscikit-learn\n')
    print('pacchetto in %s: %d file, %d righe di testo del Voynich' % (os.path.relpath(USCITA, RADICE), len(os.listdir(USCITA)), len(d['righe'])))


if __name__ == '__main__':
    main()
