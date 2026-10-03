# -*- coding: utf-8 -*-
"""Esperimento 251 (passo 2 del piano 18/18): il generatore dell'e243 con un lessico di sezione (le classi A e N pescano,
con probabilita' gamma, dalle parole gia' generate nelle pagine precedenti della stessa sezione). Il modulo contiene anche
il gancio degli interruttori di riga usato dal passo 3 (e252). Con i ganci spenti il testo e' identico a quello dell'e243.

Preregistrazione: preregistrazioni/e251.md. Scrive risultati/e251_lessico_sezione.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e206_segni_facoltativi as e206
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e238_profilo_riuso as e238
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241
import e243_riuso_esplicito as e243

RISULTATI = os.path.join(QUI, '..', 'risultati')
GAMMA, SEME_RICERCA, SEMI_VERIFICA = (0.3, 0.6), 1, (7, 8, 9)
D = e237.D


# ------------------------------------------------------------------ interruttori di riga (usati dall'e252)

def interruttori_voynich(classi):
    """Per ogni classe: tasso di forme lunghe nel Voynich e mappe lunga <-> corta fra parole attestate (>= 3 volte)."""
    freq = Counter(w for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) for w in r.parole if trascrizione.pulita(w))
    attestate = {w for w, c in freq.items() if c >= e206.MIN_TIPO}
    lunga, corte = defaultdict(dict), defaultdict(lambda: defaultdict(list))
    for w in sorted(attestate):
        u = D(w)
        for i, g in enumerate(u):
            corta = ''.join(u[:i] + u[i + 1:])
            if corta and corta in attestate:
                pos = 'iniziale' if i == 0 else ('finale' if i == len(u) - 1 else 'interna')
                nome = '%s %s' % (g, pos)
                if nome in classi:
                    lunga[w][nome] = corta
                    corte[corta][nome].append(w)
    tassi = {}
    for c in classi:
        n1 = sum(freq[w] for w in lunga if c in lunga[w])
        n0 = sum(freq[w] for w in corte if c in corte[w])
        tassi[c] = n1 / (n1 + n0) if n1 + n0 else 0.5
    corte = {w: {c: sorted(v, key=lambda x: -freq[x])[0] for c, v in d.items()} for w, d in corte.items()}
    return tassi, dict(lunga), corte


def applica_interruttori(riga, stato, interruttori, rnd):
    tassi, lunga, corte = interruttori
    out = []
    for w in riga:
        cl = sorted(set(lunga.get(w, {})) | set(corte.get(w, {})))
        if not cl:
            out.append(w)
            continue
        c = rnd.choice(cl)
        b = min(max(tassi[c], 1e-3), 1 - 1e-3)
        p = 1 / (1 + math.exp(-(math.log(b / (1 - b)) + stato[c])))
        vuole_lunga = rnd.random() < p
        if vuole_lunga and c in corte.get(w, {}):
            out.append(corte[w][c])
        elif not vuole_lunga and c in lunga.get(w, {}):
            out.append(lunga[w][c])
        else:
            out.append(w)
    return out


# ------------------------------------------------------------------ generatore

def genera(c, quote, dist, seme, gamma=0.0, interruttori=None):
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    frequenti = {w for w, _ in Counter(c['voy']).most_common(200)}
    classi, pesi_classi = list(e243.CLASSI), [quote[x] for x in e243.CLASSI]
    sez = e230.sezioni()
    lessico = defaultdict(list)
    h = {f: 0.0 for f in e145.SCELTE}
    stato = {k: 0.0 for k in (interruttori[0] if interruttori else {})}
    righe = []
    for pag, d in c['P'].items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        gt, gp = e232.globali(c, lingua, 1.0)
        ft, fp = e238.frequenti(c, lingua)
        lex = lessico[sez.get(pag)]
        nuove_pag = []
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        if interruttori:
            for k in stato:
                stato[k] = (e152.RHO / 2) * stato[k] + rnd.gauss(0, e152.SIGMA)
        prima_sopra, ultime = None, []
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            if interruttori:
                for k in stato:
                    stato[k] = e152.RHO * stato[k] + rnd.gauss(0, e152.SIGMA)
            n = len(ps)
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or Dv(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            while len(riga) < n:
                pos = len(riga)
                x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                cand = []
                for _ in range(e243.K):
                    cl = rnd.choices(classi, pesi_classi)[0]
                    w = None
                    if cl in ('R', 'V'):
                        s = e243.fonte(rnd, dist[cl], riga, ultime, x0, Dv)
                        if s is not None:
                            w = s if cl == 'R' else e234.forza_variante(s, mod, rnd, e243.NU, att, Dv)
                        else:
                            cl = 'F'
                    if cl == 'F':
                        w = rnd.choices(ft, fp)[0]
                    elif cl in ('A', 'N'):
                        if gamma and lex and rnd.random() < gamma:
                            base = rnd.choice(lex)
                        else:
                            base = rnd.choices(gt, gp)[0]
                        w = base if cl == 'A' else e234.forza_variante(base, mod, rnd, e243.NU, att, Dv)
                    cand.append(w)
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** e243.LAM) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** e243.ETA
                    if x not in frequenti:
                        p *= (len(Dv(x)) / media) ** e243.ELL_R
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if interruttori:
                riga = applica_interruttori(riga, stato, interruttori, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            ultime = (ultime + [[w for w in riga if trascrizione.pulita(w)]])[-e243.D_MAX:]
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w)]
        lex.extend(nuove_pag)
    return righe


def tara(c, dist, freq, bersaglio, **ganci):
    quote = OrderedDict((x, bersaglio[x]) for x in e243.CLASSI)
    storia = []
    for it in range(e243.ITERAZIONI):
        gp = e232.pagine_di(e236.dopo(genera(c, quote, dist, SEME_RICERCA, **ganci), freq, 0))
        prof = e237.profilo(gp)
        storia.append(OrderedDict([('quote', dict(quote)), ('profilo', {x: prof[x] for x in e243.CLASSI})]))
        if it < e243.ITERAZIONI - 1:
            nuove = {x: quote[x] * bersaglio[x] / max(prof[x], 1e-3) for x in e243.CLASSI}
            s = sum(nuove.values())
            quote = OrderedDict((x, nuove[x] / s) for x in e243.CLASSI)
    return quote, storia


def verifica(c, c2, vpag, rif, freq, quote, dist, **ganci):
    out = []
    for s in SEMI_VERIFICA:
        rr = e236.dopo(genera(c2, quote, dist, s, **ganci), freq, 100 + s)
        gp = e232.pagine_di(rr)
        r = e231.confronto(vpag, gp, rif)
        r.update(e234.descrittive(gp))
        r['profilo'] = e237.profilo(gp)
        r['pagella_e224'] = e236.pagella(c, rr)
        r['R_parole_rare'] = e243.R_rare(rr)
        r['righe'] = rr
        out.append(r)
        print('seme %d: AUC %.3f | pagella %d/18 riga %s mancano %s | R rare %.1f' % (
            s, r['AUC'], r['pagella_e224']['pagella'], r['pagella_e224']['riga'], r['pagella_e224']['mancano'], r['R_parole_rare']), flush=True)
    return out


def contesto():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    return c, c2, freq, vpag, rif, pv


def main():
    c, c2, freq, vpag, rif, pv = contesto()
    bersaglio = e237.profilo(pv)
    dist = e243.distanze_voynich(pv)
    q243 = json.load(open(os.path.join(RISULTATI, 'e243_riuso_esplicito.json'), encoding='utf-8'))['quote_finali']
    identico = genera(c2, q243, dist, SEME_RICERCA) == e243.genera(c2, q243, dist, SEME_RICERCA)
    print("identico all'e243 con gamma 0: %s" % identico, flush=True)
    scelta = OrderedDict()
    for g in GAMMA:
        quote, storia = tara(c2, dist, freq, bersaglio, gamma=g)
        rr = e236.dopo(genera(c2, quote, dist, SEME_RICERCA, gamma=g), freq, 0)
        scelta['gamma %.1f' % g] = OrderedDict([('quote', quote), ('R_parole_rare', e243.R_rare(rr)), ('pagella_e224', e236.pagella(c, rr))])
        print('gamma %.1f (seme 1): R rare %.1f, pagella %d/18' % (g, scelta['gamma %.1f' % g]['R_parole_rare'], scelta['gamma %.1f' % g]['pagella_e224']['pagella']), flush=True)
    # scelta: fra i gamma con pagella (seme 1) non inferiore di oltre 1 alla migliore, quello con R rare piu' vicino a 1,96 (scala log)
    massimo = max(scelta['gamma %.1f' % g]['pagella_e224']['pagella'] for g in GAMMA)
    ammessi = [g for g in GAMMA if scelta['gamma %.1f' % g]['pagella_e224']['pagella'] >= massimo - 1]
    migliore = min(ammessi, key=lambda g: (abs(math.log(scelta['gamma %.1f' % g]['R_parole_rare'] / 1.96)), g))
    quote = scelta['gamma %.1f' % migliore]['quote']
    ver = verifica(c, c2, vpag, rif, freq, quote, dist, gamma=migliore)
    rif243 = json.load(open(os.path.join(RISULTATI, 'e243_riuso_esplicito.json'), encoding='utf-8'))
    pag = statistics.mean(x['pagella_e224']['pagella'] for x in ver)
    R = statistics.mean(x['R_parole_rare'] for x in ver)
    auc = statistics.mean(x['AUC'] for x in ver)
    esito = ('non valido' if not identico else 'passo superato' if R <= 5 and pag >= rif243['pagella_media'] else 'non superato')
    for x in ver:
        x.pop('righe', None)
    ris = OrderedDict([('validita_identico_e243', identico), ('scelta_seme_1', scelta), ('gamma', migliore), ('verifica', ver), ('pagella_media', pag),
                       ('R_parole_rare_media', R), ('AUC_media', auc), ('pagella_e243', rif243['pagella_media']), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e251_lessico_sezione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e251 — Passo 2 del piano 18/18: lessico che circola fra le pagine', '',
          "Generatore dell'e243 con le classi A e N che pescano, con probabilità γ, dalle parole già generate nelle pagine precedenti della stessa "
          'sezione. γ scelto sul seme 1 fra %s: %.1f. Validità (γ 0 = e243): %s. Preregistrazione: `preregistrazioni/e251.md`.' % (GAMMA, migliore, 'sì' if identico else 'NO'), '',
          '| seme | AUC | pagella | riga | mancano | R parole rare |', '|---|---|---|---|---|---|']
    for s, x in zip(SEMI_VERIFICA, ver):
        md.append('| %d | %.3f | %d/18 | %s | %s | %.1f |' % (s, x['AUC'], x['pagella_e224']['pagella'], 'sì' if x['pagella_e224']['riga'] else 'no',
                                                         ', '.join(x['pagella_e224']['mancano']) or '—', x['R_parole_rare']))
    md += ['', 'Medie: pagella %.1f/18 (e243: %.1f), R parole rare %.1f (Voynich 1,96), AUC %.3f.' % (pag, rif243['pagella_media'], R, auc), '',
           'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e251_lessico_sezione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
