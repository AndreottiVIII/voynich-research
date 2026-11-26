# -*- coding: utf-8 -*-
"""IA44 (schemi noti in anticipo): i libri dei controlli.

Tutti i libri sono "pagine": OrderedDict nome-pagina -> lista di (inizio_paragrafo, [parola, ...]) con la parola come
STRINGA (glifi attaccati). Nessun testo del manoscritto: i libri sono scritti da generatori (v21, Naibbe, Timm e Schinner)
o sono latino cifrato parola per parola.

Fonti dei controlli (tutte non Voynich):
  v21        libri senza messaggio del voynichizzatore v21: chiavi 13-24 gia' fatte da IA1 (`dati/cache/ia01_libri/b<k>.pkl`),
             chiavi 1-12 fatte qui (`dati/cache/ia44_controlli/v21_b<k>.pkl`, stesso programma `canale_sacco.codifica(None,
             'e409-<k>', 'v21')`): in tutto 24 libri, come l'e419.
  naibbe     8 libri del cifrario Naibbe (Greshko 2025) fatti da IA28 (`dati/cache/ia28/libri/NB_<k>.pkl`).
  timm       testo generato da Timm e Schinner (seme 1, 2, 3, 4, 19), tagliato qui in pagine della lunghezza delle pagine date.
  latino     Macer Floridus (OCR dell'edizione del 1832, archive.org, pubblico dominio; e99) e Isidoro, Etymologiae XVII (The Latin
             Library, Public Domain Mark 1.0): flusso di parole, cifrato parola per parola (`cifra_latino`).
Percorsi in `dati/cache/ia44_controlli/` (fuori da git, come tutta la cache).
"""
import os
import pickle
import random
import re
import sys
import zlib
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, '..')
sys.path.insert(0, os.path.join(RADICE, 'analisi'))
sys.path.insert(0, os.path.join(RADICE, 'voynichizzatore'))
sys.path.insert(0, QUI)

CACHE = os.environ.get('LIBRI44', os.path.join(RADICE, 'dati', 'cache', 'ia44_controlli'))
IA01 = os.path.join(RADICE, 'dati', 'cache', 'ia01_libri')
IA28 = os.path.join(RADICE, 'dati', 'cache', 'ia28', 'libri')
TS = os.path.join(RADICE, 'dati', 'cache', 'timm_schinner')
ISIDORO = os.path.join(RADICE, 'dati', 'cache', 'sorgenti', 'lat_text_latin_library', 'isidore', '17.txt')
CHIAVI_V21_NUOVE = tuple(range(1, 13))        # 1-12 fatte qui; 13-24 le ha fatte IA1
CHIAVI_V21 = tuple(range(1, 25))
SEMI_TIMM = (1, 2, 3, 4, 19)
NAIBBE = tuple(range(8))


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def a_stringhe(libro):
    """Libro di ia01/ia28 (parole = tuple di glifi) -> pagine con parole stringa."""
    out = OrderedDict()
    for p, righe in libro.items():
        out[p] = [(bool(ini), [''.join(w) for w in ws]) for ini, ws in righe if ws]
    return out


def percorso_v21(k):
    if k >= 13:
        return os.path.join(IA01, 'b%d.pkl' % k)
    return os.path.join(CACHE, 'v21_b%d.pkl' % k)


def genera_v21(k):
    """Un libro v21 senza messaggio con la chiave k (1-12; ~100 s). Lo stesso procedimento di ia01.genera_libro('b<k>')."""
    p = percorso_v21(k)
    if os.path.exists(p):
        return 'gia fatto'
    import misure
    import trascrizione
    import canale_sacco
    os.makedirs(CACHE, exist_ok=True)
    rr, _ = canale_sacco.codifica(None, 'e409-%d' % k, 'v21', verifica=False)
    dividi = misure.divisore(misure.GLIFI_EVA)
    out = OrderedDict()
    for pag, ini, ps in rr:
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            out.setdefault(pag, []).append((bool(ini), [tuple(dividi(w)) for w in ps]))
    with open(p + '.tmp', 'wb') as f:
        pickle.dump(out, f)
    os.replace(p + '.tmp', p)
    return 'fatto'


def libro_v21(k):
    with open(percorso_v21(k), 'rb') as f:
        return a_stringhe(pickle.load(f))


def libro_naibbe(k):
    with open(os.path.join(IA28, 'NB_%d.pkl' % k), 'rb') as f:
        return a_stringhe(pickle.load(f))


def flusso_timm(seme):
    """Le parole del testo generato da Timm e Schinner, nell'ordine."""
    with open(os.path.join(TS, 'seme_%d' % seme, 'generate', 'generated_text.txt'), encoding='utf-8') as f:
        return [w for l in f if l.strip() and not l.startswith('#') for w in l.split()]


def impagina(flusso, lunghezze, nomi, inizio=0):
    """Taglia un flusso di parole in pagine con le lunghezze date (in cerchio se il flusso finisce)."""
    out = OrderedDict()
    i = inizio
    n = len(flusso)
    for nome, L in zip(nomi, lunghezze):
        ws = [flusso[(i + j) % n] for j in range(L)]
        out[nome] = [(True, ws)]
        i += L
    return out


# ---------------------------------------------------------------- latino cifrato parola per parola

def _parole_latine(testo):
    import lingue
    t = lingue.normalizza(testo).replace('j', 'i').replace('v', 'u')
    return [w for w in t.split() if w.isalpha()]


def capitoli_latini():
    """Lista di capitoli (liste di parole): i 79 del Macer (e99) e quelli del libro XVII di Isidoro (a ogni "I. ", "II. "...)."""
    import e99_macer
    caps = [[w for r in c for w in _parole_latine(' '.join(r))] for c in e99_macer.capitoli()]
    with open(ISIDORO, encoding='utf-8', errors='replace') as f:
        t = f.read()
    t = t.split('DE REBVS RVSTICIS', 1)[-1]
    pezzi = re.split(r'(?:^|\s)(?=[IVXLC]{1,7}\.\s+DE\s)', t)
    for z in pezzi:
        ws = _parole_latine(z)
        if len(ws) >= 20:
            caps.append(ws)
    return [c for c in caps if c]


def flusso_latino(seme):
    """I capitoli in un ordine che dipende dal seme, poi uniti in un solo flusso."""
    caps = list(capitoli_latini())
    random.Random(seme).shuffle(caps)
    return [w for c in caps for w in c]


def cifra_latino(flusso_lat, vocabolario_cifra, seme, riservate=()):
    """Cifrario parola per parola: i tipi latini, per frequenza decrescente, ricevono i tipi del `vocabolario_cifra` (lista di parole
    in ordine di frequenza decrescente) per frequenza decrescente; gli spareggi sono rimescolati dal seme. I tipi di cifra in
    `riservate` non si usano (parole piantate). Se i tipi latini sono piu' di quelli della cifra, i rimasti riusano tipi della
    cifra (collisioni, solo fra i piu' rari)."""
    rnd = random.Random(seme)
    voc = [w for w in vocabolario_cifra if w not in set(riservate)]
    conta = Counter(flusso_lat)
    tipi = sorted(conta, key=lambda w: (-conta[w], rnd.random()))
    mappa = {}
    for i, w in enumerate(tipi):
        mappa[w] = voc[i] if i < len(voc) else voc[rnd.randrange(len(voc) // 2, len(voc))]
    return [mappa[w] for w in flusso_lat], mappa


def vocabolario_ordinato(libro):
    """Tipi di parola di un libro per frequenza decrescente (spareggio alfabetico)."""
    c = Counter(w for righe in libro.values() for _, ws in righe for w in ws)
    return [w for w, _ in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]


def main():
    """Fa i libri v21 mancanti (chiavi 1-12), al massimo 4 processi: `python schemi_libri.py [processi]`."""
    from multiprocessing import get_context
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    n = max(1, min(4, n))
    with get_context('spawn').Pool(n) as pool:
        for k, r in zip(CHIAVI_V21_NUOVE, pool.imap(genera_v21, CHIAVI_V21_NUOVE)):
            print('v21 b%d: %s' % (k, r), flush=True)


if __name__ == '__main__':
    main()
