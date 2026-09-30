# -*- coding: utf-8 -*-
"""Esperimento 50: recenza delle fonti (Recente.java) e parole composte volutamente nuove
(Composizione.java, -Dcomposizione.nuove=1), sopra il generatore dell'e49.

Controlli di validita': con q = 0 e K = 0 testo identico all'e23; con q = 0,3, lambda 0,9, K = 0
e novita' spenta, testo identico alla stessa combinazione dell'e49 (seme 19).
Preregistrazione: preregistrazioni/e50.md. Serve Java.
Scrive risultati/e50_recenza_novita.json e .md.
"""
import hashlib, json, os, shutil, subprocess, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
import e49_composizione_giunture as e49
e48 = e49.e48
from e07_codifiche import pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
LAVORO = os.path.join(e22.LAVORO, 'recenza_novita')
RECENTE = os.path.join(QUI, '..', 'analisi', 'timm_schinner', 'Recente.java')
QUOTE = (0.2, 0.3, 0.4)
LAMBDA = (0.75, 0.9)
RECENZA = (0, 2, 5)
SEMI = (19, 1, 2)


def compila():
    """Le aggiunte dell'e49 (compilate da e48.compila in LAVORO) piu' la recenza delle fonti."""
    e48.LAVORO = LAVORO
    sorgente_classi = e48.compila()
    sorgente = os.path.join(LAVORO, 'java')
    chooser = os.path.join(sorgente, 'de', 'voynich', 'text', 'sourcechooser', 'PageSourceGroupChooser.java')
    testo = open(chooser, encoding='utf-8').read()
    vecchio = '        int rand = randomNumberGenerator.rand(paragraphInitialLinesList.size());'
    nuovo = ('        // recenza (aggiunta, vedi Recente.java): solo le ultime K righe iniziali di paragrafo\n'
             '        int quante = de.voynich.text.Recente.quante(paragraphInitialLinesList.size());\n'
             '        int rand = (paragraphInitialLinesList.size() - quante) + randomNumberGenerator.rand(quante);')
    assert testo.count(vecchio) == 1
    open(chooser, 'w', encoding='utf-8').write(testo.replace(vecchio, nuovo))
    shutil.copy(RECENTE, os.path.join(sorgente, 'de', 'voynich', 'text'))
    shutil.rmtree(sorgente_classi, ignore_errors=True)
    os.makedirs(sorgente_classi)
    files = [os.path.join(d, f) for d, _, fs in os.walk(sorgente) for f in fs if f.endswith('.java')]
    r = subprocess.run(['javac', '-nowarn', '-d', sorgente_classi] + files, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-3000:])
    return sorgente_classi


def genera(classi, tabella, parole_file, q, lam, k, seme, nuove=True):
    cartella = os.path.join(LAVORO, 'q_%g_l_%g_k_%d_n_%d_seme_%d' % (q, lam, k, nuove, seme))
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
                    '-Dcomposizione.giunture=1', '-Dcomposizione.nuove=%d' % nuove, '-Drecente.paragrafi=%d' % k,
                    '-cp', classi, 'de.voynich.text.SelfCitationTextGenerator'], cwd=cartella, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    testo = open(os.path.join(cartella, 'generate', 'generated_text.txt'), encoding='utf-8').read()
    corpo = [l for l in testo.splitlines() if l.strip() and not l.startswith('#')]
    linee = [l.split() for l in corpo]
    pagine = [linee[i:i + e22.RIGHE_PAGINA] for i in range(0, len(linee), e22.RIGHE_PAGINA)]
    return pagine, hashlib.md5('\n'.join(corpo).encode()).hexdigest()


def main():
    os.makedirs(LAVORO, exist_ok=True)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_file = os.path.join(LAVORO, 'parole_voynich.txt')
    with open(parole_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(trascrizione.parole(corrente)) + '\n')
    tabella = os.path.join(LAVORO, 'giunture.tsv')
    e23.tabella_giunture(tabella)
    classi = compila()
    ris = OrderedDict()
    # validita' 1: tutto spento = e23
    classi_e23 = e23.compila()
    ris['validita'] = {}
    for seme in SEMI:
        _, a = genera(classi, tabella, parole_file, 0.0, 0.0, 0, seme, nuove=False)
        _, b = e23.genera(classi_e23, tabella, 3.0, seme, nome='per_e50_seme_%d' % seme)
        ris['validita']['q0 K0 = e23, seme %d' % seme] = a == b
    # validita' 2: novita' e recenza spente = e49 (q 0,3, lambda 0,9, seme 19)
    _, a = genera(classi, tabella, parole_file, 0.3, 0.9, 0, 19, nuove=False)
    e49_testo = os.path.join(e22.LAVORO, 'composizione_giunture', 'q_0.3_l_0.9_seme_19', 'generate', 'generated_text.txt')
    corpo = [l for l in open(e49_testo, encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('#')]
    ris['validita']['spente = e49 (q 0,3, lambda 0,9, seme 19)'] = a == hashlib.md5('\n'.join(corpo).encode()).hexdigest()
    print('validita', ris['validita'], flush=True)
    assert all(ris['validita'].values()), 'le aggiunte spente cambiano il testo'
    pv = pagine_voynich(corrente)
    ris['Voynich'] = dict(e48.misura(pv, glifi), **e49.validazione(pv))
    medie = OrderedDict()
    for k in RECENZA:
        for q in QUOTE:
            for lam in LAMBDA:
                gruppo = []
                for seme in SEMI:
                    pagine, _ = genera(classi, tabella, parole_file, q, lam, k, seme)
                    r = dict(e48.misura(pagine, glifi), **e49.validazione(pagine))
                    ris['K %d, q %.2f, lambda %.2f, seme %d' % (k, q, lam, seme)] = r
                    gruppo.append(r)
                chiavi = [c for c, v in gruppo[0].items() if isinstance(v, (int, float))]
                m = {c: sum(g[c] for g in gruppo) / len(gruppo) for c in chiavi}
                m['compatibile'] = e48.compatibile(m)
                m['validazione'] = e49.esito_validazione(m)
                medie['K %d, q %.2f, lambda %.2f' % (k, q, lam)] = m
                print('MEDIA K %d q %.2f l %.2f: rip %.2f somigl %.1f%%/%.1f%% h2 %.2f confine %.3f uniche %.2f/%.2f | V2 %.3f R %.2f quota %.3f %s %s' % (
                    k, q, lam, m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
                    m['h2'], m['confine'], m['hapax_1000'], m['hapax_34000'], m['V2_ricambio_k1_meno_k20'],
                    m['V3_R'] or 0, m['V3_quota_media'], 'COMPATIBILE' if m['compatibile'] else '',
                    ' '.join(c for c, v in m['validazione'].items() if v)), flush=True)
    ris['medie'] = medie
    with open(os.path.join(RISULTATI, 'e50_recenza_novita.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    v = ris['Voynich']
    out = ['# e50 — Recenza delle fonti e parole composte volutamente nuove', '',
           'Generatore dell\'e49 (composizione con giunture) con novità (la parola composta dev\'essere una forma mai '
           'scritta) e recenza K (le righe iniziali di paragrafo si copiano dalle ultime K; 0 = tutte). Medie su tre '
           'semi. Validità: %s. Criterio e validazione come l\'e49 (V2 non è fuori campione per la recenza). '
           'Preregistrazione: `preregistrazioni/e50.md`.' % ('superata' if all(ris['validita'].values()) else 'FALLITA'), '',
           '| testo | h2 | ripetizione | somigl. riga | 6 righe | legame | uniche 1.000 | uniche 34.000 | V2 | V3 R | V3 quota | compatibile | validazione |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|',
           '| **Voynich** | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.3f | %.2f | %.3f | | |' % (
               v['h2'], v['identiche_vs_riga'], 100 * v['somiglianza_riga'], 100 * v['somiglianza_6_righe'], v['confine'],
               v['hapax_1000'], v['hapax_34000'], v['V2_ricambio_k1_meno_k20'], v['V3_R'], v['V3_quota_media'])]
    for nome, m in medie.items():
        out.append('| %s | %.2f | %.2f | %.1f%% | %.1f%% | %.3f | %.2f | %.2f | %.3f | %.2f | %.3f | %s | %s |' % (
            nome, m['h2'], m['identiche_vs_riga'], 100 * m['somiglianza_riga'], 100 * m['somiglianza_6_righe'],
            m['confine'], m['hapax_1000'], m['hapax_34000'], m['V2_ricambio_k1_meno_k20'], m['V3_R'] or 0,
            m['V3_quota_media'], 'sì' if m['compatibile'] else 'no',
            ', '.join(c for c, x in m['validazione'].items() if x) or '—'))
    with open(os.path.join(RISULTATI, 'e50_recenza_novita.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
