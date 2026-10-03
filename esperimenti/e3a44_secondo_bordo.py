# -*- coding: utf-8 -*-
"""Esperimento e3a44: inizi uguali fra le parole che ripartono dopo un salto del disegno in righe consecutive (secondo
bordo sinistro), contro il rimescolamento fra le righe con salto della pagina; controllo con il margine vero.

Preregistrazione: preregistrazioni/e3a44.md. Scrive risultati/e3a44_secondo_bordo.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386

RISULTATI = os.path.join(QUI, '..', 'risultati')


def main():
    rnd = random.Random(3144)
    rr = e386.righe()
    righe = []    # (pagina, paragrafo, parola dopo il salto, prima parola)
    for st, pag, npar, ws, seps in rr:
        if '|' in seps:
            j = seps.index('|') + 1
            dopo = ws[j] if j < len(ws) else None
            righe.append((pag, npar, dopo, ws[0]))
        else:
            righe.append((pag, npar, None, None))
    coppie = []    # (pagina, indice riga sopra, indice riga sotto)
    for i in range(1, len(righe)):
        a, b = righe[i - 1], righe[i]
        if a[0] == b[0] and a[1] == b[1] and a[2] is not None and b[2] is not None:
            coppie.append((b[0], i - 1, i))
    per_pag = defaultdict(list)
    for i, r in enumerate(righe):
        if r[2] is not None:
            per_pag[r[0]].append(i)

    def quota(campo, assegna):
        s = t = 0
        for pag, i, j in coppie:
            a, b = assegna(i, campo), assegna(j, campo)
            if a and b and len(a) >= 2 and len(b) >= 2:
                t += 1
                s += a[:2] == b[:2]
        return s / t if t else 0.0, t
    ris = OrderedDict()
    for nome, campo in (('secondo bordo (dopo il disegno)', 2), ('margine vero (controllo)', 3)):
        vero, t = quota(campo, lambda i, c: righe[i][c])
        nul = []
        for _ in range(2000):
            perm = {}
            for pag, idx in per_pag.items():
                sh = rnd.sample(idx, len(idx))
                perm.update(zip(idx, sh))
            nul.append(quota(campo, lambda i, c: righe[perm.get(i, i)][c])[0])
        m, sd = statistics.mean(nul), statistics.pstdev(nul)
        ris[nome] = OrderedDict([('coppie', t), ('osservata', vero), ('nullo', m), ('rapporto', vero / m if m else None), ('z', (vero - m) / sd if sd else 0.0)])
        print(nome, json.dumps(ris[nome], ensure_ascii=False), flush=True)
    s, c = ris['secondo bordo (dopo il disegno)'], ris['margine vero (controllo)']
    if s['coppie'] < 100:
        esito = 'non deciso (pochi dati)'
    elif s['rapporto'] is not None and s['rapporto'] < 0.8 and s['z'] < -2.5:
        esito = 'evitato anche sul secondo bordo'
    elif abs(s['z']) < 2 and c['z'] < -2.5:
        esito = 'solo sul margine vero'
    else:
        esito = 'non deciso'
    out = OrderedDict([('misure', ris), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3a44_secondo_bordo.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a44 — L\'evitamento del margine sinistro vale anche dopo il disegno?', '', 'Preregistrazione: `preregistrazioni/e3a44.md`. Coppie di righe consecutive dello stesso paragrafo, entrambe con un salto del disegno.', '',
          '| bordo | coppie | osservata | nullo | rapporto | z |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %.3f | %.3f | %s | %.1f |' % (k, x['coppie'], x['osservata'], x['nullo'], '%.2f' % x['rapporto'] if x['rapporto'] else '', x['z']) for k, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a44_secondo_bordo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
