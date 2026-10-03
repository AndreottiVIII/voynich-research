# -*- coding: utf-8 -*-
"""Esperimento 362: (a) le forme nuove sono ben formate secondo una catena di Markov di ordine 2 sui segni (stimata sulle
parole non uniche)? (b) le forme nuove arrivano a gruppi nella riga o nel paragrafo?

Preregistrazione: preregistrazioni/e362.md. Scrive risultati/e362_forme_nuove.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e350_sessioni as e350

RISULTATI = os.path.join(QUI, '..', 'risultati')
D = misure.divisore(misure.GLIFI_EVA)
ALFA = 0.1


def transizioni(u):
    s = ('^', '^') + tuple(u) + ('$',)
    return [((s[i - 2], s[i - 1]), s[i]) for i in range(2, len(s))]


def main():
    rnd = random.Random(362)
    pagine = OrderedDict()
    for r in trascrizione.testo_corrente(trascrizione.leggi('ZL')):
        if r.parole:
            ws = [w for w in r.parole if trascrizione.pulita(w)]
            if ws:
                pars = pagine.setdefault(r.pagina, [])
                if r.inizio_par or not pars:
                    pars.append([])
                pars[-1].append(ws)
    tok = [w for pars in pagine.values() for par in pars for r in par for w in r]
    freq = Counter(tok)
    sim = e350.simili_globali(set(freq))
    U = {w: tuple(D(w)) for w in freq}
    cat = {}
    for w, n in freq.items():
        if n == 1:
            cat[w] = 'errore' if any(freq[v] >= 20 for v in sim[w] if v != w) else 'nuova'
    # (a) modello dei segni sulle parole non uniche
    ctx, tr = Counter(), Counter()
    for w in tok:
        if freq[w] >= 2:
            for c, g in transizioni(U[w]):
                ctx[c] += 1
                tr[(c, g)] += 1
    alfabeto = {g for w in freq for g in U[w]} | {'$'}
    V = len(alfabeto)

    def ll(w, togli=0):
        """Log-verosimiglianza media per segno; togli = occorrenze della parola da togliere dal modello."""
        t = transizioni(U[w])
        ct, cc = Counter(t), Counter(c for c, _ in t)
        tot = 0.0
        for c, g in t:
            n_cg = tr[(c, g)] - togli * ct[(c, g)]
            n_c = ctx[c] - togli * cc[c]
            tot += math.log((n_cg + ALFA) / (n_c + ALFA * V))
        return tot / len(t)
    nuove = [w for w, c in cat.items() if c == 'nuova']
    errori = [w for w, c in cat.items() if c == 'errore']
    comuni = defaultdict(list)
    for w, n in freq.items():
        if n >= 5:
            comuni[len(U[w])].append(w)
    ll_com = {w: ll(w, togli=freq[w]) for L in comuni for w in comuni[L]}
    a = OrderedDict()
    for nome, gruppo in (('forme nuove', nuove), ('errori', errori)):
        v = statistics.mean(ll(w) for w in gruppo)
        lens = [len(U[w]) for w in gruppo]
        rif = []
        for _ in range(1000):
            camp = []
            for L in lens:
                pool = comuni.get(L) or comuni.get(L - 1) or comuni.get(L + 1) or list(ll_com)
                camp.append(ll_com[rnd.choice(pool)])
            rif.append(statistics.mean(camp))
        m, sd = statistics.mean(rif), statistics.pstdev(rif)
        a[nome] = OrderedDict([('parole', len(gruppo)), ('logverosimiglianza_per_segno', v), ('comuni_stessa_lunghezza', m), ('differenza', v - m), ('z', (v - m) / sd if sd else 0.0)])
    za = a['forme nuove']['z']
    esito_a = 'forme nuove fuori dalle regole dei segni' if za < -3 else ('ben formate' if abs(za) < 2 else 'incerto')
    tn, tc = Counter(), Counter()
    for w in nuove:
        tn.update(transizioni(U[w]))
    for L in comuni:
        for w in comuni[L]:
            tc.update(transizioni(U[w]))
    nn, nc = sum(tn.values()), sum(tc.values())
    tipiche = sorted(((tn[k] / nn) / ((tc[k] + 0.5) / nc), k) for k in tn if tn[k] >= 15)[::-1][:10]
    # (b) a gruppi?
    def coppie(livello, flag):
        if livello == 'riga':
            return sum(math.comb(sum(f), 2) for par in flag for f in par)
        return sum(math.comb(sum(sum(f) for f in par), 2) for par in flag)
    flag_pag = [[[[cat.get(w) == 'nuova' for w in r] for r in par] for par in pars] for pars in pagine.values()]
    flag_par = [par for pars in flag_pag for par in pars]
    v_riga = coppie('riga', flag_par)
    nul_r = []
    for _ in range(1000):
        out = []
        for par in flag_par:
            tutte = [x for r in par for x in r]
            rnd.shuffle(tutte)
            i, nuovo = 0, []
            for r in par:
                nuovo.append(tutte[i:i + len(r)])
                i += len(r)
            out.append(nuovo)
        nul_r.append(coppie('riga', out))
    v_par = sum(coppie('paragrafo', pars) for pars in flag_pag)
    nul_p = []
    for _ in range(1000):
        tot = 0
        for pars in flag_pag:
            tutte = [x for par in pars for r in par for x in r]
            rnd.shuffle(tutte)
            i = 0
            for par in pars:
                n = sum(len(r) for r in par)
                tot += math.comb(sum(tutte[i:i + n]), 2)
                i += n
        nul_p.append(tot)
    zr = (v_riga - statistics.mean(nul_r)) / statistics.pstdev(nul_r)
    zp = (v_par - statistics.mean(nul_p)) / statistics.pstdev(nul_p)
    esito_b = 'momenti inventivi' if (zr > 3 or zp > 3) else ('sparse' if abs(zr) < 2 and abs(zp) < 2 else 'incerto')
    out = OrderedDict([('a', a), ('esito_a', esito_a), ('passaggi_tipici_delle_forme_nuove', [('%s%s→%s' % (k[0][0], k[0][1], k[1]), round(r, 2)) for r, k in tipiche]),
                       ('b', OrderedDict([('coppie_nella_riga', v_riga), ('nullo_riga', statistics.mean(nul_r)), ('z_riga', zr),
                                          ('coppie_nel_paragrafo', v_par), ('nullo_paragrafo', statistics.mean(nul_p)), ('z_paragrafo', zp)])), ('esito_b', esito_b)])
    print(json.dumps(out, ensure_ascii=False, default=float)[:1500], flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e362_forme_nuove.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    md = ['# e362 — Come sono fatte le forme nuove, e quando arrivano', '', 'Preregistrazione: `preregistrazioni/e362.md`.', '', '## (a)', '',
          '| parole | numero | log-verosimiglianza per segno | parole comuni a pari lunghezza | differenza | z |', '|---|---|---|---|---|---|']
    for k, v in a.items():
        md.append('| %s | %d | %.3f | %.3f | %+.3f | %.1f |' % (k, v['parole'], v['logverosimiglianza_per_segno'], v['comuni_stessa_lunghezza'], v['differenza'], v['z']))
    md += ['', 'Esito (a): **%s**. Passaggi più tipici delle forme nuove (rapporto sulle comuni): %s.' % (esito_a, ', '.join('%s %.1f' % x for x in out['passaggi_tipici_delle_forme_nuove'])),
           '', '## (b)', '', '- Coppie di forme nuove nella stessa riga: %d contro %.1f del nullo, z %.1f.' % (v_riga, statistics.mean(nul_r), zr),
           '- Coppie nello stesso paragrafo: %d contro %.1f, z %.1f.' % (v_par, statistics.mean(nul_p), zp), '', 'Esito (b): **%s**.' % esito_b]
    open(os.path.join(RISULTATI, 'e362_forme_nuove.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
