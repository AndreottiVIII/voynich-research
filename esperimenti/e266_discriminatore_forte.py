# -*- coding: utf-8 -*-
"""Esperimento 266: il discriminatore dell'e231 con quattro gruppi in piu' (G6 coppie di parole, G7 posizione nella riga,
G8 prime righe di paragrafo, G9 ortografia di pagina), contro i generatori e192 ed e241.

Preregistrazione: preregistrazioni/e266.md. Scrive risultati/e266_discriminatore_forte.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, misure, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = e231.D
GRUPPI = ('G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9')
RIF_E231 = 0.874


def jsd(a, b):
    ks = set(a) | set(b)
    na, nb = sum(a.values()) or 1, sum(b.values()) or 1
    h = 0.0
    for k in ks:
        p, q = a[k] / na, b[k] / nb
        m = (p + q) / 2
        if p:
            h += p / 2 * math.log2(p / m)
        if q:
            h += q / 2 * math.log2(q / m)
    return h


def voynich_ini():
    out = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            out.setdefault(r.pagina, [r.lingua, []])[1].append((bool(r.inizio_par), ps))
    return out


def e192_ini(seme=1):
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy), 0.4
    e153.variante = e192.variante
    out = OrderedDict()
    for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy, e162.D), seme, None):
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            out.setdefault(pag, []).append((bool(ini), ps))
    return out


def extra(pagine_ini):
    """Caratteristiche G6-G9 per pagina: OrderedDict pagina -> OrderedDict."""
    tutte = [w for rr in pagine_ini.values() for _, r in rr for w in r]
    coppie_tot = Counter((a, b) for rr in pagine_ini.values() for _, r in rr for a, b in zip(r, r[1:]))
    glob = Counter(x for w in tutte for x in D(w))
    out = OrderedDict()
    for p, rr in pagine_ini.items():
        righe = [r for _, r in rr]
        if sum(map(len, righe)) < e231.MIN_PAROLE:
            continue
        f = OrderedDict()
        cp = [(a, b) for r in righe for a, b in zip(r, r[1:])]
        f['G6 coppie viste altrove'] = sum(coppie_tot[x] >= 2 for x in cp) / len(cp) if cp else 0.0
        f['G6 coppie identiche'] = sum(a == b for a, b in cp) / len(cp) if cp else 0.0
        s2 = [1 - misure._dist_norm(tuple(D(a)), tuple(D(b))) for r in righe for a, b in zip(r, r[2:])]
        f['G6 somiglianza a distanza 2'] = statistics.mean(s2) if s2 else 0.0
        for nome, sel in (('prima', lambda r: r[0]), ('seconda', lambda r: r[1] if len(r) > 1 else None), ('ultima', lambda r: r[-1])):
            ls = [len(D(sel(r))) for r in righe if sel(r)]
            f['G7 lunghezza %s parola' % nome] = statistics.mean(ls) if ls else 0.0
        f['G7 prime con y/d/s'] = statistics.mean(D(r[0])[0] in ('y', 'd', 's') for r in righe)
        for g in ('m', 'n', 'l', 'r', 'y'):
            f['G7 ultime in %s' % g] = statistics.mean(D(r[-1])[-1] == g for r in righe)
        prime = [w for ini, r in rr if ini for w in r]
        altre = [w for ini, r in rr if not ini for w in r]
        cp_, ca = Counter(x for w in prime for x in D(w)), Counter(x for w in altre for x in D(w))
        np_, na = sum(cp_.values()) or 1, sum(ca.values()) or 1
        for g in ('p', 'f', 't', 'k'):
            f['G8 %s prime righe meno altre' % g] = cp_[g] / np_ - ca[g] / na
        f['G8 lunghezza parole prime righe'] = statistics.mean(len(D(w)) for w in prime) if prime else 0.0
        cpag = Counter(x for r in righe for w in r for x in D(w))
        f['G9 JSD pagina-manoscritto'] = jsd(cpag, glob)
        meta = len(righe) // 2
        f['G9 JSD prima-seconda meta'] = jsd(Counter(x for r in righe[:meta] for w in r for x in D(w)), Counter(x for r in righe[meta:] for w in r for x in D(w)))
        out[p] = f
    return out


def tabella(pagine_ini, rif):
    nomi, X, nf = e231.caratteristiche(OrderedDict((p, [r for _, r in rr]) for p, rr in pagine_ini.items()), rif)
    ex = extra(pagine_ini)
    righe = [list(x) + list(ex[p].values()) for p, x in zip(nomi, X) if p in ex]
    nomi = [p for p in nomi if p in ex]
    return nomi, np.array(righe), nf + list(next(iter(ex.values())).keys())


def confronto(vt, gt):
    nv, Xv, nf = vt
    ng, Xg, _ = gt
    comuni = [p for p in nv if p in set(ng)]
    iv, ig = {p: i for i, p in enumerate(nv)}, {p: i for i, p in enumerate(ng)}
    X = np.vstack([Xv[[iv[p] for p in comuni]], Xg[[ig[p] for p in comuni]]])
    y = np.array([0] * len(comuni) + [1] * len(comuni))
    gruppi = np.array(comuni + comuni)
    auc = e231.auc_cv(X, y, gruppi)
    per = OrderedDict()
    for g in GRUPPI:
        col = [i for i, n in enumerate(nf) if n.startswith(g + ' ')]
        per[g] = e231.auc_cv(X[:, col], y, gruppi) if col else None
    m = e231.modello().fit(X, y)
    coef = m[-1].coef_[0]
    pesanti = [(nf[i], float(coef[i]), float(X[y == 0, i].mean()), float(X[y == 1, i].mean())) for i in np.argsort(-np.abs(coef))[:12]]
    return OrderedDict([('pagine', len(comuni)), ('AUC', auc), ('AUC_per_gruppo', per), ('piu_pesanti', pesanti)])


def main():
    c = e224.contesto()
    vi = voynich_ini()
    vpag = OrderedDict((p, rr) for p, (_, rr) in vi.items())
    rif = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt = tabella(vpag, rif)
    nv, Xv, nf = vt
    lingua = {p: l for p, (l, _) in vi.items()}
    ab = [i for i, p in enumerate(nv) if lingua[p] in ('A', 'B')]
    yab = np.array([lingua[nv[i]] == 'B' for i in ab], int)
    ris = OrderedDict([('controllo positivo (A contro B)', e231.auc_cv(Xv[ab], yab))])
    neg = []
    for s in e231.SEMI_NEGATIVO:
        y = np.array([1] * (len(nv) // 2) + [0] * (len(nv) - len(nv) // 2))
        random.Random(s).shuffle(y)
        neg.append(e231.auc_cv(Xv, y, semi=(s,)))
    ris['controllo negativo (etichette a caso)'] = float(np.mean(neg))
    print('controlli', ris, flush=True)
    pv_parole = OrderedDict((p, [r for _, r in rr]) for p, rr in vpag.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv_parole))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv_parole)))
    rr = e236.dopo(e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), 2), Counter(c['voy']), 102)
    g241 = OrderedDict()
    for pag, ini, ps in rr:
        g241.setdefault(pag, []).append((bool(ini), ps))
    for nome, gp in (('generatore e192 (seme 1)', e192_ini(1)), ('generatore e241 (seme 2)', g241)):
        ris[nome] = confronto(vt, tabella(gp, rif))
        print(nome, ris[nome]['AUC'], {k: (round(v, 3) if v is not None else None) for k, v in ris[nome]['AUC_per_gruppo'].items()}, flush=True)
    valido = ris['controllo positivo (A contro B)'] >= 0.8 and 0.4 <= ris['controllo negativo (etichette a caso)'] <= 0.6
    g = ris['generatore e241 (seme 2)']
    nuovi = [g['AUC_per_gruppo'][k] or 0 for k in ('G6', 'G7', 'G8', 'G9')]
    esito = 'non valido' if not valido else ('piu\' forte' if g['AUC'] >= RIF_E231 + 0.03 or max(nuovi) > 0.8 else 'non piu\' forte')
    ris['esito'] = esito
    json.dump(ris, open(os.path.join(RISULTATI, 'e266_discriminatore_forte.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e266 — Un discriminatore più forte', '',
          "Caratteristiche dell'e231 più G6 (coppie di parole), G7 (posizione nella riga), G8 (prime righe di paragrafo), G9 (ortografia di pagina). "
          'Controlli: A contro B %.3f; etichette a caso %.3f. Preregistrazione: `preregistrazioni/e266.md`.' % (
              ris['controllo positivo (A contro B)'], ris['controllo negativo (etichette a caso)']), '',
          '| confronto | AUC | ' + ' | '.join(GRUPPI) + ' |', '|---|---|' + '---|' * len(GRUPPI)]
    for nome in ('generatore e192 (seme 1)', 'generatore e241 (seme 2)'):
        r = ris[nome]
        md.append('| %s | %.3f | %s |' % (nome, r['AUC'], ' | '.join('%.3f' % (r['AUC_per_gruppo'][k] or 0) for k in GRUPPI)))
    md += ['', 'Caratteristiche più pesanti contro il generatore e241 (coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in g['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s** (riferimento e231 sul generatore e241: %.3f).' % (esito, RIF_E231)]
    open(os.path.join(RISULTATI, 'e266_discriminatore_forte.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
