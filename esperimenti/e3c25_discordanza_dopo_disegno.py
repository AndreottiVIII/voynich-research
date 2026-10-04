# -*- coding: utf-8 -*-
"""Esperimento e3c25: dopo il salto di un disegno, ZL e IT leggono diversamente qo/o più spesso che altrove? Righe di ZL con
lo stesso numero di parole in IT (allineate per pagina e numero di riga); per le parole di ZL nella classe qo/o, quota in
cui IT legge l'altra scelta (o una parola fuori classe), per la prima parola dopo un salto e per le altre parole interne.
Rapporto delle quote con intervallo ricampionando pagine.

Preregistrazione: preregistrazioni/e3c25.md. Scrive risultati/e3c25_discordanza_dopo_disegno.json e .md.
"""
import json, os, re, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e3b62_memoria_nullo_largo as e3b62

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 5000


def separatori_zl(r):
    """Separatori fra le parole di una riga di ZL ('|' per il salto del disegno), come in e386."""
    s = re.sub(r'<![^>]*>', '', r.grezza)
    s = s.replace('<%>', '').replace('<$>', '').replace('<->', '|').replace('<~>', '.')
    s = re.sub(r'<@[^>]*>', '', s)
    s = re.sub(r'<[^>]*>', '', s)
    s = re.sub(r'\[([^\]]*)\]', trascrizione._scegli, s)
    s = s.replace('{', '').replace('}', '').replace("'", '')
    s = re.sub(r'@\d{3};', '*', s)
    seps, prec, n = [], None, 0
    for p in [p for p in re.split(r'([.,|]+)', s) if p]:
        if re.fullmatch(r'[.,|]+', p):
            prec = '|' if '|' in p else '.'
            continue
        n += 1
        if n > 1:
            seps.append(prec or '.')
        prec = None
    return seps


def main():
    rng = np.random.default_rng(3325)
    f = e3b62.CV['qo/o']
    zl = {(r.pagina, r.numero): r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    it = {(r.pagina, r.numero): r for r in trascrizione.testo_corrente(trascrizione.leggi('IT'))}
    righe = []
    for k, r in zl.items():
        if k not in it or len(r.parole) != len(it[k].parole):
            continue
        seps = separatori_zl(r)
        if len(seps) != len(r.parole) - 1:
            continue
        righe.append((k[0], r.parole, it[k].parole, seps))
    pagine = sorted({x[0] for x in righe})
    ip = {p: i for i, p in enumerate(pagine)}
    conta = np.zeros((len(pagine), 2, 2))  # pagina, gruppo (0 altre interne, 1 dopo il salto), [parole, discordi]
    for p, a, b, seps in righe:
        for i in range(1, len(a) - 1):
            if not (trascrizione.pulita(a[i]) and trascrizione.pulita(b[i])):
                continue
            fa = f(tuple(e3b62.D(a[i])))
            if fa is None:
                continue
            fb = f(tuple(e3b62.D(b[i])))
            g = 1 if seps[i - 1] == '|' else 0
            conta[ip[p], g, 0] += 1
            conta[ip[p], g, 1] += 0 if (fb is not None and fb[0] == fa[0]) else 1
    tot = conta.sum(0)
    q = tot[:, 1] / tot[:, 0]
    boot = []
    for _ in range(BOOT):
        t = conta[rng.integers(0, len(pagine), len(pagine))].sum(0)
        if t[0, 0] > 0 and t[1, 0] > 0 and t[0, 1] > 0:
            boot.append((t[1, 1] / t[1, 0]) / (t[0, 1] / t[0, 0]))
    boot = np.array(boot)
    rapporto = float(q[1] / q[0]) if q[0] > 0 else None
    ic = [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))]
    ris = OrderedDict([('altre_parole_interne', OrderedDict([('parole', int(tot[0, 0])), ('discordi', int(tot[0, 1])), ('quota', float(q[0]))])),
                       ('prima_dopo_il_disegno', OrderedDict([('parole', int(tot[1, 0])), ('discordi', int(tot[1, 1])), ('quota', float(q[1]))])),
                       ('rapporto', rapporto), ('IC95', ic)])
    if ic[0] > 1:
        esito = 'dopo il disegno i trascrittori discordano di più su qo/o: indizio di difficoltà di lettura'
    elif ic[1] < 3:
        esito = 'dopo il disegno i trascrittori non discordano molto di più: nessun indizio di difficoltà di lettura'
    else:
        esito = 'incerto'
    ris['esito'] = esito
    print(json.dumps(ris, ensure_ascii=False), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e3c25_discordanza_dopo_disegno.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c25 — Dopo il disegno ZL e IT leggono qo/o diversamente più spesso?', '', 'Preregistrazione: `preregistrazioni/e3c25.md`.', '',
          '| parole di ZL nella classe qo/o | parole | discordi con IT | quota |', '|---|---|---|---|',
          '| altre parole interne | %d | %d | %.3f |' % (tot[0, 0], tot[0, 1], q[0]),
          '| prima parola dopo il disegno | %d | %d | %.3f |' % (tot[1, 0], tot[1, 1], q[1]),
          '', 'Rapporto delle quote: %s (IC 95%% %.2f – %.2f).' % ('—' if rapporto is None else '%.2f' % rapporto, ic[0], ic[1]), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3c25_discordanza_dopo_disegno.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
