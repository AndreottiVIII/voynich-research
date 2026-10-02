# -*- coding: utf-8 -*-
"""Esperimento 159: indice d'informazione delle parole sulla posizione nel testo (Montemurro e Zanette 2013) per Voynich,
latino e testi senza messaggio.

Preregistrazione: preregistrazioni/e159.md. Scrive risultati/e159_montemurro_zanette.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, MINIMO = 159, 20, 10
D = misure.divisore(misure.GLIFI_EVA)


def entropie(testo, P):
    N = len(testo)
    parte = [min(P - 1, i * P // N) for i in range(N)]
    pos = defaultdict(Counter)
    for w, j in zip(testo, parte):
        pos[w][j] += 1
    out = {}
    for w, c in pos.items():
        n = sum(c.values())
        if n >= MINIMO:
            out[w] = -sum(v / n * math.log2(v / n) for v in c.values())
    return out


def informazione(testo, P, rnd):
    N = len(testo)
    H = entropie(testo, P)
    Ht = defaultdict(float)
    for _ in range(RIMESCOLAMENTI):
        x = testo[:]
        rnd.shuffle(x)
        for w, h in entropie(x, P).items():
            Ht[w] += h / RIMESCOLAMENTI
    freq = Counter(testo)
    I = {w: freq[w] / N * (Ht[w] - H[w]) for w in H}
    return sum(I.values()), sorted(I, key=I.get, reverse=True)[:10]


def main():
    rnd = random.Random(SEME)
    voy = [w for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))) if trascrizione.pulita(w)]
    lat = lingue.parole('Latin')
    ts = [w for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')) for w in ps]
    import e131_procedimento_riga as e131, e145_abitudini as e145, e152_righe_in_ordine as e152
    g152 = [w for _, _, ps in e152.genera(e145.pagine(), e131.inizi(), e145.quote(), e152.lift(), 2, 0.5, 1.0, generatori.Modifiche(voy, D), 1) for w in ps if trascrizione.pulita(w)]
    import e128_scrittura_inventata as e128
    gib = [w for _, _, ps in e128.inventati() for w in ps]
    ris = OrderedDict()
    for N, P, testi in ((35000, 32, OrderedDict([('Voynich ZL', voy), ('Bibbia latina', lat), ('Timm e Schinner, seme 19', ts), ('generatore e152 (riferimento)', g152)])),
                        (10000, 10, OrderedDict([('Voynich ZL', voy), ('Bibbia latina', lat), ('Timm e Schinner, seme 19', ts), ('generatore e152 (riferimento)', g152),
                                                 ('testi inventati (Gaskell e Bowern)', gib)]))):
        chiave = 'N %d, P %d' % (N, P)
        ris[chiave] = OrderedDict()
        for nome, t in testi.items():
            t = t[:N]
            I, top = informazione(t, P, rnd)
            ris[chiave][nome] = OrderedDict([('parole', len(t)), ('informazione', I), ('parole_chiave', top)])
            print('%-14s %-38s parole %6d | I %.4f bit/parola | %s' % (chiave, nome, len(t), I, ' '.join(top[:6])), flush=True)
    esiti = OrderedDict()
    for chiave, r in ris.items():
        iv = r['Voynich ZL']['informazione']
        controlli = [n for n in r if n.startswith('Timm') or n.startswith('testi inventati')]
        esiti[chiave] = any(r[n]['informazione'] >= 0.8 * iv for n in controlli)
    ris['parole_chiave_non_distinguono'] = esiti
    print('le parole-chiave non distinguono un contenuto:', dict(esiti))
    with open(os.path.join(RISULTATI, 'e159_montemurro_zanette.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e159 — Le "parole-chiave" di Montemurro e Zanette, con testi senza messaggio', '', 'I = Σ (n/N)(H̃ − H) sulle parole con almeno %d occorrenze; H̃ su %d rimescolamenti. '
           'Preregistrazione: `preregistrazioni/e159.md`.' % (MINIMO, RIMESCOLAMENTI), '', '| impostazione | testo | I (bit/parola) | rispetto al Voynich | prime parole-chiave |', '|---|---|---|---|---|']
    for chiave, r in ris.items():
        if not isinstance(r, dict) or chiave == 'parole_chiave_non_distinguono':
            continue
        iv = r['Voynich ZL']['informazione']
        for nome, x in r.items():
            out.append('| %s | %s | %.4f | %.2f | %s |' % (chiave, nome, x['informazione'], x['informazione'] / iv if iv else 0, ', '.join(x['parole_chiave'][:6])))
    out += ['', 'Le parole-chiave non distinguono un contenuto: **%s**.' % ', '.join('%s %s' % (k, 'sì' if v else 'no') for k, v in esiti.items())]
    with open(os.path.join(RISULTATI, 'e159_montemurro_zanette.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
