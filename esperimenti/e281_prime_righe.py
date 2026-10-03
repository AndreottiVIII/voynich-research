# -*- coding: utf-8 -*-
"""Esperimento 281: il risolutore dell'e17 sulle sole prime righe dei paragrafi, contro le stesse rimescolate e contro le
seconde righe; condizione di validita' sul controllo positivo (lezione dell'e212b).

Preregistrazione: preregistrazioni/e281.md. Scrive risultati/e281_prime_righe.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e17_ricottura as e17
import e160_testo_ripulito as e160

RISULTATI = os.path.join(QUI, '..', 'risultati')
LINGUE = ('Latin', 'Italian', 'German', 'Spanish', 'Hebrew', 'Arabic')
PRIME, RIM, SECONDE = 'prime righe', 'prime righe, rimescolate', 'seconde righe'


def testi():
    pul = e160.ripulisci(e160.pagine_voynich())
    pulita = lambda ps: [w if trascrizione.pulita(w) else None for w in ps]
    prime, seconde = [], []
    for p in pul:
        for i, (ini, ps) in enumerate(p):
            if ini:
                prime.append(pulita(ps))
                if i + 1 < len(p) and not p[i + 1][0]:
                    seconde.append(pulita(p[i + 1][1]))
    g = misure.divisore(misure.GLIFI_EVA)
    tutte = e17.in_unita(prime + seconde, g)
    ammesse = {u for r in tutte for u in r}
    return e17.in_unita(prime, g, ammesse=ammesse), e17.in_unita(seconde, g, ammesse=ammesse)


def rimescola(righe, rnd):
    unita = [u for r in righe for u in r]
    rnd.shuffle(unita)
    out, i = [], 0
    for r in righe:
        out.append(unita[i:i + len(r)])
        i += len(r)
    return out


def una(lingua):
    prime, seconde = testi()
    voynich = OrderedDict([(PRIME, prime), (RIM, rimescola(prime, random.Random('e281-' + lingua))), (SECONDE, seconde)])
    return e17.una_lingua((lingua, lingua, voynich))


def giudica(r):
    pos, neg = r[PRIME + ', controllo positivo'], r[PRIME + ', controllo negativo']
    valido = pos['copertura_6'] >= 0.3 and pos['punteggio'] > neg['punteggio'] and pos['copertura_6'] > neg['copertura_6']
    p = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in (PRIME, RIM, SECONDE)}
    cand = (valido and min(p[PRIME]) >= 0.5 and all(p[PRIME][i] - p[RIM][i] >= 0.3 for i in (0, 1))
            and all(p[PRIME][i] - p[SECONDE][i] >= 0.2 for i in (0, 1)))
    return valido, p, 'non valido' if not valido else ('candidato, da riprovare (e281b)' if cand else 'nessuna lettura')


def main():
    prime, seconde = testi()
    print('prime righe: %d segmenti, %d unita; seconde righe: %d segmenti, %d unita' % (len(prime), sum(map(len, prime)), len(seconde), sum(map(len, seconde))), flush=True)
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, LINGUE):
            ris[nome] = r
            json.dump(ris, open(os.path.join(RISULTATI, 'e281_prime_righe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    esiti = OrderedDict()
    md = ['# e281 — Decifrare solo le prime righe dei paragrafi', '',
          'Risolutore dell\'e17 (4 ripartenze, segni EVA). Posizione fra negativo (0) e positivo (1), punteggio / copertura delle parole di almeno 6 lettere. '
          'Preregistrazione: `preregistrazioni/e281.md`.', '',
          '| lingua | positivo sulle prime righe (punt. / cop.) | negativo | prime righe | rimescolate | seconde righe | valido | esito |', '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        valido, p, esito = giudica(r)
        esiti[nome] = OrderedDict([('valido', valido), ('posizioni', p), ('esito', esito)])
        t = lambda k: '%.2f / %.2f' % (r[PRIME + ', ' + k]['punteggio'], r[PRIME + ', ' + k]['copertura_6'])
        md.append('| %s | %s | %s | %.2f / %.2f | %.2f / %.2f | %.2f / %.2f | %s | %s |' % (
            nome, t('controllo positivo'), t('controllo negativo'), *p[PRIME], *p[RIM], *p[SECONDE], 'sì' if valido else 'no', esito))
    md += ['', 'Esempi decifrati delle prime righe:', '']
    for nome, r in ris.items():
        md.append('- %s: %s' % (nome, ' / '.join(x[:60] for x in r[PRIME + ', Voynich'].get('esempi', [])[:2])))
    esito = ('candidati: ' + ', '.join(k for k, v in esiti.items() if v['esito'].startswith('candidato'))) if any(
        v['esito'].startswith('candidato') for v in esiti.values()) else 'nessuna lettura'
    md += ['', 'Esito: **%s**.' % esito]
    json.dump({'lingue': ris, 'esiti': esiti, 'esito': esito}, open(os.path.join(RISULTATI, 'e281_prime_righe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(RISULTATI, 'e281_prime_righe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
