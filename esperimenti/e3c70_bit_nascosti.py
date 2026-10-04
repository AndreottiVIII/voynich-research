# -*- coding: utf-8 -*-
"""Esperimento e3c70: un messaggio a bit nascosto nelle scelte doppie (idea del cifrario biletterale di Bacone: la
forma scelta porta un bit, cinque bit fanno una lettera). Sequenza, pagina per pagina in ordine di lettura, degli scarti
r = scelta − atteso (atteso dell'e3c48: stessa parola coperta + pagina + deriva) per qo/o, k/t, sh/ch, -ey/-dy.
(1) Pettine nell'autocorrelazione: D_L = C(L) − (C(L − 1) + C(L + 1)) / 2 per L = 3 … 10, z da ricampionamento delle
pagine. (2) Fase fissa: per P = 2 … 8, quanto la media degli scarti dipende dalla posizione modulo P contata
dall'inizio della pagina e dall'inizio della riga; nullo con spostamenti circolari casuali della sequenza (che tengono
lo stato). Controlli finti: messaggio latino codificato alla Bacone (deve dare il segnale) e solo stato (non deve).

Preregistrazione: preregistrazioni/e3c70.md. Scrive risultati/e3c70_bit_nascosti.json e .md.
"""
import json, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e381_parole_intere as e381
import e3b45_raccordo_a_capo as e3b45
import e3b62_memoria_nullo_largo as e3b62
import e3c33_riga_o_memoria as e3c33
import e3c68_segno_che_azzera as e3c68

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUATTRO = ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')
LMAX = 11
PP = tuple(range(2, 9))
BOOT = 1000
PERM = 300
Z = 3.5


def flussi(pagine, classi):
    """Per pagina: (scarti, posizione nella riga) in ordine di lettura."""
    e3c33.MIN_PAROLE, e3c33.DMAX = 3, 3
    tok = e3c33.raccogli(pagine, classi)
    v, p = e3c68.attese(tok)
    per = defaultdict(list)
    conta_riga = defaultdict(int)
    for j, t in enumerate(tok):
        k = conta_riga[t[2]]
        conta_riga[t[2]] += 1
        per[t[0]].append((v[j] - p[j], k))
    return [(np.array([a for a, _ in x]), np.array([b for _, b in x])) for _, x in sorted(per.items())]


def autocorr(ff):
    """(pagine, LMAX + 1, 2): Σ r_i r_{i+L} e Σ r_i² per pagina."""
    out = np.zeros((len(ff), LMAX + 1, 2))
    for u, (r, _) in enumerate(ff):
        for L in range(1, LMAX + 1):
            if len(r) > L:
                out[u, L, 0] = float((r[:-L] * r[L:]).sum())
                out[u, L, 1] = float((r[:-L] ** 2).sum() + (r[L:] ** 2).sum()) / 2
    return out


def pettine(s):
    C = s[..., 0] / s[..., 1]
    return np.stack([C[..., L] - (C[..., L - 1] + C[..., L + 1]) / 2 for L in range(3, LMAX)], axis=-1), C


def fase(ff, P, ancora):
    """Σ_φ n_φ · (media_φ − media)², con le medie per fase prese su tutte le pagine insieme (ancora 'pagina' o 'riga')."""
    s, n = np.zeros(P), np.zeros(P)
    for r, pos in ff:
        idx = (np.arange(len(r)) if ancora == 'pagina' else pos) % P
        s += np.bincount(idx, weights=r, minlength=P)
        n += np.bincount(idx, minlength=P)
    m = s / np.where(n > 0, n, 1)
    mt = s.sum() / n.sum()
    return float((n * (m - mt) ** 2).sum())


def prova_fase(ff, rng):
    ris = OrderedDict()
    for ancora in ('pagina', 'riga'):
        for P in PP:
            oss = fase(ff, P, ancora)
            nul = []
            for _ in range(PERM):
                sp = []
                for r, pos in ff:
                    s = rng.integers(0, len(r)) if len(r) else 0
                    sp.append((np.roll(r, s), pos))
                nul.append(fase(sp, P, ancora))
            nul = np.array(nul)
            ris['%s, P=%d' % (ancora, P)] = OrderedDict([('F', oss), ('F_nullo', float(nul.mean())), ('z', float((oss - nul.mean()) / nul.std()) if nul.std() > 0 else 0.0)])
    return ris


def misura(ff, rng):
    st = autocorr(ff)
    d, C = pettine(st.sum(0))
    boot = np.array([pettine(st[rng.integers(0, len(ff), len(ff))].sum(0))[0] for _ in range(BOOT)])
    z = d / boot.std(0)
    pet = OrderedDict(('L=%d' % L, OrderedDict([('D', float(d[i])), ('z', float(z[i]))])) for i, L in enumerate(range(3, LMAX)))
    fa = prova_fase(ff, rng)
    return OrderedDict([('scelte', int(sum(len(r) for r, _ in ff))), ('autocorrelazione', [float(x) for x in C[1:]]), ('pettine', pet),
                        ('picchi', [k for k, x in pet.items() if x['z'] > Z]), ('fase', fa), ('fasi_significative', [k for k, x in fa.items() if x['z'] > Z])])


def bacone(testo):
    alfa = 'abcdefghiklmnopqrstuxyz'
    bits = []
    for c in testo.lower():
        c = {'j': 'i', 'v': 'u', 'w': 'u'}.get(c, c)
        if c in alfa:
            i = alfa.index(c)
            bits += [(i >> (4 - b)) & 1 for b in range(5)]
    return bits


def finto(modo, rng, bits=None, pagine=200, righe=18):
    """Flussi finti: scelte con preferenza di parola; 'bacone' = il 35% delle scelte porta il bit del messaggio (che
    riparte a ogni pagina); 'stato' = il 35% segue uno stato che cambia con probabilità 0,2."""
    ff = []
    for _ in range(pagine):
        r, pos, n, stato = [], [], 0, rng.random() < 0.5
        for _ in range(righe):
            for k in range(rng.integers(4, 9)):
                q = rng.uniform(0.2, 0.8)
                if modo == 'bacone':
                    v = bits[n % len(bits)] if rng.random() < 0.35 else (rng.random() < q)
                else:
                    if rng.random() < 0.2:
                        stato = rng.random() < 0.5
                    v = stato if rng.random() < 0.35 else (rng.random() < q)
                r.append(float(v) - q)
                pos.append(k)
                n += 1
        ff.append((np.array(r), np.array(pos)))
    return ff


def main():
    rng = np.random.default_rng(3370)
    latino = ' '.join(' '.join(''.join(w) for w in r) for r in e381.testi()['Historical - Latin (Abbreviated) - Literary - NT (Vulgate).txt'][:3000] if r)
    bits = bacone(latino)
    ris = OrderedDict()
    ris['controllo: messaggio alla Bacone'] = misura(finto('bacone', rng, bits), rng)
    ris['controllo: solo stato'] = misura(finto('stato', rng), rng)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    cl = OrderedDict((k, e3b62.CV[k]) for k in QUATTRO)
    for q, pd in (('Voynich ZL', e341.pagine()), ('Voynich IT', e3b45.pagine_it())):
        pagine = [(mano[pg], [[tuple(e3b62.D(w)) for w in r if w] for par in pars for r in par]) for pg, pars in pd.items() if mano.get(pg)]
        ris[q] = misura(flussi(pagine, cl), rng)
    for k, x in ris.items():
        print(k, x['picchi'], x['fasi_significative'], flush=True)
    b, s = ris['controllo: messaggio alla Bacone'], ris['controllo: solo stato']
    ok = bool(b['picchi'] or b['fasi_significative']) and not (s['picchi'] or s['fasi_significative'])
    zl, it = ris['Voynich ZL'], ris['Voynich IT']
    comuni = sorted((set(zl['picchi']) & set(it['picchi'])) | (set(zl['fasi_significative']) & set(it['fasi_significative'])))
    if not ok:
        esito = 'prova non valida (i controlli non si comportano come previsto)'
    elif comuni:
        esito = 'segnale di un messaggio a bit: ' + ', '.join(comuni)
    else:
        esito = 'nessun segnale di un messaggio a bit nelle scelte'
    out = OrderedDict([('misure', ris), ('controlli_ok', ok), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c70_bit_nascosti.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c70 — Un messaggio a bit nascosto nelle scelte (alla Bacone)?', '', 'Preregistrazione: `preregistrazioni/e3c70.md`.', '']
    for k, x in ris.items():
        md += ['## %s (%d scelte)' % (k, x['scelte']), '', 'Autocorrelazione a 1 … %d: %s.' % (LMAX, ' '.join('%+.3f' % c for c in x['autocorrelazione'])), '',
               'Pettine (z): ' + ', '.join('%s %.1f' % (L, y['z']) for L, y in x['pettine'].items()) + '.', '',
               'Fase (z): ' + ', '.join('%s %.1f' % (f, y['z']) for f, y in x['fase'].items()) + '.', '',
               'Picchi: %s. Fasi significative: %s.' % (', '.join(x['picchi']) or 'nessuno', ', '.join(x['fasi_significative']) or 'nessuna'), '']
    md += ['Controlli validi: %s. Esito: **%s**.' % ('sì' if ok else 'no', esito)]
    open(os.path.join(RISULTATI, 'e3c70_bit_nascosti.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
