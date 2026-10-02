# -*- coding: utf-8 -*-
"""Esperimento 216: risolutore dell'e17 sul testo ripulito con ordini di lettura diversi (righe al contrario, parole al
contrario, per colonne) e senza i segni facoltativi piu' frequenti; 6 lingue.

Preregistrazione: preregistrazioni/e216.md. Scrive risultati/e216_ordini_di_lettura.json e .md.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e17_ricottura as e17
import e160_testo_ripulito as e160

RISULTATI = os.path.join(QUI, '..', 'risultati')
LINGUE = OrderedDict([('Latin', 'latino'), ('Italian', 'italiano'), ('German', 'tedesco'), ('Spanish', 'spagnolo'), ('Czech', 'ceco'), ('Hebrew', 'ebraico')])
RIF = 'ripulito, segni EVA'
MODI = [RIF, 'righe al contrario', 'parole al contrario', 'per colonne', 'senza segni facoltativi']
G = misure.divisore(misure.GLIFI_EVA)
GALLOW = {'k', 't', 'p', 'f', 'ch', 'sh', 'ckh', 'cth', 'cph', 'cfh'}


def senza_facoltativi(w):
    u = G(w)
    if len(u) >= 3 and u[0] == 'o' and u[1] in GALLOW:
        u = u[1:]
    if len(u) >= 3 and u[-1] == 'y':
        u = u[:-1]
    return ''.join(u)


def modi():
    pul = e160.ripulisci(e160.pagine_voynich())
    righe = [[w if trascrizione.pulita(w) else None for w in ps] for p in pul for _, ps in p]
    out = OrderedDict()
    out[RIF] = e17.in_unita(righe, G)
    base = out[RIF]
    ammesse = {u for r in base for u in r}
    out['righe al contrario'] = [r[::-1] for r in base]
    out['parole al contrario'] = e17.in_unita(righe, lambda w: G(w)[::-1], ammesse=ammesse)
    colonne = []
    for p in pul:
        rr = [[w if trascrizione.pulita(w) else None for w in ps] for _, ps in p]
        for i in range(max(len(r) for r in rr)):
            colonne.append([r[i] for r in rr if i < len(r)])
    out['per colonne'] = e17.in_unita(colonne, G, ammesse=ammesse)
    out['senza segni facoltativi'] = e17.in_unita([[senza_facoltativi(w) if w else None for w in r] for r in righe], G, ammesse=ammesse)
    return out


def main():
    voynich = modi()
    for m, rr in voynich.items():
        print('%-26s simboli %d lunghezza %d righe %d' % (m, len({u for r in rr for u in r}), sum(map(len, rr)), len(rr)), flush=True)
    lavori = [(k, n, voynich) for k, n in LINGUE.items()]
    ris = OrderedDict()
    percorso = os.path.join(RISULTATI, 'e216_ordini_di_lettura.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(e17.una_lingua, lavori):
            ris[nome] = r
            json.dump(ris, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    candidati, righe_md = [], []
    for nome, r in ris.items():
        pos = {m: (e17.posizione(r, m, 'punteggio'), e17.posizione(r, m, 'copertura_6')) for m in MODI}
        for m in MODI[1:]:
            p, c = pos[m]
            if p >= 0.5 and c >= 0.5 and p - pos[RIF][0] >= 0.2:
                candidati.append((nome, m, p, c))
        righe_md.append('| %s | %s |' % (nome, ' | '.join('%.2f / %.2f' % pos[m] for m in MODI)))
        print('%-10s %s' % (nome, ' | '.join('%.2f/%.2f' % pos[m] for m in MODI)), flush=True)
    esito = 'candidato, da esaminare' if candidati else 'nessuna lettura'
    json.dump({'lingue': ris, 'candidati': candidati, 'esito': esito}, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e216 — Forza bruta con altri ordini di lettura', '', 'Posizione fra controllo negativo (0) e positivo (1): punteggio / copertura_6. Preregistrazione: `preregistrazioni/e216.md`.', '',
          '| lingua | ' + ' | '.join(MODI) + ' |', '|---|' + '---|' * len(MODI)] + righe_md + ['', 'Candidati: %s. Esito: **%s**.' % (candidati or 'nessuno', esito)]
    open(os.path.join(RISULTATI, 'e216_ordini_di_lettura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, candidati)


if __name__ == '__main__':
    main()
