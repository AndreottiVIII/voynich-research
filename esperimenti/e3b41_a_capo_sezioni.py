# -*- coding: utf-8 -*-
"""Esperimento e3b41: memoria delle scelte nella stessa riga e a cavallo dell'a capo (e3b38), sezione per sezione.

Preregistrazione: preregistrazioni/e3b41.md. Scrive risultati/e3b41_a_capo_sezioni.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b38_solo_testo_a_capo as e3b38

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_COPPIE = 300


def main():
    rnd = random.Random(3241)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    gruppi = OrderedDict((s, []) for s in 'HACZBPST')
    for pg, pars in e341.pagine().items():
        pp = [[[w for w in r if trascrizione.pulita(w)] for r in par] for par in pars]
        pp = [[r for r in par if r] for par in pp]
        pp = [par for par in pp if par]
        if sezione.get(pg) in gruppi and pp:
            gruppi[sezione[pg]].append(pp)
    ris = OrderedDict()
    for s, pagine in gruppi.items():
        if not pagine:
            continue
        try:
            ris[s] = e3b38.analizza(pagine, rnd)
        except (KeyError, ZeroDivisionError, IndexError) as e:
            ris[s] = OrderedDict([('pagine', len(pagine)), ('errore', repr(e))])
        print(s, json.dumps(ris[s], ensure_ascii=False), flush=True)
    valide = [s for s, x in ris.items() if s != 'T' and x.get('coppie_a_cavallo', 0) >= MIN_COPPIE]
    sopra = [s for s in valide if ris[s]['IC95_a_cavallo'][0] > 0]
    if not sopra:
        esito = 'solo le pagine solo testo'
    elif sopra == ['S'] or (('S' in sopra) and not any(s in sopra for s in 'HBP')):
        esito = 'anche le ricette'
    else:
        esito = 'anche altre sezioni: ' + ', '.join(sopra)
    out = OrderedDict([('sezioni', ris), ('valide', valide), ('sopra_zero', sopra), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b41_a_capo_sezioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b41 — La memoria che passa l\'a capo, sezione per sezione', '', 'Preregistrazione: `preregistrazioni/e3b41.md`.', '',
          '| sezione | pagine | stessa riga: eccesso (coppie) | a cavallo dell\'a capo: eccesso (coppie) | IC 95% a cavallo |', '|---|---|---|---|---|']
    for s, x in ris.items():
        if 'errore' in x:
            md.append('| %s (%s) | %d | — | — | %s |' % (s, trascrizione.SEZIONI[s], x['pagine'], x['errore']))
        else:
            md.append('| %s (%s) | %d | %+.4f (%d) | %+.4f (%d) | %+.4f – %+.4f |' % (s, trascrizione.SEZIONI[s], x['pagine'], x['stessa_riga'], x['coppie_stessa'], x['a_cavallo'], x['coppie_a_cavallo'], x['IC95_a_cavallo'][0], x['IC95_a_cavallo'][1]))
    md += ['', 'Sezioni valide (diverse da T, almeno %d coppie a cavallo): %s.' % (MIN_COPPIE, ', '.join(valide)), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b41_a_capo_sezioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
