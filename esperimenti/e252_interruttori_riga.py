# -*- coding: utf-8 -*-
"""Esperimento 252 (passo 3 del piano 18/18): il generatore dell'e251 (gamma scelto li') con i 12 interruttori di riga
dell'e206b (stato con memoria AR(1) e ripartenza a pagina; ogni parola che ha una forma lunga/corta attestata si riscrive
secondo lo stato della riga). Verifica: l'e206b sull'uscita, pagella, discriminatore.

Preregistrazione: preregistrazioni/e252.md. Scrive risultati/e252_interruttori_riga.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e206_segni_facoltativi as e206
import e237_riuso_pagina as e237
import e243_riuso_esplicito as e243
import e251_lessico_sezione as e251

RISULTATI = os.path.join(QUI, '..', 'risultati')
RIMESCOLAMENTI, SEME_TEST = 100, 2521


def test_classi(rr, classi):
    """Come l'e206b sul testo dato (righe (pagina, inizio, parole)), con RIMESCOLAMENTI rimescolamenti: z per classe."""
    rnd = random.Random(SEME_TEST)
    righe = [(p, ini, [w for w in ps if trascrizione.pulita(w)]) for p, ini, ps in rr]
    freq = Counter(w for _, _, ps in righe for w in ps)
    cl = e206.classi_di(freq)
    occ = defaultdict(list)
    for k, (pag, ini, ps) in enumerate(righe):
        for j, w in enumerate(ps):
            pos = 0 if j == 0 else (2 if j == len(ps) - 1 else 1)
            for c, v in cl.get(w, {}).items():
                nome = '%s %s' % c
                if nome in classi:
                    occ[nome].append(((pag, ini, pos), k, v))
    out = OrderedDict()
    for nome in classi:
        oo = occ.get(nome, [])
        if len(oo) < 100:
            out[nome] = None
            continue
        per_riga = defaultdict(list)
        for _, k, v in oo:
            per_riga[k].append(v)
        vero = e206.accordo(per_riga)
        strati = defaultdict(list)
        for i, (s, _, _) in enumerate(oo):
            strati[s].append(i)
        nulli = []
        for _ in range(RIMESCOLAMENTI):
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
        sd = statistics.pstdev(nulli)
        out[nome] = (vero - statistics.mean(nulli)) / sd if sd else None
    return out


def main():
    c, c2, freq, vpag, rif, pv = e251.contesto()
    bersaglio = e237.profilo(pv)
    dist = e243.distanze_voynich(pv)
    j251 = json.load(open(os.path.join(RISULTATI, 'e251_lessico_sezione.json'), encoding='utf-8'))
    gamma = j251['gamma']
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    inter = e251.interruttori_voynich(classi)
    print('tassi di forma lunga: %s' % {k: round(v, 3) for k, v in inter[0].items()}, flush=True)
    quote, storia = e251.tara(c2, dist, freq, bersaglio, gamma=gamma, interruttori=inter)
    ver = e251.verifica(c, c2, vpag, rif, freq, quote, dist, gamma=gamma, interruttori=inter)
    z = test_classi(ver[0]['righe'], classi)
    ritrovate = [k for k, v in z.items() if (v or 0) > 3]
    print('classi ritrovate (z > 3) sul seme %d: %d su %d: %s' % (e251.SEMI_VERIFICA[0], len(ritrovate), len(classi), {k: (round(v, 1) if v is not None else None) for k, v in z.items()}), flush=True)
    pag = statistics.mean(x['pagella_e224']['pagella'] for x in ver)
    auc = statistics.mean(x['AUC'] for x in ver)
    R = statistics.mean(x['R_parole_rare'] for x in ver)
    esito = 'passo superato' if len(ritrovate) >= 10 and pag >= j251['pagella_media'] else 'non superato'
    for x in ver:
        x.pop('righe', None)
    ris = OrderedDict([('gamma', gamma), ('tassi', inter[0]), ('quote', quote), ('taratura', storia), ('verifica', ver), ('classi_z_seme_7', z),
                       ('classi_ritrovate', ritrovate), ('pagella_media', pag), ('pagella_e251', j251['pagella_media']), ('AUC_media', auc),
                       ('R_parole_rare_media', R), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e252_interruttori_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e252 — Passo 3 del piano 18/18: dodici interruttori di riga', '',
          "Generatore dell'e251 (γ %.1f) con le 12 classi dell'e206b come interruttori di riga (memoria AR(1), ripartenza a pagina). Preregistrazione: "
          '`preregistrazioni/e252.md`.' % gamma, '', '| seme | AUC | pagella | riga | mancano | R parole rare |', '|---|---|---|---|---|---|']
    for s, x in zip(e251.SEMI_VERIFICA, ver):
        md.append('| %d | %.3f | %d/18 | %s | %s | %.1f |' % (s, x['AUC'], x['pagella_e224']['pagella'], 'sì' if x['pagella_e224']['riga'] else 'no',
                                                         ', '.join(x['pagella_e224']['mancano']) or '—', x['R_parole_rare']))
    md += ['', 'Classi dell\'e206b ritrovate con z > 3 (seme 7): %d su %d (%s).' % (len(ritrovate), len(classi), ', '.join(ritrovate) or 'nessuna'),
           '', 'z per classe: %s.' % ', '.join('%s %s' % (k, '%.1f' % v if v is not None else '–') for k, v in z.items()), '',
           'Medie: pagella %.1f/18 (e251: %.1f), AUC %.3f, R parole rare %.1f.' % (pag, j251['pagella_media'], auc, R), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e252_interruttori_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
