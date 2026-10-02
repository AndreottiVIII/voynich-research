# -*- coding: utf-8 -*-
"""Esperimento 215: allineamento non supervisionato di spazi di parole (PPMI + SVD, inizio da profili di somiglianza,
Procrustes iterato con CSLS) fra il Voynich ripulito e latino/italiano/tedesco; controlli positivi (latino cifrato a
parole, con e senza involucro) e negativi (generatore, Voynich rimescolato nella riga).

Preregistrazione: preregistrazioni/e215.md. Scrive risultati/e215_allineamento_parole.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e156_lingue_ab as e156
import e160_testo_ripulito as e160
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192

RISULTATI = os.path.join(QUI, '..', 'risultati')
V, DIM, FIN, ITER, K = 1000, 40, 2, 30, 10
SEMI = (1, 2, 3, 4, 5)


def spazio(righe):
    """righe: liste di parole. -> (parole, matrice normalizzata V x DIM)."""
    freq = Counter(w for r in righe for w in r)
    voc = [w for w, _ in freq.most_common(V)]
    idx = {w: i for i, w in enumerate(voc)}
    C = np.zeros((len(voc), len(voc)))
    for r in righe:
        ii = [idx.get(w) for w in r]
        for a, i in enumerate(ii):
            if i is None:
                continue
            for b in range(max(0, a - FIN), min(len(ii), a + FIN + 1)):
                j = ii[b]
                if b != a and j is not None:
                    C[i, j] += 1
    tot = C.sum()
    r_, c_ = C.sum(axis=1, keepdims=True), C.sum(axis=0, keepdims=True)
    with np.errstate(divide='ignore', invalid='ignore'):
        P = np.log(C * tot / (r_ * c_))
    P[~np.isfinite(P)] = 0
    P = np.maximum(P, 0)
    U, S, _ = np.linalg.svd(P, full_matrices=False)
    X = U[:, :DIM] * np.sqrt(S[:DIM])
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    X -= X.mean(axis=0)
    X /= np.linalg.norm(X, axis=1, keepdims=True) + 1e-9
    return voc, X


def profili(X):
    M = X @ X.T
    M = np.sort(M, axis=1)
    M -= M.mean(axis=1, keepdims=True)
    M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
    return M


def csls(A, B):
    S = A @ B.T
    ra = np.sort(S, axis=1)[:, -K:].mean(axis=1, keepdims=True)
    rb = np.sort(S, axis=0)[-K:, :].mean(axis=0, keepdims=True)
    return 2 * S - ra - rb


def allinea(X, Z):
    n = min(len(X), len(Z))
    X, Z = X[:n], Z[:n]
    PX, PZ = profili(X), profili(Z)
    diz = np.argmax(PX @ PZ.T, axis=1)
    for _ in range(ITER):
        U, _, Vt = np.linalg.svd(X.T @ Z[diz])
        W = U @ Vt
        diz = np.argmax(csls(X @ W, Z), axis=1)
    S = csls(X @ W, Z)
    a = np.argmax(S, axis=1)
    b = np.argmax(S, axis=0)
    mutue = [(i, int(a[i]), float(S[i, a[i]])) for i in range(n) if b[a[i]] == i]
    return a, mutue


def bootstrap(righe, seme):
    rnd = random.Random(seme)
    return [rnd.choice(righe) for _ in righe]


def testi():
    pagine = e160.pagine_voynich()
    pul = e160.ripulisci(pagine)
    voy = [[w for w in ps if trascrizione.pulita(w)] for p in pul for _, ps in p]
    rnd = random.Random(215)
    rim = []
    for r in voy:
        r = r[:]
        rnd.shuffle(r)
        rim.append(r)
    # controllo positivo, come nell'e160, con la verita'
    voy_parole = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    lat = lingue.parole('Latin')[:35000]
    codice = generatori.codice_per_rango(lat, voy_parole, generatori.ModelloParole(voy_parole, e160.D), random.Random(e160.SEME))
    verita = defaultdict(Counter)
    for c, l in zip(codice, lat):
        verita[c][l] += 1
    verita_pul = defaultdict(Counter)
    for c, l in zip(codice, lat):
        verita_pul[e156.n2(c)][l] += 1
    tetto, con = e160.controllo()
    ctrl = [ps for p in tetto for _, ps in p]
    ctrl_pul = [ps for p in e160.ripulisci(con) for _, ps in p]
    # generatore e192
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(voy_parole), 0.4
    e153.variante = e192.variante
    per = OrderedDict()
    for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(voy_parole, e162.D), 1, None):
        per.setdefault(pag, []).append((ini, ps))
    gen = [[w for w in ps if trascrizione.pulita(w)] for p in e160.ripulisci(list(per.values())) for _, ps in p]
    return OrderedDict([('Voynich ripulito', (voy, None)), ('controllo: latino a parole', (ctrl, {k: v.most_common(1)[0][0] for k, v in verita.items()})),
                        ('controllo: latino a parole, involucro ripulito', (ctrl_pul, {k: v.most_common(1)[0][0] for k, v in verita_pul.items()})),
                        ('generatore e192 ripulito', (gen, None)), ('Voynich rimescolato nella riga', (rim, None))])


def riferimenti():
    lat = lingue.parole('Latin')[35000:335000]
    return OrderedDict([('latino', lat), ('italiano', lingue.parole('Italian')[:300000]), ('tedesco', lingue.parole('German')[:300000])])


def una(args):
    nome, righe, verita, lingua, rif_vz, seme = args
    voc_r, Z = rif_vz
    vv, X = spazio(bootstrap(righe, seme))
    a, mutue = allinea(X, Z)
    acc = None
    if verita is not None and lingua == 'latino':
        giuste = [verita.get(vv[i]) == voc_r[a[i]] for i in range(min(500, len(a))) if verita.get(vv[i]) in set(voc_r)]
        acc = sum(giuste) / len(giuste) if giuste else None
    gloss = sorted(((vv[i], voc_r[j], s) for i, j, s in mutue), key=lambda x: -x[2])[:40]
    return nome, lingua, seme, len(mutue), statistics.mean(s for *_, s in mutue) if mutue else 0.0, acc, gloss


def main():
    T = testi()
    R = riferimenti()
    spazi_r = {l: spazio([r[i:i + 9] for i in range(0, len(r), 9)]) for l, r in R.items()}
    lavori = [(n, rr, ver, l, spazi_r[l], s) for n, (rr, ver) in T.items() for l in R for s in SEMI]
    agg = defaultdict(list)
    glossari = {}
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, lingua, seme, nm, sm, acc, gloss in pool.imap(una, lavori):
            agg[(nome, lingua)].append((nm, sm, acc))
            if nome == 'Voynich ripulito' and seme == 1:
                glossari[lingua] = gloss
            print('%-46s %-8s seme %d | coppie mutue %d (somiglianza %.3f) | acc %s' % (nome, lingua, seme, nm, sm, '%.3f' % acc if acc is not None else '-'), flush=True)
    ris = OrderedDict()
    for (nome, lingua), v in agg.items():
        accs = [a for *_, a in v if a is not None]
        ris['%s | %s' % (nome, lingua)] = OrderedDict([('mutue_media', statistics.mean(x[0] for x in v)), ('mutue_dev', statistics.pstdev(x[0] for x in v)),
                                                       ('somiglianza_media', statistics.mean(x[1] for x in v)), ('accuratezza', statistics.mean(accs) if accs else None)])
    acc_ctrl = ris['controllo: latino a parole | latino']['accuratezza'] or 0
    valido = acc_ctrl >= 0.10
    significativo = []
    for l in R:
        v = ris['Voynich ripulito | %s' % l]
        g = ris['generatore e192 ripulito | %s' % l]
        r = ris['Voynich rimescolato nella riga | %s' % l]
        sd = (v['mutue_dev'] ** 2 + max(g['mutue_dev'], r['mutue_dev']) ** 2) ** 0.5 or 1.0
        if v['mutue_media'] - max(g['mutue_media'], r['mutue_media']) >= 3 * sd:
            significativo.append(l)
    esito = 'test non valido' if not valido else ('allineamento significativo' if significativo else 'nessun allineamento')
    out = {'risultati': ris, 'glossari_voynich_seme1': glossari, 'valido': valido, 'lingue_significative': significativo, 'esito': esito}
    json.dump(out, open(os.path.join(RISULTATI, 'e215_allineamento_parole.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e215 — Decifrazione a parole per allineamento dei contesti', '', 'Coppie mutue (su 1.000 parole) dopo l\'allineamento, media ± dev. su 5 ricampionamenti; '
          'accuratezza @1 dove la verità è nota. Preregistrazione: `preregistrazioni/e215.md`.', '', '| testo | lingua | coppie mutue | somiglianza | accuratezza |', '|---|---|---|---|---|']
    for k, r in ris.items():
        n, l = k.split(' | ')
        md.append('| %s | %s | %.1f ± %.1f | %.3f | %s |' % (n, l, r['mutue_media'], r['mutue_dev'], r['somiglianza_media'], '%.3f' % r['accuratezza'] if r['accuratezza'] is not None else '–'))
    md += ['', 'Controllo valido: **%s**. Esito: **%s** %s.' % ('sì' if valido else 'no', esito, significativo or ''), '', 'Glossario del Voynich (seme 1), solo descrittivo:', '']
    for l, g in glossari.items():
        md.append('- %s: %s' % (l, ', '.join('%s=%s' % (a, b) for a, b, _ in g[:25])))
    open(os.path.join(RISULTATI, 'e215_allineamento_parole.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(valido, esito, significativo)


if __name__ == '__main__':
    main()
