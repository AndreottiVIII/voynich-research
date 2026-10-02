# -*- coding: utf-8 -*-
"""Esperimento 217: risolutore a ricottura con le parole Voynich (ripulite) come simboli e le sillabe/morfemi di lingue
monosillabiche come lettere; controlli positivi e negativi.

Preregistrazione: preregistrazioni/e217.md. Scrive risultati/e217_parole_sillabe.json e .md.
"""
import json, os, random, re, sys
from collections import Counter, OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, ricottura, trascrizione
import e160_testo_ripulito as e160

RISULTATI = os.path.join(QUI, '..', 'risultati')
SIMBOLI, UNITA, N, RIPARTENZE, PER_RIGA = 300, 150, 3, 3, 8
LINGUE = OrderedDict([('cinese con toni', ('Chinese-pinyin', False, 'vietnamita')), ('cinese senza toni', ('Chinese-pinyin', True, 'vietnamita')),
                      ('vietnamita', ('Vietnamese', False, 'cinese senza toni')), ('giapponese (morfemi)', ('Japanese-tok', False, 'cinese con toni')),
                      ('tailandese (parole)', ('Thai-tok', False, 'vietnamita'))])


def unita_di(nome):
    k, senza_toni, _ = LINGUE[nome]
    u = lingue.parole(k)
    if senza_toni:
        u = [re.sub(r'\d', '', x) for x in u]
    return [x for x in u if x]


def alfabeto(unita):
    """prime UNITA-1 unita' -> caratteri; le altre -> carattere 'altro'."""
    top = [x for x, _ in Counter(unita).most_common(UNITA - 1)]
    m = {x: chr(0x4E00 + i) for i, x in enumerate(top)}
    altro = chr(0x4E00 + UNITA - 1)
    return lambda x: m.get(x, altro), top


def voynich():
    pul = e160.ripulisci(e160.pagine_voynich())
    righe = [[w for w in ps if trascrizione.pulita(w)] for p in pul for _, ps in p]
    top = {w for w, _ in Counter(w for r in righe for w in r).most_common(SIMBOLI)}
    out = []
    for r in righe:
        cur = []
        for w in r:
            if w in top:
                cur.append(w)
            else:
                if len(cur) >= N + 1:
                    out.append(cur)
                cur = []
        if len(cur) >= N + 1:
            out.append(cur)
    return out


def codifica(seq, rnd, simboli=SIMBOLI):
    """Sequenza di caratteri-unita' -> righe di simboli 'cN', con simboli divisi in proporzione alla frequenza."""
    freq = Counter(seq)
    ordine = [c for c, _ in freq.most_common()]
    quota = {c: max(1, round(simboli * freq[c] / len(seq))) for c in ordine}
    while sum(quota.values()) > simboli:
        c = max(quota, key=lambda x: quota[x])
        quota[c] -= 1
    chiave, vera, k = {}, {}, 0
    for c in ordine:
        chiave[c] = ['c%d' % (k + i) for i in range(quota[c])]
        for s in chiave[c]:
            vera[s] = c
        k += quota[c]
    cif = [rnd.choice(chiave[c]) for c in seq]
    return [cif[i:i + PER_RIGA] for i in range(0, len(cif), PER_RIGA)], vera


def attacca(righe, modello, rnd, vera=None):
    g = ricottura.Grammi(righe, modello.n)
    esito, esiti = ricottura.risolvi(g, modello, rnd, ripartenze=RIPARTENZE)
    dec = ricottura.decifra(righe, esito.chiave, g, modello)
    r = OrderedDict([('punteggio', ricottura.punteggio_righe(dec, modello)), ('simboli', len(g.simboli))])
    if vera is not None:
        tot = sum(g.frequenza.values())
        r['chiave_giusta'] = sum(g.frequenza[i] for i, s in enumerate(g.simboli) if modello.lettere[esito.chiave[i]] == vera.get(s)) / tot
    r['esempio'] = dec[:4]
    return r


def una(args):
    nome, voy = args
    rnd = random.Random('e217-' + nome)
    u = unita_di(nome)
    car, top = alfabeto(u)
    k = int(len(u) * 0.8)
    modello = ricottura.ModelloLettere(''.join(car(x) for x in u[:k]) + ''.join(chr(0x4E00 + i) for i in range(UNITA)), n=N)
    L = sum(map(len, voy))
    pos, vera = codifica([car(x) for x in u[k:k + L]], rnd)
    altra = unita_di(LINGUE[nome][2])
    car2, _ = alfabeto(altra)
    neg, _ = codifica([car2(x) for x in altra[:L]], rnd)
    r = OrderedDict()
    r['positivo'] = attacca(pos, modello, rnd, vera)
    r['negativo'] = attacca(neg, modello, rnd)
    r['Voynich'] = attacca(voy, modello, rnd)
    p, n_, v = r['positivo']['punteggio'], r['negativo']['punteggio'], r['Voynich']['punteggio']
    r['posizione'] = (v - n_) / (p - n_) if p != n_ else None
    inv = {chr(0x4E00 + i): x for i, x in enumerate(top)}
    r['esempio_voynich_leggibile'] = [' '.join(inv.get(c, '·') for c in s) for s in r['Voynich']['esempio']]
    print('%-22s positivo %.3f (chiave giusta %.2f) | negativo %.3f | Voynich %.3f | posizione %s | %s' % (
        nome, p, r['positivo']['chiave_giusta'], n_, v, '%.2f' % r['posizione'] if r['posizione'] is not None else '-', r['esempio_voynich_leggibile'][:1]), flush=True)
    return nome, r


def main():
    voy = voynich()
    print('Voynich: simboli %d, lunghezza %d, righe %d' % (len({w for r in voy for w in r}), sum(map(len, voy)), len(voy)), flush=True)
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '3'))) as pool:
        for nome, r in pool.imap(una, [(n, voy) for n in LINGUE]):
            ris[nome] = r
            json.dump(ris, open(os.path.join(RISULTATI, 'e217_parole_sillabe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    valide = [n for n, r in ris.items() if r['positivo']['chiave_giusta'] >= 0.20]
    candidati = [n for n in valide if (ris[n]['posizione'] or 0) >= 0.5]
    esito = 'test non valido' if len(valide) < 3 else ('candidato, da esaminare' if candidati else 'nessuna lettura')
    json.dump({'lingue': ris, 'valide': valide, 'candidati': candidati, 'esito': esito}, open(os.path.join(RISULTATI, 'e217_parole_sillabe.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e217 — Una parola Voynich = una sillaba', '', 'Preregistrazione: `preregistrazioni/e217.md`.', '',
          '| lingua | positivo (chiave giusta) | negativo | Voynich | posizione | esempio Voynich decifrato |', '|---|---|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %.3f (%.2f) | %.3f | %.3f | %s | %s |' % (n, r['positivo']['punteggio'], r['positivo']['chiave_giusta'], r['negativo']['punteggio'], r['Voynich']['punteggio'],
                  '%.2f' % r['posizione'] if r['posizione'] is not None else '–', r['esempio_voynich_leggibile'][0][:60] if r['esempio_voynich_leggibile'] else ''))
    md += ['', 'Lingue valide: %s. Candidati: %s. Esito: **%s**.' % (', '.join(valide) or 'nessuna', ', '.join(candidati) or 'nessuno', esito)]
    open(os.path.join(RISULTATI, 'e217_parole_sillabe.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito, valide, candidati)


if __name__ == '__main__':
    main()
