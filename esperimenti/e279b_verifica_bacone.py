# -*- coding: utf-8 -*-
"""Esperimento 279b: verifica del canale dell'e279 con un nullo che rimescola parole intere (con i loro bit) dentro la
riga, il generatore con gli interruttori dell'e252 come negativo e i positivi di Bacone.

Preregistrazione: preregistrazioni/e279b.md. Scrive risultati/e279b_verifica_bacone.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e181_bacone as e181
import e206_segni_facoltativi as e206
import e236_due_fonti as e236
import e251_lessico_sezione as e251
import e252_interruttori_riga as e252
import e279_bacone_classi as e279

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI, L = 2791, 200, 5


def righe_bit(righe, classi):
    """righe di parole -> righe di blocchi di bit (uno per parola che ha almeno una classe; classi nell'ordine fisso)."""
    cl = e206.classi_di(Counter(w for r in righe for w in r))
    ordine = {c: i for i, c in enumerate(classi)}
    out = []
    for r in righe:
        blocchi = []
        for w in r:
            b = [v for n, v in sorted(((('%s %s' % c), v) for c, v in cl.get(w, {}).items() if ('%s %s' % c) in ordine), key=lambda x: ordine[x[0]])]
            if b:
                blocchi.append(b)
        out.append(blocchi)
    return out


def flusso(rb):
    return [v for r in rb for b in r for v in b]


def nullo_parole(rb, rnd):
    vero = e181.ioc(flusso(rb), L)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in rb:
            x = list(r)
            rnd.shuffle(x)
            mes.append(x)
        nulli.append(e181.ioc(flusso(mes), L))
    m, s = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('ioc', vero), ('nullo', m), ('z', (vero - m) / s if s else None)])


def nullo_bit(rb, rnd):
    occ = [('%d' % i, k, v) for k, r in enumerate(rb) for b in r for i, v in enumerate(b)]
    return e181.prova(occ, [v for _, _, v in occ], L, rnd)


def sostituisci(rb, msg, p, rnd):
    it = iter(msg)
    return [[[next(it) if rnd.random() < p else v for v in b] for b in r] for r in rb]


def main():
    rnd = random.Random(SEME)
    classi = json.load(open(os.path.join(RISULTATI, 'e206b_facoltativi_strati.json'), encoding='utf-8'))['scelte_di_riga']
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]
    rb_v = righe_bit(voy, classi)
    k = e251._prepara()
    inter = e251.interruttori_voynich(classi)
    rr = e236.dopo(e252.genera_ii(k['c2'], dict(e251.CONF, gamma=0.0), 7, inter), k['freq'], 107)
    rb_g = righe_bit([[w for w in ps if trascrizione.pulita(w)] for _, _, ps in rr], classi)
    msg = e279.bacone(len(flusso(rb_v)))
    testi = OrderedDict([('Voynich', rb_v), ('generatore e241 + interruttori (seme 7)', rb_g),
                         ('positivo: Bacone al 70%', sostituisci(rb_v, msg, 0.7, rnd)), ('positivo: Bacone al 30%', sostituisci(rb_v, msg, 0.3, rnd))])
    ris = OrderedDict()
    for n, rb in testi.items():
        ris[n] = OrderedDict([('bit', len(flusso(rb))), ('nullo a parole intere', nullo_parole(rb, rnd)), ('nullo bit per bit (come e279, per posizione nella parola)', nullo_bit(rb, rnd))])
        print('%-42s parole intere z %.1f | bit per bit z %.1f' % (n, ris[n]['nullo a parole intere']['z'] or 0, ris[n]['nullo bit per bit (come e279, per posizione nella parola)']['z'] or 0), flush=True)
    z = lambda n: ris[n]['nullo a parole intere']['z'] or 0
    valido = z('positivo: Bacone al 70%') > 4
    regge = z('Voynich') > 4 and z('Voynich') - z('generatore e241 + interruttori (seme 7)') >= 3
    esito = 'non valido' if not valido else ('il canale regge (nessuna lettura)' if regge else 'artefatto delle parole ripetute')
    json.dump(OrderedDict([('risultati', ris), ('valido', valido), ('esito', esito)]), open(os.path.join(RISULTATI, 'e279b_verifica_bacone.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    md = ['# e279b — Verifica del canale "alla Bacone" dell\'e279', '',
          'Indice di coincidenza dei gruppi di 5 bit, z contro %d rimescolamenti. Preregistrazione: `preregistrazioni/e279b.md`.' % RIMESCOLAMENTI, '',
          '| testo | bit | indice | z, nullo a parole intere | z, nullo bit per bit (come e279) |', '|---|---|---|---|---|']
    for n, r in ris.items():
        md.append('| %s | %d | %.4f | %.1f | %.1f |' % (n, r['bit'], r['nullo a parole intere']['ioc'], r['nullo a parole intere']['z'] or 0, r['nullo bit per bit (come e279, per posizione nella parola)']['z'] or 0))
    md += ['', 'Valido: **%s**. Esito: **%s**.' % ('sì' if valido else 'no', esito)]
    open(os.path.join(RISULTATI, 'e279b_verifica_bacone.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esito)


if __name__ == '__main__':
    main()
