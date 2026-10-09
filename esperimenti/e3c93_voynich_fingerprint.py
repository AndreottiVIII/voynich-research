# -*- coding: utf-8 -*-
"""Esperimento e3c93: il generatore di voynich-fingerprint (Sachak 2026) e il suo manuale eseguibile a mano, alla prova
delle misure con cui sono stati provati gli altri generatori pubblicati (Naibbe, U2, U3, Timm e Schinner).

Testi:
- tre libri del generatore con la configurazione congelata pubblicata (versione 3, commit a6d7558), semi 7, 21, 44,
  generati da analisi/esterni_genera_vf.py; paragrafi separati da una riga vuota;
- il campione pubblicato del manuale a mano (analysis/scribe_sample.txt, 15.336 parole).
Pagine di 29 righe come nell'e134 (25 righe per lo stato breve, come nell'e3c49).

Misure:
- batteria dell'e134: pagella (18), proprietà di riga e di pagina (12), chiusura R, S(1), copia, bordo di riga;
- giuntura E e rispecchiamento ρ (e3c85), mediane su 5 sottoinsiemi di 10.000 parole;
- stato breve K corretto (e3c48, criterio della finestra dell'e3c49);
- deriva lungo la riga (e3c13, criterio dell'e3c62) per qo/o, k/t, sh/ch, -ey/-dy;
- ripetizione osservata/attesa nella riga (e3c88).
I valori del Voynich si leggono dai risultati già pubblicati (e134, e3c85, e3c48, e3c62, e3c88).

Preregistrazione: preregistrazioni/e3c93.md. Scrive risultati/e3c93_voynich_fingerprint.json e .md.
SOLO_CONTROLLI=1: prova del codice su U3 (la riga dell'e134 deve tornare uguale), niente testi di voynich-fingerprint.
"""
import hashlib, json, os, random, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e129_griglia_ricca as e129
import e134_generatori_esterni as e134
import e3b62_memoria_nullo_largo as e3b62
import e3c13_sh_lungo_la_riga as e3c13
import e3c48_finestra_corretta as e3c48
import e3c85_nullo_grammatica_parola as e3c85
import e3c88_ripetizioni_osservate_attese as e3c88
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
ESTERNI = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
D = e3b62.D
RP = 29
TRE = ('k/t', 'sh/ch', '-ey/-dy')
SOGLIA_DERIVA = 0.010  # per 10 segni, come nell'e3c62
SHA = {os.path.join(ESTERNI, 'vf_seme7.txt'): '809260612408b099c64c170b4809aedb1168bd331684cb2e096a5e043b26b386',
       os.path.join(ESTERNI, 'vf_seme21.txt'): '19b4329a08303a12adae79da1b576fcbc3a0c11c77bb83e01f612226f032e94a',
       os.path.join(ESTERNI, 'vf_seme44.txt'): '00740f9ac3d5fe40ca43a44a27fca14f64fb6b45638b9a1774d7c593a39eb390',
       os.path.join(ESTERNI, 'voynich-fingerprint', 'analysis', 'scribe_sample.txt'):
           '2c749fd3213249b80ff281984cb984d24db9c3613912beba3167f2d8606f2ff7'}


def righe_paragrafi(percorso):
    """[(inizio di paragrafo, parole)] da un file con i paragrafi separati da una riga vuota."""
    out = []
    for blocco in open(percorso, encoding='utf-8').read().split('\n\n'):
        rr = [l.split() for l in blocco.splitlines() if l.strip()]
        out += [(i == 0, r) for i, r in enumerate(rr)]
    return out


def testi():
    t = OrderedDict()
    if SOLO_CONTROLLI:
        e134.controlla()
        t['U3 (controllo, e134)'] = e71.righe_file(os.path.join(ESTERNI, 'u3_righe.txt'))
        return t
    for f, s in SHA.items():
        if hashlib.sha256(open(f, 'rb').read()).hexdigest() != s:
            raise SystemExit('%s diverso da quello preregistrato' % f)
    for seme in (7, 21, 44):
        t['voynich-fingerprint, seme %d' % seme] = righe_paragrafi(os.path.join(ESTERNI, 'vf_seme%d.txt' % seme))
    t['voynich-fingerprint, manuale a mano'] = righe_paragrafi(
        os.path.join(ESTERNI, 'voynich-fingerprint', 'analysis', 'scribe_sample.txt'))
    return t


def sottoinsiemi(pagine, rnd, n=10000, quanti=5):
    """Come e3c84.voynich_sottoinsiemi: pagine prese a caso fino a n parole."""
    out = []
    for _ in range(quanti):
        prese, k = [], 0
        for p in rnd.sample(pagine, len(pagine)):
            if k >= n:
                break
            prese += p
            k += sum(len(r) for r in p)
        out.append(prese)
    return out


def una(args):
    nome, righe, voy, soglia_ab, v, vb = args
    _, r = e134.una((nome, righe, voy, soglia_ab, v, vb))
    r['totale'] = sum(r['esiti'].values())
    r['di_riga'] = e129.di_riga(r)
    r['riproduce_la_riga'] = (sum(r['di_riga'].values()) >= 8 and (r['R_riga'] or 1) < 0.1 and r['S1'] <= 0.7
                              and (r['quota_sh_per_riga'] or 0) > 1.05 and (r['accordo_riga_z'] or 0) < 2)
    tt = [rr for rr in ([tuple(D(w)) for w in ps if w] for _, ps in righe) if rr]
    pagine = [tt[i:i + RP] for i in range(0, len(tt), RP)]
    rnd = random.Random(393)
    rng = np.random.default_rng(393)
    # giuntura e rispecchiamento
    if sum(len(x) for x in tt) >= 20000:
        camp = sottoinsiemi(pagine, rnd)
    else:
        camp = [tt]
    mis = [e3c85.misura(c, rnd) for c in camp]
    r['giuntura_E'] = statistics.median(m['giuntura'] for m in mis)
    r['rispecchiamento_rho'] = statistics.median(m['rispecchiamento'] for m in mis)
    r['sottoinsiemi'] = len(camp)
    # stato breve
    e3c48.PERM = 20
    k = e3c48.misura([('g', tt[i:i + 25]) for i in range(0, len(tt), 25)], OrderedDict((c, e3b62.CV[c]) for c in TRE), rng)
    k['finestra'] = bool(k['K1_IC95'][0] > 0.02 and k['K23_IC95'][0] > 0.02)
    r['stato_breve'] = k
    # deriva
    der = OrderedDict()
    for c, f in e3b62.CV.items():
        x = e3c13.pendenza(pagine, OrderedDict([(c, f)]), rng)
        x['deriva'] = bool(x['IC95'][1] < 0 or x['IC95'][0] > 0)
        der[c] = x
    r['deriva_riga'] = der
    # ripetizione
    e3c88.PERM = 20
    r['ripetizione_OE'] = e3c88.misura(tt, random.Random(3388))
    return nome, r


def riferimento():
    def j(nome):
        return json.load(open(os.path.join(RISULTATI, nome), encoding='utf-8'))
    ref = OrderedDict()
    v134 = j('e134_generatori_esterni.json')['Voynich']
    ref['pagella'] = sum(v134['esiti'].values())
    ref['di_riga'] = sum(v134['di_riga'].values())
    ref['R_riga'], ref['S1'] = v134['R_riga'], v134['S1']
    ref['bordo'] = (v134['bordo_inizio'], v134['bordo_fine'])
    t85 = j('e3c85_nullo_grammatica_parola.json')['voynich_e_nulli']['testo']
    ref['giuntura_E'], ref['rispecchiamento_rho'] = t85['giuntura'], t85['rispecchiamento']
    ref['K_corretto'] = j('e3c48_finestra_corretta.json')['varianti']['Voynich ZL, pagine intere']['K_corretto']
    ref['deriva_per_10_segni'] = OrderedDict((c, j('e3c62_deriva_scribi.json')['misure']['Voynich ZL, ' + c]['per_10_segni'])
                                             for c in e3b62.CV)
    ref['OE_riga'] = j('e3c88_ripetizioni_osservate_attese.json')['testi']['Voynich ZL']['OE_riga']
    return ref


def criteri(r, ref):
    """Le tre proprietà della frase del paper e le descrittive."""
    c = OrderedDict()
    c['giuntura'] = bool(r['giuntura_E'] >= ref['giuntura_E'] / 2 and r['rispecchiamento_rho'] >= ref['rispecchiamento_rho'] / 2)
    c['riga chiusa'] = bool(r['di_riga']['chiusura R'])
    c['margine'] = bool(r['di_riga']['S(1)'])
    d = OrderedDict()
    d['bordo di riga'] = bool(r['esiti']['bordo di riga'])
    d['copia dalla riga sopra'] = bool(r['di_riga']['copia'])
    d['stato breve'] = r['stato_breve']['finestra']
    d['deriva come il Voynich'] = sum(1 for k, x in r['deriva_riga'].items()
                                      if x['deriva'] and abs(x['per_10_segni']) >= SOGLIA_DERIVA
                                      and np.sign(x['per_10_segni']) == np.sign(ref['deriva_per_10_segni'][k]))
    d['ripetizione non evitata'] = bool((r['ripetizione_OE']['OE_riga'] or 0) >= 0.95)
    return c, d


def main():
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), e134.D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    ref = riferimento()
    t = testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, voy, soglia_ab, v, vb) for n, rr in t.items()]):
            r['criteri'], r['descrittive'] = criteri(r, ref)
            r['tutte_e_tre'] = all(r['criteri'].values())
            ris[nome] = r
            print('%-40s parole %6d | pagella %d/18 | riga e pagina %d/12 | E %.3f rho %.3f | R %.2f S1 %.2f | bordo %.2f/%.2f | K %s | deriva %d/4 | O/E riga %.2f | criteri %s | descrittive %s' % (
                nome, r['parole'], r['totale'], sum(r['di_riga'].values()), r['giuntura_E'], r['rispecchiamento_rho'],
                r['R_riga'] or 0, r['S1'], r['bordo_inizio'], r['bordo_fine'],
                ' '.join('%+.3f' % z for z in r['stato_breve']['K_corretto']), r['descrittive']['deriva come il Voynich'],
                r['ripetizione_OE']['OE_riga'] or 0, dict(r['criteri']), dict(r['descrittive'])), flush=True)
    if SOLO_CONTROLLI:
        u3 = json.load(open(os.path.join(RISULTATI, 'e134_generatori_esterni.json'), encoding='utf-8'))['U3 (Whitehatnetizen 2026)']
        r = ris['U3 (controllo, e134)']
        uguali = all(json.dumps(r[k], default=str) == json.dumps(u3[k], default=str) for k in u3)
        print('riga U3 dell\'e134 riprodotta: %s' % uguali)
        return
    semi = [k for k in ris if 'seme' in k]
    prop = list(ris[semi[0]]['criteri'])
    gen = OrderedDict((p, sum(ris[k]['criteri'][p] for k in semi) >= 2) for p in prop)
    man = ris['voynich-fingerprint, manuale a mano']['criteri']
    if all(gen.values()):
        esito = 'il generatore di voynich-fingerprint riproduce insieme giuntura, riga chiusa e margine'
    else:
        esito = 'il generatore di voynich-fingerprint non riproduce insieme le tre proprietà; mancano: ' + ', '.join(p for p, x in gen.items() if not x)
    esito_man = ('il manuale a mano riproduce insieme le tre proprietà' if all(man.values()) else
                 'il manuale a mano non le riproduce insieme; mancano: ' + ', '.join(p for p, x in man.items() if not x))
    out = OrderedDict([('riferimento_voynich', ref), ('testi', ris), ('generatore_2_su_3_semi', gen), ('esito', esito), ('esito_manuale', esito_man)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c93_voynich_fingerprint.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    md = ['# e3c93 — voynich-fingerprint (Sachak 2026) alla prova delle nostre misure', '',
          'Preregistrazione: `preregistrazioni/e3c93.md`. Configurazione congelata versione 3 (commit a6d7558), addestrata sui fogli pari di IT2a come nel loro protocollo; '
          'semi 7, 21, 44; un libro intero per seme (772 paragrafi). Manuale a mano: il loro campione pubblicato. Pagine di 29 righe.', '',
          '| testo | parole | pagella | riga e pagina | giuntura E | ρ | R | S(1) | bordo inizio / fine | K corretto 1/2/3 | deriva come il Voynich | O/E nella riga | giuntura / riga chiusa / margine |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|---|',
          '| Voynich (riferimento) | | %d/18 | %d/12 | %.3f | %.3f | %.2f | %.2f | %.2f / %.2f | %s | 4/4 | %.2f | sì / sì / sì |' % (
              ref['pagella'], ref['di_riga'], ref['giuntura_E'], ref['rispecchiamento_rho'], ref['R_riga'], ref['S1'], ref['bordo'][0], ref['bordo'][1],
              ' / '.join('%+.3f' % z for z in ref['K_corretto']), ref['OE_riga'])]
    sn = lambda x: 'sì' if x else 'no'
    for nome, r in ris.items():
        md.append('| %s | %d | %d/18 | %d/12 | %.3f | %.3f | %.2f | %.2f | %.2f / %.2f | %s | %d/4 | %.2f | %s |' % (
            nome, r['parole'], r['totale'], sum(r['di_riga'].values()), r['giuntura_E'], r['rispecchiamento_rho'], r['R_riga'] or 0, r['S1'],
            r['bordo_inizio'], r['bordo_fine'], ' / '.join('%+.3f' % z for z in r['stato_breve']['K_corretto']),
            r['descrittive']['deriva come il Voynich'], r['ripetizione_OE']['OE_riga'] or 0, ' / '.join(sn(x) for x in r['criteri'].values())))
    props = list(e61.BANDE) + ['bordo di riga']
    md += ['', '| testo | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, r in ris.items():
        md.append('| %s | %s |' % (nome, ' | '.join('✓' if r['esiti'][p] else '·' for p in props)))
    md += ['', 'Esito: **%s**. Manuale: **%s**.' % (esito, esito_man)]
    open(os.path.join(RISULTATI, 'e3c93_voynich_fingerprint.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)
    print(esito_man)


if __name__ == '__main__':
    main()
