# -*- coding: utf-8 -*-
"""Esperimento 212c: verifica dei candidati dell'e212b (hindi, finlandese, birmano) con 8 ripartenze (RIPARTENZE=8 nella
coda), il latino come negativo per il finlandese, il Voynich rimescolato dentro il criterio e una condizione di validita'
sul controllo positivo.

Preregistrazione: preregistrazioni/e212c.md. Scrive risultati/e212c_candidati.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e17_ricottura as e17
import e212_forza_bruta_ripulito as e212

RISULTATI = os.path.join(QUI, '..', 'risultati')
MODO = 'ripulito, segni EVA'
RIM = MODO + ', rimescolato'
CANDIDATI = ('Hindi', 'Finnish', 'Burmese')


def rimescola(righe, rnd):
    unita = [u for r in righe for u in r]
    rnd.shuffle(unita)
    out, i = [], 0
    for r in righe:
        out.append(unita[i:i + len(r)])
        i += len(r)
    return out


def una(lingua):
    if lingua == 'Finnish':
        e17.STRANIERO = 'Latin'
    v = e212.modi()[MODO]
    voynich = OrderedDict([(MODO, v), (RIM, rimescola(v, random.Random('e212c-' + lingua)))])
    return e17.una_lingua((lingua, lingua, voynich))


def giudica(r):
    pos, neg = r[MODO + ', controllo positivo'], r[MODO + ', controllo negativo']
    valido = pos['copertura_6'] >= 0.3 and pos['punteggio'] > neg['punteggio'] and pos['copertura_6'] > neg['copertura_6']
    p = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in (MODO, RIM)}
    regge = valido and min(p[MODO]) >= 0.5 and all(p[MODO][i] - p[RIM][i] >= 0.3 for i in (0, 1))
    return valido, p, 'non valido' if not valido else ('il candidato regge (nessuna lettura)' if regge else 'artefatto')


def main():
    if os.environ.get('RIPARTENZE') != '8':
        sys.exit('e212c va eseguito con RIPARTENZE=8')
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, CANDIDATI):
            ris[nome] = r
            json.dump(ris, open(os.path.join(RISULTATI, 'e212c_candidati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    esiti = OrderedDict()
    md = ['# e212c — Verifica dei candidati dell\'e212b', '', '8 ripartenze; negativo latino per il finlandese; Voynich rimescolato nel criterio. '
          'Posizione fra negativo (0) e positivo (1), punteggio / copertura delle parole di almeno 6 lettere. Preregistrazione: `preregistrazioni/e212c.md`.', '',
          '| lingua | negativo | positivo (punt. / cop.) | negativo | Voynich | posizione Voynich | posizione rimescolato | valido | esito |', '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        valido, p, esito = giudica(r)
        esiti[nome] = OrderedDict([('valido', valido), ('posizioni', p), ('esito', esito)])
        t = lambda k: '%.2f / %.2f' % (r[MODO + ', ' + k]['punteggio'], r[MODO + ', ' + k]['copertura_6'])
        md.append('| %s | %s | %s | %s | %s | %.2f / %.2f | %.2f / %.2f | %s | %s |' % (
            nome, r['lingua del controllo negativo'], t('controllo positivo'), t('controllo negativo'), t('Voynich'), *p[MODO], *p[RIM], 'sì' if valido else 'no', esito))
    json.dump({'lingue': ris, 'esiti': esiti}, open(os.path.join(RISULTATI, 'e212c_candidati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(RISULTATI, 'e212c_candidati.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(dict((k, v['esito']) for k, v in esiti.items()))


if __name__ == '__main__':
    main()
