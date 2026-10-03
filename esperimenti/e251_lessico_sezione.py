# -*- coding: utf-8 -*-
"""Esperimento 251 (passo 2 del piano 18/18, integrazione del 3/10/2026): il generatore dell'e241 con il lessico di sezione
gia' presente in e233.genera (gamma: con questa probabilita' la base viene dalle forme non attestate gia' scritte nelle pagine
precedenti della stessa sezione). Braccio di controllo e241 (gamma 0) sugli stessi semi; scelta di gamma sul seme 1; verifica
sui semi 7, 8, 9 con pagella, R delle parole rare, discriminatori dell'e231 e dell'e266, profilo, diagnosi delle rare confinate.
Il modulo contiene anche gli interruttori di riga usati dall'e252 e contesto(), usato da e243b ed e276: restano invariati.

Preregistrazione: preregistrazioni/e251.md (integrazione in fondo). Scrive risultati/e251_lessico_sezione.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e135_stato_riga as e135
import e145_abitudini as e145
import e146_deriva_preferenze as e146
import e206_segni_facoltativi as e206
import e211_parole_proprie as e211
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e240_operatore_empirico as e240
import e241_operatore_contesto as e241
import e243_riuso_esplicito as e243
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
GAMMA = (0.1, 0.2, 0.3, 0.45, 0.6)
SEME_SCELTA, SEME_REPLICA, SEMI_VERIFICA = 1, 2, (7, 8, 9)
CONF = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2)
R_VOYNICH, SOGLIA_R, COSTO_AUC, TOLL_AUC = 1.96, 5.0, 0.05, 0.001
E241_SEME_2 = (16, True, ['ripetizione', 'verticale'], 0.8620086266052347)
D = e237.D


# ------------------------------------------------------------------ interruttori di riga (usati dall'e252)

def interruttori_voynich(classi):
    """Per ogni classe: tasso di forme lunghe nel Voynich e mappe lunga <-> corta fra parole attestate (>= 3 volte)."""
    freq = Counter(w for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) for w in r.parole if trascrizione.pulita(w))
    attestate = {w for w, c in freq.items() if c >= e206.MIN_TIPO}
    lunga, corte = defaultdict(dict), defaultdict(lambda: defaultdict(list))
    for w in sorted(attestate):
        u = D(w)
        for i, g in enumerate(u):
            corta = ''.join(u[:i] + u[i + 1:])
            if corta and corta in attestate:
                pos = 'iniziale' if i == 0 else ('finale' if i == len(u) - 1 else 'interna')
                nome = '%s %s' % (g, pos)
                if nome in classi:
                    lunga[w][nome] = corta
                    corte[corta][nome].append(w)
    tassi = {}
    for c in classi:
        n1 = sum(freq[w] for w in lunga if c in lunga[w])
        n0 = sum(freq[w] for w in corte if c in corte[w])
        tassi[c] = n1 / (n1 + n0) if n1 + n0 else 0.5
    corte = {w: {c: sorted(v, key=lambda x: -freq[x])[0] for c, v in d.items()} for w, d in corte.items()}
    return tassi, dict(lunga), corte


def applica_interruttori(riga, stato, interruttori, rnd):
    tassi, lunga, corte = interruttori
    out = []
    for w in riga:
        cl = sorted(set(lunga.get(w, {})) | set(corte.get(w, {})))
        if not cl:
            out.append(w)
            continue
        c = rnd.choice(cl)
        b = min(max(tassi[c], 1e-3), 1 - 1e-3)
        p = 1 / (1 + math.exp(-(math.log(b / (1 - b)) + stato[c])))
        vuole_lunga = rnd.random() < p
        if vuole_lunga and c in corte.get(w, {}):
            out.append(corte[w][c])
        elif not vuole_lunga and c in lunga.get(w, {}):
            out.append(lunga[w][c])
        else:
            out.append(w)
    return out


def contesto():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=e241.OperatoreContesto(ripiego, e241.operazioni_contesto(pv)))
    return c, c2, freq, vpag, rif, pv



# ------------------------------------------------------------------ generatore e misure

def righe(c2, freq, gamma, seme):
    """Testo dell'e241 con il lessico di sezione gamma: (grezzo, dopo spezzature e prefissi staccati)."""
    grezzo = e233.genera(c2, dict(CONF, gamma=gamma), seme)
    return grezzo, e236.dopo(grezzo, freq, 100 + seme)


def righe_ini(rr):
    out = OrderedDict()
    for pag, ini, ps in rr:
        out.setdefault(pag, []).append((bool(ini), ps))
    return out


def ripetizioni_immediate(gp):
    cp = [(a, b) for rr in gp.values() for r in rr for a, b in zip(r, r[1:])]
    return sum(a == b for a, b in cp) / len(cp)


def pagella_grezza(c, rr):
    """Come e236.pagella, restituendo anche i valori grezzi delle misure dietro le proprieta'."""
    e110.RIMESCOLAMENTI = 50
    e135.PERM = 300
    rg = [(ini, ps) for _, ini, ps in rr]
    r = e106.misura(rg, c['voy'], c['soglia_ab'], c['v'], c['vb'])
    _, a = e110.una(('x', [ps for _, ps in rg], 'eva'))
    r['A'] = a['senza identiche']['A']
    _, s = e135.una(('x', [(pag, ps) for pag, _, ps in rr], False))
    r['scelte_per_riga'] = sum((s['varianza_per_riga'][e135.SCELTE[f]]['z'] or 0) > 3 for f in e145.SCELTE if e135.SCELTE[f] in s['varianza_per_riga'])
    par, kk = [], 0
    for pag, ini, ps in rr:
        kk += ini
        par.append((pag, kk, ps))
    r['r_righe_consecutive'] = e146.corr(e146.gruppi_coppie(par)['dentro la pagina, d=1'], e146.residui(par))
    esiti, riga = e224.valuta(r, c)
    numero = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    valori = OrderedDict((k, v) for k, v in r.items() if numero(v))
    voy = OrderedDict((k, c['v'][k]) for k in valori if k in c['v'] and numero(c['v'][k]))
    return OrderedDict([('pagella', sum(esiti.values())), ('riga', riga), ('mancano', [k for k, x in esiti.items() if not x]),
                        ('valori', valori), ('valori_Voynich', voy)])


_SEZ_ZL = {}


def unita_erbario(rr):
    """Le unita' di e243.R_rare: pagine dell'erbario (sezione H della ZL) con almeno 60 parole pulite."""
    if not _SEZ_ZL:
        _SEZ_ZL.update({x.pagina: x.sezione for x in trascrizione.testo_corrente(trascrizione.leggi('ZL'))})
    herb = defaultdict(list)
    for pag, _, ps in rr:
        herb[pag] += [w for w in ps if trascrizione.pulita(w)]
    nomi = [p for p, v in herb.items() if len(v) >= 60 and _SEZ_ZL.get(p) == 'H']
    return nomi, [herb[p] for p in nomi]


def R_completo(rr, controllo=True):
    nomi, unita = unita_erbario(rr)
    r = e211.prova(unita, random.Random(211))
    r['confinate'] = round(r['C'] * r['rare']) if r['C'] is not None else None
    r['sparse'] = r['rare'] - r['confinate'] if r['confinate'] is not None else None
    if controllo:
        r['uguale_R_rare'] = r['R'] == e243.R_rare(rr)
    return r


def ricircolo(c, grezzo):
    """Quota delle occorrenze pulite non attestate gia' comparse in una pagina precedente della stessa sezione."""
    sez, att = e230.sezioni(), c['att']
    per_pag = OrderedDict()
    for pag, _, ps in grezzo:
        per_pag.setdefault(pag, []).extend(w for w in ps if trascrizione.pulita(w) and w not in att)
    viste, gia, tot = defaultdict(set), 0, 0
    for pag, ws in per_pag.items():
        s = sez.get(pag)
        gia += sum(w in viste[s] for w in ws)
        tot += len(ws)
        viste[s].update(ws)
    return gia / tot if tot else 0.0


_PAGINE_VERE = {}


def diagnosi(c, grezzo, rr):
    att = c['att']
    if not _PAGINE_VERE:
        for p, d in c['P'].items():
            for _, ps in d['righe']:
                for w in ps:
                    _PAGINE_VERE.setdefault(w, set()).add(p)
    nomi, unita = unita_erbario(rr)
    freq = Counter(w for u in unita for w in u)
    dove = defaultdict(set)
    for p, u in zip(nomi, unita):
        for w in u:
            dove[w].add(p)
    grezzo_pag = defaultdict(set)
    for pag, _, ps in grezzo:
        grezzo_pag[pag].update(w for w in ps if trascrizione.pulita(w))
    posizioni = defaultdict(list)
    for pag, _, ps in rr:
        for i, w in enumerate(x for x in ps if trascrizione.pulita(x)):
            posizioni[(pag, w)].append(i)
    origini = Counter()
    for w, n in freq.items():
        if not 2 <= n <= 5 or len(dove[w]) != 1:
            continue
        p = next(iter(dove[w]))
        if w not in grezzo_pag[p]:
            origini['creata_da_dopo'] += 1
        elif all(i == 0 for i in posizioni[(p, w)]):
            origini['inizio_riga'] += 1
        elif w not in att:
            origini['forma_nuova'] += 1
        elif _PAGINE_VERE.get(w) == {p}:
            origini['propria_pagina_vera'] += 1
        else:
            origini['altra_attestata'] += 1
    pulite = [w for _, _, ps in grezzo for w in ps if trascrizione.pulita(w)]
    sez = e230.sezioni()
    nuove_h = Counter(w for pag, _, ps in grezzo if sez.get(pag) == 'H' for w in ps if trascrizione.pulita(w) and w not in att)
    prima_h = nomi[0] if nomi else None
    return OrderedDict([
        ('a_ricircolo', ricircolo(c, grezzo)),
        ('b_confinate_per_origine', OrderedDict((k, origini[k]) for k in ('creata_da_dopo', 'inizio_riga', 'forma_nuova', 'propria_pagina_vera', 'altra_attestata'))),
        ('c_quota_non_attestate', sum(w not in att for w in pulite) / len(pulite)),
        ('d_forme_nuove_oltre_5_erbario', sum(n > 5 for n in nuove_h.values())),
        ('d_massimo_forma_nuova_erbario', max(nuove_h.values()) if nuove_h else 0),
        ('e_lessico_H_occorrenze', sum(nuove_h.values())),
        ('e_lessico_H_tipi', len(nuove_h)),
        ('confinate_prima_pagina_H', sum(1 for w, n in freq.items() if 2 <= n <= 5 and dove[w] == {prima_h})),
    ])


# ------------------------------------------------------------------ lavori (anche in parallelo)

_CTX = {}


def _prepara():
    if not _CTX:
        c, c2, freq, vpag, rif, pv = contesto()
        vi = e266.voynich_ini()
        rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
        vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
        _CTX.update(c=c, c2=c2, freq=freq, vpag=vpag, rif=rif, pv=pv, vt266=vt266, rif266=rif266)
    return _CTX


def lavoro(args):
    """('scelta' | 'completa', gamma, seme) -> misure. Ogni lavoro rigenera il suo testo: il risultato non dipende da PROCESSI."""
    tipo, gamma, seme = args
    k = _prepara()
    c = k['c']
    grezzo, rr = righe(k['c2'], k['freq'], gamma, seme)
    out = OrderedDict([('gamma', gamma), ('seme', seme), ('pagella', pagella_grezza(c, rr)), ('R_parole_rare', R_completo(rr))])
    if tipo == 'scelta':
        out['ricircolo'] = ricircolo(c, grezzo)
        return args, out
    gp = e232.pagine_di(rr)
    d231 = e231.confronto(k['vpag'], gp, k['rif'])
    out['AUC_e231'] = d231['AUC']
    out['piu_pesanti_e231'] = d231['piu_pesanti']
    out['AUC_e266'] = e266.confronto(k['vt266'], e266.tabella(righe_ini(rr), k['rif266']))['AUC']
    out['profilo'] = e237.profilo(gp)
    out['descrittive'] = e234.descrittive(gp)
    out['ripetizioni_immediate'] = ripetizioni_immediate(gp)
    out['diagnosi'] = diagnosi(c, grezzo, rr)
    return args, out


def tutti(lavori):
    n = int(os.environ.get('PROCESSI', '1'))
    if n <= 1:
        return dict(lavoro(a) for a in lavori)
    with Pool(n) as pool:
        return dict(pool.imap_unordered(lavoro, lavori))


def main():
    k = _prepara()
    c, c2, freq, vpag, rif = k['c'], k['c2'], k['freq'], k['vpag'], k['rif']
    val = OrderedDict()

    # V1: replica dell'e241 sul seme 2 (si riporta, non ferma la corsa)
    _, rr2 = righe(c2, freq, 0.0, SEME_REPLICA)
    uff = e236.pagella(c, rr2)
    pg2 = pagella_grezza(c, rr2)
    auc2 = e231.confronto(vpag, e232.pagine_di(rr2), rif)['AUC']
    copia_ok = (pg2['pagella'], pg2['riga'], pg2['mancano']) == (uff['pagella'], uff['riga'], uff['mancano'])
    replica_ok = (pg2['pagella'], pg2['riga'], pg2['mancano']) == E241_SEME_2[:3] and abs(auc2 - E241_SEME_2[3]) <= TOLL_AUC
    val['replica_e241_seme_2'] = OrderedDict([('pagella', pg2['pagella']), ('riga', pg2['riga']), ('mancano', pg2['mancano']),
                                              ('AUC_e231', auc2), ('ok', replica_ok), ('copia_pagella_ok', copia_ok)])
    print('V1 replica e241 seme 2: %d/18 riga %s mancano %s AUC %.4f -> %s (copia pagella %s)' % (
        pg2['pagella'], pg2['riga'], pg2['mancano'], auc2, replica_ok, copia_ok), flush=True)

    # V2: con gamma 0 il testo e' quello dell'e241 (scritto in chiaro, non tramite CONF)
    grezzo1, rr1 = righe(c2, freq, 0.0, SEME_SCELTA)
    rif_grezzo = e233.genera(c2, dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2), SEME_SCELTA)
    identico = OrderedDict([('grezzo', grezzo1 == rif_grezzo), ('dopo', rr1 == e236.dopo(rif_grezzo, freq, 100 + SEME_SCELTA))])
    val['identico_e241_gamma_0'] = identico
    print("V2 gamma 0 identico all'e241: %s" % dict(identico), flush=True)

    # controllo del metro: R delle parole rare del Voynich con la stessa funzione
    rv = R_completo([(p, ini, ps) for p, d in c['P'].items() for ini, ps in d['righe']], controllo=False)
    val['R_Voynich'] = rv
    print('R delle parole rare del Voynich: %.3f (C %.4f, atteso %.4f, rare %d, unita %d)' % (rv['R'], rv['C'], rv['atteso'], rv['rare'], rv['unita']), flush=True)

    # scelta di gamma sul seme 1 (gamma 0 compreso, per P*)
    sc = tutti([('scelta', g, SEME_SCELTA) for g in (0.0,) + GAMMA])
    scelta = OrderedDict()
    for g in (0.0,) + GAMMA:
        x = sc[('scelta', g, SEME_SCELTA)]
        scelta['gamma %.2f' % g] = x
        print('seme 1, gamma %.2f: pagella %d/18 riga %s | R rare %s | ricircolo %.3f' % (
            g, x['pagella']['pagella'], x['pagella']['riga'], x['R_parole_rare']['R'], x['ricircolo']), flush=True)
    P = max(scelta[n]['pagella']['pagella'] for n in scelta)
    riga_e241 = scelta['gamma 0.00']['pagella']['riga']

    def ammesso(g):
        x = scelta['gamma %.2f' % g]
        return (x['pagella']['pagella'] >= P - 1 and (x['pagella']['riga'] or not riga_e241)
                and x['R_parole_rare']['R'] is not None and x['R_parole_rare']['R'] > 0)
    ammessi = [g for g in GAMMA if ammesso(g)]
    gs = min(ammessi, key=lambda g: (abs(math.log(scelta['gamma %.2f' % g]['R_parole_rare']['R'] / R_VOYNICH)), g)) if ammessi else 0.1
    print('P* %d, ammessi %s -> gamma* %.2f' % (P, ammessi, gs), flush=True)

    # V3: il meccanismo agisce
    attivo = scelta['gamma %.2f' % gs]['ricircolo'] > scelta['gamma 0.00']['ricircolo']
    val['meccanismo_attivo'] = OrderedDict([('ricircolo_gamma_0', scelta['gamma 0.00']['ricircolo']),
                                            ('ricircolo_gamma_scelto', scelta['gamma %.2f' % gs]['ricircolo']), ('ok', attivo)])

    # seme 1 completo e verifica sui semi 7, 8, 9, due bracci
    lavori = [('completa', g, s) for s in (SEME_SCELTA,) + SEMI_VERIFICA for g in (0.0, gs)]
    cm = tutti(lavori)
    seme_1 = OrderedDict([('base', cm[('completa', 0.0, SEME_SCELTA)]), ('gamma', cm[('completa', gs, SEME_SCELTA)])])
    ver = []
    for s in SEMI_VERIFICA:
        b, g = cm[('completa', 0.0, s)], cm[('completa', gs, s)]
        mb, mg = set(b['pagella']['mancano']), set(g['pagella']['mancano'])
        ver.append(OrderedDict([('seme', s), ('base', b), ('gamma', g), ('guadagnate', sorted(mb - mg)), ('perse', sorted(mg - mb))]))
        for nome, x in (('base', b), ('gamma %.2f' % gs, g)):
            print('seme %d %-10s: pagella %d/18 riga %s mancano %s | R rare %.1f | AUC e231 %.3f e266 %.3f' % (
                s, nome, x['pagella']['pagella'], x['pagella']['riga'], x['pagella']['mancano'], x['R_parole_rare']['R'] or float('nan'),
                x['AUC_e231'], x['AUC_e266']), flush=True)

    # V4: coerenza con il braccio "globale" dell'e276 (se c'e')
    p276 = os.path.join(RISULTATI, 'e276_parametri_sezione.json')
    coer = OrderedDict([('disponibile', os.path.exists(p276))])
    v4 = True
    if coer['disponibile']:
        glob = {x['seme']: x['globale'] for x in json.load(open(p276, encoding='utf-8'))['verifica']}
        for v in ver:
            g276, b = glob.get(v['seme']), v['base']
            ok = None if g276 is None else (g276['pagella'] == b['pagella']['pagella'] and g276['riga'] == b['pagella']['riga']
                                            and list(g276['mancano']) == b['pagella']['mancano']
                                            and abs(g276['AUC_e231'] - b['AUC_e231']) <= TOLL_AUC and abs(g276['AUC_e266'] - b['AUC_e266']) <= TOLL_AUC)
            coer['seme %d' % v['seme']] = ok
            v4 = v4 and ok is not False
    val['coerenza_e276'] = coer

    media = lambda braccio, f: statistics.mean(f(v[braccio]) for v in ver)
    medie = OrderedDict()
    for braccio in ('base', 'gamma'):
        Rs = [v[braccio]['R_parole_rare']['R'] for v in ver]
        medie[braccio] = OrderedDict([('pagella_somma', sum(v[braccio]['pagella']['pagella'] for v in ver)),
                                      ('pagella_media', media(braccio, lambda x: x['pagella']['pagella'])),
                                      ('semi_con_riga', sum(bool(v[braccio]['pagella']['riga']) for v in ver)),
                                      ('R_parole_rare_media', statistics.mean(Rs) if None not in Rs else None),
                                      ('AUC_e231_media', media(braccio, lambda x: x['AUC_e231'])),
                                      ('AUC_e266_media', media(braccio, lambda x: x['AUC_e266']))])
    mb, mg = medie['base'], medie['gamma']
    motivi = []
    if mg['R_parole_rare_media'] is None or mg['R_parole_rare_media'] > SOGLIA_R:
        motivi.append('R')
    if mg['pagella_somma'] < mb['pagella_somma']:
        motivi.append('pagella')
    if mg['semi_con_riga'] < mb['semi_con_riga']:
        motivi.append('riga')
    if not (identico['grezzo'] and identico['dopo']):
        esito = "non valido: γ 0 diverso dall'e241"
    elif not attivo:
        esito = 'non valido: meccanismo inattivo'
    elif not v4:
        esito = "non valido: braccio di controllo diverso dall'e276"
    else:
        esito = 'passo superato' if not motivi else 'non superato: ' + ' + '.join(motivi)
    superato = esito == 'passo superato'
    costo = superato and mg['AUC_e231_media'] - mb['AUC_e231_media'] > COSTO_AUC
    ris = OrderedDict([('validita', val), ('scelta_seme_1', scelta), ('P_star', P), ('ammessi', ammessi), ('gamma', gs),
                       ('seme_1_completo', seme_1), ('verifica', ver), ('medie', medie),
                       ('pagella_media', mg['pagella_media']), ('pagella_media_base', mb['pagella_media']),
                       ('R_parole_rare_media', mg['R_parole_rare_media']), ('AUC_e231_media', mg['AUC_e231_media']),
                       ('AUC_e266_media', mg['AUC_e266_media']), ('esito', esito), ('motivo', motivi), ('costo_AUC', costo),
                       ('base_non_replicata', not replica_ok),
                       ('gamma_per_e252', gs if superato else 0.0),
                       ('pagella_media_per_e252', mg['pagella_media'] if superato else mb['pagella_media'])])
    json.dump(ris, open(os.path.join(RISULTATI, 'e251_lessico_sezione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    scrivi_md(ris, rv)
    print(esito, flush=True)


def scrivi_md(ris, rv):
    v, gs = ris['validita'], ris['gamma']
    f = lambda x, d=3: ('%.' + str(d) + 'f') % x if isinstance(x, (int, float)) and x is not None else '—'
    md = ['# e251 — Passo 2 del piano 18/18 sopra l\'e241: lessico di sezione', '',
          "Generatore dell'e241 con γ (base presa, con questa probabilità, dalle forme non attestate già scritte nelle pagine precedenti della stessa "
          'sezione). γ scelto sul seme 1 fra %s: **%.2f**. Preregistrazione: `preregistrazioni/e251.md` (integrazione del 3/10/2026).' % (list(GAMMA), gs), '',
          '## Validità', '', '| controllo | esito |', '|---|---|',
          "| V1 replica dell'e241 sul seme 2 (16/18, ripetizione e verticale, AUC 0,862) | %s (%d/18, %s, AUC %s) |" % (
              'sì' if v['replica_e241_seme_2']['ok'] else 'NO', v['replica_e241_seme_2']['pagella'], ', '.join(v['replica_e241_seme_2']['mancano']),
              f(v['replica_e241_seme_2']['AUC_e231'], 4)),
          "| V2 γ 0 identico all'e241 (grezzo, dopo) | %s, %s |" % tuple('sì' if v['identico_e241_gamma_0'][k] else 'NO' for k in ('grezzo', 'dopo')),
          '| V3 meccanismo attivo (ricircolo γ 0 → γ*) | %s (%s → %s) |' % ('sì' if v['meccanismo_attivo']['ok'] else 'NO',
                                                                        f(v['meccanismo_attivo']['ricircolo_gamma_0']), f(v['meccanismo_attivo']['ricircolo_gamma_scelto'])),
          "| V4 coerenza con l'e276 | %s |" % ', '.join('%s: %s' % (k, x) for k, x in v['coerenza_e276'].items()),
          '| R delle parole rare del Voynich (atteso 1,96) | %s (C %s, atteso %s, rare %d) |' % (f(rv['R']), f(rv['C'], 4), f(rv['atteso'], 4), rv['rare']), '',
          '## Scelta sul seme 1', '', '| γ | pagella | riga | R parole rare | ricircolo |', '|---|---|---|---|---|']
    for n, x in ris['scelta_seme_1'].items():
        md.append('| %s | %d/18 | %s | %s | %s |' % (n.split()[1], x['pagella']['pagella'], 'sì' if x['pagella']['riga'] else 'no', f(x['R_parole_rare']['R'], 1), f(x['ricircolo'])))
    md += ['', 'P* %d; ammessi %s; scelto γ* %.2f.' % (ris['P_star'], ris['ammessi'], gs), '',
           '## Verifica (semi 7, 8, 9)', '',
           '| seme | braccio | pagella | riga | mancano | R rare | C | atteso | rare | confinate | AUC e231 | AUC e266 | R | V | F | A | N | ripetizioni |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in ris['verifica']:
        for br, nome in (('base', 'e241'), ('gamma', 'γ %.2f' % gs)):
            y = x[br]
            r, p = y['R_parole_rare'], y['profilo']
            md.append('| %d | %s | %d/18 | %s | %s | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                x['seme'], nome, y['pagella']['pagella'], 'sì' if y['pagella']['riga'] else 'no', ', '.join(y['pagella']['mancano']) or '—',
                f(r['R'], 1), f(r['C'], 4), f(r['atteso'], 4), r['rare'], r['confinate'], f(y['AUC_e231']), f(y['AUC_e266']),
                *('%.1f%%' % (100 * p[k]) for k in e237.CLASSI), '%.2f%%' % (100 * y['ripetizioni_immediate'])))
    md += ['', '| seme | proprietà guadagnate | proprietà perse |', '|---|---|---|']
    for x in ris['verifica']:
        md.append('| %d | %s | %s |' % (x['seme'], ', '.join(x['guadagnate']) or '—', ', '.join(x['perse']) or '—'))
    md += ['', '## Diagnosi (semi 7, 8, 9)', '', '| seme | braccio | ricircolo | dopo | inizio riga | forme nuove | proprie della pagina vera | altre attestate | '
           'quota non attestate | nuove > 5 (erbario) | massimo | lessico H occ. | lessico H tipi |', '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for x in ris['verifica']:
        for br, nome in (('base', 'e241'), ('gamma', 'γ %.2f' % gs)):
            dg = x[br]['diagnosi']
            o = dg['b_confinate_per_origine']
            md.append('| %d | %s | %s | %d | %d | %d | %d | %d | %s | %d | %d | %d | %d |' % (
                x['seme'], nome, f(dg['a_ricircolo']), o['creata_da_dopo'], o['inizio_riga'], o['forma_nuova'], o['propria_pagina_vera'], o['altra_attestata'],
                f(dg['c_quota_non_attestate']), dg['d_forme_nuove_oltre_5_erbario'], dg['d_massimo_forma_nuova_erbario'], dg['e_lessico_H_occorrenze'], dg['e_lessico_H_tipi']))
    m = ris['medie']
    md += ['', 'Medie: e241 pagella %s (somma %d), riga in %d semi, R rare %s, AUC e231 %s, e266 %s; γ* pagella %s (somma %d), riga in %d semi, R rare %s, '
           'AUC e231 %s, e266 %s.' % (f(m['base']['pagella_media'], 2), m['base']['pagella_somma'], m['base']['semi_con_riga'], f(m['base']['R_parole_rare_media'], 1),
                                      f(m['base']['AUC_e231_media']), f(m['base']['AUC_e266_media']), f(m['gamma']['pagella_media'], 2), m['gamma']['pagella_somma'],
                                      m['gamma']['semi_con_riga'], f(m['gamma']['R_parole_rare_media'], 1), f(m['gamma']['AUC_e231_media']), f(m['gamma']['AUC_e266_media'])), '',
           "Caratteristiche più pesanti dell'e231 (seme 7, γ*; positivo = più nel generatore):", '', '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in ris['verifica'][0]['gamma']['piu_pesanti_e231']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.%s%s' % (ris['esito'], ' Costo: AUC dell\'e231 salita di oltre 0,05.' if ris['costo_AUC'] else '',
                                       ' Base non replicata sul seme 2.' if ris['base_non_replicata'] else '')]
    open(os.path.join(RISULTATI, 'e251_lessico_sezione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
