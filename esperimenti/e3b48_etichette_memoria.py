# -*- coding: utf-8 -*-
"""Esperimento e3b48: accordo delle scelte di grafia fra etichette consecutive contro etichette lontane della stessa
pagina, togliendo le coppie di parole simili (copia).

Preregistrazione: preregistrazioni/e3b48.md. Scrive risultati/e3b48_etichette_memoria.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import trascrizione
import e3a86_ripetizioni_riga as e3a86
import e3b20_memoria_segni as e3b20

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 2000
MIN_ETICHETTE = 6
MIN_COPPIE = 200
LONTANE = range(4, 11)


def simili(a, b):
    x, y = tuple(D(a)), tuple(D(b))
    return x == y or e3a86.una_modifica(x, y)


def eventi(pagine, togli_simili):
    """[(pagina, 'consecutive'|'lontane', accordo − atteso)]."""
    out = []
    for pid, ee in enumerate(pagine):
        for c, f in e3b20.CLASSI.items():
            v = [f(w) for w in ee]
            T = sum(1 for x in v if x is not None)
            U = sum(1 for x in v if x == 1)
            for i in range(len(ee)):
                if v[i] is None:
                    continue
                for j in range(i + 1, min(len(ee), i + max(LONTANE) + 1)):
                    d = j - i
                    if v[j] is None or not (d == 1 or d in LONTANE):
                        continue
                    if togli_simili and simili(ee[i], ee[j]):
                        continue
                    t, u = T - 2, U - v[i] - v[j]
                    if t < 3:
                        continue
                    p = u / t
                    out.append((pid, 'consecutive' if d == 1 else 'lontane', int(v[i] == v[j]) - (p * p + (1 - p) * (1 - p))))
    return out


def differenza(ev):
    acc = defaultdict(lambda: [0.0, 0])
    for _, g, x in ev:
        acc[g][0] += x
        acc[g][1] += 1
    if not acc['consecutive'][1] or not acc['lontane'][1]:
        return None, {}
    return acc['consecutive'][0] / acc['consecutive'][1] - acc['lontane'][0] / acc['lontane'][1], {g: (s / n, n) for g, (s, n) in acc.items()}


def stima(ev, rnd):
    d, dett = differenza(ev)
    per = defaultdict(list)
    for x in ev:
        per[x[0]].append(x)
    chiavi = list(per)
    boot = sorted(v for v in (differenza([x for k in (rnd.choice(chiavi) for _ in chiavi) for x in per[k]])[0] for _ in range(BOOT)) if v is not None)
    return OrderedDict([('differenza', d), ('dettaglio', dett), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]])])


def main():
    rnd = random.Random(3248)
    per_pag = OrderedDict()
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.ETICHETTA:
            continue
        ws = [w for w in r.parole if trascrizione.pulita(w) and tuple(D(w))]
        if ws:
            per_pag.setdefault(r.pagina, []).append(ws[0])
    pagine = [v for v in per_pag.values() if len(v) >= MIN_ETICHETTE]
    senza = stima(eventi(pagine, True), rnd)
    con = stima(eventi(pagine, False), rnd)
    n_cons = senza['dettaglio'].get('consecutive', (0, 0))[1]
    ic = senza['IC95']
    if n_cons < MIN_COPPIE:
        esito = 'dati insufficienti'
    elif ic[0] > 0:
        esito = "la memoria passa da un'etichetta alla successiva"
    elif ic[1] < 0:
        esito = 'al contrario'
    else:
        esito = 'fra etichette la memoria si azzera'
    out = OrderedDict([('pagine', len(pagine)), ('etichette', sum(len(v) for v in pagine)), ('senza_simili', senza), ('con_simili', con), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b48_etichette_memoria.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b48 — Le scelte di grafia passano da un\'etichetta alla successiva?', '', 'Preregistrazione: `preregistrazioni/e3b48.md`. Pagine con almeno %d etichette: %d (%d etichette).' % (MIN_ETICHETTE, len(pagine), out['etichette']), '',
          '| coppie | consecutive: eccesso (coppie) | lontane 4–10: eccesso (coppie) | differenza (IC 95%) |', '|---|---|---|---|']
    for nome, x in (('senza parole simili', senza), ('con le parole simili (descrittivo)', con)):
        c, l = x['dettaglio'].get('consecutive', (0, 0)), x['dettaglio'].get('lontane', (0, 0))
        md.append('| %s | %+.4f (%d) | %+.4f (%d) | %+.4f (%+.4f – %+.4f) |' % (nome, c[0], c[1], l[0], l[1], x['differenza'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b48_etichette_memoria.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
