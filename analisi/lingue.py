# -*- coding: utf-8 -*-
"""Testi di confronto: la Bibbia in un centinaio di lingue.

Il corpus e' quello di Christos Christodoulopoulos (github.com/christos-c/
bible-corpus, pubblico dominio CC0), fissato a un commit preciso perche' i
numeri si possano rifare. Non lo copiamo nel repository: pesa 600 MB. Lo script
prepara.py lo clona e ne estrae i campioni in dati/cache/.

Normalizzazione uguale per tutti: minuscole, via punteggiatura e cifre, restano
lettere e segni combinanti (servono alle scritture indiane), una parola e'
cio' che sta fra due spazi. Il campione parte dal Vangelo di Matteo, che c'e'
in quasi tutte le traduzioni: cosi' il contenuto e' lo stesso per ogni lingua.
"""
import csv, json, os, re, unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(QUI, '..', 'dati', 'cache', 'lingue')
SORGENTI = os.path.join(QUI, '..', 'dati', 'cache', 'sorgenti')
SORGENTE = os.environ.get('BIBLE_CORPUS', os.path.join(SORGENTI, 'bible-corpus'))
COMMIT = '44e5fca'

_VERSO = re.compile(r"<seg id=['\"]b\.([A-Z0-9]+)\.(\d+)\.(\d+)['\"][^>]*>(.*?)</seg>", re.S)

# Scritture in cui il carattere Unicode non e' una lettera nel senso nostro
ALFABETICHE = {'Latin', 'Cyrillic', 'Greek', 'Armenian', 'Coptic'}
ABJAD = {'Arabic', 'Hebrew', 'Syriac'}
SILLABARI = {'Cherokee', 'Aboriginal Syllabics', 'Ethiopic'}
LOGOGRAFICHE = {'Chinese', 'Kanjii', 'Hangul'}


def tipo_scrittura(script):
    if script in ALFABETICHE:
        return 'alfabeto'
    if script in ABJAD:
        return 'abjad'
    if script in SILLABARI:
        return 'sillabario'
    if script in LOGOGRAFICHE:
        return 'logografica'
    return 'abugida'   # devanagari, thai, kannada, ecc.


def normalizza(testo):
    """Minuscole e solo lettere/segni combinanti; tutto il resto diventa spazio."""
    testo = unicodedata.normalize('NFC', testo).casefold()
    fuori = []
    for c in testo:
        cat = unicodedata.category(c)
        fuori.append(c if cat[0] in 'LM' else ' ')
    return ' '.join(''.join(fuori).split())


def metadati():
    with open(os.path.join(SORGENTE, 'metadata.csv'), encoding='utf-8') as f:
        return {r['Filename']: r for r in csv.DictReader(f)}


def estrai(nome_file):
    """Testo normalizzato a partire da Matteo 1,1 (o dall'inizio se manca)."""
    grezzo = open(os.path.join(SORGENTE, 'bibles', nome_file), encoding='utf-8').read()
    versi = [(m.group(1), m.group(4)) for m in _VERSO.finditer(grezzo)]
    libri = [v[0] for v in versi]
    parti = libri.index('MAT') if 'MAT' in libri else 0
    testo = ' '.join(re.sub(r'<[^>]+>', ' ', v[1]) for v in versi[parti:] + versi[:parti])
    return normalizza(testo)


def prepara(nomi=None, max_caratteri=2_000_000):
    """Scrive in cache un file per lingua, piu' un indice con i metadati."""
    os.makedirs(CACHE, exist_ok=True)
    meta = metadati()
    indice = {}
    for nome, m in sorted(meta.items()):
        if nomi and nome not in nomi:
            continue
        testo = estrai(nome)[:max_caratteri]
        chiave = nome[:-4]
        with open(os.path.join(CACHE, chiave + '.txt'), 'w', encoding='utf-8') as f:
            f.write(testo)
        indice[chiave] = {
            'lingua': m['Language'], 'famiglia': m['Family'], 'scrittura': m['Script'],
            'tipo_scrittura': tipo_scrittura(m['Script']), 'parti': m['Parts'] or 'tutta',
            'caratteri': len(testo), 'file': nome}
    with open(os.path.join(CACHE, 'indice.json'), 'w', encoding='utf-8') as f:
        json.dump({'commit': COMMIT, 'lingue': indice}, f, ensure_ascii=False, indent=1)
    return indice


def prepara_pinyin(max_caratteri=2_000_000):
    """Il cinese trascritto in pinyin, una sillaba per parola, tono in cifra.

    Serve a mettere alla prova l'idea (di Stolfi, fra gli altri) che ogni
    "parola" del Voynich sia una sillaba di una lingua monosillabica e tonale.
    La cifra del tono resta attaccata alla sillaba: fa parte della sillaba."""
    from pypinyin import lazy_pinyin, Style
    grezzo = open(os.path.join(SORGENTE, 'bibles', 'Chinese.xml'), encoding='utf-8').read()
    versi = [(m.group(1), m.group(4)) for m in _VERSO.finditer(grezzo)]
    libri = [v[0] for v in versi]
    parti = libri.index('MAT')
    sillabe, lung = [], 0
    for _, testo in versi[parti:] + versi[:parti]:
        for s in lazy_pinyin(re.sub(r'<[^>]+>', ' ', testo), style=Style.TONE3,
                             neutral_tone_with_five=True, v_to_u=True):
            s = s.strip().lower()
            if re.fullmatch(r'[a-zü]+[1-5]', s):
                sillabe.append(s)
                lung += len(s) + 1
        if lung > max_caratteri:
            break
    testo = ' '.join(sillabe)[:max_caratteri]
    with open(os.path.join(CACHE, 'Chinese-pinyin.txt'), 'w', encoding='utf-8') as f:
        f.write(testo)
    percorso = os.path.join(CACHE, 'indice.json')
    with open(percorso, encoding='utf-8') as f:
        tutto = json.load(f)
    tutto['lingue']['Chinese-pinyin'] = {
        'lingua': 'Chinese (pinyin, una sillaba per parola)', 'famiglia': 'Sino-Tibetan',
        'scrittura': 'Pinyin', 'tipo_scrittura': 'alfabeto', 'parti': 'tutta',
        'caratteri': len(testo), 'file': 'Chinese.xml'}
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(tutto, f, ensure_ascii=False, indent=1)


def indice():
    with open(os.path.join(CACHE, 'indice.json'), encoding='utf-8') as f:
        return json.load(f)['lingue']


# --- Testi tecnici latini: il controllo di genere ---------------------------
#
# La Bibbia e' prosa narrativa. Un erbario o un ricettario e' quasi un elenco,
# e la sintassi potrebbe pesarci meno: prima di dire che il Voynich ha poca
# sintassi bisogna vedere quanta ne hanno ricette, manuali e voci di piante.
# Dalla Latin Library (github.com/cltk/lat_text_latin_library, commit fissato).

LATIN_LIBRARY = os.environ.get('LATIN_LIBRARY', os.path.join(SORGENTI, 'lat_text_latin_library'))
COMMIT_LL = '76229acaf02efd1964ac32009408a90b6f279758'

GENERI = {
    'Apicio, ricette di cucina': ['apicius/apicius%d.txt' % i for i in range(1, 6)],
    'Catone, agricoltura e ricette': ['cato/cato.agri.txt'],
    'Columella XII, conserve e ricette': ['columella/columella.rr12.txt'],
    'Varrone, agricoltura': ['varro.rr%d.txt' % i for i in range(1, 4)],
    'Isidoro XVII, piante': ['isidore/17.txt'],
    'Isidoro XVI, pietre e metalli': ['isidore/16.txt'],
    'Vegezio, arte militare': ['vegetius%d.txt' % i for i in range(1, 5)],
    'Vitruvio, architettura': ['vitruvius%d.txt' % i for i in range(1, 11)],
}


def genere(nome):
    """Le parole di un testo tecnico latino, normalizzate come le Bibbie."""
    pezzi = []
    for rel in GENERI[nome]:
        with open(os.path.join(LATIN_LIBRARY, rel), encoding='utf-8') as f:
            righe = [r for r in f if 'Latin Library' not in r and 'Classics Page' not in r]
        pezzi.append(normalizza(' '.join(righe)))
    return ' '.join(pezzi).split()


def parole(chiave, max_caratteri=None, inizio=0):
    """Le parole di una lingua, prese da un tratto contiguo del testo in cache."""
    with open(os.path.join(CACHE, chiave + '.txt'), encoding='utf-8') as f:
        testo = f.read()
    if inizio:
        testo = testo[inizio:]
        testo = testo[testo.find(' ') + 1:]      # non partire a meta' parola
    if max_caratteri:
        testo = testo[:max_caratteri]
        testo = testo[:testo.rfind(' ')]
    return testo.split()
