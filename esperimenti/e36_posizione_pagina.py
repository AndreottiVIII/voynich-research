# -*- coding: utf-8 -*-
"""Esperimento 36: in quale posizione della parola sta l'informazione sulla pagina?

Ipotesi della lingua filosofica (rassegna/lingue_filosofiche.md): una pagina che tratta
un argomento usa parole della stessa classe, e la classe sta nel prefisso; quindi
l'informazione sulla pagina deve concentrarsi nel primo segno. Si confronta il profilo
del Voynich con controlli di cui si sa la risposta.

Preregistrazione: preregistrazioni/e36-e38.md. Misura: analisi/posizioni.py (D-006).
Serve Java (generatore di Timm e Schinner). Scrive risultati/e36_posizione_pagina.json e .md.
"""
import json, os, random, sys
from collections import Counter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, posizioni, trascrizione
from posizioni import Blocco

RISULTATI = os.path.join(QUI, '..', 'risultati')
PLINIO = os.path.join(lingue.SORGENTI, 'voynich-units', 'herbal')
NAIBBE = os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
LIBRI = range(20, 28)                  # Plinio, piante medicinali
PAROLE_PER_LIBRO = 4400                 # 8 libri x 4400 = 35.200 parole, come il Voynich
PAROLE_PAGINA, PAROLE_RIGA = 170, 9
PAGINA_MIN = 40                         # parole utili minime per tenere una pagina del Voynich
CATEGORIE, FREQ_MIN = 20, 5
DIVIDI = misure.divisore(misure.GLIFI_EVA)

# inventari dei codici sintetici: segni EVA, cosi' si tagliano come il Voynich
PREFISSI = ['q', 'o', 'd', 's', 'y', 'ch', 'sh', 'k', 't', 'p', 'f', 'l', 'r', 'a', 'e', 'i',
            'n', 'm', 'g', 'cth', 'ckh']          # 20 categorie + la residua
CIFRE = ['a', 'e', 'i', 'o', 'y', 'k', 't', 'd']
DESINENZE = ['n', 'l', 'r', 'm', 's', 'y', 'g', 'dy', 'in', 'ar', 'al', 'or', 'ol', 'am', 'ey', 'iin']
ALFABETO_CASUALE = PREFISSI[:20]


# ---------------------------------------------------------------- testi

def plinio():
    """Parole di Plinio, libri 20-27: (libro, parole) con PAROLE_PER_LIBRO parole ciascuno."""
    per_libro = {}
    for nome in sorted(os.listdir(PLINIO)):
        if not nome.startswith('pliny'):
            continue
        for riga in open(os.path.join(PLINIO, nome), encoding='utf-8'):
            if not riga.startswith('<'):
                continue
            etichetta, _, testo = riga.partition('>')
            libro = int(etichetta.split()[-1].split('.')[0])
            if libro in LIBRI:
                per_libro.setdefault(libro, []).extend(lingue.normalizza(testo).split())
    return [(libro, per_libro[libro][:PAROLE_PER_LIBRO]) for libro in LIBRI]


def categorie_semantiche(parole):
    """Categoria di ogni tipo frequente: k-medie sui vettori di co-occorrenza (seme fisso)."""
    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    freq = Counter(parole)
    tipi = sorted(t for t, c in freq.items() if c >= FREQ_MIN)
    indice = {t: i for i, t in enumerate(tipi)}
    contesti = [t for t, _ in freq.most_common(1000)]
    cindice = {t: i for i, t in enumerate(contesti)}
    m = np.zeros((len(tipi), len(contesti)))
    for i, w in enumerate(parole):
        if w not in indice:
            continue
        for j in range(max(0, i - 5), min(len(parole), i + 6)):
            if j != i and parole[j] in cindice:
                m[indice[w], cindice[parole[j]]] += 1
    m = np.log1p(m)
    x = TruncatedSVD(50, random_state=0).fit_transform(m)
    x /= np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
    etichette = KMeans(CATEGORIE, random_state=0, n_init=10).fit_predict(x)
    return {t: int(e) for t, e in zip(tipi, etichette)}


def in_base(n, cifre, minimo=2):
    out = []
    while True:
        out.append(cifre[n % len(cifre)])
        n //= len(cifre)
        if n == 0 and len(out) >= minimo:
            break
    return ''.join(reversed(out))


def codice_semantico(parole, categorie, alfabetico=True):
    """prefisso di categoria + indice nella categoria + desinenza dalle ultime due lettere.

    alfabetico=False e' la versione preregistrata: l'indice segue la prima comparsa della
    parola nel testo, e cosi' porta informazione sulla pagina (DECISIONI.md, D-007)."""
    finali = [f for f, _ in Counter(w[-2:] for w in parole).most_common(len(DESINENZE) - 1)]
    desinenza = {f: DESINENZE[i] for i, f in enumerate(finali)}
    ordine = sorted(set(parole)) if alfabetico else list(dict.fromkeys(parole))
    posto, codici = Counter(), {}
    for w in ordine:
        cat = categorie.get(w, CATEGORIE)                # CATEGORIE = la residua
        codici[w] = PREFISSI[cat] + in_base(posto[cat], CIFRE)
        posto[cat] += 1
    return [codici[w] + desinenza.get(w[-2:], DESINENZE[-1]) for w in parole]


def codice_casuale(parole, seme=0):
    rnd = random.Random(seme)
    codici = {}
    for w in parole:
        if w not in codici:
            codici[w] = ''.join(rnd.choice(ALFABETO_CASUALE) for _ in range(rnd.randint(4, 6)))
    return [codici[w] for w in parole]


def pagine_da_parole(parole):
    """Pagine di PAROLE_PAGINA parole in righe di PAROLE_RIGA."""
    pagine = []
    for i in range(0, len(parole) - PAROLE_PAGINA + 1, PAROLE_PAGINA):
        pezzo = parole[i:i + PAROLE_PAGINA]
        pagine.append([pezzo[j:j + PAROLE_RIGA] for j in range(0, len(pezzo), PAROLE_RIGA)])
    return pagine


# ---------------------------------------------------------------- blocchi

def blocchi_da_pagine(pagine, dividi, strato=None):
    """Un blocco per parola utile; gruppo = pagina; grappolo = pagina modulo 10."""
    out = []
    for n, righe in enumerate(pagine):
        for w in posizioni.righe_utili(righe):
            out.append(Blocco(n, strato or 0, n % 10, [dividi(w) if dividi else list(w)]))
    return out


def blocchi_voynich(lingua=None):
    righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua)
    per_pagina, meta = {}, {}
    for r in righe:
        if r.inizio_par:
            continue
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        per_pagina.setdefault(r.pagina, []).append(ps)
        meta[r.pagina] = (r.sezione, r.lingua, r.quire)
    out = []
    for pag, righe_p in per_pagina.items():
        utili = [DIVIDI(w) for w in posizioni.righe_utili(righe_p)]
        if sum(1 for u in utili if len(u) >= 4) < PAGINA_MIN:
            continue
        sezione, ling, quire = meta[pag]
        out.extend(Blocco(pag, (sezione, ling), quire, [u]) for u in utili)
    return out


def testi_timm_schinner():
    import e22_timm_schinner as e22
    for seme in (19, 1, 2):
        pagine = e22.genera(seme)
        yield 'Timm e Schinner, seme %d' % seme, blocchi_da_pagine(pagine, DIVIDI)


# ---------------------------------------------------------------- esecuzione

def misura(nome, blocchi, ris):
    p = posizioni.profilo(blocchi)
    p['stabilita'] = posizioni.stabilita(blocchi)
    ris[nome] = p
    q = p['posizioni']
    print('%-44s R %6s  quote: %s  z primo %.1f  stab. %s-%s' % (
        nome, fmt(p['R']), ' '.join('%s %.4f' % (k[:3], v['quota']) for k, v in q.items()),
        q['primo']['z'], fmt(p['stabilita']['min']), fmt(p['stabilita']['max'])), flush=True)


def fmt(x):
    if x is None:
        return '—'
    if x == float('inf'):
        return '∞'
    return '%.2f' % x


def main():
    ris = {}
    misura('Voynich ZL', blocchi_voynich(), ris)
    misura('Voynich ZL, Currier A', blocchi_voynich('A'), ris)
    misura('Voynich ZL, Currier B', blocchi_voynich('B'), ris)

    libri = plinio()
    tutte = [w for _, ps in libri for w in ps]
    categorie = categorie_semantiche(tutte)
    misura('controllo positivo: codice a prefisso semantico',
           blocchi_da_pagine(pagine_da_parole(codice_semantico(tutte, categorie)), DIVIDI), ris)
    misura('controllo positivo, versione preregistrata (D-007)',
           blocchi_da_pagine(pagine_da_parole(codice_semantico(tutte, categorie, alfabetico=False)), DIVIDI), ris)
    misura('controllo di forma: codice casuale',
           blocchi_da_pagine(pagine_da_parole(codice_casuale(tutte)), DIVIDI), ris)
    misura('Plinio in latino, lettere', blocchi_da_pagine(pagine_da_parole(tutte), None), ris)
    naibbe = open(NAIBBE, encoding='utf-8').read().split()[:len(tutte)]
    misura('Naibbe (Plinio XVI cifrato da Greshko)', blocchi_da_pagine(pagine_da_parole(naibbe), DIVIDI), ris)
    for nome, blocchi in testi_timm_schinner():
        misura(nome, blocchi, ris)

    os.makedirs(RISULTATI, exist_ok=True)
    with open(os.path.join(RISULTATI, 'e36_posizione_pagina.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    scrivi_tabella(ris)


def scrivi_tabella(ris, nome_file='e36_posizione_pagina.md',
                   titolo="# e36 — In quale posizione della parola sta l'informazione sulla pagina"):
    righe = [titolo, '',
             'Quota = (informazione mutua pagina/segno − media di 200 rimescolamenti) / entropia del segno. '
             'R = quota al primo segno / media delle quote a penultimo e ultimo. Stabilità: R togliendo '
             'un fascicolo (Voynich) o una pagina su dieci (controlli). Preregistrazione: '
             '`preregistrazioni/e36-e38.md`.', '',
             '| testo | parole | pagine | primo | secondo | penultimo | ultimo | z primo | R | stabilità di R |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for nome, p in ris.items():
        q = p['posizioni']
        righe.append('| %s | %d | %d | %s | %s | %.1f | %s | %s–%s |' % (
            nome, p['parole'], p['gruppi'],
            ' | '.join('%.4f' % q[k]['quota'] for k in ('primo', 'secondo', 'penultimo')),
            '%.4f' % q['ultimo']['quota'], q['primo']['z'], fmt(p['R']),
            fmt(p['stabilita']['min']), fmt(p['stabilita']['max'])))
    with open(os.path.join(RISULTATI, nome_file), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


# ---------------------------------------------------------------- esplorativo (non preregistrato)

def a_strati_contigui(blocchi, n_strati):
    """Stesse pagine, ma rimescolamento solo dentro n_strati tratti contigui del testo."""
    pagine = sorted({b.gruppo for b in blocchi}, key=lambda g: (str(type(g)), g))
    tratto = {g: i * n_strati // len(pagine) for i, g in enumerate(pagine)}
    return [Blocco(b.gruppo, tratto[b.gruppo], b.grappolo, b.parole) for b in blocchi]


def esplorativo():
    """Confronto alla pari fra Voynich e generatore: la stessa stratificazione per entrambi.
    Nella corsa ufficiale il Voynich era stratificato per sezione x lingua (9 strati) e il
    generatore no; qui entrambi senza strati, ed entrambi con 9 tratti contigui."""
    import e22_timm_schinner as e22
    ris = {}
    voy = blocchi_voynich()
    ordine = {pag: i for i, pag in enumerate(dict.fromkeys(b.gruppo for b in voy))}
    voy_ordinati = [Blocco(ordine[b.gruppo], b.strato, b.grappolo, b.parole) for b in voy]
    senza = [Blocco(b.gruppo, 0, b.grappolo, b.parole) for b in voy_ordinati]
    misura('Voynich ZL, senza strati', senza, ris)
    misura('Voynich ZL, 9 tratti contigui', a_strati_contigui(senza, 9), ris)
    for seme in (19, 1, 2):
        ts = blocchi_da_pagine(e22.genera(seme), DIVIDI)
        misura('Timm e Schinner %d, senza strati' % seme, ts, ris)
        misura('Timm e Schinner %d, 9 tratti contigui' % seme, a_strati_contigui(ts, 9), ris)
    with open(os.path.join(RISULTATI, 'e36_posizione_pagina_esplorativo.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    scrivi_tabella(ris, 'e36_posizione_pagina_esplorativo.md',
                   '# e36, analisi esplorativa (non preregistrata): Voynich e generatore alla pari')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e36_posizione_pagina.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f))
    elif '--esplorativo' in sys.argv:
        esplorativo()
    else:
        main()
