# -*- coding: utf-8 -*-
"""Esecuzione comune per gli attacchi a ricottura dell'e17 su trasformazioni del testo ripulito del Voynich (e218,
e221, e222): per ogni lingua e modo, controllo positivo, negativo e Voynich (e17.una_lingua); posizione fra i
controlli; candidati; scrittura dei risultati.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import misure, trascrizione
import e17_ricottura as e17
import e160_testo_ripulito as e160

RISULTATI = os.path.join(QUI, '..', 'risultati')
G = misure.divisore(misure.GLIFI_EVA)
RIF = 'ripulito, segni EVA'


def righe_ripulite():
    pul = e160.ripulisci(e160.pagine_voynich())
    return [[w if trascrizione.pulita(w) else None for w in ps] for p in pul for _, ps in p]


def esegui(modi, lingue, nome_file, titolo, preregistrazione):
    for m, rr in modi.items():
        print('%-34s simboli %d lunghezza %d righe %d' % (m, len({u for r in rr for u in r}), sum(map(len, rr)), len(rr)), flush=True)
    lavori = [(k, n, modi) for k, n in lingue.items()]
    ris = OrderedDict()
    percorso = os.path.join(RISULTATI, nome_file + '.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(e17.una_lingua, lavori):
            ris[nome] = r
            json.dump(ris, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    nomi_modi = list(modi)
    candidati, righe_md = [], []
    for nome, r in ris.items():
        pos = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in nomi_modi}
        for m in nomi_modi:
            if m == RIF:
                continue
            p, c = pos[m]
            rif = pos.get(RIF, (float('-inf'), None))[0]
            if p >= 0.5 and c >= 0.5 and (RIF not in pos or p - rif >= 0.2):
                candidati.append((nome, m, p, c))
        righe_md.append('| %s | %s |' % (nome, ' | '.join('%.2f / %.2f' % pos[m] for m in nomi_modi)))
        print('%-12s %s' % (nome, ' | '.join('%.2f/%.2f' % pos[m] for m in nomi_modi)), flush=True)
    esito = 'candidato, da esaminare' if candidati else 'nessuna lettura'
    json.dump({'lingue': ris, 'candidati': candidati, 'esito': esito}, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# ' + titolo, '', 'Posizione fra controllo negativo (0) e positivo (1): punteggio / copertura con parole di almeno 6 lettere. Preregistrazione: `%s`.' % preregistrazione, '',
          '| lingua | ' + ' | '.join(nomi_modi) + ' |', '|---|' + '---|' * len(nomi_modi)] + righe_md
    md += ['', 'Candidati: %s. Esito: **%s**.' % (candidati or 'nessuno', esito), '', 'Esempi decifrati (primo modo non di riferimento):', '']
    altro = [m for m in nomi_modi if m != RIF][0]
    for nome, r in ris.items():
        v = r.get(altro + ', Voynich', {})
        md.append('- %s: %s' % (nome, ' / '.join(v.get('esempio', [])[:2])[:160]))
    open(os.path.join(RISULTATI, nome_file + '.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, candidati)
    return ris
