# -*- coding: utf-8 -*-
"""Esperimento 391: la giuntura (ultimo -> primo segno) e la regola di qo- nei testi in cerchio e lungo i raggi,
confrontati con i paragrafi a parita' di coppie.

Preregistrazione: preregistrazioni/e391.md. Scrive risultati/e391_cerchi.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e377_giuntura_gibberish as e377
import e380_sandhi as e380
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}


def coppie_tipo(tipi):
    out = []
    for r in trascrizione.leggi('ZL'):
        if r.tipo[0] not in tipi:
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
            ws.append(tuple(D(p)) if trascrizione.pulita(p) else None)
            if len(ws) > 1:
                seps.append(prec or '.')
            prec = None
        for j in range(len(ws) - 1):
            if ws[j] and ws[j + 1] and seps[j] == '.':
                out.append((r.sezione or '?', ws[j], ws[j + 1]))
    return out


def main():
    rnd = random.Random(391)
    cerchi = coppie_tipo(('C', 'R'))
    par = []
    for st, pag, p, ws, seps in e386.righe():
        for j in range(len(ws) - 1):
            if ws[j] and ws[j + 1] and seps[j] == '.':
                par.append((st.split('-')[0], ws[j], ws[j + 1]))
    giunt = lambda cc: [(s, a[-1], b[0]) for s, a, b in cc]
    Ec = e386.prova(giunt(cerchi), rnd, 1000)
    n = len(cerchi)
    sub = [e386.prova(giunt(rnd.sample(par, n)), rnd, 200)['E'] for _ in range(20)]
    Ep = statistics.median(sub)
    Q = Ec['E'] / Ep if Ep > 0 else None
    # regola di qo-
    ev = []
    for s, a, b in cerchi:
        x = e380.ini_qo(b)
        if x and (a[-1] in V or a[-1] in C):
            ev.append((a[-1] in V, x[1] == 'qo'))

    def diff(e):
        v = [q for c, q in e if c]
        c = [q for cl, q in e if not cl]
        return (sum(v) / len(v) - sum(c) / len(c)) if v and c else 0.0
    d = diff(ev)
    classi = [c for c, _ in ev]
    esiti_q = [q for _, q in ev]
    nul = []
    for _ in range(10000):
        rnd.shuffle(classi)
        nul.append(diff(list(zip(classi, esiti_q))))
    p = sum(x >= d for x in nul) / len(nul)
    nv = sum(1 for c, _ in ev if c)
    if Ec['z'] > 3 and Q is not None and Q > 0.5:
        esito = 'la giuntura c\'è anche nei cerchi'
    elif Ec['z'] < 2:
        esito = 'non c\'è'
    else:
        esito = 'incerto'
    esito_q = 'la regola di qo- vale anche nei cerchi' if p < 0.01 and d > 0 else 'non dimostrata nei cerchi'
    out = OrderedDict([('coppie_cerchi_raggi', n), ('per_sezione', dict(Counter(s for s, _, _ in cerchi))), ('E_cerchi', Ec), ('E_paragrafi_a_parita', Ep), ('Q', Q),
                       ('qo', OrderedDict([('eventi', len(ev)), ('dopo_y_o_d', nv), ('differenza', d), ('p', p)])), ('esito', esito), ('esito_qo', esito_q)])
    print(json.dumps(out, ensure_ascii=False, default=float), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e391_cerchi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e391 — La giuntura nei testi scritti in cerchio e lungo i raggi', '', 'Preregistrazione: `preregistrazioni/e391.md`.', '',
          'Coppie nei cerchi e raggi: %d (%s). Giuntura: E %.4f, z %.1f. Paragrafi a parità di coppie: E %.4f. Q = %s.' % (
              n, ', '.join('%s %d' % kv for kv in out['per_sezione'].items()), Ec['E'], Ec['z'], Ep, '%.2f' % Q if Q is not None else 'n.d.'), '',
          'Regola di *qo*- nei cerchi e raggi: %d eventi (%d dopo -y/-o/-d); differenza %+.3f, p %.4f.' % (len(ev), nv, d, p), '',
          'Esito: **%s**; **%s**.' % (esito, esito_q)]
    open(os.path.join(RISULTATI, 'e391_cerchi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
