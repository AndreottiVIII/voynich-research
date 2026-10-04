# -*- coding: utf-8 -*-
"""Esperimento e3b43: copia dalla riga sopra (parole simili nella riga sopra contro le altre righe del paragrafo) nelle
pagine "solo testo" e nelle altre, contando le parole dalla quarta della riga in poi.

Preregistrazione: preregistrazioni/e3b43.md. Scrive risultati/e3b43_solo_testo_copia.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e341_fonti as e341
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000


def paragrafo(par, da):
    """(osservate nella riga sopra, attese dalle altre righe) per le parole dalla posizione `da` in poi."""
    sim = e385.simili_unita(par)
    o = a = 0.0
    for i in range(1, len(par)):
        sopra = par[i - 1]
        altre = [j for j in range(len(par)) if j not in (i, i - 1) and len(par[j]) >= 4]
        if len(sopra) < 4 or not altre:
            continue
        for w in par[i][da:]:
            if len(w) < 3:
                continue
            o += sum(v in sim[w] for v in sopra)
            a += sum(sum(v in sim[w] for v in par[j]) for j in altre) / len(altre)
    return o, a


def rapporto(bb):
    o, a = sum(b[0] for b in bb), sum(b[1] for b in bb)
    return o / a if a else None


def main():
    rnd = random.Random(3243)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    gruppi = OrderedDict([('solo testo (T)', []), ('altre pagine', [])])
    for pg, pars in e341.pagine().items():
        for par in pars:
            pp = [[w for w in (tuple(D(x)) for x in r if trascrizione.pulita(x)) if w] for r in par]
            pp = [r for r in pp if r]
            if len(pp) >= 3:
                gruppi['solo testo (T)' if sezione.get(pg) == 'T' else 'altre pagine'].append(pp)
    ris = OrderedDict()
    for k, pars in gruppi.items():
        x = OrderedDict([('paragrafi', len(pars))])
        for nome, da in (('dalla_quarta', 3), ('tutte', 0)):
            bb = [paragrafo(p, da) for p in pars]
            r = rapporto(bb)
            boot = sorted(v for v in (rapporto([bb[rnd.randrange(len(bb))] for _ in bb]) for _ in range(BOOT)) if v is not None)
            x[nome] = OrderedDict([('osservate', sum(b[0] for b in bb)), ('attese', sum(b[1] for b in bb)), ('rapporto', r),
                                   ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])
        ris[k] = x
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    t, a = ris['solo testo (T)']['dalla_quarta'], ris['altre pagine']['dalla_quarta']
    if t['IC95'][0] > 1:
        esito = 'copia anche nelle pagine solo testo'
    elif t['IC95'][0] <= 1 <= t['IC95'][1] and (t['rapporto'] - 1) < 0.5 * (a['rapporto'] - 1):
        esito = 'nelle pagine solo testo manca la copia'
    else:
        esito = 'incerto'
    out = OrderedDict([('gruppi', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b43_solo_testo_copia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b43 — Nelle pagine "solo testo" c\'è la copia dalla riga sopra?', '', 'Preregistrazione: `preregistrazioni/e3b43.md`.', '',
          '| pagine | paragrafi | parole contate | simili nella riga sopra | attese (altre righe) | rapporto (IC 95%) |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        for nome, et in (('dalla_quarta', 'dalla quarta parola'), ('tutte', 'tutte (descrittivo)')):
            y = x[nome]
            md.append('| %s | %d | %s | %.0f | %.1f | %.2f (%.2f – %.2f) |' % (k, x['paragrafi'], et, y['osservate'], y['attese'], y['rapporto'], y['IC95'][0], y['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b43_solo_testo_copia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
