# -*- coding: utf-8 -*-
"""Esperimento 226: dove nascono le parole nuove? Una parola alla sua prima occorrenza ha un "genitore" (tipo gia' visto
a distanza di edit 1) fra le parole precedenti della stessa pagina piu' spesso che fra le prime parole di altre pagine
precedenti della stessa sezione?

Preregistrazione: preregistrazioni/e226.md. Scrive risultati/e226_nascita_parole.json e .md.
"""
import json, math, os, random, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e99_macer as e99
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
import e162b_messaggio_a_voci as e162b
import e192_generatore_misto as e192

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEME, CONTROLLI, RICAMPIONI, MIN_UNITA = 226, 20, 1000, 3


def voynich():
    """[(sezione, [parole])] per pagina, nell'ordine della ZL."""
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            per.setdefault(r.pagina, [r.sezione, []])[1].extend(ps)
    return [(s, ws) for s, ws in per.values()]


def generatore(seme=1):
    """Generatore e192 (nu 0,4) sulle pagine vere, con le loro sezioni."""
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    sez = {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        sez.setdefault(r.pagina, r.sezione)
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    per = OrderedDict()
    for pag, _, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), seme, None):
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            per.setdefault(pag, [sez.get(pag), []])[1].extend(ps)
    return [(s, ws) for s, ws in per.values()]


def rimescola(unita, rnd):
    """Controllo negativo: parole rimescolate fra le pagine della stessa sezione, lunghezze conservate."""
    per = defaultdict(list)
    for s, ws in unita:
        per[s].extend(ws)
    for s in per:
        rnd.shuffle(per[s])
    pos = defaultdict(int)
    out = []
    for s, ws in unita:
        out.append((s, per[s][pos[s]:pos[s] + len(ws)]))
        pos[s] += len(ws)
    return out


def vicini(u, inventario):
    """Tutte le forme a distanza di edit 1 dalla tupla di unita' u."""
    out = set()
    for i in range(len(u)):
        out.add(u[:i] + u[i + 1:])
        for x in inventario:
            if x != u[i]:
                out.add(u[:i] + (x,) + u[i + 1:])
    for i in range(len(u) + 1):
        for x in inventario:
            out.add(u[:i] + (x,) + u[i:])
    return out


def nascita(unita, dividi, rnd):
    unita = [(s, [tuple(dividi(w)) for w in ws]) for s, ws in unita]
    inventario = sorted({x for _, ws in unita for w in ws for x in w})
    visti = set()
    loc, ctr, qualunque = [], [], []
    for k, (s, ws) in enumerate(unita):
        prima = [j for j in range(k) if unita[j][0] == s] or list(range(k))
        locali = set()
        for t, w in enumerate(ws):
            if w not in visti and k > 0 and len(w) >= 3:
                g = vicini(w, inventario) & visti
                qualunque.append(bool(g))
                loc.append(bool(g & locali))
                n = 0
                for _ in range(CONTROLLI):
                    j = rnd.choice(prima)
                    n += bool(g & set(unita[j][1][:t]))
                ctr.append(n / CONTROLLI)
            visti.add(w)
            locali.add(w)
    loc, ctr = np.array(loc, float), np.array(ctr)
    L = float(loc.mean() / ctr.mean()) if ctr.mean() else None
    bs = []
    for _ in range(RICAMPIONI):
        idx = np.array([rnd.randrange(len(loc)) for _ in range(len(loc))])
        c = ctr[idx].mean()
        if c:
            bs.append(loc[idx].mean() / c)
    parole = [w for _, ws in unita for w in ws]
    xs, ys, tipi = [], [], set()
    for i, w in enumerate(parole, 1):
        tipi.add(w)
        if i % 1000 == 0:
            xs.append(math.log(i))
            ys.append(math.log(len(tipi)))
    return OrderedDict([('unita', len(unita)), ('parole', len(parole)), ('nuove', len(loc)),
                        ('quota_genitore_qualunque', float(np.mean(qualunque))), ('quota_locale', float(loc.mean())),
                        ('quota_controllo', float(ctr.mean())), ('L', L),
                        ('L_basso', float(np.percentile(bs, 2.5))), ('L_alto', float(np.percentile(bs, 97.5))),
                        ('heaps', float(np.polyfit(xs, ys, 1)[0]) if len(xs) > 2 else None)])


def main():
    rnd = random.Random(SEME)
    voy = voynich()
    lettere = lambda w: list(w)
    testi = OrderedDict([
        ('Voynich', (voy, D)),
        ('generatore e192 (controllo positivo)', (generatore(1), D)),
        ('Voynich rimescolato nella sezione (controllo negativo)', (rimescola(voy, random.Random(SEME)), D)),
        ('Macer floridus, capitoli', ([(None, [w for ps in c for w in ps]) for c in e99.capitoli()], lettere)),
        ('Isidoro XVII, paragrafi', ([(None, v) for v in e162b.voci() if len(v) >= MIN_UNITA], lettere)),
    ])
    ris = OrderedDict()
    for nome, (unita, dividi) in testi.items():
        ris[nome] = nascita(unita, dividi, rnd)
        r = ris[nome]
        print('%s: nuove %d, genitore %.2f, locale %.3f, controllo %.3f, L %.2f [%.2f, %.2f], Heaps %.3f' % (
            nome, r['nuove'], r['quota_genitore_qualunque'], r['quota_locale'], r['quota_controllo'], r['L'], r['L_basso'], r['L_alto'],
            r['heaps']), flush=True)
    v, g, n = ris['Voynich'], ris['generatore e192 (controllo positivo)'], ris['Voynich rimescolato nella sezione (controllo negativo)']
    valido = g['L'] >= 2 and g['L_basso'] > 1.5 and 0.8 <= n['L'] <= 1.25
    esito = ('non valido' if not valido else 'nascita locale' if v['L'] >= 2 and v['L_basso'] > 1.5
             else 'nascita non locale' if v['L'] <= 1.3 else 'nascita intermedia')
    troppo = g['L'] >= 2 * v['L'] and g['L_basso'] > v['L_alto']
    ris['esito'] = esito
    ris['generatore_troppo_locale'] = troppo
    json.dump(ris, open(os.path.join(RISULTATI, 'e226_nascita_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e226 — Dove nascono le parole nuove?', '',
          'Parola nuova = prima occorrenza di un tipo (≥ 3 unità); genitore = tipo già visto a distanza di edit 1. L = quota con '
          'un genitore fra le parole precedenti della stessa unità / quota fra le prime parole di %d unità precedenti a caso '
          '(stessa sezione quando c\'è). Intervallo al 95%% con %d ricampionamenti. Preregistrazione: `preregistrazioni/e226.md`.'
          % (CONTROLLI, RICAMPIONI), '',
          '| testo | unità | parole nuove | con un genitore | locale | controllo | L | intervallo | Heaps |',
          '|---|---|---|---|---|---|---|---|---|']
    for nome, r in list(ris.items())[:5]:
        md.append('| %s | %d | %d | %.0f%% | %.1f%% | %.1f%% | %.2f | %.2f–%.2f | %.3f |' % (
            nome, r['unita'], r['nuove'], 100 * r['quota_genitore_qualunque'], 100 * r['quota_locale'], 100 * r['quota_controllo'],
            r['L'], r['L_basso'], r['L_alto'], r['heaps']))
    md += ['', 'Esito: **%s**. Generatore troppo locale rispetto al Voynich: **%s**.' % (esito, 'sì' if troppo else 'no')]
    open(os.path.join(RISULTATI, 'e226_nascita_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, troppo)


if __name__ == '__main__':
    main()
