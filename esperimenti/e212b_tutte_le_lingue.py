# -*- coding: utf-8 -*-
"""Esperimento 212b: come l'e212 (testo ripulito, segni EVA) su tutte le lingue della cache non fatte nell'e212.

Preregistrazione: preregistrazioni/e212b.md. Scrive risultati/e212b_tutte_le_lingue.json e .md.
"""
import json, os, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue
import e17_ricottura as e17
import e212_forza_bruta_ripulito as e212

RISULTATI = os.path.join(QUI, '..', 'risultati')
MODO = 'ripulito, segni EVA'


def una(args):
    try:
        return e17.una_lingua(args)
    except Exception as e:
        return args[1], {'errore': repr(e)}


def main():
    # le ripartenze (2) si impostano con la variabile d'ambiente RIPARTENZE, letta da e17 all'importazione
    voynich = OrderedDict([(MODO, e212.modi()[MODO])])
    lingue_tutte = [k for k in lingue.indice() if k not in e17.LINGUE]
    lavori = [(k, k, voynich) for k in lingue_tutte]
    ris = OrderedDict()
    percorso = os.path.join(RISULTATI, 'e212b_tutte_le_lingue.json')
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, lavori):
            ris[nome] = r
            json.dump(ris, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            if 'errore' not in r:
                print('%-26s punteggio %.2f copertura_6 %.2f' % (nome, e17.posizione(r, MODO, 'punteggio'), e17.posizione(r, MODO, 'copertura_6')), flush=True)
            else:
                print(nome, r['errore'], flush=True)
    grad = sorted(((n, e17.posizione(r, MODO, 'punteggio'), e17.posizione(r, MODO, 'copertura_6')) for n, r in ris.items() if 'errore' not in r), key=lambda x: -(x[1] + x[2]))
    candidati = [g for g in grad if g[1] >= 0.5 and g[2] >= 0.5]
    json.dump({'lingue': ris, 'graduatoria': grad, 'candidati': candidati}, open(percorso, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e212b — Forza bruta sul testo ripulito in tutte le lingue', '', 'Posizione del Voynich fra controllo negativo (0) e positivo (1). Preregistrazione: `preregistrazioni/e212b.md`.', '',
          '| lingua | punteggio | copertura_6 |', '|---|---|---|'] + ['| %s | %.2f | %.2f |' % g for g in grad]
    md += ['', 'Candidati (da riprovare con e212c): %s.' % (', '.join(g[0] for g in candidati) or 'nessuno')]
    open(os.path.join(RISULTATI, 'e212b_tutte_le_lingue.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('candidati', candidati)


if __name__ == '__main__':
    main()
