# -*- coding: utf-8 -*-
"""Esperimento 116: che cosa si ripete? Concentrazione, sezioni, serie, posizione delle ripetizioni immediate.

Preregistrazione: preregistrazioni/e116.md. Scrive risultati/e116_ripetizioni.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, BOOT, RIMESCOLAMENTI = 116, 1000, 500
SEZIONI = OrderedDict([('H', 'erbario'), ('B', 'biologia'), ('P', 'farmacia'), ('S', 'ricette')])


def rapporto_riga(righe):
    vic = sum(a == b for r in righe for a, b in zip(r, r[1:])) / max(1, sum(len(r) - 1 for r in righe if r))
    tot = ug = 0
    for r in righe:
        c = Counter(r)
        n = len(r)
        tot += n * (n - 1) / 2
        ug += sum(k * (k - 1) / 2 for k in c.values())
    return vic / (ug / tot) if ug else None


def concentrazione(righe, k=10):
    rip = Counter(a for r in righe for a, b in zip(r, r[1:]) if a == b)
    occ = Counter(w for r in righe for w in r)
    top = [w for w, _ in rip.most_common(k)]
    q_rip = sum(rip[w] for w in top) / max(1, sum(rip.values()))
    q_occ = sum(occ[w] for w in top) / sum(occ.values())
    return q_rip / q_occ, top, rip


def serie(righe):
    oss = Counter()
    for r in righe:
        i = 0
        while i < len(r):
            j = i
            while j + 1 < len(r) and r[j + 1] == r[i]:
                j += 1
            L = j - i + 1
            if L >= 2:
                oss[min(L, 4)] += 1
            i = j + 1
    p = sum(a == b for r in righe for a, b in zip(r, r[1:])) / max(1, sum(len(r) - 1 for r in righe if r))
    # attesa con ripetizione indipendente dalla storia: serie di lunghezza L ~ p^(L-1)(1-p) sui punti di inizio
    inizi = sum(1 for r in righe for i in range(len(r)) if i == 0 or r[i] != r[i - 1])
    att = {L: inizi * p ** (L - 1) * (1 - p) for L in (2, 3)}
    att[4] = inizi * p ** 3
    return {L: (oss[L], att[L]) for L in (2, 3, 4)}


def posizione(righe, rnd):
    def pos(rr):
        c = Counter()
        for r in rr:
            n = len(r)
            for i in range(1, n):
                if r[i] == r[i - 1]:
                    c[min(3, 4 * i // n)] += 1
        return c
    tutte = Counter(min(3, 4 * i // len(r)) for r in righe for i in range(1, len(r)))
    vera = e71.jsd(pos(righe), tutte)
    nul = []
    for _ in range(RIMESCOLAMENTI):
        mes = []
        for r in righe:
            r = r[:]
            rnd.shuffle(r)
            mes.append(r)
        nul.append(e71.jsd(pos(mes), tutte))
    m, s = statistics.mean(nul), statistics.pstdev(nul)
    return vera, (vera - m) / s if s else None, dict(pos(righe))


def main():
    righe_v = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    voy = [[w for w in r.parole if trascrizione.pulita(w)] for r in righe_v]
    ris = OrderedDict()
    conc, top, rip = concentrazione(voy)
    ris['concentrazione'] = conc
    ris['tipi_piu_ripetuti'] = [(w, rip[w]) for w in [x for x, _ in rip.most_common(15)]]
    contesti = defaultdict(Counter)
    for r in voy:
        for i in range(1, len(r)):
            if r[i] == r[i - 1] and r[i] in top:
                contesti[r[i]][(r[i - 2] if i >= 2 else '^', r[i + 1] if i + 1 < len(r) else '$')] += 1
    ris['contesti'] = {w: [('%s _ _ %s' % k, n) for k, n in c.most_common(3)] for w, c in contesti.items()}
    # per sezione, con bootstrap delle pagine
    per_pag = defaultdict(lambda: defaultdict(list))
    for r in righe_v:
        sez = r.sezione if r.sezione in SEZIONI else 'altre'
        ps = [w for w in r.parole if trascrizione.pulita(w)]
        if ps:
            per_pag[sez][r.pagina].append(ps)
    rnd = random.Random(SEME)
    sez_ris = OrderedDict()
    for sez, pagine in per_pag.items():
        chiavi = list(pagine)
        val = rapporto_riga([r for p in chiavi for r in pagine[p]])
        boot = []
        for _ in range(BOOT):
            camp = [chiavi[rnd.randrange(len(chiavi))] for _ in chiavi]
            x = rapporto_riga([r for p in camp for r in pagine[p]])
            if x is not None:
                boot.append(x)
        boot.sort()
        sez_ris[SEZIONI.get(sez, sez)] = OrderedDict([('pagine', len(chiavi)), ('rapporto', val),
                                                     ('ic95', (boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]))])
    ris['sezioni'] = sez_ris
    ris['serie'] = {str(L): v for L, v in serie(voy).items()}
    jsd, z, dist = posizione(voy, random.Random(SEME))
    ris['posizione'] = {'jsd': jsd, 'z': z, 'quarti': dist}
    # confronti
    conf = OrderedDict()
    ts = [ps for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt'))]
    from e65_aperture_ricette import paragrafi_apicio
    api = [w for p in paragrafi_apicio() for w in p]
    lat = lingue.parole('Latin')[:35000]
    for nome, rr in (('Timm e Schinner', ts), ('Apicio', [api[i:i + 9] for i in range(0, len(api), 9)]), ('Bibbia latina', [lat[i:i + 9] for i in range(0, len(lat), 9)])):
        c, tt, rp = concentrazione(rr)
        conf[nome] = OrderedDict([('rapporto_riga', rapporto_riga(rr)), ('concentrazione', c), ('serie', {str(L): v for L, v in serie(rr).items()}),
                                  ('tipi_piu_ripetuti', [(w, rp[w]) for w, _ in rp.most_common(8)])])
    ris['confronti'] = conf
    # lettura
    sp = [sez_ris[n] for n in ('ricette', 'farmacia') if n in sez_ris]
    altre = [v for n, v in sez_ris.items() if n not in ('ricette', 'farmacia')]
    sez_ok = any(all(x['ic95'][0] > y['ic95'][1] for y in altre) for x in sp)
    s3 = ris['serie']['3'][0] > 1.5 * ris['serie']['3'][1] or ris['serie']['4'][0] > 1.5 * ris['serie']['4'][1]
    pos_ok = (z or 0) > 4
    if conc >= 3 and sez_ok and (s3 or pos_ok):
        lettura = 'numeri e quantità sostenuti'
    elif conc < 1.5 and not sez_ok:
        lettura = 'contro i numeri'
    else:
        lettura = 'misto'
    ris['lettura'] = lettura
    print('concentrazione %.2f | tipi piu ripetuti %s' % (conc, ris['tipi_piu_ripetuti'][:10]))
    for n, v in sez_ris.items():
        print('  sezione %-10s pagine %3d rapporto %.2f [%.2f, %.2f]' % (n, v['pagine'], v['rapporto'], v['ic95'][0], v['ic95'][1]))
    print('  serie (osservate, attese):', ris['serie'], '| posizione jsd %.4f z %.1f %s' % (jsd, z or 0, dist))
    for n, v in conf.items():
        print('  %-16s rapporto %.2f concentrazione %.2f serie %s top %s' % (n, v['rapporto_riga'], v['concentrazione'], v['serie'], v['tipi_piu_ripetuti'][:5]))
    print('  contesti:', ris['contesti'])
    print('lettura:', lettura)
    with open(os.path.join(RISULTATI, 'e116_ripetizioni.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e116 — Che cosa si ripete?', '', 'Preregistrazione: `preregistrazioni/e116.md`.', '',
           '- Concentrazione delle ripetizioni nei 10 tipi più ripetuti: **%.2f**' % conc,
           '- Tipi più ripetuti: %s' % ', '.join('%s (%d)' % x for x in ris['tipi_piu_ripetuti']),
           '- Serie (osservate / attese): %s' % ', '.join('%s: %d / %.1f' % (L, o, a) for L, (o, a) in ris['serie'].items()),
           '- Posizione della ripetizione nella riga: JSD %.4f, z %.1f, per quarti %s' % (jsd, z or 0, dist), '',
           '| sezione | pagine | ripetizione / attesa | IC 95% |', '|---|---|---|---|']
    for n, v in sez_ris.items():
        out.append('| %s | %d | %.2f | %.2f–%.2f |' % (n, v['pagine'], v['rapporto'], v['ic95'][0], v['ic95'][1]))
    out += ['', '| confronto | ripetizione / attesa | concentrazione | serie |', '|---|---|---|---|']
    for n, v in conf.items():
        out.append('| %s | %.2f | %.2f | %s |' % (n, v['rapporto_riga'], v['concentrazione'], ', '.join('%s: %d/%.1f' % (L, o, a) for L, (o, a) in v['serie'].items())))
    out += ['', 'Lettura: **%s**.' % lettura]
    with open(os.path.join(RISULTATI, 'e116_ripetizioni.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
