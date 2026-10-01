# -*- coding: utf-8 -*-
"""Esperimento 71: anatomia del bordo di riga (prima e ultima parola).

Distinzione del bordo (JSD primo/ultimo segno contro le parole interne), prova del segno aggiunto
(tolto il primo/ultimo segno, la forma e' attestata a meta' riga?), esclusivita', lunghezze.
Nullo: 200 rimescolamenti delle parole dentro ogni riga.
Preregistrazione: preregistrazioni/e71.md. Scrive risultati/e71_bordo_riga.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
RIMESCOLAMENTI, MIN_PAROLE, SEME = 200, 3, 71
D = misure.divisore(misure.GLIFI_EVA)
CACHE = os.path.join(QUI, '..', 'dati', 'cache', 'timm_schinner')


def lettere(w):
    return list(w)


# ---------- testi come righe: (inizio_paragrafo, [parole]) ----------

def righe_voynich(lingua=None):
    out = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua):
        if r.parole:
            out.append((bool(r.inizio_par), list(r.parole)))
    return out


def righe_file(percorso):
    righe = [l.split() for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    mediana = statistics.median(len(r) for r in righe)
    return [(i == 0 or len(righe[i - 1]) < mediana / 2, r) for i, r in enumerate(righe)]


def a_capo(parole, dividi, larghezze, media_voy):
    """A capo avido sulle larghezze delle righe del Voynich, riscalate sulla lunghezza media."""
    media = sum(len(dividi(w)) for w in parole) / len(parole)
    scala = (media + 1) / (media_voy + 1)
    out, i, k = [], 0, 0
    while i < len(parole):
        larghezza = larghezze[k % len(larghezze)] * scala
        k += 1
        riga, usata = [parole[i]], len(dividi(parole[i]))
        i += 1
        while i < len(parole) and usata + 1 + len(dividi(parole[i])) <= larghezza:
            usata += 1 + len(dividi(parole[i]))
            riga.append(parole[i])
            i += 1
        out.append((len(out) == 0, riga))
    return out


# ---------- misure ----------

def jsd(a, b):
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb:
        return None
    h = 0.0
    for g in set(a) | set(b):
        p, q = a[g] / na, b[g] / nb
        m = (p + q) / 2
        if p:
            h += p / 2 * math.log2(p / m)
        if q:
            h += q / 2 * math.log2(q / m)
    return h


def posizioni(righe, pulita):
    """Parole iniziali (righe non d'inizio paragrafo), finali, interne, e iniziali di paragrafo."""
    ini, fin, mez, par = [], [], [], []
    for inizio, ps in righe:
        if len(ps) < MIN_PAROLE:
            continue
        if pulita(ps[0]):
            (par if inizio else ini).append(ps[0])
        if pulita(ps[-1]):
            fin.append(ps[-1])
        mez.extend(w for w in ps[1:-1] if pulita(w))
    return ini, fin, mez, par


def misura(righe, dividi, pulita):
    ini, fin, mez, par = posizioni(righe, pulita)
    seg = {w: tuple(dividi(w)) for w in set(ini) | set(fin) | set(mez) | set(par)}
    primo = lambda ws: Counter(seg[w][0] for w in ws)
    ultimo = lambda ws: Counter(seg[w][-1] for w in ws)
    conto_mez = Counter(mez)
    attestate = {w for w, n in conto_mez.items() if n >= 2}
    tipi_mez = set(conto_mez)

    def aggiunto(bordo, taglia):
        # quota per lunghezza delle parole interne la cui forma tagliata e' attestata
        per_l = defaultdict(lambda: [0, 0])
        for w in mez:
            s = seg[w]
            if len(s) >= 3:
                per_l[len(s)][0] += ''.join(taglia(s)) in attestate
                per_l[len(s)][1] += 1
        oss = att = 0.0
        for w in bordo:
            s = seg[w]
            if len(s) >= 3 and per_l[len(s)][1]:
                oss += ''.join(taglia(s)) in attestate
                att += per_l[len(s)][0] / per_l[len(s)][1]
        return oss / att if att else None

    lung = lambda ws: sum(len(seg[w]) for w in ws) / len(ws) if ws else None
    return OrderedDict([
        ('jsd_inizio', jsd(primo(ini), primo(mez))),
        ('jsd_fine', jsd(ultimo(fin), ultimo(mez))),
        ('jsd_paragrafo', jsd(primo(par), primo(mez)) if par else None),
        ('aggiunto_inizio', aggiunto(ini, lambda s: s[1:])),
        ('aggiunto_fine', aggiunto(fin, lambda s: s[:-1])),
        ('esclusive_inizio', sum(w not in tipi_mez for w in ini) / len(ini) if ini else None),
        ('esclusive_fine', sum(w not in tipi_mez for w in fin) / len(fin) if fin else None),
        ('lunghezza_inizio', lung(ini)), ('lunghezza_interna', lung(mez)), ('lunghezza_fine', lung(fin)),
        ('lunghezza_paragrafo', lung(par)),
        ('n_inizio', len(ini)), ('n_fine', len(fin)), ('n_interne', len(mez)), ('n_paragrafo', len(par)),
    ])


def arricchiti(righe, dividi, pulita, k=5):
    """I segni piu' arricchiti al bordo rispetto all'interno (rapporto di frequenze, almeno 20 occorrenze)."""
    ini, fin, mez, _ = posizioni(righe, pulita)
    out = {}
    for nome, bordo, pos in (('inizio', ini, 0), ('fine', fin, -1)):
        cb = Counter(dividi(w)[pos] for w in bordo)
        cm = Counter(dividi(w)[pos] for w in mez)
        nb, nm = sum(cb.values()), sum(cm.values())
        r = {g: (cb[g] / nb) / ((cm[g] + 1) / nm) for g in cb if cb[g] >= 20}
        out[nome] = [(g, round(x, 2), cb[g]) for g, x in sorted(r.items(), key=lambda kv: -kv[1])[:k]]
    return out


def una(args):
    nome, righe, quale = args
    dividi = lettere if quale == 'lettere' else D
    pulita = trascrizione.pulita
    reale = misura(righe, dividi, pulita)
    rnd = random.Random(SEME)
    nulli = defaultdict(list)
    for _ in range(RIMESCOLAMENTI):
        mescolate = []
        for inizio, ps in righe:
            ps = ps[:]
            rnd.shuffle(ps)
            mescolate.append((inizio, ps))
        for k, x in misura(mescolate, dividi, pulita).items():
            if x is not None and not k.startswith('n_') and not k.startswith('lunghezza'):
                nulli[k].append(x)
    sintesi = OrderedDict()
    for k, x in reale.items():
        if k in nulli and x is not None and nulli[k]:
            m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
            sintesi[k] = OrderedDict([('reale', x), ('nullo', m), ('rapporto', x / m if m else None),
                                      ('z', (x - m) / s if s else None)])
        else:
            sintesi[k] = x
    sintesi['arricchiti'] = arricchiti(righe, dividi, pulita)
    return nome, sintesi


def main():
    from e36_posizione_pagina import plinio
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    rv = righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    media_voy = sum(len(D(w)) for w in voy) / len(voy)
    latino = [w for _, ps in plinio() for w in ps]
    codificato = generatori.codice_per_rango(latino, voy, generatori.ModelloParole(voy, D), random.Random(SEME))
    naibbe = open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'),
                  encoding='utf-8').read().split()
    testi = OrderedDict()
    testi['Voynich'] = (rv, 'eva')
    testi['Voynich A'] = (righe_voynich('A'), 'eva')
    testi['Voynich B'] = (righe_voynich('B'), 'eva')
    testi['Plinio, a capo'] = (a_capo(latino, lettere, larghezze, media_voy), 'lettere')
    rc = a_capo(codificato, D, larghezze, media_voy)
    testi['Plinio codificato, a capo'] = (rc, 'eva')
    testi['Naibbe, a capo'] = (a_capo(naibbe[:len(voy)], D, larghezze, media_voy), 'eva')
    rnd = random.Random(SEME)
    marcato = [(i, ['s' + ps[0]] + ps[1:] if rnd.random() < 0.5 else ps) for i, ps in rc]
    testi['controllo: codificato + "s" a meta\' delle righe'] = (marcato, 'eva')
    for s in (19, 1, 2):
        testi['Timm e Schinner, seme %d' % s] = (righe_file(os.path.join(CACHE, 'seme_%d' % s, 'generate', 'generated_text.txt')), 'eva')
    testi['+ giunture (e23), seme 19'] = (righe_file(os.path.join(CACHE, 'giunture', 'forza_3_seme_19', 'generate', 'generated_text.txt')), 'eva')
    testi['modello e51, seme 19'] = (righe_file(os.path.join(CACHE, 'recenza_novita', 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt')), 'eva')
    ris = OrderedDict()
    lavori = [(n, r, q) for n, (r, q) in testi.items()]
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, s in pool.imap(una, lavori):
            ris[nome] = s
            f = lambda k: '%.2f(z%+.0f)' % (s[k]['rapporto'], s[k]['z'] or 0) if isinstance(s[k], dict) and s[k]['rapporto'] else '  -  '
            print('%-46s distinz. ini %s fin %s | aggiunto ini %s fin %s | esclus. ini %s fin %s | lungh %.2f/%.2f/%.2f' % (
                nome, f('jsd_inizio'), f('jsd_fine'), f('aggiunto_inizio'), f('aggiunto_fine'),
                f('esclusive_inizio'), f('esclusive_fine'), s['lunghezza_inizio'], s['lunghezza_interna'],
                s['lunghezza_fine']), flush=True)
            print('    arricchiti inizio %s | fine %s' % (s['arricchiti']['inizio'], s['arricchiti']['fine']), flush=True)
    with open(os.path.join(RISULTATI, 'e71_bordo_riga.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e71 — Anatomia del bordo di riga', '',
           'Rapporti con il nullo (parole rimescolate dentro ogni riga, %d volte); z fra parentesi. Righe con almeno %d '
           'parole; iniziali senza le righe d\'inizio paragrafo. "Segno aggiunto": tolto il primo (ultimo) segno, la forma '
           'è attestata a metà riga, rispetto alle parole interne di pari lunghezza. Preregistrazione: '
           '`preregistrazioni/e71.md`.' % (RIMESCOLAMENTI, MIN_PAROLE), '',
           '| testo | distinzione inizio | distinzione fine | segno aggiunto inizio | segno aggiunto fine | '
           'esclusive inizio | esclusive fine | lunghezza ini / int / fin |', '|---|---|---|---|---|---|---|---|']
    g = lambda s, k: ('%.2f (z %.1f)' % (s[k]['rapporto'], s[k]['z'] or 0)) if isinstance(s[k], dict) and s[k]['rapporto'] else '–'
    for nome, s in ris.items():
        out.append('| %s | %s | %s | %s | %s | %s | %s | %.2f / %.2f / %.2f |' % (
            nome, g(s, 'jsd_inizio'), g(s, 'jsd_fine'), g(s, 'aggiunto_inizio'), g(s, 'aggiunto_fine'),
            g(s, 'esclusive_inizio'), g(s, 'esclusive_fine'), s['lunghezza_inizio'], s['lunghezza_interna'],
            s['lunghezza_fine']))
    out += ['', 'Segni più arricchiti al bordo (segno, rapporto di frequenza, occorrenze):', '']
    for nome, s in ris.items():
        out.append('- **%s**: inizio %s; fine %s' % (nome, ', '.join('%s ×%s' % (a, b) for a, b, _ in s['arricchiti']['inizio']),
                                                      ', '.join('%s ×%s' % (a, b) for a, b, _ in s['arricchiti']['fine'])))
    with open(os.path.join(RISULTATI, 'e71_bordo_riga.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
