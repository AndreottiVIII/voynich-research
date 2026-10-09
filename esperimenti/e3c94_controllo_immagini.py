# -*- coding: utf-8 -*-
"""Esperimento e3c94: campione per il controllo sulle immagini. Parole subito dopo il salto del disegno (<-> nella ZL)
trascritte o + gallows (A, 16) e qo + gallows (B, 4, controllo positivo); ultime parole di riga in -m (C, 6). Calcola
anche la quota di qo- fra qo-/o- davanti a gallows in mezzo alla riga e dopo il salto, e la soglia
s = (p_mezzo - p_salto) / (1 - p_salto).

Preregistrazione: preregistrazioni/e3c94.md. Scrive risultati/e3c94_campione.json e .md.
"""
import json, os, random, re, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
IMMAGINI = os.path.join(QUI, '..', 'dati', 'immagini.json')
D = misure.divisore(misure.GLIFI_EVA)
GALLOWS = {'k', 't', 'p', 'f', 'ckh', 'cth', 'cph', 'cfh'}
QUANTI = OrderedDict([('A', 16), ('B', 4), ('C', 6)])


def righe():
    """[(pagina, numero, testo leggibile, parole, separatori)], come e386.righe ma con le parole come stringhe."""
    out = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] != trascrizione.PARAGRAFO:
            continue
        s = re.sub(r'<![^>]*>', '', r.grezza)
        s = s.replace('<%>', '').replace('<$>', '').replace('<->', '|').replace('<~>', '.')
        s = re.sub(r'<@[^>]*>', '', s)
        s = re.sub(r'<[^>]*>', '', s)
        s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
        s = s.replace('{', '').replace('}', '').replace("'", '')
        s = re.sub(r'@\d{3};', '*', s)
        ws, seps, prec = [], [], None
        for p in [p for p in re.split(r'([.,|]+)', s) if p]:
            if re.fullmatch(r'[.,|]+', p):
                prec = '|' if '|' in p else ('.' if '.' in p else ',')
                continue
            ws.append(p if trascrizione.pulita(p) else None)
            if len(ws) > 1:
                seps.append(prec or '.')
            prec = None
        if ws:
            out.append((r.pagina, r.numero, s, ws, seps))
    return out


def tipo(w):
    """'qo' o 'o' se la parola è qo/o + gallows, altrimenti None."""
    if w is None:
        return None
    g = D(w)
    if len(g) >= 3 and g[0] == 'q' and g[1] == 'o' and g[2] in GALLOWS:
        return 'qo'
    if len(g) >= 2 and g[0] == 'o' and g[1] in GALLOWS:
        return 'o'
    return None


def main():
    rnd = random.Random(3394)
    imm = json.load(open(IMMAGINI, encoding='utf-8'))
    conta = {'mezzo': {'qo': 0, 'o': 0}, 'salto': {'qo': 0, 'o': 0}}
    cand = {'A': [], 'B': [], 'C': []}
    for pag, num, testo, ws, seps in righe():
        for i, w in enumerate(ws):
            t = tipo(w)
            voce = OrderedDict([('pagina', pag), ('riga', num), ('parola', i + 1), ('di', len(ws)), ('testo_parola', w), ('riga_trascritta', testo)])
            if i > 0 and seps[i - 1] == '|':
                if t:
                    conta['salto'][t] += 1
                    cand['A' if t == 'o' else 'B'].append(voce)
            elif i > 0 and i < len(ws) - 1 and seps[i - 1] == '.' and t:
                conta['mezzo'][t] += 1
        if ws[-1] and ws[-1].endswith('m'):
            cand['C'].append(OrderedDict([('pagina', pag), ('riga', num), ('parola', len(ws)), ('di', len(ws)), ('testo_parola', ws[-1]), ('riga_trascritta', testo)]))
    p_mezzo = conta['mezzo']['qo'] / (conta['mezzo']['qo'] + conta['mezzo']['o'])
    p_salto = conta['salto']['qo'] / (conta['salto']['qo'] + conta['salto']['o'])
    soglia = (p_mezzo - p_salto) / (1 - p_salto)
    campione = OrderedDict()
    saltate = []
    for gruppo, n in QUANTI.items():
        ordine = rnd.sample(cand[gruppo], len(cand[gruppo]))
        presi = []
        for v in ordine:
            if len(presi) == n:
                break
            chiave = v['pagina'][1:]
            if chiave not in imm:
                saltate.append('%s %s.%s' % (gruppo, v['pagina'], v['riga']))
                continue
            v['immagine'] = imm[chiave]['file']
            v['iiif_id'] = imm[chiave]['url'].split('/iiif/2/')[1].split('/')[0]
            v['id'] = '%s%02d' % (gruppo, len(presi) + 1)
            presi.append(v)
        campione[gruppo] = presi
    out = OrderedDict([('conteggi', conta), ('p_mezzo', p_mezzo), ('p_salto', p_salto), ('soglia', soglia),
                       ('candidati', {g: len(c) for g, c in cand.items()}), ('saltate_senza_immagine', saltate), ('campione', campione)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c94_campione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c94 — Campione per il controllo sulle immagini', '',
          'Preregistrazione: `preregistrazioni/e3c94.md`. ZL, testo dei paragrafi, seme 3394.', '',
          'Quota di *qo-* fra *qo-*/*o-* davanti a gallows: in mezzo alla riga %.3f (%d parole), dopo il salto del disegno %.3f (%d parole). '
          'Soglia s = %.3f.' % (p_mezzo, sum(conta['mezzo'].values()), p_salto, sum(conta['salto'].values()), soglia), '',
          'Candidati: A %d, B %d, C %d. Saltate perché la pagina non ha un\'immagine singola: %s.' % (
              len(cand['A']), len(cand['B']), len(cand['C']), ', '.join(saltate) or 'nessuna'), '',
          '| id | pagina.riga | parola | trascrizione della riga (| = salto del disegno) |', '|---|---|---|---|']
    for g, vv in campione.items():
        for v in vv:
            md.append('| %s | %s.%s | %d di %d: *%s* | `%s` |' % (v['id'], v['pagina'], v['riga'], v['parola'], v['di'], v['testo_parola'], v['riga_trascritta']))
    open(os.path.join(RISULTATI, 'e3c94_campione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('p_mezzo %.3f p_salto %.3f soglia %.3f; candidati %s; saltate %s' % (p_mezzo, p_salto, soglia, {g: len(c) for g, c in cand.items()}, saltate))


if __name__ == '__main__':
    main()
