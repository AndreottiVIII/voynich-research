# -*- coding: utf-8 -*-
"""Esperimento 213: ricottura congiunta (una chiave) con modelli di lingua latini di dominio per sezione (piante,
ricette, astronomia); verifica fuori campione della discriminazione fra sezioni. Voynich ripulito, controllo positivo
(latino di dominio cifrato) e negativo (generatore senza messaggio).

Preregistrazione: preregistrazioni/e213.md. Scrive risultati/e213_decifrazione_di_dominio.json e .md.
"""
import json, math, os, random, statistics, sys, unicodedata
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, ricottura, trascrizione
import e17_ricottura as e17
import e99_macer as e99
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIPARTENZE, PERMUTAZIONI = 213, 4, 1000
DOMINI = OrderedDict([('piante', ('H', 'P')), ('ricette', ('S',)), ('astronomia', ('A', 'C', 'T'))])
LETTERE = set('abcdefghiklmnopqrstuxyz')
LL = lingue.LATIN_LIBRARY
CORPORA = {
    'piante': ['isidore/17.txt', 'columella/columella.arbor.txt'] + ['columella/columella.rr%d.txt' % i for i in (2, 3, 4, 5)] + ['cato/cato.agri.txt'],
    'ricette': ['apicius/apicius%d.txt' % i for i in range(1, 6)] + ['columella/columella.rr12.txt'],
    'astronomia': ['manilius%d.txt' % i for i in range(1, 6)] + ['hyginus/hyginus%d.txt' % i for i in range(1, 7)] + ['germanicus.txt', 'isidore/3.txt', 'pliny.nh2.txt'],
}


def lettere_di(s):
    s = unicodedata.normalize('NFD', s.lower().replace('j', 'i').replace('v', 'u').replace('w', 'u'))
    return ''.join(c for c in s if c in LETTERE)


def corpus(dominio):
    parti = []
    for rel in CORPORA[dominio]:
        p = os.path.join(LL, rel)
        if os.path.exists(p):
            righe = [r for r in open(p, encoding='utf-8', errors='ignore') if 'Latin Library' not in r and 'Classics Page' not in r]
            parti += lingue.normalizza(' '.join(righe)).split()
    if dominio == 'piante':
        parti += [w for c in e99.capitoli() for ps in c for w in ps]
    return [x for x in (lettere_di(w) for w in parti) if x]


def modelli():
    bibbia = [x for x in (lettere_di(w) for w in lingue.parole('Latin')[:250000]) if x]
    mod, controllo = OrderedDict(), OrderedDict()
    for d in DOMINI:
        c = corpus(d)
        k = int(len(c) * 0.8)
        mod[d] = ricottura.ModelloLettere(''.join(c[:k] * 3 + bibbia) + ''.join(sorted(LETTERE)), n=5)
        controllo[d] = c[k:]
    return mod, controllo


def pagine_voynich():
    """{pagina: (sezione, [righe di parole ripulite con None per le illeggibili])} nell'ordine della ZL."""
    per, sez = OrderedDict(), {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            per.setdefault(r.pagina, []).append((bool(r.inizio_par), list(r.parole)))
            sez[r.pagina] = r.sezione
    pul = e160.ripulisci(list(per.values()))
    return OrderedDict((p, (sez[p], [[w if trascrizione.pulita(w) else None for w in ps] for _, ps in righe])) for p, righe in zip(per, pul))


def dominio_di(sezione):
    for d, ss in DOMINI.items():
        if sezione in ss:
            return d
    return None


def ricottura_congiunta(gruppi, rnd, passi):
    """gruppi: [(Grammi, ModelloLettere)] con gli stessi simboli e le stesse lettere; una chiave."""
    G0, M0 = gruppi[0]
    S, A = len(G0.simboli), M0.A
    chiave = np.array([rnd.randrange(A) for _ in range(S)], dtype=np.int64)
    freq = sum(np.array([g.frequenza[s] for s in range(S)], dtype=np.float64) for g, _ in gruppi)
    totale = sum(g.totale for g, _ in gruppi)
    scala = totale / freq.sum()
    conti = np.bincount(chiave, weights=freq, minlength=A).astype(np.float64)
    contr = [m.logp[ricottura._codici(chiave, g.G, A)] * g.c for g, m in gruppi]
    lm = sum(c.sum() for c in contr)
    ent = scala * ricottura._entropia_conti(conti)
    attuale = lm + ent
    migliore, chiave_m = attuale, chiave.copy()
    cumul = np.cumsum(np.sqrt(freq + 1) / np.sqrt(freq + 1).sum())
    fattore = (0.002 / 0.5) ** (1.0 / passi)
    t = 0.5 * totale
    xl = lambda x: x * math.log(x) if x > 0 else 0.0
    for _ in range(passi):
        s = min(int(np.searchsorted(cumul, rnd.random())), S - 1)
        nuova = rnd.randrange(A - 1)
        vecchia = int(chiave[s])
        if nuova >= vecchia:
            nuova += 1
        chiave[s] = nuova
        nuovi, d_lm = [], 0.0
        for (g, m), c in zip(gruppi, contr):
            idx = g.contiene[s]
            x = m.logp[ricottura._codici(chiave, g.G[idx], A)] * g.c[idx]
            d_lm += x.sum() - c[idx].sum()
            nuovi.append((idx, x))
        f = freq[s]
        d_ent = scala * (xl(conti[vecchia]) + xl(conti[nuova]) - xl(conti[vecchia] - f) - xl(conti[nuova] + f))
        delta = d_lm + d_ent
        if delta >= 0 or rnd.random() < math.exp(delta / t):
            for (idx, x), c in zip(nuovi, contr):
                c[idx] = x
            conti[vecchia] -= f
            conti[nuova] += f
            attuale += delta
            if attuale > migliore:
                migliore, chiave_m = attuale, chiave.copy()
        else:
            chiave[s] = vecchia
        t *= fattore
    return migliore / totale, chiave_m


def decifra(righe, chiave, indice, lettere):
    return [''.join(lettere[chiave[indice[u]]] for u in r if u in indice) for r in righe]


def prova(nome, pagine, mod, rnd):
    """pagine: [(dominio, righe di unita')], con la meta' di stima e quella di verifica alternate."""
    stima = defaultdict(list)
    for i, (d, rr) in enumerate(pagine):
        if i % 2 == 0:
            stima[d] += rr
    simboli = sorted({u for _, rr in pagine for r in rr for u in r}, key=str)
    gruppi = []
    for d in DOMINI:
        g = ricottura.Grammi(stima[d] + [simboli], 5)       # la riga finta garantisce tutti i simboli in ogni gruppo
        gruppi.append((g, mod[d]))
    lettere = mod['piante'].lettere
    assert all(m.lettere == lettere for m in mod.values())
    passi = 1500 * len(simboli)
    esiti = [ricottura_congiunta(gruppi, rnd, passi) for _ in range(RIPARTENZE)]
    obiettivo, chiave = max(esiti, key=lambda e: e[0])
    indice = gruppi[0][0].indice
    verifica = [(d, decifra(rr, chiave, indice, lettere)) for i, (d, rr) in enumerate(pagine) if i % 2 == 1]
    punti = [(d, {dd: ricottura.punteggio_righe([x for x in t if len(x) >= 5], m) for dd, m in mod.items()}, sum(map(len, t))) for d, t in verifica]
    punti = [(d, s, n) for d, s, n in punti if n >= 50 and all(not math.isnan(v) for v in s.values())]

    def delta(etichette):
        num = den = 0.0
        for (d0, s, n), d in zip(punti, etichette):
            altri = [s[x] for x in DOMINI if x != d]
            num += n * (s[d] - statistics.mean(altri))
            den += n
        return num / den
    et = [d for d, _, _ in punti]
    vero = delta(et)
    nulli = []
    for _ in range(PERMUTAZIONI):
        x = et[:]
        rnd.shuffle(x)
        nulli.append(delta(x))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    esempi = OrderedDict((d, [t for dd, t in verifica if dd == d][0][:2]) for d in DOMINI if any(dd == d for dd, _ in verifica))
    r = OrderedDict([('simboli', len(simboli)), ('obiettivo', obiettivo), ('pagine_verifica', len(punti)), ('delta', vero), ('nullo', m),
                     ('z', (vero - m) / sd if sd else None), ('chiave', {str(s): lettere[chiave[indice[s]]] for s in simboli}), ('esempi', esempi)])
    print('%-28s simboli %d | obiettivo %.3f | Δ %.4f (nullo %.4f) z %.1f | esempi %s' % (nome, len(simboli), obiettivo, vero, m, r['z'] or 0,
          {d: [x[:50] for x in v] for d, v in esempi.items()}), flush=True)
    return r


def a_unita(per_pag):
    glifi = misure.divisore(misure.GLIFI_EVA)
    tutte = [r for _, rr in per_pag for r in rr]
    unita = e17.in_unita(tutte, glifi)
    ammesse = {u for r in unita for u in r}
    return [(d, e17.in_unita(rr, glifi, ammesse=ammesse)) for d, rr in per_pag]


def controllo_positivo(pagine_v, controllo, rnd, simboli):
    """Latino di dominio (parte non usata per i modelli) diviso in pagine con le lunghezze e le sezioni del Voynich,
    cifrato con una chiave omofonica di `simboli` simboli."""
    cur = {d: 0 for d in DOMINI}
    righe_parole, pos = [], []
    for d, rr in pagine_v:
        L = sum(map(len, rr))
        ps, n = [], 0
        while n < L:
            w = controllo[d][cur[d] % len(controllo[d])]
            cur[d] += 1
            ps.append(w)
            n += len(w)
        a = len(righe_parole)
        righe_parole += e17.in_righe(ps)
        pos.append((d, a, len(righe_parole)))
    cif, _ = e17.cifra_abbinata(righe_parole, simboli, rnd)
    return [(d, cif[a:b]) for d, a, b in pos]


def una(args):
    nome, pagine, mod = args
    return nome, prova(nome, pagine, mod, random.Random(SEME))


def main():
    rnd = random.Random(SEME)
    mod, controllo = modelli()
    pv = pagine_voynich()
    voy = a_unita([(dominio_di(s), rr) for p, (s, rr) in pv.items() if dominio_di(s)])
    simboli = len({u for _, rr in voy for r in rr for u in r})
    voynich_parole = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voynich_parole), 0.4
    e153.variante = e192.variante
    gen = e162.genera(P, starts, q, L, generatori.Modifiche(voynich_parole, e162.D), 1, None)
    per_g = OrderedDict()
    for pag, ini, ps in gen:
        per_g.setdefault(pag, []).append((ini, ps))
    pul_g = e160.ripulisci(list(per_g.values()))
    neg = a_unita([(dominio_di(pv[p][0]), [[w if trascrizione.pulita(w) else None for w in ps] for _, ps in rr])
                   for p, rr in zip(per_g, pul_g) if p in pv and dominio_di(pv[p][0])])
    pos = controllo_positivo(voy, controllo, rnd, simboli)
    lavori = [('controllo positivo (latino)', pos, mod), ('Voynich ripulito', voy, mod), ('controllo negativo (generatore)', neg, mod)]
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, lavori):
            ris[nome] = r
    zp, zv, zn = (ris[k]['z'] or 0 for k in ('controllo positivo (latino)', 'Voynich ripulito', 'controllo negativo (generatore)'))
    valido = zp > 4
    esito = 'test non valido' if not valido else ('lettura di dominio, da esaminare' if zv > 4 and zv - zn >= 3 else 'nessuna lettura')
    ris['valido'], ris['esito'] = valido, esito
    print('valido %s | %s' % (valido, esito))
    json.dump(ris, open(os.path.join(RISULTATI, 'e213_decifrazione_di_dominio.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = ['# e213 — Decifrazione guidata dal contenuto atteso', '', 'Una chiave, modelli latini per sezione (piante, ricette, astronomia); discriminazione fuori campione Δ e z '
           'contro il rimescolamento delle sezioni. Preregistrazione: `preregistrazioni/e213.md`.', '', '| testo | simboli | obiettivo | Δ | z |', '|---|---|---|---|---|']
    for k in ('controllo positivo (latino)', 'Voynich ripulito', 'controllo negativo (generatore)'):
        r = ris[k]
        out.append('| %s | %d | %.3f | %.4f | %.1f |' % (k, r['simboli'], r['obiettivo'], r['delta'], r['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito), '', 'Esempi decifrati del Voynich (descrittivi):', '']
    for d, v in ris['Voynich ripulito']['esempi'].items():
        out.append('- %s: %s' % (d, ' / '.join(x[:80] for x in v)))
    out += ['', 'Chiave del Voynich: ' + ', '.join('%s→%s' % kv for kv in ris['Voynich ripulito']['chiave'].items())]
    open(os.path.join(RISULTATI, 'e213_decifrazione_di_dominio.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
