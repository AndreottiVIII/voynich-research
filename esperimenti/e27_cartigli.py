# -*- coding: utf-8 -*-
"""Esperimento 27: i nomi delle piante come cartigli.

Se una pagina dell'erbario parla di una pianta riconoscibile dal disegno, il suo
nome potrebbe stare nel testo, per esempio nella prima parola (molti erbari
aprono la voce col nome) o almeno nella prima riga. E' l'idea di Champollion
con i cartigli di Tolomeo e Cleopatra.

Le identificazioni delle piante non si raggiungono da qui alla fonte (voynich.nu,
HerbalGram, i blog di botanica voynichiana e le scansioni della Beinecke sono
bloccati). L'unico elenco raggiungibile e' la tabella FOLIO_PLANTS del toolkit
di Antenore Gatta (commit cb13763, licenza MIT), 58 fogli con un nome italiano e
un grado di confidenza: U universale, S forte, B da Bax, M moderata. Le fonti che
cita sono Sherwood e Petersen, Bax, Tucker e Janick, Zandbergen e il blog
voynichbotany; non si possono controllare. Le "moderate" vanno prese con cautela:
per esempio il foglio 2r, di solito identificato con una centaurea, qui e' un
elleboro, e molte cadono sui recto in fila. I nomi latini li aggiungiamo noi (i nomi usati
negli erbari medievali).

Il metodo non presuppone una lingua ne' un cifrario preciso. Un modello di
allineamento (il Model 1 di IBM per la traduzione automatica, con la parola
nulla) impara quanto spesso ogni segno del Voynich "produce" ogni lettera del
nome, su tutte le coppie (pagina, nome) insieme. Se i nomi sono scritti nella
pagina con un cifrario coerente, anche verboso o con segni nulli, le coppie
vere si spiegano meglio delle coppie sbagliate. La prova: la verosimiglianza
delle coppie vere contro quella di 1.000 abbinamenti rimescolati fra i fogli,
ciascuno con il suo modello imparato da capo. Due posizioni: la prima parola
della pagina e l'intera prima riga.

Controllo positivo: le stesse pagine, con il nome della pianta cifrato da un
cifrario verboso casuale (ogni lettera diventa uno o due segni, con due
varianti per lettera) messo al posto della prima parola, o di una parola a caso
della prima riga; anche con il 20% dei segni sbagliati. Se la prova non ritrova
questi nomi, non vale niente.

Scrive risultati/e27_cartigli.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ITERAZIONI = 20
RIMESCOLAMENTI = int(os.environ.get('RIMESCOLAMENTI', '1000'))
ERRORI = 0.2

# foglio, grado di confidenza (Gatta), nomi italiani (Gatta), nomi latini (nostri)
PIANTE = [
    ('f9v', 'U', 'viola', 'viola'), ('f48v', 'U', 'ruta', 'ruta'), ('f25r', 'S', 'timo', 'thymus'),
    ('f5v', 'S', 'malva', 'malva'), ('f37r', 'S', 'menta', 'menta'), ('f39r', 'S', 'croco', 'crocus'),
    ('f51v', 'S', 'salvia', 'salvia'), ('f44v', 'S', 'sedano', 'apium'), ('f41r', 'S', 'origano', 'origanum'),
    ('f29v', 'B', 'nigella', 'nigella'), ('f45v', 'S', 'lavanda', 'lavandula'),
    ('f31v', 'S', 'valeriana', 'valeriana'), ('f11r', 'U', 'rosmarino', 'rosmarinus'),
    ('f41v', 'B', 'coriandolo', 'coriandrum'), ('f44r', 'U', 'mandragora', 'mandragora'),
    ('f2r', 'M', 'elleboro', 'elleborus'), ('f4r', 'M', 'borragine', 'borago'),
    ('f6r', 'M', 'artemisia', 'artemisia'), ('f13r', 'M', 'ninfea', 'nymphaea'),
    ('f14r', 'M', 'piantagine', 'plantago'), ('f15r', 'M', 'calendula', 'calendula'),
    ('f17r', 'M', 'papavero', 'papaver'), ('f22r', 'M', 'sambuco', 'sambucus'), ('f23r', 'M', 'edera', 'hedera'),
    ('f25v', 'M', 'centaurea', 'centaurea'), ('f26r', 'M', 'genziana', 'gentiana'), ('f27r', 'M', 'felce', 'filix'),
    ('f28r', 'M', 'betonica', 'betonica'), ('f30r', 'M', 'aconito', 'aconitum'), ('f32r', 'M', 'verbena', 'verbena'),
    ('f33r', 'M', 'consolida', 'consolida'), ('f34r', 'M', 'achillea', 'millefolium'),
    ('f35r', 'M', 'assenzio', 'absinthium'), ('f36r', 'M', 'enula', 'enula'), ('f38r', 'M', 'cardo', 'carduus'),
    ('f40r', 'M', 'nepeta', 'nepeta'), ('f42r', 'M', 'belladonna', 'solatrum'),
    ('f43r', 'M', 'cicoria', 'cichorium'), ('f46r', 'M', 'finocchio', 'feniculum'),
    ('f47r', 'M', 'aneto', 'anethum'), ('f49r', 'M', 'cumino', 'ciminum'), ('f50r', 'M', 'basilico', 'basilicon'),
    ('f52r', 'M', 'prezzemolo', 'petroselinum'), ('f54r', 'M', 'camomilla', 'camomilla'),
    ('f55r', 'M', 'issopo', 'ysopus'), ('f56r', 'M', 'santoreggia', 'satureia'), ('f65r', 'M', 'ricino', 'ricinus'),
    ('f87r', 'M', 'ninfea', 'nymphaea'), ('f90r1', 'M', 'mirto', 'myrtus'), ('f93r', 'M', 'ginepro', 'iuniperus'),
    ('f94r', 'M', 'alloro', 'laurus'), ('f95r1', 'M', 'cipresso', 'cypressus'), ('f96r', 'M', 'quercia', 'quercus'),
    ('f99r', 'M', 'aloe', 'aloe'), ('f100r', 'M', 'rosa', 'rosa'), ('f101r', 'M', 'pepe', 'piper'),
    ('f16v', 'M', 'giglio', 'lilium'), ('f3r', 'M', 'ranuncolo', 'ranunculus'),
]


def prime_righe():
    """Per ogni pagina, la prima riga di testo in paragrafi, come lista di parole."""
    out = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        parole = [p for p in r.parole if trascrizione.pulita(p)]
        if r.pagina not in out and parole:
            out[r.pagina] = parole
    return out


# --- il modello di allineamento ------------------------------------------------

class Allineamento:
    """IBM Model 1: P(nome | segni) = prodotto sulle lettere della media di t(lettera | segno),
    con un segno nullo sempre presente. Le t si imparano con EM su tutte le coppie."""

    def __init__(self, coppie):
        self.segni = sorted({s for src, _ in coppie for s in src})
        self.lettere = sorted({c for _, tgt in coppie for c in tgt})
        si = {s: i + 1 for i, s in enumerate(self.segni)}          # 0 = segno nullo
        li = {c: i for i, c in enumerate(self.lettere)}
        self.sorgenti = [np.array([0] + [si[s] for s in src]) for src, _ in coppie]
        self.bersagli = [np.array([li[c] for c in tgt]) for _, tgt in coppie]

    def verosimiglianza(self, ordine, iterazioni=ITERAZIONI):
        """Log-verosimiglianza per lettera, con i nomi abbinati alle sorgenti nell'ordine dato."""
        t = np.full((len(self.segni) + 1, len(self.lettere)), 1.0 / len(self.lettere))
        coppie = [(self.sorgenti[i], self.bersagli[j]) for i, j in enumerate(ordine)]
        for _ in range(iterazioni):
            conti = np.zeros_like(t)
            for s, b in coppie:
                sotto = t[np.ix_(s, b)]
                np.add.at(conti, (s[:, None], b[None, :]), sotto / sotto.sum(0))
            t = conti / np.maximum(conti.sum(1, keepdims=True), 1e-300)
            t = np.where(conti.sum(1, keepdims=True) > 0, t, 1.0 / len(self.lettere))
        lv = sum(np.log(t[np.ix_(s, b)].mean(0)).sum() for s, b in coppie)
        return lv / sum(len(b) for _, b in coppie)


def prova(coppie, rnd, rimescolamenti=RIMESCOLAMENTI):
    modello = Allineamento(coppie)
    n = len(coppie)
    vera = modello.verosimiglianza(list(range(n)))
    caso = []
    for _ in range(rimescolamenti):
        ordine = list(range(n))
        rnd.shuffle(ordine)
        caso.append(modello.verosimiglianza(ordine))
    m = sum(caso) / len(caso)
    sd = (sum((x - m) ** 2 for x in caso) / (len(caso) - 1)) ** 0.5
    return OrderedDict([('coppie', n), ('vera', vera), ('caso_media', m), ('caso_sd', sd),
                        ('z', (vera - m) / sd if sd else 0.0),
                        ('p', (1 + sum(1 for x in caso if x >= vera)) / (1 + len(caso)))])


# --- il controllo positivo: nomi cifrati apposta --------------------------------

def cifrario_verboso(segni, rnd, varianti=2):
    """Ogni lettera ha `varianti` codici di uno o due segni del Voynich, diversi fra loro."""
    usati, chiave = set(), {}
    for c in 'abcdefghijklmnopqrstuvwxyz':
        chiave[c] = []
        while len(chiave[c]) < varianti:
            codice = tuple(rnd.choice(segni) for _ in range(rnd.choice((1, 2))))
            if codice not in usati:
                usati.add(codice)
                chiave[c].append(codice)
    return chiave


def cifra_nome(nome, chiave, segni, rnd, errori=0.0):
    out = [s for c in nome for s in rnd.choice(chiave[c])]
    return [rnd.choice(segni) if rnd.random() < errori else s for s in out]


def coppie_per(fogli, righe, nome_di, glifi, dove, cifrati=None, rnd=None):
    """Le coppie (segni della sorgente, lettere del nome) per i fogli dati."""
    out = []
    for f in fogli:
        parole = [glifi(p) for p in righe[f]]
        if cifrati is not None:
            posto = 0 if dove == 'prima parola' else rnd.randrange(len(parole))
            parole[posto] = cifrati[f]
        sorgente = parole[0] if dove == 'prima parola' else [s for p in parole for s in p]
        out.append((sorgente, nome_di[f]))
    return out


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    righe = prime_righe()
    presenti = [p for p in PIANTE if p[0] in righe]
    mancanti = [p[0] for p in PIANTE if p[0] not in righe]
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    segni_comuni = [s for s, _ in Counter(s for p in trascrizione.parole(corrente) for s in glifi(p)).most_common(20)]
    ris = OrderedDict([('fogli', len(presenti)), ('senza_testo_in_paragrafi', mancanti), ('prove', OrderedDict())])
    gruppi = OrderedDict([('gradi U, S, B', [p for p in presenti if p[1] != 'M']), ('tutti', presenti)])
    for gruppo, piante in gruppi.items():
        fogli = [p[0] for p in piante]
        for lingua, colonna in (('italiano', 2), ('latino', 3)):
            nome_di = {p[0]: p[colonna] for p in piante}
            for dove in ('prima parola', 'prima riga'):
                rnd = random.Random(27)
                casi = OrderedDict()
                casi['Voynich'] = coppie_per(fogli, righe, nome_di, glifi, dove)
                chiave = cifrario_verboso(segni_comuni, rnd)
                for etichetta, errori in (('nome cifrato (controllo positivo)', 0.0),
                                          ('nome cifrato, 20% di segni sbagliati', ERRORI)):
                    cifrati = {f: cifra_nome(nome_di[f], chiave, segni_comuni, rnd, errori) for f in fogli}
                    casi[etichetta] = coppie_per(fogli, righe, nome_di, glifi, dove, cifrati, rnd)
                for caso, coppie in casi.items():
                    chiave_ris = ' | '.join((gruppo, lingua, dove, caso))
                    ris['prove'][chiave_ris] = prova(coppie, random.Random(270))
                    r = ris['prove'][chiave_ris]
                    print('%-80s z=%6.2f p=%.3f' % (chiave_ris, r['z'], r['p']), flush=True)
    with open(os.path.join(RISULTATI, 'e27_cartigli.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def num(x, cifre=2):
    return ('%.*f' % (cifre, x)).replace('.', ',')


def scrivi_tabella(ris):
    out = ['# Esperimento 27: i nomi delle piante come cartigli', '',
           'Identificazioni dalla tabella FOLIO_PLANTS del toolkit di Antenore Gatta (%d fogli con testo in '
           'paragrafi; senza: %s). Per ogni prova: la verosimiglianza per lettera dei nomi dato il testo, col '
           'modello di allineamento imparato sulle coppie vere, contro %s abbinamenti rimescolati (media ± '
           'deviazione, z, e p: la quota di rimescolamenti che fanno almeno altrettanto).' % (
               ris['fogli'], ', '.join(ris['senza_testo_in_paragrafi']) or 'nessuno',
               '{:,}'.format(RIMESCOLAMENTI).replace(',', '.')), '',
           '| fogli | nomi | dove | testo | coppie | vere | rimescolate | z | p |',
           '|---|---|---|---|---|---|---|---|---|']
    for chiave, r in ris['prove'].items():
        gruppo, lingua, dove, caso = chiave.split(' | ')
        out.append('| %s | %s | %s | %s | %d | %s | %s ± %s | %s | %s |' % (
            gruppo, lingua, dove, caso, r['coppie'], num(r['vera'], 3), num(r['caso_media'], 3),
            num(r['caso_sd'], 3), num(r['z'], 1), num(r['p'], 3)))
    out += ['', 'Il controllo positivo mette al posto della prima parola (o di una parola a caso della prima riga) il '
            'nome cifrato con un cifrario verboso casuale: ogni lettera ha due codici di uno o due segni fra i 20 '
            'più comuni del Voynich.', '',
            'Cautele. Le identificazioni non si possono controllare alla fonte da qui, e quelle di grado M sono '
            'deboli (il foglio 2r, di solito identificato con una centaurea, qui è un elleboro). Con la prima riga '
            'intera la prova ha poca forza: sui 15 fogli migliori ritrova il nome cifrato solo in latino e senza '
            'errori. Un esito negativo esclude il nome scritto lettera per lettera, con un cifrario coerente, in '
            'italiano o in latino e in quella posizione; non esclude altre lingue, altre posizioni o identificazioni '
            'diverse.']
    with open(os.path.join(RISULTATI, 'e27_cartigli.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e27_cartigli.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
