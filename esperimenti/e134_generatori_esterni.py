# -*- coding: utf-8 -*-
"""Esperimento 134: Naibbe (Greshko 2025) e i generatori U2/U3 (Whitehatnetizen 2026) alla prova delle proprieta' di
riga e di pagina del Voynich.

Preregistrazione: preregistrazioni/e134.md. Scrive risultati/e134_generatori_esterni.json e .md.
"""
import hashlib, json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
import e106_procedimento_versi as e106
import e110_alternanza as e110
import e126_trasposizione_riga as e126
import e129_griglia_ricca as e129
import e130_mani as e130
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
ESTERNI = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni')
NAIBBE = os.path.join(ESTERNI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
SHA = {NAIBBE: '3409d5a1f8553a55195cb833e2629352e7a64d0ee7f2717bfe458bd05ad35185',
       os.path.join(ESTERNI, 'u2_righe.txt'): '9b795bbde22c4411d713818df240aa2fe00753e9ba678bf952401dd2f39ed7ab',
       os.path.join(ESTERNI, 'u3_righe.txt'): '89acd90661c5d56b782aa71117a3c2c21a779f0e2d390feb3b6b461b9c6a4def'}
D = misure.divisore(misure.GLIFI_EVA)
RP = 29


def controlla():
    for f, s in SHA.items():
        if hashlib.sha256(open(f, 'rb').read()).hexdigest() != s:
            raise SystemExit('%s diverso da quello preregistrato' % f)


def naibbe_righe():
    rv = e71.righe_voynich()
    larghezze = [sum(len(D(w)) for w in ps) + len(ps) - 1 for _, ps in rv]
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    media = sum(len(D(w)) for w in voy) / len(voy)
    out = []
    for l in open(NAIBBE, encoding='utf-8').read().splitlines():
        ps = l.split()
        if ps:
            out.extend(e71.a_capo(ps, D, larghezze[len(out):] + larghezze[:len(out)], media))
    return out


def testi():
    t = OrderedDict()
    t['Voynich'] = e71.righe_voynich()
    t['Naibbe (Greshko 2025), a capo'] = naibbe_righe()
    t['U2 (Whitehatnetizen 2026)'] = e71.righe_file(os.path.join(ESTERNI, 'u2_righe.txt'))
    t['U3 (Whitehatnetizen 2026)'] = e71.righe_file(os.path.join(ESTERNI, 'u3_righe.txt'))
    return t


def una(args):
    nome, righe, voy, soglia_ab, v, vb = args
    e83.PERMUTAZIONI = 200
    e88.PERMUTAZIONI = 100
    e71.RIMESCOLAMENTI = 50
    e110.RIMESCOLAMENTI = 50
    if len(righe) < 4000:
        import e49_composizione_giunture as e49
        e49.validazione = e78._validazione_corta
    r = e106.misura(righe, voy, soglia_ab, v, vb)
    _, a = e110.una(('x', [ps for _, ps in righe], 'eva'))
    r['A'] = a['senza identiche']['A']
    con_pag = [(k // RP, ini, ps) for k, (ini, ps) in enumerate(righe)]
    r['quota_sh_per_riga'] = e130.varianza_sh(con_pag, 200, random.Random(134))
    pagine = [[ps for _, ps in righe[i:i + RP]] for i in range(0, len(righe), RP)]
    _, g = e126.una(('x', pagine, 'eva'))
    r['accordo_riga_z'] = g['accordo']['z']
    r['parole'] = sum(len(ps) for _, ps in righe)
    return nome, r


def main():
    controlla()
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), D, voy, soglia_ab)
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    t = testi()
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '1'))) as pool:
        for nome, r in pool.imap(una, [(n, rr, voy, soglia_ab, v, vb) for n, rr in t.items()]):
            r['totale'] = sum(r['esiti'].values())
            r['di_riga'] = e129.di_riga(r)
            r['riproduce_la_riga'] = (sum(r['di_riga'].values()) >= 8 and (r['R_riga'] or 1) < 0.1 and r['S1'] <= 0.7
                                      and (r['quota_sh_per_riga'] or 0) > 1.05 and (r['accordo_riga_z'] or 0) < 2)
            ris[nome] = r
            print('%-32s parole %6d | %d/18 | riga e pagina %d/12 | R %.2f S1 %.2f copia %.2f/%.2f e94 %.2f A %.3f | bordo %.2f/%.2f | sh per riga %.3f | accordo z %.1f | riproduce %s | mancano: %s' % (
                nome, r['parole'], r['totale'], sum(r['di_riga'].values()), r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'],
                r['e94_pos2'], r['A'], r['bordo_inizio'], r['bordo_fine'], r['quota_sh_per_riga'] or 0, r['accordo_riga_z'] or 0,
                r['riproduce_la_riga'], ', '.join(p for p, x in r['di_riga'].items() if not x)), flush=True)
    with open(os.path.join(RISULTATI, 'e134_generatori_esterni.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    props = list(e61.BANDE) + ['bordo di riga']
    out = ['# e134 — Generatori e cifrari proposti da altri, alla prova delle proprietà di riga', '',
           'Naibbe: Greshko (2025), testo cifrato pubblicato (Plinio XVI), mandato a capo sulle righe del Voynich. U2/U3: Whitehatnetizen/voynich-investigation '
           '(commit ccd5db0, seme 1492). Preregistrazione: `preregistrazioni/e134.md`.', '',
           '| testo | parole | pagella | riga e pagina | R | S(1) | copia 1ª / 2ª | e94 | A | bordo inizio / fine | sh per riga | accordo nella riga (z) | riproduce la riga |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %d | %d/18 | %d/12 | %.2f | %.2f | %.2f / %.2f | %.2f | %.3f | %.2f / %.2f | %.3f | %.1f | %s |' % (
            nome, r['parole'], r['totale'], sum(r['di_riga'].values()), r['R_riga'] or 0, r['S1'], r['copia_prima'], r['copia_seconda'],
            r['e94_pos2'], r['A'], r['bordo_inizio'], r['bordo_fine'], r['quota_sh_per_riga'] or 0, r['accordo_riga_z'] or 0,
            'sì' if r['riproduce_la_riga'] else 'no'))
    out += ['', '| testo | ' + ' | '.join(props) + ' |', '|---|' + '---|' * len(props)]
    for nome, r in ris.items():
        out.append('| %s | %s |' % (nome, ' | '.join(('✓ ' if r['esiti'][p] else '· ') + ('%.3g' % r[e61.VALORI[p]] if e61.VALORI.get(p) in r else '') for p in props)))
    with open(os.path.join(RISULTATI, 'e134_generatori_esterni.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
