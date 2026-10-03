# -*- coding: utf-8 -*-
"""Esperimento e3a36: quota dell'incertezza su qo-/o- e -l/-r tolta dal contesto trovato (posto, segno vicino, riga sopra,
lingua), con modello a tabella addestrato su meta' delle pagine e valutato sull'altra.

Preregistrazione: preregistrazioni/e3a36.md. Scrive risultati/e3a36_prevedibili.json e .md.
"""
import json, math, os, re, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e380_sandhi as e380

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
V, C = {'y', 'o', 'd'}, {'n', 'r', 's', 'm'}


def parse(r):
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
    return ws, seps


def classe_fin(s):
    return 'V' if s in V else ('C' if s in C else 'X')


def classe_ini(s):
    return 'a' if s == 'a' else ('oy' if s in ('o', 'y') else ('K' if s in ('k', 't', 'd', 'l', 's', 'q') else 'X'))


def eventi():
    qo, lr = [], []    # (pagina, contesto dict, esito)
    prec_inizio = {}
    npar = 0
    ultima_riga = None
    pagina_prec = None
    for r in trascrizione.leggi('ZL'):
        t = r.tipo[0]
        ws, seps = parse(r)
        lg = r.lingua or '-'
        if t == trascrizione.PARAGRAFO:
            if r.inizio_par or r.pagina != pagina_prec:
                npar += 1
                ultima_riga = None
            pagina_prec = r.pagina
        n = len(ws)
        for j, w in enumerate(ws):
            if not w:
                continue
            q = e380.ini_qo(w)
            if q:
                if t in ('C', 'R'):
                    ctx = {'posto': 'cerchio', 'prima': '-', 'sopra': '-'}
                elif t == trascrizione.ETICHETTA:
                    ctx = {'posto': 'etichetta', 'prima': '-', 'sopra': '-'}
                elif j == 0:
                    sopra = '-' if ultima_riga is None or ultima_riga[1] else ('qo' if ultima_riga[0] else 'no')
                    ctx = {'posto': 'inizio riga', 'prima': '-', 'sopra': sopra}
                elif seps[j - 1] == '|':
                    ctx = {'posto': 'dopo disegno', 'prima': '-', 'sopra': '-'}
                else:
                    a = ws[j - 1]
                    ctx = {'posto': 'mezzo', 'prima': classe_fin(a[-1]) if a else 'X', 'sopra': '-'}
                ctx['lingua'] = lg
                qo.append((r.pagina, ctx, q[1] == 'qo'))
            f = e380.fin_lr(w)
            if f:
                if t in ('C', 'R'):
                    ctx = {'posto': 'cerchio', 'dopo': '-'}
                elif t == trascrizione.ETICHETTA:
                    ctx = {'posto': 'etichetta', 'dopo': '-'}
                elif j == n - 1:
                    ctx = {'posto': 'fine riga', 'dopo': '-'}
                elif seps[j] == '|':
                    ctx = {'posto': 'prima del disegno', 'dopo': '-'}
                else:
                    b = ws[j + 1]
                    ctx = {'posto': 'mezzo', 'dopo': classe_ini(b[0]) if b else 'X'}
                ctx['lingua'] = lg
                lr.append((r.pagina, ctx, f[1] == 'l'))
        if t == trascrizione.PARAGRAFO and ws and ws[0]:
            ultima_riga = (ws[0][:2] == ('q', 'o'), ultima_riga is None)
    return qo, lr


def valuta(ev, chiavi):
    pagine = sorted({p for p, _, _ in ev})
    meta = {p: i % 2 for i, p in enumerate(pagine)}
    hc = hb = 0.0
    ok = okb = n = 0
    for prova in (0, 1):
        tab = defaultdict(lambda: [1, 1])
        base = [1, 1]
        for p, ctx, y in ev:
            if meta[p] != prova:
                tab[tuple(ctx[k] for k in chiavi)][y] += 1
                base[y] += 1
        pb = base[1] / sum(base)
        for p, ctx, y in ev:
            if meta[p] == prova:
                c = tab[tuple(ctx[k] for k in chiavi)]
                pc = c[1] / sum(c)
                hc -= math.log2(pc if y else 1 - pc)
                hb -= math.log2(pb if y else 1 - pb)
                ok += (pc >= 0.5) == y
                okb += (pb >= 0.5) == y
                n += 1
    return OrderedDict([('eventi', n), ('quota_incertezza_tolta', 1 - hc / hb), ('accuratezza', ok / n), ('accuratezza_base', okb / n)])


def main():
    qo, lr = eventi()
    ris = OrderedDict()
    for nome, ev, chiavi in (('qo-/o-', qo, ['posto', 'prima', 'sopra', 'lingua']), ('-l/-r', lr, ['posto', 'dopo', 'lingua'])):
        x = OrderedDict([('tutto il contesto', valuta(ev, chiavi))])
        for k in chiavi:
            x['senza %s' % k] = valuta(ev, [c for c in chiavi if c != k])
        x['frequenze per posto'] = OrderedDict((p, OrderedDict([('eventi', n), ('quota', sum(y for _, c, y in ev if c['posto'] == p) / n)])) for p, n in Counter(c['posto'] for _, c, _ in ev).most_common())
        ris[nome] = x
        print(nome, json.dumps(x, ensure_ascii=False, default=float), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3a36_prevedibili.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3a36 — Quanto sono prevedibili qo-/o- e -l/-r dal contesto trovato?', '', 'Preregistrazione: `preregistrazioni/e3a36.md`. Modello a tabella, pagine pari contro dispari.', '']
    for nome, x in ris.items():
        md += ['## %s' % nome, '', '| contesto | eventi | incertezza tolta | accuratezza | accuratezza della scelta più frequente |', '|---|---|---|---|---|']
        for k, v in x.items():
            if k != 'frequenze per posto':
                md.append('| %s | %d | %.1f%% | %.1f%% | %.1f%% |' % (k, v['eventi'], 100 * v['quota_incertezza_tolta'], 100 * v['accuratezza'], 100 * v['accuratezza_base']))
        md += ['', 'Quota di %s per posto: %s.' % ('qo' if nome == 'qo-/o-' else '-l', '; '.join('%s %.2f (%d)' % (p, v['quota'], v['eventi']) for p, v in x['frequenze per posto'].items())), '']
    open(os.path.join(RISULTATI, 'e3a36_prevedibili.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
