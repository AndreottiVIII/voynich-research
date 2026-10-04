# -*- coding: utf-8 -*-
"""Esperimento e3c65: le ripetizioni di parole vicine negli scribi veri e nel cifrario Copiale (batteria scribi, 6).
Misura dell'e3b25: quota di coppie di parole vicine nella stessa riga identiche (parole di almeno 2 segni) e a una sola
modifica (parole di almeno 3 segni). Scribi Menota a livello facsimile; Copiale a livello del cifrato (parole = simboli
fra due simboli-spazio). Voynich ZL rifatto nella stessa esecuzione su tutto il testo (e3b25: 1,01% e 4,13%, mediane di
sottocampioni).

Preregistrazione: preregistrazioni/e3c65.md. Scrive risultati/e3c65_ripetizioni_scribi.json e .md.
"""
import json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import copiale_allinea as ca
import e375_coppie as e375
import e3b25_ripetizioni_grezze as e3b25
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANOSCRITTI = ['AM-519a-4to', 'AM-677-4to', 'AM-60-4to', 'AM-242-fol', 'Holm-A-10', 'AM-302-fol']


def righe_copiale():
    out = []
    for _, simboli, _ in ca.leggi():
        if '#' in simboli:
            continue
        r, w = [], []
        for s in simboli:
            if ca.spazio(s):
                if w:
                    r.append(tuple(w))
                w = []
            else:
                w.append(s)
        if w:
            r.append(tuple(w))
        if r:
            out.append(r)
    return out


def main():
    ris = OrderedDict()
    ris['Voynich ZL'] = e3b25.quote([r for p in e375.voynich() for r in p])
    print('Voynich', json.dumps(ris['Voynich ZL']), flush=True)
    for ms in MANOSCRITTI:
        ris[ms] = e3b25.quote([[tuple(w) for w in r] for _, _, rr in e3c58.leggi(ms) for r in rr])
        print(ms, json.dumps(ris[ms]), flush=True)
    ris['Copiale (cifrato)'] = e3b25.quote(righe_copiale())
    print('Copiale', json.dumps(ris['Copiale (cifrato)']), flush=True)
    v = ris['Voynich ZL']
    come = [k for k, x in ris.items() if k != 'Voynich ZL' and x['ripetizione'] >= v['ripetizione'] / 2 and x['quasi'] >= v['quasi'] / 2]
    esito = ('almeno un testo scritto a mano ripete come il Voynich: ' + ', '.join(come)) if come else 'nessuno scriba né il Copiale ripete come il Voynich'
    out = OrderedDict([('misure', ris), ('come_voynich', come), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c65_ripetizioni_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c65 — Le ripetizioni di parole vicine negli scribi veri e nel Copiale', '', 'Preregistrazione: `preregistrazioni/e3c65.md`. Misura dell\'e3b25 (lingue: mediana 0,10% / 0,23%, massimo 0,71% / 2,21%).', '',
          '| testo | coppie | parole vicine identiche | a una modifica |', '|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.4f | %.4f |' % (k, x['coppie'], x['ripetizione'], x['quasi']))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c65_ripetizioni_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
