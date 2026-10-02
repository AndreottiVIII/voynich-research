# -*- coding: utf-8 -*-
"""Esperimento 219: risolutore dell'e17 sul testo ripulito con modelli di lingue volgari e storiche (corpora Wikipedia
di Hermes) e di latino abbreviato all'uso medievale.

Preregistrazione: preregistrazioni/e219.md. Scrive risultati/e219_volgari_e_abbreviato.json e .md.
"""
import json, os, random, re, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, ricottura
import forza_bruta as fb
import e17_ricottura as e17

RISULTATI = os.path.join(QUI, '..', 'risultati')
CORPORA = os.path.join(QUI, '..', 'dati', 'cache', 'hermes_wikipedia')
VOLGARI = OrderedDict([('Catalan', 'catalano'), ('Occitan', 'occitano'), ('Anglo Saxon', 'anglosassone'), ('Gothic', 'gotico'),
                       ('Old Church Slavonic', 'slavo ecclesiastico'), ('Alemannic', 'alemanno'), ('Bavarian', 'bavarese'), ('Venetian', 'veneto'),
                       ('Lombard', 'lombardo'), ('Neapolitan', 'napoletano'), ('Sicilian', 'siciliano'), ('Friulian', 'friulano'), ('Ladino', 'ladino'),
                       ('Picard', 'piccardo'), ('Franco-Provençal', 'franco-provenzale')])
PAROLE_MAX = 400000
VOCALI = set('aeiouy')


def abbrevia(w):
    if w == 'et':
        return '&'
    for a, b in (('per', 'P'), ('pro', 'Q'), ('prae', 'R')):
        if w.startswith(a) and len(w) > len(a) + 1:
            w = b + w[len(a):]
            break
    if (w.startswith('con') or w.startswith('com')) and len(w) > 4:
        w = '7' + w[3:]
    if w.endswith('que') and len(w) > 4:
        w = w[:-3] + 'q;'
    elif w.endswith('rum') and len(w) > 4:
        w = w[:-3] + '4'
    elif w.endswith('us') and len(w) > 3:
        w = w[:-2] + '9'
    w = re.sub(r'([aeiou])[mn](?=[bcdfgklpqrstv])', r'\1~', w)
    if len(w) >= 7:
        w = w[0] + ''.join(c for c in w[1:-1] if c not in VOCALI) + w[-1]
    return w


def parole_corpus(chiave):
    if chiave == 'latino abbreviato':
        return [abbrevia(w) for w in lingue.parole('Latin')]
    testo = open(os.path.join(CORPORA, chiave + '.txt'), encoding='utf-8', errors='ignore').read()
    return testo.split()[:PAROLE_MAX]


def prepara(chiave):
    testo = parole_corpus(chiave)
    lettere = e17.alfabeto(testo)
    testo = e17.pulisci(testo, lettere)
    add = int(len(testo) * 0.8)
    modello = ricottura.ModelloLettere(''.join(testo[:add]), n=5)
    lessico = e17.Lessico({p for p in testo[:add] if len(p) >= 4}, set(zip(testo[:add], testo[1:add])))
    return testo, add, lettere, modello, lessico


def una(args):
    chiave, nome, voynich = args
    try:
        rnd = random.Random('e219-' + chiave)
        testo, add, lettere, modello, lessico = prepara(chiave)
        altro = lingue.parole('Finnish')
        altro = e17.pulisci(altro, e17.alfabeto(altro))
        r = OrderedDict([('lettere', len(modello.lettere))])
        for modo, righe_v in voynich.items():
            simboli = len({u for x in righe_v for u in x})
            L = sum(map(len, righe_v))
            cif, vera = e17.cifra_abbinata(e17.in_righe(e17.prendi(testo[add:], L)), simboli, rnd)
            r[modo + ', controllo positivo'] = e17.attacca(cif, modello, lessico, rnd, vera=vera)
            cif, _ = e17.cifra_abbinata(e17.in_righe(e17.prendi(altro, L)), simboli, rnd)
            r[modo + ', controllo negativo'] = e17.attacca(cif, modello, lessico, rnd)
            r[modo + ', Voynich'] = e17.attacca(righe_v, modello, lessico, rnd)
            for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
                e17.stampa(nome, modo + ', ' + k, r[modo + ', ' + k])
        return nome, r
    except Exception as e:
        return nome, {'errore': repr(e)}


def main():
    righe = fb.righe_ripulite()
    modo = fb.RIF
    voynich = OrderedDict([(modo, e17.in_unita(righe, fb.G))])
    corpora = OrderedDict(VOLGARI)
    corpora['latino abbreviato'] = 'latino abbreviato'
    ris = OrderedDict()
    percorso = os.path.join(RISULTATI, 'e219_volgari_e_abbreviato.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(k, n, voynich) for k, n in corpora.items()]):
            ris[nome] = r
            json.dump(ris, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    grad, candidati = [], []
    for nome, r in ris.items():
        if 'errore' in r:
            print(nome, r['errore'])
            continue
        p, c = e17.posizione(r, modo, 'punteggio'), e17.posizione(r, modo, 'copertura_6')
        grad.append((nome, p, c, r[modo + ', controllo positivo'].get('chiave_giusta')))
        if p >= 0.5 and c >= 0.5:
            candidati.append(nome)
    grad.sort(key=lambda x: -(x[1] + x[2]))
    esito = 'candidato, da riprovare' if candidati else 'nessuna lettura'
    json.dump({'corpora': ris, 'graduatoria': grad, 'candidati': candidati, 'esito': esito}, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e219 — Lingue volgari e storiche, e latino abbreviato', '', 'Posizione del Voynich ripulito fra controllo negativo (0) e positivo (1). Preregistrazione: `preregistrazioni/e219.md`.', '',
          '| corpus | punteggio | copertura_6 | chiave giusta nel controllo positivo |', '|---|---|---|---|']
    md += ['| %s | %.2f | %.2f | %s |' % (n, p, c, '%.2f' % k if k is not None else '–') for n, p, c, k in grad]
    md += ['', 'Candidati: %s. Esito: **%s**.' % (', '.join(candidati) or 'nessuno', esito), '', 'Esempi decifrati:', '']
    for nome, r in ris.items():
        if 'errore' not in r:
            md.append('- %s: %s' % (nome, ' / '.join(r[modo + ', Voynich'].get('esempio', [])[:2])[:150]))
    open(os.path.join(RISULTATI, 'e219_volgari_e_abbreviato.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, candidati)


if __name__ == '__main__':
    main()
