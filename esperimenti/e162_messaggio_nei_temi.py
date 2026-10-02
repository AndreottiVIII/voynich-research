# -*- coding: utf-8 -*-
"""Esperimento 162: generatore e153 con i temi di riga presi da un testo latino codificato parola per parola. Le
proprieta' di riga restano? I test di struttura (e160) vedono il messaggio?

Preregistrazione: preregistrazioni/e162.md. Scrive risultati/e162_messaggio_nei_temi.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e131_procedimento_riga as e131
import e135_stato_riga as e135
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
SEMI = (1, 2, 3)
THETA, C = 0.3, 0.0
_MOD = None


def genera(P, starts, q, L, mod, seme, flusso):
    """Come e153.genera, ma se flusso non e' None il tema di ogni riga sono le 3 parole successive del flusso."""
    rnd = random.Random(seme)
    it = iter(flusso) if flusso is not None else None
    h = {f: 0.0 for f in e145.SCELTE}
    righe = []
    for pag, d in P.items():
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        prima_sopra = None
        tema = [rnd.choice(pool) for _ in range(e153.K)]
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            if it is not None:
                tema = [next(it) for _ in range(e153.K)]
            else:
                tema = [t if rnd.random() < C else rnd.choice(pool) for t in tema]
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or D(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            for pos in range(1, len(ps)):
                cand = [e153.variante(rnd.choice(tema) if rnd.random() < THETA else rnd.choice(pool), e153.MU, mod, rnd) for _ in range(e152.CANDIDATE)]
                ultimo = D(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, D(x)[0]), 0.05) ** e153.LAM) if ultimo else 1.0
                    if pos == 1 and D(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    pesi.append(p)
                riga.append(rnd.choices(cand, pesi)[0])
            riga = e145.riscrivi(riga, h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = D(riga[0])[0]
            righe.append((pag, ini, riga))
    return righe


def una(args):
    global _MOD
    nome, seme, flusso, P, starts, q, L, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    if _MOD is None:
        _MOD = generatori.Modifiche(voy, D)
    rr = genera(P, starts, q, L, _MOD, seme, flusso)
    righe = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(righe, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in e145.SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, kk = [], 0
    for pag, ini, ps in rr:
        kk += ini
        par.append((pag, kk, ps))
    r['r_righe_consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    per = OrderedDict()
    for pag, ini, ps in rr:
        per.setdefault(pag, []).append((ini, ps))
    pagine = list(per.values())
    for etich, pp in (('grezzo', pagine), ('ripulito', e160.ripulisci(pagine))):
        _, t = e160.una(('x', pp))
        for k, x in t.items():
            r['%s %s' % (etich, k)] = x['z']
    return (nome, seme), r


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    lat = lingue.parole('Latin')[:60000]
    flusso = generatori.codice_per_rango(lat, voy, generatori.ModelloParole(voy, D), random.Random(162))
    lavori = [(n, s, f, P, starts, q, L, voy, soglia_ab, v, vb) for n, f in (('temi dal messaggio (latino codificato)', flusso), ('temi a caso (riferimento e153)', None)) for s in SEMI]
    per = defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for (nome, seme), r in pool.imap(una, lavori):
            per[nome].append(r)
    medie = OrderedDict()
    for nome in ('temi dal messaggio (latino codificato)', 'temi a caso (riferimento e153)'):
        gruppo = per[nome]
        chiavi = [k for k, x in gruppo[0].items() if isinstance(x, (int, float)) and all(isinstance(g.get(k), (int, float)) for g in gruppo)]
        mm = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
        esiti = OrderedDict()
        for prop, f in e61.BANDE.items():
            try:
                esiti[prop] = bool(f(mm, v))
            except (KeyError, TypeError, ZeroDivisionError):
                esiti[prop] = False
        esiti['bordo di riga'] = 0.5 * vb[0] <= mm['bordo_inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= mm['bordo_fine'] <= 2 * vb[1]
        mm['esiti'] = esiti
        R = mm['R_riga'] if mm.get('R_riga') is not None else 1
        mm['riga_riprodotta'] = (mm['S1'] <= 0.7 and R < 0.1 and mm['A'] >= 1.0 and mm['scelte_per_riga'] >= 3 and abs(mm['r_righe_consecutive'] - e145.VOY_R1) <= 0.07)
        medie[nome] = mm
        print('%-40s %d/18 | R %.2f S1 %.2f A %.3f scelte %.1f r %.3f | riga %s | %s' % (
            nome, sum(esiti.values()), mm.get('R_riga') or 0, mm['S1'], mm['A'], mm['scelte_per_riga'], mm['r_righe_consecutive'], mm['riga_riprodotta'],
            ' '.join('%s %.1f' % (k, mm[k]) for k in mm if k.startswith(('grezzo', 'ripulito')))), flush=True)
    mess, rif = medie['temi dal messaggio (latino codificato)'], medie['temi a caso (riferimento e153)']
    visibile = any((mess[k] or 0) > 4 and (mess[k] or 0) - (rif.get(k) or 0) >= 3 for k in mess if k.startswith(('grezzo', 'ripulito')))
    esito = OrderedDict([('a_riga_riprodotta_col_messaggio', mess['riga_riprodotta']), ('b_messaggio_visibile', visibile)])
    print('(a) riga riprodotta col messaggio: %s | (b) messaggio visibile ai test: %s' % (mess['riga_riprodotta'], visibile))
    with open(os.path.join(RISULTATI, 'e162_messaggio_nei_temi.json'), 'w', encoding='utf-8') as fo:
        json.dump({'medie': medie, 'esito': esito}, fo, ensure_ascii=False, indent=1, default=str)
    misure_t = [k for k in mess if k.startswith(('grezzo', 'ripulito'))]
    out = ['# e162 — Un messaggio nascosto nei temi di riga sarebbe visibile?', '', 'Generatore e153 (θ 0,3) con temi dal latino codificato parola per parola, contro temi a caso. '
           'Medie su tre semi. Preregistrazione: `preregistrazioni/e162.md`.', '',
           '| generatore | pagella | R | S(1) | A | scelte | r | riga | ' + ' | '.join(misure_t) + ' |', '|---|---|---|---|---|---|---|---|' + '---|' * len(misure_t)]
    for nome, m in medie.items():
        out.append('| %s | %d/18 | %.2f | %.2f | %.3f | %.1f | %.3f | %s | %s |' % (nome, sum(m['esiti'].values()), m.get('R_riga') or 0, m['S1'], m['A'], m['scelte_per_riga'],
                                                                             m['r_righe_consecutive'], 'sì' if m['riga_riprodotta'] else 'no', ' | '.join('%.1f' % (m.get(k) or 0) for k in misure_t)))
    out += ['', '(a) Riga riprodotta col messaggio: **%s**. (b) Messaggio visibile ai test di struttura: **%s**.' % ('sì' if mess['riga_riprodotta'] else 'no', 'sì' if visibile else 'no')]
    with open(os.path.join(RISULTATI, 'e162_messaggio_nei_temi.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
