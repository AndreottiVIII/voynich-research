# -*- coding: utf-8 -*-
"""Esperimento 193: testo circolare, radiale, rosette, anello di f57v ed etichette contro campioni di paragrafi della
stessa dimensione; ordine della sequenza di f57v contro frequenza dei segni.

Preregistrazione: preregistrazioni/e193.md. Scrive risultati/e193_parti_a_se.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e173_dimensione_scrittura as e173

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, CAMPIONI = 193, 1000
D = misure.divisore(misure.GLIFI_EVA)
NOMI = ('tipi/parole', 'lunghezza media', 'quota di un segno', 'quota con o-', 'nel vocabolario dei paragrafi', 'ripetizione per 100 coppie')


def misure_blocco(righe, voc):
    ps = [w for r in righe for w in r if trascrizione.pulita(w)]
    if len(ps) < 2:
        return None
    u = [D(w) for w in ps]
    coppie = [(a, b) for r in righe for a, b in zip(r, r[1:]) if trascrizione.pulita(a) and trascrizione.pulita(b)]
    return [len(set(ps)) / len(ps), statistics.mean(len(x) for x in u), sum(len(x) == 1 for x in u) / len(u),
            sum(x[0] == 'o' for x in u) / len(u), sum(voc(w) for w in ps) / len(ps),
            100 * sum(a == b for a, b in coppie) / len(coppie) if coppie else 0.0]


def main():
    rnd = random.Random(SEME)
    par = [r for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')) if r.parole and r.pagina != 'fRos']
    zl = [r for r in trascrizione.leggi('ZL') if r.parole]   # tutti i loci (testo_corrente ha solo i paragrafi)
    blocchi = OrderedDict([
        ('circolare (Cc, Ca)', [list(r.parole) for r in zl if r.tipo in ('Cc', 'Ca') and r.pagina not in ('fRos', 'f57v')]),
        ('radiale (Ri, Ro)', [list(r.parole) for r in zl if r.tipo in ('Ri', 'Ro') and r.pagina != 'fRos']),
        ('rosette (fRos)', [list(r.parole) for r in zl if r.pagina == 'fRos']),
        ('anello di f57v', [list(r.parole) for r in zl if r.pagina == 'f57v' and r.tipo and r.tipo[0] == 'C']),
        ('etichette (L)', [list(r.parole) for r in zl if r.tipo and r.tipo[0] == 'L' and r.pagina != 'fRos'])])
    ris = OrderedDict()
    for nome, righe in blocchi.items():
        n = sum(1 for r in righe for w in r if trascrizione.pulita(w))
        tutto = Counter(w for r in par for w in r.parole)
        vero = misure_blocco(righe, lambda w: tutto[w] > 0)
        camp = []
        for _ in range(CAMPIONI):
            i = rnd.randrange(len(par))
            sel, k = [], 0
            while k < n and i < len(par):
                sel.append(par[i])
                k += sum(1 for w in par[i].parole if trascrizione.pulita(w))
                i += 1
            dentro = Counter(w for r in sel for w in r.parole)
            camp.append(misure_blocco([list(r.parole) for r in sel], lambda w, d=dentro: tutto[w] - d[w] > 0))
        zz = []
        for j in range(len(NOMI)):
            col = [c[j] for c in camp if c]
            m, s = statistics.mean(col), statistics.pstdev(col)
            zz.append((vero[j] - m) / s if s else None)
        diverso = sum(1 for z in zz if z is not None and abs(z) > 3) >= 2
        ris[nome] = OrderedDict([('parole', n), ('valori', OrderedDict(zip(NOMI, vero))), ('z', OrderedDict(zip(NOMI, zz))), ('diverso', diverso)])
        print('%-22s n %d | %s | diverso %s' % (nome, n, ' '.join('%s %.2f(z %.1f)' % (k[:12], v, z or 0) for k, v, z in zip(NOMI, vero, zz)), diverso), flush=True)
    # anello di f57v: segni singoli in ordine
    # la riga dell'anello con piu' segni singoli; un periodo = fino al ritorno del primo segno
    riga = max(blocchi['anello di f57v'], key=lambda r: sum(1 for w in r if trascrizione.pulita(w) and len(D(w)) == 1))
    singoli = [w for w in riga if trascrizione.pulita(w) and len(D(w)) == 1]
    seq = singoli[:1]
    for g in singoli[1:]:
        if g == seq[0]:
            break
        seq.append(g)
    freq = Counter(u for r in par for w in r.parole if trascrizione.pulita(w) for u in D(w))
    rango = {g: i for i, (g, _) in enumerate(freq.most_common())}
    seq_r = [g for g in seq if g in rango]
    if len(seq_r) >= 5:
        vero_s = e173.spearman(list(range(len(seq_r))), [rango[g] for g in seq_r])
        nulli = []
        for _ in range(10000):
            x = seq_r[:]
            rnd.shuffle(x)
            nulli.append(e173.spearman(list(range(len(x))), [rango[g] for g in x]))
        p = (1 + sum(abs(n) >= abs(vero_s) for n in nulli)) / 10001
    else:
        vero_s, p = None, None
    ris['anello_f57v_sequenza'] = OrderedDict([('sequenza', seq), ('ranghi', [rango.get(g) for g in seq]), ('spearman', vero_s), ('p_due_code', p)])
    print('f57v sequenza %s | ranghi %s | Spearman %s p %s' % (seq, [rango.get(g) for g in seq], vero_s, p))
    with open(os.path.join(RISULTATI, 'e193_parti_a_se.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e193 — Le parti "a sé" del testo', '', 'z contro %d campioni di paragrafi della stessa dimensione. Preregistrazione: `preregistrazioni/e193.md`.' % CAMPIONI, '',
           '| blocco | parole | ' + ' | '.join(NOMI) + ' | diverso |', '|---|---|' + '---|' * len(NOMI) + '---|']
    for nome in blocchi:
        r = ris[nome]
        out.append('| %s | %d | %s | %s |' % (nome, r['parole'], ' | '.join('%.2f (z %.1f)' % (r['valori'][k], r['z'][k] or 0) for k in NOMI), 'sì' if r['diverso'] else 'no'))
    a = ris['anello_f57v_sequenza']
    out += ['', 'Anello di f57v: sequenza %s, ranghi di frequenza %s, Spearman %s (p %s).' % (' '.join(a['sequenza']), a['ranghi'],
            '%.2f' % a['spearman'] if a['spearman'] is not None else '–', '%.3f' % a['p_due_code'] if a['p_due_code'] is not None else '–')]
    with open(os.path.join(RISULTATI, 'e193_parti_a_se.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
