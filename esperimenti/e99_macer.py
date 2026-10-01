# -*- coding: utf-8 -*-
"""Esperimento 99: il Macer floridus (erbario medievale in esametri) come confronto: proprieta' di riga e pagella.

Preregistrazione: preregistrazioni/e99.md. Scrive risultati/e99_macer.json e .md.
"""
import hashlib, json, os, random, re, statistics, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
import e48_composizione as e48
import e55_forma_parole as e55
import e61_pagella as e61
import e71_bordo_riga as e71
import e74_legame_a_capo as e74
import e76_righe_piene as e76
import e78_versi_pagella as e78
import e83_evitamento_inizi as e83
import e88_copia_cambia_inizio as e88
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
FILE = os.path.join(QUI, '..', 'dati', 'cache', 'macer', 'macer_1832_djvu.txt')
SHA = '1baed87fec67e0c7d785fc7c92452bba8185f03e18b1b02b6b0378717161d8e3'
SEME = 99
GRECO = re.compile(r'[Ͱ-Ͽἀ-῿]')


def capitoli():
    dati = open(FILE, 'rb').read()
    if hashlib.sha256(dati).hexdigest() != SHA:
        raise SystemExit('OCR del Macer diverso da quello preregistrato')
    righe = dati.decode('utf-8').splitlines()[2165:7570]
    out, cur = [], []
    for l in righe:
        s = l.strip()
        if re.match(r'^[IVXLC]+\.\s+[A-Z]', s) or (s.isupper() and len(s) < 40 and s.replace('.', '').strip()):
            if cur:
                out.append(cur)
            cur = []
            continue
        s = re.sub(r'^\d+\s+', '', s)
        if not s or GRECO.search(s) or '—' in s or '|' in s or len(s) < 22 or len(s) > 75:
            continue
        if not s[0].isupper() or any(c.isdigit() for c in s):
            continue
        if len(re.findall(r'\b[a-z]{1,4}\.', s)) >= 2 or 'Macer Floridus' in s or 'Prolegomena' in s:
            continue
        ps = lingue.normalizza(s).split()
        if ps:
            cur.append(ps)
    if cur:
        out.append(cur)
    return [c for c in out if c]


def proprieta_riga(caps):
    versi = [ps for c in caps for ps in c]
    rnd = random.Random(SEME)
    per_versi = [(k, j == 0, ps) for k, c in enumerate(caps) for j, ps in enumerate(c)]
    larghezza = statistics.median(sum(len(w) for w in ps) + len(ps) - 1 for ps in versi)
    seguito = [(i // 20, i % 20 == 0, ps) for i, (_, _, ps) in enumerate(e76.a_capo_per_voce([[w for ps in versi for w in ps]], e71.lettere, larghezza))]
    out = OrderedDict()
    for nome, rr in (('un verso per riga', per_versi), ('di seguito, a capo', seguito)):
        d, a = e74.coppie(rr, e71.lettere)
        x, y = e74.eccesso(d, rnd), e74.eccesso(a, rnd)
        out['R ' + nome] = y['eccesso'] / x['eccesso'] if x['eccesso'] > 0 else None
        out['legame dentro, ' + nome] = x['eccesso']
    larg = [sum(len(w) for w in ps) + len(ps) - 1 for ps in versi]
    out['CV'] = statistics.pstdev(larg) / statistics.mean(larg)
    b = e71.una(('Macer', [(ini, ps) for _, ini, ps in per_versi], 'lettere'))[1]
    out['bordo inizio'] = b['jsd_inizio']['rapporto']
    out['bordo fine'] = b['jsd_fine']['rapporto']
    out['arricchiti'] = b['arricchiti']
    per = OrderedDict()
    for k, ini, ps in per_versi:
        per.setdefault(k, []).append((k, ini, ps[0]))
    s1 = e83.misura(per, 1, lambda w: w[0], random.Random(SEME))
    out['S(1)'] = s1['S']
    out['S(1) z'] = s1['z']
    e88.D = e71.lettere
    col = OrderedDict()
    for k, ini, ps in per_versi:
        col.setdefault(k, []).append((k, ini, ps[0]))
    c = e88.misura(col, random.Random(SEME))
    out['prima parola, corpi identici'] = c['corpi_identici']['rapporto']
    return out


def main():
    caps = capitoli()
    ris = OrderedDict([('capitoli', len(caps)), ('versi', sum(len(c) for c in caps)), ('parole', sum(len(ps) for c in caps for ps in c))])
    print('capitoli %d, versi %d, parole %d' % (ris['capitoli'], ris['versi'], ris['parole']), flush=True)
    e83.PERMUTAZIONI = 300
    e88.PERMUTAZIONI = 300
    pr = proprieta_riga(caps)
    ris['riga'] = pr
    for k, x in pr.items():
        print('  %s: %s' % (k, ('%.3f' % x) if isinstance(x, float) else x), flush=True)
    # pagella (lettere)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = trascrizione.parole(corrente)
    soglia_ab = e55.distanze(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='A')),
                             trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua='B')))
    v = e61.scheda(pagine_voynich(corrente), misure.divisore(misure.GLIFI_EVA), voy, soglia_ab)
    import e49_composizione_giunture as e49
    e49.validazione = e78._validazione_corta
    r = e61.scheda(caps, None, voy, soglia_ab)
    n = ris['parole']
    finestre_v = e48.per_finestre(voy)
    vv = dict(v)
    vv['hapax_34000'] = finestre_v[max(k for k in finestre_v if k <= n)]['hapax']
    esiti = OrderedDict()
    for prop, f in e61.BANDE.items():
        if prop == 'forma parole':
            continue
        try:
            esiti[prop] = bool(f(r, vv))
        except (KeyError, TypeError, ZeroDivisionError):
            esiti[prop] = False
    vb = e78.bordo(e71.righe_voynich(), 'eva')
    esiti['bordo di riga'] = 0.5 * vb[0] <= pr['bordo inizio'] <= 2 * vb[0] and 0.5 * vb[1] <= pr['bordo fine'] <= 2 * vb[1]
    r['esiti'] = esiti
    ris['pagella'] = r
    print('pagella %d/%d: %s' % (sum(esiti.values()), len(esiti), ' '.join(('✓' if x else '·') + p for p, x in esiti.items())), flush=True)
    print('  h2 %.2f spazio %.2f uniche %.2f tipi %.3f rip %.2f omog %.3f/%.3f legame %.3f' % (
        r['h2'], r['spazio_spiegato'], r['hapax_34000'], r['tipi_su_parole'], r['identiche_vs_riga'], r['somiglianza_riga'],
        r['somiglianza_6_righe'], r['confine']), flush=True)
    with open(os.path.join(RISULTATI, 'e99_macer.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1, default=str)
    out = ['# e99 — Il *Macer floridus* come confronto', '',
           '%d capitoli (piante), %d versi, %d parole (OCR Choulant 1832). Preregistrazione: `preregistrazioni/e99.md`.' % (
               ris['capitoli'], ris['versi'], ris['parole']), '', '## Proprietà di riga', '',
           '| misura | Macer | Voynich |', '|---|---|---|',
           '| R, un verso per riga | %.3f | 0,006 |' % pr['R un verso per riga'],
           '| R, di seguito | %.3f | – |' % pr['R di seguito, a capo'],
           '| legame dentro la riga (bit) | %.3f | 0,20 |' % pr['legame dentro, un verso per riga'],
           '| CV delle larghezze | %.3f | 0,049 (S) |' % pr['CV'],
           '| bordo inizio / fine | %.1f / %.1f | 23 / 55 |' % (pr['bordo inizio'], pr['bordo fine']),
           '| S(1) inizi consecutivi | %.2f | 0,52 |' % pr['S(1)'],
           '| prima parola, corpi identici con la riga sopra | %.2f | 1,03 |' % pr['prima parola, corpi identici'],
           '', '## Pagella (e61, per lettere)', '', '| proprietà | esito |', '|---|---|']
    for p, x in esiti.items():
        out.append('| %s | %s |' % (p, '✓' if x else '·'))
    out.append('| **totale** | **%d/%d** |' % (sum(esiti.values()), len(esiti)))
    with open(os.path.join(RISULTATI, 'e99_macer.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
