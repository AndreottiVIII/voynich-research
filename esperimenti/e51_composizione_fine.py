# -*- coding: utf-8 -*-
"""Esperimento 51: meno composizione (q 0,05-0,15), con novita', giunture e recenza.
Stesso generatore dell'e50; validazione fuori campione V1, V3, V4 (lunghezza delle parole),
V5 (unioni attestate rispetto al caso); V2 riportata ma non piu' fuori campione.

Preregistrazione: preregistrazioni/e51.md. Serve Java. Scrive risultati/e51_composizione_fine.json e .md.
"""
import json, math, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e23_giunture as e23
import e50_recenza_novita as e50
e48, e49 = e50.e48, e50.e49
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUOTE = (0.05, 0.1, 0.15)
LAMBDA = (0.6, 0.75, 0.9)
RECENZA = (0, 5)
SEMI = (19, 1, 2)
DIVIDI = misure.divisore(misure.GLIFI_EVA)


def extra(pagine):
    parole = [w for p in pagine for r in p for w in r]
    lung = [len(DIVIDI(w)) for w in parole]
    media = sum(lung) / len(lung)
    dev = math.sqrt(sum((x - media) ** 2 for x in lung) / len(lung))
    return {'lung_media_segni': media, 'lung_dev_segni': dev}


def validazione(m, v):
    e = e49.esito_validazione(m)
    return {'V1': e['V1'], 'V3': e['V3'],
            'V4': abs(m['lung_media_segni'] - v['lung_media_segni']) <= 0.25
                  and abs(m['lung_dev_segni'] - v['lung_dev_segni']) <= 0.25,
            'V5': m['unione_attestata'] / m['unione_caso'] >= 1.5,
            'V2 (non fuori campione)': e['V2']}


def main():
    os.makedirs(e50.LAVORO, exist_ok=True)
    glifi = DIVIDI
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_file = os.path.join(e50.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(trascrizione.parole(corrente)) + '\n')
    tabella = os.path.join(e50.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = e50.compila()
    pv = pagine_voynich(corrente)
    ris = OrderedDict()
    v = dict(e48.misura(pv, glifi), **e49.validazione(pv), **extra(pv))
    ris['Voynich'] = v
    medie = OrderedDict()
    for k in RECENZA:
        for q in QUOTE:
            for lam in LAMBDA:
                gruppo = []
                for seme in SEMI:
                    pagine, _ = e50.genera(classi, tabella, parole_file, q, lam, k, seme)
                    r = dict(e48.misura(pagine, glifi), **e49.validazione(pagine), **extra(pagine))
                    ris['K %d, q %.2f, lambda %.2f, seme %d' % (k, q, lam, seme)] = r
                    gruppo.append(r)
                chiavi = [c for c, x in gruppo[0].items() if isinstance(x, (int, float))]
                m = {c: sum(g[c] for g in gruppo) / len(gruppo) for c in chiavi}
                m['compatibile'] = e48.compatibile(m)
                m['validazione'] = validazione(m, v)
                medie['K %d, q %.2f, lambda %.2f' % (k, q, lam)] = m
                print('MEDIA K %d q %.2f l %.2f: rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f uniche %.2f/%.2f lung %.2f/%.2f unioni x%.2f | %s %s' % (
                    k, q, lam, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
                    m['h2'], m['confine'], m['hapax_1000'], m['hapax_34000'], m['lung_media_segni'], m['lung_dev_segni'],
                    m['unione_attestata'] / m['unione_caso'], 'COMPATIBILE' if m['compatibile'] else '',
                    ' '.join(c for c, x in m['validazione'].items() if x)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e51_composizione_fine.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    out = ['# e51 — Meno composizione, con novità, giunture e recenza', '',
           'Medie su tre semi. Compatibile come e48–e50. Validazione: V1 curva piatta, V3 profilo di pagina, V4 '
           'lunghezza delle parole (±0,25 in media e deviazione), V5 unioni attestate/caso ≥ 1,5; V2 riportata ma non '
           'fuori campione. Preregistrazione: `preregistrazioni/e51.md`.', '',
           '| testo | h2 | ripetizione | somigl. riga | 6 righe | legame | uniche 34.000 | lunghezza | unioni/caso | V2 | V3 quota | compatibile | validazione |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f ± %.2f | %.2f | %.3f | %.3f | | |' % (
               v['h2'], v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'],
               v['hapax_34000'], v['lung_media_segni'], v['lung_dev_segni'], v['unione_attestata'] / v['unione_caso'],
               v['V2_ricambio_k1_meno_k20'], v['V3_quota_media'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f ± %.2f | %.2f | %.3f | %.3f | %s | %s |' % (
            nome, m['h2'], m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
            m['confine'], m['hapax_34000'], m['lung_media_segni'], m['lung_dev_segni'],
            m['unione_attestata'] / m['unione_caso'], m['V2_ricambio_k1_meno_k20'], m['V3_quota_media'],
            'sì' if m['compatibile'] else 'no', ', '.join(c for c, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e51_composizione_fine.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
