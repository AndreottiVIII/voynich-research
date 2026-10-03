# -*- coding: utf-8 -*-
"""Esperimento 235: salita per coordinate su kappa, chi, tau, ell, alfa (generatore dell'e234, spezzature e prefissi
staccati dopo la generazione) con l'AUC del discriminatore dell'e231 come obiettivo; verifica su semi nuovi.

Preregistrazione: preregistrazioni/e235.md. Scrive risultati/e235_ricerca_discriminatore.json e .md.
"""
import json, os, statistics, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e234_tema_variato as e234

RISULTATI = os.path.join(QUI, '..', 'risultati')
PARTENZA = OrderedDict([('alfa', 1.0), ('tau', 0.0), ('ell', 0.0), ('kappa', 1.0), ('chi', 0.2)])
GRIGLIA = OrderedDict([('alfa', [1.0, 1.3, 1.6]), ('tau', [0.0, 0.5, 1.0]), ('ell', [0.0, 0.5, 1.0]), ('kappa', [0.5, 1.0, 1.5]), ('chi', [0.1, 0.2, 0.3])])
PASSATE, SEME_RICERCA, SEMI_VERIFICA = 2, 1, (2, 3)
_CTX = {}


def contesto():
    if not _CTX:
        c = e224.contesto()
        vpag = e231.voynich()
        _CTX.update(c=c, vpag=vpag, rif=e231.riferimenti(vpag), freq=Counter(c['voy']))
    return _CTX


def valuta(args):
    prm, seme, indice = args
    x = contesto()
    conf = dict(e224.BASE, eta=1.0, **prm)
    r = e234.prova(x['c'], x['vpag'], x['rif'], x['freq'], conf, seme, indice)
    return json.dumps(prm), seme, r


def main():
    corrente = OrderedDict(PARTENZA)
    storia = []
    with Pool(int(os.environ.get('PROCESSI', '2'))) as pool:
        _, _, r0 = valuta((dict(corrente), SEME_RICERCA, 0))
        migliore = r0['AUC']
        storia.append((dict(corrente), migliore))
        print('partenza %s: AUC %.3f' % (dict(corrente), migliore), flush=True)
        for passata in range(PASSATE):
            for par, valori in GRIGLIA.items():
                prove = [dict(corrente, **{par: v}) for v in valori if v != corrente[par]]
                for p, (_, _, r) in zip(prove, pool.imap(valuta, [(p, SEME_RICERCA, 0) for p in prove])):
                    storia.append((dict(p), r['AUC']))
                    print('  %s=%s: AUC %.3f (tipi pagina %.3f, fra le 100 %.3f, uniche %.3f, vicine %.3f, lunghezza %.2f)' % (
                        par, p[par], r['AUC'], r['tipi_su_parole_pagina'], r['fra_le_100'], r['uniche_nel_testo'], r['somiglianza_vicine'],
                        r['lunghezza_media']), flush=True)
                    if r['AUC'] < migliore:
                        corrente, migliore = OrderedDict(p), r['AUC']
                print('passata %d, %s: tengo %s (AUC %.3f)' % (passata + 1, par, corrente[par], migliore), flush=True)
        lavori = [(dict(PARTENZA), s, 100 + s) for s in SEMI_VERIFICA] + [(dict(corrente), s, 100 + s) for s in SEMI_VERIFICA]
        ver = list(pool.imap(valuta, lavori))
    rp = [r for _, _, r in ver[:len(SEMI_VERIFICA)]]
    rf = [r for _, _, r in ver[len(SEMI_VERIFICA):]]
    a0, af = statistics.mean(r['AUC'] for r in rp), statistics.mean(r['AUC'] for r in rf)
    esito = 'indistinguibile' if af <= 0.6 else 'miglioramento' if af <= a0 - 0.05 else 'nessun miglioramento netto'
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    ris = OrderedDict([('partenza', PARTENZA), ('finale', corrente), ('AUC_ricerca_finale', migliore), ('AUC_verifica_partenza', a0), ('AUC_verifica_finale', af),
                       ('verifica_partenza', rp), ('verifica_finale', rf), ('ricerca', storia), ('esito', esito)])
    json.dump(ris, open(os.path.join(RISULTATI, 'e235_ricerca_discriminatore.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('finale %s: AUC ricerca %.3f; verifica partenza %.3f, finale %.3f -> %s' % (dict(corrente), migliore, a0, af, esito), flush=True)
    vv = e234.descrittive(OrderedDict((p, rr) for p, (_, rr) in contesto()['vpag'].items()))
    md = ['# e235 — Ricerca congiunta contro il discriminatore', '',
          "Salita per coordinate (2 passate) su α, τ, ℓ, κ, χ con l'AUC del discriminatore dell'e231 sul seme 1; generatore dell'e234 con η 1, "
          'spezzature σ 0,09 e prefissi staccati π 0,30 dopo la generazione. Verifica sui semi 2–3. Preregistrazione: `preregistrazioni/e235.md`.', '',
          'Partenza: %s. Finale: %s.' % (', '.join('%s %s' % kv for kv in PARTENZA.items()), ', '.join('%s %s' % kv for kv in corrente.items())), '',
          '| | AUC (semi 2–3) | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media |', '|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s |' % ' | '.join('%.3f' % vv[q] for q in cols),
          '| partenza | %.3f | %s |' % (a0, ' | '.join('%.3f' % statistics.mean(r[q] for r in rp) for q in cols)),
          '| finale | %.3f | %s |' % (af, ' | '.join('%.3f' % statistics.mean(r[q] for r in rf) for q in cols)), '',
          'Caratteristiche più pesanti che restano (finale, seme 2; coefficiente positivo = più nel generatore):', '',
          '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in rf[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Ricerca (seme 1): %s.' % '; '.join('%s → %.3f' % (', '.join('%s %s' % kv for kv in p.items()), a) for p, a in storia), '',
           'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e235_ricerca_discriminatore.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
