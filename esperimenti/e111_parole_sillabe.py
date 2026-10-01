# -*- coding: utf-8 -*-
"""Esperimento 111: classi di varianti (normalizzazioni N0-N4) e confronto dei flussi di classi del Voynich con flussi di
sillabe veri; prova del metro.

Preregistrazione: preregistrazioni/e111.md. Scrive risultati/e111_parole_sillabe.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 30000
D = misure.divisore(misure.GLIFI_EVA)
LEGGERE = {'sh': 'ch', 'p': 't', 'f': 'k', 'cph': 'cth', 'cfh': 'ckh'}
FORTI = {'k': 't', 'ckh': 'cth', 'r': 'd', 's': 'd'}
LIVELLI = ('N0', 'N1', 'N2', 'N3', 'N4')
MISURE = ('classi', 'quota_classi_uniche', 'h1', 'h2', 'zipf', 'ripetizione')


def normalizza(w, livello):
    u = list(D(w))
    if livello >= 1:
        u = [LEGGERE.get(g, g) for g in u]
    if livello >= 2:
        v = []
        for g in u:
            if g in ('e', 'i') and v and v[-1] == g:
                continue
            v.append(g)
        u = v
    if livello >= 3 and len(u) > 1 and u[0] == 'q':
        u = u[1:]
    if livello >= 4:
        u = [FORTI.get(g, g) for g in u]
    return ''.join(u)


def tronca(righe, n=N):
    out, tot = [], 0
    for r in righe:
        if tot >= n:
            break
        r = r[:n - tot]
        if r:
            out.append(r)
            tot += len(r)
    return out


def statistiche(righe):
    unita = [u for r in righe for u in r]
    c = Counter(unita)
    n = len(unita)
    h1 = -sum(k / n * math.log2(k / n) for k in c.values())
    coppie = [(a, b) for r in righe for a, b in zip(r, r[1:])]
    cp = Counter(coppie)
    ca = Counter(a for a, _ in coppie)
    h2 = -sum(k / len(coppie) * math.log2(k / ca[a]) for (a, _), k in cp.items())
    cc = sorted(c.values(), reverse=True)[:1000]
    xs = [math.log(i + 1) for i in range(len(cc))]
    ys = [math.log(v) for v in cc]
    mx, my = statistics.mean(xs), statistics.mean(ys)
    zipf = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    lun = [len(r) for r in righe]
    return OrderedDict([('unita', n), ('classi', len(c)), ('quota_classi_uniche', sum(v == 1 for v in c.values()) / len(c)),
                        ('h1', h1), ('h2', h2), ('zipf', zipf), ('ripetizione', sum(a == b for a, b in coppie) / len(coppie)),
                        ('unita_per_riga', statistics.mean(lun)), ('cv_unita_per_riga', statistics.pstdev(lun) / statistics.mean(lun))])


def sillabe_righe(righe_parole):
    return [[s for w in ps for s in generatori.sillabe(w)] for ps in righe_parole]


def purezza(classi, vere):
    """H(vera | classe), H(classe | vera) in bit, su sequenze allineate."""
    coppie = list(zip(classi, vere))
    def hcond(xy):
        cx = Counter(x for x, _ in xy)
        cxy = Counter(xy)
        n = len(xy)
        return -sum(k / n * math.log2(k / cx[x]) for (x, _), k in cxy.items())
    return hcond(coppie), hcond([(b, a) for a, b in coppie])


def metro():
    out = OrderedDict()
    righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'), sezione='S')
    par, cur = [], []
    for r in righe:
        if r.inizio_par and cur:
            par.append(cur)
            cur = []
        if r.parole:
            cur.append(r.parole)
    if cur:
        par.append(cur)
    sel = [ps for p in par for ps in p[:-1] if len(ps) >= 3]
    nparole = [len(ps) for ps in sel]
    nsegni = [sum(len(D(w)) for w in ps) + len(ps) - 1 for ps in sel]
    cv = lambda x: statistics.pstdev(x) / statistics.mean(x)
    out['Voynich S'] = {'righe': len(sel), 'cv_unita': cv(nparole), 'cv_segni': cv(nsegni), 'unita_media': statistics.mean(nparole)}
    import e98_versi_latini as e98
    import e99_macer as e99
    import e73_bordo_interno as e73
    for nome, versi in (('Ovidio (sillabe)', e98.versi(e98.TESTI['Ovidio, Metamorfosi'])), ('Macer (sillabe)', [ps for c in e99.capitoli() for ps in c])):
        su = [len(r) for r in sillabe_righe(versi)]
        sl = [sum(len(w) for w in ps) + len(ps) - 1 for ps in versi]
        out[nome] = {'righe': len(versi), 'cv_unita': cv(su), 'cv_segni': cv(sl), 'unita_media': statistics.mean(su)}
    pl = [ps for _, ps in e73.testi()['Plinio, a capo'][0]]
    out['Plinio a capo (parole)'] = {'righe': len(pl), 'cv_unita': cv([len(p) for p in pl]),
                                     'cv_segni': cv([sum(len(w) for w in p) + len(p) - 1 for p in pl]), 'unita_media': statistics.mean(len(p) for p in pl)}
    return out


def main():
    import e98_versi_latini as e98
    import e99_macer as e99
    voy_righe = [[w for w in r.parole if trascrizione.pulita(w)] for r in trascrizione.testo_corrente(trascrizione.leggi('ZL'))]
    voy_righe = [r for r in voy_righe if r]
    ris = OrderedDict()
    # sillabe vere
    macer = [ps for c in e99.capitoli() for ps in c]
    vere = OrderedDict()
    vere['Macer (versi)'] = sillabe_righe(macer)
    vere['Ovidio (versi)'] = sillabe_righe(e98.versi(e98.TESTI['Ovidio, Metamorfosi']))
    for chiave, nome in (('Latin', 'Bibbia latina'), ('Italian', 'Bibbia italiana')):
        ps = lingue.parole(chiave)[:40000]
        vere[nome] = sillabe_righe([ps[i:i + 9] for i in range(0, len(ps), 9)])
    for nome, rr in vere.items():
        ris[nome] = statistiche(tronca(rr))
    # controllo positivo: Macer cifrato come e104 (mu 0,6, seme 1)
    import e104_sillabe_varianti as e104
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    mod = generatori.Modifiche(voy, D)
    caps = e99.capitoli()
    sill = [[[s for w in ps for s in generatori.sillabe(w)] for ps in cap] for cap in caps]
    cifrato = e104.costruisci(sill, voy, mod, 0.6, 1)
    cif_righe = [r for p in cifrato for r in p]
    vere_seq = [s for p in sill for r in p for s in r]
    ts = [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))]
    intervalli = {m: (min(ris[n][m] for n in vere), max(ris[n][m] for n in vere)) for m in MISURE}
    regge = OrderedDict()
    for k, L in enumerate(LIVELLI):
        v = statistiche(tronca([[normalizza(w, k) for w in r] for r in voy_righe]))
        ris['Voynich ' + L] = v
        c = statistiche(tronca([[normalizza(w, k) for w in r] for r in cif_righe]))
        classi_c = [normalizza(w, k) for r in cif_righe for w in r]
        c['H(sillaba|classe)'], c['H(classe|sillaba)'] = purezza(classi_c, vere_seq)
        ris['controllo: Macer cifrato ' + L] = c
        ris['Timm e Schinner ' + L] = statistiche(tronca([[normalizza(w, k) for w in r] for r in ts]))
        fuori = []
        for m in MISURE:
            a, b = intervalli[m]
            marg = 0.15 * (b - a)
            if not (a - marg <= v[m] <= b + marg):
                fuori.append(m)
        regge[L] = fuori
    scelto = next((L for L in LIVELLI if not regge[L]), None)
    ris['misure_fuori_intervallo'] = regge
    ris['livello_scelto'] = scelto
    ris['metro'] = metro()
    for nome, r in ris.items():
        if isinstance(r, dict) and 'classi' in r:
            extra = ' | H(sill|cl) %.2f H(cl|sill) %.2f' % (r['H(sillaba|classe)'], r['H(classe|sillaba)']) if 'H(sillaba|classe)' in r else ''
            print('%-30s classi %5d uniche %.2f h1 %.2f h2 %.2f zipf %.2f rip %.3f unita/riga %.1f (cv %.2f)%s' % (
                nome, r['classi'], r['quota_classi_uniche'], r['h1'], r['h2'], r['zipf'], r['ripetizione'], r['unita_per_riga'],
                r['cv_unita_per_riga'], extra), flush=True)
    print('misure fuori intervallo per livello:', dict(regge), '| livello scelto:', scelto)
    for k, x in ris['metro'].items():
        print('metro %-24s righe %4d unita/riga %.1f cv unita %.3f cv segni %.3f' % (k, x['righe'], x['unita_media'], x['cv_unita'], x['cv_segni']))
    with open(os.path.join(RISULTATI, 'e111_parole_sillabe.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e111 — Parole come sillabe?', '',
           'Flussi troncati a %d unità. Livelli di normalizzazione N0–N4 (vedi preregistrazione). Preregistrazione: '
           '`preregistrazioni/e111.md`.' % N, '',
           '| flusso | classi | quota uniche | h1 | h2 | Zipf | ripetizione | unità/riga (CV) |', '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict) and 'classi' in r:
            out.append('| %s | %d | %.2f | %.2f | %.2f | %.2f | %.3f | %.1f (%.2f) |' % (nome, r['classi'], r['quota_classi_uniche'], r['h1'], r['h2'],
                                                                                  r['zipf'], r['ripetizione'], r['unita_per_riga'], r['cv_unita_per_riga']))
    out += ['', 'Misure del Voynich fuori dall\'intervallo delle sillabe vere, per livello: %s. Livello scelto: **%s**.' % (dict(regge), scelto), '',
            '## Metro', '', '| testo | righe | unità per riga | CV unità | CV larghezza |', '|---|---|---|---|---|']
    for k, x in ris['metro'].items():
        out.append('| %s | %d | %.1f | %.3f | %.3f |' % (k, x['righe'], x['unita_media'], x['cv_unita'], x['cv_segni']))
    with open(os.path.join(RISULTATI, 'e111_parole_sillabe.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
