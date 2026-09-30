# -*- coding: utf-8 -*-
"""Esperimento 12: quali spazi del Voynich sono veri?

Se due parole vicine, scritte di seguito, formano una parola che il
manoscritto usa altrove, lo spazio fra loro potrebbe essere facoltativo. Lo
misuriamo per ogni coppia di parole adiacenti e lo confrontiamo con il caso
(la stessa seconda parola preceduta da una prima parola qualsiasi). Poi
guardiamo per tipo di giuntura (ultimo segno della prima parola, primo segno
della seconda) e per tipo di spazio (certo o incerto secondo i trascrittori).

Per confronto, lo stesso sul latino e sull'italiano. Infine una versione del
Voynich "risegmentata", senza gli spazi incerti e senza quelli alle giunture
morbide, misurata come le altre: se le unita' vere fossero piu' grandi delle
parole scritte, il testo risegmentato dovrebbe somigliare di piu' a una lingua.

Scrive risultati/e12_giunture.json e risultati/e12_giunture.md.
"""
import json, os, random, re, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione
from e07_codifiche import impronta

RISULTATI = os.path.join(QUI, '..', 'risultati')
MORBIDA, DURA = 0.30, 0.02       # soglie sulla quota di unioni attestate
MINIMO = 40                      # coppie minime per giudicare una giuntura


def righe_con_spazi(righe):
    """Per ogni riga: le parole e, fra una e l'altra, il tipo di spazio
    ('.' certo, ',' incerto, '|' interruzione per un disegno)."""
    out = []
    for r in righe:
        s = re.sub(r'<![^>]*>', '', r.grezza).replace('<%>', '').replace('<$>', '')
        s = s.replace('<->', '|').replace('<~>', '|')
        s = re.sub(r'<[^>]*>', '', s)
        s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
        s = s.replace('{', '').replace('}', '').replace("'", '')
        s = re.sub(r'@\d{3};', '*', s)
        pezzi = re.split(r'([.,|])', s)
        parole, spazi = pezzi[0::2], pezzi[1::2]
        coppie = [(a, sp, b) for a, sp, b in zip(parole, spazi, parole[1:]) if a and b]
        out.append((parole, spazi, coppie))
    return out


def analizza(coppie, vocabolario, dividi, rnd):
    prime = [a for a, _, _ in coppie]
    attestate = sum(1 for a, _, b in coppie if vocabolario[a + b])
    caso = sum(1 for a, _, b in coppie if vocabolario[rnd.choice(prime) + b])
    per_giuntura = defaultdict(lambda: [0, 0, 0])
    for a, sp, b in coppie:
        k = (dividi(a)[-1], dividi(b)[0]) if dividi else (a[-1], b[0])
        per_giuntura[k][0] += 1
        per_giuntura[k][1] += bool(vocabolario[a + b])
        per_giuntura[k][2] += sp == ','
    return {'coppie': len(coppie), 'unione_attestata': attestate / len(coppie),
            'unione_attestata_caso': caso / len(coppie)}, per_giuntura


def main():
    rnd = random.Random(0)
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl = trascrizione.leggi('ZL')
    vocabolario = Counter(p for r in zl for p in r.parole if trascrizione.pulita(p))
    corrente = trascrizione.testo_corrente(zl)
    righe = righe_con_spazi(corrente)
    coppie = [(a, sp, b) for _, _, cc in righe for a, sp, b in cc
              if trascrizione.pulita(a) and trascrizione.pulita(b) and sp in '.,']
    ris = {'voynich': {}}
    tot, per_giuntura = analizza(coppie, vocabolario, glifi, rnd)
    ris['voynich']['tutte'] = tot
    for tipo, nome in (('.', 'spazi certi'), (',', 'spazi incerti')):
        sotto = [c for c in coppie if c[1] == tipo]
        ris['voynich'][nome] = analizza(sotto, vocabolario, glifi, rnd)[0]
    giunture = []
    for (fine, inizio), (n, att, inc) in per_giuntura.items():
        if n >= MINIMO:
            giunture.append({'fine': fine, 'inizio': inizio, 'coppie': n, 'unione_attestata': att / n,
                             'spazi_incerti': inc / n,
                             'tipo': 'morbida' if att / n >= MORBIDA else ('dura' if att / n <= DURA else 'intermedia')})
    giunture.sort(key=lambda g: -g['unione_attestata'])
    ris['giunture'] = giunture
    print('Voynich: unioni attestate %.1f%% (caso %.1f%%); spazi certi %.1f%%, incerti %.1f%%' % (
        100 * tot['unione_attestata'], 100 * tot['unione_attestata_caso'],
        100 * ris['voynich']['spazi certi']['unione_attestata'],
        100 * ris['voynich']['spazi incerti']['unione_attestata']))

    ris['lingue'] = {}
    for nome, parole in [('Vitruvio', lingue.genere('Vitruvio, architettura')),
                         ('Bibbia latina', lingue.parole('Latin')[:60000]),
                         ('Bibbia italiana', lingue.parole('Italian')[:60000]),
                         ('Bibbia tedesca', lingue.parole('German')[:60000])]:
        voc = Counter(parole)
        cc = [(a, '.', b) for a, b in zip(parole, parole[1:])][:30000]
        ris['lingue'][nome] = analizza(cc, voc, None, rnd)[0]
        print('%-16s unioni attestate %.1f%% (caso %.1f%%)' % (
            nome, 100 * ris['lingue'][nome]['unione_attestata'], 100 * ris['lingue'][nome]['unione_attestata_caso']))

    # Voynich risegmentato: via gli spazi incerti e quelli alle giunture morbide
    morbide = {(g['fine'], g['inizio']) for g in giunture if g['tipo'] == 'morbida'}
    pagine = OrderedDict()
    tolti = 0
    for r, (parole, spazi, _) in zip(corrente, righe):
        nuove = []
        for i, p in enumerate(parole):
            if not p:
                continue
            if nuove and i > 0 and trascrizione.pulita(p) and trascrizione.pulita(nuove[-1]):
                sp = spazi[i - 1]
                if sp == ',' or (sp == '.' and (glifi(nuove[-1])[-1], glifi(p)[0]) in morbide):
                    nuove[-1] += p
                    tolti += 1
                    continue
            nuove.append(p)
        nuove = [p for p in nuove if trascrizione.pulita(p)]
        if nuove:
            pagine.setdefault(r.pagina, []).append(nuove)
    pagine = list(pagine.values())
    originale = OrderedDict()
    for r in corrente:
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        if ps:
            originale.setdefault(r.pagina, []).append(ps)
    ris['risegmentato'] = {'spazi_tolti': tolti, 'giunture_morbide': sorted('%s|%s' % g for g in morbide)}
    for nome, pp in (('originale', list(originale.values())), ('risegmentato', pagine)):
        r = impronta(pp, glifi)
        r.update(misure.confine([riga for pag in pp for riga in pag], glifi, solo_interne=True))
        ris['risegmentato'][nome] = r
        print('%-13s parole %d  h2 %.2f lung %.2f tipi %.3f hapax %.2f ident x%.2f somigl. %.1f%% confine %.3f' % (
            nome, r['parole'], r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_vs_riga'],
            100 * r['somiglianza_riga'], r['im_confine_eccesso']))
    with open(os.path.join(RISULTATI, 'e12_giunture.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    v = ris['voynich']
    out = ['# Esperimento 12: quali spazi sono veri', '',
           'Per ogni coppia di parole adiacenti: la loro unione è una parola che il testo usa altrove? '
           'Il "caso" è la stessa seconda parola preceduta da una prima parola qualsiasi.', '',
           '| testo | coppie | unione attestata | caso |', '|---|---|---|---|',
           '| **Voynich, tutti gli spazi** | %d | %.1f%% | %.1f%% |' % (
               v['tutte']['coppie'], 100 * v['tutte']['unione_attestata'], 100 * v['tutte']['unione_attestata_caso']),
           '| **Voynich, spazi certi** | %d | %.1f%% | %.1f%% |' % (
               v['spazi certi']['coppie'], 100 * v['spazi certi']['unione_attestata'],
               100 * v['spazi certi']['unione_attestata_caso']),
           '| **Voynich, spazi incerti** | %d | %.1f%% | %.1f%% |' % (
               v['spazi incerti']['coppie'], 100 * v['spazi incerti']['unione_attestata'],
               100 * v['spazi incerti']['unione_attestata_caso'])]
    for nome, r in ris['lingue'].items():
        out.append('| %s | %d | %.1f%% | %.1f%% |' % (nome, r['coppie'], 100 * r['unione_attestata'],
                                                      100 * r['unione_attestata_caso']))
    out += ['', '## Giunture del Voynich (almeno %d coppie)' % MINIMO, '',
            'Morbida: unione attestata almeno nel %d%% dei casi; dura: al massimo nel %d%%.' % (
                100 * MORBIDA, 100 * DURA), '',
            '| fine | inizio | coppie | unione attestata | spazi incerti | tipo |', '|---|---|---|---|---|---|']
    for g in ris['giunture']:
        if g['tipo'] != 'intermedia':
            out.append('| %s | %s | %d | %.0f%% | %.0f%% | %s |' % (
                g['fine'], g['inizio'], g['coppie'], 100 * g['unione_attestata'], 100 * g['spazi_incerti'], g['tipo']))
    rs = ris['risegmentato']
    out += ['', '## Il Voynich risegmentato', '',
            'Tolti %d spazi (gli incerti e quelli alle giunture morbide: %s).' % (
                rs['spazi_tolti'], ', '.join(rs['giunture_morbide'])), '',
            '| versione | parole | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza nella riga | confine |',
            '|---|---|---|---|---|---|---|---|---|']
    for nome in ('originale', 'risegmentato'):
        r = rs[nome]
        out.append('| %s | %d | %.2f | %.2f | %.3f | %.2f | ×%.2f | %.1f%% | %.3f |' % (
            nome, r['parole'], r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'],
            r['identiche_vs_riga'], 100 * r['somiglianza_riga'], r['im_confine_eccesso']))
    with open(os.path.join(RISULTATI, 'e12_giunture.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
