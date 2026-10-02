# -*- coding: utf-8 -*-
"""Esperimento 186: ricerca di cifrari a nulli e acrostici (12 regole di estrazione), legame fra simboli estratti
consecutivi contro rimescolamento dentro la pagina; confronto con il generatore e180 e controlli con latino nascosto.

Preregistrazione: preregistrazioni/e186.md. Scrive risultati/e186_nulli_acrostici.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e162_messaggio_nei_temi as e162

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RIMESCOLAMENTI = 186, 200
D = misure.divisore(misure.GLIFI_EVA)
REGOLE = ['I1', 'I2', 'I3', 'I4', 'F1', 'F2', 'F3', 'F4', 'R1', 'R2', 'R3', 'P1']


def estrai(righe, regola):
    """righe: (pagina, inizio paragrafo, parole). -> {pagina: [simboli]}"""
    out = defaultdict(list)
    conta = defaultdict(int)
    for pag, ini, ps in righe:
        ps = [w for w in ps if trascrizione.pulita(w)]
        if not ps:
            continue
        if regola[0] in 'IF':
            passo = int(regola[1])
            for w in ps:
                if conta[pag] % passo == 0:
                    u = D(w)
                    out[pag].append(u[0] if regola[0] == 'I' else u[-1])
                conta[pag] += 1
        elif regola == 'R1':
            out[pag].append(D(ps[0])[0])
        elif regola == 'R2':
            out[pag].append(D(ps[-1])[-1])
        elif regola == 'R3' and len(ps) >= 2:
            out[pag].append(D(ps[1])[0])
        elif regola == 'P1' and ini:
            out[pag].append(D(ps[0])[0])
    return out


def prova(seq, rnd):
    def mi(ss):
        return misure.informazione_mutua([(a, b) for s in ss.values() for a, b in zip(s, s[1:])])
    if sum(len(s) for s in seq.values()) < 50:
        return OrderedDict([('n', sum(len(s) for s in seq.values())), ('eccesso', None), ('z', None)])
    vero = mi(seq)
    nulli = []
    for _ in range(RIMESCOLAMENTI):
        mes = {}
        for p, s in seq.items():
            s = s[:]
            rnd.shuffle(s)
            mes[p] = s
        nulli.append(mi(mes))
    m, sd = statistics.mean(nulli), statistics.pstdev(nulli)
    return OrderedDict([('n', sum(len(s) for s in seq.values())), ('eccesso', vero - m), ('z', (vero - m) / sd if sd else None)])


def righe_voynich():
    return [(r.pagina, bool(r.inizio_par), list(r.parole)) for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole]


def generatore(voy):
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K = 0.3, 1.0, 3
    mod = generatori.Modifiche(voy, D)
    return [(p, ini, ps) for p, ini, ps in e162.genera(P, starts, q, L, mod, 1, None)]


def nascondi(righe, solo_inizio_riga):
    lat = [c for w in lingue.parole('Latin')[:30000] for c in w if c.isalpha()]
    voc = Counter(D(w)[0] for _, _, ps in righe for w in ps if trascrizione.pulita(w))
    glifi = [g for g, _ in voc.most_common()]
    lettere = [c for c, _ in Counter(lat).most_common()]
    mappa = {c: glifi[i % len(glifi)] for i, c in enumerate(lettere)}
    it = iter(lat)
    out = []
    for pag, ini, ps in righe:
        nuove = []
        for i, w in enumerate(ps):
            if trascrizione.pulita(w) and (not solo_inizio_riga or i == 0):
                u = D(w)
                w = mappa[next(it)] + ''.join(u[1:])
            nuove.append(w)
        out.append((pag, ini, nuove))
    return out


def main():
    rnd = random.Random(SEME)
    rv = righe_voynich()
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    rg = generatore(voy)
    ris = OrderedDict()
    for nome, rr in (('Voynich', rv), ('generatore e180 (senza messaggio)', rg)):
        ris[nome] = OrderedDict((r, prova(estrai(rr, r), rnd)) for r in REGOLE)
        print('%-36s ' % nome + ' '.join('%s %.1f' % (r, x['z'] or 0) for r, x in ris[nome].items()), flush=True)
    ris['controllo I1 (latino nelle iniziali)'] = prova(estrai(nascondi(rv, False), 'I1'), rnd)
    ris['controllo R1 (latino nelle iniziali di riga)'] = prova(estrai(nascondi(rv, True), 'R1'), rnd)
    print('controlli: I1 z %.1f, R1 z %.1f' % (ris['controllo I1 (latino nelle iniziali)']['z'] or 0, ris['controllo R1 (latino nelle iniziali di riga)']['z'] or 0), flush=True)
    valido = (ris['controllo I1 (latino nelle iniziali)']['z'] or 0) > 4 and (ris['controllo R1 (latino nelle iniziali di riga)']['z'] or 0) > 4
    candidate = [r for r in REGOLE if (ris['Voynich'][r]['z'] or 0) > 4 and (ris['Voynich'][r]['z'] or 0) - (ris['generatore e180 (senza messaggio)'][r]['z'] or 0) >= 3]
    ris['valido'], ris['candidate'] = valido, candidate
    print('valido %s | candidate %s' % (valido, candidate))
    with open(os.path.join(RISULTATI, 'e186_nulli_acrostici.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e186 — Cifrari a nulli e acrostici: ricerca sistematica', '',
           'Eccesso d\'informazione mutua fra simboli estratti consecutivi (z contro rimescolamento dentro la pagina). Preregistrazione: `preregistrazioni/e186.md`.', '',
           '| regola | Voynich (n; z) | generatore senza messaggio (z) |', '|---|---|---|']
    for r in REGOLE:
        v, g = ris['Voynich'][r], ris['generatore e180 (senza messaggio)'][r]
        out.append('| %s | %d; %.1f | %.1f |' % (r, v['n'], v['z'] or 0, g['z'] or 0))
    out += ['', 'Controlli: I1 z %.1f, R1 z %.1f. Validità: **%s**. Regole candidate: **%s**.' % (
        ris['controllo I1 (latino nelle iniziali)']['z'] or 0, ris['controllo R1 (latino nelle iniziali di riga)']['z'] or 0, 'sì' if valido else 'no', ', '.join(candidate) or 'nessuna')]
    with open(os.path.join(RISULTATI, 'e186_nulli_acrostici.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
