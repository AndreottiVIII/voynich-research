# -*- coding: utf-8 -*-
"""Esperimento 386: la giuntura (ultimo segno -> primo segno della parola seguente) attraverso il salto del disegno
(<-> nella ZL), confrontata con lo spazio normale, lo spazio incerto e l'a capo, a parita' di numero di coppie.

Preregistrazione: preregistrazioni/e386.md. Scrive risultati/e386_salto_disegno.json e .md.
"""
import json, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e377_giuntura_gibberish as e377

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def righe():
    """[(strato, pagina, paragrafo, parole, separatori)]: separatori '.', ',', '|' (salto del disegno)."""
    out = []
    npar = 0
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
            ws.append(tuple(D(p)) if trascrizione.pulita(p) else None)
            if len(ws) > 1:
                seps.append(prec or '.')
            prec = None
        if r.inizio_par:
            npar += 1
        if ws:
            out.append(('%s-%s' % (r.sezione or '?', r.lingua or '?'), r.pagina, npar, ws, seps))
    return out


def prova(coppie, rnd, perm):
    """coppie: [(strato, ultimo, primo)]; nullo: primi rimescolati nello strato."""
    vero = e377.mi(Counter((a, b) for _, a, b in coppie))
    per = defaultdict(list)
    for st, a, b in coppie:
        per[st].append((a, b))
    nul = []
    for _ in range(perm):
        c = Counter()
        for xs in per.values():
            dx = [b for _, b in xs]
            rnd.shuffle(dx)
            c.update((a, b) for (a, _), b in zip(xs, dx))
        nul.append(e377.mi(c))
    m, sd = statistics.mean(nul), statistics.pstdev(nul)
    return OrderedDict([('coppie', len(coppie)), ('E', vero - m), ('z', (vero - m) / sd if sd else 0.0)])


def main():
    rnd = random.Random(386)
    rr = righe()
    tipi = {'|': [], '.': [], ',': []}
    capo = []
    for k, (st, pag, par, ws, seps) in enumerate(rr):
        for j in range(len(ws) - 1):
            if ws[j] and ws[j + 1]:
                tipi[seps[j]].append((st, ws[j][-1], ws[j + 1][0]))
        if k + 1 < len(rr):
            st2, pag2, par2, ws2, _ = rr[k + 1]
            if pag2 == pag and par2 == par and ws[-1] and ws2[0]:
                capo.append((st, ws[-1][-1], ws2[0][0]))
    ris = OrderedDict()
    for nome, chiave in (('salto del disegno', '|'), ('spazio normale', '.'), ('spazio incerto', ',')):
        ris[nome] = prova(tipi[chiave], rnd, 1000)
        print(nome, json.dumps(ris[nome], default=float), flush=True)
    ris['a capo'] = prova(capo, rnd, 1000)
    print('a capo', json.dumps(ris['a capo'], default=float), flush=True)
    n = len(tipi['|'])
    pari = OrderedDict()
    for nome, cc in (('spazio normale', tipi['.']), ('a capo', capo)):
        pari[nome] = statistics.median(prova(rnd.sample(cc, n), rnd, 200)['E'] for _ in range(20))
    Q = ris['salto del disegno']['E'] / pari['spazio normale'] if pari['spazio normale'] > 0 else None
    z = ris['salto del disegno']['z']
    if z > 3 and Q is not None and Q > 0.5:
        esito = 'la giuntura attraversa il disegno: vale per la riga, non per il gesto'
    elif z < 2:
        esito = 'si rompe anche al disegno: dipende dal gesto continuo'
    else:
        esito = 'incerto'
    out = OrderedDict([('tipi', ris), ('E_a_parita_di_coppie', pari), ('Q_salto', Q), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e386_salto_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e386 — La giuntura attraversa il salto del disegno?', '', 'Preregistrazione: `preregistrazioni/e386.md`.', '', '| coppie | quante | E | z |', '|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.4f | %.1f |' % (k, x['coppie'], x['E'], x['z']))
    md += ['', 'A parità di coppie (%d, mediana di 20 sottoinsiemi): spazio normale E %.4f, a capo E %.4f. Q_salto = %s.' % (
        n, pari['spazio normale'], pari['a capo'], '%.2f' % Q if Q is not None else 'n.d.'), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e386_salto_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
