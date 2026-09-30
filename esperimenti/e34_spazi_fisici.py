# -*- coding: utf-8 -*-
"""Esperimento 34: gli spazi certi sono graduati? La larghezza fisica sulla pagina.

Riquadri per parola di voynichese.com (repository di Rozanova e Temerev, commit 66f8ada)
allineati alla ZL. Fra gli spazi che la ZL segna certi, a parita' dei due segni ai
lati: lo spazio e' piu' stretto quando le due parole, unite, formano una parola che il
manoscritto scrive altrove attaccata? Controllo di validita': incerti contro certi, a
parita' di segni, deve dare gli incerti piu' stretti (Rozanova e Temerev 2026).

Preregistrazione: preregistrazioni/e34.md. Scrive risultati/e34_spazi_fisici.json e .md.
"""
import json, os, re, sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
from e12_giunture import righe_con_spazi

RISULTATI = os.path.join(QUI, '..', 'risultati')
RIQUADRI = os.path.join(lingue.SORGENTI, 'voynich-units', 'morphometry_voynichese', 'voynichese_boxes')
FUSI = [('cth', 'T'), ('ckh', 'K'), ('cph', 'P'), ('cfh', 'F'), ('ch', 'C'), ('sh', 'S'),
        ('iin', 'N'), ('in', 'I'), ('ee', 'E')]      # come Rozanova e Temerev
MINIMO = 5
RIMESCOLAMENTI = 2000


def fondi(w):
    for a, b in FUSI:
        w = w.replace(a, b)
    return w


def riquadri(foglio):
    """Parole di voynichese.com con x, y, larghezza e riga (nuova riga quando x torna indietro)."""
    percorso = os.path.join(RIQUADRI, foglio + '.js')
    if not os.path.exists(percorso):
        return None
    d = json.load(open(percorso, encoding='utf-8'))
    voc = [w[0] for w in d[0]]
    out, riga, prima = [], 0, None
    for e in d[1]:
        if prima is not None and e[1] < prima - 3:
            riga += 1
        out.append({'parola': voc[e[0]], 'x': e[1], 'y': e[2], 'w': e[3], 'riga': riga})
        prima = e[1]
    return out


def parole_zl():
    """Per foglio: parole della ZL (paragrafi) e separatore dopo ciascuna ('.', ',', '|', 'L')."""
    per_foglio = defaultdict(lambda: ([], []))
    righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    for r, (parole, spazi, _) in zip(righe, righe_con_spazi(righe)):
        ps = [p for p in parole if p]
        sp = [s for p, s in zip(parole, spazi) if p][:len(ps) - 1] + ['L']
        per_foglio[r.pagina][0].extend(ps)
        per_foglio[r.pagina][1].extend(sp)
    return per_foglio


def spazi_etichettati():
    """[(foglio, parola prima, parola dopo, separatore ZL, larghezza normalizzata)]."""
    out, fogli_usati = [], 0
    for foglio, (zt, zs) in sorted(parole_zl().items()):
        vt = riquadri(foglio)
        if not vt or not zt:
            continue
        fogli_usati += 1
        mediana = float(np.median([t['w'] for t in vt])) or 1.0
        sm = SequenceMatcher(a=[fondi(t['parola']) for t in vt], b=[fondi(w) for w in zt], autojunk=False)
        for i0, j0, n in sm.get_matching_blocks():
            for k in range(n - 1):
                a, b = vt[i0 + k], vt[i0 + k + 1]
                sep = zs[j0 + k]
                if a['riga'] != b['riga'] or sep not in '.,':
                    continue
                out.append((foglio, zt[j0 + k], zt[j0 + k + 1], sep, (b['x'] - (a['x'] + a['w'])) / mediana))
    return out, fogli_usati


def differenza_stratificata(dati, rnd):
    """dati: [(strato, etichetta 0/1, larghezza)]. Media pesata (sul numero di casi) di
    larghezza(0) - larghezza(1) negli strati con almeno MINIMO casi per etichetta,
    contro RIMESCOLAMENTI rimescolamenti delle etichette dentro gli strati."""
    per = defaultdict(list)
    for s, e, g in dati:
        per[s].append((e, g))
    strati = [(np.array([e for e, _ in v]), np.array([g for _, g in v])) for v in per.values()
              if sum(e for e, _ in v) >= MINIMO and sum(1 - e for e, _ in v) >= MINIMO]

    def stat(etichette):
        num = den = 0.0
        for (_, g), e in zip(strati, etichette):
            num += (g[e == 0].mean() - g[e == 1].mean()) * len(g)
            den += len(g)
        return num / den
    oss = stat([e for e, _ in strati])
    nulle = np.array([stat([rnd.permutation(e) for e, _ in strati]) for _ in range(RIMESCOLAMENTI)])
    return {'strati': len(strati), 'casi': int(sum(len(g) for _, g in strati)), 'differenza': float(oss),
            'nulla_media': float(nulle.mean()), 'nulla_dev': float(nulle.std(ddof=1)),
            'z': float((oss - nulle.mean()) / nulle.std(ddof=1)),
            'p_una_coda': float((1 + (nulle >= oss).sum()) / (1 + len(nulle)))}


def main():
    rnd = np.random.default_rng(34)
    spazi, fogli = spazi_etichettati()
    voc = Counter(trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))))
    coppia = lambda a, b: (fondi(a)[-1], fondi(b)[0])
    pulite = [(f, a, b, s, g) for f, a, b, s, g in spazi if trascrizione.pulita(a) and trascrizione.pulita(b)]
    ris = {'fogli': fogli, 'spazi_allineati': len(spazi), 'spazi_puliti': len(pulite),
           'certi': sum(s == '.' for *_, s, _ in pulite), 'incerti': sum(s == ',' for *_, s, _ in pulite),
           'larghezza_media': {'certi': float(np.mean([g for *_, s, g in pulite if s == '.'])),
                               'incerti': float(np.mean([g for *_, s, g in pulite if s == ','])) }}
    # validita': incerti (1) contro certi (0) a parita' di coppia di segni
    ris['validita_incerti'] = differenza_stratificata(
        [(coppia(a, b), int(s == ','), g) for _, a, b, s, g in pulite], rnd)
    # primaria: fra i certi, unione attestata (1) contro no (0), a parita' di coppia di segni
    certi = [(a, b, g) for _, a, b, s, g in pulite if s == '.']
    ris['primaria_unione_attestata'] = differenza_stratificata(
        [(coppia(a, b), int(voc[a + b] > 0), g) for a, b, g in certi], rnd)
    ris['quota_certi_con_unione_attestata'] = float(np.mean([voc[a + b] > 0 for a, b, _ in certi]))
    # secondaria: tipo di giuntura dell'e12 (segni composti fusi come nell'e12: cth ckh cph cfh ch sh)
    with open(os.path.join(RISULTATI, 'e12_giunture.json'), encoding='utf-8') as f:
        tipo = {(g['fine'], g['inizio']): g['tipo'] for g in json.load(f)['giunture']}
    import misure
    dividi = misure.divisore(misure.GLIFI_EVA)
    per_tipo = defaultdict(list)
    for a, b, g in certi:
        per_tipo[tipo.get((dividi(a)[-1], dividi(b)[0]), 'altra')].append(g)
    ris['secondaria_per_giuntura'] = {t: {'n': len(v), 'media': float(np.mean(v)), 'mediana': float(np.median(v))}
                                      for t, v in sorted(per_tipo.items())}
    v, p = ris['validita_incerti'], ris['primaria_unione_attestata']
    print('fogli %d, spazi allineati %d (certi %d, incerti %d)' % (fogli, len(spazi), ris['certi'], ris['incerti']))
    print('validita\' (certi - incerti, a parita\' di segni): %.4f  z %.1f  p %.4f  strati %d' % (
        v['differenza'], v['z'], v['p_una_coda'], v['strati']))
    print('primaria (non attestata - attestata, fra i certi): %.4f  z %.1f  p %.4f  strati %d casi %d' % (
        p['differenza'], p['z'], p['p_una_coda'], p['strati'], p['casi']))
    for t, x in ris['secondaria_per_giuntura'].items():
        print('  giuntura %-8s n %5d  media %.4f  mediana %.4f' % (t, x['n'], x['media'], x['mediana']))
    with open(os.path.join(RISULTATI, 'e34_spazi_fisici.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    righe = ['# e34 — Gli spazi certi sono graduati? Larghezza fisica sulla pagina', '',
             'Riquadri per parola di voynichese.com (via Rozanova e Temerev 2026, commit 66f8ada) allineati '
             'alla ZL. Larghezza = distanza fra i riquadri divisa per la mediana della larghezza dei riquadri '
             'del foglio. Differenze a parità dei due segni ai lati (strati con almeno %d casi per gruppo), '
             '%d rimescolamenti dentro gli strati. Preregistrazione: `preregistrazioni/e34.md`.' % (MINIMO, RIMESCOLAMENTI), '',
             'Fogli: %d; spazi allineati con entrambe le parole pulite: %d (certi %d, incerti %d). Larghezza '
             'media: certi %.3f, incerti %.3f.' % (fogli, len(pulite), ris['certi'], ris['incerti'],
                                                   ris['larghezza_media']['certi'], ris['larghezza_media']['incerti']), '',
             '| prova | strati | casi | differenza | z | p (una coda) |', '|---|---|---|---|---|---|',
             '| validità: certi − incerti | %d | %d | %.4f | %.1f | %.4f |' % (
                 v['strati'], v['casi'], v['differenza'], v['z'], v['p_una_coda']),
             '| **primaria**: fra i certi, unione non attestata − attestata | %d | %d | %.4f | %.1f | %.4f |' % (
                 p['strati'], p['casi'], p['differenza'], p['z'], p['p_una_coda']), '',
             'Secondaria (senza controllo per la forma dei segni): larghezza degli spazi certi per tipo di '
             'giuntura dell\'e12.', '', '| giuntura | spazi | media | mediana |', '|---|---|---|---|']
    righe += ['| %s | %d | %.4f | %.4f |' % (t, x['n'], x['media'], x['mediana'])
              for t, x in ris['secondaria_per_giuntura'].items()]
    with open(os.path.join(RISULTATI, 'e34_spazi_fisici.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


if __name__ == '__main__':
    main()
