# -*- coding: utf-8 -*-
"""Esperimento 230: il generatore dell'e224 (configurazione finale) con i meccanismi indicati dagli esperimenti della
notte: parole spezzate alla quota dell'e227b, un lessico di parole nuove che cresce per sezione (e226, e211) e la copia
verticale per posizione fisica (e228/e228b).

Preregistrazione: preregistrazioni/e230.md. Scrive risultati/e230_generatore_meccanismi.json e .md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e110_alternanza as e110
import e106_procedimento_versi as e106
import e135_stato_riga as e135
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e211_parole_proprie as e211
import e224_generatore_completo as e224
import e226_nascita_parole as e226
import e227_unioni_e_legame as e227
import e227b_spezzature as e227b

RISULTATI = os.path.join(QUI, '..', 'risultati')
GAMMA, PHI_FISICA, SEME_SCELTA, SEMI_VERIFICA = (0.05, 0.10), 0.10, 1, (2, 3, 4)
_SEZ = {}
_genera_e224 = e224.genera


def sezioni():
    if not _SEZ:
        for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
            _SEZ.setdefault(r.pagina, r.sezione)
    return _SEZ


def genera(c, prm, seme):
    """Come e224.genera; in piu' (spenti se assenti da prm): 'gamma' (la parola di base viene, con questa probabilita',
    dalle parole nuove gia' generate nelle pagine precedenti della stessa sezione) e 'fisica' (la copia verticale
    prende la parola della riga sopra il cui centro, in unita', e' piu' vicino alla posizione corrente)."""
    rnd = random.Random(seme)
    Dv, mod, att, L, starts, q = c['D'], c['mod'], c['att'], c['L'], c['starts'], c['q']
    lam, k = prm['lam_k']
    gamma, fisica = prm.get('gamma', 0.0), prm.get('fisica', False)
    sez = sezioni()
    lessico = defaultdict(list)
    media = sum(len(Dv(w)) for w in c['voy']) / len(c['voy'])
    h = {f: 0.0 for f in e145.SCELTE}
    righe, storia = [], []
    for pag, d in c['P'].items():
        s_pag = sez.get(pag)
        nuove_pag = []
        lingua = d['lingua'] if d['lingua'] in starts else 'B'
        for f in e145.SCELTE:
            h[f] = (e152.RHO / 2) * h[f] + rnd.gauss(0, e152.SIGMA)
        pool = [w for _, ps in d['righe'] for w in ps[1:] if trascrizione.pulita(w)] or [w for _, ps in d['righe'] for w in ps]
        cnt = Counter(pool)
        tipi = list(cnt)
        pesi_pool = [cnt[t] ** prm['alfa'] for t in tipi]
        lex = lessico[s_pag]

        def estrai():
            if gamma and lex and rnd.random() < gamma:
                return rnd.choice(lex)
            return rnd.choices(tipi, pesi_pool)[0]

        tema = [estrai() for _ in range(e153.K)]
        prima_sopra, sopra = None, None
        for ini, ps in d['righe']:
            for f in e145.SCELTE:
                h[f] = e152.RHO * h[f] + rnd.gauss(0, e152.SIGMA)
            n = len(ps)
            if ini:
                w0 = rnd.choices(*starts[lingua][1])[0]
            else:
                w0 = rnd.choices(*starts[lingua][0])[0]
                for _ in range(10):
                    if prima_sopra is None or Dv(w0)[0] != prima_sopra or rnd.random() >= 0.5:
                        break
                    w0 = rnd.choices(*starts[lingua][0])[0]
            riga = [w0]
            while len(riga) < n:
                pos = len(riga)
                if prm['psi'] and storia and 1 <= pos <= n - 3 and rnd.random() < prm['psi']:
                    src = rnd.choice(storia)
                    if len(src) >= 4:
                        a = rnd.randrange(1, len(src) - 2)
                        m = min(rnd.choice((2, 3)), n - pos, len(src) - a)
                        riga += [e224.variante(x, e153.MU / 2, mod, rnd, prm['nu'], att, Dv) for x in src[a:a + m]]
                        continue
                cand = []
                for j in range(k):
                    if fisica:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi']
                    else:
                        copia = prm['phi'] and sopra and j == 0 and rnd.random() < prm['phi'] and pos < len(sopra)
                    if copia and fisica:
                        x0 = sum(len(Dv(w)) + 1 for w in riga) + media / 2
                        centri, acc = [], 0
                        for w in sopra:
                            centri.append(acc + len(Dv(w)) / 2)
                            acc += len(Dv(w)) + 1
                        base = sopra[min(range(len(sopra)), key=lambda t: abs(centri[t] - x0))]
                    elif copia:
                        base = sopra[pos]
                    else:
                        base = rnd.choice(tema) if rnd.random() < 0.3 else estrai()
                    cand.append(e224.variante(base, e153.MU, mod, rnd, prm['nu'], att, Dv))
                ultimo = Dv(riga[-1])[-1] if trascrizione.pulita(riga[-1]) else None
                pesi = []
                for x in cand:
                    p = (L.get((ultimo, Dv(x)[0]), 0.05) ** lam) if ultimo else 1.0
                    if pos == 1 and Dv(x)[0] in ('ch', 'sh'):
                        p *= e153.BANCO
                    if pos == n - 1 and prm['eta'] and trascrizione.pulita(x):
                        p *= c['rapporto'].get(Dv(x)[-1], 1.0) ** prm['eta']
                    pesi.append(p)
                x = rnd.choices(cand, pesi)[0]
                if prm['sigma'] and pos < n - 1 and len(Dv(x)) >= 4 and rnd.random() < prm['sigma']:
                    s = e224.spezza(x, att, Dv, rnd)
                    if s:
                        riga += s
                        continue
                riga.append(x)
            riga = e145.riscrivi(riga[:n], h, q, rnd)
            if trascrizione.pulita(riga[0]):
                prima_sopra = Dv(riga[0])[0]
            sopra = riga
            storia.append(riga)
            righe.append((pag, ini, riga))
            nuove_pag += [w for w in riga if trascrizione.pulita(w) and w not in att]
        lex.extend(nuove_pag)
    return righe


def misura(args):
    """Le misure dell'e224 (completa) piu' quelle dell'e226 e dell'e227 sullo stesso testo."""
    prm, seme = args
    c = e224.contesto()
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    e227.ESTRAZIONI = 50
    rr = genera(c, prm, seme)
    righe = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(righe, c['voy'], c['soglia_ab'], c['v'], c['vb'])
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in e145.SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, kk = [], 0
    for pag, ini, ps in rr:
        kk += ini
        par.append((pag, kk, ps))
    r['r_righe_consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    per = OrderedDict()
    for pag, ini, ps in rr:
        per.setdefault(pag, []).append((ini, ps))
    _, t = e160.una(('x', list(per.values())))
    for kx, x in t.items():
        r['T ' + kx] = x['z']
    sez = sezioni()
    herb = defaultdict(list)
    for pag, _, ps in rr:
        herb[pag] += [w for w in ps if trascrizione.pulita(w)]
    unita_h = [v for p, v in herb.items() if len(v) >= 60 and sez.get(p) == 'H']
    r['R_parole_proprie'] = e211.prova(unita_h, random.Random(seme))['R'] if unita_h else None
    pagine = [[[w for w in ps if trascrizione.pulita(w)] for _, ps in v] for v in per.values()]
    pagine = [[x for x in p if x] for p in pagine]
    u = e227.unioni(pagine, random.Random(227))
    r['U/N1'], r['U/N2'] = u['N1']['rapporto'], u['N2']['rapporto']
    r['Q'] = e227.legame(pagine)['Q']
    e226.RICAMPIONI = 50
    r['L_nascita'] = e226.nascita([(sez.get(p), [w for x in rr2 for w in x]) for p, rr2 in zip(per, pagine)], c['D'], random.Random(226))['L']
    return json.dumps(prm, default=list), seme, r


def configurazioni():
    """Configurazione finale dell'e224, sigma dall'e227b, esito dell'e228b."""
    j224 = json.load(open(os.path.join(RISULTATI, 'e224_generatore_completo.json'), encoding='utf-8'))
    base = dict(j224['configurazione'])
    base['lam_k'] = tuple(base['lam_k'])
    j227b = json.load(open(os.path.join(RISULTATI, 'e227b_spezzature.json'), encoding='utf-8'))
    if j227b.get('verifica') and not j227b['verifica']['misure']['fuori']:
        sigma = j227b['verifica']['sigma']
    else:
        sigma = min(e227b.GRIGLIA, key=lambda s: (len(j227b['sigma %.2f' % s]['fuori']), e227b.scarto(j227b['sigma %.2f' % s])))
    j228b = json.load(open(os.path.join(RISULTATI, 'e228b_verticale_nullo.json'), encoding='utf-8'))
    return base, sigma, j228b['esito'] == 'copia a vista (fisica)'


def main():
    c = e224.contesto()
    base, sigma, fisica = configurazioni()
    # validita': con i meccanismi nuovi spenti il testo e' identico a quello dell'e224
    identico = genera(c, base, SEME_SCELTA) == _genera_e224(c, base, SEME_SCELTA)
    print('configurazione e224 %s; sigma %.2f; copia fisica %s; identico all\'e224: %s' % (base, sigma, fisica, identico), flush=True)
    v1 = dict(base, sigma=sigma)
    with Pool(int(os.environ.get('PROCESSI', '2'))) as pool:
        scelta = list(pool.imap(misura, [(dict(v1, gamma=g), SEME_SCELTA) for g in GAMMA]))
        punti = [e224.punteggio(r, c)[0] for _, _, r in scelta]
        gamma = GAMMA[max(range(len(GAMMA)), key=lambda i: (punti[i], -i))]
        print('scelta di gamma (seme %d): %s -> %s' % (SEME_SCELTA, dict(zip(GAMMA, punti)), gamma), flush=True)
        varianti = OrderedDict([('V0 e224 finale', base), ('V1 + parole spezzate', v1), ('V2 + lessico per sezione', dict(v1, gamma=gamma))])
        if fisica:
            varianti['V3 + copia verticale fisica'] = dict(v1, gamma=gamma, fisica=True, phi=base['phi'] or PHI_FISICA)
        lavori = [(p, s) for p in varianti.values() for s in SEMI_VERIFICA]
        uscite = list(pool.imap(misura, lavori))
    ris = OrderedDict([('validita_identico', identico), ('sigma', sigma), ('gamma', gamma), ('punti_scelta_gamma', dict(zip(map(str, GAMMA), punti))),
                       ('copia_fisica', fisica)])
    righe_md = []
    for i, (nome, prm) in enumerate(varianti.items()):
        rr = [uscite[i * len(SEMI_VERIFICA) + t][2] for t in range(len(SEMI_VERIFICA))]
        chiavi = [kx for kx, x in rr[0].items() if isinstance(x, (int, float)) and all(isinstance(y.get(kx), (int, float)) for y in rr)]
        mm = {kx: sum(y[kx] for y in rr) / len(rr) for kx in chiavi}
        esiti, riga = e224.valuta(mm, c)
        ris[nome] = OrderedDict([('configurazione', {kx: (list(v) if isinstance(v, tuple) else v) for kx, v in prm.items()}),
                                 ('pagella', sum(esiti.values())), ('riga', riga), ('mancano', [kx for kx, x in esiti.items() if not x]), ('medie', mm)])
        righe_md.append('| %s | %d/18 | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            nome, sum(esiti.values()), 'sì' if riga else 'no', ', '.join(ris[nome]['mancano']) or '—',
            '%.2f' % mm['R_parole_proprie'] if mm.get('R_parole_proprie') is not None else '–',
            '%.2f' % mm['U/N1'], '%.2f' % mm['U/N2'], '%.2f' % mm['Q'], '%.2f' % mm['L_nascita'],
            ', '.join('%s %.1f' % (kx[2:], v) for kx, v in mm.items() if kx.startswith('T '))))
    n0, nl = ris['V0 e224 finale'], ris[list(varianti)[-1]]
    lr = lambda R: abs(math.log(R / 1.96)) if R else float('inf')
    migliora = (identico and nl['riga'] and nl['pagella'] > n0['pagella']
                and lr(nl['medie'].get('R_parole_proprie')) < lr(n0['medie'].get('R_parole_proprie')))
    ris['esito'] = 'non valido' if not identico else ('miglioramento' if migliora else 'nessun miglioramento netto')
    json.dump(ris, open(os.path.join(RISULTATI, 'e230_generatore_meccanismi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e230 — Il generatore con i meccanismi della notte', '',
          'Medie sui semi 2–4. σ = %.2f (e227b); γ = %s (scelto sul seme 1 fra %s); copia verticale fisica: %s (e228b). '
          'Validità (meccanismi spenti = e224): %s. Preregistrazione: `preregistrazioni/e230.md`.' % (
              sigma, gamma, GAMMA, 'sì' if fisica else 'no', 'sì' if identico else 'NO'), '',
          'Voynich: R parole proprie 1,96; U/N1 1,29; U/N2 1,16; Q 0,67; L nascita 1,56.', '',
          '| variante | pagella | riga | mancano | R | U/N1 | U/N2 | Q | L | T (z) |', '|---|---|---|---|---|---|---|---|---|---|'] + righe_md
    md += ['', 'Esito: **%s**.' % ris['esito']]
    open(os.path.join(RISULTATI, 'e230_generatore_meccanismi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(ris['esito'])


if __name__ == '__main__':
    main()
