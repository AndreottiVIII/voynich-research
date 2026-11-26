# -*- coding: utf-8 -*-
"""IA43, modulo di supporto: piantare un messaggio in chiaro, a dose nota, dentro un libro v21 (strada 1 di `voynich-ia/PROPOSTE_DECIFRARE_FABLE.md`).

In parole semplici
- Il libro di partenza ("base") e' un libro v21 SENZA messaggio (`canale_sacco.codifica(None, chiave, 'v21')`, soli bit di riempimento): righe, paragrafi e parole come il v21 le scrive.
  Piantare = sostituire una quota `dose` dei posti di parola del libro con parole che vengono da un testo latino vero (il Macer floridus, un erbario in versi, e l'inizio di
  Isidoro XVII), lasciando il resto del libro com'e'. Il messaggio non e' cifrato ne' compresso: e' in chiaro, "ingenuo".
- Tre modi (Fable):
    a  parola per parola: ogni parola latina diventa sempre la stessa parola del libro (o una di `alt` alternative), nell'ordine del testo;
    b  lettera per lettera alla Naibbe: il testo senza spazi si taglia in pezzi di una o due lettere e ogni pezzo diventa una parola presa dalle tavole del cifrario Naibbe
       (le tavole vere, pubbliche; `alt` = quante delle sei tavole si usano, 1, 3 o 6);
    c  solo "quali parole stanno nella pagina": le parole sono quelle di a, ma dentro ogni pagina il loro ordine e' rimescolato (il canale del v21, in chiaro).
  Controllo di sostituzione (`z`): come a, ma le parole del messaggio sono rimescolate su tutto il libro (stesso lessico, stesso numero di posti, niente ordine ne' pagina):
  serve a separare "e' il messaggio" da "e' solo il fatto di aver sostituito parole".
- I posti sono annidati: ogni posto ha un numero a caso fisso (dal seme della base), e a dose `d` si sostituiscono i posti con numero < d. I posti a dose 5% sono dentro quelli a 10% e cosi' via,
  uguali per tutte le forme: i confronti fra forme e dosi sono appaiati.
- Il libro dei codici (a, c, z): i tipi latini, dal piu' frequente, prendono parole del libro base in ordine di frequenza decrescente (`alt` parole consecutive per tipo; oltre la fine
  del vocabolario si ricomincia: i tipi rari condividono parole). Ogni occorrenza sceglie fra le `alt` parole con un numero a caso fisso del posto.
- Controllo di correttezza (`decodifica`): con la chiave (posti, libro dei codici) il messaggio si ritrova dal libro piantato; con una chiave sbagliata (altri posti) no.
Nessun risultato e' scritto qui. Non legge il Voynich.
"""
import hashlib
import os
import pickle
import random
import re
import sys
import unicodedata
import zlib
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

MACER = os.path.join(QUI, '..', 'dati', 'cache', 'macer', 'macer_1832_djvu.txt')
MACER_SHA = '1baed87fec67e0c7d785fc7c92452bba8185f03e18b1b02b6b0378717161d8e3'
ISIDORO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
TAVOLE_NAIBBE = os.path.join(QUI, '..', 'dati', 'cache', 'sorgenti', 'naibbe-cipher', 'references', 'naibbe_tables.csv')

FORME = ('a', 'b', 'c')
ALTERNATIVE = {'a': (1, 3, 10), 'b': (1, 3, 6), 'c': (1, 3, 10)}
DOSI = (0.05, 0.10, 0.20, 0.40, 0.70, 1.00)
Z_FORMA = 'z'                      # controllo di sostituzione


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


# ---------------------------------------------------------------- il testo in chiaro

def _pulisci_token(t, originale):
    t = ''.join(c for c in unicodedata.normalize('NFD', t.lower()) if unicodedata.category(c) != 'Mn')
    t = t.replace('æ', 'ae').replace('œ', 'oe').replace('j', 'i').replace('v', 'u')
    if not re.fullmatch('[a-z]+', t):
        return None
    if originale.isupper() and re.fullmatch('[IVXLCDM]+', originale):      # numeri romani (capitoli)
        return None
    if len(t) == 1 and t not in ('a', 'e'):                                 # residui di OCR e numeri di verso
        return None
    if not re.search('[aeiou]', t):
        return None
    return t


def parole_di(testo):
    out = []
    for t in re.findall(r"[^\W\d_]+", testo):
        p = _pulisci_token(t, t)
        if p:
            out.append(p)
    return out


_TESTO = {}


def testo_chiaro():
    """Le parole del messaggio in chiaro, nell'ordine: Macer floridus (OCR 1832, sha256 controllato, pubblico) e poi l'inizio di Isidoro XVII. Pulito: minuscole, senza segni, j->i, v->u,
    senza numeri romani, lettere sole (salvo a, e) e sigle senza vocali (residui di OCR)."""
    if 'p' not in _TESTO:
        dati = open(MACER, 'rb').read()
        if hashlib.sha256(dati).hexdigest() != MACER_SHA:
            raise SystemExit('OCR del Macer diverso da quello preregistrato')
        macer = ' '.join(dati.decode('utf-8').splitlines()[2165:7570])
        isid = open(ISIDORO, encoding='utf-8').read().replace('\r\n', '\n')
        _TESTO['p'] = parole_di(macer) + parole_di(isid)
    return _TESTO['p']


def messaggio(n, inizio=0):
    """`n` parole del messaggio a partire da `inizio` (si ricomincia se il testo finisce)."""
    t = testo_chiaro()
    return [t[(inizio + i) % len(t)] for i in range(n)]


# ---------------------------------------------------------------- libri di partenza

def genera_base(chiave, cartella):
    """Il libro v21 senza messaggio con la chiave `e409-<chiave>`: lista di (pagina, inizio, [parole stringa]). Salvato in `cartella`/base_<chiave>.pkl."""
    p = os.path.join(cartella, 'base_%s.pkl' % chiave)
    if os.path.exists(p):
        return p
    os.makedirs(cartella, exist_ok=True)
    import canale_sacco
    righe, _ = canale_sacco.codifica(None, 'e409-%s' % chiave, 'v21', verifica=False)
    t = [(pag, bool(ini), list(ps)) for pag, ini, ps in righe]
    with open(p + '.tmp', 'wb') as f:
        pickle.dump(t, f)
    os.replace(p + '.tmp', p)
    return p


def leggi_base(chiave, cartella):
    return pickle.load(open(os.path.join(cartella, 'base_%s.pkl' % chiave), 'rb'))


# ---------------------------------------------------------------- posti e libro dei codici

def posti(t):
    """Tutti i posti di parola del libro, in ordine: (indice riga, posizione nella riga)."""
    return [(i, j) for i, (_, _, ps) in enumerate(t) for j in range(len(ps))]


def numeri_posti(t, chiave):
    """Un numero a caso fisso in [0, 1) per ogni posto (dal seme della base) e uno per la scelta fra le alternative."""
    r = random.Random(seme_str('ia43-posti', chiave))
    n = sum(len(ps) for _, _, ps in t)
    return [r.random() for _ in range(n)], [r.random() for _ in range(n)]


def libro_codici(t, alt, chiave):
    """Tipo latino -> lista di `alt` parole del libro. I tipi latini dal piu' frequente (a parita' in ordine alfabetico) prendono parole del libro base dalla piu' frequente."""
    voc = [w for w, _ in sorted(Counter(w for _, _, ps in t for w in ps).items(), key=lambda kv: (-kv[1], kv[0]))]
    lat = [w for w, _ in sorted(Counter(testo_chiaro()).items(), key=lambda kv: (-kv[1], kv[0]))]
    V = len(voc)
    return OrderedDict((tipo, [voc[(r * alt + k) % V] for k in range(alt)]) for r, tipo in enumerate(lat))


# ---------------------------------------------------------------- Naibbe con tavole limitate

def _tavole():
    if 't' not in _TESTO:
        import generatori
        _TESTO['t'] = generatori.naibbe_tabelle(TAVOLE_NAIBBE)
    return _TESTO['t']


def naibbe_parole(lettere, n_tavole, rnd, n_parole):
    """Le prime `n_parole` parole del cifrario Naibbe (tavole vere, algoritmo di `generatori.naibbe`) su `lettere`, usando solo le prime `n_tavole` delle sei tavole
    (alpha, beta1, beta2, beta3, gamma1, gamma2) con i pesi del mazzo originale. Ricomincia dal testo se non basta."""
    import generatori
    glifi = _tavole()
    tab = list(generatori.NAIBBE_TABELLE[:n_tavole])
    unigrammi = {g for c, g in glifi.items() if c.startswith('unigram_')}
    mazzo, pos = [], [0]

    def pesca():
        if pos[0] >= len(mazzo):
            mazzo[:] = [t for t in tab for _ in range(generatori.NAIBBE_PESI[t])]
            rnd.shuffle(mazzo)
            pos[0] = 0
        pos[0] += 1
        return mazzo[pos[0] - 1]
    parole, i = [], 0
    n = len(lettere)
    while len(parole) < n_parole:
        if i >= n:
            i = 0
        if i == n - 1 or rnd.random() < 17 / 36:
            parole.append(glifi['unigram_%s_%s' % (pesca(), lettere[i])])
            i += 1
        else:
            for _ in range(60):
                w = glifi['prefix_%s_%s' % (pesca(), lettere[i])] + glifi['suffix_%s_%s' % (pesca(), lettere[i + 1])]
                if w not in unigrammi:
                    break
            parole.append(w)
            i += 2
    return parole


def lettere_messaggio(n_parole_testo, inizio=0):
    """Il testo in chiaro come stringa di lettere (come `generatori.naibbe_pulisci`: solo a-z, w->uu, j->i, k->c)."""
    import generatori
    return generatori.naibbe_pulisci(' '.join(messaggio(n_parole_testo, inizio)))


# ---------------------------------------------------------------- piantare

def pianta(t, chiave, forma, dose, alt=1, inizio=0):
    """Il libro `t` (lista di (pagina, inizio, parole)) con una quota `dose` dei posti di parola sostituita. `forma`: 'a', 'b', 'c' o 'z' (controllo di sostituzione).
    -> (nuovo libro, info). Info: `posti` (lista di posti sostituiti), `parole_messaggio` (i tipi latini per a/c/z, i pezzi per b), `libro_codici` (per a/c/z)."""
    num, scelta = numeri_posti(t, chiave)
    flat = posti(t)
    sel = [k for k, u in enumerate(num) if u < dose] if dose < 1.0 else list(range(len(flat)))
    n = len(sel)
    nuovo = [(p, i, list(ps)) for p, i, ps in t]
    info = OrderedDict([('forma', forma), ('dose', dose), ('alt', alt), ('posti_sostituiti', n), ('posti_totali', len(flat))])
    if n == 0:
        info['posti'] = []
        return nuovo, info
    if forma == 'b':
        rnd = random.Random(seme_str('ia43-naibbe', chiave, alt))
        lett = lettere_messaggio(int(n * 1.6) + 50, inizio)
        parole = naibbe_parole(lett, alt, rnd, n)
        for k, w in zip(sel, parole):
            i, j = flat[k]
            nuovo[i][2][j] = w
        info['posti'] = [flat[k] for k in sel]
        info['parole_messaggio'] = None
        return nuovo, info
    msg = messaggio(n, inizio)
    libro = libro_codici(t, alt, chiave)
    if forma == 'c':
        # dentro ogni riga di pagina: i tipi dei posti scelti si rimescolano fra i posti scelti della stessa pagina
        per_pag = OrderedDict()
        for q, k in enumerate(sel):
            per_pag.setdefault(t[flat[k][0]][0], []).append(q)
        msg = list(msg)
        for p, qs in per_pag.items():
            vals = [msg[q] for q in qs]
            random.Random(seme_str('ia43-c', chiave, p)).shuffle(vals)
            for q, v in zip(qs, vals):
                msg[q] = v
    elif forma == 'z':
        msg = list(msg)
        random.Random(seme_str('ia43-z', chiave)).shuffle(msg)
    for q, k in enumerate(sel):
        i, j = flat[k]
        c = libro[msg[q]]
        nuovo[i][2][j] = c[min(int(scelta[k] * len(c)), len(c) - 1)]
    info['posti'] = [flat[k] for k in sel]
    info['parole_messaggio'] = msg
    info['libro_codici'] = libro
    return nuovo, info


def decodifica(t_piantato, info):
    """Con la chiave (posti e libro dei codici) il messaggio si ritrova: per ogni posto sostituito il tipo latino la cui lista di parole contiene la parola scritta (se piu' tipi
    la condividono, il piu' frequente). -> lista dei tipi ritrovati (a, c, z)."""
    inv = {}
    for tipo, ws in info['libro_codici'].items():
        for w in ws:
            inv.setdefault(w, tipo)                       # i tipi sono in ordine di frequenza: il primo vince
    return [inv.get(t_piantato[i][2][j]) for i, j in info['posti']]


def recuperato(t_piantato, info, posti_alt=None):
    """Quota dei posti sostituiti il cui tipo latino viene ritrovato esattamente. Con `posti_alt` (una chiave sbagliata: altri posti) si decodificano quelli."""
    inf = dict(info)
    if posti_alt is not None:
        inf['posti'] = posti_alt
    d = decodifica(t_piantato, inf)
    if posti_alt is None:
        ok = sum(a == b for a, b in zip(d, info['parole_messaggio']))
        return ok / max(1, len(d))
    return sum(a == b for a, b in zip(d, info['parole_messaggio'])) / max(1, len(d))


if __name__ == '__main__':
    pass
