# -*- coding: utf-8 -*-
"""Esperimento 158: riconoscimento della lingua alla Hauer e Kondrak (profilo di frequenza, schemi di ripetizione,
versione per anagrammi) con controlli su lingue cifrate e su testi senza messaggio.

Preregistrazione: preregistrazioni/e158.md. Scrive risultati/e158_hauer_kondrak.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, N_PAROLE, N_PROFILO, N_VALIDITA = 158, 35000, 25, 20
D = misure.divisore(misure.GLIFI_EVA)


def lettere(w):
    return [c for c in w.lower() if c.isalpha()]


def profilo(parole_unita):
    c = Counter(u for w in parole_unita for u in w)
    n = sum(c.values())
    v = sorted((x / n for x in c.values()), reverse=True)[:N_PROFILO]
    return v + [0.0] * (N_PROFILO - len(v))


def schema(w):
    idx, out = {}, []
    for u in w:
        idx.setdefault(u, len(idx))
        out.append(str(idx[u]))
    return ''.join(out)


def schema_anagramma(w):
    return ','.join(str(x) for x in sorted(Counter(w).values(), reverse=True))


def distr(parole_unita, f):
    c = Counter(f(w) for w in parole_unita if w)
    n = sum(c.values())
    return {k: v / n for k, v in c.items()}


def jsd(p, q):
    out = 0.0
    for k in set(p) | set(q):
        a, b = p.get(k, 0.0), q.get(k, 0.0)
        m = (a + b) / 2
        if a:
            out += 0.5 * a * math.log2(a / m)
        if b:
            out += 0.5 * b * math.log2(b / m)
    return out


def firme(parole_unita):
    return {'F': profilo(parole_unita), 'P': distr(parole_unita, schema), 'A': distr(parole_unita, schema_anagramma)}


def distanza(m, a, b):
    return math.dist(a, b) if m == 'F' else jsd(a, b)


def classifica(f, riferimenti, metodo):
    d = {lang: distanza(metodo, f[metodo], r[metodo]) for lang, r in riferimenti.items()}
    ordine = sorted(d, key=d.get)
    vals = list(d.values())
    sic = (statistics.mean(vals) - d[ordine[0]]) / statistics.pstdev(vals) if statistics.pstdev(vals) else None
    return ordine, sic, d


def cifra(parole_unita, rnd, anagramma=False):
    alfabeto = sorted({u for w in parole_unita for u in w})
    perm = alfabeto[:]
    rnd.shuffle(perm)
    mappa = dict(zip(alfabeto, ['s%d' % i for i in range(len(perm))]))
    out = []
    for w in parole_unita:
        u = [mappa[x] for x in w]
        if anagramma:
            u = sorted(u)
        out.append(u)
    return out


def main():
    rnd = random.Random(SEME)
    nomi = sorted(f[:-4] for f in os.listdir(lingue.CACHE) if f.endswith('.txt'))
    testi_l = {}
    for n in nomi:
        try:
            ws = [lettere(w) for w in lingue.parole(n)[:N_PAROLE]]
            ws = [w for w in ws if w]
            if len(ws) >= 5000:
                testi_l[n] = ws
        except Exception:
            pass
    riferimenti = {n: firme(ws) for n, ws in testi_l.items()}
    print('lingue di riferimento: %d' % len(riferimenti), flush=True)
    ris = OrderedDict([('lingue', len(riferimenti))])
    # validita'
    scelte = rnd.sample(sorted(riferimenti), N_VALIDITA)
    val = OrderedDict()
    for metodo in ('F', 'P', 'A'):
        giuste = 0
        for n in scelte:
            cif = cifra(testi_l[n], rnd, anagramma=(metodo == 'A'))
            ordine, _, _ = classifica(firme(cif), riferimenti, metodo)
            giuste += ordine[0] == n
        val[metodo] = giuste / N_VALIDITA
        print('validita %s: lingua giusta prima in %.0f%%' % (metodo, 100 * val[metodo]), flush=True)
    ris['validita'] = val
    # testi
    voy = [D(w) for w in trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL'))) if trascrizione.pulita(w)][:N_PAROLE]
    ts = [D(w) for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')) for w in ps][:N_PAROLE]
    import e131_procedimento_riga as e131, e145_abitudini as e145, e152_righe_in_ordine as e152
    vv = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    g152 = [D(w) for _, _, ps in e152.genera(e145.pagine(), e131.inizi(), e145.quote(), e152.lift(), 2, 0.5, 1.0, generatori.Modifiche(vv, D), 1) for w in ps if trascrizione.pulita(w)][:N_PAROLE]
    import e128_scrittura_inventata as e128
    gib = [lettere(w) for _, _, ps in e128.inventati() for w in ps]
    testi = OrderedDict([('Voynich ZL', voy), ('Timm e Schinner, seme 19', ts), ('generatore e152', g152), ('testi inventati (Gaskell e Bowern)', gib)])
    for nome, t in testi.items():
        f = firme(t)
        r = OrderedDict()
        for metodo in ('F', 'P', 'A'):
            ordine, sic, d = classifica(f, riferimenti, metodo)
            r[metodo] = OrderedDict([('prime_5', ordine[:5]), ('sicurezza', sic), ('posizione_ebraico', ordine.index('Hebrew') + 1 if 'Hebrew' in ordine else None)])
        ris[nome] = r
        print('%-36s %s' % (nome, ' | '.join('%s: %s (sic %.2f, ebraico %s)' % (m, ', '.join(x['prime_5'][:3]), x['sicurezza'] or 0, x['posizione_ebraico']) for m, x in r.items())), flush=True)
    validi = [m for m in ('F', 'P') if val[m] >= 0.7]
    informativa = OrderedDict()
    for m in validi:
        sv = ris['Voynich ZL'][m]['sicurezza'] or 0
        informativa[m] = all(sv > (ris[n][m]['sicurezza'] or 0) for n in ('Timm e Schinner, seme 19', 'generatore e152', 'testi inventati (Gaskell e Bowern)'))
    ris['metodi_validi'], ris['indicazione_informativa'] = validi, informativa
    print('metodi validi %s | indicazione sul Voynich informativa %s' % (validi, dict(informativa)))
    with open(os.path.join(RISULTATI, 'e158_hauer_kondrak.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e158 — Riconoscimento della lingua alla Hauer e Kondrak, con controlli', '', 'Ricostruzione dei metodi F (profilo di frequenza), P (schemi di ripetizione), A (per anagrammi) '
           'su %d lingue. Preregistrazione: `preregistrazioni/e158.md`.' % len(riferimenti), '',
           'Validità (lingua giusta prima, %d lingue cifrate): F %.0f%%, P %.0f%%, A %.0f%%.' % (N_VALIDITA, 100 * val['F'], 100 * val['P'], 100 * val['A']), '',
           '| testo | metodo | prime 5 lingue | sicurezza | posizione dell\'ebraico |', '|---|---|---|---|---|']
    for nome in testi:
        for m, x in ris[nome].items():
            out.append('| %s | %s | %s | %.2f | %s |' % (nome, m, ', '.join(x['prime_5']), x['sicurezza'] or 0, x['posizione_ebraico']))
    out += ['', 'Metodi validi: **%s**. Indicazione sul Voynich informativa: **%s**.' % (', '.join(validi) or 'nessuno',
                                                                                     ', '.join('%s %s' % (m, 'sì' if v else 'no') for m, v in informativa.items()) or '–')]
    with open(os.path.join(RISULTATI, 'e158_hauer_kondrak.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
