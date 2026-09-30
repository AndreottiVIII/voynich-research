# -*- coding: utf-8 -*-
"""Legge le trascrizioni del manoscritto Voynich nel formato IVTFF di voynich.nu.

Ogni riga del manoscritto diventa una Riga con i suoi metadati (pagina, tipo di
testo, sezione illustrata, lingua A/B di Currier, mano) e la lista delle parole.
Le parole sono stringhe nell'alfabeto della trascrizione: EVA per ZL e
Takahashi, v101 per Glen Claston.

Scelte di pulizia, tutte documentate perche' cambiano i numeri:
- le letture incerte [a:b] prendono la prima opzione, che per convenzione e'
  la piu' probabile;
- le legature {..} perdono le graffe, e l'apostrofo dell'EVA esteso sparisce;
- i glifi rari @nnn; diventano '*', i caratteri illeggibili restano '?': le
  parole che li contengono sono segnate come sporche e le analisi le scartano;
- l'interruzione per un disegno <-> e il disallineamento <~> separano parole
  (nella ZL non stanno mai attaccati a un punto, quindi fanno da spazio);
- la virgola, lo spazio incerto, per default e' uno spazio: con
  virgola_spazio=False le due meta' restano unite.
"""
import os, re
from collections import namedtuple

QUI = os.path.dirname(os.path.abspath(__file__))
CARTELLA = os.path.join(QUI, '..', 'dati', 'trascrizioni')

FILE = {
    'ZL': 'ZL3b-n.txt',   # Zandbergen-Landini, EVA, la piu' completa
    'IT': 'IT2a-n.txt',   # Takahashi, EVA di base
    'GC': 'GC2a-n.txt',   # Glen Claston, alfabeto v101
}

# Tipi di testo (prima lettera del tipo di locus)
PARAGRAFO, ETICHETTA, CERCHIO, RAGGIO = 'P', 'L', 'C', 'R'

SEZIONI = {
    'H': 'erbario', 'A': 'astronomia', 'C': 'cosmologia', 'Z': 'zodiaco',
    'B': 'biologia', 'P': 'farmacia', 'S': 'ricette', 'T': 'solo testo',
}

Riga = namedtuple('Riga', [
    'pagina', 'numero', 'tipo', 'sezione', 'lingua', 'mano', 'quire',
    'inizio_par', 'fine_par', 'parole', 'grezza'])

_PAGINA = re.compile(r'^<(f[^.>\s]+)>\s*(?:<!(.*)>)?')
_LOCUS = re.compile(r'^<(f[^.>\s]+)\.(\d+),(.)(\w\w)(?:;(\w))?>\s*(.*)$')
_VAR = re.compile(r'\$(\w)=(\w)')


def _scegli(m):
    """[a:b:c] -> a ; [ab] -> a (forma abbreviata ammessa dal formato)."""
    dentro = m.group(1)
    if ':' in dentro:
        return dentro.split(':')[0]
    return dentro[:1]


def pulisci(corpo, virgola_spazio=True):
    """Dal testo trascritto di un locus alle sue parole, piu' i segni di paragrafo."""
    inizio = '<%>' in corpo
    fine = '<$>' in corpo
    s = re.sub(r'<![^>]*>', '', corpo)            # commenti liberi
    s = s.replace('<%>', '').replace('<$>', '')
    s = s.replace('<->', '.').replace('<~>', '.')
    s = re.sub(r'<@[^>]*>', '', s)                # cambi di variabile in riga
    s = re.sub(r'<[^>]*>', '', s)                 # altri commenti dedicati
    s = re.sub(r'\[([^\]]*)\]', _scegli, s)
    s = s.replace('{', '').replace('}', '').replace("'", '')
    s = re.sub(r'@\d{3};', '*', s)
    separatori = r'[.,]+' if virgola_spazio else r'\.+'
    if not virgola_spazio:
        s = s.replace(',', '')
    parole = [p for p in re.split(separatori, s) if p]
    return parole, inizio, fine


def leggi(quale='ZL', virgola_spazio=True):
    """Tutte le righe della trascrizione, nell'ordine del file."""
    percorso = os.path.join(CARTELLA, FILE.get(quale, quale))
    righe, var, pagina = [], {}, None
    with open(percorso, encoding='latin-1') as f:
        for linea in f:
            linea = linea.rstrip('\n')
            if not linea or linea[0] == '#':
                continue
            m = _LOCUS.match(linea)
            if m:
                pag, num, _loc, tipo, _trascrittore, corpo = m.groups()
                if pag != pagina:
                    raise ValueError('locus %s fuori dalla sua pagina' % linea[:20])
                parole, inizio, fine = pulisci(corpo, virgola_spazio)
                righe.append(Riga(
                    pagina=pag, numero=int(num), tipo=tipo,
                    sezione=var.get('I'), lingua=var.get('L'), mano=var.get('H'),
                    quire=var.get('Q'), inizio_par=inizio, fine_par=fine,
                    parole=parole, grezza=corpo))
                continue
            m = _PAGINA.match(linea)
            if m:
                pagina = m.group(1)
                var = dict(_VAR.findall(m.group(2) or ''))
                continue
            raise ValueError('riga non riconosciuta: %r' % linea[:40])
    return righe


def pulita(parola):
    """Vera se la parola non contiene caratteri illeggibili o glifi rari."""
    return '?' not in parola and '*' not in parola


def testo_corrente(righe, lingua=None, sezione=None, mano=None):
    """Solo il testo in paragrafi (niente etichette, cerchi, raggi), filtrabile."""
    out = []
    for r in righe:
        if r.tipo[0] != PARAGRAFO:
            continue
        if lingua and r.lingua != lingua:
            continue
        if sezione and r.sezione != sezione:
            continue
        if mano and r.mano != mano:
            continue
        out.append(r)
    return out


def parole(righe, solo_pulite=True):
    """La sequenza piatta delle parole, riga dopo riga."""
    return [p for r in righe for p in r.parole if pulita(p) or not solo_pulite]


def righe_di_parole(righe, solo_pulite=True):
    """Lista di righe, ciascuna come lista di parole: serve agli effetti di riga."""
    out = []
    for r in righe:
        ps = [p for p in r.parole if pulita(p) or not solo_pulite]
        if ps:
            out.append(ps)
    return out
