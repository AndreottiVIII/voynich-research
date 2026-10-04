# -*- coding: utf-8 -*-
"""Esperimento e3c63: il legame verticale sul margine sinistro negli scribi veri (batteria scribi, 4). Nel Voynich una
riga evita di cominciare con lo stesso inizio della riga sopra (e3a25 – e3a33: qo-, o-, d-, y-, ch- evitati). Qui, per
ogni manoscritto Menota, lo stesso conto con il primo segno della prima parola della riga, contro il nullo che rimescola
l'ordine delle righe nella pagina (i file Menota non segnano i paragrafi). Riferimento: Voynich ZL (e3a33, rifatto
nella stessa esecuzione).

Preregistrazione: preregistrazioni/e3c63.md. Scrive risultati/e3c63_margine_scribi.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a27_margine_robustezza as e3a27
import e3a33_margine_corretto as e3a33
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANOSCRITTI = ['AM-519a-4to', 'AM-677-4to', 'AM-60-4to', 'AM-242-fol', 'Holm-A-10', 'AM-302-fol']
PERM = 2000


def esito_segno(x):
    return 'evitato' if x['delta'] < 0 and x['z'] < -3.3 else ('ripetuto' if x['delta'] > 0 and x['z'] > 3.3 else '—')


def misura(pars, rnd):
    conta = Counter(a for xs in pars for (a, _) in xs[:-1])
    segni = [s for s, n in conta.most_common() if n >= 30][:12]
    per_s, _ = e3a33.prova(pars, segni, rnd)
    for s, x in per_s.items():
        x['righe_sopra'] = conta[s]
        x['esito'] = esito_segno(x)
    return per_s


def main():
    e3a33.PERM = PERM
    rnd = random.Random(3363)
    ris = OrderedDict()
    ris['Voynich ZL'] = misura(e3a33.righe_utili(e3a27.paragrafi('ZL')), rnd)
    print('Voynich', json.dumps(ris['Voynich ZL'], ensure_ascii=False), flush=True)
    for ms in MANOSCRITTI:
        pars = []
        for _, _, rr in e3c58.leggi(ms):
            xs = [(r[0][0], None) for r in rr if r and r[0]]
            if len(xs) >= 2:
                pars.append(xs)
        ris[ms] = misura(pars, rnd)
        print(ms, json.dumps(ris[ms], ensure_ascii=False), flush=True)
    per_ms = OrderedDict((k, [s for s, x in v.items() if x['esito'] == 'evitato']) for k, v in ris.items())
    generale = [k for k in MANOSCRITTI if len(per_ms[k]) >= 3]
    qualche = [k for k in MANOSCRITTI if per_ms[k]]
    if len(generale) >= 2:
        esito = 'gli scribi evitano gli inizi ripetuti come il Voynich'
    elif not qualche:
        esito = 'nessuno scriba evita gli inizi ripetuti'
    else:
        esito = 'in parte (evitamento generale in %d manoscritti, qualche segno evitato in %d)' % (len(generale), len(qualche))
    out = OrderedDict([('misure', ris), ('evitati', per_ms), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c63_margine_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c63 — Il margine sinistro negli scribi veri', '', 'Preregistrazione: `preregistrazioni/e3c63.md`. Δ = P(stesso inizio | riga sopra con quell\'inizio) − P(stesso inizio | riga sopra diversa); nullo: righe rimescolate nella pagina (Voynich: nel paragrafo, come e3a33).', '',
          '| testo | inizio | righe sopra | Δ | nullo | z | esito |', '|---|---|---|---|---|---|---|']
    for k, v in ris.items():
        for s, x in v.items():
            md.append('| %s | %s | %d | %+.3f | %+.3f | %.1f | %s |' % (k, s, x['righe_sopra'], x['delta'], x['nullo'], x['z'], x['esito']))
    md += ['', 'Segni evitati: ' + '; '.join('%s: %s' % (k, ', '.join(v) or 'nessuno') for k, v in per_ms.items()) + '.', '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c63_margine_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
