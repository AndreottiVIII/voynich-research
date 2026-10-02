# -*- coding: utf-8 -*-
"""Esperimento 206b: come l'e206 (segni "facoltativi" concordi dentro la riga), con il nullo che rimescola dentro gli
strati pagina x prima riga di paragrafo x posizione della parola nella riga.

Preregistrazione: preregistrazioni/e206b.md. Scrive risultati/e206b_facoltativi_strati.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e206_segni_facoltativi as e206

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME = 2061
# classi di segno tolto che corrispondono a scelte note: q iniziale = qo-/o- (F5), d interna = -dy/-ey (F7, chedy -> chey);
# F1 ch/sh, F2 k/t e F3 -l/-r sono sostituzioni, non segni tolti, e non hanno una classe qui
NOTE = {'q iniziale', 'd interna'}


def main():
    rnd = random.Random(SEME)
    righe = []
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if r.parole:
            righe.append((r.pagina, bool(r.inizio_par), ps))
    freq = Counter(w for _, _, ps in righe for w in ps)
    cl = e206.classi_di(freq)
    occ = defaultdict(list)    # classe -> [(strato, riga, valore)]
    for k, (pag, ini, ps) in enumerate(righe):
        n = len(ps)
        for j, w in enumerate(ps):
            pos = 0 if j == 0 else (2 if j == n - 1 else 1)
            for c, v in cl.get(w, {}).items():
                occ[c].append(((pag, ini, pos), k, v))
    precedente = json.load(open(os.path.join(RISULTATI, 'e206_segni_facoltativi.json'), encoding='utf-8'))['classi']
    ris = OrderedDict()
    for c, oo in sorted(occ.items(), key=lambda kv: -len(kv[1])):
        if len(oo) < e206.MIN_OCC:
            continue
        per_riga = defaultdict(list)
        for _, k, v in oo:
            per_riga[k].append(v)
        vero = e206.accordo(per_riga)
        strati = defaultdict(list)
        for i, (s, _, _) in enumerate(oo):
            strati[s].append(i)
        nulli = []
        for _ in range(e206.RIMESCOLAMENTI):
            vals = [v for _, _, v in oo]
            for idx in strati.values():
                x = [vals[i] for i in idx]
                rnd.shuffle(x)
                for i, y in zip(idx, x):
                    vals[i] = y
            pr = defaultdict(list)
            for (_, k, _), v in zip(oo, vals):
                pr[k].append(v)
            nulli.append(e206.accordo(pr))
        m, s = statistics.mean(nulli), statistics.pstdev(nulli)
        z = (vero - m) / s if s else None
        nome = '%s %s' % c
        ris[nome] = OrderedDict([('occorrenze', len(oo)), ('accordo', vero), ('nullo', m), ('z', z),
                                 ('z_e206', precedente.get(nome, {}).get('z'))])
        print('%-16s occ %5d | accordo %.4f nullo %.4f z %.1f (e206 %s)' % (nome, len(oo), vero or 0, m, z or 0,
                                                                         '%.1f' % ris[nome]['z_e206'] if ris[nome]['z_e206'] is not None else '-'), flush=True)
    controllo = ris.get('q iniziale', {}).get('z') or 0
    valido = controllo > 3
    di_riga = [n for n, r in ris.items() if (r['z'] or 0) > 3]
    cadute = [n for n, r in ris.items() if (r['z_e206'] or 0) > 3 and (r['z'] or 0) <= 3]
    nuove = [n for n in di_riga if n not in NOTE]
    out = OrderedDict([('classi', ris), ('controllo_q_iniziale_z', controllo), ('valido', valido), ('scelte_di_riga', di_riga),
                       ('cadute_rispetto_e206', cadute), ('nuove_rispetto_alle_cinque', nuove)])
    json.dump(out, open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e206b — Segni facoltativi decisi per riga, nullo stratificato', '',
          'Accordo dentro la riga fra forme lunghe e corte, contro il rimescolamento dentro pagina × prima riga di paragrafo × posizione '
          'della parola. Preregistrazione: `preregistrazioni/e206b.md`.', '',
          '| classe | occorrenze | accordo | nullo | z | z nell\'e206 |', '|---|---|---|---|---|---|']
    md += ['| %s | %d | %.4f | %.4f | %.1f | %s |' % (n, r['occorrenze'], r['accordo'] or 0, r['nullo'], r['z'] or 0,
                                                    '%.1f' % r['z_e206'] if r['z_e206'] is not None else '–') for n, r in ris.items()]
    md += ['', 'Controllo (q iniziale = qo-/o-): z %.1f, valido **%s**.' % (controllo, 'sì' if valido else 'no'), '',
           '- Classi decise per riga (z > 3): %s.' % (', '.join(di_riga) or 'nessuna'),
           '- Cadute rispetto all\'e206: %s.' % (', '.join(cadute) or 'nessuna'),
           '- Nuove rispetto alle cinque scelte note: %s.' % (', '.join(nuove) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
