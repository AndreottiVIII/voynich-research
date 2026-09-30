# -*- coding: utf-8 -*-
"""Esperimento 8: un testo che si copia da solo somiglia al Voynich?

L'alternativa alle codifiche: il testo nasce copiando e ritoccando parole gia'
scritte poco sopra (autocitazione, Timm e Schinner 2020). Il generatore usa la
stessa impaginazione del Voynich (pagine, righe, parole per riga) e ha quattro
manopole: quante modifiche subisce in media una copia (lam), quante righe
sopra si va a pescare (tau), quanto spesso si pesca da lontano (lontano), e
quanto si preferisce copiare parole gia' usate spesso (preferenza).

Regola del gioco, per non barare: le manopole si regolano SOLO sulla varieta'
del vocabolario (tipi/parole e hapax). Le misure su cui il modello si giudica
(ripetizioni immediate, somiglianza nella stessa riga e nelle righe sotto) non
entrano nella taratura.

Controlli: il Voynich con le parole rimescolate in tutto il testo, e
rimescolate solo dentro ogni pagina.

Scrive risultati/e08_autocitazione.json e risultati/e08_autocitazione.md.
"""
import itertools, json, math, os, random, sys
from collections import Counter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, grafici, misure, trascrizione
from e07_codifiche import impronta, pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRIGLIA = {'lam': [0.8, 1.1, 1.4, 1.8, 2.2], 'tau': [1.0, 2.0, 4.0], 'lontano': [0.05, 0.2],
           'preferenza': [0.0, 0.5, 1.0, 1.5]}
TOLLERANZA = {'tipi_su_parole': 0.02, 'hapax': 0.03}


def vocabolario(pagine):
    parole = [p for pag in pagine for riga in pag for p in riga][:30000]
    tipi = Counter(parole)
    return {'tipi_su_parole': len(tipi) / len(parole),
            'hapax': sum(1 for c in tipi.values() if c == 1) / len(tipi)}


def rimescola(pagine, rnd, dentro_pagina):
    if dentro_pagina:
        out = []
        for pag in pagine:
            parole = [p for riga in pag for p in riga]
            rnd.shuffle(parole)
            it = iter(parole)
            out.append([[next(it) for _ in riga] for riga in pag])
        return out
    parole = [p for pag in pagine for riga in pag for p in riga]
    rnd.shuffle(parole)
    it = iter(parole)
    return [[[next(it) for _ in riga] for riga in pag] for pag in pagine]


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    vere = pagine_voynich(corrente)
    parole_v = [p for pag in vere for riga in pag for p in riga]
    struttura = [[len(riga) for riga in pag] for pag in vere]
    semi_righe = vere[0][:3]
    modifiche = generatori.Modifiche(parole_v, glifi)
    bersaglio = vocabolario(vere)
    print('Voynich: tipi/parole %.3f  hapax %.3f' % (bersaglio['tipi_su_parole'], bersaglio['hapax']))

    taratura = []
    for lam, tau, lontano, preferenza in itertools.product(*GRIGLIA.values()):
        rnd = random.Random(11)
        gen = generatori.autocitazione(struttura, semi_righe, modifiche, rnd, lam, tau, lontano, preferenza)
        v = vocabolario(gen)
        ok = all(abs(v[k] - bersaglio[k]) <= TOLLERANZA[k] for k in TOLLERANZA)
        taratura.append({'lam': lam, 'tau': tau, 'lontano': lontano, 'preferenza': preferenza, **v, 'tarato': ok})
        print('lam %.1f tau %.1f lontano %.2f pref %.1f -> tipi %.3f hapax %.3f %s' % (
            lam, tau, lontano, preferenza, v['tipi_su_parole'], v['hapax'], 'TARATO' if ok else ''))

    ris = {'bersaglio_vocabolario': bersaglio, 'taratura': taratura, 'impronte': {}}
    ris['impronte']['Voynich'] = impronta(vere, glifi)
    rnd = random.Random(5)
    ris['impronte']['Voynich rimescolato in tutto il testo'] = impronta(rimescola(vere, rnd, False), glifi)
    ris['impronte']['Voynich rimescolato dentro ogni pagina'] = impronta(rimescola(vere, rnd, True), glifi)
    for t in taratura:
        if not t['tarato']:
            continue
        rnd = random.Random(11)
        gen = generatori.autocitazione(struttura, semi_righe, modifiche, rnd, t['lam'], t['tau'],
                                       t['lontano'], t['preferenza'])
        nome = 'autocitazione lam %.1f, tau %.1f, lontano %.2f, preferenza %.1f' % (
            t['lam'], t['tau'], t['lontano'], t['preferenza'])
        ris['impronte'][nome] = impronta(gen, glifi)
        ris['impronte'][nome]['esempio'] = [' '.join(riga) for riga in gen[40][:6]]
    if not any(t['tarato'] for t in taratura):
        # Nessuna combinazione rientra: misuriamo le tre piu' vicine, come indicazione.
        dist = lambda t: math.hypot((t['tipi_su_parole'] - bersaglio['tipi_su_parole']) / TOLLERANZA['tipi_su_parole'],
                                    (t['hapax'] - bersaglio['hapax']) / TOLLERANZA['hapax'])
        for t in sorted(taratura, key=dist)[:3]:
            rnd = random.Random(11)
            gen = generatori.autocitazione(struttura, semi_righe, modifiche, rnd, t['lam'], t['tau'],
                                           t['lontano'], t['preferenza'])
            nome = 'autocitazione NON tarata: lam %.1f, tau %.1f, lontano %.2f, preferenza %.1f' % (
                t['lam'], t['tau'], t['lontano'], t['preferenza'])
            ris['impronte'][nome] = impronta(gen, glifi)
            ris['impronte'][nome]['esempio'] = [' '.join(riga) for riga in gen[40][:6]]
    for nome, r in ris['impronte'].items():
        print('%-48s h2 %.2f lung %.2f ident %.2f%% (x%.2f) somigl. %.1f%% / %.1f%% / %.1f%%' % (
            nome, r['h2'], r['lung_media'], 100 * r['identiche_immediate'], r['identiche_vs_riga'],
            100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe']))
    with open(os.path.join(RISULTATI, 'e08_autocitazione.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    b = ris['bersaglio_vocabolario']
    tarati = [t for t in ris['taratura'] if t['tarato']]
    out = ['# Esperimento 8: autocitazione', '',
           'Griglia di %d combinazioni di manopole; tarate (entro %.2f su tipi/parole e %.2f su hapax '
           'dal Voynich, %.3f e %.3f): %d.' % (
               len(ris['taratura']), TOLLERANZA['tipi_su_parole'], TOLLERANZA['hapax'],
               b['tipi_su_parole'], b['hapax'], len(tarati)), '',
           '| testo | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza: stessa riga | riga sotto | 6 righe sotto |',
           '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris['impronte'].items():
        grassetto = '**%s**' % nome if nome == 'Voynich' else nome
        out.append('| %s | %.2f | %.2f | %.3f | %.2f | %.2f%% (×%.2f) | %.1f%% | %.1f%% | %.1f%% |' % (
            grassetto, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'],
            100 * r['identiche_immediate'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'],
            100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe']))
    if not tarati:
        out += ['', '**Nessuna combinazione rientra nella taratura.** Quando la varietà del vocabolario è '
                'quella del Voynich, le parole usate una volta sola sono troppo poche; e dopo molte copie '
                'le parole degenerano (troppo corte, troppe ripetizioni). Le righe "NON tarata" sono le tre '
                'combinazioni più vicine, riportate solo come indicazione: questa versione ridotta '
                'dell\'autocitazione non è una prova né a favore né contro l\'ipotesi di Timm e Schinner.']
    esempi = [(n, r['esempio']) for n, r in ris['impronte'].items() if 'esempio' in r][:2]
    for nome, righe in esempi:
        out += ['', 'Un pezzo di pagina generata (%s):' % nome, '', '```'] + righe + ['```']
    with open(os.path.join(RISULTATI, 'e08_autocitazione.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
