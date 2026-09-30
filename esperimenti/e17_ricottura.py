# -*- coding: utf-8 -*-
"""Esperimento 17: il Voynich senza spazi, con un risolutore vero.

L'esperimento 16 non rompeva nemmeno i controlli. Qui il risolutore e' quello
con cui si attaccano i cifrari omofonici veri (ricottura simulata su n-grammi
di cinque lettere, analisi/ricottura.py).

Ipotesi messa alla prova: ogni unita' del Voynich vale una lettera di una
lingua nota, piu' unita' possono valere la stessa lettera, e gli spazi non
contano (ogni riga e' una sequenza continua). Le unita' si contano in quattro
modi:
- i segni EVA, con i segni composti fusi (ch, sh, cth...);
- i segni dell'alfabeto v101 di Glen Claston, che conta come un segno solo
  alcuni gruppi che l'EVA spezza (per esempio le serie di i);
- gruppi di segni imparati dal testo, a due gradi (20 e 50 fusioni): si
  fondono via via le due unita' vicine piu' legate fra loro dentro le parole
  (vedi impara_gruppi). E' la versione "tokenizzata": ogni gruppo una
  lettera, come in un cifrario verboso.

Per ogni lingua:
- tetto: il testo in chiaro (non visto in addestramento) e come lo giudica il
  modello della lingua;
- controllo positivo: lo stesso testo cifrato con una chiave omofonica
  casuale; se il risolutore non lo rompe, il resto non vale;
- controllo negativo: un testo di un'altra lingua, cifrato allo stesso modo e
  attaccato come se fosse in questa. Dice quanto "legge" il risolutore dove
  non c'e' niente da leggere in quella lingua;
- il Voynich, nei quattro modi.
Controlli positivi e negativi si rifanno per ogni modo di contare le unita',
con lo stesso numero di simboli e la stessa lunghezza del Voynich letto in
quel modo (i simboli divisi fra le lettere in proporzione alla frequenza).

Misure, sul testo decifrato:
- punteggio: log-probabilita' media per lettera secondo il modello della
  lingua (piu' alto e' meglio; il tetto e' quello del testo in chiaro);
- copertura: quota delle lettere che si possono coprire con parole vere della
  lingua di almeno 4 lettere, dividendo la riga al meglio; copertura_6 lo
  stesso con parole di almeno 6 lettere;
- coppie attestate: fra le parole vere trovate una accanto all'altra, quante
  coppie compaiono anche nel testo di addestramento;
- parole diverse usate dalla divisione.

Solo per il latino, altri controlli:
- due testi latini che non sono la Bibbia (Varrone sull'agricoltura, Isidoro
  sulle piante), cifrati come il controllo positivo: il modello li conosce
  meno, come conoscerebbe meno il testo del Voynich se fosse latino;
- un cifrario verboso fatto apposta: ogni lettera diventa uno o due gruppi di
  1-3 segni EVA. I gruppi imparati dal testo devono ritrovarlo;
- il Plinio cifrato col Naibbe: latino vero, ma con un meccanismo diverso.

Scrive risultati/e17_ricottura.json e .md; con --grafico il grafico.
"""
import json, os, random, sys, time, unicodedata
from collections import Counter, OrderedDict, namedtuple
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import decifra, lingue, misure, ricottura, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ADDESTRAMENTO = 250000      # parole della Bibbia per il modello della lingua
PER_RIGA = 7                # parole per riga nei testi di controllo, come nel Voynich
MINIMO_UNITA = 20           # unita' piu' rare: la riga si spezza li'
RIPARTENZE = int(os.environ.get('RIPARTENZE', '4'))
LINGUE = OrderedDict([
    ('Latin', 'latino'), ('Italian', 'italiano'), ('German', 'tedesco'), ('English', 'inglese'),
    ('French', 'francese'), ('Spanish', 'spagnolo'), ('Czech', 'ceco'), ('Hungarian', 'ungherese'),
    ('Greek', 'greco'), ('Hebrew', 'ebraico'), ('Arabic', 'arabo'), ('Turkish', 'turco'),
    ('Malagasy', 'malgascio'), ('Chinantec-NT', 'chinanteco'),
])
STRANIERO = 'Finnish'       # per il controllo negativo (per l'ungherese, anch'esso uralico: il latino)
FUSIONI = (20, 50)
LATINO_AMPIO = 8000000      # caratteri della Latin Library aggiunti al modello latino


# ---------------------------------------------------------------- testi

def alfabeto(parole, soglia=0.0005):
    """Le lettere (senza segni diacritici) che fanno almeno lo 0,05% del testo."""
    c = Counter(_base(''.join(parole)))
    tot = sum(c.values())
    return {x for x, n in c.items() if n / tot >= soglia}


def _base(s):
    return ''.join(x for x in unicodedata.normalize('NFD', s) if unicodedata.category(x) != 'Mn')


def pulisci(parole, lettere):
    out = []
    for p in parole:
        q = ''.join(x for x in _base(p) if x in lettere)
        if q:
            out.append(q)
    return out


def latino_ampio(massimo=LATINO_AMPIO):
    """Parole dalla Latin Library, esclusi i testi tecnici usati per le prove."""
    esclusi = {os.path.normpath(r) for rs in lingue.GENERI.values() for r in rs}
    parole, n = [], 0
    for cartella, sotto, files in sorted(os.walk(lingue.LATIN_LIBRARY)):
        sotto.sort()
        for nome in sorted(files):
            rel = os.path.normpath(os.path.relpath(os.path.join(cartella, nome), lingue.LATIN_LIBRARY))
            if not nome.endswith('.txt') or rel in esclusi or nome in ('README.md', 'LICENSE.md'):
                continue
            with open(os.path.join(cartella, nome), encoding='utf-8', errors='ignore') as f:
                righe = [r for r in f if 'Latin Library' not in r and 'Classics Page' not in r]
            ps = lingue.normalizza(' '.join(righe)).split()
            parole += ps
            n += sum(map(len, ps))
            if n >= massimo:
                return parole
    return parole


def in_righe(parole, per_riga=PER_RIGA):
    """Righe finte di per_riga parole: liste di parole."""
    return [parole[i:i + per_riga] for i in range(0, len(parole) - per_riga + 1, per_riga)]


def prendi(parole, lunghezza):
    """Le prime parole, fino ad arrivare a `lunghezza` lettere."""
    out, n = [], 0
    for p in parole:
        out.append(p)
        n += len(p)
        if n >= lunghezza:
            break
    return out


def cifra(righe_parole, rnd, omofoni=(1, 2)):
    """Cifratura omofonica di righe di parole; ogni riga diventa una lista di
    unita' senza spazi. Restituisce anche la chiave (unita' -> lettera)."""
    stringhe = [''.join(r) for r in righe_parole]
    cif, chiave = decifra.cifra_omofonico(stringhe, rnd, unita_per_lettera=omofoni)
    return [decifra.dividi_unita(c) for c in cif], {u: l for l, us in chiave.items() for u in us}


def cifra_abbinata(righe_parole, simboli, rnd):
    """Cifratura omofonica con un numero dato di simboli, come il Voynich letto
    in un certo modo. I simboli si dividono fra le lettere in proporzione alla
    frequenza (almeno uno per lettera), come fa chi vuole appiattire le
    frequenze; se sono meno delle lettere, le lettere piu' rare ne condividono
    uno. Restituisce le righe di unita' e la chiave (unita' -> lettera)."""
    stringhe = [''.join(r) for r in righe_parole]
    freq = Counter(''.join(stringhe))
    lettere = [l for l, _ in freq.most_common()]
    tot = sum(freq.values())
    if simboli < len(lettere):
        quote = {l: 1 for l in lettere[:simboli]}   # l'ultimo simbolo e' condiviso dalle piu' rare
    else:
        resto = simboli - len(lettere)
        ideali = {l: resto * freq[l] / tot for l in lettere}
        quote = {l: 1 + int(ideali[l]) for l in lettere}
        mancano = simboli - sum(quote.values())
        for l in sorted(lettere, key=lambda l: -(ideali[l] - int(ideali[l])))[:mancano]:
            quote[l] += 1
    chiave, n = {}, 0
    for l in lettere:
        if l in quote:
            chiave[l] = ['u%d.' % (n + i) for i in range(quote[l])]
            n += quote[l]
    vera = {u: l for l, us in chiave.items() for u in us}
    for l in lettere[len(quote):]:
        chiave[l] = chiave[lettere[len(quote) - 1]]
    return [[rnd.choice(chiave[c]) for c in x] for x in stringhe], vera


# ---------------------------------------------------------------- unita' del Voynich

def impara_gruppi(parole, fusioni, minimo=MINIMO_UNITA):
    """Gruppi di segni imparati dal testo: parole = liste di unita'. A ogni
    passo si fondono le due unita' vicine piu' legate fra loro, misurando il
    legame con n(ab)^2 / (n(a) n(b)): conta quante volte stanno insieme, ma
    anche quanto di rado stanno separate. Il byte-pair encoding classico
    guarda solo n(ab) e finisce per incollare lettere diverse che vanno spesso
    insieme; su un cifrario verboso di prova questa misura ritrova tutti i
    gruppi veri (35 su 35 con 50 fusioni), il byte-pair encoding 27.
    Restituisce le fusioni, in ordine."""
    voc = Counter(tuple(p) for p in parole)
    regole = []
    for _ in range(fusioni):
        coppie, singole = Counter(), Counter()
        for w, c in voc.items():
            for u in w:
                singole[u] += c
            for a, b in zip(w, w[1:]):
                coppie[a, b] += c
        candidate = [(ab, c) for ab, c in coppie.items() if c >= minimo]
        if not candidate:
            break
        (a, b), _ = max(candidate, key=lambda x: (x[1] ** 2 / (singole[x[0][0]] * singole[x[0][1]]), x[0]))
        regole.append((a, b))
        voc = Counter({tuple(_fondi(w, a, b)): c for w, c in voc.items()})
    return regole


def _fondi(w, a, b):
    out, i = [], 0
    while i < len(w):
        if i + 1 < len(w) and w[i] == a and w[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(w[i])
            i += 1
    return out


def applica_gruppi(regole, dividi):
    memo = {}

    def taglia(parola):
        if parola not in memo:
            w = dividi(parola)
            for a, b in regole:
                w = _fondi(w, a, b)
            memo[parola] = w
        return memo[parola]
    return taglia


def in_unita(righe_parole, taglia, minimo=MINIMO_UNITA, ammesse=None):
    """Righe di parole -> righe di unita' senza spazi. Le unita' rare (o non
    ammesse) spezzano la riga, come le parole illeggibili."""
    pezzi = []
    for r in righe_parole:
        corrente = []
        for p in r:
            if p is None:
                if corrente:
                    pezzi.append(corrente)
                corrente = []
            else:
                corrente.extend(taglia(p))
        if corrente:
            pezzi.append(corrente)
    if ammesse is None:
        conta = Counter(u for pz in pezzi for u in pz)
        ammesse = {u for u, c in conta.items() if c >= minimo}
    out = []
    for pz in pezzi:
        cur = []
        for u in pz:
            if u in ammesse:
                cur.append(u)
            elif cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
    return [r for r in out if len(r) >= 5]


def righe_voynich(quale):
    """Le righe del testo in paragrafi; le parole illeggibili diventano None."""
    righe = trascrizione.testo_corrente(trascrizione.leggi(quale))
    return [[p if trascrizione.pulita(p) else None for p in r.parole] for r in righe]


def modi_voynich():
    """Il testo in paragrafi del Voynich come righe di unita', nei quattro modi."""
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl, gc = righe_voynich('ZL'), righe_voynich('GC')
    parole_zl = [glifi(p) for r in zl for p in r if p]
    out = OrderedDict()
    out['segni EVA'] = in_unita(zl, glifi)
    out['segni v101'] = in_unita(gc, list)
    for f in FUSIONI:
        out['gruppi (%d fusioni)' % f] = in_unita(zl, applica_gruppi(impara_gruppi(parole_zl, f), glifi))
    return out


# ---------------------------------------------------------------- controlli solo latini

VERBOSO_SEGNI = ['o', 'e', 'ch', 'y', 'a', 'd', 'i', 'k', 'l', 'r', 's', 't', 'n', 'q', 'sh', 'p']


def cifrario_verboso(lettere, rnd):
    """Ogni lettera -> uno o due gruppi diversi di 1-3 segni EVA. Nessun gruppo
    e' l'inizio di un altro, cosi' il testo senza spazi si rilegge in un modo
    solo, come deve fare un cifrario pensato per essere letto."""
    usati, chiave = [], {}
    for l in sorted(lettere):
        chiave[l] = []
        for _ in range(rnd.choice((1, 2))):
            while True:
                g = tuple(rnd.choice(VERBOSO_SEGNI) for _ in range(rnd.choice((1, 2, 2, 3))))
                if all(g[:len(u)] != u and u[:len(g)] != g for u in usati):
                    usati.append(g)
                    chiave[l].append(g)
                    break
    return chiave


def naibbe_righe():
    percorso = os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
    righe = [r.split() for r in open(percorso, encoding='utf-8') if r.strip()]
    return [r[i:i + 8] for r in righe for i in range(0, len(r), 8)]


# ---------------------------------------------------------------- misure

def copertura(stringa, vocabolario, minimo=4, massimo=16):
    """Divisione della stringa che copre piu' lettere con parole vere (di
    almeno `minimo` lettere). Restituisce (lettere coperte, [(inizio, fine)])."""
    n = len(stringa)
    migliore = [0] * (n + 1)
    da = [None] * (n + 1)
    for i in range(1, n + 1):
        migliore[i], da[i] = migliore[i - 1], None
        for l in range(minimo, min(massimo, i) + 1):
            if stringa[i - l:i] in vocabolario and migliore[i - l] + l > migliore[i]:
                migliore[i], da[i] = migliore[i - l] + l, l
    tratti, i = [], n
    while i > 0:
        if da[i]:
            tratti.append((i - da[i], i))
            i -= da[i]
        else:
            i -= 1
    return migliore[n], tratti[::-1]


Lessico = namedtuple('Lessico', 'parole coppie')


def giudica(righe_lettere, modello, lessico):
    """Come il modello giudica un testo (righe di lettere), e quanto se ne
    copre con parole vere:
    - copertura: lettere coperte da parole vere di almeno 4 lettere;
    - copertura_6: lo stesso con parole di almeno 6 lettere (a caso se ne
      trovano molte meno);
    - coppie_attestate: fra le parole vere una accanto all'altra, la quota
      delle coppie che compaiono anche nel testo di addestramento. In un
      testo vero sono molte, in parole messe a caso quasi nessuna."""
    lettere = sum(map(len, righe_lettere))
    coperte = coperte6 = accanto = attestate = 0
    usate = Counter()
    for r in righe_lettere:
        c, tratti = copertura(r, lessico.parole)
        coperte += c
        usate.update(r[a:b] for a, b in tratti)
        for (a1, b1), (a2, b2) in zip(tratti, tratti[1:]):
            if b1 == a2:
                accanto += 1
                attestate += (r[a1:b1], r[a2:b2]) in lessico.coppie
        coperte6 += copertura(r, lessico.parole, minimo=6)[0]
    tot = sum(usate.values())
    return OrderedDict([
        ('punteggio', ricottura.punteggio_righe(righe_lettere, modello)),
        ('copertura', coperte / lettere),
        ('copertura_6', coperte6 / lettere),
        ('coppie_attestate', attestate / accanto if accanto else 0.0),
        ('coppie_accanto', accanto),
        ('parole_diverse', len(usate)),
        ('quota_tre_piu_frequenti', sum(c for _, c in usate.most_common(3)) / tot if tot else 0.0),
        ('parole_frequenti', [p for p, _ in usate.most_common(12)]),
    ])


def attacca(righe, modello, lessico, rnd, vera=None, ripartenze=RIPARTENZE):
    """Risolve un testo cifrato (righe di unita') e giudica il testo decifrato."""
    grammi = ricottura.Grammi(righe, modello.n)
    t = time.time()
    esito, esiti = ricottura.risolvi(grammi, modello, rnd, ripartenze=ripartenze)
    decifrato = ricottura.decifra(righe, esito.chiave, grammi, modello)
    v = giudica(decifrato, modello, lessico)
    v['obiettivo'] = esito.obiettivo
    v['ripartenze'] = [round(e.modello, 4) for e in esiti]
    v['simboli'] = len(grammi.simboli)
    v['lunghezza'] = sum(map(len, righe))
    if vera is not None:
        tot = sum(grammi.frequenza.values())
        giuste = sum(grammi.frequenza[i] for i, s in enumerate(grammi.simboli)
                     if modello.lettere[esito.chiave[i]] == vera.get(s))
        v['chiave_giusta'] = giuste / tot
    v['chiave'] = {str(s): modello.lettere[esito.chiave[i]] for i, s in enumerate(grammi.simboli)}
    v['esempio'] = decifrato[:6]
    v['secondi'] = round(time.time() - t)
    return v


# ---------------------------------------------------------------- una lingua

def prepara_lingua(chiave_l):
    testo = lingue.parole(chiave_l)
    lettere = alfabeto(testo)
    testo = pulisci(testo, lettere)
    add = min(ADDESTRAMENTO, int(len(testo) * 0.8))
    addestramento = testo[:add]
    if chiave_l == 'Latin':
        addestramento = addestramento + pulisci(latino_ampio(), lettere)
    modello = ricottura.ModelloLettere(''.join(addestramento), n=5)
    lessico = Lessico({p for p in addestramento if len(p) >= 4}, set(zip(addestramento, addestramento[1:])))
    return testo, add, lettere, modello, lessico


def una_lingua(argomenti):
    """Per ogni modo di contare le unita' del Voynich: controllo positivo e
    negativo con lo stesso numero di simboli e la stessa lunghezza, poi il
    Voynich."""
    chiave_l, nome, voynich = argomenti
    rnd = random.Random('e17-' + chiave_l)
    testo, add, lettere, modello, lessico = prepara_lingua(chiave_l)
    altra = 'Latin' if chiave_l == 'Hungarian' else STRANIERO
    altro = lingue.parole(altra)
    altro = pulisci(altro, alfabeto(altro))
    r = OrderedDict([('lettere', len(modello.lettere)), ('lingua del controllo negativo', altra)])
    lunghezza = max(sum(map(len, v)) for v in voynich.values())
    r['tetto (testo in chiaro)'] = giudica([''.join(x) for x in in_righe(prendi(testo[add:], lunghezza))],
                                           modello, lessico)
    stampa(nome, 'tetto (testo in chiaro)', r['tetto (testo in chiaro)'])
    for modo, righe_v in voynich.items():
        simboli = len({u for x in righe_v for u in x})
        L = sum(map(len, righe_v))
        cif, vera = cifra_abbinata(in_righe(prendi(testo[add:], L)), simboli, rnd)
        r[modo + ', controllo positivo'] = attacca(cif, modello, lessico, rnd, vera=vera)
        cif, _ = cifra_abbinata(in_righe(prendi(altro, L)), simboli, rnd)
        r[modo + ', controllo negativo'] = attacca(cif, modello, lessico, rnd)
        r[modo + ', Voynich'] = attacca(righe_v, modello, lessico, rnd)
        for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
            stampa(nome, modo + ', ' + k, r[modo + ', ' + k])
    return nome, r


NON_BIBLICI = ('Varrone, agricoltura', 'Isidoro XVII, piante')


def controlli_latini(lunghezza):
    """Due testi latini non biblici cifrati (il Voynich non e' la Bibbia: il
    modello li conosce meno), il cifrario verboso fatto apposta e il Plinio
    col Naibbe."""
    rnd = random.Random('e17-latino-extra')
    testo, add, lettere, modello, lessico = prepara_lingua('Latin')
    r = OrderedDict()
    glifi = misure.divisore(misure.GLIFI_EVA)
    for opera in NON_BIBLICI:
        ps, n = [], 0
        for p in pulisci(lingue.genere(opera), lettere):
            ps.append(p)
            n += len(p)
            if n >= lunghezza:
                break
        righe = in_righe(ps)
        r['%s, tetto (testo in chiaro)' % opera] = giudica([''.join(x) for x in righe], modello, lessico)
        cif, vera = cifra(righe, rnd)
        v = r['%s, controllo positivo' % opera] = attacca(cif, modello, lessico, rnd, vera=vera)
        stampa('latino', opera, v)
    # cifrario verboso: lungo quanto il Voynich in segni EVA
    chiave = cifrario_verboso(lettere, rnd)
    prova, n = [], 0
    for p in testo[add + 60000:]:
        prova.append(p)
        n += 2 * len(p)
        if n >= lunghezza:
            break
    righe = in_righe(prova)
    # le "parole" cifrate (con gli spazi dove sono nel chiaro), per imparare i gruppi
    righe_cif = [[''.join(''.join(rnd.choice(chiave[c])) for c in p) for p in riga] for riga in righe]
    parole_cif = [glifi(p) for riga in righe_cif for p in riga]
    tetto = giudica([''.join(x) for x in righe], modello, lessico)
    r['cifrario verboso, tetto (testo in chiaro)'] = tetto
    for nome_modo, taglia in [('segni', glifi)] + [
            ('gruppi (%d fusioni)' % f, applica_gruppi(impara_gruppi(parole_cif, f), glifi)) for f in FUSIONI]:
        cif = in_unita(righe_cif, taglia)
        v = attacca(cif, modello, lessico, rnd)
        r['cifrario verboso, ' + nome_modo] = v
        stampa('latino', 'cifrario verboso, ' + nome_modo, v)
    # il Plinio cifrato col Naibbe
    righe_n = naibbe_righe()
    for nome_modo, taglia in [('segni', glifi)] + [
            ('gruppi (%d fusioni)' % f, applica_gruppi(impara_gruppi([glifi(p) for x in righe_n for p in x], f), glifi))
            for f in FUSIONI]:
        v = attacca(in_unita(righe_n, taglia), modello, lessico, rnd)
        r['Naibbe (Plinio), ' + nome_modo] = v
        stampa('latino', 'Naibbe (Plinio), ' + nome_modo, v)
    return r


def stampa(nome, etichetta, v):
    print('%-10s %-52s punteggio %6.3f  copertura %4.1f%% (6+: %4.1f%%)  coppie %4.1f%%  parole %5d%s  simboli %3d  %4ds' % (
        nome, etichetta, v['punteggio'], 100 * v['copertura'], 100 * v['copertura_6'], 100 * v['coppie_attestate'],
        v['parole_diverse'], '  chiave %5.1f%%' % (100 * v['chiave_giusta']) if 'chiave_giusta' in v else '',
        v.get('simboli', 0), v.get('secondi', 0)), flush=True)


def main():
    voynich = modi_voynich()
    for modo, righe in voynich.items():
        print('Voynich, %-22s simboli %3d  lunghezza %6d  righe %5d' % (
            modo, len({u for r in righe for u in r}), sum(map(len, righe)), len(righe)))
    lunghezza = sum(map(len, voynich['segni EVA']))
    percorso = os.path.join(RISULTATI, 'e17_ricottura.json')
    ris = OrderedDict()
    solo = os.environ.get('LINGUE_SOLO')
    lavori = [(k, n, voynich) for k, n in LINGUE.items() if not solo or k in solo.split(',')]
    with Pool(int(os.environ.get('PROCESSI', '4'))) as pool:
        extra = pool.apply_async(controlli_latini, (lunghezza,))
        for nome, r in pool.imap(una_lingua, lavori):
            ris[nome] = r
            with open(percorso, 'w', encoding='utf-8') as f:
                json.dump(ris, f, ensure_ascii=False, indent=1)
        if 'latino' in ris:
            ris['latino'].update(extra.get())
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


MODI = ['segni EVA', 'segni v101'] + ['gruppi (%d fusioni)' % f for f in FUSIONI]


def posizione(r, modo, misura='punteggio'):
    """Dove cade il Voynich fra il controllo negativo (0) e il positivo (1)."""
    pos, neg, voy = (r[modo + ', ' + k][misura] for k in ('controllo positivo', 'controllo negativo', 'Voynich'))
    return (voy - neg) / (pos - neg) if pos != neg else float('nan')


def _terna(r, modo, misura, fmt):
    return ' / '.join(fmt(r[modo + ', ' + k][misura]) for k in ('controllo positivo', 'Voynich', 'controllo negativo'))


def scrivi_tabella(ris):
    pct = lambda x: '%.0f%%' % (100 * x)
    num = lambda x: '%.2f' % x
    out = ['# Esperimento 17: il Voynich senza spazi, con un risolutore vero', '',
           'Ipotesi: ogni unità del Voynich vale una lettera (più unità possono valere la stessa lettera), '
           'gli spazi non contano. Risolutore: ricottura simulata su 5-grammi di lettere '
           '(analisi/ricottura.py), %d ripartenze. Per ogni modo di contare le unità, il controllo positivo '
           '(la lingua stessa, testo non visto in addestramento) e il negativo (un\'altra lingua) sono cifrati '
           'con lo stesso numero di simboli e hanno la stessa lunghezza del Voynich letto in quel modo.' % max(
               len(v['ripartenze']) for r in ris.values() for v in r.values() if isinstance(v, dict) and 'ripartenze' in v),
           '',
           '- **punteggio**: log-probabilità media per lettera del testo decifrato secondo il modello della '
           'lingua (più alto è meglio).',
           '- **posizione**: dove cade il punteggio del Voynich fra il controllo negativo (0) e il positivo (1).',
           '- **copertura 6+**: quota delle lettere coperte da parole vere di almeno 6 lettere.',
           '- **coppie**: fra le parole vere (di almeno 4 lettere) trovate una accanto all\'altra, quota delle '
           'coppie che compaiono nel testo di addestramento.',
           '- **chiave**: nel controllo positivo, quota del testo cifrato con il simbolo attribuito alla lettera '
           'giusta.', '',
           'Ogni cella con tre numeri: controllo positivo / Voynich / controllo negativo.', '',
           '| lingua | unità | simboli | chiave (positivo) | punteggio | posizione | copertura 6+ | coppie |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        for modo in MODI:
            if modo + ', Voynich' not in r:
                continue
            out.append('| %s | %s | %d | %s | %s | %.2f | %s | %s |' % (
                nome, modo, r[modo + ', Voynich']['simboli'], pct(r[modo + ', controllo positivo']['chiave_giusta']),
                _terna(r, modo, 'punteggio', num), posizione(r, modo), _terna(r, modo, 'copertura_6', pct),
                _terna(r, modo, 'coppie_attestate', pct)))
    out += ['', 'Il testo in chiaro (tetto), per confronto:', '',
            '| lingua | lettere | punteggio | copertura 6+ | coppie | controllo negativo |', '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        t = r['tetto (testo in chiaro)']
        out.append('| %s | %d | %.2f | %s | %s | %s |' % (nome, r['lettere'], t['punteggio'], pct(t['copertura_6']),
                                                       pct(t['coppie_attestate']), r['lingua del controllo negativo']))
    lat = ris.get('latino', {})
    extra = [k for k in lat if k.startswith(('Varrone', 'Isidoro', 'cifrario verboso', 'Naibbe'))]
    if extra:
        out += ['', '## Controlli in più, in latino', '',
                '| testo | punteggio | copertura 6+ | coppie | chiave | simboli |', '|---|---|---|---|---|---|']
        for k in extra:
            v = lat[k]
            out.append('| %s | %.2f | %s | %s | %s | %s |' % (
                k, v['punteggio'], pct(v['copertura_6']), pct(v['coppie_attestate']),
                pct(v['chiave_giusta']) if 'chiave_giusta' in v else '–', v.get('simboli', '–')))
    out += ['', '## Come "legge" il Voynich la chiave migliore', '']
    for nome in ('latino', 'italiano', 'tedesco', 'ebraico'):
        if nome not in ris:
            continue
        for modo in ('segni EVA', 'gruppi (50 fusioni)'):
            v = ris[nome].get(modo + ', Voynich')
            if v:
                out += ['**%s, %s** (le parole vere più frequenti: %s):' % (nome, modo, ', '.join(v['parole_frequenti'][:8])),
                        '', '```'] + v['esempio'][:4] + ['```', '']
    for k in ('cifrario verboso, gruppi (50 fusioni)', 'Varrone, agricoltura, controllo positivo'):
        if k in lat:
            out += ['**controllo: %s**:' % k, '', '```'] + lat[k]['esempio'][:4] + ['```', '']
    with open(os.path.join(RISULTATI, 'e17_ricottura.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    """Per ogni lingua e modo di contare le unita': dove cade il Voynich fra il
    controllo negativo (0) e il positivo (1)."""
    import grafici
    nomi = [n for n in ris if all(m + ', Voynich' in ris[n] for m in MODI)]
    forme = {'segni EVA': 'o', 'segni v101': 's', MODI[2]: '^', MODI[3]: 'D'}
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=5.6)
        fig.subplots_adjust(left=0.16, right=0.97, top=0.80, bottom=0.17)
        ys = range(len(nomi))
        for x, etichetta in ((0, 'un\'altra lingua, cifrata'), (1, 'la lingua stessa, cifrata')):
            ax.axvline(x, color=t['muto'], linewidth=1.2, zorder=1)
            ax.text(x, -0.85, etichetta, ha='center', va='bottom', fontsize=8, color=t['secondario'])
        for modo in MODI:
            xs = [posizione(ris[n], modo) for n in nomi]
            ax.scatter(xs, ys, s=34, marker=forme[modo], color=t['accento'], edgecolor=t['sfondo'], linewidth=0.8,
                       alpha=0.9, label='Voynich, ' + modo, zorder=3)
        ax.set_yticks(list(ys))
        ax.set_yticklabels(nomi, fontsize=8.5)
        ax.set_ylim(len(nomi) - 0.4, -1.1)
        tutte = [posizione(ris[n], m) for n in nomi for m in MODI]
        ax.set_xlim(min(-0.6, min(tutte) - 0.1), 1.25)
        ax.set_xlabel('punteggio del testo decifrato: 0 = come un\'altra lingua, 1 = come la lingua stessa')
        ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.13), ncol=4, frameon=False, fontsize=7.5,
                  labelcolor=t['secondario'], handletextpad=0.2, columnspacing=1.0)
        piu = lambda x: ('%.1f' % x).replace('.', ',').replace('-', '−')
        grafici.titoli(fig, ax, t, 'Senza spazi, nessuna lingua legge il Voynich',
                       'Per ogni lingua e ogni modo di contare i segni, la chiave migliore trovata dal risolutore.\n'
                       'Un testo vero cifrato arriva a 1; il Voynich resta fra %s e %s, dalla parte di un\'altra lingua.'
                       % (piu(min(tutte)), piu(max(tutte))))
        grafici.salva(fig, RISULTATI, 'e17_ricottura', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e17_ricottura.json'), encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
