# -*- coding: utf-8 -*-
"""Esperimento 136: le fini delle righe rimano? IM e quota di fini identiche fra la riga i e la riga i + k nello stesso
paragrafo, contro il rimescolamento dell'ordine delle righe dentro il paragrafo.

Preregistrazione: preregistrazioni/e136.md. Scrive risultati/e136_rima.json e .md.
"""
import hashlib, json, os, random, statistics, sys, unicodedata
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
DANTE = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni', 'naibbe-cipher', 'input', 'examples', 'divina_commedia.txt')
SHA_DANTE = 'd1de9b0babca43d8c02258781f6f08ce93d1b99521e234ff44b60a996c54f7b9'
SEME, RIMESCOLAMENTI, KK = 136, 1000, (1, 2, 3, 4)
D = misure.divisore(misure.GLIFI_EVA)


def lettere(w):
    w = unicodedata.normalize('NFD', w.lower())
    return [c for c in w if c.isalpha() and not unicodedata.combining(c)]


def fini(paragrafi, dividi):
    """paragrafi: liste di righe di parole -> liste di fini (ultimi 2 segni) per paragrafo."""
    out = []
    for p in paragrafi:
        f = []
        for ps in p:
            if ps and trascrizione.pulita(ps[-1]):
                u = dividi(ps[-1])
                if u:
                    f.append(''.join(u[-2:]))
        if len(f) >= 2:
            out.append(f)
    return out


def coppie(pp, k):
    return [(p[i], p[i + k]) for p in pp for i in range(len(p) - k)]


def stat(pp):
    out = {}
    for k in KK:
        cc = coppie(pp, k)
        out[k] = (misure.informazione_mutua(cc), sum(a == b for a, b in cc) / len(cc) if cc else 0, len(cc))
    return out


def una(args):
    nome, paragrafi, quale = args
    pp = fini(paragrafi, D if quale == 'eva' else lettere)
    reale = stat(pp)
    rnd = random.Random(SEME)
    nim, nug = {k: [] for k in KK}, {k: [] for k in KK}
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for p in pp:
            p = p[:]
            rnd.shuffle(p)
            mes.append(p)
        for k, (im, ug, _) in stat(mes).items():
            nim[k].append(im)
            nug[k].append(ug)
    r = OrderedDict([('paragrafi', len(pp)), ('righe', sum(map(len, pp)))])
    for k in KK:
        m, s = statistics.mean(nim[k]), statistics.pstdev(nim[k])
        mu = statistics.mean(nug[k])
        r['k%d' % k] = OrderedDict([('coppie', reale[k][2]), ('eccesso_im', reale[k][0] - m), ('z', (reale[k][0] - m) / s if s else None),
                                    ('identiche', reale[k][1]), ('rapporto_identiche', reale[k][1] / mu if mu else None)])
    return nome, r


def dante():
    if hashlib.sha256(open(DANTE, 'rb').read()).hexdigest() != SHA_DANTE:
        raise SystemExit('Commedia diversa da quella preregistrata')
    canti, cur = [], []
    for l in open(DANTE, encoding='utf-8').read().splitlines():
        s = l.strip()
        if not s:
            continue
        if s.startswith('Canto ') or s.isupper() or s in ('Inferno', 'Purgatorio', 'Paradiso'):
            if s.startswith('Canto ') and cur:
                canti.append(cur)
                cur = []
            continue
        cur.append(s.split())
    if cur:
        canti.append(cur)
    # il file contiene il poema due volte: si tiene la prima occorrenza di ogni canto
    visti, unici = set(), []
    for c in canti:
        chiave = ' '.join(' '.join(v) for v in c[:2])
        if chiave not in visti:
            visti.add(chiave)
            unici.append(c)
    return unici


def testi():
    import e98_versi_latini as e98
    import e99_macer as e99
    t = OrderedDict()
    for q in ('ZL', 'IT'):
        per = OrderedDict()
        par = 0
        for r in trascrizione.testo_corrente(trascrizione.leggi(q)):
            if r.parole:
                par += bool(r.inizio_par)
                per.setdefault((r.pagina, par), []).append(list(r.parole))
        t['Voynich ' + q] = (list(per.values()), 'eva')
    t['Dante, Commedia (terza rima)'] = (dante(), 'lettere')
    ov = e98.versi(e98.TESTI['Ovidio, Metamorfosi'])
    t['Ovidio, Metamorfosi'] = ([ov[i:i + 29] for i in range(0, len(ov), 29)], 'lettere')
    t['Macer floridus'] = (e99.capitoli(), 'lettere')
    ts = [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))]
    t['Timm e Schinner, seme 19'] = ([ts[i:i + 29] for i in range(0, len(ts), 29)], 'eva')
    return t


def main():
    t = testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, p, q) for n, (p, q) in t.items()]):
            ris[nome] = r
            print('%-30s paragrafi %4d righe %5d | %s' % (nome, r['paragrafi'], r['righe'], ' | '.join(
                'k%d %+.4f (z %.1f) ident x%.2f' % (k, r['k%d' % k]['eccesso_im'], r['k%d' % k]['z'] or 0, r['k%d' % k]['rapporto_identiche'] or 0) for k in KK)), flush=True)
    z = lambda n, k: ris[n]['k%d' % k]['z'] or 0
    valido = z('Dante, Commedia (terza rima)', 2) > 10
    rif = ('Ovidio, Metamorfosi', 'Macer floridus', 'Timm e Schinner, seme 19')
    rima = all(any(z(v, k) > 4 and all(z(v, k) > z(n, k) for n in rif) and (ris[v]['k%d' % k]['rapporto_identiche'] or 0) > 1.2 for k in (1, 2))
               for v in ('Voynich ZL', 'Voynich IT'))
    ris['valido'], ris['rima'] = valido, rima
    print('controllo valido:', valido, '| rima nel Voynich:', rima)
    with open(os.path.join(RISULTATI, 'e136_rima.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e136 — Le righe rimano?', '', 'Fine di riga = ultimi 2 segni (lettere). Eccesso d\'IM fra la riga i e la riga i + k nello stesso paragrafo, contro %d '
           'rimescolamenti dell\'ordine delle righe nel paragrafo; z e rapporto di fini identiche. Preregistrazione: `preregistrazioni/e136.md`.' % RIMESCOLAMENTI, '',
           '| testo | righe | ' + ' | '.join('k = %d' % k for k in KK) + ' |', '|---|---|' + '---|' * len(KK)]
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %s |' % (nome, r['righe'], ' | '.join('%+.4f (z %.1f; ×%.2f)' % (r['k%d' % k]['eccesso_im'], r['k%d' % k]['z'] or 0,
                                                                                         r['k%d' % k]['rapporto_identiche'] or 0) for k in KK)))
    out += ['', 'Controllo valido: **%s**. Rima nel Voynich: **%s**.' % ('sì' if valido else 'no', 'sì' if rima else 'no')]
    with open(os.path.join(RISULTATI, 'e136_rima.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
