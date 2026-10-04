# -*- coding: utf-8 -*-
"""Esperimento e3b31: ripetizione (uguale o a una modifica) fra le 4 parole precedenti nella stessa riga, per classe di
frequenza, contro le stesse posizioni di un'altra riga del paragrafo.

Preregistrazione: preregistrazioni/e3b31.md. Scrive risultati/e3b31_memoria_frequenza.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e341_fonti as e341
import e385_calo as e385
import e3b30_copia_frequenza as e3b30

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
BOOT = 1000


def paragrafo(par, freq):
    sim = e385.simili_unita(par)
    out = defaultdict(lambda: [0.0, 0.0, 0])
    for i, r in enumerate(par):
        for a in range(4, len(r)):
            w = r[a]
            if len(w) < 3:
                continue
            altre = [par[j] for j in range(len(par)) if j not in (i, i - 1) and len(par[j]) >= a]
            if not altre:
                continue
            c = e3b30.classe(freq[w])
            x = out[c]
            x[0] += bool(sim[w] & set(r[a - 4:a]))
            x[1] += sum(bool(sim[w] & set(o[a - 4:a])) for o in altre) / len(altre)
            x[2] += 1
    return out


def main():
    rnd = random.Random(3231)
    pars = []
    for pp in e341.pagine().values():
        for par in pp:
            rr = [[w for w in (tuple(D(x)) for x in r) if w] for r in par]
            rr = [r for r in rr if r]
            if len(rr) >= 3:
                pars.append(rr)
    freq = Counter(w for par in pars for r in par for w in r)
    blocchi = [paragrafo(p, freq) for p in pars]
    s = e3b30.somma(blocchi)
    boot = defaultdict(list)
    for _ in range(BOOT):
        sb = e3b30.somma([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi])
        for c, v in sb.items():
            if v[1] is not None:
                boot[c].append(v[1])
    ic = {c: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for c, v in boot.items()}
    ris = OrderedDict((c, OrderedDict([('parole', s[c][2]), ('eccesso', s[c][0]), ('eccesso_relativo', s[c][1]), ('IC95_relativo', ic.get(c))])) for c in e3b30.CLASSI if c in s)
    r, f = ris.get('rara'), ris.get('frequente')
    if r and f and r['IC95_relativo'][0] > f['IC95_relativo'][1]:
        esito = 'anche la memoria corta favorisce le parole rare'
    elif r and f and f['IC95_relativo'][0] > r['IC95_relativo'][1]:
        esito = 'favorisce le frequenti'
    else:
        esito = 'nessuna preferenza'
    out = OrderedDict([('classi', ris), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b31_memoria_frequenza.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b31 — Anche la ripetizione dentro la riga favorisce le parole rare?', '', 'Preregistrazione: `preregistrazioni/e3b31.md`. Riga sopra (e3b30): rare +31%, frequenti +15%.', '',
          '| classe di frequenza | parole | eccesso per parola | eccesso relativo | IC 95% relativo |', '|---|---|---|---|---|']
    md += ['| %s | %d | %+.4f | %+.2f | %+.2f – %+.2f |' % (c, x['parole'], x['eccesso'], x['eccesso_relativo'], x['IC95_relativo'][0], x['IC95_relativo'][1]) for c, x in ris.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3b31_memoria_frequenza.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
