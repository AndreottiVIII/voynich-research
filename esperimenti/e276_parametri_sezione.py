# -*- coding: utf-8 -*-
"""Esperimento 276: kappa e chi del generatore regolati per gruppo di sezione (erbario, biologica, ricette e stelle, altre).
Base: il migliore fra e241 ed e243b secondo l'AUC dell'e266. Scelta per gruppo sul seme 1 con l'AUC dell'e231 sulle sole
pagine del gruppo; verifica sui semi 7-9 contro lo stesso generatore con parametri globali.

Il generatore per sezione e' composto: per ogni combinazione scelta si genera tutto il manoscritto con lo stesso seme e si
prendono le pagine dei gruppi che l'hanno scelta. Con tutti i gruppi alla combinazione globale coincide con il generatore
globale (controllo di validita').

Preregistrazione: preregistrazioni/e276.md. Scrive risultati/e276_parametri_sezione.json e .md.
"""
import json, os, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e230_generatore_meccanismi as e230
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e243_riuso_esplicito as e243
import e243b_riuso_su_vocabolario as e243b
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRUPPI = OrderedDict([('erbario', ('H',)), ('biologica', ('B',)), ('ricette e stelle', ('S',)), ('altre', None)])
KAPPA, CHI, GLOBALE = (0.5, 1.0, 1.5), (0.1, 0.2, 0.3), (1.0, 0.2)
SEME_SCELTA, SEMI_VERIFICA, RIF_E241_E266 = 1, (7, 8, 9), 0.937


def gruppo(s):
    for nome, sez in GRUPPI.items():
        if sez is None or s in sez:
            return nome


def base(pv):
    """(nome, funzione, parametri) del generatore di base."""
    j = json.load(open(os.path.join(RISULTATI, 'e243b_riuso_su_vocabolario.json'), encoding='utf-8'))
    conf = dict(e224.BASE, eta=1.0, kappa=GLOBALE[0], chi=GLOBALE[1])
    if j['AUC_e266_media'] < RIF_E241_E266:
        dist = e243.distanze_voynich(pv)
        ds = list(range(1, e243.D_MAX + 1))
        ws = [dist['R'][1][d] + dist['V'][1][d] for d in ds]
        prm = dict(conf, ell_r=1.0, tau=0.0, phi=j['phi'], fisica=True, distanza=(ds, ws), rip=j['rip'])
        return 'e243b (AUC e266 %.3f)' % j['AUC_e266_media'], e243b.genera, prm
    return 'e241 (AUC e266 %.3f; e243b %.3f)' % (RIF_E241_E266, j['AUC_e266_media']), e233.genera, conf


def componi(gen, c2, prm, scelte, seme):
    """Righe del generatore per sezione: ogni pagina viene dalla generazione con la combinazione del suo gruppo."""
    sez = e230.sezioni()
    corse = {}
    for kx in sorted(set(scelte.values())):
        corse[kx] = gen(c2, dict(prm, kappa=kx[0], chi=kx[1]), seme)
    per_pagina = {kx: {} for kx in corse}
    for kx, rr in corse.items():
        for pag, ini, ps in rr:
            per_pagina[kx].setdefault(pag, []).append((pag, ini, ps))
    ordine = list(OrderedDict.fromkeys(pag for pag, _, _ in next(iter(corse.values()))))
    return [x for pag in ordine for x in per_pagina[scelte[gruppo(sez.get(pag))]][pag]]


def misure(c, rr, vpag, rif, vt266, rif266):
    gp = e232.pagine_di(rr)
    p = e236.pagella(c, rr)
    return OrderedDict([('AUC_e231', e231.confronto(vpag, gp, rif)['AUC']),
                        ('AUC_e266', e266.confronto(vt266, e266.tabella(e243b.righe_ini(rr), rif266))['AUC']),
                        ('pagella', p['pagella']), ('riga', p['riga']), ('mancano', p['mancano'])])


def main():
    c, c2, freq, vpag, rif, pv = e251.contesto()
    vi = e266.voynich_ini()
    rif266 = e231.riferimenti(OrderedDict((p, (l, [r for _, r in rr])) for p, (l, rr) in vi.items()))
    vt266 = e266.tabella(OrderedDict((p, rr) for p, (_, rr) in vi.items()), rif266)
    nome_base, gen, prm = base(pv)
    print('base: %s' % nome_base, flush=True)
    sez = e230.sezioni()
    globali = OrderedDict((g, GLOBALE) for g in GRUPPI)
    identico = componi(gen, c2, prm, globali, SEME_SCELTA) == gen(c2, prm, SEME_SCELTA)
    print('validita\' (tutti i gruppi globali = generatore globale): %s' % identico, flush=True)
    vgr = {g: OrderedDict((p, v) for p, v in vpag.items() if gruppo(sez.get(p)) == g) for g in GRUPPI}
    tabella = OrderedDict()
    for k in KAPPA:
        for x in CHI:
            gp = e232.pagine_di(e236.dopo(gen(c2, dict(prm, kappa=k, chi=x), SEME_SCELTA), freq, 100 + SEME_SCELTA))
            tabella[(k, x)] = OrderedDict((g, e231.confronto(vgr[g], gp, rif)['AUC']) for g in GRUPPI)
            print('kappa %.1f chi %.1f: %s' % (k, x, ' '.join('%s %.3f' % kv for kv in tabella[(k, x)].items())), flush=True)
    ordine = list(tabella)
    scelte = OrderedDict((g, min(ordine, key=lambda kx: (tabella[kx][g], ordine.index(kx)))) for g in GRUPPI)
    print('scelte: %s' % dict(scelte), flush=True)
    ver = []
    for s in SEMI_VERIFICA:
        rg = e236.dopo(gen(c2, prm, s), freq, 100 + s)
        rs = e236.dopo(componi(gen, c2, prm, scelte, s), freq, 100 + s)
        r = OrderedDict([('seme', s), ('globale', misure(c, rg, vpag, rif, vt266, rif266)), ('per_sezione', misure(c, rs, vpag, rif, vt266, rif266))])
        ver.append(r)
        print('seme %d: globale AUC e231 %.3f e266 %.3f pagella %d | per sezione AUC e231 %.3f e266 %.3f pagella %d' % (
            s, r['globale']['AUC_e231'], r['globale']['AUC_e266'], r['globale']['pagella'],
            r['per_sezione']['AUC_e231'], r['per_sezione']['AUC_e266'], r['per_sezione']['pagella']), flush=True)
    media = lambda q, m: statistics.mean(x[q][m] for x in ver)
    d266 = media('globale', 'AUC_e266') - media('per_sezione', 'AUC_e266')
    aiuta = d266 >= 0.03 and media('per_sezione', 'pagella') >= media('globale', 'pagella')
    esito = 'non valido' if not identico else ('aiuta' if aiuta else 'non aiuta')
    ris = OrderedDict([('base', nome_base), ('validita_identico_globale', identico),
                       ('scelta_seme_1', OrderedDict(('kappa %.1f chi %.1f' % kx, v) for kx, v in tabella.items())),
                       ('scelte', OrderedDict((g, OrderedDict([('kappa', kx[0]), ('chi', kx[1])])) for g, kx in scelte.items())),
                       ('verifica', ver),
                       ('medie', OrderedDict((q, OrderedDict((m, media(q, m)) for m in ('AUC_e231', 'AUC_e266', 'pagella'))) for q in ('globale', 'per_sezione'))),
                       ('differenza_AUC_e266', d266), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e276_parametri_sezione.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e276 — Parametri del generatore per sezione', '',
          'Base: %s. κ e χ scelti per gruppo sul seme 1 con l\'AUC dell\'e231 sulle pagine del gruppo; globale κ %.1f, χ %.1f. '
          'Validità (tutti i gruppi globali = generatore globale): %s. Preregistrazione: `preregistrazioni/e276.md`.' % (
              nome_base, GLOBALE[0], GLOBALE[1], 'sì' if identico else 'NO'), '',
          '| κ | χ | ' + ' | '.join(GRUPPI) + ' |', '|---|---|' + '---|' * len(GRUPPI)]
    for (k, x), v in tabella.items():
        md.append('| %.1f | %.1f | %s |' % (k, x, ' | '.join('%.3f' % v[g] for g in GRUPPI)))
    md += ['', 'Scelte: ' + '; '.join('%s κ %.1f χ %.1f' % (g, kx[0], kx[1]) for g, kx in scelte.items()) + '.', '',
           '| seme | AUC e231 globale | per sezione | AUC e266 globale | per sezione | pagella globale | per sezione |', '|---|---|---|---|---|---|---|']
    for r in ver:
        g, p = r['globale'], r['per_sezione']
        md.append('| %d | %.3f | %.3f | %.3f | %.3f | %d/18 | %d/18 |' % (r['seme'], g['AUC_e231'], p['AUC_e231'], g['AUC_e266'], p['AUC_e266'], g['pagella'], p['pagella']))
    md += ['', 'Differenza media dell\'AUC dell\'e266 (globale − per sezione): %+.3f.' % d266, '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e276_parametri_sezione.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
