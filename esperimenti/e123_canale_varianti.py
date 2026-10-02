# -*- coding: utf-8 -*-
"""Esperimento 123: un messaggio nella scelta ch/sh (canale alla Bacone)? Dipendenza in sequenza e schemi di 5 scelte,
contro il rimescolamento delle scelte dentro gli strati (pagina, prima riga, posizione, contesto).

Preregistrazione: preregistrazioni/e123.md. Scrive risultati/e123_canale_varianti.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, PERMUTAZIONI, KK = 123, 500, (1, 2, 3, 4, 5)
D = misure.divisore(misure.GLIFI_EVA)
BACONE = 'abcdefghiklmnopqrstuxyz'  # 23 lettere latine del codice (i=j, u=v, niente w)


def occorrenze(righe):
    """righe: (pagina, prima riga del paragrafo, parole). -> lista di (strato, scelta)."""
    out = []
    for pag, prima, ps in righe:
        n = len(ps)
        for i, w in enumerate(ps):
            if not trascrizione.pulita(w):
                continue
            u = D(w)
            pos = 'prima' if i == 0 else 'ultima' if i == n - 1 else 'seconda' if i == 1 else 'interna'
            for j, g in enumerate(u):
                if g in ('ch', 'sh'):
                    dopo = u[j + 1] if j + 1 < len(u) else '$'
                    out.append(((pag, prima, pos, j == 0, dopo), 1 if g == 'sh' else 0))
    return out


def entropia_blocchi(scelte, L=5):
    blocchi = Counter(tuple(scelte[i:i + L]) for i in range(0, len(scelte) - L + 1, L))
    n = sum(blocchi.values())
    return -sum(k / n * math.log2(k / n) for k in blocchi.values())


def statistiche(scelte):
    out = {'k%d' % k: misure.informazione_mutua(list(zip(scelte, scelte[k:]))) for k in KK}
    out['h5'] = entropia_blocchi(scelte)
    return out


def misura(occ, rnd):
    strati = [s for s, _ in occ]
    scelte = [c for _, c in occ]
    reale = statistiche(scelte)
    per = defaultdict(list)
    for i, s in enumerate(strati):
        per[s].append(i)
    nulli = defaultdict(list)
    for _ in range(PERMUTAZIONI):
        x = scelte[:]
        for idx in per.values():
            v = [x[i] for i in idx]
            rnd.shuffle(v)
            for i, c in zip(idx, v):
                x[i] = c
        for k, val in statistiche(x).items():
            nulli[k].append(val)
    out = OrderedDict([('occorrenze', len(occ)), ('quota_sh', sum(scelte) / len(scelte)), ('strati', len(per))])
    for k in reale:
        m, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        if k == 'h5':
            out['deficit_blocchi5'] = OrderedDict([('deficit', m - reale[k]), ('z', (m - reale[k]) / s if s else None)])
        else:
            out[k] = OrderedDict([('eccesso', reale[k] - m), ('z', (reale[k] - m) / s if s else None)])
    return out


def righe_voynich():
    out, prima = [], False
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole:
            continue
        out.append((r.pagina, bool(r.inizio_par), list(r.parole)))
    return out


def main():
    rv = righe_voynich()
    occ = occorrenze(rv)
    ris = OrderedDict()
    ris['Voynich'] = misura(occ, random.Random(SEME))
    # controllo positivo: testo latino nel canale (5 bit per lettera)
    lat = ''.join(c for c in ''.join(lingue.parole('Latin')[:20000]).replace('j', 'i').replace('v', 'u').replace('w', 'uu') if c in BACONE)
    bit = [int(b) for c in lat for b in format(BACONE.index(c), '05b')]
    occ_pos = [(s, bit[i] if i < len(bit) else c) for i, (s, c) in enumerate(occ)]
    ris['controllo positivo: latino nel canale'] = misura(occ_pos, random.Random(SEME))
    ts = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    ris['Timm e Schinner, seme 19'] = misura(occorrenze([(i // 29, ini, ps) for i, (ini, ps) in enumerate(ts)]), random.Random(SEME))
    for nome, r in ris.items():
        print('%-36s occ %5d sh %.2f strati %4d | %s | deficit blocchi5 %.4f (z %.1f)' % (
            nome, r['occorrenze'], r['quota_sh'], r['strati'], ' '.join('k%d %+.4f (z %.1f)' % (k, r['k%d' % k]['eccesso'], r['k%d' % k]['z'] or 0) for k in KK),
            r['deficit_blocchi5']['deficit'], r['deficit_blocchi5']['z'] or 0), flush=True)
    valido = (ris['controllo positivo: latino nel canale']['deficit_blocchi5']['z'] or 0) > 10
    v, t = ris['Voynich'], ris['Timm e Schinner, seme 19']
    dip = any((v['k%d' % k]['z'] or 0) > 4 and (t['k%d' % k]['z'] or 0) <= 4 for k in KK)
    aperto = (v['deficit_blocchi5']['z'] or 0) > 4 or dip
    frazione = v['deficit_blocchi5']['deficit'] / ris['controllo positivo: latino nel canale']['deficit_blocchi5']['deficit']
    ris['valido'], ris['canale_non_escluso'], ris['frazione_del_controllo'] = valido, aperto, frazione
    print('valido', valido, '| canale non escluso', aperto, '| deficit Voynich / controllo %.3f' % frazione)
    with open(os.path.join(RISULTATI, 'e123_canale_varianti.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e123 — Un messaggio nella scelta fra ch e sh?', '', 'Scelte ch/sh in ordine di lettura; nullo: rimescolamento dentro gli strati '
           '(pagina, prima riga, posizione nella riga e nella parola, segno seguente), %d volte. Preregistrazione: '
           '`preregistrazioni/e123.md`.' % PERMUTAZIONI, '',
           '| testo | occorrenze | quota sh | ' + ' | '.join('dist. %d (z)' % k for k in KK) + ' | deficit blocchi di 5 (z) |', '|---|---|---|' + '---|' * len(KK) + '---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'occorrenze' in r:
            out.append('| %s | %d | %.2f | %s | %.4f (%.1f) |' % (nome, r['occorrenze'], r['quota_sh'], ' | '.join('%+.4f (%.1f)' % (r['k%d' % k]['eccesso'], r['k%d' % k]['z'] or 0) for k in KK),
                                                            r['deficit_blocchi5']['deficit'], r['deficit_blocchi5']['z'] or 0))
    out += ['', 'Controllo valido: **%s**. Canale non escluso: **%s**. Deficit del Voynich rispetto al controllo: %.3f.' % ('sì' if valido else 'no', 'sì' if aperto else 'no', frazione)]
    with open(os.path.join(RISULTATI, 'e123_canale_varianti.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
