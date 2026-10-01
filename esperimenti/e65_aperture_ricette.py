# -*- coding: utf-8 -*-
"""Esperimento 65: formule d'apertura nelle ricette. Le prime parole dei paragrafi sono
concentrate su poche forme piu' delle parole interne?

Voynich (sezione ricette, $I=S), Apicio (controllo positivo), Bibbia latina (versetti).
Preregistrazione: preregistrazioni/e65.md. Scrive risultati/e65_aperture_ricette.json e .md.
"""
import json, os, random, re, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ESTRAZIONI, PRIME = 200, 5


def concentrazione(parole):
    c = Counter(parole)
    return sum(n for _, n in c.most_common(PRIME)) / len(parole)


def paragrafi_voynich():
    out, cur = [], None
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione='S'):
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        if r.inizio_par or cur is None:
            if cur and len(cur) >= 4:
                out.append(cur)
            cur = []
        cur.extend(ps)
    if cur and len(cur) >= 4:
        out.append(cur)
    return out


def paragrafi_apicio():
    out = []
    for i in range(1, 6):
        testo = open(os.path.join(lingue.LATIN_LIBRARY, 'apicius', 'apicius%d.txt' % i), encoding='utf-8').read()
        for riga in testo.splitlines():
            s = riga.strip()
            if not s or re.match(r'^\d+\.', s) or s.isupper() or 'Latin Library' in s:
                continue
            ps = lingue.normalizza(s).split()
            if 'apicius' in ps:             # intestazioni del file ("Apicius: de re coquinaria, liber I")
                continue
            if len(ps) >= 4:
                out.append(ps)
    return out


def paragrafi_bibbia(n=1500):
    """Versetti della Bibbia latina dal corpus (un versetto = un paragrafo)."""
    import xml.etree.ElementTree as ET
    import lingue as L
    percorso = os.path.join(L.SORGENTE, 'bibles', 'Latin.xml')
    testo = open(percorso, encoding='utf-8').read()
    versi = re.findall(r"<seg[^>]*>(.*?)</seg>", testo, re.S)
    out = []
    for v in versi:
        ps = L.normalizza(v).split()
        if len(ps) >= 4:
            out.append(ps)
        if len(out) >= n:
            break
    return out


def prova(paragrafi, seme=65):
    ap = concentrazione([p[0] for p in paragrafi])
    se = concentrazione([p[1] for p in paragrafi])
    rnd = random.Random(seme)
    nulle = np.array([concentrazione([p[rnd.randrange(1, len(p) - 1)] for p in paragrafi]) for _ in range(ESTRAZIONI)])
    return {'paragrafi': len(paragrafi), 'apertura': ap, 'seconda': se, 'interne': float(nulle.mean()),
            'rapporto': ap / float(nulle.mean()), 'p': float((1 + (nulle >= ap).sum()) / (1 + ESTRAZIONI)),
            'aperture_frequenti': Counter(p[0] for p in paragrafi).most_common(8)}


def main():
    testi = OrderedDict([('Voynich, ricette', paragrafi_voynich()), ('Apicio (controllo positivo)', paragrafi_apicio())])
    try:
        testi['Bibbia latina (versetti)'] = paragrafi_bibbia()
    except (OSError, IndexError) as e:
        print('Bibbia non disponibile:', e)
    ris = OrderedDict()
    for nome, par in testi.items():
        ris[nome] = prova(par)
        r = ris[nome]
        print('%-28s paragrafi %4d apertura %.3f seconda %.3f interne %.3f rapporto %.2f p %.3f | %s' % (
            nome, r['paragrafi'], r['apertura'], r['seconda'], r['interne'], r['rapporto'], r['p'],
            r['aperture_frequenti'][:5]), flush=True)
    with open(os.path.join(RISULTATI, 'e65_aperture_ricette.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e65 — Formule d\'apertura nelle ricette', '',
           'Concentrazione = quota coperta dalle %d forme più frequenti. Interne = una parola interna a caso per '
           'paragrafo (media di %d estrazioni). Preregistrazione: `preregistrazioni/e65.md`.' % (PRIME, ESTRAZIONI), '',
           '| testo | paragrafi | aperture | seconde | interne | rapporto | p | aperture più frequenti |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %d | %.3f | %.3f | %.3f | %.2f | %.3f | %s |' % (
            nome, r['paragrafi'], r['apertura'], r['seconda'], r['interne'], r['rapporto'], r['p'],
            ', '.join('%s %d' % x for x in r['aperture_frequenti'][:5])))
    with open(os.path.join(RISULTATI, 'e65_aperture_ricette.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
