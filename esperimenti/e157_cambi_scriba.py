# -*- coding: utf-8 -*-
"""Esperimento 157: salti delle preferenze di grafia dentro la pagina come indizio di cambio di scriba. Taratura su
pagine cucite (mani diverse contro stessa mano), poi pagine vere.

Preregistrazione: preregistrazioni/e157.md. Scrive risultati/e157_cambi_scriba.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e146_deriva_preferenze as e146

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERM, COPPIE, MIN_RIGHE, MARGINE = 157, 500, 100, 10, 4
SCELTE = e146.SCELTE


def righe_con_residui():
    righe, info, par = [], [], 0
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            par += bool(r.inizio_par)
            righe.append((r.pagina, par, list(r.parole)))
            info.append((r.pagina, r.mano))
    res = e146.residui(righe)
    vett = [{f: res.get((f, i)) for f in SCELTE} for i in range(len(righe))]
    per = OrderedDict()
    for i, (pag, mano) in enumerate(info):
        per.setdefault(pag, {'mano': mano, 'righe': []})['righe'].append(vett[i])
    return per


def stat_taglio(rr, t):
    s = 0.0
    for f in SCELTE:
        a = [r[f] for r in rr[:t] if r[f] is not None]
        b = [r[f] for r in rr[t:] if r[f] is not None]
        if len(a) >= 2 and len(b) >= 2:
            se = math.sqrt(statistics.pvariance(a) / len(a) + statistics.pvariance(b) / len(b))
            if se > 0:
                s += ((statistics.mean(a) - statistics.mean(b)) / se) ** 2
    return s


def massimo(rr):
    tagli = range(MARGINE, len(rr) - MARGINE + 1)
    return max((stat_taglio(rr, t), t) for t in tagli)


def prova(args):
    nome, rr, seme = args
    rnd = random.Random(seme)
    s, t = massimo(rr)
    nulli = []
    for _ in range(PERM):
        x = rr[:]
        rnd.shuffle(x)
        nulli.append(massimo(x)[0])
    p = (sum(n >= s for n in nulli) + 1) / (PERM + 1)
    return nome, OrderedDict([('righe', len(rr)), ('statistica', s), ('taglio', t), ('p', p)])


def main():
    rnd = random.Random(SEME)
    per = righe_con_residui()
    lunghe = {p: d for p, d in per.items() if len(d['righe']) >= 7}
    per_mano = defaultdict(list)
    for p, d in lunghe.items():
        if d['mano'] in ('1', '2', '3'):
            per_mano[d['mano']].append(p)
    lavori = []
    diverse = [('1', '2'), ('1', '3'), ('2', '3')]
    for i in range(COPPIE):
        a, b = diverse[i % 3]
        pa, pb = rnd.choice(per_mano[a]), rnd.choice(per_mano[b])
        lavori.append(('diverse %d %s+%s' % (i, pa, pb), lunghe[pa]['righe'][:7] + lunghe[pb]['righe'][:7], SEME + i))
    for i in range(COPPIE):
        m = rnd.choice(['1', '2', '3'])
        pa, pb = rnd.sample(per_mano[m], 2)
        lavori.append(('stessa %d %s+%s' % (i, pa, pb), lunghe[pa]['righe'][:7] + lunghe[pb]['righe'][:7], SEME + 1000 + i))
    vere = [(p, d['righe'], SEME + 5000 + k) for k, (p, d) in enumerate(per.items()) if len(d['righe']) >= MIN_RIGHE]
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        out = dict(pool.imap(prova, lavori + vere))
    rilev = lambda pref: [out[n[0]] for n in lavori if n[0].startswith(pref)]
    ok = lambda r: r['p'] < 0.01 and abs(r['taglio'] - 7) <= 2
    d_div = sum(ok(r) for r in rilev('diverse')) / COPPIE
    d_st = sum(ok(r) for r in rilev('stessa')) / COPPIE
    valido = d_div >= 0.5 and d_div >= 2 * max(d_st, 1e-9)
    pagine_vere = OrderedDict((p, out[p]) for p, _, _ in vere)
    candidate = OrderedDict((p, r) for p, r in pagine_vere.items() if r['p'] < 0.01)
    ris['taratura'] = OrderedDict([('rilevate_mani_diverse', d_div), ('rilevate_stessa_mano', d_st), ('valido', valido)])
    ris['pagine_vere'] = len(pagine_vere)
    ris['candidate'] = candidate
    ris['quota_candidate'] = len(candidate) / len(pagine_vere) if pagine_vere else None
    ris['f115r'] = pagine_vere.get('f115r')
    print('taratura: mani diverse %.2f, stessa mano %.2f | valido %s' % (d_div, d_st, valido))
    print('pagine vere %d, candidate (p<0,01) %d (%.1f%%) | f115r: %s' % (len(pagine_vere), len(candidate), 100 * ris['quota_candidate'], ris['f115r']))
    for p, r in candidate.items():
        print('   %s: righe %d, taglio dopo la riga %d, p %.4f' % (p, r['righe'], r['taglio'], r['p']))
    with open(os.path.join(RISULTATI, 'e157_cambi_scriba.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out_md = ['# e157 — Cambi di scriba dentro la pagina', '', 'Salto massimo delle preferenze di grafia fra due blocchi di righe; nullo: %d rimescolamenti delle righe. '
              'Preregistrazione: `preregistrazioni/e157.md`.' % PERM, '',
              '- Taratura: cuciture fra mani diverse rilevate **%.0f%%**, fra stessa mano %.0f%%. Metodo valido: **%s**.' % (100 * d_div, 100 * d_st, 'sì' if valido else 'no'),
              '- Pagine vere con almeno %d righe: %d; candidate con p < 0,01: **%d** (%.1f%%, attese per caso circa 1%%).' % (MIN_RIGHE, len(pagine_vere), len(candidate), 100 * ris['quota_candidate']),
              '- f115r: %s.' % (('p %.4f, taglio dopo la riga %d' % (ris['f115r']['p'], ris['f115r']['taglio'])) if ris['f115r'] else 'non analizzabile'), '',
              '| pagina | righe | taglio dopo la riga | p |', '|---|---|---|---|']
    for p, r in candidate.items():
        out_md.append('| %s | %d | %d | %.4f |' % (p, r['righe'], r['taglio'], r['p']))
    with open(os.path.join(RISULTATI, 'e157_cambi_scriba.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out_md) + '\n')


if __name__ == '__main__':
    main()
