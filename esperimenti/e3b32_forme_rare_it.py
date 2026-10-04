# -*- coding: utf-8 -*-
"""Esperimento e3b32: e3b30 (ripresa dalla riga sopra per frequenza) ed e3b31 (ripetizione nella riga per frequenza) con
la trascrizione IT.

Preregistrazione: preregistrazioni/e3b32.md. Scrive risultati/e3b32_forme_rare_it.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3a80_catena_takahashi as e3a80
import e3b30_copia_frequenza as e3b30
import e3b31_memoria_frequenza as e3b31

RISULTATI = os.path.join(QUI, '..', 'risultati')


def analizza(pars, funzione, freq, rnd):
    blocchi = [funzione(p, freq) for p in pars]
    s = e3b30.somma(blocchi)
    boot = defaultdict(list)
    for _ in range(e3b30.BOOT):
        sb = e3b30.somma([blocchi[rnd.randrange(len(blocchi))] for _ in blocchi])
        for c, v in sb.items():
            if v[1] is not None:
                boot[c].append(v[1])
    ic = {c: [sorted(v)[int(0.025 * len(v))], sorted(v)[int(0.975 * len(v)) - 1]] for c, v in boot.items()}
    ris = OrderedDict((c, OrderedDict([('parole', s[c][2]), ('eccesso_relativo', s[c][1]), ('IC95_relativo', ic.get(c))])) for c in e3b30.CLASSI if c in s)
    r, f = ris['rara'], ris['frequente']
    return ris, ('si ritrova' if r['IC95_relativo'][0] > f['IC95_relativo'][1] else 'non si ritrova')


def main():
    rnd = random.Random(3232)
    pars = [[r for r in par if r] for pp in e3a80.pagine_it() for par in pp]
    pars = [p for p in pars if len(p) >= 3]
    freq = Counter(w for par in pars for r in par for w in r)
    out = OrderedDict()
    for nome, f in (('riga sopra (e3b30)', e3b30.paragrafo), ('dentro la riga (e3b31)', e3b31.paragrafo)):
        ris, es = analizza(pars, f, freq, rnd)
        out[nome] = OrderedDict([('classi', ris), ('esito', es)])
        print(nome, json.dumps(out[nome], ensure_ascii=False), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3b32_forme_rare_it.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b32 — Le preferenze per le forme rare (e3b30, e3b31) si ritrovano con Takahashi?', '', 'Preregistrazione: `preregistrazioni/e3b32.md`. ZL: riga sopra rare +31%, frequenti +15%; dentro la riga rare +40%, frequenti +8%.', '']
    for nome, x in out.items():
        md += ['## %s' % nome, '', '| classe | parole | eccesso relativo | IC 95% |', '|---|---|---|---|']
        md += ['| %s | %d | %+.2f | %+.2f – %+.2f |' % (c, y['parole'], y['eccesso_relativo'], y['IC95_relativo'][0], y['IC95_relativo'][1]) for c, y in x['classi'].items()]
        md += ['', 'Esito: **%s**.' % x['esito'], '']
    open(os.path.join(RISULTATI, 'e3b32_forme_rare_it.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
