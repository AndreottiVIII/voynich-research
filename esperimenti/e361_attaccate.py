# -*- coding: utf-8 -*-
"""Esperimento 361: le forme nuove (parole uniche non varianti di parole frequenti) si tagliano in due parole esistenti
piu' delle parole comuni della stessa lunghezza? Le due parti compaiono altrove come coppia vicina? Stanno in fine riga?

Preregistrazione: preregistrazioni/e361.md. Scrive risultati/e361_attaccate.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
PERM = 1000


def main():
    rnd = random.Random(361)
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                righe.append(ws)
    freq = Counter(w for r in righe for w in r)
    coppie = Counter((a, b) for r in righe for a, b in zip(r, r[1:]))
    fine = {w for r in righe for w in r[-1:]}
    in_fine = Counter(r[-1] for r in righe)
    sim = e350.simili_globali(set(freq))
    U = {w: tuple(D(w)) for w in freq}

    def tagli(w):
        u = U[w]
        out = []
        for k in range(2, len(u) - 1):
            a, b = ''.join(u[:k]), ''.join(u[k:])
            if freq.get(a, 0) >= 3 and freq.get(b, 0) >= 3:
                out.append((a, b))
        return out
    nuove, errori = [], []
    for w, n in freq.items():
        if n == 1 and len(U[w]) >= 5:
            (errori if any(freq[v] >= 20 for v in sim[w] if v != w) else nuove).append(w)
    comuni = defaultdict(list)
    for w, n in freq.items():
        if n >= 5 and len(U[w]) >= 5:
            comuni[len(U[w])].append(w)
    quota = lambda ws: statistics.mean(bool(tagli(w)) for w in ws)
    qn, qe = quota(nuove), quota(errori)
    lens = [len(U[w]) for w in nuove]
    rif = []
    for _ in range(PERM):
        camp = []
        for L in lens:
            pool = comuni.get(L) or comuni.get(L - 1) or comuni.get(L + 1) or [w for v in comuni.values() for w in v]
            camp.append(rnd.choice(pool))
        rif.append(quota(camp))
    m, sd = statistics.mean(rif), statistics.pstdev(rif)
    z = (qn - m) / sd if sd else 0.0
    att = [w for w in nuove if tagli(w)]
    viste = statistics.mean(any(coppie[t] > 0 for t in tagli(w)) for w in att) if att else 0.0
    # fondo: le stesse parti, accoppiate a caso
    parti_a = [t[0] for w in att for t in tagli(w)[:1]]
    parti_b = [t[1] for w in att for t in tagli(w)[:1]]
    fondo = []
    for _ in range(200):
        bb = rnd.sample(parti_b, len(parti_b))
        fondo.append(statistics.mean(coppie[(a, b)] > 0 for a, b in zip(parti_a, bb)))
    fine_att = statistics.mean(in_fine[w] > 0 for w in att) if att else 0.0
    non_att = [w for w in nuove if not tagli(w)]
    fine_non = statistics.mean(in_fine[w] > 0 for w in non_att) if non_att else 0.0
    if z > 3 and qn >= 0.30:
        esito = 'molte forme nuove sono due parole attaccate'
    elif z < 2:
        esito = 'no'
    else:
        esito = 'incerto'
    out = OrderedDict([('forme_nuove', len(nuove)), ('quota_attaccate_forme_nuove', qn), ('quota_attaccate_errori', qe), ('riferimento_parole_comuni', m), ('z', z),
                       ('attaccate_con_coppia_vista_altrove', viste), ('fondo_coppie_a_caso', statistics.mean(fondo)),
                       ('in_fine_riga_attaccate', fine_att), ('in_fine_riga_altre_forme_nuove', fine_non), ('esito', esito),
                       ('esempi', [(w, tagli(w)[0]) for w in att[:20]])])
    print(json.dumps(out, ensure_ascii=False)[:1500], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e361_attaccate.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e361 — Le forme nuove sono due parole attaccate?', '', 'Preregistrazione: `preregistrazioni/e361.md`.', '',
          '- Forme nuove (≥ 5 segni): %d; si tagliano in due parole esistenti: %.3f.' % (len(nuove), qn),
          '- Errori (≥ 5 segni): %.3f.' % qe,
          '- Parole comuni della stessa lunghezza: %.3f (z della differenza %.1f).' % (m, z),
          '- Fra le forme nuove attaccate, la coppia compare altrove come due parole vicine: %.3f (fondo con le parti accoppiate a caso %.3f).' % (viste, statistics.mean(fondo)),
          '- In fine riga: attaccate %.3f, altre forme nuove %.3f.' % (fine_att, fine_non), '', 'Esito: **%s**.' % esito, '',
          'Esempi: %s.' % ', '.join('%s = %s + %s' % (w, a, b) for w, (a, b) in out['esempi'][:12])]
    open(os.path.join(RISULTATI, 'e361_attaccate.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
