# -*- coding: utf-8 -*-
"""Esperimento 77: versi sanscriti con sandhi (Manusmrti, Raghuvamsa) in due impaginazioni (un mezzo verso
per riga; testo di seguito mandato a capo): legame attraverso l'a capo, CV delle larghezze, bordo di riga.

Preregistrazione: preregistrazioni/e77.md. Scrive risultati/e77_versi_sandhi.json e .md.
"""
import hashlib, json, os, random, re, statistics, sys, unicodedata
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e76_righe_piene as e76

RISULTATI = os.path.join(QUI, '..', 'risultati')
CARTELLA = os.path.join(QUI, '..', 'dati', 'cache', 'sanscrito')
URL = 'https://raw.githubusercontent.com/ambuda-org/gretil/96e96220c686c9083d1646f85d5289cf0ab9e9ff/1_sanskr/tei/'
TESTI = OrderedDict([
    ('Manusmṛti', ('sa_manusmRti.xml', '666c2d3c05a41b9bc449c50a5afffe575e278085269d93dccb0f480a61cdf7e1')),
    ('Raghuvaṃśa', ('sa_kAlidAsa-raghuvaMza.xml', '268de86e64d026ef9e67cb784902c6b08e73926315e16d44eb10357e80d93404')),
])
RIGHE_PAGINA, SEME = 20, 77


def parola(w):
    w = unicodedata.normalize('NFC', w.lower())
    return ''.join(c for c in w if unicodedata.category(c)[0] in 'LM')


def mezzi_versi(nome_file, sha):
    percorso = os.path.join(CARTELLA, nome_file)
    dati = open(percorso, 'rb').read()
    if hashlib.sha256(dati).hexdigest() != sha:
        raise SystemExit('file diverso da quello preregistrato: %s (scaricare da %s)' % (nome_file, URL + nome_file))
    testo = dati.decode('utf-8')
    righe = []
    for blocco in re.findall(r'<lg xml:id="[^"]*">(.*?)</lg>', testo, re.S):
        for l in re.findall(r'<l\b[^>]*>(.*?)</l>', blocco, re.S):
            ps = [parola(w) for w in re.sub(r'<[^>]+>', ' ', l).split()]
            ps = [w for w in ps if w]
            if ps:
                righe.append(ps)
    return righe


def misura(nome, righe):
    """righe: lista di (pagina, inizio, parole)."""
    r = OrderedDict()
    rnd = random.Random(SEME)
    dentro, a_capo = e74.coppie(righe, e71.lettere)
    y, x = e74.eccesso(dentro, rnd), e74.eccesso(a_capo, rnd)
    r['dentro'], r['a_capo'] = y, x
    r['R'] = x['eccesso'] / y['eccesso'] if y['eccesso'] > 0 else None
    larg = [sum(len(w) for w in ps) + len(ps) - 1 for _, _, ps in righe]
    r['cv'] = statistics.pstdev(larg) / statistics.mean(larg)
    b = e71.una((nome, [(inizio, ps) for _, inizio, ps in righe], 'lettere'))[1]
    r['distinzione_inizio'] = b['jsd_inizio']['rapporto'] if isinstance(b['jsd_inizio'], dict) else None
    r['distinzione_fine'] = b['jsd_fine']['rapporto'] if isinstance(b['jsd_fine'], dict) else None
    r['arricchiti'] = b['arricchiti']
    print('%-40s righe %5d | dentro %.4f (z %.0f) a capo %.4f (z %.1f) R %s | CV %.3f | bordo ini %.1f fin %.1f | %s' % (
        nome, len(righe), y['eccesso'], y['z'] or 0, x['eccesso'], x['z'] or 0,
        '%.2f' % r['R'] if r['R'] is not None else '-', r['cv'], r['distinzione_inizio'] or 0, r['distinzione_fine'] or 0,
        b['arricchiti']), flush=True)
    return r


def main():
    ris = OrderedDict()
    for nome, (f, sha) in TESTI.items():
        versi = mezzi_versi(f, sha)
        imp1 = [(i // RIGHE_PAGINA, i % RIGHE_PAGINA == 0, ps) for i, ps in enumerate(versi)]
        larghezza = statistics.median(sum(len(w) for w in ps) + len(ps) - 1 for ps in versi)
        di_seguito = [w for ps in versi for w in ps]
        avvolto = e76.a_capo_per_voce([di_seguito], e71.lettere, larghezza)
        imp2 = [(i // RIGHE_PAGINA, i % RIGHE_PAGINA == 0, ps) for i, (_, _, ps) in enumerate(avvolto)]
        ris[nome] = OrderedDict([('mezzi_versi', len(versi)), ('larghezza', larghezza),
                                 ('un mezzo verso per riga', misura(nome + ', un mezzo verso per riga', imp1)),
                                 ('di seguito, a capo', misura(nome + ', di seguito, a capo', imp2))])
    with open(os.path.join(RISULTATI, 'e77_versi_sandhi.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# e77 — Versi con sandhi: un meccanismo naturale per la riga chiusa?', '',
           'Legame (eccesso d\'informazione mutua, ultimo segno → primo segno) dentro la riga e attraverso l\'a capo; R = '
           'rapporto. CV delle larghezze; distinzione del bordo (rapporto con il nullo). Preregistrazione: '
           '`preregistrazioni/e77.md`. Voynich per confronto: R 0,01, dentro 0,20 bit; CV (sezione S) 0,049; bordo 23 / 55.', '',
           '| testo | impaginazione | dentro la riga | a capo | R | CV | bordo inizio | bordo fine |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        for imp in ('un mezzo verso per riga', 'di seguito, a capo'):
            x = r[imp]
            out.append('| %s | %s | %.4f (z %.0f) | %.4f (z %.1f) | %s | %.3f | %.1f | %.1f |' % (
                nome, imp, x['dentro']['eccesso'], x['dentro']['z'] or 0, x['a_capo']['eccesso'], x['a_capo']['z'] or 0,
                '%.2f' % x['R'] if x['R'] is not None else '–', x['cv'], x['distinzione_inizio'] or 0, x['distinzione_fine'] or 0))
    with open(os.path.join(RISULTATI, 'e77_versi_sandhi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
