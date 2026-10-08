# -*- coding: utf-8 -*-
"""Esperimento e3c84: i confronti del white paper con i 71 testi di Gaskell e Bowern, rifatti per lingua.

I 71 "testi sensati" sono 56 testi in 24 lingue naturali (quasi sempre due per lingua) e 15 in 8 lingue artificiali.
Il paper li chiamava "71 lingue". Qui ogni statistica si riassume per lingua naturale (mediana dei suoi testi), le
lingue artificiali si tengono a parte, e si rifanno le frasi del paper. Due prove di sensibilità: per lingua e periodo
(storico / moderno) e, per ogni lingua, il suo testo più simile al Voynich.

Parte A: valori testo per testo già salvati (e3a49, e3a55, e3a58, e3a61, e3a67, e384, e3a03, e3a35, e3a89, e3b25 per il
Voynich). Parte B: valori mai salvati testo per testo, ricalcolati con le stesse misure: giuntura (e377, prime 10.000
parole, 50 rimescolamenti) e ripetizioni (e3b25).

Preregistrazione: preregistrazioni/e3c84.md. Scrive risultati/e3c84_confronti_per_lingua.json e .md.
SOLO_CONTROLLI=1: prova del codice sui soli testi di confronto (niente Voynich), prima della preregistrazione.
"""
import json, os, random, statistics, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e375_coppie as e375
import e377_giuntura_gibberish as e377
import e381_parole_intere as e381
import e3a58_spazi_prevedibili as e3a58
import e3b25_ripetizioni_grezze as e3b25

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
PERM = 50
NORMA = {'Latin (Abbreviated)': 'Latin', 'Chinese (Pinyin)': 'Chinese'}


def carica(nome):
    return json.load(open(os.path.join(RISULTATI, nome), encoding='utf-8'))


def etichetta(testo):
    """('Historical' | 'Modern' | 'Conlangs', lingua normalizzata) dal nome del file di Gaskell e Bowern."""
    parti = [p.strip() for p in testo.replace('.txt', '').split(' - ')]
    return parti[0], NORMA.get(parti[1], parti[1])


# --------------------------------------------------------------------------- parte A: valori salvati
def parte_a():
    st = OrderedDict()
    d = carica('e3a58_spazi_prevedibili.json')['parte1']
    st['spazio'] = (d['altri']['Voynich']['f1'], dict(d['testi_sensati']))
    d = carica('e3a61_forme_riempite.json')
    st['riempimento'] = (d['altri']['Voynich']['riempimento'], {k: v['riempimento'] for k, v in d['testi_sensati'].items()})
    d = carica('e3a67_spazi_rifatti.json')
    st['attestazione'] = (d['altri']['Voynich']['attestazione'], dict(d['testi_sensati']))
    d = carica('e3a49_dentro_fra.json')
    st['rispecchiamento'] = (d['Voynich']['mediana_10000'], {k: v['rho'] for k, v in d['testi_sensati'].items()})
    d = carica('e3a55_frequenza_forma.json')
    st['frequenza_forma'] = (d['Voynich']['mediana_10000'], dict(d['testi_sensati']))
    d = carica('e384_giuntura_a_capo.json')['testi']
    st['a_capo_Q'] = (d['Voynich']['Q'], {k: v['Q'] for k, v in d.items() if k not in ('Voynich', 'gibberish umano')})
    d = carica('e3a03_distanza_due.json')
    st['distanza_due_z'] = (d['Voynich']['z'], {k: v['z'] for k, v in d['testi_sensati'].items()})
    d = carica('e3a35_margine_confronti.json')
    st['margine'] = (d['Voynich']['primi 2 segni']['rapporto'],
                     {k: v['primi 2 segni']['rapporto'] for k, v in d['testi_sensati'].items() if v['primi 2 segni']['coppie'] >= 300})
    d = carica('e3a89_ripresa_lingue.json')
    st['calo'] = (d['confronto']['calo']['voynich'], {k: v['calo'] for k, v in d['testi_sensati'].items() if v['coppie_stessa_d7_10'] >= 500})
    return st


# --------------------------------------------------------------------------- parte B: valori ricalcolati
def voynich_sottoinsiemi(rnd, n=10000, quanti=5):
    pag = e375.voynich()
    out = []
    for _ in range(quanti):
        ordine = rnd.sample(pag, len(pag))
        prese, k = [], 0
        for p in ordine:
            if k >= n:
                break
            prese += p
            k += sum(len(r) for r in p)
        out.append(prese)
    return out


def parte_b(rnd):
    testi = OrderedDict((k.replace('.txt', ''), e3a58.righe_prime(t)) for k, t in e381.testi().items())
    giun, rip, quasi = OrderedDict(), OrderedDict(), OrderedDict()
    for k, righe in testi.items():
        giun[k] = e377.prova(righe, rnd, PERM)['E']
        q = e3b25.quote(righe)
        rip[k], quasi[k] = q['ripetizione'], q['quasi']
        print(k, '%.4f %.4f %.4f' % (giun[k], rip[k], quasi[k]), flush=True)
    if SOLO_CONTROLLI:
        vg = vr = vq = None
    else:
        vg = statistics.median(e377.prova(s, rnd, PERM)['E'] for s in voynich_sottoinsiemi(rnd))
        d = carica('e3b25_ripetizioni_grezze.json')['altri']['Voynich']
        vr, vq = d['ripetizione'], d['quasi']
    return OrderedDict([('giuntura', (vg, giun)), ('ripetizione', (vr, rip)), ('quasi_ripetizione', (vq, quasi))])


# --------------------------------------------------------------------------- riassunto per lingua
# direzione: 'alto' = il Voynich sta in alto (conta chi lo supera); 'basso' = il Voynich sta in basso (conta chi sta sotto)
DIREZIONE = OrderedDict([('spazio', 'alto'), ('riempimento', 'alto'), ('attestazione', 'alto'), ('rispecchiamento', 'alto'),
                         ('frequenza_forma', 'alto'), ('giuntura', 'alto'), ('ripetizione', 'alto'), ('quasi_ripetizione', 'alto'),
                         ('margine', 'basso'), ('calo', 'basso'), ('a_capo_Q', 'descrittiva'), ('distanza_due_z', 'descrittiva')])


def gruppi(valori, modo):
    g = defaultdict(list)
    for t, v in valori.items():
        if v is None:
            continue
        cat, ling = etichetta(t)
        if cat == 'Conlangs':
            continue
        g[ling if modo != 'periodo' else '%s (%s)' % (ling, cat)].append(v)
    return g


def riassunto(voy, valori, direzione):
    out = OrderedDict()
    for modo in ('lingua', 'periodo', 'piu_simile'):
        g = gruppi(valori, modo)
        if modo == 'piu_simile':
            agg = {k: (max(v) if direzione != 'basso' else min(v)) for k, v in g.items()}
        else:
            agg = {k: statistics.median(v) for k, v in g.items()}
        r = OrderedDict([('n', len(agg)), ('mediana', statistics.median(agg.values())), ('minimo', min(agg.values())),
                         ('massimo', max(agg.values()))])
        if voy is not None and direzione in ('alto', 'basso'):
            oltre = sorted(k for k, v in agg.items() if (v > voy if direzione == 'alto' else v < voy))
            r['oltre_il_voynich'] = oltre
            r['quota_dietro_il_voynich'] = 1 - len(oltre) / len(agg)
        r['valori'] = OrderedDict(sorted(agg.items(), key=lambda kv: -kv[1]))
        out[modo] = r
    art = {t: v for t, v in valori.items() if v is not None and etichetta(t)[0] == 'Conlangs'}
    a = OrderedDict([('testi', len(art)), ('valori', OrderedDict(sorted(art.items(), key=lambda kv: -kv[1])))])
    if voy is not None and direzione in ('alto', 'basso'):
        a['oltre_il_voynich'] = sorted(k for k, v in art.items() if (v > voy if direzione == 'alto' else v < voy))
    out['lingue_artificiali'] = a
    return out


def esiti(voy, R):
    """Le frasi del paper rifatte con i criteri della preregistrazione (aggregazione primaria: per lingua)."""
    e = OrderedDict()

    def quota(k):
        return R[k]['lingua']['quota_dietro_il_voynich']

    def nessuna(k):
        return all(not R[k][m]['oltre_il_voynich'] for m in ('lingua', 'periodo', 'piu_simile'))

    for k in ('spazio', 'riempimento'):
        e[k] = 'regge (sopra almeno il 90% delle lingue)' if quota(k) >= 0.9 else 'non regge (sopra il %.0f%% delle lingue)' % (100 * quota(k))
    for k in ('attestazione', 'rispecchiamento', 'frequenza_forma', 'ripetizione', 'quasi_ripetizione'):
        if nessuna(k):
            e[k] = 'regge: più di tutte le lingue naturali'
        else:
            e[k] = 'da riformulare: %d lingue su %d oltre il Voynich (%s)' % (
                len(R[k]['lingua']['oltre_il_voynich']), R[k]['lingua']['n'], ', '.join(R[k]['lingua']['oltre_il_voynich']) or 'solo nelle prove di sensibilità')
    e['giuntura'] = ('parte alta della gamma' if quota('giuntura') >= 0.75 else 'non nella parte alta') + \
        ': %d lingue su %d oltre il Voynich (%s)' % (len(R['giuntura']['lingua']['oltre_il_voynich']), R['giuntura']['lingua']['n'],
                                                     ', '.join(R['giuntura']['lingua']['oltre_il_voynich']))
    for k in ('margine', 'calo'):
        n_sotto, n = len(R[k]['lingua']['oltre_il_voynich']), R[k]['lingua']['n']
        e[k] = ('regge: raro nelle lingue' if n_sotto / n <= 0.10 else 'non regge come "raro"') + \
            ' (%d lingue su %d sotto il Voynich: %s)' % (n_sotto, n, ', '.join(R[k]['lingua']['oltre_il_voynich']))
    chiuse = sorted(k for k, v in R['a_capo_Q']['lingua']['valori'].items() if v <= 0.10)
    e['a_capo_Q'] = 'descrittiva: %d lingue su %d con Q ≤ 0,10 (%s)' % (len(chiuse), R['a_capo_Q']['lingua']['n'], ', '.join(chiuse))
    con = sorted(k for k, v in R['distanza_due_z']['lingua']['valori'].items() if v >= 3)
    e['distanza_due_z'] = 'descrittiva: legame a distanza due (z ≥ 3) in %d lingue su %d' % (len(con), R['distanza_due_z']['lingua']['n'])
    return e


def main():
    rnd = random.Random(3384)
    stat = OrderedDict()
    if not SOLO_CONTROLLI:
        stat.update(parte_a())
    stat.update(parte_b(rnd))
    R = OrderedDict()
    for k in DIREZIONE:
        if k in stat:
            voy, valori = stat[k]
            R[k] = OrderedDict([('voynich', voy)])
            R[k].update(riassunto(voy, valori, DIREZIONE[k]))
    if SOLO_CONTROLLI:
        for k, r in R.items():
            print(k, json.dumps({m: {'n': r[m]['n'], 'mediana': r[m]['mediana'], 'massimo': r[m]['massimo']} for m in ('lingua', 'periodo', 'piu_simile')}, default=float))
            print('   lingue artificiali:', r['lingue_artificiali']['testi'])
        return
    E = esiti(None, R)
    out = OrderedDict([('statistiche', R), ('esiti', E)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c84_confronti_per_lingua.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c84 — I confronti con i testi di Gaskell e Bowern rifatti per lingua', '',
          'Preregistrazione: `preregistrazioni/e3c84.md`. Lingue naturali: valore di una lingua = mediana dei suoi testi; '
          'lingue artificiali a parte. "Oltre il Voynich" = lingue più in là del Voynich nella sua direzione.', '',
          '| statistica | Voynich | lingue (n) | mediana | min – max | oltre il Voynich: per lingua / per periodo / testo più simile | lingue artificiali oltre |',
          '|---|---|---|---|---|---|---|']
    for k, r in R.items():
        L = r['lingua']
        oltre = ' / '.join(str(len(r[m].get('oltre_il_voynich', []))) if 'oltre_il_voynich' in r[m] else '–' for m in ('lingua', 'periodo', 'piu_simile'))
        art = r['lingue_artificiali']
        md.append('| %s | %.4f | %d | %.4f | %.4f – %.4f | %s | %s |' % (
            k, r['voynich'], L['n'], L['mediana'], L['minimo'], L['massimo'], oltre,
            ', '.join(a.split(' - ')[1] for a in art.get('oltre_il_voynich', [])) or ('–' if 'oltre_il_voynich' not in art else 'nessuna')))
    md += ['', '## Esiti', '']
    md += ['- **%s:** %s' % (k, v) for k, v in E.items()]
    md += ['', '## Valori per lingua (aggregazione primaria)', '']
    for k, r in R.items():
        md.append('- **%s** (Voynich %.4f): %s' % (k, r['voynich'], '; '.join('%s %.4f' % kv for kv in r['lingua']['valori'].items())))
    open(os.path.join(RISULTATI, 'e3c84_confronti_per_lingua.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(E, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
