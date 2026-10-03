# -*- coding: utf-8 -*-
"""Esperimento 268b: come l'e268, con rho scelto sul seme 1 perche' la misura dell'e273 sia la piu' vicina a quella del
Voynich (+0,047), a pagella non inferiore all'e241. Stampa ogni risultato appena arriva.

Preregistrazione: preregistrazioni/e268b.md. Scrive risultati/e268b_prime_righe_misura.json e .md.
"""
import json, os, statistics, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e266_discriminatore_forte as e266
import e268_prime_righe as e268

RISULTATI = os.path.join(QUI, '..', 'risultati')
RHO, SEME_SCELTA, SEMI_VERIFICA, E273_VOYNICH = (0.1, 0.15, 0.2, 0.25, 0.3, 0.4), 1, (7, 8, 9), 0.047


def lavoro(args):
    tipo, rho, seme = args
    k = e251._prepara()
    c = k['c']
    rr = e236.dopo(e268.genera_pr(k['c2'], dict(e251.CONF, gamma=0.0), seme, rho, e268.prime_per_pagina(c)), k['freq'], 100 + seme)
    pg = e251.pagella_grezza(c, rr)
    d266 = e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))
    out = OrderedDict([('rho', rho), ('seme', seme), ('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                       ('AUC_e266', d266['AUC']), ('AUC_G8', d266['AUC_per_gruppo']['G8'])])
    if tipo == 'scelta' or seme == SEMI_VERIFICA[0]:
        out['e273'] = e268.misura_e273(rr)
    if tipo == 'verifica':
        out['AUC_e231'] = e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']
    return args, out


def tutti(lavori):
    n, ris = int(os.environ.get('PROCESSI', '1')), {}
    with Pool(max(n, 1)) as pool:
        for a, x in pool.imap_unordered(lavoro, lavori):
            ris[a] = x
            print('%s rho %.2f seme %d: pagella %d riga %s | AUC e266 %.3f G8 %.3f%s' % (a[0], a[1], a[2], x['pagella'], x['riga'], x['AUC_e266'], x['AUC_G8'],
                  (' | e273 %+.3f (z %.1f)' % (x['e273']['D1_meno_D2'], x['e273']['z'] or 0)) if 'e273' in x else ''), flush=True)
    return ris


def main():
    sc = tutti([('scelta', r, SEME_SCELTA) for r in (0.0,) + RHO])
    b1 = sc[('scelta', 0.0, SEME_SCELTA)]
    ammessi = [r for r in RHO if sc[('scelta', r, SEME_SCELTA)]['pagella'] >= b1['pagella'] and (sc[('scelta', r, SEME_SCELTA)]['riga'] or not b1['riga'])]
    if ammessi:
        rs = min(ammessi, key=lambda r: (abs(sc[('scelta', r, SEME_SCELTA)]['e273']['D1_meno_D2'] - E273_VOYNICH), r))
    else:
        rs = min(RHO, key=lambda r: (-sc[('scelta', r, SEME_SCELTA)]['pagella'], r))
    print('ammessi %s -> rho* %.2f' % (ammessi, rs), flush=True)
    vv = tutti([('verifica', r, s) for s in SEMI_VERIFICA for r in (0.0, rs)])
    br = {'base': [vv[('verifica', 0.0, s)] for s in SEMI_VERIFICA], 'rho': [vv[('verifica', rs, s)] for s in SEMI_VERIFICA]}
    medie = {n: OrderedDict([('pagella_somma', sum(x['pagella'] for x in xs)), ('semi_con_riga', sum(bool(x['riga']) for x in xs)),
                             ('AUC_e231_media', statistics.mean(x['AUC_e231'] for x in xs)), ('AUC_e266_media', statistics.mean(x['AUC_e266'] for x in xs)),
                             ('AUC_G8_media', statistics.mean(x['AUC_G8'] for x in xs))]) for n, xs in br.items()}
    z273 = br['rho'][0]['e273']['z']
    motivi = []
    if not (z273 or 0) > 3:
        motivi.append('e273')
    if medie['rho']['AUC_G8_media'] > medie['base']['AUC_G8_media'] - 0.05:
        motivi.append('G8')
    if medie['rho']['pagella_somma'] < medie['base']['pagella_somma'] or medie['rho']['semi_con_riga'] < medie['base']['semi_con_riga']:
        motivi.append('pagella o riga')
    esito = 'passo superato' if not motivi else 'non superato: ' + ' + '.join(motivi)
    out = OrderedDict([('scelta_seme_1', [sc[('scelta', r, SEME_SCELTA)] for r in (0.0,) + RHO]), ('ammessi', ammessi), ('rho', rs), ('verifica', br),
                       ('medie', medie), ('esito', esito), ('motivo', motivi)])
    json.dump(out, open(os.path.join(RISULTATI, 'e268b_prime_righe_misura.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    mb, mr = medie['base'], medie['rho']
    md = ['# e268b — Il registro delle prime righe, secondo tentativo: ρ alla misura del Voynich', '',
          'ρ scelto sul seme 1 perché la misura dell\'e273 sia la più vicina a quella del Voynich (+0,047), a pagella non inferiore all\'e241: **%.2f**. '
          'Preregistrazione: `preregistrazioni/e268b.md`.' % rs, '', '| ρ (seme 1) | pagella | riga | AUC e266 | G8 | e273 |', '|---|---|---|---|---|---|']
    for x in out['scelta_seme_1']:
        md.append('| %.2f | %d | %s | %.3f | %.3f | %+.3f (z %.1f) |' % (x['rho'], x['pagella'], 'sì' if x['riga'] else 'no', x['AUC_e266'], x['AUC_G8'],
                                                                     x['e273']['D1_meno_D2'], x['e273']['z'] or 0))
    md += ['', '| seme | braccio | pagella | riga | mancano | AUC e231 | AUC e266 | G8 |', '|---|---|---|---|---|---|---|---|']
    for i, s in enumerate(SEMI_VERIFICA):
        for n in ('base', 'rho'):
            x = br[n][i]
            md.append('| %d | %s | %d/18 | %s | %s | %.3f | %.3f | %.3f |' % (s, 'e241' if n == 'base' else 'ρ %.2f' % rs, x['pagella'], 'sì' if x['riga'] else 'no',
                                                                       ', '.join(x['mancano']) or '—', x['AUC_e231'], x['AUC_e266'], x['AUC_G8']))
    md += ['', "Misura dell'e273 sul seme 7: e241 %+.3f (z %.1f); ρ %+.3f (z %.1f)." % (br['base'][0]['e273']['D1_meno_D2'], br['base'][0]['e273']['z'] or 0,
                                                                                    br['rho'][0]['e273']['D1_meno_D2'], z273 or 0), '',
           'Medie: e241 pagella %d, riga in %d semi, AUC %.3f / %.3f, G8 %.3f; ρ pagella %d, riga in %d semi, AUC %.3f / %.3f, G8 %.3f.' % (
               mb['pagella_somma'], mb['semi_con_riga'], mb['AUC_e231_media'], mb['AUC_e266_media'], mb['AUC_G8_media'],
               mr['pagella_somma'], mr['semi_con_riga'], mr['AUC_e231_media'], mr['AUC_e266_media'], mr['AUC_G8_media']), '', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e268b_prime_righe_misura.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, flush=True)


if __name__ == '__main__':
    main()
