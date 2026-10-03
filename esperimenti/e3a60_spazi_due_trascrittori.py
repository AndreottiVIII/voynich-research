# -*- coding: utf-8 -*-
"""Esperimento e3a60: spazi della ZL contro spazi della IT (Takahashi) nelle righe con la stessa sequenza di segni;
probabilita' della regola di spaziatura (e3a58) nei punti di accordo e di disaccordo.

Preregistrazione: preregistrazioni/e3a60.md. Scrive risultati/e3a60_spazi_due_trascrittori.json e .md.
"""
import json, os, re, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def righe(quale):
    """{(pagina, numero): (segni, {posizione: separatore})}, solo righe di paragrafo con tutte le parole leggibili."""
    out = {}
    for r in trascrizione.leggi(quale):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        s = re.sub(r'<![^>]*>', '', r.grezza)
        s = s.replace('<%>', '').replace('<$>', '').replace('<->', '|').replace('<~>', '.')
        s = re.sub(r'<@[^>]*>', '', s)
        s = re.sub(r'<[^>]*>', '', s)
        s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
        s = s.replace('{', '').replace('}', '').replace("'", '')
        s = re.sub(r'@\d{3};', '*', s)
        segni, sep, prec, ok = [], {}, None, True
        for p in [p for p in re.split(r'([.,|]+)', s) if p]:
            if re.fullmatch(r'[.,|]+', p):
                prec = '|' if '|' in p else ('.' if '.' in p else ',')
                continue
            if not trascrizione.pulita(p):
                ok = False
                break
            w = list(D(p))
            if not w:
                ok = False
                break
            if segni:
                sep[len(segni)] = prec or '.'
            segni += w
            prec = None
        if ok and segni:
            out[(r.pagina, r.numero)] = (tuple(segni), sep)
    return out


def main():
    zl, it = righe('ZL'), righe('IT')
    comuni = [k for k in zl if k in it]
    uguali = [k for k in comuni if zl[k][0] == it[k][0]]
    # regola dell'e3a58 su tutta la ZL (posizioni con '.' e senza separatore)
    pos = []
    for segni, sep in zl.values():
        pos += [(segni[i - 1], segni[i], sep.get(i, '') == '.') for i in range(1, len(segni)) if sep.get(i, '') in ('.', '')]
    reg = e3a58.Regola(pos)
    tab = Counter()
    p_reg = {'accordo spazio': [], 'accordo non-spazio': [], 'disaccordo': []}
    virgole_it = 0
    for k in uguali:
        segni, sz = zl[k]
        _, si = it[k]
        for i in range(1, len(segni)):
            a, b = sz.get(i, ''), si.get(i, '')
            if a == '|' or b == '|':
                continue
            virgole_it += b == ','
            sp_it = b in ('.', ',')
            tab[a, sp_it] += 1
            if a == ',':
                continue
            p = reg.p(segni[i - 1], segni[i])
            if a == '.' and sp_it:
                p_reg['accordo spazio'].append(p)
            elif a == '' and not sp_it:
                p_reg['accordo non-spazio'].append(p)
            else:
                p_reg['disaccordo'].append(p)
    prob = OrderedDict()
    for a, nome in (('.', 'ZL spazio (.)'), (',', 'ZL spazio incerto (,)'), ('', 'ZL nessuno spazio')):
        n = tab[a, True] + tab[a, False]
        prob[nome] = OrderedDict([('punti', n), ('IT spazio', tab[a, True]), ('P(IT spazio)', tab[a, True] / n if n else None)])
    medie = OrderedDict((k, OrderedDict([('punti', len(v)), ('p_media', float(np.mean(v)) if v else None)])) for k, v in p_reg.items())
    q = prob['ZL spazio incerto (,)']['P(IT spazio)']
    es_a = 'n.d.' if q is None else ('l\'incertezza è sul foglio' if 0.25 <= q <= 0.75 else ('la virgola della ZL è uno spazio per la IT' if q > 0.75 else 'è un non-spazio per la IT'))
    md_ = medie['disaccordo']['p_media']
    es_b = 'n.d.' if md_ is None else ('i disaccordi cadono dove la regola è incerta' if 0.3 <= md_ <= 0.7 else ('i disaccordi cadono dove la regola vuole lo spazio' if md_ > 0.7 else 'i disaccordi cadono dove la regola non vuole lo spazio'))
    out = OrderedDict([('righe_comuni', len(comuni)), ('righe_con_stessi_segni', len(uguali)), ('virgole_nella_IT', virgole_it),
                       ('spazi', prob), ('regola', medie), ('esito_a', es_a), ('esito_b', es_b)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a60_spazi_due_trascrittori.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a60 — Dove la ZL ha uno spazio incerto, Takahashi mette lo spazio una volta su due?', '', 'Preregistrazione: `preregistrazioni/e3a60.md`.', '',
          'Righe di paragrafo leggibili in tutte e due: %d; con la stessa sequenza di segni: %d. Virgole nella IT in queste righe: %d.' % (len(comuni), len(uguali), virgole_it), '',
          '| punto nella ZL | punti | spazio nella IT | P(spazio nella IT) |', '|---|---|---|---|']
    md += ['| %s | %d | %d | %s |' % (k, x['punti'], x['IT spazio'], '%.3f' % x['P(IT spazio)'] if x['P(IT spazio)'] is not None else 'n.d.') for k, x in prob.items()]
    md += ['', '| punti (senza le virgole della ZL) | quanti | probabilità media della regola |', '|---|---|---|']
    md += ['| %s | %d | %s |' % (k, x['punti'], '%.3f' % x['p_media'] if x['p_media'] is not None else 'n.d.') for k, x in medie.items()]
    md += ['', 'Esito (a): **%s**. Esito (b): **%s**.' % (es_a, es_b)]
    open(os.path.join(RISULTATI, 'e3a60_spazi_due_trascrittori.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
