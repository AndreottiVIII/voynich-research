# -*- coding: utf-8 -*-
"""Esperimento e3c80: le ripetizioni di parole vicine del Voynich vengono dal genere (elenchi di ricette, erbari,
astrologia), che ripete formule? Misura dell'e3b25 (parole vicine identiche e a una modifica nella stessa riga) sui
cinque manoscritti tecnici del ReF 1350 – 1500 (testo intero): Buch der Natur, Naturlehre Mainau, Ulmer Wundarznei,
Mondbuch, Buch aller verbotenen Künste; Voynich ZL intero e per sezione (erbario, biologia, farmacia, stelle/ricette,
il resto). Anche i tipi di parola ogni 10.000.

Preregistrazione: preregistrazioni/e3c80.md. Scrive risultati/e3c80_ripetizioni_testi_tecnici.json e .md.
"""
import glob, json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b25_ripetizioni_grezze as e3b25
import e3b62_memoria_nullo_largo as e3b62
import ref_leggi

RISULTATI = os.path.join(QUI, '..', 'risultati')
TECNICI = OrderedDict([('F001', 'Buch der Natur (c. 1350 – 75)'), ('F088', 'Naturlehre Mainau'), ('F120', 'Ulmer Wundarznei (ricette di chirurgia)'),
                       ('F219', 'Mondbuch (astrologia)'), ('F137', 'Buch aller verbotenen Künste (magia, alchimia)')])
SEZIONI = OrderedDict([('erbario', ('H',)), ('biologia', ('B',)), ('farmacia', ('P',)), ('stelle / ricette', ('S',))])


def misura(righe):
    x = e3b25.quote(righe)
    tok = [w for r in righe for w in r][:10000]
    x['tipi_su_10000'] = len(set(tok)) if len(tok) >= 10000 else None
    x['parole'] = sum(len(r) for r in righe)
    return x


def main():
    ris = OrderedDict()
    sez = {}
    for r in trascrizione.leggi('ZL'):
        if r.sezione:
            sez.setdefault(r.pagina, r.sezione)
    pd = e341.pagine()
    tutte = []
    per_sez = OrderedDict((k, []) for k in SEZIONI)
    for pg, pars in pd.items():
        rr = [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]
        rr = [r for r in rr if r]
        tutte += rr
        for k, ss in SEZIONI.items():
            if sez.get(pg) in ss:
                per_sez[k] += rr
    ris['Voynich ZL, tutto'] = misura(tutte)
    for k, rr in per_sez.items():
        ris['Voynich ZL, ' + k] = misura(rr)
    for f in sorted(glob.glob(os.path.join(ref_leggi.CARTELLA, '*', '*.xml'))):
        sigla = os.path.basename(f)[:-4]
        if sigla in TECNICI:
            _, pagine = ref_leggi.leggi(f)
            ris['%s %s' % (sigla, TECNICI[sigla])] = misura([[tuple(w) for w in r] for _, rr in pagine for r in rr])
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    v = ris['Voynich ZL, tutto']
    come = [k for k, x in ris.items() if not k.startswith('Voynich') and x['ripetizione'] >= v['ripetizione'] / 2 and x['quasi'] >= v['quasi'] / 2]
    esito = ('un testo tecnico ripete come il Voynich: ' + ', '.join(come)) if come else 'nessun testo tecnico ripete come il Voynich'
    out = OrderedDict([('misure', ris), ('come_voynich', come), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c80_ripetizioni_testi_tecnici.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c80 — Le ripetizioni del Voynich vengono dal genere?', '', 'Preregistrazione: `preregistrazioni/e3c80.md`.', '',
          '| testo | parole | identiche | a una modifica | tipi su 10.000 |', '|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.4f | %.4f | %s |' % (k, x['parole'], x['ripetizione'], x['quasi'], x['tipi_su_10000'] if x['tipi_su_10000'] else '—'))
    md += ['', 'Esito: **%s**.' % esito, '', 'Fonte dei testi tecnici: ReF 1.0.2, CC-BY-SA 4.0; file non nel repository.']
    open(os.path.join(RISULTATI, 'e3c80_ripetizioni_testi_tecnici.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
