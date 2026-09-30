# -*- coding: utf-8 -*-
"""Esperimento 26: due decifrazioni pubblicate, alla prova dei controlli.

Due proposte recenti hanno il codice pubblico, e si possono rifare:

- Scott Schechter, "voynich-decoded" (2026): un glossario di 4.063 parole EVA,
  ognuna con una parola latina (qualcuna occitana o ebraica); le forche
  composte (cth, ckh, cph, cfh) sono nulle e si tolgono se la parola non e' nel
  glossario. Dichiara: l'87,8% delle parole decifrate contro il 2,1% di stringhe
  EVA a caso; il 79-81% su pagine lasciate fuori; 94 frasi di tre parole
  ripetute contro 16 nel testo rimescolato; la legge di Zipf con esponente
  -0,919, "come una lingua naturale".
- Antenore Gatta, "voynich-toolkit" (2026): una corrispondenza segno per segno
  EVA -> consonanti ebraiche, letta da destra a sinistra. Lui stesso conclude
  che nessuna pagina si legge, ma che nelle parole di 3-4 lettere c'e' un
  segnale (le parole ebraiche trovate sono piu' che con corrispondenze a caso).

Il controllo che manca a entrambe e' lo stesso: un testo che non dice niente
ma somiglia al Voynich. Qui e' il testo del generatore ad autocitazione di Timm
e Schinner (esperimenti 22-23), che copia e ritocca le proprie parole: se la
stessa decifrazione "legge" anche quello, non e' una lettura.

Per Schechter (la sua trascrizione e il suo modo di dividere le righe,
controllando che la copertura sia la sua):
- copertura, contro quella di un glossario qualunque con lo stesso numero di
  voci: le parole piu' frequenti del testo, con un significato qualsiasi;
- la prova sulle pagine lasciate fuori, contro la semplice quota di parole
  delle pagine pari che compaiono gia' nelle dispari;
- il glossario applicato al testo senza messaggio;
- se l'ordine delle parole latine e' latino: quante coppie vicine compaiono
  una accanto all'altra nel latino vero (Latin Library, esclusi i testi di
  prova), contro le stesse parole rimescolate nella riga; per paragone un
  latino vero (Apicio e Isidoro sulle piante, fuori dal riferimento) e lo
  stesso glossario con i significati rimescolati fra le voci;
- le frasi di tre parole ripetute e l'esponente di Zipf, anche sul Voynich
  non decifrato e sul testo senza messaggio.

Per Gatta: la quota di parole decifrate (di 3 e 4 consonanti, e di 5 o piu')
che sono parole ebraiche (le forme della Bibbia in ebraico, senza vocali: i primi
due milioni di caratteri della Bibbia in 100 lingue, cioe' il Nuovo Testamento e buona
parte dell'Antico), con la sua corrispondenza e con 200
corrispondenze a caso; e la stessa prova con una corrispondenza cercata apposta
per ogni testo (salita a gradini sulla quota), Voynich e testo senza messaggio.

Scrive risultati/e26_decifrazioni_pubblicate.json e .md.
"""
import json, math, os, random, re, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e17_ricottura as e17
import e22_timm_schinner as e22
import e23_giunture as e23

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCHECHTER = os.path.join(lingue.SORGENTI, 'voynich-decoded')
PERMUTAZIONI = 20
MESCOLAMENTI = 10
CASUALI = 200
PASSI_SALITA = 3000


# --- Schechter: il glossario e il decodificatore (decode.js, rifatto) --------

def glossario():
    testo = open(os.path.join(SCHECHTER, 'tools', 'glossary-export.js'), encoding='utf-8').read()
    return json.loads(testo[testo.index('{'):testo.rindex('}') + 1])


DIGRAMMI = ('cth', 'cph', 'cfh', 'ckh', 'sh', 'ch', 'ii', 'ee')
FORCHE = {'cth', 'ckh', 'cph', 'cfh'}


def segni(parola):
    s = re.sub(r'[.<>%$\s]', '', parola)
    out, i = [], 0
    while i < len(s):
        d = next((d for d in DIGRAMMI if s.startswith(d, i)), s[i])
        out.append(d)
        i += len(d)
    return out


def senza_forche(parola):
    return ''.join(t for t in segni(parola) if t not in FORCHE)


def decodifica(parola, gloss):
    pulita = re.sub(r'[<>%$?*!{}\[\]()]', '', parola).strip()
    if not pulita:
        return None
    if pulita in gloss:
        return gloss[pulita]
    s = senza_forche(pulita)
    if s != pulita and s in gloss:
        return gloss[s]
    return None


def righe_schechter():
    """Le righe della trascrizione di Takahashi come le legge decode.js: (foglio, parole)."""
    righe = []
    for riga in open(os.path.join(SCHECHTER, 'tools', 'eva-data', 'eva_takahashi.txt'), encoding='utf-8'):
        riga = riga.rstrip('\n')
        if riga.startswith('#') or not riga.strip():
            continue
        m = re.match(r'^<(f\d+[rv]\d?)\.(\d+),[^>]+>\s+(.+)', riga)
        if not m:
            continue
        t = m.group(3).replace('<%>', '').replace('<$>', '').replace('<->', '.')
        t = re.sub(r'\{[^}]*\}', '', re.sub(r'<[^>]*>', '', t)).strip()
        parole = [re.sub(r'[?*!]', '', p).strip() for p in re.split(r'\.+', t)]
        parole = [p for p in parole if p]
        if parole:
            righe.append((m.group(1), parole))
    return righe


def righe_generate(pagine):
    """Il testo del generatore nello stesso formato: una pagina vale un foglio."""
    return [('p%d' % i, r) for i, p in enumerate(pagine) for r in p if r]


def copertura(righe, gloss):
    parole = [p for _, r in righe for p in r]
    return sum(1 for p in parole if decodifica(p, gloss)) / len(parole)


def glossario_dei_frequenti(righe, n):
    """Un glossario qualunque con n voci: le n parole piu' frequenti del testo."""
    conta = Counter(p for _, r in righe for p in r)
    return {p: 'X' for p, _ in conta.most_common(n)}


def fogli_dispari(foglio):
    return int(re.sub(r'\D', '', foglio.split('v')[0].split('r')[0]) or 0) % 2 == 1


def lasciate_fuori(righe, gloss):
    """La prova di Schechter (glossario ridotto alle voci viste nei fogli dispari, provato
    sui pari e viceversa) e la quota di parole che compaiono gia' nell'altra meta'."""
    out = {}
    for nome, prima in (('pari', True), ('dispari', False)):
        allenamento = [r for f, r in righe if fogli_dispari(f) == prima]
        prova = [p for f, r in righe if fogli_dispari(f) != prima for p in r]
        viste = {p for r in allenamento for p in r} | {senza_forche(p) for r in allenamento for p in r}
        ridotto = {k: v for k, v in gloss.items() if k in viste}
        out['glossario_su_' + nome] = sum(1 for p in prova if decodifica(p, ridotto)) / len(prova)
        out['parole_gia_viste_su_' + nome] = sum(
            1 for p in prova if p in viste or senza_forche(p) in viste) / len(prova)
    return out


# --- l'ordine delle parole: e' latino? ---------------------------------------

def norma(parola):
    return parola.lower().replace('j', 'i').replace('v', 'u')


class Riferimento:
    """Coppie di parole vicine nella Latin Library (esclusi i testi tecnici di prova)."""

    def __init__(self, servono):
        parole = [norma(p) for p in e17.latino_ampio()]
        self.parole = len(parole)
        self.vocabolario = Counter(parole)
        self.coppie = set()
        for a, b in zip(parole, parole[1:]):
            if a in servono and b in servono:
                self.coppie.add((a, b))

    def attestate(self, righe):
        """Fra le coppie vicine di parole latine note, la quota che compare nel riferimento."""
        tot = buone = 0
        for r in righe:
            for a, b in zip(r, r[1:]):
                if a in self.vocabolario and b in self.vocabolario:
                    tot += 1
                    buone += (a, b) in self.coppie
        return buone / tot if tot else float('nan'), tot


def rimescola_nelle_righe(righe, rnd):
    out = []
    for r in righe:
        r = list(r)
        rnd.shuffle(r)
        out.append(r)
    return out


def ordine_latino(righe, rif, seme=26):
    """Coppie attestate nell'ordine del testo e con le parole rimescolate nella riga."""
    vere, n = rif.attestate(righe)
    rnd = random.Random(seme)
    caso = sum(rif.attestate(rimescola_nelle_righe(righe, rnd))[0] for _ in range(MESCOLAMENTI)) / MESCOLAMENTI
    return {'coppie': n, 'attestate': vere, 'attestate_rimescolate': caso, 'rapporto': vere / caso}


def decifrate(righe, gloss):
    """Le righe tradotte; le parole non decifrate restano come segnaposto che non si accoppia."""
    out = []
    for _, r in righe:
        t = []
        for p in r:
            v = decodifica(p, gloss)
            t.append(norma(v) if v else '#' + p)
        out.append(t)
    return out


def glossario_rimescolato(gloss, rnd):
    chiavi, valori = list(gloss), list(gloss.values())
    rnd.shuffle(valori)
    return dict(zip(chiavi, valori))


# --- frasi ripetute e Zipf -----------------------------------------------------

def frasi_ripetute(righe_con_fogli, minimo=3):
    """Frasi di tre parole (tutte decifrate, se c'e' la traduzione) che ricorrono almeno
    `minimo` volte in piu' di un foglio."""
    dove, quante = {}, Counter()
    for f, r in righe_con_fogli:
        for t in zip(r, r[1:], r[2:]):
            if any(p.startswith('#') for p in t):
                continue
            quante[t] += 1
            dove.setdefault(t, set()).add(f)
    return sum(1 for t, n in quante.items() if n >= minimo and len(dove[t]) > 1)


def rimescola_tutto(righe_con_fogli, rnd):
    tutte = [p for _, r in righe_con_fogli for p in r]
    rnd.shuffle(tutte)
    out, i = [], 0
    for f, r in righe_con_fogli:
        out.append((f, tutte[i:i + len(r)]))
        i += len(r)
    return out


def zipf(parole, ranghi=1000):
    """Pendenza di log(frequenza) su log(rango), sui primi `ranghi` ranghi."""
    f = [n for _, n in Counter(parole).most_common(ranghi)]
    xs = [math.log(i + 1) for i in range(len(f))]
    ys = [math.log(n) for n in f]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


# --- Gatta: la corrispondenza EVA -> ebraico (full_decode.py, rifatta) --------

GATTA = {'a': 'y', 'c': 'A', 'd': 'r', 'e': 'p', 'f': 'l', 'g': 'X', 'h': 'E', 'k': 't', 'l': 'm',
         'm': 'g', 'n': 'd', 'o': 'w', 'p': 'l', 'r': 'h', 's': 'n', 't': 'J', 'y': 'S',
         '\x01': 'h', '\x02': 'r', '\x03': 'k'}      # ii = he, i da sola = resh, ch = kaf
EBRAICO = dict(zip('אבגדהוזחטיכךלמםנןסעפףצץקרשת', 'AbgdhwzXJykklmmnnsEppCCqrSt'))
LETTERE_EBRAICHE = 'AbgdhwzXJyklmnsEpCqrSt'


def prepara_gatta(parola):
    w = parola.replace('ch', '\x03')
    if w.startswith('qo'):
        w = w[2:]
    elif w.startswith('q') and len(w) > 1:
        w = w[1:]
    w = re.sub(r'i{3,}', lambda m: '\x01' * (len(m.group()) // 2) + ('\x02' if len(m.group()) % 2 else ''), w)
    return w.replace('ii', '\x01').replace('i', '\x02')


def in_ebraico(preparata, mappa):
    lettere = [mappa.get(c, '?') for c in reversed(preparata)]
    if lettere and lettere[0] == 'd':
        lettere[0] = 'b'           # dalet iniziale -> bet
    if lettere and lettere[0] == 'h':
        lettere[0] = 's'           # he iniziale -> samekh
    return ''.join(lettere)


def lessico_ebraico():
    parole = lingue.parole('Hebrew')
    return {''.join(EBRAICO.get(c, '') for c in p) for p in parole} - {''}


CLASSI = (('3-4', 3, 4), ('5+', 5, 99))


def quota_ebraica(tipi, mappa, lessico, dettagli=False):
    """Quota delle parole (contate con la frequenza) che diventano parole ebraiche,
    per le decifrate di 3-4 consonanti e di 5 o piu'."""
    out = {}
    for nome, lo, hi in CLASSI:
        tot, trovate = 0, Counter()
        for w, n in tipi:
            h = in_ebraico(w, mappa)
            if lo <= len(h) <= hi and '?' not in h:
                tot += n
                if h in lessico:
                    trovate[w] = n
        out[nome] = sum(trovate.values()) / tot if tot else 0.0
        if dettagli:
            leggibile = lambda w: w.replace('\x01', 'ii').replace('\x02', 'i').replace('\x03', 'ch')
            out[nome + ' tipi'] = len(trovate)
            out[nome + ' prime'] = [[leggibile(w), in_ebraico(w, mappa), n] for w, n in trovate.most_common(3)]
            out[nome + ' quota delle prime due'] = (sum(n for _, n in trovate.most_common(2)) /
                                                   sum(trovate.values()) if trovate else 0.0)
    return out


def mappa_a_caso(rnd):
    chiavi = sorted(GATTA)
    return dict(zip(chiavi, rnd.sample(LETTERE_EBRAICHE, len(chiavi))))


def salita(tipi, lessico, rnd, passi=PASSI_SALITA):
    """Una corrispondenza cercata apposta: scambi e sostituzioni che alzano la quota."""
    mappa = mappa_a_caso(rnd)
    punti = lambda m: sum(quota_ebraica(tipi, m, lessico).values())
    migliore = punti(mappa)
    for _ in range(passi):
        nuova = dict(mappa)
        k = rnd.choice(sorted(nuova))
        altra = rnd.choice(LETTERE_EBRAICHE)
        vecchia = nuova[k]
        for j, v in nuova.items():
            if v == altra:
                nuova[j] = vecchia
        nuova[k] = altra
        p = punti(nuova)
        if p >= migliore:
            mappa, migliore = nuova, p
    return mappa


def prova_gatta(parole, lessico, rnd):
    tipi = Counter(prepara_gatta(p) for p in parole if p)
    tipi = [(w, n) for w, n in tipi.items() if w]
    vera = quota_ebraica(tipi, GATTA, lessico, dettagli=True)
    caso = [quota_ebraica(tipi, mappa_a_caso(rnd), lessico) for _ in range(CASUALI)]
    cercata = salita(tipi, lessico, rnd)
    q = quota_ebraica(tipi, cercata, lessico, dettagli=True)
    out = OrderedDict()
    for k, _, _ in CLASSI:
        xs = [c[k] for c in caso]
        m = sum(xs) / len(xs)
        sd = (sum((x - m) ** 2 for x in xs) / (len(xs) - 1)) ** 0.5
        out[k] = OrderedDict([('sua', vera[k]), ('caso_media', m), ('caso_sd', sd),
                              ('z', (vera[k] - m) / sd if sd else 0.0),
                              ('cercata', q[k]), ('z_cercata', (q[k] - m) / sd if sd else 0.0)])
        for chi, d in (('sua', vera), ('cercata', q)):
            for campo in ('tipi', 'prime', 'quota delle prime due'):
                out[k]['%s %s' % (chi, campo)] = d['%s %s' % (k, campo)]
    return out


# --- tutto insieme ---------------------------------------------------------------

def testi_senza_messaggio():
    t = OrderedDict()
    t['Timm e Schinner, programma pubblicato'] = righe_generate(e22.genera(e22.SEMI[0]))
    tabella = os.path.join(e23.LAVORO, 'giunture.tsv')
    os.makedirs(e23.LAVORO, exist_ok=True)
    e23.tabella_giunture(tabella)
    pagine, _ = e23.genera(e23.compila(), tabella, 3.0, e22.SEMI[0])
    t['Timm e Schinner, con le giunture'] = righe_generate(pagine)
    return t


def latino_di_prova():
    parole = [norma(p) for nome in ('Apicio, ricette di cucina', 'Isidoro XVII, piante') for p in lingue.genere(nome)]
    return [('l%d' % (i // 290), parole[i:i + 8]) for i in range(0, len(parole) - 7, 8)]


def main():
    gloss = glossario()
    voynich = righe_schechter()
    senza = testi_senza_messaggio()
    latino = latino_di_prova()
    ris = OrderedDict()

    # 1. copertura
    cop = OrderedDict()
    cop['voci del glossario'] = len(gloss)
    cop['significati diversi'] = len(set(gloss.values()))
    cop['parole del Voynich'] = sum(len(r) for _, r in voynich)
    cop['Voynich'] = copertura(voynich, gloss)
    usate = {p for _, r in voynich for p in r if decodifica(p, gloss)}
    conta = Counter(p for _, r in voynich for p in r)
    cop['parole diverse decifrate'] = len(usate)
    cop['di cui compaiono una volta sola'] = sum(1 for p in usate if conta[p] == 1)
    cop['glossario qualunque con altrettante voci'] = copertura(voynich, glossario_dei_frequenti(voynich, len(usate)))
    for nome, righe in senza.items():
        cop[nome] = copertura(righe, gloss)
    ris['copertura'] = cop
    print(json.dumps(cop, ensure_ascii=False, indent=1))

    # 2. pagine lasciate fuori
    ris['lasciate_fuori'] = OrderedDict([('Voynich', lasciate_fuori(voynich, gloss))] +
                                        [(n, lasciate_fuori(r, gloss)) for n, r in senza.items()])
    print(json.dumps(ris['lasciate_fuori'], ensure_ascii=False, indent=1))

    # 3. l'ordine delle parole
    rnd = random.Random(26)
    testi = OrderedDict()
    testi['Voynich decifrato'] = decifrate(voynich, gloss)
    for nome, righe in senza.items():
        testi[nome + ', decifrato'] = decifrate(righe, gloss)
    testi['latino vero (Apicio, Isidoro XVII)'] = [r for _, r in latino]
    rimescolati = [decifrate(voynich, glossario_rimescolato(gloss, rnd)) for _ in range(PERMUTAZIONI)]
    servono = {p for t in list(testi.values()) + rimescolati for r in t for p in r}
    rif = Riferimento(servono)
    ordine = OrderedDict((nome, ordine_latino(t, rif)) for nome, t in testi.items())
    perm = [ordine_latino(t, rif, seme=i) for i, t in enumerate(rimescolati)]
    ordine['Voynich, significati rimescolati fra le voci'] = {
        k: sum(p[k] for p in perm) / len(perm) for k in ('coppie', 'attestate', 'attestate_rimescolate', 'rapporto')}
    ordine['Voynich, significati rimescolati fra le voci']['rapporto_max'] = max(p['rapporto'] for p in perm)
    ris['ordine_latino'] = ordine
    ris['riferimento_parole'] = rif.parole
    print(json.dumps(ordine, ensure_ascii=False, indent=1))

    # 4. frasi ripetute e Zipf
    frasi = OrderedDict()
    casi = OrderedDict()
    casi['Voynich decifrato'] = [(f, t) for (f, _), t in zip(voynich, testi['Voynich decifrato'])]
    casi['Voynich non decifrato'] = voynich
    for nome, righe in senza.items():
        casi[nome + ', decifrato'] = [(f, t) for (f, _), t in zip(righe, testi[nome + ', decifrato'])]
        casi[nome + ', non decifrato'] = righe
    casi['latino vero (Apicio, Isidoro XVII)'] = latino
    for nome, righe in casi.items():
        rnd = random.Random(3)
        parole = [p for _, r in righe for p in r if not p.startswith('#')]
        frasi[nome] = {'frasi': frasi_ripetute(righe),
                       'frasi_rimescolate': sum(frasi_ripetute(rimescola_tutto(righe, rnd)) for _ in range(5)) / 5,
                       'zipf': zipf(parole), 'parole': len(parole)}
    ris['frasi_e_zipf'] = frasi
    print(json.dumps(frasi, ensure_ascii=False, indent=1))

    # 5. Gatta
    lessico = lessico_ebraico()
    rnd = random.Random(5)
    gatta = OrderedDict()
    gatta['Voynich'] = prova_gatta([p for _, r in voynich for p in r], lessico, rnd)
    for nome, righe in senza.items():
        gatta[nome] = prova_gatta([p for _, r in righe for p in r], lessico, rnd)
    ris['gatta'] = gatta
    ris['lessico_ebraico'] = len(lessico)
    print(json.dumps(gatta, ensure_ascii=False, indent=1))

    with open(os.path.join(RISULTATI, 'e26_decifrazioni_pubblicate.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def pc(x, cifre=1):
    return ('%.*f%%' % (cifre, 100 * x)).replace('.', ',')


def num(x, cifre=2):
    return ('%.*f' % (cifre, x)).replace('.', ',')


def migliaia(n):
    return '{:,}'.format(int(round(n))).replace(',', '.')


def scrivi_tabella(ris):
    c, lf, o, fz, g = (ris['copertura'], ris['lasciate_fuori'], ris['ordine_latino'], ris['frasi_e_zipf'],
                       ris['gatta'])
    tp, tg = 'Timm e Schinner, programma pubblicato', 'Timm e Schinner, con le giunture'
    out = ['# Esperimento 26: due decifrazioni pubblicate, alla prova dei controlli', '',
           'Il testo senza messaggio è quello del generatore ad autocitazione di Timm e Schinner '
           '(esperimenti 22 e 23): parole copiate e ritoccate, nessun significato.', '',
           '## Schechter: un glossario EVA → latino', '',
           'Glossario di %s voci con %s significati diversi; la sua trascrizione (Takahashi) e il suo modo di '
           'leggerla, rifatti in Python: %s parole, copertura %s come dà il suo programma.' % (
               migliaia(c['voci del glossario']), migliaia(c['significati diversi']),
               migliaia(c['parole del Voynich']), pc(c['Voynich'])), '',
           '| testo | parole decifrate |', '|---|---|',
           '| Voynich, col suo glossario | %s |' % pc(c['Voynich']),
           '| Voynich, con un glossario qualunque: le %s parole più frequenti, senza significato | %s |' % (
               migliaia(c['parole diverse decifrate']), pc(c['glossario qualunque con altrettante voci'])),
           '| testo senza messaggio (%s), col suo glossario | %s |' % (tp, pc(c[tp])),
           '| testo senza messaggio (%s), col suo glossario | %s |' % (tg, pc(c[tg])), '',
           'Le parole diverse che il glossario decifra sono %s; %s compaiono una volta sola nel manoscritto.' % (
               migliaia(c['parole diverse decifrate']), migliaia(c['di cui compaiono una volta sola'])), '',
           '**Pagine lasciate fuori.** Il glossario ridotto alle parole viste nei fogli dispari, provato sui pari '
           '(e viceversa), come fa lui; accanto, la quota di parole dei fogli di prova che compaiono già '
           'nell\'altra metà, qualunque significato abbiano:', '',
           '| testo | glossario ridotto, sui pari | già viste, sui pari | glossario ridotto, sui dispari | '
           'già viste, sui dispari |', '|---|---|---|---|---|']
    for nome, r in lf.items():
        out.append('| %s | %s | %s | %s | %s |' % (nome, pc(r['glossario_su_pari']), pc(r['parole_gia_viste_su_pari']),
                                                   pc(r['glossario_su_dispari']),
                                                   pc(r['parole_gia_viste_su_dispari'])))
    out += ['', '**L\'ordine delle parole.** Fra le coppie di parole vicine che il latino conosce, quante compaiono '
            'una accanto all\'altra nella Latin Library (%s parole, esclusi i testi di prova); poi le stesse parole '
            'rimescolate dentro la riga. Se l\'ordine è latino, le coppie vere sono attestate più di quelle '
            'rimescolate.' % migliaia(ris['riferimento_parole']), '',
            '| testo | coppie | attestate | rimescolate | rapporto |', '|---|---|---|---|---|']
    for nome, r in o.items():
        extra = ' (al massimo %s)' % num(r['rapporto_max']) if 'rapporto_max' in r else ''
        out.append('| %s | %s | %s | %s | ×%s%s |' % (nome, migliaia(r['coppie']), pc(r['attestate']),
                                                      pc(r['attestate_rimescolate']), num(r['rapporto']), extra))
    out += ['', 'Per i significati rimescolati: media di %d glossari con gli stessi valori spostati a caso fra le '
            'voci.' % PERMUTAZIONI, '',
            '**Frasi ripetute e legge di Zipf.** Frasi di tre parole (tutte decifrate, dove c\'è la traduzione) che '
            'ricorrono almeno tre volte in più di un foglio, nel testo e rimescolando tutte le parole (media di 5); '
            'pendenza di log(frequenza) su log(rango) sui primi 1.000 ranghi.', '',
            '| testo | parole | frasi ripetute | rimescolato | Zipf |', '|---|---|---|---|---|']
    for nome, r in fz.items():
        out.append('| %s | %s | %d | %s | %s |' % (nome, migliaia(r['parole']), r['frasi'],
                                                   num(r['frasi_rimescolate'], 1), num(r['zipf'])))
    out += ['', '## Gatta: una corrispondenza EVA → consonanti ebraiche', '',
            'Quota delle parole decifrate che sono forme della Bibbia in ebraico (%s forme senza vocali, dal Nuovo '
            'Testamento e da buona parte dell\'Antico), '
            'contate con la loro frequenza: con la sua corrispondenza, con %d corrispondenze a caso (media e z), e '
            'con una corrispondenza cercata apposta per quel testo (%s passi di salita).' % (
                migliaia(ris['lessico_ebraico']), CASUALI, migliaia(PASSI_SALITA)), '',
            '| testo | consonanti | sua | a caso | z | cercata apposta | z |', '|---|---|---|---|---|---|---|']
    for nome, r in g.items():
        for k, _, _ in CLASSI:
            x = r[k]
            out.append('| %s | %s | %s | %s ± %s | %s | %s | %s |' % (
                nome, k, pc(x['sua']), pc(x['caso_media']), pc(x['caso_sd']), num(x['z'], 1),
                pc(x['cercata']), num(x['z_cercata'], 1)))
    v5 = g['Voynich']['5+']
    out += ['', 'Sul Voynich, con la sua corrispondenza, le parole di 5 o più consonanti trovate sono %d forme '
            'diverse, e le due più frequenti (%s) fanno il %s dei casi. Con la corrispondenza cercata apposta, '
            'la più frequente è %s → %s, %d volte.' % (
                v5['sua tipi'], ', '.join('%s → %s, %d volte' % tuple(p) for p in v5['sua prime'][:2]),
                pc(v5['sua quota delle prime due'], 0), *v5['cercata prime'][0])]
    with open(os.path.join(RISULTATI, 'e26_decifrazioni_pubblicate.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e26_decifrazioni_pubblicate.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
