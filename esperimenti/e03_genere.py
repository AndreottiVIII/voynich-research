# -*- coding: utf-8 -*-
"""Esperimento 3: il genere del testo spiega la poca sintassi del Voynich?

L'esperimento 2 trova che nel Voynich una parola dice pochissimo sulla parola
che segue, meno che in qualsiasi Bibbia. Ma la Bibbia e' prosa narrativa: un
ricettario o un erbario potrebbero avere meno sintassi. Qui confrontiamo il
Voynich, sezione per sezione, con ricette, manuali di agricoltura, voci di
piante e trattati tecnici in latino, tutti a 7.500 parole (Apicio e' corto).

Scrive risultati/e03_genere.json e risultati/e03_genere.md.
"""
import json, os, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
from e02_impronta import misura

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 7500


def testi():
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl = trascrizione.leggi('ZL')
    yield 'Voynich, tutto il testo', 'voynich', trascrizione.parole(trascrizione.testo_corrente(zl)), glifi
    for sez, nome in [('H', 'erbario'), ('B', 'biologica'), ('S', 'ricette (stelle a margine)')]:
        yield 'Voynich, sezione %s' % nome, 'voynich', trascrizione.parole(
            trascrizione.testo_corrente(zl, sezione=sez)), glifi
    for nome in lingue.GENERI:
        yield nome, 'latino tecnico', lingue.genere(nome), None
    yield 'Bibbia latina', 'bibbia', lingue.parole('Latin'), None
    yield 'Bibbia italiana', 'bibbia', lingue.parole('Italian'), None


def main():
    ris = {'N': N, 'testi': {}}
    for nome, gruppo, parole, dividi in testi():
        r = misura(parole, N, dividi)
        if r is None:
            print('%-40s troppo corto (%d parole)' % (nome, len(parole)))
            continue
        r.update({'gruppo': gruppo, 'disponibili': len(parole)})
        ris['testi'][nome] = r
        print('%-40s parole %6d  h2 %.2f  tipi/parole %.3f  IM+ %.3f  rip x%.2f  somiglianza %.3f' % (
            nome, len(parole), r['h2'], r['tipi_su_parole'], r['im_vicine_eccesso'],
            r['ripetute_rapporto'], r['dist_rapporto_diverse']))
    with open(os.path.join(RISULTATI, 'e03_genere.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# Esperimento 3: il genere del testo', '',
           'Campioni di %d parole, media di tre finestre. Stesse misure dell\'esperimento 2.' % N, '',
           '| testo | gruppo | parole disponibili | h2 | tipi/parole | IM in più | ripetute × | somiglianza vicine |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in sorted(ris['testi'].items(), key=lambda kv: kv[1]['im_vicine_eccesso']):
        out.append('| %s | %s | %d | %.2f | %.3f | %.3f ± %.3f | %.2f | %.3f |' % (
            nome, r['gruppo'], r['disponibili'], r['h2'], r['tipi_su_parole'],
            r['im_vicine_eccesso'], r['im_vicine_eccesso_dev'], r['ripetute_rapporto'],
            r['dist_rapporto_diverse']))
    with open(os.path.join(RISULTATI, 'e03_genere.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
