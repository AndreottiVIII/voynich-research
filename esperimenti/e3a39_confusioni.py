# -*- coding: utf-8 -*-
"""Esperimento e3a39: le sostituzioni di segno negli "errori" (parole uniche a una sostituzione da parole frequenti)
cadono sui segni su cui ZL e IT non concordano (confusioni di lettura) piu' della variazione normale fra parole frequenti?

Preregistrazione: preregistrazioni/e3a39.md. Scrive risultati/e3a39_confusioni.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)


def sost(a, b):
    """Coppia di segni (ordinata alfabeticamente) se a e b differiscono per una sola sostituzione, altrimenti None."""
    if len(a) != len(b):
        return None
    d = [(x, y) for x, y in zip(a, b) if x != y]
    return tuple(sorted(d[0])) if len(d) == 1 else None


def main():
    rnd = random.Random(3139)
    zl = {(r.pagina, r.numero): r for r in trascrizione.leggi('ZL') if r.tipo[0] == 'P'}
    it = {(r.pagina, r.numero): r for r in trascrizione.leggi('IT') if r.tipo[0] == 'P'}
    conf = Counter()
    for k in set(zl) & set(it):
        a, b = zl[k].parole, it[k].parole
        if len(a) != len(b):
            continue
        for x, y in zip(a, b):
            if x != y and trascrizione.pulita(x) and trascrizione.pulita(y):
                s = sost(tuple(D(x)), tuple(D(y)))
                if s:
                    conf[s] += 1
    tot = sum(conf.values())
    insieme, acc = set(), 0
    for s, n in conf.most_common():
        if acc >= 0.8 * tot:
            break
        insieme.add(s)
        acc += n
    freq = Counter(tuple(D(w)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) for w in r.parole if trascrizione.pulita(w))
    per_lung = defaultdict(list)
    for w, n in freq.items():
        if n >= 5:
            per_lung[len(w)].append(w)
    err = []
    frequenti = {w for w, n in freq.items() if n >= 20}
    fr_lung = defaultdict(list)
    for w in frequenti:
        fr_lung[len(w)].append(w)
    for w, n in freq.items():
        if n != 1:
            continue
        ss = {sost(w, v) for v in fr_lung[len(w)]} - {None}
        if len(ss) == 1:
            err.append(next(iter(ss)))
    var = []
    for L, ws in per_lung.items():
        for i in range(len(ws)):
            for j in range(i + 1, len(ws)):
                s = sost(ws[i], ws[j])
                if s:
                    var.append(s)
    q = lambda xs: sum(1 for s in xs if s in insieme) / len(xs)
    qe, qv = q(err), q(var)
    boot = sorted(q([err[rnd.randrange(len(err))] for _ in err]) - q([var[rnd.randrange(len(var))] for _ in var]) for _ in range(2000))
    ic = [boot[50], boot[1949]]
    esito = 'gli errori somigliano a confusioni di lettura' if ic[0] > 0 else ('gli errori evitano le confusioni' if ic[1] < 0 else 'no: gli errori hanno le sostituzioni della variazione normale')
    out = OrderedDict([('confusioni', tot), ('insieme_confondibile', [['/'.join(s), conf[s]] for s in sorted(insieme, key=lambda s: -conf[s])]),
                       ('errori', len(err)), ('variazione_normale', len(var)), ('q_errori', qe), ('q_variazione', qv), ('differenza', qe - qv), ('IC95', ic),
                       ('sostituzioni_negli_errori', [['/'.join(s), n] for s, n in Counter(err).most_common(12)]),
                       ('sostituzioni_nella_variazione', [['/'.join(s), n] for s, n in Counter(var).most_common(12)]), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False)[:2500], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a39_confusioni.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a39 — Gli "errori" sono confusioni di lettura dei trascrittori?', '', 'Preregistrazione: `preregistrazioni/e3a39.md`.', '',
          'Confusioni di lettura fra ZL e IT (una sola sostituzione): %d. Insieme confondibile (80%%): %s.' % (tot, ', '.join('%s %d' % tuple(x) for x in out['insieme_confondibile'])), '',
          '| gruppo | sostituzioni | quota nell\'insieme confondibile |', '|---|---|---|',
          '| errori (parole uniche) | %d | %.3f |' % (len(err), qe), '| variazione normale (parole con almeno 5 occorrenze) | %d | %.3f |' % (len(var), qv), '',
          'Differenza %+.3f (IC 95%% %+.3f – %+.3f).' % (qe - qv, ic[0], ic[1]), '',
          'Sostituzioni più frequenti negli errori: %s.' % ', '.join('%s %d' % tuple(x) for x in out['sostituzioni_negli_errori']),
          'Nella variazione normale: %s.' % ', '.join('%s %d' % tuple(x) for x in out['sostituzioni_nella_variazione']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a39_confusioni.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
