# -*- coding: utf-8 -*-
"""Esperimento e3b51: controllo naturale con uno scriba anglosassone. Scelta fra þ e ð: memoria corta (coppie vicine
contro lontane, senza parole simili) e legame con la parola oltre i segni vicini (contro la catena di ordine 2).

Preregistrazione: preregistrazioni/e3b51.md. Scrive risultati/e3b51_thorn_eth.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e381_parole_intere as e381
import e3a71_catene_ordini as e3a71
import e3a78_cosa_spiega_la_catena as e3a78
import e3a86_ripetizioni_riga as e3a86
import e3b49_scelte_parola as e3b49

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
BLOCCO = 25
VICINE, LONTANE = (2, 3), tuple(range(6, 11))
TH = ('þ', 'ð')
TESTI = OrderedDict([('Hatton Gospels', 'Historical - Anglo-Saxon - Literary - NT - Hatton Gospels.txt'),
                     ('Leechbook', 'Historical - Anglo-Saxon - Technical - Leechbook.txt')])


def iniziale(w):
    return (1 if w[0] == 'þ' else 0) if w and w[0] in TH else None


def interna(w):
    pos = [i for i, s in enumerate(w) if i and s in TH]
    return (1 if w[pos[0]] == 'þ' else 0) if len(pos) == 1 else None


CLASSI = OrderedDict([('iniziale', iniziale), ('interna', interna)])


def blocchi(righe):
    return [[w for r in righe[i:i + BLOCCO] for w in r] for i in range(0, len(righe), BLOCCO)]


def eventi_memoria(bb):
    out = []
    for b, parole in enumerate(bb):
        for c, f in CLASSI.items():
            v = [f(w) for w in parole]
            T = sum(1 for x in v if x is not None)
            U = sum(1 for x in v if x == 1)
            for i in range(len(parole)):
                if v[i] is None:
                    continue
                for d in VICINE + LONTANE:
                    j = i + d
                    if j >= len(parole) or v[j] is None:
                        continue
                    a, z = parole[i], parole[j]
                    if a == z or e3a86.una_modifica(a, z):
                        continue
                    t, u = T - 2, U - v[i] - v[j]
                    if t < 5:
                        continue
                    p = u / t
                    out.append((b, 'vicine' if d in VICINE else 'lontane', int(v[i] == v[j]) - (p * p + (1 - p) * (1 - p))))
    return out


def differenza(ev):
    acc = defaultdict(lambda: [0.0, 0])
    for _, g, x in ev:
        acc[g][0] += x
        acc[g][1] += 1
    if not acc['vicine'][1] or not acc['lontane'][1]:
        return None, {}
    return acc['vicine'][0] / acc['vicine'][1] - acc['lontane'][0] / acc['lontane'][1], {g: (s / n, n) for g, (s, n) in acc.items()}


def memoria(righe, rnd):
    ev = eventi_memoria(blocchi(righe))
    d, dett = differenza(ev)
    per = defaultdict(list)
    for x in ev:
        per[x[0]].append(x)
    chiavi = list(per)
    boot = sorted(v for v in (differenza([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])[0] for _ in range(BOOT)) if v is not None)
    return OrderedDict([('differenza', d), ('dettaglio', dett), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])


def eventi_parola(r):
    seq, inizio = [e3b49.I, e3b49.I], []
    for j, w in enumerate(r):
        if j:
            seq.append(e3b49.S)
        inizio.append(len(seq))
        seq += list(w)
    seq += [e3b49.F, e3b49.F]
    out = []
    for j, w in enumerate(r):
        pos = [i for i, s in enumerate(w) if s in TH]
        if len(pos) != 1:
            continue
        i = inizio[j] + pos[0]
        out.append(((seq[i - 2], seq[i - 1], seq[i + 1], seq[i + 2]), w[:pos[0]] + ('*',) + w[pos[0] + 1:], w[pos[0]]))
    return out


def parola(pagine):
    meta = ([], [])
    for k, pars in enumerate(pagine):
        for par in pars:
            for r in par:
                meta[k % 2].extend(eventi_parola(r))
    s1, n1 = e3b49.risparmio(meta[0], meta[1])
    s2, n2 = e3b49.risparmio(meta[1], meta[0])
    return (s1 + s2) / (n1 + n2), n1 + n2


def main():
    rnd = random.Random(3251)
    tt = e381.testi()
    ris = OrderedDict()
    for nome, chiave in TESTI.items():
        righe = [r for r in tt[chiave] if r]
        x = OrderedDict([('righe', len(righe)), ('parole', sum(len(r) for r in righe)), ('memoria', memoria(righe, rnd))])
        if nome == 'Hatton Gospels':
            pagine = [[righe[i:i + BLOCCO]] for i in range(0, len(righe), BLOCCO)]
            vero = parola(pagine)
            tab = e3a71.catena(righe, e3a78.ORDINE)
            cat = [parola(e3a78.riscrivi(pagine, tab, rnd)) for _ in range(5)]
            x['parola'] = OrderedDict([('risparmio', vero[0]), ('occorrenze', vero[1]), ('catene', [c[0] for c in cat]),
                                       ('catena_media', sum(c[0] for c in cat) / 5), ('catena_max', max(c[0] for c in cat))])
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False), flush=True)
    h = ris['Hatton Gospels']
    ic = h['memoria']['IC95']
    es1 = 'memoria corta anche nello scriba anglosassone' if ic[0] > 0 else ('al contrario' if ic[1] < 0 else 'nessuna memoria corta')
    dp = h['parola']['risparmio'] - h['parola']['catena_max']
    es2 = 'scelta legata alla parola' if dp >= 0.01 else ('solo segni vicini' if dp < 0.005 else 'incerto')
    out = OrderedDict([('testi', ris), ('esito_1', es1), ('esito_2', es2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b51_thorn_eth.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b51 — Controllo naturale: þ e ð di uno scriba anglosassone', '', 'Preregistrazione: `preregistrazioni/e3b51.md`.', '',
          '## Memoria corta (senza parole simili)', '', '| testo | parole | vicine 2–3: eccesso (coppie) | lontane 6–10: eccesso (coppie) | differenza (IC 95%) |', '|---|---|---|---|---|']
    for nome, x in ris.items():
        m = x['memoria']
        v, l = m['dettaglio'].get('vicine', (0, 0)), m['dettaglio'].get('lontane', (0, 0))
        md.append('| %s | %d | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) |' % (nome, x['parole'], v[0], v[1], l[0], l[1], m['differenza'], m['IC95'][0], m['IC95'][1]))
    md += ['', 'Voynich (e3b06): +0,031. Esito 1 (Hatton): **%s**.' % es1, '', '## Legame con la parola (Hatton Gospels)', '',
           'Risparmio fuori campione %+.4f bit per occorrenza (%d occorrenze); catena di ordine 2: media %+.4f, massimo %+.4f. Esito 2: **%s**.' % (
               h['parola']['risparmio'], h['parola']['occorrenze'], h['parola']['catena_media'], h['parola']['catena_max'], es2)]
    open(os.path.join(RISULTATI, 'e3b51_thorn_eth.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
