# -*- coding: utf-8 -*-
"""Esperimento 223b: verifica del candidato tedesco dell'e223 secondo il protocollo per i candidati. Prove: 8 ripartenze,
meta' invertite, Voynich rimescolato dentro la riga, generatore trattato come il Voynich con cinque semi, controllo
positivo nelle stesse forme. Ogni prova ha il suo generatore casuale ('e223b-' + nome), quindi PROCESSI non cambia nulla.

Preregistrazione: preregistrazioni/e223b.md. Scrive risultati/e223b_verifica_tedesco.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192
import e213_decifrazione_di_dominio as e213
import e223_dominio_volgari as e223

RISULTATI = os.path.join(QUI, '..', 'risultati')
LINGUA, SEMI_GENERATORE = 'German', (1, 2, 3, 4, 5)
_MOD = {}


def modelli():
    if not _MOD:
        _MOD['m'] = e223.modelli(LINGUA)
    return _MOD['m']


def inverti(pagine):
    """Ruota di una pagina: le pagine di stima diventano quelle di verifica e viceversa."""
    return pagine[1:] + pagine[:1]


def rimescola(pagine, rnd):
    out = []
    for d, rr in pagine:
        nuove = []
        for r in rr:
            r = list(r)
            rnd.shuffle(r)
            nuove.append(r)
        out.append((d, nuove))
    return out


def generatore(pv, seme):
    """Il controllo negativo dell'e223 (e162 con le impostazioni dell'e192), con il seme dato."""
    vp = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(vp), 0.4
    e153.variante = e192.variante
    per_g = OrderedDict()
    for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(vp, e162.D), seme, None):
        per_g.setdefault(pag, []).append((ini, ps))
    pul_g = e160.ripulisci(list(per_g.values()))
    return e213.a_unita([(e213.dominio_di(pv[p][0]), [[w if trascrizione.pulita(w) else None for w in ps] for _, ps in rr])
                         for p, rr in zip(per_g, pul_g) if p in pv and e213.dominio_di(pv[p][0])])


def una(args):
    nome, pagine, ripartenze = args
    mod, _, _ = modelli()
    e213.RIPARTENZE = ripartenze
    return nome, e213.prova(nome, pagine, mod, random.Random('e223b-' + nome))


def main():
    pv = e213.pagine_voynich()
    voy = e213.a_unita([(e213.dominio_di(s), rr) for p, (s, rr) in pv.items() if e213.dominio_di(s)])
    _, ctrl, _ = modelli()
    simboli = len({u for _, rr in voy for r in rr for u in r})
    # controllo positivo identico a quello dell'e223 (stesso seme, stesso ordine delle chiamate)
    pos = e213.controllo_positivo(voy, ctrl, random.Random('e223-' + LINGUA), simboli)
    prove = [('positivo', pos, 4),
             ('positivo, metà invertite', inverti(pos), 4),
             ('positivo, rimescolato nella riga', rimescola(pos, random.Random('e223b-rimescola-positivo')), 4),
             ('Voynich, 8 ripartenze', voy, 8),
             ('Voynich, metà invertite', inverti(voy), 4),
             ('Voynich, rimescolato nella riga', rimescola(voy, random.Random('e223b-rimescola-Voynich')), 4)]
    prove += [('generatore, seme %d' % s, generatore(pv, s), 4) for s in SEMI_GENERATORE]
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '2'))) as pool:
        for nome, r in pool.imap(una, prove):
            ris[nome] = r
            json.dump(ris, open(os.path.join(RISULTATI, 'e223b_verifica_tedesco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    z = {k: (v['z'] if v['z'] is not None else float('nan')) for k, v in ris.items()}
    zg = max(z['generatore, seme %d' % s] for s in SEMI_GENERATORE)
    valido = z['positivo'] > 4 and z['positivo, metà invertite'] > 4 and z['positivo'] - z['positivo, rimescolato nella riga'] >= 3
    prove_c = OrderedDict([('1. 8 ripartenze, z > 4', z['Voynich, 8 ripartenze'] > 4),
                           ('2. metà invertite, z > 4', z['Voynich, metà invertite'] > 4),
                           ('3. Voynich − rimescolato ≥ 3', z['Voynich, 8 ripartenze'] - z['Voynich, rimescolato nella riga'] >= 3),
                           ('4. Voynich ≥ massimo generatori + 3', z['Voynich, 8 ripartenze'] >= zg + 3)])
    if not valido:
        esito = 'non valido'
    elif all(prove_c.values()):
        esito = 'il candidato regge (nessuna lettura: si esaminano gli esempi)'
    else:
        esito = 'artefatto (prove mancate: %s)' % ', '.join(k for k, v in prove_c.items() if not v)
    out = OrderedDict([('prove', ris), ('z', z), ('massimo_generatori', zg), ('valido', valido), ('criteri', prove_c), ('esito', esito)])
    json.dump(out, open(os.path.join(RISULTATI, 'e223b_verifica_tedesco.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e223b — Verifica del candidato tedesco dell\'e223', '',
          'Modelli, controllo positivo e misura dell\'e223 (z della discriminazione fra sezioni fuori campione, 1.000 permutazioni). '
          'Preregistrazione: `preregistrazioni/e223b.md`.', '', '| prova | ripartenze | Δ | nullo | z |', '|---|---|---|---|---|']
    for nome, _, rip in prove:
        r = ris[nome]
        md.append('| %s | %d | %.4f | %.4f | %.1f |' % (nome, rip, r['delta'], r['nullo'], z[nome]))
    md += ['', 'Validità (positivo > 4 nelle due direzioni e rimescolato ≥ 3 sotto): **%s**.' % ('sì' if valido else 'no'), '',
           'Criteri: ' + '; '.join('%s: %s' % (k, 'sì' if v else 'no') for k, v in prove_c.items()) + '.', '',
           'Esempi del Voynich con 8 ripartenze: %s' % '; '.join('%s: %s' % (d, ' / '.join(x[:60] for x in v))
                                                             for d, v in ris['Voynich, 8 ripartenze']['esempi'].items()), '',
           'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e223b_verifica_tedesco.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
