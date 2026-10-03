# -*- coding: utf-8 -*-
"""Esperimento e3a63: il legame dell'e3a14 dopo aver tolto le coppie con una parola copiata dalla riga sopra, contro
lo stesso togliendo le coppie con una parola presente in una riga lontana (controllo); Voynich e Timm e Schinner.

Preregistrazione: preregistrazioni/e3a63.md. Scrive risultati/e3a63_legame_copia.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e337_posizione as e337
import e341_fonti as e341
import e380_sandhi as e380
import e385_calo as e385

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
VOLTE = 20
PERM = 100


def prepara(pagine):
    """pagine: [(pagina, [paragrafi di righe di parole (tuple)])]. Restituisce [(pagina, riga, sopra, lontane, sim)]."""
    out = []
    for pg, pars in pagine:
        righe_pg = [r for par in pars for r in par]
        sim = e385.simili_unita(righe_pg)
        k = 0
        for par in pars:
            for i, r in enumerate(par):
                idx = k + i
                lontane = [j for j in range(len(righe_pg)) if abs(j - idx) >= 3]
                if i >= 1 and lontane and len(r) >= 2:
                    out.append((pg, r, set(par[i - 1]), [set(righe_pg[j]) for j in lontane], sim))
            k += len(par)
    return out


def eventi(dati, scegli):
    """scegli(d) -> insieme di riferimento, oppure None per tenere tutte le coppie."""
    av, ind = [], []
    for d in dati:
        pg, r, _, _, sim = d
        ref = scegli(d)
        for a, b in zip(r, r[1:]):
            if ref is not None and (sim[a] & ref or sim[b] & ref):
                continue
            av.append(((pg, a[-1]), a, b[0]))
            ind.append(((pg, b[0]), b, a[-1]))
    return av, ind


def analizza(dati, rnd):
    ris = OrderedDict()
    tutte = eventi(dati, lambda d: None)
    sopra = eventi(dati, lambda d: d[2])
    lont = []
    for v in range(VOLTE):
        rr = random.Random(rnd.random())
        lont.append(eventi(dati, lambda d: rr.choice(d[3])))
    for j, lato in enumerate(('avanti', 'indietro')):
        e_tutte = e380.prova(tutte[j], rnd, PERM)
        e_sopra = e380.prova(sopra[j], rnd, PERM)
        e_lont = [e380.prova(x[j], rnd, PERM) for x in lont]
        Er = [x['E'] for x in e_lont]
        mr = statistics.mean(Er)
        Es = e_sopra['E']
        if Es < min(Er) and Es < 0.5 * mr:
            es = 'la copia dalla riga sopra spiega il legame'
        elif Es < min(Er):
            es = 'ne spiega una parte'
        else:
            es = 'la copia non c\'entra'
        ris[lato] = OrderedDict([('tutte', e_tutte), ('sopra', e_sopra), ('lontana_E', Er), ('lontana_eventi', [x['eventi'] for x in e_lont]),
                                 ('lontana_media', mr), ('lontana_min', min(Er)), ('lontana_max', max(Er)), ('esito', es)])
        print(lato, json.dumps(ris[lato], default=float, ensure_ascii=False), flush=True)
    return ris


def main():
    rnd = random.Random(3163)
    voy = [(pg, [[[w for w in (tuple(D(x)) for x in r) if w] for r in par] for par in pars]) for pg, pars in e341.pagine().items()]
    ts = [(i, [[[tuple(D(w)) for w in r] for r in p]]) for i, p in enumerate(e337.pagine_ts(1))]
    out = OrderedDict()
    for nome, pagine in (('Voynich', voy), ('Timm e Schinner, seme 1 (controllo positivo)', ts)):
        print(nome, flush=True)
        dati = prepara(pagine)
        out[nome] = analizza(dati, rnd)
        out[nome]['righe'] = len(dati)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a63_legame_copia.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a63 — Il piccolo legame fra parole intere viene dalla copia dalla riga sopra?', '', 'Preregistrazione: `preregistrazioni/e3a63.md`. E come nell\'e3a14; "sopra": tolte le coppie con una parola uguale o a una modifica nella riga sopra; "lontana": lo stesso con una riga a caso a distanza 3 o più (20 volte).', '',
          '| testo | direzione | tutte: E (eventi) | sopra: E (eventi) | lontana: media E (min – max), eventi medi | esito |', '|---|---|---|---|---|---|']
    for nome, x in out.items():
        for lato in ('avanti', 'indietro'):
            y = x[lato]
            md.append('| %s | %s | %.4f (%d) | %.4f (%d) | %.4f (%.4f – %.4f), %d | %s |' % (nome, lato, y['tutte']['E'], y['tutte']['eventi'], y['sopra']['E'], y['sopra']['eventi'],
                                                                                    y['lontana_media'], y['lontana_min'], y['lontana_max'], statistics.mean(y['lontana_eventi']), y['esito']))
    open(os.path.join(RISULTATI, 'e3a63_legame_copia.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
