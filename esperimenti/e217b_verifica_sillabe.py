# -*- coding: utf-8 -*-
"""Esperimento 217b: verifica del candidato dell'e217 (una parola Voynich = una sillaba) con 8 ripartenze, il Voynich
rimescolato, il generatore trattato come il Voynich, e la chiave stimata su meta' delle righe e applicata all'altra.

Preregistrazione: preregistrazioni/e217b.md. Scrive risultati/e217b_verifica_sillabe.json e .md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, ricottura, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192
import e217_parole_sillabe as e217

RISULTATI = os.path.join(QUI, '..', 'risultati')
CANDIDATE = ('cinese con toni', 'vietnamita', 'giapponese (morfemi)')


def segmenta(righe):
    """Come e217.voynich: solo le SIMBOLI parole piu' frequenti; le altre spezzano; segmenti di almeno N+1."""
    top = {w for w, _ in Counter(w for r in righe for w in r).most_common(e217.SIMBOLI)}
    out = []
    for r in righe:
        cur = []
        for w in r:
            if w in top:
                cur.append(w)
            else:
                if len(cur) >= e217.N + 1:
                    out.append(cur)
                cur = []
        if len(cur) >= e217.N + 1:
            out.append(cur)
    return out


def generatore_come_voynich():
    vp = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(vp), 0.4
    e153.variante = e192.variante
    per = OrderedDict()
    for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(vp, e162.D), 1, None):
        per.setdefault(pag, []).append((ini, ps))
    pul = e160.ripulisci(list(per.values()))
    return segmenta([[w for w in ps if trascrizione.pulita(w)] for p in pul for _, ps in p])


def rimescola(righe, rnd):
    tutte = [w for r in righe for w in r]
    rnd.shuffle(tutte)
    out, i = [], 0
    for r in righe:
        out.append(tutte[i:i + len(r)])
        i += len(r)
    return out


def meta(righe, modello, rnd, ripartenze):
    pari, dispari = righe[0::2], righe[1::2]
    g = ricottura.Grammi(pari, modello.n)
    esito, _ = ricottura.risolvi(g, modello, rnd, ripartenze=ripartenze)
    dentro = ricottura.punteggio_righe(ricottura.decifra(pari, esito.chiave, g, modello), modello)
    fuori = ricottura.punteggio_righe(ricottura.decifra(dispari, esito.chiave, g, modello), modello)
    return OrderedDict([('pari', dentro), ('dispari', fuori), ('calo', fuori - dentro)])


def una(args):
    nome, voy, gen = args
    rnd = random.Random('e217b-' + nome)
    u = e217.unita_di(nome)
    car, top = e217.alfabeto(u)
    k = int(len(u) * 0.8)
    modello = ricottura.ModelloLettere(''.join(car(x) for x in u[:k]) + ''.join(chr(0x4E00 + i) for i in range(e217.UNITA)), n=e217.N)
    L = sum(map(len, voy))
    pos, vera = e217.codifica([car(x) for x in u[k:k + L]], random.Random('e217b-pos-' + nome))
    r = OrderedDict()
    e217.RIPARTENZE = 8
    r['Voynich, 8 ripartenze'] = e217.attacca(voy, modello, random.Random('e217b-' + nome + '-8'))
    e217.RIPARTENZE = 3
    r['Voynich rimescolato'] = e217.attacca(rimescola(voy, random.Random('e217b-mesc-' + nome)), modello, random.Random('e217b-' + nome + '-mesc'))
    r['generatore come il Voynich'] = e217.attacca(gen, modello, random.Random('e217b-' + nome + '-gen'))
    r['meta Voynich'] = meta(voy, modello, random.Random('e217b-' + nome + '-metaV'), 3)
    r['meta positivo'] = meta(pos, modello, random.Random('e217b-' + nome + '-metaP'), 3)
    print('%s: %s' % (nome, {k2: (round(v['punteggio'], 3) if 'punteggio' in v else {a: round(b, 3) for a, b in v.items()}) for k2, v in r.items()}), flush=True)
    return nome, r


def main():
    voy = e217.voynich()
    gen = generatore_come_voynich()
    print('Voynich %d parole in %d segmenti; generatore %d parole in %d segmenti' % (sum(map(len, voy)), len(voy), sum(map(len, gen)), len(gen)), flush=True)
    prima = json.load(open(os.path.join(RISULTATI, 'e217_parole_sillabe.json'), encoding='utf-8'))['lingue']
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, voy, gen) for n in CANDIDATE]):
            ris[nome] = r
    esiti = OrderedDict()
    righe = []
    for nome, r in ris.items():
        p, n_ = prima[nome]['positivo']['punteggio'], prima[nome]['negativo']['punteggio']
        d = p - n_
        v8 = r['Voynich, 8 ripartenze']['punteggio']
        c1 = (v8 - n_) / d >= 0.5
        c2 = v8 - r['Voynich rimescolato']['punteggio'] >= 0.5 * d
        c3 = v8 - r['generatore come il Voynich']['punteggio'] >= 0.5 * d
        c4 = r['meta Voynich']['calo'] >= r['meta positivo']['calo'] - 0.2
        regge = c1 and c2 and c3 and c4
        motivi = [m for m, c in (('posizione con 8 ripartenze', c1), ('non supera il rimescolato', c2), ('non supera il generatore', c3),
                                 ('cala fuori campione', c4)) if not c]
        esiti[nome] = 'regge' if regge else 'artefatto (%s)' % ', '.join(motivi)
        righe.append('| %s | %.3f | %.3f | %.2f | %.3f | %.3f | %.3f / %.3f | %.3f / %.3f | %s |' % (
            nome, p, n_, (v8 - n_) / d, r['Voynich rimescolato']['punteggio'], r['generatore come il Voynich']['punteggio'], v8,
            r['meta Voynich']['calo'], r['meta positivo']['pari'], r['meta positivo']['calo'], esiti[nome]))
    json.dump({'lingue': ris, 'esiti': esiti}, open(os.path.join(RISULTATI, 'e217b_verifica_sillabe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e217b — Verifica del candidato dell\'e217', '',
          "Punteggi (log-probabilità media per unità). Positivo e negativo dall'e217; posizione del Voynich con 8 ripartenze; Voynich rimescolato e "
          "generatore trattato come il Voynich (3 ripartenze); chiave stimata sulle righe pari e applicata alle dispari (calo dispari − pari). "
          'Preregistrazione: `preregistrazioni/e217b.md`.', '',
          '| lingua | positivo | negativo | posizione (8 ripartenze) | rimescolato | generatore | Voynich / calo fuori campione | positivo: pari / calo | esito |',
          '|---|---|---|---|---|---|---|---|---|'] + righe
    open(os.path.join(RISULTATI, 'e217b_verifica_sillabe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esiti)


if __name__ == '__main__':
    main()
