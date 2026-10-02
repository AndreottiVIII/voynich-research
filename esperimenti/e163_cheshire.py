# -*- coding: utf-8 -*-
"""Esperimento 163: la chiave di Cheshire (2019) contro chiavi casuali della stessa forma, su un lessico romanzo,
fuori campione; controllo positivo con italiano vero scritto con l'inverso della chiave.

Preregistrazione: preregistrazioni/e163.md. Scrive risultati/e163_cheshire.json e .md.
"""
import hashlib, json, os, random, re, sys, unicodedata
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
CACHE = os.path.join(QUI, '..', 'dati', 'cache', 'letture_proposte')
SHA = '7cffdecd7ebfb89b91ba79eb320c9be04b7c13e34832a8b17318f9c8cc592ecd'
SEME, CHIAVI_M1, CHIAVI_M2 = 163, 2000, 200
LINGUE = ['Latin', 'Italian', 'Portuguese', 'Romanian', 'Spanish', 'French', 'Basque-NT']
CONTROLLO_CARATTERI = 150000

CHIAVE = OrderedDict([('ckh', 'ele'), ('cth', 'eme'), ('cfh', 'eque'), ('cph', 'epe'), ('ch', 'e'), ('sh', 'ae'), ('ii', 'u'),
                      ('a', 'a'), ('y', 'a'), ('o', 'o'), ('e', 'e'), ('i', 'i'), ('n', 's'), ('q', 'd'), ('d', 'n'), ('k', 'l'),
                      ('t', 'm'), ('f', 'qu'), ('p', 'p'), ('l', 'r'), ('r', 's'), ('s', 't'), ('m', 'sa'), ('g', 'ta'), ('x', 'v')])
VOCALICHE = {'ch', 'sh', 'ii', 'a', 'y', 'o', 'e', 'i'}
UNITA = sorted(CHIAVE, key=len, reverse=True)
INVERSA = {'a': 'a', 'e': 'e', 'i': 'i', 'o': 'o', 'u': 'ii', 's': 'r', 'd': 'q', 'n': 'd', 'l': 'k', 'm': 't', 'p': 'p', 'r': 'l',
           't': 's', 'b': 'p', 'c': 'k', 'k': 'k', 'g': 'q', 'f': 'f', 'h': '', 'z': 'r', 'j': 'i', 'w': 'ii', 'x': 's', 'y': 'a', 'v': 'x'}


def piatta(w):
    w = unicodedata.normalize('NFKD', w.lower().replace('æ', 'ae').replace('œ', 'oe'))
    return ''.join(c for c in w if 'a' <= c <= 'z')


def unita(w):
    out, i = [], 0
    while i < len(w):
        for u in UNITA:
            if w.startswith(u, i):
                out.append(u)
                i += len(u)
                break
        else:
            return None
    return tuple(out)


def fuori_campione(pagina):
    m = re.match(r'f(\d+)', pagina)
    if m is None:               # fRos: il pieghevole delle rosette (f85-f86), escluso
        return False
    n = int(m.group(1))
    return not (n in (17, 19, 34) or pagina == 'f53r' or 67 <= n <= 86 or pagina == 'f116v')


def lessico(escludi_italiano=0):
    tutte = set()
    for l in LINGUE:
        ps = lingue.parole(l, inizio=escludi_italiano) if (l == 'Italian' and escludi_italiano) else lingue.parole(l)
        c = Counter(piatta(w) for w in ps)
        tutte |= {w for w, n in c.items() if n >= 2 and w}
    return tutte


def segmentabile(s, lex, cache):
    if s in cache:
        return cache[s]
    ok = [True] + [False] * len(s)
    for j in range(1, len(s) + 1):
        for i in range(max(0, j - 15), j - 1):
            if ok[i] and s[i:j] in lex:
                ok[j] = True
                break
    cache[s] = ok[-1]
    return ok[-1]


def misura(tipi, chiave, lex, con_m2):
    tot = sum(tipi.values())
    m1 = m2 = 0
    lung = []
    cache = {}
    for u, n in tipi.items():
        s = ''.join(chiave[x] for x in u)
        if s in lex:
            m1 += n
            lung.append(len(s))
        if con_m2 and segmentabile(s, lex, cache):
            m2 += n
    return m1 / tot, (m2 / tot if con_m2 else None), (sum(lung) / len(lung) if lung else 0)


def casuale(rnd):
    voc = [u for u in CHIAVE if u in VOCALICHE]
    con = [u for u in CHIAVE if u not in VOCALICHE]
    out = {}
    for gruppo in (voc, con):
        uscite = [CHIAVE[u] for u in gruppo]
        rnd.shuffle(uscite)
        out.update(zip(gruppo, uscite))
    return out


def prova(nome, tipi, lex, rnd):
    vero = misura(tipi, CHIAVE, lex, True)
    n1 = [misura(tipi, casuale(rnd), lex, False)[0] for _ in range(CHIAVI_M1)]
    n2 = [misura(tipi, casuale(rnd), lex, True)[1] for _ in range(CHIAVI_M2)]
    q = lambda v, p: sorted(v)[int(p * (len(v) - 1))]
    r = OrderedDict([('parole', sum(tipi.values())), ('tipi', len(tipi)), ('M1', vero[0]), ('M2', vero[1]), ('lunghezza_media_trovate', vero[2]),
                     ('M1_casuali_mediana', q(n1, 0.5)), ('M1_casuali_p95', q(n1, 0.95)), ('M1_casuali_p99', q(n1, 0.99)),
                     ('M1_quota_casuali_maggiori_o_uguali', sum(x >= vero[0] for x in n1) / len(n1)),
                     ('M2_casuali_mediana', q(n2, 0.5)), ('M2_casuali_p95', q(n2, 0.95)), ('M2_casuali_p99', q(n2, 0.99)),
                     ('M2_quota_casuali_maggiori_o_uguali', sum(x >= vero[1] for x in n2) / len(n2))])
    print('%-28s M1 %.3f (casuali med %.3f p99 %.3f, p %.4f) | M2 %.3f (casuali med %.3f p99 %.3f, p %.3f)' % (
        nome, r['M1'], r['M1_casuali_mediana'], r['M1_casuali_p99'], r['M1_quota_casuali_maggiori_o_uguali'],
        r['M2'], r['M2_casuali_mediana'], r['M2_casuali_p99'], r['M2_quota_casuali_maggiori_o_uguali']), flush=True)
    return r


def main():
    if hashlib.sha256(open(os.path.join(CACHE, 'cheshire_2019.pdf'), 'rb').read()).hexdigest() != SHA:
        raise SystemExit('cheshire_2019.pdf diverso da quello preregistrato')
    rnd = random.Random(SEME)
    zl = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    tipi_v, scartate = Counter(), 0
    for r in zl:
        if not fuori_campione(r.pagina):
            continue
        for w in r.parole:
            if not trascrizione.pulita(w):
                continue
            u = unita(w)
            if u is None:
                scartate += 1
            else:
                tipi_v[u] += 1
    print('Voynich fuori campione: %d parole lette, %d scartate (segni fuori chiave)' % (sum(tipi_v.values()), scartate), flush=True)
    esempi = [(' '.join(w for w in r.parole), ' '.join(''.join(CHIAVE[x] for x in (unita(w) or ())) for w in r.parole)) for r in zl if r.pagina == 'f53r'][:4]

    ita = lingue.parole('Italian', max_caratteri=CONTROLLO_CARATTERI)
    tipi_c = Counter()
    for w in ita:
        e = ''.join(INVERSA.get(c, '') for c in piatta(w))
        u = unita(e) if e else None
        if u:
            tipi_c[u] += 1
    lex_c = lessico(escludi_italiano=CONTROLLO_CARATTERI)
    lex_v = lessico()
    ris = OrderedDict()
    ris['esempi_f53r'] = esempi
    ris['controllo: italiano scritto con l\'inverso della chiave'] = prova('controllo italiano', tipi_c, lex_c, rnd)
    ris['Voynich fuori campione'] = prova('Voynich fuori campione', tipi_v, lex_v, rnd)
    ris['parole_scartate_voynich'] = scartate
    c, v = ris['controllo: italiano scritto con l\'inverso della chiave'], ris['Voynich fuori campione']
    valido = c['M1_quota_casuali_maggiori_o_uguali'] == 0 and c['M2_quota_casuali_maggiori_o_uguali'] == 0
    if v['M1'] > v['M1_casuali_p99'] and v['M2'] > v['M2_casuali_p99']:
        esito = 'chiave sostenuta'
    elif v['M1'] <= v['M1_casuali_p95'] and v['M2'] <= v['M2_casuali_p95']:
        esito = 'chiave non sostenuta'
    else:
        esito = 'incerto'
    ris['controllo_valido'], ris['esito'] = valido, esito
    print('controllo valido:', valido, '| esito:', esito)
    with open(os.path.join(RISULTATI, 'e163_cheshire.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e163 — La chiave di Cheshire contro chiavi casuali della stessa forma', '',
           'Lessico: unione dei vocabolari biblici di %s (parole con almeno 2 occorrenze). M1: parole intere nel lessico; '
           'M2: parole risegmentabili in parole del lessico di almeno 2 lettere. Chiavi casuali: uscite rimescolate fra unità, '
           'vocali fra vocali e consonanti fra consonanti (%d per M1, %d per M2). Preregistrazione: `preregistrazioni/e163.md`.' % (', '.join(LINGUE), CHIAVI_M1, CHIAVI_M2), '',
           '| testo | parole | M1 Cheshire | M1 casuali (mediana / 99°) | quota ≥ | M2 Cheshire | M2 casuali (mediana / 99°) | quota ≥ |', '|---|---|---|---|---|---|---|---|']
    for n in ('controllo: italiano scritto con l\'inverso della chiave', 'Voynich fuori campione'):
        r = ris[n]
        out.append('| %s | %d | %.3f | %.3f / %.3f | %.4f | %.3f | %.3f / %.3f | %.3f |' % (n, r['parole'], r['M1'], r['M1_casuali_mediana'], r['M1_casuali_p99'],
                   r['M1_quota_casuali_maggiori_o_uguali'], r['M2'], r['M2_casuali_mediana'], r['M2_casuali_p99'], r['M2_quota_casuali_maggiori_o_uguali']))
    out += ['', 'Prime righe di f53r con la chiave (lui risegmenta e cerca in nove lingue):', '']
    out += ['- `%s` → %s' % e for e in esempi]
    out += ['', 'Controllo valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    with open(os.path.join(RISULTATI, 'e163_cheshire.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
