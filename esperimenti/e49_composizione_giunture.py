# -*- coding: utf-8 -*-
"""Esperimento 49: il generatore che compone parole, con le giunture anche per le parole
composte, e la validazione su proprieta' non usate per costruirlo (V1 curva piatta delle
parole uniche, V2 ricambio del vocabolario, V3 profilo di pagina dell'e36).

Preregistrazione: preregistrazioni/e49.md. Serve Java.
Scrive risultati/e49_composizione_giunture.json e .md.
"""
import hashlib, json, os, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, posizioni, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e48_composizione as e48
from e07_codifiche import pagine_voynich
from e36_posizione_pagina import blocchi_da_pagine, DIVIDI
from e47_vocabolario import ricambio

RISULTATI = os.path.join(QUI, '..', 'risultati')
QUOTE = (0.2, 0.3, 0.4, 0.5)
LAMBDA = (0.6, 0.75, 0.9)
SEMI = (19, 1, 2)
VOYNICH_QUOTA_PAGINA = 0.0525      # e36 esplorativo, Voynich senza strati: media delle quattro posizioni

# la stessa aggiunta dell'e48, ma la parola composta conosce la precedente della riga
e48.LAVORO = os.path.join(e22.LAVORO, 'composizione_giunture')
e48.INSERIMENTO = e48.INSERIMENTO.replace(
    'Composizione.componi(config)',
    'Composizione.componi(config, glyphGroupList.size() > 0 ? '
    'glyphGroupList.get(glyphGroupList.size() - 1).glyphGroup : "")')


def genera(classi, tabella, parole_file, q, lam, seme):
    cartella = os.path.join(e48.LAVORO, 'q_%g_l_%g_seme_%d' % (q, lam, seme))
    os.makedirs(os.path.join(cartella, 'generate'), exist_ok=True)
    conf = open(os.path.join(e22.GENERATORE, 'executable', 'conf.properties'), encoding='utf-8').read()
    righe = []
    for riga in conf.splitlines():
        if riga.startswith('text.lines_to_create='):
            riga = 'text.lines_to_create=%d' % e22.RIGHE
        elif riga.startswith('method.random.pseudo.seed='):
            riga = 'method.random.pseudo.seed=%d' % seme
        righe.append(riga)
    with open(os.path.join(cartella, 'conf.properties'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    subprocess.run(['java', '-Dgiunture.file=' + tabella, '-Dgiunture.forza=%g' % e48.FORZA,
                    '-Dcomposizione.file=' + parole_file, '-Dcomposizione.quota=%g' % q,
                    '-Dcomposizione.pagina=%g' % lam, '-Dcomposizione.seme=%d' % (48 + seme),
                    '-Dcomposizione.giunture=1',
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    linee = [l.split() for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    return [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]


def validazione(pagine):
    parole = [w for p in pagine for r in p for w in r]
    ric = ricambio(parole)
    prof = posizioni.profilo(blocchi_da_pagine(pagine, DIVIDI))
    quota = sum(v['quota'] for v in prof['posizioni'].values()) / len(prof['posizioni'])
    return {'V2_ricambio_k1_meno_k20': ric[1] - ric[20], 'V3_R': prof['R'], 'V3_quota_media': quota}


def esito_validazione(m):
    return {'V1': m['hapax_1000'] - m['hapax_34000'] <= 0.10,
            'V2': m['V2_ricambio_k1_meno_k20'] >= 0.05,
            'V3': (m['V3_R'] is not None and 0.8 <= m['V3_R'] <= 1.25
                   and 0.5 * VOYNICH_QUOTA_PAGINA <= m['V3_quota_media'] <= 1.5 * VOYNICH_QUOTA_PAGINA)}


def main():
    os.makedirs(e48.LAVORO, exist_ok=True)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_file = os.path.join(e48.LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(trascrizione.parole(corrente)) + '\n')
    tabella = os.path.join(e48.LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = e48.compila()
    ris = OrderedDict()
    pv = pagine_voynich(corrente)
    ris['Voynich'] = dict(e48.misura(pv, glifi), **validazione(pv))
    medie = OrderedDict()
    for q in QUOTE:
        for lam in LAMBDA:
            gruppo = []
            for seme in SEMI:
                pagine = genera(classi, tabella, parole_file, q, lam, seme)
                r = dict(e48.misura(pagine, glifi), **validazione(pagine))
                ris['q %.2f, lambda %.2f, seme %d' % (q, lam, seme)] = r
                gruppo.append(r)
            chiavi = [k for k, v in gruppo[0].items() if isinstance(v, (int, float))]
            m = {k: sum(g[k] for g in gruppo) / len(gruppo) for k in chiavi}
            m['compatibile'] = e48.compatibile(m)
            m['validazione'] = esito_validazione(m)
            medie['q %.2f, lambda %.2f' % (q, lam)] = m
            print('MEDIA q %.2f l %.2f: rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f uniche %.2f/%.2f | V2 %.3f R %.2f quota %.3f %s %s' % (
                q, lam, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'], m['h2'],
                m['confine'], m['hapax_1000'], m['hapax_34000'], m['V2_ricambio_k1_meno_k20'], m['V3_R'] or 0,
                m['V3_quota_media'], 'COMPATIBILE' if m['compatibile'] else '',
                ' '.join(k for k, v in m['validazione'].items() if v)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e49_composizione_giunture.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    v = ris['Voynich']
    out = ['# e49 — Composizione con giunture, e validazione fuori campione', '',
           'Come l\'e48, ma le parole composte rispettano la regola delle giunture. Medie su tre semi. Compatibile = '
           'ripetizione ≥ 0,7, somiglianza nella riga ≥ 3%% e calante, h2 ≤ 2,40, legame ≥ 0,15, parole uniche a '
           '34.000 ≥ 0,60. Validazione (non usata per costruire il modello): V1 uniche(1.000) − uniche(34.000) ≤ 0,10; '
           'V2 ricambio k=1 − k=20 ≥ 0,05; V3 profilo di pagina R fra 0,8 e 1,25 e quota fra %.3f e %.3f. '
           'Preregistrazione: `preregistrazioni/e49.md`.' % (0.5 * VOYNICH_QUOTA_PAGINA, 1.5 * VOYNICH_QUOTA_PAGINA), '',
           '| testo | h2 | ripetizione | somigl. riga | 6 righe | legame | uniche 1.000 | uniche 34.000 | V2 | V3 R | V3 quota | compatibile | validazione superata |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.3f | %.2f | %.3f | | |' % (
               v['h2'], v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'],
               v['hapax_1000'], v['hapax_34000'], v['V2_ricambio_k1_meno_k20'], v['V3_R'], v['V3_quota_media'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.3f | %.2f | %.3f | %s | %s |' % (
            nome, m['h2'], m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
            m['confine'], m['hapax_1000'], m['hapax_34000'], m['V2_ricambio_k1_meno_k20'], m['V3_R'] or 0,
            m['V3_quota_media'], 'sì' if m['compatibile'] else 'no',
            ', '.join(k for k, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e49_composizione_giunture.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
