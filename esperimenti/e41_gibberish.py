# -*- coding: utf-8 -*-
"""Esperimento 41: il gibberish scritto a mano riproduce le anomalie del Voynich?

38 documenti di testo senza senso scritti da volontari (Gaskell e Bowern 2022, CEUR
Workshop Proceedings, International Conference on the Voynich Manuscript 2022; dati
con licenza MIT modificata, che chiede di citare l'articolo). Misure a scala di riga e
di pagina, con ogni documento come riferimento di se' stesso:
M1 ripetizione immediata nella riga, M2 somiglianza fra parole della stessa riga e di
righe vicine, M3 legame fra fine di una parola e inizio della successiva.
Controlli: Bibbia inglese e latina impaginate come ciascun documento.

Preregistrazione: preregistrazioni/e41.md. Scrive risultati/e41_gibberish.json e .md.
"""
import hashlib, json, os, sys, zipfile
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ZIP = os.path.join(lingue.SORGENTI, 'gaskell_bowern', 'gibberish_transcriptions.zip')
SHA_ZIP = 'a4bfa58af956603ab6607227ad640e01cb695c7b492c6914488bd30f6d0aebbe'
DIVIDI = misure.divisore(misure.GLIFI_EVA)
DISTANZE = (0, 1, 2, 3)


def gibberish():
    """{nome: [righe di parole]} dei 38 documenti."""
    with open(ZIP, 'rb') as f:
        if hashlib.sha256(f.read()).hexdigest() != SHA_ZIP:
            raise SystemExit('lo zip del gibberish non e\' quello atteso')
    z = zipfile.ZipFile(ZIP)
    out = OrderedDict()
    for nome in sorted(z.namelist()):
        testo = z.read(nome).decode('utf-8', errors='replace')
        righe = [lingue.normalizza(r).split() for r in testo.splitlines()]
        out[nome.replace('Gibberish - ', '').replace('.txt', '')] = [r for r in righe if r]
    return out


def impagina_come(documenti, chiave):
    """Per ogni documento, un tratto contiguo della Bibbia con le stesse lunghezze di riga."""
    parole = lingue.parole(chiave)
    out, i = OrderedDict(), 0
    for nome, righe in documenti.items():
        pagina = []
        for r in righe:
            pagina.append(parole[i:i + len(r)])
            i += len(r)
        out[nome] = pagina
    return out


def pagine_voynich():
    pagine = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        if ps:
            pagine.setdefault(r.pagina, []).append(ps)
    return pagine


def misura(documenti, dividi):
    righe = [r for doc in documenti.values() for r in doc]
    m1 = misure.vicinato(righe, dividi)
    # M2: ogni documento con il suo riferimento; media pesata sulle coppie
    somme = {d: [0.0, 0] for d in DISTANZE}
    for doc in documenti.values():
        if sum(len(r) for r in doc) < 30 or len(doc) < 4:
            continue
        dec = misure.decadimento([doc], dividi, coppie_caso=20000, distanze=DISTANZE)
        for d in DISTANZE:
            if dec[d]['coppie']:
                somme[d][0] += dec[d]['distanza'] * dec[d]['coppie']
                somme[d][1] += dec[d]['coppie']
    m2 = {d: 1 - s / n for d, (s, n) in somme.items() if n}
    m3 = misure.confine(righe, dividi, solo_interne=True)
    parole = [p for r in righe for p in r]
    return OrderedDict([
        ('documenti', len(documenti)), ('parole', len(parole)),
        ('lung_media', sum(len(dividi(p)) if dividi else len(p) for p in parole) / len(parole)),
        ('M1_ripetizione', m1['identiche_rapporto']), ('M1_coppie', m1['coppie']),
        ('M2_eccesso', m2), ('M3_confine', m3['im_confine_eccesso'])])


def m1_documento(righe):
    """M1 di un solo documento; None se il documento e' troppo corto per stimarlo."""
    try:
        v = misure.vicinato(righe, None)['identiche_rapporto']
    except ZeroDivisionError:
        return None
    return v if v == v else None


def main():
    docs = gibberish()
    testi = OrderedDict([
        ('gibberish (Gaskell e Bowern)', (docs, None)),
        ('Bibbia inglese, stessa impaginazione', (impagina_come(docs, 'English'), None)),
        ('Bibbia latina, stessa impaginazione', (impagina_come(docs, 'Latin'), None)),
        ('Voynich ZL, pagine', (pagine_voynich(), DIVIDI)),
    ])
    ris = OrderedDict()
    for nome, (documenti, dividi) in testi.items():
        ris[nome] = misura(documenti, dividi)
        r = ris[nome]
        print('%-40s M1 %.2f  M2 %s  M3 %.3f' % (nome, r['M1_ripetizione'],
              ' '.join('d%d %.3f' % kv for kv in r['M2_eccesso'].items()), r['M3_confine']), flush=True)
    # M1 documento per documento, solo per il gibberish: quanto varia fra gli autori
    ris['gibberish, per documento'] = OrderedDict((nome, m1_documento(righe)) for nome, righe in docs.items())
    with open(os.path.join(RISULTATI, 'e41_gibberish.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    righe = ['# e41 — Il gibberish umano e le anomalie del Voynich', '',
             'M1: parola identica alla precedente nella stessa riga, rispetto a due parole a caso della '
             'riga (Voynich nel dossier ×1,0; lingue mediana ×0,12). M2: eccesso di somiglianza fra parole '
             'diverse a distanza d righe, rispetto a due parole a caso **dello stesso documento**. M3: '
             'legame fine–inizio in bit oltre il rimescolamento nella riga. Dati del gibberish: Gaskell e '
             'Bowern (2022). Preregistrazione: `preregistrazioni/e41.md`.', '',
             '| testo | documenti | parole | M1 | M2 d=0 | M2 d=1 | M2 d=2 | M2 d=3 | M3 (bit) |',
             '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if 'M1_ripetizione' not in r:
            continue
        m2 = {int(k): v for k, v in r['M2_eccesso'].items()}
        righe.append('| %s | %d | %d | %.2f | %s | %.3f |' % (
            nome, r['documenti'], r['parole'], r['M1_ripetizione'],
            ' | '.join('%.3f' % m2[d] for d in DISTANZE), r['M3_confine']))
    per_doc = ris['gibberish, per documento']
    valori = sorted(v for v in per_doc.values() if v is not None)
    righe += ['', 'M1 del gibberish documento per documento: mediana %.2f, da %.2f a %.2f (%d documenti con '
              'almeno una coppia attesa).' % (valori[len(valori) // 2], valori[0], valori[-1], len(valori))]
    with open(os.path.join(RISULTATI, 'e41_gibberish.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e41_gibberish.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f))
    else:
        main()
