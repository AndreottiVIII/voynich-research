# -*- coding: utf-8 -*-
"""Esperimento 128: le proprieta' di riga del Voynich nei testi senza senso scritti a mano da volontari (Gaskell e
Bowern 2022), a parita' di dimensione con Voynich, Timm e Schinner e lingue.

Preregistrazione: preregistrazioni/e128.md. Scrive risultati/e128_scrittura_inventata.json e .md.
"""
import hashlib, json, os, random, statistics, sys, zipfile
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e83_evitamento_inizi as e83
import e110_alternanza as e110
import e114_accordo_terminazioni as e114

RISULTATI = os.path.join(QUI, '..', 'risultati')
ZIP = os.path.join(QUI, '..', 'dati', 'cache', 'gaskell_bowern', 'data', 'gibberish_transcriptions.zip')
SHA = 'a4bfa58af956603ab6607227ad640e01cb695c7b492c6914488bd30f6d0aebbe'
SEMI = range(1, 11)
SEME, RIMESCOLAMENTI = 128, 50
D = misure.divisore(misure.GLIFI_EVA)
PROPRIETA = ('bordo d\'inizio', 'S(1)', 'accordo a distanza 2', 'lunghezze vicine', 'ripetizione immediata', 'alternanza A', 'chiusura R')


def inventati():
    dati = open(ZIP, 'rb').read()
    if hashlib.sha256(dati).hexdigest() != SHA:
        raise SystemExit('archivio di Gaskell e Bowern diverso da quello preregistrato')
    out = []
    with zipfile.ZipFile(ZIP) as z:
        for k, nome in enumerate(sorted(n for n in z.namelist() if n.endswith('.txt'))):
            b = z.read(nome)
            try:
                testo = b.decode('utf-8')
            except UnicodeDecodeError:
                testo = b.decode('latin-1')
            nuovo = True
            for l in testo.splitlines():
                s = l.strip()
                if not s or set(s) <= set('_-'):
                    nuovo = True
                    continue
                ps = [''.join(c for c in w.lower() if c.isalpha()) for w in s.split()]
                ps = [w for w in ps if w]
                if ps:
                    out.append((k, nuovo, ps))
                    nuovo = False
    return out


def parole(righe):
    return sum(len(ps) for _, _, ps in righe)


def sottoinsiemi(righe, n_parole):
    pagine = OrderedDict()
    for r in righe:
        pagine.setdefault(r[0], []).append(r)
    chiavi = list(pagine)
    out = []
    for s in SEMI:
        rnd = random.Random(s)
        ordine = chiavi[:]
        rnd.shuffle(ordine)
        scelte, n = [], 0
        for c in ordine:
            if n >= n_parole:
                break
            scelte.append(c)
            n += sum(len(ps) for _, _, ps in pagine[c])
        scelte = set(scelte)
        out.append([r for r in righe if r[0] in scelte])
    return out


def lunghezze_vicine(rr, dividi, rnd):
    def corr(righe):
        xs, ys = [], []
        for ps in righe:
            ll = [len(dividi(w)) for w in ps]
            xs.extend(ll[:-1])
            ys.extend(ll[1:])
        mx, my = statistics.mean(xs), statistics.mean(ys)
        cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
        vx, vy = sum((a - mx) ** 2 for a in xs), sum((b - my) ** 2 for b in ys)
        return cov / (vx * vy) ** 0.5 if vx and vy else 0.0
    righe = [ps for ps in rr if len(ps) >= 2]
    reale = corr(righe)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for ps in righe:
            ps = ps[:]
            rnd.shuffle(ps)
            mes.append(ps)
        nulli.append(corr(mes))
    return reale - statistics.mean(nulli)


def ripetizione(rr, rnd):
    def quota(righe):
        cc = [(a, b) for ps in righe for a, b in zip(ps, ps[1:])]
        return sum(a == b for a, b in cc) / len(cc)
    righe = [ps for ps in rr if len(ps) >= 2]
    reale = quota(righe)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for ps in righe:
            ps = ps[:]
            rnd.shuffle(ps)
            mes.append(ps)
        nulli.append(quota(mes))
    m = statistics.mean(nulli)
    return reale / m if m else None


def misura(args):
    nome, righe, quale = args
    e71.RIMESCOLAMENTI = RIMESCOLAMENTI
    e83.PERMUTAZIONI = 200
    e110.RIMESCOLAMENTI = RIMESCOLAMENTI
    e110.MIN_PAROLE = 4
    e114.RIMESCOLAMENTI = RIMESCOLAMENTI
    e114.MIN_PAROLE = 4
    dividi = e71.lettere if quale == 'lettere' else D
    rnd = random.Random(SEME)
    r = OrderedDict()
    r["bordo d'inizio"] = e71.una(('x', [(ini, ps) for _, ini, ps in righe], quale))[1]['jsd_inizio']['rapporto']
    per, par = OrderedDict(), 0
    for pag, ini, ps in righe:
        par += ini
        per.setdefault(pag, []).append((par, ini, ps[0] if ps else None))
    r['S(1)'] = e83.misura(per, 1, lambda w: dividi(w)[0], rnd)['S']
    r['accordo a distanza 2'] = e114.una(('x', [ps for _, _, ps in righe], quale))[1]['k2']['eccesso']
    r['lunghezze vicine'] = lunghezze_vicine([ps for _, _, ps in righe], dividi, rnd)
    r['ripetizione immediata'] = ripetizione([ps for _, _, ps in righe], rnd)
    r['alternanza A'] = e110.una(('x', [ps for _, _, ps in righe], quale))[1]['senza identiche']['A']
    r['chiusura R'] = e74.una(('x', righe, quale))[1]['R']
    return nome, r


def bibbia(chiave):
    ps = lingue.parole(chiave)
    out = []
    righe = [ps[i:i + 6] for i in range(0, len(ps), 6)]
    for k, r in enumerate(righe):
        out.append((k // 50, k % 10 == 0, r))
    return out


def main():
    gib = inventati()
    n = parole(gib)
    print('testi senza senso: %d pagine, %d righe, %d parole' % (len({p for p, _, _ in gib}), len(gib), n), flush=True)
    voy = [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    ts = [(i // 29, ini, ps) for i, (ini, ps) in enumerate(e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')))]
    lavori = [('testi senza senso', gib, 'lettere')]
    for nome, rr, q in (('Voynich', voy, 'eva'), ('Timm e Schinner', ts, 'eva'), ('Bibbia latina', bibbia('Latin'), 'lettere'),
                        ('Bibbia italiana', bibbia('Italian'), 'lettere')):
        for s, sub in zip(SEMI, sottoinsiemi(rr, n)):
            lavori.append(('%s %d' % (nome, s), sub, q))
    per = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(misura, lavori):
            per[nome] = r
            print('%-20s %s' % (nome, ' | '.join('%s %.3f' % (k, v if v is not None else float('nan')) for k, v in r.items())), flush=True)

    def gruppo(prefissi):
        return [r for nome, r in per.items() if any(nome.startswith(p + ' ') for p in prefissi)]
    G = per['testi senza senso']
    V, T, L = gruppo(['Voynich']), gruppo(['Timm e Schinner']), gruppo(['Bibbia latina', 'Bibbia italiana'])
    tabella = OrderedDict()
    for p in PROPRIETA:
        vv = [r[p] for r in V if r[p] is not None]
        ll = [r[p] for r in L if r[p] is not None]
        tt = [r[p] for r in T if r[p] is not None]
        discr = max(vv) < min(ll) or max(ll) < min(vv)
        mv, ml, mt = statistics.mean(vv), statistics.mean(ll), statistics.mean(tt)
        g = G[p]
        tabella[p] = OrderedDict([('Voynich', [mv, min(vv), max(vv)]), ('lingue', [ml, min(ll), max(ll)]), ('Timm e Schinner', [mt, min(tt), max(tt)]),
                                  ('testi senza senso', g), ('discriminante', discr),
                                  ('senza_senso_lato_Voynich', g is not None and abs(g - mv) < abs(g - ml)),
                                  ('TS_lato_Voynich', abs(mt - mv) < abs(mt - ml))])
    d = [p for p in PROPRIETA if tabella[p]['discriminante']]
    ng = sum(tabella[p]['senza_senso_lato_Voynich'] for p in d)
    nt = sum(tabella[p]['TS_lato_Voynich'] for p in d)
    if d and ng >= 2 * len(d) / 3:
        esito = 'riproduce la struttura di riga'
    elif not d or ng < len(d) / 3:
        esito = 'non la riproduce'
    else:
        esito = 'in parte'
    print('proprieta discriminanti %d | testi senza senso dalla parte del Voynich %d | Timm e Schinner %d | esito: %s' % (len(d), ng, nt, esito))
    ris = OrderedDict([('parole', n), ('per_testo', per), ('tabella', tabella), ('discriminanti', d), ('senza_senso_lato_Voynich', ng),
                       ('TS_lato_Voynich', nt), ('esito', esito)])
    with open(os.path.join(RISULTATI, 'e128_scrittura_inventata.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    f = lambda x: '%.3f (%.3f–%.3f)' % tuple(x)
    out = ['# e128 — Il Voynich e la scrittura inventata da persone', '',
           'Testi senza senso scritti a mano da volontari (Gaskell e Bowern 2022, %d parole) contro 10 sottoinsiemi della stessa '
           'dimensione di Voynich, Timm e Schinner e Bibbie latina e italiana. Media (min–max). Preregistrazione: '
           '`preregistrazioni/e128.md`.' % n, '',
           '| proprietà | Voynich | lingue | Timm e Schinner | testi senza senso | discriminante | senza senso dalla parte del Voynich | TS dalla parte del Voynich |',
           '|---|---|---|---|---|---|---|---|']
    for p, t in tabella.items():
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (p, f(t['Voynich']), f(t['lingue']), f(t['Timm e Schinner']),
                                                             '%.3f' % t['testi senza senso'] if t['testi senza senso'] is not None else '–',
                                                             'sì' if t['discriminante'] else 'no', 'sì' if t['senza_senso_lato_Voynich'] else 'no',
                                                             'sì' if t['TS_lato_Voynich'] else 'no'))
    out += ['', 'Proprietà discriminanti: %d. Testi senza senso dalla parte del Voynich: **%d**; Timm e Schinner: **%d**. Esito: **%s**.' % (len(d), ng, nt, esito),
            '', 'Fonte dei testi senza senso: Gaskell, D. E., Bowern, C. L. (2022), *Gibberish after all? Voynichese is statistically similar to '
            'human-produced samples of meaningless text*, CEUR Workshop Proceedings 3313; dati: github.com/danielgaskell/voynich (commit d076a7d).']
    with open(os.path.join(RISULTATI, 'e128_scrittura_inventata.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
