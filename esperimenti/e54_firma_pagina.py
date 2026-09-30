# -*- coding: utf-8 -*-
"""Esperimento 54 (diagnosi esplorativa, non preregistrata): quali segni portano l'informazione
sulla pagina, posizione per posizione, nel Voynich e nei generatori?

Nel Voynich il profilo e' piatto (e36: R ~ 1); nel generatore di Timm e Schinner e nel modello
dell'e53 si concentra verso la fine della parola (R ~ 0,74) ed e' piu' forte. Si scompone
l'informazione mutua pagina/segno in contributi per segno (p(g) * KL(p(pagina|g) || p(pagina)),
come nell'e37), per le posizioni primo, secondo, penultimo, ultimo. Pagine del Voynich con almeno
40 parole utili; generatori con pagine di 29 righe. Parole di almeno 4 segni, senza la prima e
l'ultima parola della riga (D-006).

Scrive risultati/e54_firma_pagina.json e .md.
"""
import json, math, os, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import posizioni
import e22_timm_schinner as e22
import e36_posizione_pagina as e36

RISULTATI = os.path.join(QUI, '..', 'risultati')
MODELLO = os.path.join(e22.LAVORO, 'recenza_novita', 'e53_finali_0_seme_19', 'generate', 'generated_text.txt')


def contributi(blocchi, pos):
    coppie = [(b.gruppo, w[pos]) for b in blocchi for w in b.parole if len(w) >= 4]
    n = len(coppie)
    pg, ps, pj = Counter(g for _, g in coppie), Counter(s for s, _ in coppie), Counter(coppie)
    out = {}
    for g, cg in pg.items():
        kl = sum(c / cg * math.log2((c / cg) / (ps[s] / n)) for (s, gg), c in pj.items() if gg == g)
        out[g] = {'frequenza': cg / n, 'contributo': cg / n * kl}
    tot = sum(v['contributo'] for v in out.values())
    for v in out.values():
        v['frazione'] = v['contributo'] / tot
    return tot, dict(sorted(out.items(), key=lambda kv: -kv[1]['contributo']))


def pagine_da_file(percorso):
    linee = [l.split() for l in open(percorso, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    return [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]


def main():
    testi = OrderedDict()
    voy = e36.blocchi_voynich()
    testi['Voynich'] = [posizioni.Blocco(b.gruppo, 0, b.grappolo, b.parole) for b in voy]
    testi['Timm e Schinner (seme 19)'] = e36.blocchi_da_pagine(e22.genera(19), e36.DIVIDI)
    if os.path.exists(MODELLO):
        testi['modello e53 (finali spente, seme 19, senza scissione)'] = e36.blocchi_da_pagine(pagine_da_file(MODELLO), e36.DIVIDI)
    ris = OrderedDict()
    righe = ['# e54 — Quali segni portano la firma di pagina (diagnosi esplorativa)', '',
             'Informazione mutua pagina/segno (non corretta per il caso) e contributo dei segni principali, per '
             'posizione. Non preregistrato.', '']
    for nome, blocchi in testi.items():
        ris[nome] = {}
        righe += ['## %s' % nome, '', '| posizione | informazione (bit) | segni principali: frazione (frequenza) |', '|---|---|---|']
        for pnome, pos in posizioni.POSIZIONI.items():
            tot, c = contributi(blocchi, pos)
            ris[nome][pnome] = {'informazione': tot, 'segni': c}
            righe.append('| %s | %.3f | %s |' % (pnome, tot, '; '.join(
                '%s %.2f (%.2f)' % (g, v['frazione'], v['frequenza']) for g, v in list(c.items())[:6])))
        righe.append('')
    print('\n'.join(righe))
    with open(os.path.join(RISULTATI, 'e54_firma_pagina.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    with open(os.path.join(RISULTATI, 'e54_firma_pagina.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
