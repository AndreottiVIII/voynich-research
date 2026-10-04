# -*- coding: utf-8 -*-
"""Esperimento e3c01: alternanze di lettere dentro la parola scelte dai dati (coppie minime), stessa regola per il
Voynich e per i testi grandi del corpus; memoria (e3b62 + e3b70) e forma del calo (e3b96).

Preregistrazione: preregistrazioni/e3c01.md. Scrive risultati/e3c01_alternanze_interne.json e .md.
"""
import json, os, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b51_thorn_eth as e3b51
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3b96_forma_calo as e3b96

RISULTATI = os.path.join(QUI, '..', 'risultati')
MIN_PAROLE = 50000
COPPIE = 3
MIN_FREQ = 2


def alternanze(sequenze, quante=COPPIE):
    """Le coppie di lettere (x, y) che formano più coppie minime in una posizione interna (né prima né ultima), fra
    tipi di parola visti almeno MIN_FREQ volte; coppie con lettere tutte diverse fra loro."""
    freq = Counter(w for s in sequenze for w in s if len(w) >= 3)
    chiavi = {}
    for w, n in freq.items():
        if n < MIN_FREQ:
            continue
        for i in range(1, len(w) - 1):
            chiavi.setdefault(w[:i] + ('*',) + w[i + 1:], set()).add(w[i])
    punti = Counter()
    for lettere in chiavi.values():
        ll = sorted(lettere)
        for a in range(len(ll)):
            for b in range(a + 1, len(ll)):
                punti[(ll[a], ll[b])] += 1
    scelte, usate = [], set()
    for (x, y), _ in punti.most_common():
        if x in usate or y in usate:
            continue
        scelte.append((x, y))
        usate |= {x, y}
        if len(scelte) == quante:
            break
    return scelte, [punti[c] for c in scelte]


def classe(x, y):
    def f(w):
        pos = [i for i in range(1, len(w) - 1) if w[i] in (x, y)]
        if len(w) < 3 or len(pos) != 1:
            return None
        i = pos[0]
        return (1 if w[i] == y else 0, w[:i] + ('*',) + w[i + 1:])
    return f


def misura(uu, strati, classi, rng):
    cc = OrderedDict((k, e3b62.prepara(uu, strati, f)) for k, f in classi.items())
    pr = e3b62.prova(cc, rng)
    ins = pr['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], ins['nullo'], rng)
    per_classe = OrderedDict((k, OrderedDict([('M', pr[k]['M']), ('nullo', pr[k].get('nullo'))])) for k in classi)
    r = e3b96.rapporto([e3b96.somme_unita(u, classi) for u in uu])
    return OrderedDict([('occorrenze', int(sum(len(c['val']) for c in cc.values()))), ('coppie_vicine', ins['coppie_vicine']), ('M', ins['M']), ('nullo', ins['nullo']),
                        ('effetto', iv['effetto']), ('IC95', iv['IC95']), ('R', r), ('per_classe', per_classe)])


def main():
    rng = np.random.default_rng(3301)
    testi = OrderedDict()
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    for nome, pd in (('Voynich IT', e3b45.pagine_it()), ('Voynich ZL', e341.pagine())):
        uu, ss = e3b62.voynich(pd, mano)
        testi[nome] = (uu, ss, [r for u in uu for r in u])
    for chiave, righe in e381.testi().items():
        righe = [r for r in righe if r]
        if 'Abbreviated' in chiave or sum(len(r) for r in righe) < MIN_PAROLE:
            continue
        uu = [[b] for b in e3b51.blocchi(righe)]
        testi[chiave.replace('.txt', '')] = (uu, [chiave] * len(uu), [b for u in uu for b in u])
    ris = OrderedDict()
    for nome, (uu, ss, seq) in testi.items():
        scelte, punti = alternanze(seq)
        classi = OrderedDict(('%s/%s' % c, classe(*c)) for c in scelte)
        x = misura(uu, ss, classi, rng)
        x['alternanze'] = ['%s/%s' % c for c in scelte]
        x['coppie_minime'] = punti
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    voy = [ris['Voynich IT'], ris['Voynich ZL']]
    rif = min(v['effetto'] if v['effetto'] is not None else 0.0 for v in voy)
    lingue = [k for k in ris if not k.startswith('Voynich')]
    simili = [k for k in lingue if ris[k]['IC95'] and ris[k]['IC95'][0] > 0 and ris[k]['effetto'] >= rif / 2]
    if not all(v['IC95'] and v['IC95'][0] > 0 for v in voy):
        esito = 'il metodo generico non trova la memoria nel Voynich'
    elif len(simili) <= 2:
        esito = 'le alternanze interne hanno memoria solo nel Voynich'
    elif len(simili) >= 5:
        esito = 'anche le lingue'
    else:
        esito = 'incerto'
    out = OrderedDict([('testi', ris), ('riferimento_voynich', rif), ('lingue_simili', simili), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c01_alternanze_interne.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c01 — Le alternanze dentro la parola, scelte dai dati, hanno memoria fuori dal Voynich?', '', 'Preregistrazione: `preregistrazioni/e3c01.md`. Tre coppie di lettere per testo, scelte dalle coppie minime in posizione interna.', '',
          '| testo | alternanze | occorrenze | coppie vicine | effetto (IC 95%) | R |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        ef = '—' if x['effetto'] is None or not x['IC95'] else '%+.4f (%+.4f – %+.4f)' % (x['effetto'], x['IC95'][0], x['IC95'][1])
        md.append('| %s | %s | %d | %d | %s | %s |' % (k, ' '.join(x['alternanze']), x['occorrenze'], x['coppie_vicine'], ef, '—' if x['R'] is None else '%.2f' % x['R']))
    md += ['', 'Riferimento (il più piccolo dei due Voynich): %+.4f. Lingue con intervallo sopra 0 ed effetto almeno metà: %s.' % (rif, ', '.join(simili) or 'nessuna'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c01_alternanze_interne.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
