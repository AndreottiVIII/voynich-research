# -*- coding: utf-8 -*-
"""Esperimento 37: in quale posizione della parola sta l'informazione sulla sezione illustrata?

Se il Voynich fosse una lingua filosofica a prefisso di classe, pagine con soggetti
diversi (piante, stelle, figure nelle vasche, recipienti, ricette) userebbero classi
diverse, e la differenza starebbe nel primo segno; nelle etichette, che sono nomi,
ancora di piu'. Il rimescolamento sposta pagine intere fra le sezioni della stessa
lingua di Currier (per le etichette: etichette fra le sezioni).

Scelta non fissata dalla preregistrazione, dichiarata prima dell'esecuzione (QUADERNO,
30/09/2026): pagine con almeno 10 parole utili (in e36 erano 40).
Preregistrazione: preregistrazioni/e36-e38.md. Non serve Java.
Scrive risultati/e37_posizione_sezione.json e .md.
"""
import json, os, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import posizioni, trascrizione
from posizioni import Blocco
import e36_posizione_pagina as e36

RISULTATI = os.path.join(QUI, '..', 'risultati')
PAGINA_MIN = 10
DIVIDI = e36.DIVIDI
SOLO_ESTREMI = {'primo': 0, 'ultimo': -1}


def pagine_voynich():
    per_pagina, meta = {}, {}
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.inizio_par:
            continue
        per_pagina.setdefault(r.pagina, []).append([p for p in r.parole if trascrizione.pulita(p)])
        meta[r.pagina] = (r.sezione, r.lingua, r.quire)
    out = []
    for pag, righe in per_pagina.items():
        utili = [DIVIDI(w) for w in posizioni.righe_utili(righe)]
        if sum(1 for u in utili if len(u) >= 4) < PAGINA_MIN:
            continue
        sezione, lingua, quire = meta[pag]
        out.append(Blocco(sezione, lingua, quire, utili))
    return out


def etichette_voynich():
    out = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.ETICHETTA:
            continue
        for w in r.parole:
            if trascrizione.pulita(w):
                out.append(Blocco(r.sezione, 0, r.quire, [DIVIDI(w)]))
    return out


def pagine_controllo(parole_per_libro, codifica):
    """Una pagina = un blocco; gruppo = libro di Plinio."""
    out, n = [], 0
    for libro, parole in parole_per_libro:
        for righe in e36.pagine_da_parole(codifica(parole)):
            out.append(Blocco(libro, 0, n % 10, [DIVIDI(w) for w in posizioni.righe_utili(righe)]))
            n += 1
    return out


def misura(nome, blocchi, ris, **kw):
    p = posizioni.profilo(blocchi, **kw)
    p['stabilita'] = posizioni.stabilita(blocchi, **kw)
    ris[nome] = p
    q = p['posizioni']
    print('%-46s R %6s  %s  z primo %.1f  stab. %s-%s' % (
        nome, e36.fmt(p['R']), ' '.join('%s %.4f' % (k[:3], v['quota']) for k, v in q.items()),
        q['primo']['z'], e36.fmt(p['stabilita']['min']), e36.fmt(p['stabilita']['max'])), flush=True)


def main():
    ris = {}
    misura('Voynich ZL, paragrafi (sezione | lingua)', pagine_voynich(), ris)
    misura('Voynich ZL, etichette (sezione)', etichette_voynich(), ris,
           posizioni=SOLO_ESTREMI, lung_min=3)
    libri = e36.plinio()
    tutte = [w for _, ps in libri for w in ps]
    categorie = e36.categorie_semantiche(tutte)
    codici_sem = dict(zip(tutte, e36.codice_semantico(tutte, categorie)))
    codici_cas = dict(zip(tutte, e36.codice_casuale(tutte)))
    misura('controllo positivo: prefisso semantico, gruppo = libro',
           pagine_controllo(libri, lambda ps: [codici_sem[w] for w in ps]), ris)
    misura('controllo di forma: codice casuale, gruppo = libro',
           pagine_controllo(libri, lambda ps: [codici_cas[w] for w in ps]), ris)
    with open(os.path.join(RISULTATI, 'e37_posizione_sezione.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    righe = ['# e37 — In quale posizione della parola sta l\'informazione sulla sezione', '',
             'Paragrafi: una pagina è un blocco, e i rimescolamenti spostano pagine intere fra le sezioni '
             'della stessa lingua di Currier. Etichette (almeno 3 segni): solo primo e ultimo segno, '
             'rimescolate fra le sezioni. Controlli: Plinio, libri 20–27, gruppo = libro. '
             'Preregistrazione: `preregistrazioni/e36-e38.md`.', '',
             '| testo | parole | gruppi | primo | secondo | penultimo | ultimo | z primo | R | stabilità di R |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for nome, p in ris.items():
        q = p['posizioni']
        cella = lambda k: '%.4f' % q[k]['quota'] if k in q else '—'
        righe.append('| %s | %d | %d | %s | %s | %s | %s | %.1f | %s | %s–%s |' % (
            nome, p['parole'], p['gruppi'], cella('primo'), cella('secondo'), cella('penultimo'),
            cella('ultimo'), q['primo']['z'], e36.fmt(p['R']),
            e36.fmt(p['stabilita']['min']), e36.fmt(p['stabilita']['max'])))
    with open(os.path.join(RISULTATI, 'e37_posizione_sezione.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


def contributi(blocchi, pos, lung_min):
    """Analisi secondaria: quanto ciascun segno in posizione pos contribuisce all'informazione
    mutua gruppo/segno, dentro ciascuno strato: p(g) * KL(p(sezione|g) || p(sezione))."""
    import math
    from collections import Counter
    per_strato = {}
    for b in blocchi:
        for w in b.parole:
            if len(w) >= lung_min:
                per_strato.setdefault(b.strato, []).append((b.gruppo, w[pos]))
    out = {}
    for strato, coppie in per_strato.items():
        n = len(coppie)
        pg, ps, pj = Counter(g for _, g in coppie), Counter(s for s, _ in coppie), Counter(coppie)
        contrib = {}
        for g, cg in pg.items():
            kl = sum(c / cg * math.log2((c / cg) / (ps[s] / n)) for (s, gg), c in pj.items() if gg == g)
            sopra = max(ps, key=lambda s: pj[(s, g)] / cg - ps[s] / n)
            contrib[g] = {'contributo': cg / n * kl, 'frequenza': cg / n, 'sezione_in_eccesso': sopra,
                          'quota_in_quella_sezione': pj[(sopra, g)] / cg, 'quota_attesa': ps[sopra] / n}
        tot = sum(v['contributo'] for v in contrib.values())
        for v in contrib.values():
            v['frazione'] = v['contributo'] / tot if tot else 0
        out[str(strato)] = {'parole': n, 'sezioni': dict(ps), 'informazione': tot,
                            'segni': dict(sorted(contrib.items(), key=lambda kv: -kv[1]['contributo']))}
    return out


def dettaglio():
    """Analisi secondaria (non preregistrata per e37; per e36 lo era): quali segni portano
    l'informazione sulla sezione al primo segno, nei paragrafi e nelle etichette."""
    ris = {'paragrafi_primo': contributi(pagine_voynich(), 0, 4),
           'etichette_primo': contributi(etichette_voynich(), 0, 3)}
    with open(os.path.join(RISULTATI, 'e37_posizione_sezione_dettaglio.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ["# e37, analisi secondaria: quali segni portano l'informazione sulla sezione", '',
             "Contributo di ciascun segno iniziale all'informazione mutua sezione/primo segno, dentro "
             'ciascuna lingua di Currier (paragrafi) o su tutte le etichette. Non corretto per il caso: '
             "serve a vedere da dove viene l'informazione, non quanta ce n'è.", '']
    for nome, per in ris.items():
        for strato, d in per.items():
            righe += ['## %s, strato %s (%d parole; sezioni: %s)' % (
                nome, strato, d['parole'], ', '.join('%s %d' % kv for kv in sorted(d['sezioni'].items(), key=str))), '',
                "| segno | frequenza | frazione dell'informazione | sezione in eccesso | quota lì | quota attesa |",
                '|---|---|---|---|---|---|']
            for g, v in list(d['segni'].items())[:8]:
                righe.append('| %s | %.3f | %.2f | %s | %.2f | %.2f |' % (
                    g, v['frequenza'], v['frazione'], v['sezione_in_eccesso'],
                    v['quota_in_quella_sezione'], v['quota_attesa']))
            righe.append('')
    with open(os.path.join(RISULTATI, 'e37_posizione_sezione_dettaglio.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    print('\n'.join(righe))


if __name__ == '__main__':
    if '--dettaglio' in sys.argv:
        dettaglio()
    else:
        main()
