# -*- coding: utf-8 -*-
"""Esperimento 25: preghiere e litanie come termine di paragone.

Una delle possibilita' rimaste (vedi il rapporto) e' che il Voynich non sia
prosa: elenchi, formule, preghiere ripetute, dove ripetere subito una parola
puo' essere normale e ogni pagina ha il suo lessico. Gli elenchi dell'esperimento
21 (genealogie, cariche, consoli) non ripetevano le parole e non avevano pagine
omogenee. Qui le preghiere che si ripetono per costruzione, in latino, dal
breviario romano del progetto Divinum Officium:

- la litania dei santi ("Sancte Petre, ora pro nobis. Sancte Paule, ora pro
  nobis...");
- l'ordine della raccomandazione dell'anima, con la sua litania per i
  moribondi;
- salmi e cantici con ritornello: il salmo 135 ("quoniam in aeternum
  misericordia ejus", a ogni versetto), il cantico dei tre giovani
  ("Benedicite... Domino"), i salmi 148 e 150;
- le preci del breviario (versetti e risposte);
- un rosario di quindici decine, ricostruito dalle preghiere del breviario
  (Pater noster, dieci Ave Maria, Gloria): il caso estremo di una preghiera
  ripetuta.

Ogni testo si misura con la lista di controllo, in righe da 8 parole e pagine
da 20 righe, come gli elenchi; tutti insieme anche cifrati con un codice parola
per parola (come nell'esperimento 7), che da' le parole del Voynich ma conserva
come si ripetono.

Scrive risultati/e25_preghiere.json e .md.
"""
import json, os, random, re, sys, unicodedata
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e22_timm_schinner as e22
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
BREVIARIO = os.path.join(lingue.SORGENTI, 'divinum-officium', 'web', 'www', 'horas', 'Latin')
DECINE = 15


def sezione(percorso, nome=None):
    """Le righe di un file del breviario, o di una sua sezione [nome]."""
    righe = open(os.path.join(BREVIARIO, percorso), encoding='utf-8').read().splitlines()
    if nome is None:
        return righe
    out, dentro = [], False
    for r in righe:
        if r.startswith('['):
            if dentro:
                break
            dentro = r.strip() == '[%s]' % nome
            continue
        if dentro:
            out.append(r)
    return out


def pulisci(righe):
    """Solo il testo detto: via rubriche, rimandi, numeri di versetto, segni."""
    parole = []
    for r in righe:
        r = r.strip()
        if not r or r[0] in '[#@!($&_':
            continue
        r = re.sub(r'/:\(:/.*?/:\):/', ' ', r)   # varianti fra parentesi, come (ea) accanto a eo
        r = re.sub(r'/:.*?:/', ' ', r)            # rubriche dentro la riga
        r = re.sub(r'<[^>]*>', ' ', r)
        r = re.sub(r'^\d+:\d+[a-z]?\s*', '', r)   # numero del versetto
        r = re.sub(r'^[vVrR]\.\s*', '', r)       # versetto e risposta
        testo = unicodedata.normalize('NFD', lingue.normalizza(r))
        testo = ''.join(c for c in testo if unicodedata.category(c) != 'Mn')
        parole += testo.split()
    return parole


def rosario():
    pater = pulisci(sezione('Psalterium/Common/Prayers.txt', 'Pater noster'))
    ave = pulisci(sezione('Psalterium/Common/Prayers.txt', 'Ave Maria'))
    gloria = pulisci(sezione('Psalterium/Common/Prayers.txt', 'Gloria'))
    return (pater + ave * 10 + gloria) * DECINE


def testi():
    t = OrderedDict()
    t['litania dei santi'] = pulisci(sezione('Psalterium/Special/Preces.txt', 'Litania'))
    t['raccomandazione dell\'anima (con la litania dei moribondi)'] = pulisci(
        sezione('Appendix/Ordo Commendationis Animae.txt'))
    t['salmi e cantici con ritornello (135, 148, 150, tre giovani)'] = sum(
        (pulisci(sezione('Psalterium/Psalmorum/Psalm%d.txt' % n)) for n in (135, 148, 150, 210, 220)), [])
    preci = sezione('Psalterium/Special/Preces.txt')
    inizio = next(i for i, r in enumerate(preci) if r.startswith('[Preces feriales Laudes]'))
    t['preci del breviario (versetti e risposte)'] = pulisci(preci[inizio:])
    t['rosario ricostruito (%d decine)' % DECINE] = rosario()
    return t


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    ris = OrderedDict()
    ris['Voynich'] = e22.lista_di_controllo(pagine_voynich(corrente), glifi)
    ris['latino in prosa (Vangeli, 20.000 parole)'] = e22.lista_di_controllo(
        misure.pagine_finte(lingue.parole('Latin')[:20000]), None)
    tutte = []
    for nome, parole in testi().items():
        tutte += parole
        ris[nome] = e22.lista_di_controllo(misure.pagine_finte(parole), None)
        ris[nome]['parole'] = len(parole)
    ris['tutte le preghiere insieme'] = e22.lista_di_controllo(misure.pagine_finte(tutte), None)
    ris['tutte le preghiere insieme']['parole'] = len(tutte)
    modello = generatori.ModelloParole(parole_v, glifi)
    codice = generatori.codice_per_rango(tutte, parole_v, modello, random.Random(25))
    ris['tutte le preghiere insieme, con un codice'] = e22.lista_di_controllo(misure.pagine_finte(codice), glifi)
    for nome, r in ris.items():
        e22.stampa(nome[:28], r)
    with open(os.path.join(RISULTATI, 'e25_preghiere.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    chiavi = [('h2', 'h2', '%.2f'), ('spazio_spiegato', 'spazio', '%.0f%%'), ('tipi_su_parole', 'diverse', '%.0f%%'),
              ('hapax', 'hapax', '%.0f%%'), ('identiche_vs_riga', 'ripetute', '×%.2f'),
              ('somiglianza_riga', 'somiglianza riga', '%.1f%%'), ('somiglianza_6_righe', 'a 6 righe', '%.1f%%'),
              ('confine', 'legame fine-inizio', '%.3f')]
    out = ['# Esperimento 25: preghiere e litanie', '',
           'Testi latini del breviario romano (progetto Divinum Officium), in righe da 8 parole e pagine da 20 '
           'righe; il Voynich sulle sue righe e pagine vere. Misure come nella lista di controllo.', '',
           '| testo | parole | ' + ' | '.join(n for _, n, _ in chiavi) + ' |',
           '|---|---|' + '---|' * len(chiavi)]
    for nome, r in ris.items():
        out.append('| %s | %s | %s |' % (nome, r.get('parole', '–'),
                                         ' | '.join(e22.formato(k, f, r[k]) for k, _, f in chiavi)))
    out += ['', 'Testi corti: su poche migliaia di parole le misure di pagina sono approssimative.']
    with open(os.path.join(RISULTATI, 'e25_preghiere.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e25_preghiere.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
