# -*- coding: utf-8 -*-
"""Esperimento 53: parole scritte in due pezzi alle giunture morbide (scissione d) e sostituzioni di
fine parola del generatore accese o spente, sul modello migliore dell'e51 (q 0,10, lambda 0,75, K 0).
Validazione fuori campione: V1, V4, V6 (autocorrelazione delle lunghezze), V7 (Zipf).

Preregistrazione: preregistrazioni/e53.md. Serve Java. Scrive risultati/e53_scissione.json e .md.
"""
import hashlib, json, math, os, random, subprocess, sys
from collections import Counter, OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e50_recenza_novita as e50
import e51_composizione_fine as e51
e48, e49 = e50.e48, e50.e49
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
SCISSIONE = (0.0, 0.03, 0.06, 0.10)
FINALI = (True, False)
SEMI = (19, 1, 2)
Q, LAM, K = 0.10, 0.75, 0
DIVIDI = misure.divisore(misure.GLIFI_EVA)


def giunture_morbide():
    with open(os.path.join(RISULTATI, 'e12_giunture.json'), encoding='utf-8') as f:
        return {(g['fine'], g['inizio']) for g in json.load(f)['giunture'] if g['tipo'] == 'morbida'}


def scindi(pagine, d, morbide, rnd):
    out = []
    for p in pagine:
        pp = []
        for r in p:
            rr = []
            for w in r:
                u = DIVIDI(w)
                punti = [i for i in range(1, len(u)) if (u[i - 1], u[i]) in morbide] if len(u) >= 3 else []
                if punti and rnd.random() < d:
                    i = rnd.choice(punti)
                    rr += [''.join(u[:i]), ''.join(u[i:])]
                else:
                    rr.append(w)
            pp.append(rr)
        out.append(pp)
    return out


def genera(classi, tabella, parole_file, finali, seme):
    cartella = os.path.join(e50.LAVORO, 'e53_finali_%d_seme_%d' % (finali, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read()
    righe = []
    for riga in conf.splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        elif riga.startswith('method.morph.use_word_final_substitutions='):
            riga = 'method.morph.use_word_final_substitutions=%s' % ('true' if finali else 'false')
        righe.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % e48.FORZA,
                    '-Dcomposizione.file=' + parole_file, '-Dcomposizione.quota=%g' % Q,
                    '-Dcomposizione.pagina=%g' % LAM, '-Dcomposizione.seme=%d' % (48 + seme),
                    '-Dcomposizione.giunture=1', '-Dcomposizione.nuove=1', '-Drecente.paragrafi=%d' % K,
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    return [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)], \
        hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def v6_v7(pagine):
    a, b = [], []
    for p in pagine:
        for r in p:
            L = [len(DIVIDI(w)) for w in r]
            a += L[:-1]
            b += L[1:]
    c = np.array(sorted(Counter(w for p in pagine for r in p for w in r).values(), reverse=True)[:1000], float)
    zipf = float(np.polyfit(np.log(np.arange(1, len(c) + 1)), np.log(c), 1)[0])
    return {'V6_autocorrelazione_lunghezze': float(np.corrcoef(a, b)[0, 1]), 'V7_zipf': zipf}


def misura(pagine):
    return dict(e48.misura(pagine, DIVIDI), **e49.validazione(pagine), **e51.extra(pagine), **v6_v7(pagine))


def main():
    os.makedirs(e50.LAVORO, exist_ok=True)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_file = os.path.join(e50.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(trascrizione.parole(corrente)) + '\n')
    tabella = os.path.join(e50.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = e50.compila()
    morbide = giunture_morbide()
    pv = pagine_voynich(corrente)
    ris = OrderedDict()
    v = misura(pv)
    ris['Voynich'] = v
    # controllo: finali accesi e d = 0 riproducono la combinazione dell'e51 (seme 19)
    _, imp = genera(classi, tabella, parole_file, True, 19)
    e51_testo = os.path.join(e50.LAVORO, 'q_0.1_l_0.75_k_0_n_1_seme_19', 'generate', 'generated_text.txt')
    corpo = [l for l in open(e51_testo, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    ris['validita_uguale_e51'] = imp == hashlib.md5('\n'.join(corpo).encode()).hexdigest()
    print('validita', ris['validita_uguale_e51'], flush=True)
    medie = OrderedDict()
    for finali in FINALI:
        generati = {s: genera(classi, tabella, parole_file, finali, s)[0] for s in SEMI}
        for d in SCISSIONE:
            gruppo = []
            for s in SEMI:
                pagine = scindi(generati[s], d, morbide, random.Random(53 + s))
                r = misura(pagine)
                ris['finali %s, d %.2f, seme %d' % (finali, d, s)] = r
                gruppo.append(r)
            chiavi = [c for c, x in gruppo[0].items() if isinstance(x, (int, float))]
            m = {c: sum(g[c] for g in gruppo) / len(gruppo) for c in chiavi}
            m['compatibile'] = e48.compatibile(m)
            val = e51.validazione(m, v)
            m['validazione'] = {'V1': val['V1'], 'V4': val['V4'],
                                'V6': m['V6_autocorrelazione_lunghezze'] >= 0.08,
                                'V7': abs(m['V7_zipf'] - v['V7_zipf']) <= 0.10,
                                'V3 (bersaglio)': val['V3'], 'V5 (bersaglio)': val['V5']}
            medie['finali %s, d %.2f' % ('accese' if finali else 'spente', d)] = m
            print('MEDIA finali %s d %.2f: rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f uniche %.2f unioni x%.2f R %.2f quota %.3f V6 %.3f zipf %.2f | %s %s' % (
                finali, d, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
                m['confine'], m['hapax_34000'], m['unione_attestata'] / m['unione_caso'], m['V3_R'] or 0,
                m['V3_quota_media'], m['V6_autocorrelazione_lunghezze'], m['V7_zipf'],
                'COMPATIBILE' if m['compatibile'] else '', ' '.join(c for c, x in m['validazione'].items() if x)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e53_scissione.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    out = ['# e53 — Parole scritte in due pezzi e firma di fine parola', '',
           'Modello dell\'e51 (q 0,10, λ 0,75, K 0). d = probabilità di scrivere una parola in due pezzi a una '
           'giuntura morbida; "finali" = sostituzioni di fine parola del generatore. Medie su tre semi. Validità '
           '(finali accese = e51): %s. Fuori campione: V1, V4, V6 (autocorrelazione delle lunghezze ≥ 0,08), V7 '
           '(Zipf ±0,10); V3 e V5 sono bersagli. Preregistrazione: `preregistrazioni/e53.md`.'
           % ('sì' if ris['validita_uguale_e51'] else 'NO'), '',
           '| testo | h2 | ripetizione | somigl. riga | 6 righe | legame | uniche | unioni/caso | R | quota pagina | autocorr. lunghezze | Zipf | compatibile | validazione |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.2f | %.3f | %.3f | %.2f | | |' % (
               v['h2'], v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'],
               v['hapax_34000'], v['unione_attestata'] / v['unione_caso'], v['V3_R'], v['V3_quota_media'],
               v['V6_autocorrelazione_lunghezze'], v['V7_zipf'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.2f | %.3f | %.3f | %.2f | %s | %s |' % (
            nome, m['h2'], m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
            m['confine'], m['hapax_34000'], m['unione_attestata'] / m['unione_caso'], m['V3_R'] or 0,
            m['V3_quota_media'], m['V6_autocorrelazione_lunghezze'], m['V7_zipf'], 'sì' if m['compatibile'] else 'no',
            ', '.join(c for c, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e53_scissione.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
