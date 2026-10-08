# -*- coding: utf-8 -*-
"""Esperimento 419: sulla v21, libri con messaggio contro libri senza (soli bit di riempimento), 24 chiavi.
1. Contro il Voynich: dai risultati dell'e409 (caso a: file v21f1; caso b: VERSIONE=v21 CASI=b), differenza appaiata.
2. Diretto: classificatore (caratteristiche dell'e266, regressione logistica dell'e231) con messaggio contro senza,
   pieghe per chiave; AUC complessiva e per gruppo. 3. Controllo negativo: chiavi dispari contro pari sui libri senza.

    PROCESSI=8 python esegui.py e419          (dopo le corse dell'e409: v21f1 caso a e v21 caso b, chiavi 1-12 e 13-24)
    python esperimenti/e419_con_senza_messaggio.py --prova     (2 chiavi, solo il classificatore diretto)

Preregistrazione: preregistrazioni/e419.md. Scrive risultati/e419_con_senza_messaggio.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))

RISULTATI = os.path.join(QUI, '..', 'risultati')
TESTO = os.path.join(QUI, '..', 'esecuzioni', 'voynichizzatore', 'isidoro_xvii_inizio.txt')
VERSIONE, CHIAVI = 'v21', tuple(range(1, 25))
NOME = 'e419_con_senza_messaggio'
E409 = {'a': 'e409b_messaggio_nel_sacco_v21f1_chiavi_%d_%d.json', 'b': 'e409b_messaggio_nel_sacco_v21_chiavi_%d_%d.json'}


def lavoro(args):
    caso, i = args
    import canale_sacco
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()
    testo = open(TESTO, encoding='utf-8').read().replace('\r\n', '\n') if caso == 'a' else None
    t, info = canale_sacco.codifica(testo, 'e409-%d' % i, VERSIONE, verifica=False)
    nomi, X, nf = e266.tabella(e251.righe_ini(t), k['rif266'])
    return args, (nomi, X, nf, info['capacita_bit'])


def auc_gruppi(X, y, gruppi, nf):
    import e231_discriminatore as e231
    import e266_discriminatore_forte as e266
    per = OrderedDict()
    for g in e266.GRUPPI:
        col = [i for i, n in enumerate(nf) if n.startswith(g + ' ')]
        per[g] = e231.auc_cv(X[:, col], y, gruppi) if col else None
    return e231.auc_cv(X, y, gruppi), per


def contro_voynich(chiavi):
    """Dai file dell'e409: per chiave, AUC dei due giudici, pagella, cancello, per i casi a e b."""
    out = OrderedDict()
    for caso, nome in E409.items():
        for lo, hi in ((1, 12), (13, 24)):
            p = os.path.join(RISULTATI, nome % (lo, hi))
            if not os.path.exists(p):
                continue
            pc = json.load(open(p, encoding='utf-8'))['per_chiave']
            for k, r in pc.items():
                c, i = k.split('|')
                out[(caso, int(i))] = r
    righe = []
    for i in chiavi:
        if ('a', i) in out and ('b', i) in out:
            a, b = out[('a', i)], out[('b', i)]
            righe.append(OrderedDict([('chiave', i)] + [('%s_%s' % (n, c), x[n]) for n in ('AUC_e231', 'AUC_e266', 'pagella') for c, x in (('a', a), ('b', b))]
                                     + [('cancello_a', bool(a['riga'])), ('cancello_b', bool(b['riga']))]))
    return righe


def main(prova=False):
    chiavi = CHIAVI[:2] if prova else CHIAVI
    if prova:
        import e231_discriminatore as e231
        e231.PIEGHE = 2          # due sole chiavi: due pieghe
    with Pool(max(1, int(os.environ.get('PROCESSI', '1')))) as pool:
        ris = dict(pool.imap_unordered(lavoro, [(c, i) for i in chiavi for c in 'ab']))
    nf = ris[('a', chiavi[0])][2]
    X = np.vstack([ris[(c, i)][1] for c in 'ab' for i in chiavi])
    y = np.array([1 if c == 'a' else 0 for c in 'ab' for i in chiavi for _ in ris[(c, i)][0]])
    gr = np.array([i for c in 'ab' for i in chiavi for _ in ris[(c, i)][0]])
    diretto, per_gruppo = auc_gruppi(X, y, gr, nf)
    print('diretto (con contro senza): AUC %.3f | %s' % (diretto, {g: round(v, 3) for g, v in per_gruppo.items()}), flush=True)
    Xb = np.vstack([ris[('b', i)][1] for i in chiavi])
    yb = np.array([i % 2 for i in chiavi for _ in ris[('b', i)][0]])
    gb = np.array([i for i in chiavi for _ in ris[('b', i)][0]])
    negativo, per_neg = auc_gruppi(Xb, yb, gb, nf) if len(chiavi) >= 4 else (None, None)
    print('controllo negativo (dispari contro pari, senza messaggio): %s' % negativo, flush=True)
    capacita = OrderedDict((i, (ris[('a', i)][3], ris[('b', i)][3])) for i in chiavi)
    uguali = sum(a == b for a, b in capacita.values())
    print('capacita\' uguale nei due casi: %d su %d' % (uguali, len(chiavi)), flush=True)
    if prova:
        return
    righe = contro_voynich(chiavi)
    diff = OrderedDict()
    for n in ('AUC_e231', 'AUC_e266', 'pagella'):
        d = [r['%s_a' % n] - r['%s_b' % n] for r in righe]
        diff[n] = OrderedDict([('media_a', statistics.mean(r['%s_a' % n] for r in righe)), ('media_b', statistics.mean(r['%s_b' % n] for r in righe)),
                               ('differenza', statistics.mean(d)), ('errore', statistics.stdev(d) / len(d) ** 0.5 if len(d) > 1 else None)])
    cancello = (sum(r['cancello_a'] for r in righe), sum(r['cancello_b'] for r in righe))
    for n, d in diff.items():
        print('%s: a %.4f b %.4f differenza %+.4f ± %.4f' % (n, d['media_a'], d['media_b'], d['differenza'], d['errore']), flush=True)
    print('cancello: a %d, b %d su %d' % (cancello[0], cancello[1], len(righe)), flush=True)
    out = OrderedDict([('versione', VERSIONE), ('chiavi', list(chiavi)), ('contro_Voynich', OrderedDict([('per_chiave', righe), ('differenze', diff), ('cancello', cancello)])),
                       ('diretto', OrderedDict([('AUC', diretto), ('per_gruppo', per_gruppo), ('pagine', int(len(y))), ('capacita_uguale', uguali)])),
                       ('controllo_negativo', OrderedDict([('AUC', negativo), ('per_gruppo', per_neg)]))])
    json.dump(out, open(os.path.join(RISULTATI, NOME + '.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    nu = lambda v, d=3: ('%.*f' % (d, v)).replace('.', ',') if v is not None else '—'
    md = ['# e419 — Con messaggio contro senza messaggio, sulla v21', '',
          'Preregistrazione: `preregistrazioni/e419.md`. Versione v21, chiavi e409-1 … e409-%d, testo Isidoro XVII; '
          'il libro "senza" ha gli stessi parametri e la stessa chiave, con soli bit di riempimento.' % chiavi[-1], '',
          '## 1. Contro il Voynich (dai file dell\'e409: caso a `v21f1`, caso b `v21`)', '',
          '| | con messaggio (a) | senza (b) | differenza a − b |', '|---|---|---|---|']
    for n, d in diff.items():
        md.append('| %s | %s | %s | %s ± %s |' % (n.replace('AUC_', 'giudice '), nu(d['media_a']), nu(d['media_b']), ('%+.4f' % d['differenza']).replace('.', ','), nu(d['errore'], 4)))
    md += ['| cancello della riga | %d su %d | %d su %d | |' % (cancello[0], len(righe), cancello[1], len(righe)), '',
           '## 2. Diretto: le pagine dei libri con messaggio contro quelle dei libri senza', '',
           '- Caratteristiche dell\'e266, regressione logistica dell\'e231, pieghe per chiave; %d pagine.' % len(y),
           '- **AUC %s** (0,5 = tira a indovinare).' % nu(diretto),
           '- Per gruppo: ' + '; '.join('%s %s' % (g, nu(v)) for g, v in per_gruppo.items()) + '.',
           '- Capacità del libro uguale nei due casi: %d su %d chiavi.' % (uguali, len(chiavi)), '',
           '## 3. Controllo negativo: chiavi dispari contro pari, soli libri senza messaggio', '',
           '- AUC %s; per gruppo: ' % nu(negativo) + '; '.join('%s %s' % (g, nu(v)) for g, v in per_neg.items()) + '.', '']
    open(os.path.join(RISULTATI, NOME + '.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md))


if __name__ == '__main__':
    main(prova='--prova' in sys.argv)
