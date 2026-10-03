# -*- coding: utf-8 -*-
"""Esperimento 279c: come l'e279b, con i controlli positivi di Bacone allineati (puro e al 70%), come nell'e279.

Preregistrazione: preregistrazioni/e279c.md. Scrive risultati/e279c_bacone_corretto.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e252_interruttori_riga as e252
import e279_bacone_classi as e279
import e279b_verifica_bacone as e279b

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 2792


def allineato(rb, msg, p, rnd):
    """Il bit i del flusso diventa il bit i del messaggio con probabilita' p; i blocchi delle parole restano uguali."""
    it = iter(zip(msg, e279b.flusso(rb)))
    return [[[m if rnd.random() < p else v for m, v in (next(it) for _ in b)] for b in r] for r in rb]


def main():
    rnd = random.Random(SEME)
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    rb_v = e279b.righe_bit(voy, classi)
    k = e251._prepara()
    inter = e251.interruttori_voynich(classi)
    rr = e236.dopo(e252.genera_ii(k['c2'], dict(e251.CONF, gamma=0.0), 7, inter), k['freq'], 107)
    rb_g = e279b.righe_bit([[w for w in ps if trascrizione.pulita(w)] for _, _, ps in rr], classi)
    msg = e279.bacone(len(e279b.flusso(rb_v)))
    testi = OrderedDict([('Voynich', rb_v), ('generatore e241 + interruttori (seme 7)', rb_g),
                         ('positivo: Bacone puro, allineato', allineato(rb_v, msg, 1.0, rnd)), ('positivo: Bacone al 70%, allineato', allineato(rb_v, msg, 0.7, rnd))])
    ris = OrderedDict()
    for n, rb in testi.items():
        ris[n] = OrderedDict([('bit', len(e279b.flusso(rb))), ('nullo a parole intere', e279b.nullo_parole(rb, rnd))])
        print('%-42s parole intere z %.1f' % (n, ris[n]['nullo a parole intere']['z'] or 0), flush=True)
    z = lambda n: ris[n]['nullo a parole intere']['z'] or 0
    valido = z('positivo: Bacone puro, allineato') > 4
    regge = z('Voynich') > 4 and z('Voynich') - z('generatore e241 + interruttori (seme 7)') >= 3
    esito = 'non valido' if not valido else ('il canale regge (nessuna lettura)' if regge else 'artefatto delle parole ripetute')
    json.dump(OrderedDict([('risultati', ris), ('valido', valido), ('esito', esito)]), open(os.path.join(RISULTATI, 'e279c_bacone_corretto.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    md = ['# e279c — Verifica del canale "alla Bacone" con i positivi corretti', '',
          'Indice di coincidenza dei gruppi di 5 bit, z contro %d rimescolamenti di parole intere dentro la riga. Preregistrazione: `preregistrazioni/e279c.md`.' % e279b.RIMESCOLAMENTI,
          '', '| testo | bit | indice | nullo | z |', '|---|---|---|---|---|']
    for n, r in ris.items():
        x = r['nullo a parole intere']
        md.append('| %s | %d | %.4f | %.4f | %.1f |' % (n, r['bit'], x['ioc'], x['nullo'], x['z'] or 0))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e279c_bacone_corretto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
