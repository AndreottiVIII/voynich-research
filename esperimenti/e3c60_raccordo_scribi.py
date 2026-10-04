# -*- coding: utf-8 -*-
"""Esperimento e3c60: il "raccordo" negli scribi veri. Per ogni coppia di forme di lettera (lista dell'e3c58) a inizio
parola, informazione mutua fra la forma scelta e l'ultimo segno della parola prima nella stessa riga; a fine parola, fra
la forma scelta e il primo segno della parola dopo. Nullo dell'e3b58: la scelta rimescolata fra le occorrenze della
stessa parola coperta nella stessa pagina. Sei manoscritti Menota (e3c50, e3c58); riferimento nella stessa esecuzione:
Voynich ZL, qo/o a inizio parola (e3b58) e -l/-r a fine parola.

Preregistrazione: preregistrazioni/e3c60.md. Scrive risultati/e3c60_raccordo_scribi.json e .md.
"""
import json, math, os, sys
from collections import OrderedDict, defaultdict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e341_fonti as e341
import e3b54_memoria_oltre_parole as e3b54
import e3b58_raccordo_scriba as e3b58
import e3b62_memoria_nullo_largo as e3b62
import e3c50_scribi_menota as e3c50
import e3c58_altri_scribi as e3c58

RISULTATI = os.path.join(QUI, '..', 'risultati')
MANOSCRITTI = ['AM-519a-4to', 'AM-677-4to', 'AM-60-4to', 'AM-242-fol', 'Holm-A-10', 'AM-302-fol']
MINIMO = 300
PERM = 1000


def ai_bordi(aa, bb, dove):
    """Classe che guarda solo la prima (dove='inizio') o l'ultima (dove='fine') forma della parola."""
    forme = [(1, tuple(a) if isinstance(a, tuple) else (a,)) for a in aa] + [(0, tuple(b) if isinstance(b, tuple) else (b,)) for b in bb]

    def f(w):
        w = tuple(w)
        for val, s in sorted(forme, key=lambda z: -len(z[1])):
            if dove == 'inizio' and w[:len(s)] == s and len(w) > len(s):
                return val, ('*',) + w[len(s):]
            if dove == 'fine' and w[-len(s):] == s and len(w) > len(s):
                return val, w[:-len(s)] + ('*',)
        return None
    return f


def eventi(pagine, f, dove):
    """(valore, contesto, gruppo): contesto = ultimo segno della parola prima (inizio) o primo della parola dopo (fine)."""
    val, ctx, grp, gruppi, ctxid = [], [], [], {}, {}
    for u, righe in enumerate(pagine):
        for r in righe:
            for i in range(len(r)):
                j = i - 1 if dove == 'inizio' else i + 1
                if j < 0 or j >= len(r) or not r[j]:
                    continue
                x = f(r[i])
                if x is None:
                    continue
                c = r[j][-1] if dove == 'inizio' else r[j][0]
                val.append(x[0])
                ctx.append(ctxid.setdefault(c, len(ctxid)))
                grp.append(gruppi.setdefault((u, x[1]), len(gruppi)))
    return np.array(val, dtype=int), np.array(ctx, dtype=int), np.array(grp, dtype=int), len(ctxid)


def minoritarie(pagine, f):
    xs = [f(w) for righe in pagine for r in righe for w in r]
    xs = [x for x in xs if x]
    per = defaultdict(set)
    for v, t in xs:
        per[t].add(v)
    mi = [v for v, t in xs if len(per[t]) == 2]
    return len(xs), min(sum(mi), len(mi) - sum(mi))


def candidati():
    testi = OrderedDict((m, [rr for _, _, rr in e3c58.leggi(m)]) for m in MANOSCRITTI)
    tab = []
    for m, pp in testi.items():
        for nome, aa, bb in e3c58.COPPIE:
            for dove in ('inizio', 'fine'):
                f = ai_bordi(aa, bb, dove)
                n, mino = minoritarie(pp, f)
                if n:
                    tab.append((m, nome, dove, n, mino, mino >= MINIMO))
    return testi, tab


def v_lr(w):
    if len(w) >= 2 and w[-1] in ('l', 'r'):
        return (1 if w[-1] == 'l' else 0, tuple(w[:-1]) + ('*',))
    return None


def main():
    e3b58.PERM = PERM
    rng = np.random.default_rng(3360)
    testi, tab = candidati()
    fn = {nome: (aa, bb) for nome, aa, bb in e3c58.COPPIE}
    ris = OrderedDict()
    voy = [rr for rr in ([[w for w in (tuple(e3b62.D(x)) for x in r) if w] for par in pars for r in par] for pars in e341.pagine().values()) if rr]
    for nome, f, dove in (('Voynich ZL, qo/o a inizio parola', e3b54.v_qo, 'inizio'), ('Voynich ZL, -l/-r a fine parola', v_lr, 'fine')):
        x = e3b58.prova(*eventi(voy, f, dove), rng)
        x['tipo'] = 'riferimento'
        ris[nome] = x
        print(nome, json.dumps(x), flush=True)
    for m, nome, dove, n, mino, entra in tab:
        if not entra:
            continue
        aa, bb = fn[nome]
        x = e3b58.prova(*eventi(testi[m], ai_bordi(aa, bb, dove), dove), rng)
        x['tipo'], x['minoritarie_nei_misti'] = 'scriba', mino
        k = '%s, %s a %s parola' % (m, nome, dove)
        ris[k] = x
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    rif = min(ris['Voynich ZL, qo/o a inizio parola']['effetto_su_entropia'], ris['Voynich ZL, -l/-r a fine parola']['effetto_su_entropia'])
    sc = OrderedDict((k, x) for k, x in ris.items() if x['tipo'] == 'scriba')
    forti = [k for k, x in sc.items() if x['p'] < 0.01 and x['effetto_su_entropia'] >= rif / 2]
    deboli = [k for k, x in sc.items() if x['p'] < 0.01 and x['effetto_su_entropia'] < rif / 2]
    if forti:
        esito = 'almeno uno scriba ha un raccordo grande come quello del Voynich'
    elif deboli:
        esito = 'gli scribi hanno un raccordo, ma più debole della metà di quello del Voynich'
    else:
        esito = 'nessun raccordo negli scribi'
    out = OrderedDict([('ingresso', [OrderedDict(zip(('manoscritto', 'scelta', 'dove', 'parole', 'minoritarie_nei_misti', 'entra'), t)) for t in tab]),
                       ('misure', ris), ('soglia_metà_voynich', rif / 2), ('forti', forti), ('deboli', deboli), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c60_raccordo_scribi.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c60 — Il raccordo negli scribi veri', '', 'Preregistrazione: `preregistrazioni/e3c60.md`. Informazione mutua fra la forma scelta e il segno della parola vicina (prima per l\'inizio, dopo per la fine); nullo che tiene ferme le parole (e3b58).', '',
          '| testo, scelta | occorrenze | quota forma 1 | entropia | MI | MI nullo | effetto | effetto / entropia | z | p |', '|---|---|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        md.append('| %s | %d | %.3f | %.3f | %.4f | %.4f | %+.4f | %+.3f | %+.1f | %.3f |' % (k, x['occorrenze'], x['quota_1'], x['entropia'], x['MI'], x['MI_nullo'], x['effetto'], x['effetto_su_entropia'] or 0, x['z'], x['p']))
    md += ['', 'Soglia (metà del Voynich, il più piccolo dei due riferimenti): %.3f.' % (rif / 2), '', 'Esito: **%s**.' % esito,
           'Forti: %s. Deboli: %s.' % (', '.join(forti) or 'nessuno', ', '.join(deboli) or 'nessuno')]
    open(os.path.join(RISULTATI, 'e3c60_raccordo_scribi.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
