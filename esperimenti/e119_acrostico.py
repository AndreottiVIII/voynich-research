# -*- coding: utf-8 -*-
"""Esperimento 119: un messaggio nelle iniziali di riga (acrostico)? Statistica della sequenza dei primi segni delle
righe e tentativo di decifrazione con il risolutore dell'e17 (latino, italiano), con controlli positivi e negativi.

Preregistrazione: preregistrazioni/e119.md. Scrive risultati/e119_acrostico.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e17_ricottura as e17
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 119, 300
D = misure.divisore(misure.GLIFI_EVA)


def iniziali_voynich():
    per = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if not r.parole or r.inizio_par:
            continue
        w = r.parole[0]
        per.setdefault(r.pagina, []).append(D(w)[0] if trascrizione.pulita(w) else None)
    return e17.in_unita([[x for x in v] for v in per.values()], lambda x: [x])


def iniziali_ts():
    rr = e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))
    pagine = []
    for i, (ini, ps) in enumerate(rr):
        if i % 29 == 0:
            pagine.append([])
        if not ini and ps:
            pagine[-1].append(ps[0])
    return e17.in_unita(pagine, lambda w: [D(w)[0]])


def statistiche(righe, rnd):
    seq = [x for r in righe for x in r]
    c = Counter(seq)
    n = len(seq)
    h1 = -sum(k / n * math.log2(k / n) for k in c.values())
    cp = Counter((a, b) for r in righe for a, b in zip(r, r[1:]))
    ca = Counter(a for r in righe for a in r[:-1])
    m = sum(cp.values())
    h2 = -sum(k / m * math.log2(k / ca[a]) for (a, _), k in cp.items())

    def im(rr, k):
        return misure.informazione_mutua([(r[i], r[i + k]) for r in rr for i in range(len(r) - k)])

    def stesso(rr, k):
        cc = [(r[i], r[i + k]) for r in rr for i in range(len(r) - k)]
        return sum(a == b for a, b in cc) / len(cc)
    reale = {'im1': im(righe, 1), 'im2': im(righe, 2), 's1': stesso(righe, 1), 's2': stesso(righe, 2)}
    nulli = {k: [] for k in reale}
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in righe:
            r = list(r)
            rnd.shuffle(r)
            mes.append(r)
        nulli['im1'].append(im(mes, 1))
        nulli['im2'].append(im(mes, 2))
        nulli['s1'].append(stesso(mes, 1))
        nulli['s2'].append(stesso(mes, 2))
    out = OrderedDict([('lunghezza', n), ('simboli', len(c)), ('h1', h1), ('h2', h2), ('h2_su_h1', h2 / h1)])
    for k in ('im1', 'im2'):
        mm, s = statistics.mean(nulli[k]), statistics.pstdev(nulli[k])
        out[k] = OrderedDict([('eccesso', reale[k] - mm), ('z', (reale[k] - mm) / s if s else None)])
    for k in ('s1', 's2'):
        out[k.upper()] = reale[k] / statistics.mean(nulli[k])
    return out


def lettere_righe(chiave, lunghezza, per=20):
    testo = lingue.parole(chiave)
    lett = e17.alfabeto(testo)
    s = ''.join(e17.pulisci(testo, lett))[:lunghezza]
    return [list(s[i:i + per]) for i in range(0, len(s), per)]


def una_lingua(chiave_l, nome, voynich):
    rnd = random.Random('e119-' + chiave_l)
    testo, add, lettere, modello, lessico = e17.prepara_lingua(chiave_l)
    altro = lingue.parole(e17.STRANIERO)
    altro = e17.pulisci(altro, e17.alfabeto(altro))
    simboli = len({u for r in voynich for u in r})
    L = sum(map(len, voynich))
    r = OrderedDict()
    cif, vera = e17.cifra_abbinata(e17.in_righe(e17.prendi(testo[add:], L)), simboli, rnd)
    r['controllo positivo'] = e17.attacca(cif, modello, lessico, rnd, vera=vera)
    cif, _ = e17.cifra_abbinata(e17.in_righe(e17.prendi(altro, L)), simboli, rnd)
    r['controllo negativo'] = e17.attacca(cif, modello, lessico, rnd)
    r['Voynich'] = e17.attacca(voynich, modello, lessico, rnd)
    pos = r['controllo positivo']['punteggio']
    neg = r['controllo negativo']['punteggio']
    r['posizione'] = (r['Voynich']['punteggio'] - neg) / (pos - neg) if pos != neg else float('nan')
    return r


def main():
    voy = iniziali_voynich()
    print('iniziali del Voynich: %d righe-pagina, %d simboli, lunghezza %d' % (len(voy), len({u for r in voy for u in r}), sum(map(len, voy))), flush=True)
    L = sum(map(len, voy))
    simboli = len({u for r in voy for u in r})
    rnd = random.Random(SEME)
    ris = OrderedDict()
    seq = OrderedDict()
    seq['iniziali del Voynich'] = voy
    seq['lettere latine'] = lettere_righe('Latin', L)
    seq['lettere italiane'] = lettere_righe('Italian', L)
    cif, _ = e17.cifra_abbinata([[''.join(r)] for r in seq['lettere latine']], simboli, random.Random(SEME))
    seq['acrostico latino cifrato (11 simboli)'] = cif
    seq['iniziali di Timm e Schinner'] = iniziali_ts()
    stat = OrderedDict()
    for nome, rr in seq.items():
        stat[nome] = statistiche(rr, rnd)
        s = stat[nome]
        print('%-40s lungh %5d simboli %2d | h1 %.2f h2 %.2f (h2/h1 %.2f) | IM1 %.3f (z %.1f) IM2 %.3f (z %.1f) | S1 %.2f S2 %.2f' % (
            nome, s['lunghezza'], s['simboli'], s['h1'], s['h2'], s['h2_su_h1'], s['im1']['eccesso'], s['im1']['z'] or 0,
            s['im2']['eccesso'], s['im2']['z'] or 0, s['S1'], s['S2']), flush=True)
    ris['statistica'] = stat
    dec = OrderedDict()
    for chiave_l, nome in (('Latin', 'latino'), ('Italian', 'italiano')):
        r = una_lingua(chiave_l, nome, voy)
        dec[nome] = r
        for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
            x = r[k]
            print('%-10s %-20s punteggio %.3f copertura %.1f%% (6+: %.1f%%) %s' % (nome, k, x['punteggio'], 100 * x['copertura'], 100 * x['copertura_6'],
                                                                         'chiave giusta %.0f%%' % (100 * x['chiave_giusta']) if 'chiave_giusta' in x else ''), flush=True)
        print('   posizione del Voynich %.2f | decifrato: %s' % (r['posizione'], ' / '.join(r['Voynich']['esempio'][:3])[:200]), flush=True)
    ris['decifrazione'] = dec
    valido = any(dec[n]['controllo positivo'].get('chiave_giusta', 0) >= 0.5 for n in dec)
    non_escluso = any(dec[n]['posizione'] >= 0.5 and dec[n]['Voynich']['copertura_6'] >= 0.10 for n in dec)
    ris['valido'], ris['acrostico_non_escluso'] = valido, non_escluso
    print('controllo valido:', valido, '| acrostico non escluso:', non_escluso)
    with open(os.path.join(RISULTATI, 'e119_acrostico.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e119 — Un messaggio nelle iniziali di riga?', '', 'Preregistrazione: `preregistrazioni/e119.md`.', '', '## Statistica', '',
           '| sequenza | lunghezza | simboli | h1 | h2 | h2/h1 | IM1 (z) | IM2 (z) | S(1) | S(2) |', '|---|---|---|---|---|---|---|---|---|---|']
    for nome, s in stat.items():
        out.append('| %s | %d | %d | %.2f | %.2f | %.2f | %.3f (%.1f) | %.3f (%.1f) | %.2f | %.2f |' % (
            nome, s['lunghezza'], s['simboli'], s['h1'], s['h2'], s['h2_su_h1'], s['im1']['eccesso'], s['im1']['z'] or 0,
            s['im2']['eccesso'], s['im2']['z'] or 0, s['S1'], s['S2']))
    out += ['', '## Decifrazione (risolutore dell\'e17)', '', '| lingua | prova | punteggio | copertura | copertura 6+ | chiave giusta |', '|---|---|---|---|---|---|']
    for nome, r in dec.items():
        for k in ('controllo positivo', 'controllo negativo', 'Voynich'):
            x = r[k]
            out.append('| %s | %s | %.3f | %.1f%% | %.1f%% | %s |' % (nome, k, x['punteggio'], 100 * x['copertura'], 100 * x['copertura_6'],
                                                                   '%.0f%%' % (100 * x['chiave_giusta']) if 'chiave_giusta' in x else '–'))
        out.append('| %s | posizione del Voynich | %.2f | | | |' % (nome, r['posizione']))
    out += ['', 'Controllo valido: **%s**. Acrostico non escluso: **%s**.' % ('sì' if valido else 'no', 'sì' if non_escluso else 'no'), '',
            'Inizio del testo decifrato (latino): `%s`' % ' / '.join(dec['latino']['Voynich']['esempio'][:4])]
    with open(os.path.join(RISULTATI, 'e119_acrostico.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
