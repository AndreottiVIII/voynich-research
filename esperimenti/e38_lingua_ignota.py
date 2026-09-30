# -*- coding: utf-8 -*-
"""Esperimento 38 (esplorativo): dove mette la categoria la Lingua Ignota di Ildegarda?

Il glossario (XII secolo) e' ordinato per categorie (Dio, angeli, persone, corpo,
malattie, ranghi, mestieri, tempo, vestiti, casa, piante, uccelli, insetti). Si
raggruppano le voci in blocchi di 25 numeri consecutivi dell'ordine originale e si
chiede in quale posizione della parola sta l'informazione sul blocco: all'inizio,
come nelle lingue filosofiche del Seicento, o alla fine.

Dati: glossario ricompilato da Roth 1880 (archivio Wayback, vedi dati/FONTI.md),
circa 730 voci su 1011 (una fonte amatoriale, con qualche errore:
per esempio #0005 "diabolus" ha la parola di #0004). Preregistrazione: preregistrazioni/e36-e38.md.
Scrive risultati/e38_lingua_ignota.json e .md.
"""
import html, json, os, re, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import posizioni
from posizioni import Blocco

RISULTATI = os.path.join(QUI, '..', 'risultati')
GLOSSARIO = os.path.join(QUI, '..', 'dati', 'cache', 'letteratura', 'ignota_unmasqued.html')
BLOCCO = 25
_VOCE = re.compile(r'</strong>\s*([^<]+?)\s*<small[^>]*>\(<em>(.*?)#(\d{4})(?:/(\d{4}))?</em>\)</small>')


def voci():
    """{numero: (parola, glossa)} ; le voci ripetute nella pagina contano una volta."""
    testo = open(GLOSSARIO, encoding='utf-8', errors='replace').read()
    out = {}
    for parole, glossa, numero, numero2 in _VOCE.findall(testo):
        # "Abiza, Comzimaz ... #0278/0704": due parole con due numeri, una per numero
        forme = [re.sub(r'[^a-z]', '', f.split()[0]) for f in html.unescape(parole).lower().split(',')
                 if f.split()]
        numeri = [int(numero)] + ([int(numero2)] if numero2 else [])
        for i, n in enumerate(numeri):
            forma = forme[min(i, len(forme) - 1)] if forme else ''
            if forma and n <= 1011:
                out.setdefault(n, (forma, html.unescape(glossa).strip(' ;')))
    return out


def main():
    tutte = voci()
    blocchi = [Blocco(n // BLOCCO, 0, (n // BLOCCO) % 10, [list(p)]) for n, (p, _) in sorted(tutte.items())]
    ris = {'voci': len(tutte), 'blocco': BLOCCO}
    p = posizioni.profilo(blocchi)
    p['stabilita'] = posizioni.stabilita(blocchi)
    ris['profilo'] = p
    # finali e iniziali piu' tipiche di ciascun blocco: per leggere il risultato a occhio
    esempi = {}
    for n, (parola, glossa) in sorted(tutte.items()):
        esempi.setdefault(n // BLOCCO, []).append('%s (%s)' % (parola, glossa.split(';')[0].replace('Latin gloss: ', '')))
    ris['esempi'] = {str(k * BLOCCO): v[:6] for k, v in esempi.items()}
    q = p['posizioni']
    print('voci %d, blocchi %d, R %s' % (len(tutte), p['gruppi'], p['R']))
    for k, v in q.items():
        print('  %-10s quota %.4f  z %.1f  p %.3f' % (k, v['quota'], v['z'], v['p']))
    os.makedirs(RISULTATI, exist_ok=True)
    with open(os.path.join(RISULTATI, 'e38_lingua_ignota.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1, default=str)
    righe = ['# e38 — Lingua Ignota: in quale posizione sta la categoria', '',
             '%d voci del glossario (su 1011), in blocchi di %d numeri consecutivi dell\'ordine '
             'originale; parole di almeno 4 lettere (%d). Quota = (informazione mutua blocco/lettera − '
             'media di 200 rimescolamenti) / entropia della lettera.' % (len(tutte), BLOCCO, p['parole']), '',
             '| posizione | quota | z | p |', '|---|---|---|---|']
    for k, v in q.items():
        righe.append('| %s | %.4f | %.1f | %.3f |' % (k, v['quota'], v['z'], v['p']))
    righe += ['', 'R = %s; togliendo un decimo dei blocchi per volta: %s–%s.' % (
        fmt(p['R']), fmt(p['stabilita']['min']), fmt(p['stabilita']['max']))]
    with open(os.path.join(RISULTATI, 'e38_lingua_ignota.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')


def fmt(x):
    return '—' if x is None else ('∞' if x == float('inf') else '%.2f' % x)


if __name__ == '__main__':
    main()
