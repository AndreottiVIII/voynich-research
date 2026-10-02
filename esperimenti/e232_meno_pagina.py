# -*- coding: utf-8 -*-
"""Esperimento 232: il generatore dell'e230 con eta 1 e sigma 0,09, piu' 'delta' (parola di base dalle frequenze del
Voynich intero invece che dal serbatoio della pagina), valutato con il discriminatore dell'e231.

Preregistrazione: preregistrazioni/e232.md. Scrive risultati/e232_meno_pagina.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231

RISULTATI = os.path.join(QUI, '..', 'risultati')
DELTA, SEME_SCELTA, SEMI_VERIFICA = (0.0, 0.2, 0.4), 1, (2, 3)
_GLOB = {}


def globali(c, lingua, alfa):
    """Tipi e pesi (conteggio^alfa) delle parole non iniziali di riga del Voynich nella lingua data."""
    if (lingua, alfa) not in _GLOB:
        cnt = Counter(w for d in c['P'].values() if (d['lingua'] if d['lingua'] in c['starts'] else 'B') == lingua
                      for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w))
        tipi = sorted(cnt)
        _GLOB[(lingua, alfa)] = (tipi, [cnt[t] ** alfa for t in tipi])
    return _GLOB[(lingua, alfa)]


def genera(c, prm, seme):
    """Come e230.genera ('gamma', 'fisica'), con in piu' 'delta': la parola di base viene, con questa probabilita',
    dalle frequenze del Voynich intero nella lingua di Currier della pagina (peso conteggio^alfa)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica, delta = prm.get('gamma', 0.0), prm.get('fisica', False), prm.get('delta', 0.0)
    sez = e230.sezioni()
    lessico = defaultdict(list)
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    h = {f: 0.0 for f in e145.SCELTE}
    righe, storia = [], []
    for pag, d in c['P'].items():
        s_pag = sez.get(pag)
        nuove_pag = []
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        cnt = Counter(pool)
        tipi = list(cnt)
        pesi_pool = [cnt[t] ** prm['alfa'] for t in tipi]
        lex = lessico[s_pag]
        gt, gp = globali(c, lingua, prm['alfa'])

        def estrai():
            if gamma and lex and rnd.random() < gamma:
                return rnd.choice(lex)
            if delta and rnd.random() < delta:
                return rnd.choices(gt, gp)[0]
            return rnd.choices(tipi, pesi_pool)[0]

        tema = [estrai() for _ in range(e153.K)]
        prima_sopra, sopra = None, None
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
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
                if prm['psi'] and storia and 1 <= pos <= n - 3 and rnd.random() < prm['psi']:
                    src = rnd.choice(storia)
                    if len(src) >= 4:
                        a = rnd.randrange(1, len(src) - 2)
                        m = min(rnd.choice((2, 3)), n - pos, len(src) - a)
                        riga += [e224.variante(x, e153.MU / 2, mod, rnd, prm['nu'], att, Dv) for x in src[a:a + m]]
                        continue
                cand = []
                for j in range(k):
                    if fisica:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi']
                    else:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra)
                    if copia and fisica:
                        x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                        centri, acc = [], 0
                        for w in sopra:
                            centri.append(acc + len(Dv(w)) / 2)
                            acc += len(Dv(w)) + 1
                        base = sopra[min(range(len(sopra)), key=lambda t: abs(centri[t] - x0))]
                    elif copia:
                        base = sopra[pos]
                    else:
                        base = rnd.choice(tema) if rnd.random() < 0.3 else estrai()
                    cand.append(e224.variante(base, e153.MU, mod, rnd, prm['nu'], att, Dv))
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    pesi.append(p)
                x = rnd.choices(cand, pesi)[0]
                if prm['sigma'] and pos < n - 1 and len(Dv(x)) >= 4 and rnd.random() < prm['sigma']:
                    s = e224.spezza(x, att, Dv, rnd)
                    if s:
                        riga += s
                        continue
                riga.append(x)
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe


def pagine_di(rr):
    out = OrderedDict()
    for pag, _, ps in rr:
        ps = [w for w in ps if trascrizione.pulita(w)]
        if ps:
            out.setdefault(pag, []).append(ps)
    return out


def descrittive(pag):
    tutte = Counter(w for rr in pag.values() for r in rr for w in r)
    top = {w for w, _ in tutte.most_common(100)}
    tt, t100, fm = [], [], []
    for rr in pag.values():
        ws = [w for r in rr for w in r]
        if len(ws) < e231.MIN_PAROLE:
            continue
        tt.append(len(set(ws)) / len(ws))
        t100.append(sum(w in top for w in ws) / len(ws))
        fm.append(sum(r[-1].endswith('m') for r in rr) / len(rr))
    return OrderedDict([('tipi_su_parole_pagina', statistics.mean(tt)), ('fra_le_100', statistics.mean(t100)), ('fine_m', statistics.mean(fm))])


def prova(c, vpag, rif, prm, seme):
    gp = pagine_di(genera(c, prm, seme))
    r = e231.confronto(vpag, gp, rif)
    r.update(descrittive(gp))
    return r


def main():
    c = e224.contesto()
    conf = dict(e224.BASE, eta=1.0, sigma=0.09)
    identico = genera(c, conf, SEME_SCELTA) == e230.genera(c, conf, SEME_SCELTA)
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    ris = OrderedDict([('configurazione', {k: (list(v) if isinstance(v, tuple) else v) for k, v in conf.items()}), ('validita_identico_e230', identico),
                       ('Voynich', descrittive(OrderedDict((p, rr) for p, (_, rr) in vpag.items())))])
    print("identico all'e230 con delta 0: %s; Voynich %s" % (identico, dict(ris['Voynich'])), flush=True)
    scelta = OrderedDict()
    for d in DELTA:
        scelta['delta %.1f' % d] = prova(c, vpag, rif, dict(conf, delta=d), SEME_SCELTA)
        r = scelta['delta %.1f' % d]
        print('seme %d, delta %.1f: AUC %.3f, tipi/parole %.3f, fra le 100 %.3f, fine -m %.3f' % (
            SEME_SCELTA, d, r['AUC'], r['tipi_su_parole_pagina'], r['fra_le_100'], r['fine_m']), flush=True)
    migliore = min(DELTA, key=lambda d: (scelta['delta %.1f' % d]['AUC'], d))
    verifica = OrderedDict()
    for d in sorted({0.0, migliore}):
        verifica['delta %.1f' % d] = [prova(c, vpag, rif, dict(conf, delta=d), s) for s in SEMI_VERIFICA]
        print('verifica delta %.1f: AUC %s' % (d, [round(x['AUC'], 3) for x in verifica['delta %.1f' % d]]), flush=True)
    auc = {k: statistics.mean(x['AUC'] for x in v) for k, v in verifica.items()}
    a0, am = auc['delta 0.0'], auc['delta %.1f' % migliore]
    aiuta = migliore > 0 and am <= a0 - 0.05
    esito = 'non valido' if not identico else ('indistinguibile' if am <= 0.6 else ('delta aiuta' if aiuta else 'delta non aiuta abbastanza'))
    ris.update([('scelta_seme_1', scelta), ('delta_scelto', migliore), ('verifica', verifica), ('AUC_verifica', auc), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e232_meno_pagina.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v = ris['Voynich']
    md = ['# e232 — Meno pagina, più manoscritto, contro il discriminatore', '',
          "Generatore dell'e230 con la partenza dell'e224, η 1 e σ 0,09; δ = probabilità di prendere la parola di base dalle frequenze "
          "del Voynich intero (stessa lingua). AUC del discriminatore dell'e231. Validità (δ 0 = e230): %s. Preregistrazione: "
          '`preregistrazioni/e232.md`.' % ('sì' if identico else 'NO'), '',
          '| | AUC | tipi su parole (pagina) | fra le 100 più frequenti | righe in -m |', '|---|---|---|---|---|',
          '| **Voynich** | | %.3f | %.3f | %.3f |' % (v['tipi_su_parole_pagina'], v['fra_le_100'], v['fine_m'])]
    for k, r in scelta.items():
        md.append('| %s, seme 1 | %.3f | %.3f | %.3f | %.3f |' % (k, r['AUC'], r['tipi_su_parole_pagina'], r['fra_le_100'], r['fine_m']))
    for k, rr in verifica.items():
        md.append('| %s, semi 2–3 | %.3f | %.3f | %.3f | %.3f |' % (k, auc[k], *(statistics.mean(x[q] for x in rr) for q in ('tipi_su_parole_pagina', 'fra_le_100', 'fine_m'))))
    md += ['', 'Caratteristiche più pesanti che restano (δ %.1f, seme 2; coefficiente positivo = più nel generatore):' % migliore, '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica['delta %.1f' % migliore][0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e232_meno_pagina.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
