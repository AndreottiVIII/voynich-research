# -*- coding: utf-8 -*-
"""Esperimento 130: le proprieta' di riga del Voynich, mano per mano (variabile $H della ZL), con intervalli bootstrap
per pagine e riferimenti dall'e128; in piu' la quota di sh decisa per riga.

Preregistrazione: preregistrazioni/e130.md. Scrive risultati/e130_mani.json e .md.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e123b_origine_dipendenza as e123b
import e128_scrittura_inventata as e128

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANI, PRINCIPALI = ('1', '2', '3', '4', '5'), ('1', '2', '3')
BOOT, SEME, PERM_SH = 30, 130, 200
DISCRIMINANTI = ("bordo d'inizio", 'S(1)', 'lunghezze vicine', 'ripetizione immediata')


def righe_mano(h):
    return [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'), mano=h) if r.parole]


def varianza_sh(righe, perm, rnd):
    occ = e123b.occorrenze(righe)
    s = [o['scelta'] for o in occ]
    per_riga = defaultdict(list)
    for i, o in enumerate(occ):
        per_riga[o['riga']].append(i)
    idx = [v for v in per_riga.values() if len(v) >= 3]

    def var(x):
        return statistics.pvariance([sum(x[i] for i in v) / len(v) for v in idx])
    reale = var(s)
    gruppi = e123b.gruppi_di(occ, 'base')
    nulli = [var(e123b.permuta(s, gruppi, rnd)) for _ in range(perm)]
    m = statistics.mean(nulli)
    return reale / m if m else None


def ricampiona(righe, seme):
    pagine = OrderedDict()
    for r in righe:
        pagine.setdefault(r[0], []).append(r)
    chiavi = list(pagine)
    rnd = random.Random(seme)
    out = []
    for j in range(len(chiavi)):
        c = rnd.choice(chiavi)
        out.extend(((c, j), ini, ps) for _, ini, ps in pagine[c])
    return out


def una(args):
    h, b, righe = args
    rr = righe if b is None else ricampiona(righe, SEME * 1000 + b)
    _, r = e128.misura(('mano %s' % h, rr, 'eva'))
    r['quota sh per riga'] = varianza_sh(rr, PERM_SH if b is None else 50, random.Random(SEME + (b or 0)))
    return h, b, r


def main():
    rif = json.load(open(os.path.join(RISULTATI, 'e128_scrittura_inventata.json'), encoding='utf-8'))['tabella']
    lavori = []
    for h in MANI:
        rr = righe_mano(h)
        print('mano %s: %d righe, %d parole' % (h, len(rr), sum(len(ps) for _, _, ps in rr)), flush=True)
        lavori.append((h, None, rr))
        if h in PRINCIPALI:
            lavori.extend((h, b, rr) for b in range(BOOT))
    stime, boot = {}, defaultdict(list)
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for h, b, r in pool.imap(una, lavori):
            if b is None:
                stime[h] = r
                print('mano %s: %s' % (h, ' | '.join('%s %.3f' % (k, v if v is not None else float('nan')) for k, v in r.items())), flush=True)
            else:
                boot[h].append(r)
    props = list(stime['1'])
    tab = OrderedDict()
    for h in MANI:
        t = OrderedDict()
        for p in props:
            x = stime[h][p]
            iv = None
            if h in PRINCIPALI:
                vv = sorted(r[p] for r in boot[h] if r[p] is not None)
                iv = [vv[int(0.05 * (len(vv) - 1))], vv[int(0.95 * (len(vv) - 1))]] if vv else None
            lato = None
            if p in rif and x is not None:
                lato = abs(x - rif[p]['Voynich'][0]) < abs(x - rif[p]['lingue'][0])
            t[p] = OrderedDict([('stima', x), ('intervallo', iv), ('lato_Voynich', lato)])
        tab[h] = t
    sovrapposti = lambda a, b: a[0] <= b[1] and b[0] <= a[1]
    tutte_lato = all(tab[h][p]['lato_Voynich'] for h in PRINCIPALI for p in DISCRIMINANTI)
    sh_sopra = all(tab[h]['quota sh per riga']['intervallo'] and tab[h]['quota sh per riga']['intervallo'][0] > 1 for h in PRINCIPALI)
    coppie = [(a, b) for i, a in enumerate(PRINCIPALI) for b in PRINCIPALI[i + 1:]]
    concordi = all(sovrapposti(tab[a][p]['intervallo'], tab[b][p]['intervallo']) for p in ("bordo d'inizio", 'S(1)') for a, b in coppie)
    personali = any(not tab[h][p]['lato_Voynich'] for h in PRINCIPALI for p in ("bordo d'inizio", 'S(1)'))
    if tutte_lato and sh_sopra and concordi:
        esito = 'regola condivisa'
    elif personali:
        esito = 'abitudini personali'
    else:
        esito = 'in parte'
    differenze = [('mano %s, %s' % (h, p)) for h in PRINCIPALI for p in DISCRIMINANTI if not tab[h][p]['lato_Voynich']]
    differenze += ['intervalli non sovrapposti: %s, mani %s e %s' % (p, a, b) for p in ("bordo d'inizio", 'S(1)') for a, b in coppie
                   if not sovrapposti(tab[a][p]['intervallo'], tab[b][p]['intervallo'])]
    differenze += ['mano %s: quota sh per riga non sopra 1' % h for h in PRINCIPALI
                   if not (tab[h]['quota sh per riga']['intervallo'] and tab[h]['quota sh per riga']['intervallo'][0] > 1)]
    print('esito: %s | differenze: %s' % (esito, '; '.join(differenze) or 'nessuna'))
    with open(os.path.join(RISULTATI, 'e130_mani.json'), 'w', encoding='utf-8') as fo:
        json.dump({'tabella': tab, 'esito': esito, 'differenze': differenze}, fo, ensure_ascii=False, indent=1)
    out = ['# e130 — Le regole di riga sono le stesse per ogni mano?', '',
           'Mani della ZL ($H). Stima (intervallo bootstrap 5–95%%, %d ricampionamenti per pagine). Riferimenti dall\'e128 (circa 10.000 parole). '
           'Preregistrazione: `preregistrazioni/e130.md`.' % BOOT, '',
           '| proprietà | Voynich (e128) | lingue (e128) | ' + ' | '.join('mano %s' % h for h in MANI) + ' |', '|---|---|---|' + '---|' * len(MANI)]
    for p in props:
        rv = '%.3f' % rif[p]['Voynich'][0] if p in rif else '–'
        rl = '%.3f' % rif[p]['lingue'][0] if p in rif else '–'
        celle = []
        for h in MANI:
            t = tab[h][p]
            s = '%.3f' % t['stima'] if t['stima'] is not None else '–'
            if t['intervallo']:
                s += ' (%.3f–%.3f)' % tuple(t['intervallo'])
            celle.append(s)
        out.append('| %s | %s | %s | %s |' % (p, rv, rl, ' | '.join(celle)))
    out += ['', 'Esito: **%s**. Differenze: %s.' % (esito, '; '.join(differenze) or 'nessuna'),
            '', 'Confondimento: la mano 1 scrive solo in lingua A, le mani 2 e 3 quasi solo in lingua B.']
    with open(os.path.join(RISULTATI, 'e130_mani.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
