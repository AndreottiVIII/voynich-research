# -*- coding: utf-8 -*-
"""Esperimento e3c90: potenza della batteria scribi, scelta per scelta (rianalisi dei risultati salvati).

Nota A9 del revisore: negli scribi molte scelte fra allografi sono legate alla posizione nella parola, e resta poca
variazione libera; l'assenza dello "stato" o della deriva potrebbe venire dal non avere niente da misurare. Per ogni
coppia (manoscritto, scelta) si riportano parole, intervallo, effetto minimo visibile con potenza dell'80% e un giudizio:
"assente con potenza" solo se l'estremo alto dell'intervallo sta sotto metà del valore del Voynich (regola dell'e3c83).

Fonti: e3c50 e e3c58 (stato nei sei scribi nordici), e3c77 (stato e deriva nei 73 manoscritti tedeschi, insieme),
e3c62 (deriva nei nordici); Voynich dagli stessi file (e3c77, e3c62) e dall'e3c86 (intervalli per bifoglio).

Preregistrazione: preregistrazioni/e3c90.md. Scrive risultati/e3c90_potenza_scribi.json e .md.
"""
import json, os
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = os.path.join(QUI, '..', 'risultati')
Z80 = (1.96 + 0.84) / 1.96   # da semiampiezza dell'IC al 95% a effetto visibile con potenza 0,8


def carica(n):
    return json.load(open(os.path.join(RISULTATI, n), encoding='utf-8'))


def giudizio(su, meta, lo=None):
    if su < meta:
        return 'assente con potenza'
    if lo is not None and lo > 0:
        return 'presente'
    return 'potenza insufficiente'


def main():
    v77 = carica('e3c77_ref_finestra_deriva.json')['misure']['Voynich ZL']
    VK1, VK23 = v77['K_corretto'][0], (v77['K_corretto'][1] + v77['K_corretto'][2]) / 2
    d62 = carica('e3c62_deriva_scribi.json')['misure']
    VD = min(abs(d62['Voynich ZL, %s' % k]['per_10_segni']) for k in ('qo/o', 'k/t', 'sh/ch', '-ey/-dy'))
    stato, deriva = OrderedDict(), OrderedDict()
    fonti = (('e3c50_scribi_menota.json', 'nordici'), ('e3c58_altri_scribi.json', 'nordici'), ('e3c77_ref_finestra_deriva.json', 'tedeschi (insieme)'))
    for f, gruppo in fonti:
        for k, x in carica(f)['misure'].items():
            if k.startswith('Voynich') or 'K1_IC95' not in x:
                continue
            lo1, hi1 = x['K1_IC95']
            lo23, hi23 = x['K23_IC95']
            nome = ('ReF, ' + k) if f.startswith('e3c77') else k
            stato[nome] = OrderedDict([
                ('gruppo', gruppo), ('parole', x['parole']), ('K1', x['K_corretto'][0]), ('K1_IC95', [lo1, hi1]),
                ('K23', (x['K_corretto'][1] + x['K_corretto'][2]) / 2), ('K23_IC95', [lo23, hi23]),
                ('effetto_minimo_K23', Z80 * (hi23 - lo23) / 2),
                ('giudizio_finestra', giudizio(hi23, VK23 / 2, lo23)), ('giudizio_accanto', giudizio(hi1, VK1 / 2, lo1))])
            if f.startswith('e3c77'):
                dr = x['deriva']
                lo, hi = dr['IC95']
                deriva[nome] = OrderedDict([('gruppo', gruppo), ('parole', dr['parole']), ('per_10_segni', dr['per_10_segni']),
                                            ('IC95_per_10_segni', [10 * lo, 10 * hi]), ('effetto_minimo', Z80 * 10 * (hi - lo) / 2),
                                            ('giudizio', giudizio(10 * max(abs(lo), abs(hi)), VD / 2))])
    for k, x in d62.items():
        if k.startswith(('Voynich', '_')):
            continue
        # nel file dell'e3c62 l'intervallo è per segno (la stima è data anche ogni 10 segni): si porta a 10 segni
        # (correzione dell'8/10/2026: la prima esecuzione lo leggeva come già ogni 10 segni)
        lo, hi = 10 * x['IC95'][0], 10 * x['IC95'][1]
        deriva[k] = OrderedDict([('gruppo', 'nordici'), ('parole', x['parole']), ('per_10_segni', x['per_10_segni']),
                                 ('IC95_per_10_segni', [lo, hi]), ('effetto_minimo', Z80 * (hi - lo) / 2),
                                 ('giudizio', giudizio(max(abs(lo), abs(hi)), VD / 2))])

    def conta(d, chiave):
        c = OrderedDict()
        for x in d.values():
            c[x[chiave]] = c.get(x[chiave], 0) + 1
        return c
    out = OrderedDict([('voynich', OrderedDict([('K1', VK1), ('K23', VK23), ('deriva_minima_per_10_segni', VD)])),
                       ('stato', stato), ('deriva', deriva),
                       ('conteggi', OrderedDict([('finestra', conta(stato, 'giudizio_finestra')), ('accanto', conta(stato, 'giudizio_accanto')),
                                                 ('deriva', conta(deriva, 'giudizio'))]))])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c90_potenza_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c90 — Potenza della batteria scribi, scelta per scelta', '', 'Preregistrazione: `preregistrazioni/e3c90.md`. Voynich: K accanto %.3f, K a 2–3 parole %.3f; deriva minima %.3f ogni 10 segni. "Assente con potenza" = estremo alto sotto metà del Voynich.' % (VK1, VK23, VD), '',
          '## Stato breve', '', '| manoscritto, scelta | gruppo | parole | K accanto (IC) | K 2–3 (IC) | effetto minimo visibile (K 2–3) | finestra | accanto |', '|---|---|---|---|---|---|---|---|']
    for k, x in stato.items():
        md.append('| %s | %s | %d | %+.3f (%+.3f – %+.3f) | %+.3f (%+.3f – %+.3f) | %.3f | %s | %s |' % (k, x['gruppo'], x['parole'], x['K1'], *x['K1_IC95'], x['K23'], *x['K23_IC95'], x['effetto_minimo_K23'], x['giudizio_finestra'], x['giudizio_accanto']))
    md += ['', '## Deriva lungo la riga', '', '| manoscritto, scelta | gruppo | parole | ogni 10 segni (IC) | effetto minimo visibile | giudizio |', '|---|---|---|---|---|---|']
    for k, x in deriva.items():
        md.append('| %s | %s | %d | %+.4f (%+.4f – %+.4f) | %.4f | %s |' % (k, x['gruppo'], x['parole'], x['per_10_segni'], *x['IC95_per_10_segni'], x['effetto_minimo'], x['giudizio']))
    md += ['', '## Conteggi', '']
    for k, c in out['conteggi'].items():
        md.append('- **%s:** %s' % (k, ', '.join('%s %d' % kv for kv in c.items())))
    open(os.path.join(RISULTATI, 'e3c90_potenza_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(out['conteggi'], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
