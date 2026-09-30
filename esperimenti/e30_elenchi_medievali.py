# -*- coding: utf-8 -*-
"""Esperimento 30: testi a elenco medievali veri riproducono le anomalie del Voynich?

Glossari medico-botanici (Alphita, XIII secolo; Sinonoma Bartholomei, XIV secolo; OCR
delle edizioni Mowat 1887 e 1882 da archive.org) e il catalogo di stelle di Igino
(De astronomia III), con la prosa di Igino (II) come riferimento. Misure dell'e21 su
pagine finte, piu' legame fine-inizio e ordine fra parole vicine; ogni testo anche
cifrato con un codice parola per parola sul vocabolario del Voynich.

Preregistrazione: preregistrazioni/e30.md (regole di pulizia degli OCR comprese).
Scrive risultati/e30_elenchi_medievali.json e .md.
"""
import hashlib, json, os, random, re, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
from e21_sondaggi import profilo

RISULTATI = os.path.join(QUI, '..', 'risultati')
ELENCHI = os.path.join(QUI, '..', 'dati', 'cache', 'elenchi')
OCR = {
    'Alphita (glossario, XIII sec.)': ('alphitaamedicob00mowagoog.txt',
                                       '474fd50cd2058918f4828fa5c422ec595afe017aea50004c3591365d47786f87', 316, 20330),
    'Sinonoma Bartholomei (glossario, XIV sec.)': ('sinonomabartholo01mirfuoft.txt',
                                                   '7b027352d3e9c22a123c24ef896f7748594f98551c8b8511e6c206fbf03059a9', 1733, 5383),
}
SIGLE = ['p. ', 'ib.', 'Diosc', 'Bart', 'Sim. Jan', 'MS.', 'See ', 'Gerarde', 'Compare', 'ed. ', 'Coll.', 'App.']
INGLESI = {'the', 'of', 'and', 'which', 'also', 'are', 'with', 'this', 'that', 'is', 'from', 'by'}
TITOLI = ('SINONOMA BARTHOLOMEI', 'ALPHITA', 'APPENDIX')
_INIZIO = re.compile(r"^(\d|[IVXLC]+\.|[\^\*'\"])")


def pulisci_ocr(nome_file, sha, da, a):
    percorso = os.path.join(ELENCHI, nome_file)
    with open(percorso, 'rb') as f:
        if hashlib.sha256(f.read()).hexdigest() != sha:
            raise SystemExit('OCR diverso da quello preregistrato: %s' % nome_file)
    righe = open(percorso, encoding='utf-8', errors='replace').read().splitlines()[da - 1:a - 1]
    tenute, scartate = [], 0
    for r in righe:
        s = r.strip()
        if not s:
            continue
        parole_en = sum(1 for w in re.findall(r'[A-Za-z]+', s) if w.lower() in INGLESI)
        if (_INIZIO.match(s.replace(' ', '')) or any(x in s for x in SIGLE) or parole_en >= 2
                or any(t in s.upper() for t in TITOLI)):
            scartate += 1
            continue
        tenute.append(s)
    testo = ''
    for s in tenute:                                 # ricongiunge le parole spezzate a fine riga
        testo = testo[:-1] + s if testo.endswith('-') else testo + ' ' + s
    parole = [w for w in lingue.normalizza(testo).split() if len(w) > 1]
    residuo = sum(1 for w in parole if w in INGLESI) / len(parole)
    return parole, {'righe_tenute': len(tenute), 'righe_scartate': scartate, 'parole': len(parole),
                    'inglese_residuo': residuo}


def _igino(n):
    with open(os.path.join(lingue.LATIN_LIBRARY, 'hyginus', 'hyginus%d.txt' % n), encoding='utf-8') as f:
        righe = [r for r in f if 'Latin Library' not in r and 'Classics Page' not in r]
    return [w for w in lingue.normalizza(' '.join(righe)).split() if len(w) > 1]


def extra(pagine, dividi):
    righe = [r for p in pagine for r in p]
    parole = [w for r in righe for w in r]
    return {'confine': misure.confine(righe, dividi, solo_interne=True)['im_confine_eccesso'],
            'ordine_vicine': misure.parole_misure(parole, dividi)['im_vicine_eccesso']}


def main():
    rnd = random.Random(30)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    modello = generatori.ModelloParole(parole_v, glifi)
    testi, pulizia = OrderedDict(), {}
    for nome, (f, sha, da, a) in OCR.items():
        testi[nome], pulizia[nome] = pulisci_ocr(f, sha, da, a)
    testi['Igino III (catalogo di stelle)'] = _igino(3)
    testi['Igino II (prosa, riferimento)'] = _igino(2)
    ris = OrderedDict([('pulizia', pulizia)])
    pagine_v = misure.pagine_finte(parole_v)
    ris['Voynich (righe finte da 8 parole)'] = dict(profilo(pagine_v, glifi), **extra(pagine_v, glifi))
    for nome, parole in testi.items():
        pagine = misure.pagine_finte(parole)
        ris[nome] = dict(profilo(pagine, None), **extra(pagine, None))
        codice = generatori.codice_per_rango(parole, parole_v, modello, rnd)
        pagine_c = misure.pagine_finte(codice)
        ris[nome + ', con un codice'] = dict(profilo(pagine_c, glifi), **extra(pagine_c, glifi))
    for nome, r in ris.items():
        if nome == 'pulizia':
            continue
        print('%-50s parole %6d rip %.2f somigl %.3f/%.3f/%.3f confine %.3f ordine %.3f hapax %.2f h2 %.2f' % (
            nome, r['parole'], r['identiche_vs_riga'], r['somiglianza_riga'], r['somiglianza_riga_sotto'],
            r['somiglianza_6_righe'], r['confine'], r['ordine_vicine'], r['hapax'], r['h2']), flush=True)
    with open(os.path.join(RISULTATI, 'e30_elenchi_medievali.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ['# e30 — Testi a elenco medievali e anomalie del Voynich', '',
             'Pagine finte di 20 righe da 8 parole. Ripetizione: parola identica alla precedente rispetto a '
             'due parole della stessa riga (Voynich ×1,0; lingue mediana ×0,12). Somiglianza: eccesso fra '
             'parole diverse della stessa riga, della riga sotto e a 6 righe, rispetto a tutto il testo '
             '(Voynich 3,8% → 3,4%; lingue −0,4%…1,5%). Confine: legame fine–inizio (bit). Ordine: '
             'informazione fra parole vicine oltre il rimescolamento (bit). Preregistrazione: '
             '`preregistrazioni/e30.md`.', '',
             '| testo | parole | ripetizione | somigl. riga | riga sotto | 6 righe | confine | ordine | parole uniche | h2 |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if nome == 'pulizia':
            continue
        righe.append('| %s | %d | %.2f | %.1f%% | %.1f%% | %.1f%% | %.3f | %.3f | %.2f | %.2f |' % (
            nome, r['parole'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'],
            100 * r['somiglianza_6_righe'], r['confine'], r['ordine_vicine'], r['hapax'], r['h2']))
    righe += ['', 'Pulizia degli OCR:', '']
    righe += ['- %s: righe tenute %d, scartate %d; %d parole; parole inglesi funzionali residue %.2f%%.' % (
        n, p['righe_tenute'], p['righe_scartate'], p['parole'], 100 * p['inglese_residuo']) for n, p in pulizia.items()]
    with open(os.path.join(RISULTATI, 'e30_elenchi_medievali.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
