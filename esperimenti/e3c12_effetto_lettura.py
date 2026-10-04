# -*- coding: utf-8 -*-
"""Esperimento e3c12: la memoria e il consumo con le lettere sono un effetto di lettura (segni deboli, inchiostro)?

Parte 1: pendenza per lettera a parità di parole e classe (e3c10) separata per le scelte "robuste" (qo/o, k/t, -ey/-dy:
segni grandi che l'inchiostro debole non confonde) e per sh/ch (il trattino di sh può svanire). ZL e IT, con i bordi.

Parte 2: sulle righe che ZL e IT dividono nello stesso numero di parole, memoria (e3b62 + e3b70) e pendenza per lettera
con tutte le parole di ZL contro le sole parole in cui ZL e IT leggono la stessa scelta (le altre restano al loro posto
ma escono dalla classe).

Preregistrazione: preregistrazioni/e3c12.md. Scrive risultati/e3c12_effetto_lettura.json e .md.
"""
import json, os, sys
from collections import OrderedDict

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e341_fonti as e341
import e3b45_raccordo_a_capo as e3b45
import e3b54_memoria_oltre_parole as e3b54
import e3b62_memoria_nullo_largo as e3b62
import e3b70_memoria_intervalli as e3b70
import e3c09_regressione_lettere_parole as e3c09
import e3c10_strati_lettere_parole as e3c10

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 500
BOOT = 2000
ROBUSTE = ('qo/o', 'k/t', '-ey/-dy')
NEUTRO = ('·',)


def pendenza_preparate(cc, n_u, rng):
    """Pendenza per lettera dentro gli strati (classe, d), da classi già preparate con e3c09.prepara."""
    cc = OrderedDict((k, c) for k, c in cc.items() if len(c['I']) and len(set(c['val'])) > 1)
    un = np.concatenate([c['uni'][c['I']] for c in cc.values()])
    cl = np.concatenate([np.full(len(c['I']), n) for n, c in enumerate(cc.values())])
    d = np.concatenate([c['d'] for c in cc.values()])
    x = np.concatenate([c['L'] for c in cc.values()])
    _, strato = np.unique(cl * 1000 + d.astype(int), return_inverse=True)
    n_s = int(strato.max()) + 1
    y = np.concatenate([e3c09.eccesso(c, c['val']) for c in cc.values()])
    mu = float(np.mean([e3c10.pendenza(e3c10.statistiche(strato, x, np.concatenate([e3c09.eccesso(c, e3b54.rimescola(c, rng)) for c in cc.values()]),
                                                          un, n_u, n_s).sum(0)) for _ in range(PERM)]))
    st = e3c10.statistiche(strato, x, y, un, n_u, n_s)
    oss = float(e3c10.pendenza(st.sum(0)))
    boot = np.array([e3c10.pendenza(st[rng.integers(0, n_u, n_u)].sum(0)) - mu for _ in range(BOOT)])
    return OrderedDict([('coppie', int(len(y))), ('effetto', oss - mu), ('IC95', [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))])])


def memoria_preparate(cc, rng):
    pr = e3b62.prova(cc, rng)['insieme']
    iv = e3b70.intervallo([e3b70.per_unita(c) for c in cc.values()], pr['nullo'], rng)
    return OrderedDict([('coppie_vicine', pr['coppie_vicine']), ('effetto', iv['effetto']), ('IC95', iv['IC95'])])


def righe_allineate(mano):
    """Pagine con mano nota: liste di righe allineate (ZL, IT) con lo stesso numero di parole, parole come tuple di segni
    (None per le parole con segni incerti in una delle due)."""
    zl = {(r.pagina, r.numero): r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))}
    it = {(r.pagina, r.numero): r for r in trascrizione.testo_corrente(trascrizione.leggi('IT'))}
    pagine, ordine = {}, []
    for k, r in zl.items():
        if k not in it or len(r.parole) != len(it[k].parole) or not mano.get(k[0]):
            continue
        coppie = []
        for a, b in zip(r.parole, it[k].parole):
            ok = trascrizione.pulita(a) and trascrizione.pulita(b)
            coppie.append((tuple(e3b62.D(a)), tuple(e3b62.D(b)), ok))
        if k[0] not in pagine:
            pagine[k[0]] = []
            ordine.append(k[0])
        pagine[k[0]].append(coppie)
    return [pagine[p] for p in ordine], [mano[p] for p in ordine]


def unita_classe(pag, f, solo_concordi):
    """Righe di parole ZL; le parole fuori dalla classe (o discordi, se richiesto) diventano neutre con la stessa lunghezza."""
    out = []
    for righe in pag:
        rr = []
        for riga in righe:
            r = []
            for a, b, ok in riga:
                fa = f(a) if ok else None
                tiene = fa is not None
                if tiene and solo_concordi:
                    fb = f(b)
                    tiene = fb is not None and fb[0] == fa[0]
                r.append(a if tiene else NEUTRO * max(len(a), 1))
            rr.append(r)
        out.append(rr)
    return out


def main():
    rng = np.random.default_rng(3312)
    mano = {}
    for r in trascrizione.leggi('ZL'):
        mano.setdefault(r.pagina, r.mano)
    p1 = OrderedDict()
    for q, pd in (('ZL', e341.pagine()), ('IT', e3b45.pagine_it())):
        uu, ss = e3b62.voynich(pd, mano)
        for nome, chiavi in (('robuste (qo/o, k/t, -ey/-dy)', ROBUSTE), ('sh/ch', ('sh/ch',))):
            cc = OrderedDict((k, e3c09.prepara(uu, ss, e3b62.CV[k])) for k in chiavi)
            p1['%s, %s' % (q, nome)] = pendenza_preparate(cc, len(uu), rng)
            print('parte 1', q, nome, json.dumps(p1['%s, %s' % (q, nome)]), flush=True)
    pag, ss = righe_allineate(mano)
    p2 = OrderedDict()
    quote = OrderedDict()
    for k, f in e3b62.CV.items():
        tot = sum(1 for righe in pag for riga in righe for a, b, ok in riga if ok and f(a) is not None)
        conc = sum(1 for righe in pag for riga in righe for a, b, ok in riga if ok and f(a) is not None and f(b) is not None and f(b)[0] == f(a)[0])
        quote[k] = OrderedDict([('parole_ZL_in_classe', tot), ('concordi', conc), ('quota_discordi', 1 - conc / tot)])
    print('quote', json.dumps(quote), flush=True)
    for versione, solo in (('tutte le parole', False), ('solo parole concordi', True)):
        uu_k = {k: unita_classe(pag, f, solo) for k, f in e3b62.CV.items()}
        mem = memoria_preparate(OrderedDict((k, e3b62.prepara(uu_k[k], ss, f)) for k, f in e3b62.CV.items()), rng)
        pen = pendenza_preparate(OrderedDict((k, e3c09.prepara(uu_k[k], ss, f)) for k, f in e3b62.CV.items()), len(pag), rng)
        p2[versione] = OrderedDict([('memoria', mem), ('per_lettera', pen)])
        print('parte 2', versione, json.dumps(p2[versione], default=float), flush=True)
    rob = [p1['%s, robuste (qo/o, k/t, -ey/-dy)' % q]['IC95'] for q in ('ZL', 'IT')]
    sh = [p1['%s, sh/ch' % q]['IC95'] for q in ('ZL', 'IT')]
    if all(x[1] < 0 for x in rob):
        esito1 = 'il consumo con le lettere non viene dai segni deboli'
    elif all(x[1] >= 0 for x in rob) and all(x[1] < 0 for x in sh):
        esito1 = 'il consumo potrebbe venire dai segni deboli'
    else:
        esito1 = 'incerto'
    t, c = p2['tutte le parole']['memoria'], p2['solo parole concordi']['memoria']
    if c['IC95'][0] > 0 and c['effetto'] >= 2 / 3 * t['effetto']:
        esito2 = 'la memoria non è un effetto di lettura discorde'
    elif c['effetto'] < t['effetto'] / 2:
        esito2 = 'la memoria è in parte un effetto di lettura discorde'
    else:
        esito2 = 'incerto'
    out = OrderedDict([('parte1', p1), ('quote_discordi', quote), ('parte2', p2), ('esito_parte1', esito1), ('esito_parte2', esito2)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c12_effetto_lettura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e3c12 — Memoria e consumo con le lettere: effetto di lettura?', '', 'Preregistrazione: `preregistrazioni/e3c12.md`.', '',
          '## Parte 1: pendenza per lettera a parità di parole (e3c10), con i bordi', '', '| trascrizione, classi | coppie | per lettera (IC 95%) |', '|---|---|---|']
    for k, x in p1.items():
        md.append('| %s | %d | %+.4f (%+.4f – %+.4f) |' % (k, x['coppie'], x['effetto'], x['IC95'][0], x['IC95'][1]))
    md += ['', 'Esito parte 1: **%s**.' % esito1, '', '## Parte 2: righe allineate ZL–IT, tutte le parole contro le sole concordi', '',
           '| classe | parole ZL nella classe | concordi con IT | quota discordi |', '|---|---|---|---|']
    for k, x in quote.items():
        md.append('| %s | %d | %d | %.3f |' % (k, x['parole_ZL_in_classe'], x['concordi'], x['quota_discordi']))
    md += ['', '| versione | memoria (IC 95%) | per lettera (IC 95%) |', '|---|---|---|']
    for k, x in p2.items():
        m, p = x['memoria'], x['per_lettera']
        md.append('| %s | %+.4f (%+.4f – %+.4f) | %+.4f (%+.4f – %+.4f) |' % (k, m['effetto'], m['IC95'][0], m['IC95'][1], p['effetto'], p['IC95'][0], p['IC95'][1]))
    md += ['', 'Esito parte 2: **%s**.' % esito2]
    open(os.path.join(RISULTATI, 'e3c12_effetto_lettura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
