# -*- coding: utf-8 -*-
"""Esperimento 133: verifica sistematica delle letture proposte da Bax (2014) e Vatne (2021): occorrenze delle parole,
chiave di Bax contro chiavi casuali fuori campione, affermazione di Vatne sulle sue parole.

Preregistrazione: preregistrazioni/e133.md. Scrive risultati/e133_letture_proposte.json e .md.
"""
import hashlib, json, math, os, random, re, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
CACHE = os.path.join(QUI, '..', 'dati', 'cache', 'letture_proposte')
SHA_BAX = '1ae1a2dae7af8f463de8e5b94d8905028f1c555a6ea59c011c4e553375c12c4e'
SHA_VATNE = 'f7a91b48e898143edf3ca779ed1d5584ecf46a00fb8241832ad7777a40a99e72'
SEME, CHIAVI_CASUALI, CONFRONTI = 133, 10000, 1000

BAX_PAROLE = [  # (pagina, parole EVA, lettura, oggetto)
    ('f2r', ['kydainy'], 'kantairon', 'centaurea'),
    ('f2r', ['kydain', 'shaiin'], 'Chiron', 'centauro'),
    ('f3v', ['koaiin'], 'kaur', 'elleboro'),
    ('f29v', ['kooiin', 'shor'], 'ka-ur char', 'nigella'),
    ('f31r', ['keedey'], 'kooton', 'cotone'),
    ('f27r', ['ksor'], 'ksar', 'croco'),
    ('f41v', ['keeredal'], 'koratu-', 'coriandolo'),
    ('f16r', ['oror'], 'arar', 'ginepro'),
]
A_FRONTE = {'f15v': 'f16r', 'f16r': 'f15v'}
BAX_PAGINE = {'f2r', 'f3v', 'f15v', 'f16r', 'f27r', 'f29v', 'f31r'}
CONSONANTICI = ['k', 'sh', 'y', 'd', 'r', 'm', 'n', 'in', 'iin', 's']
BAX_CHIAVE = {'k': 'K', 'sh': 'K', 'y': 'N', 'd': 'T', 'r': 'R', 'm': 'R', 'n': 'R', 'in': 'R', 'iin': 'R', 's': 'S'}
VOCALI = {'o', 'a', 'e', 'ee'}
LESSICO = {'KNTRN', 'KRN', 'KR', 'KRPK', 'RR', 'TR', 'TRN', 'KTN', 'KSR', 'KRT', 'KRNTR'}
FORME = ['iin', 'in', 'ee', 'sh'] + sorted(set(CONSONANTICI + list(VOCALI)) - {'iin', 'in', 'ee', 'sh'}, key=len, reverse=True)


def controlla(nome, sha):
    d = open(os.path.join(CACHE, nome), 'rb').read()
    if hashlib.sha256(d).hexdigest() != sha:
        raise SystemExit('%s diverso da quello preregistrato' % nome)


def segni(w):
    out, i = [], 0
    while i < len(w):
        for f in FORME:
            if w.startswith(f, i):
                out.append(f)
                i += len(f)
                break
        else:
            return None
    return out


def scheletro(w, chiave):
    s = segni(w)
    if s is None:
        return None
    return ''.join(chiave[g] for g in s if g not in VOCALI)


def testo():
    zl = trascrizione.leggi('ZL')
    return [r for r in zl if r.parole]


def parte1(righe):
    tutte = [(r.pagina, r.sezione, w) for r in righe for w in r.parole if trascrizione.pulita(w)]
    freq = Counter(w for _, _, w in tutte)
    per_pag = defaultdict(Counter)
    for p, _, w in tutte:
        per_pag[w][p] += 1
    rnd = random.Random(SEME)
    out = OrderedDict()
    for pag, parole, lettura, oggetto in BAX_PAROLE:
        for w in parole:
            n = freq[w]
            pp = per_pag[w]
            sul = pp[pag] + pp[A_FRONTE[pag]] if pag in A_FRONTE else pp[pag]
            quota = sul / n if n else None
            # confronto: parole di frequenza simile, quota sulla loro pagina piu' frequente
            simili = [x for x, c in freq.items() if n and 0.8 * n <= c <= 1.2 * n and x != w]
            ref = []
            for _ in range(CONFRONTI):
                x = rnd.choice(simili)
                ref.append(max(per_pag[x].values()) / freq[x])
            m, s = statistics.mean(ref), statistics.pstdev(ref)
            sezioni = Counter(sz for p2, sz, x in tutte if x == w)
            out['%s %s' % (pag, w)] = OrderedDict([
                ('lettura', lettura), ('oggetto', oggetto), ('occorrenze', n), ('pagine', len(pp)),
                ('sezioni', dict(sezioni)), ('sulla_pagina', sul), ('quota_sulla_pagina', quota),
                ('quota_attesa_parole_simili', m), ('z', (quota - m) / s if s and quota is not None else None),
                ('coerente', quota is not None and quota >= 0.5)])
    return out


def prime_erbario(righe):
    out = OrderedDict()
    for r in righe:
        if r.sezione == 'H' and r.tipo and r.tipo[0] == 'P' and r.pagina not in out and r.parole and trascrizione.pulita(r.parole[0]):
            out[r.pagina] = r.parole[0]
    return out


def conta(prime, chiave, escluse=()):
    return sum(1 for p, w in prime.items() if p not in escluse and scheletro(w, chiave) in LESSICO)


def parte2(righe):
    prime = prime_erbario(righe)
    s_tutte, s_fuori = conta(prime, BAX_CHIAVE), conta(prime, BAX_CHIAVE, BAX_PAGINE)
    valori = [BAX_CHIAVE[g] for g in CONSONANTICI]
    rnd = random.Random(SEME)
    nulli_t, nulli_f = [], []
    for _ in range(CHIAVI_CASUALI):
        v = valori[:]
        rnd.shuffle(v)
        ch = dict(zip(CONSONANTICI, v))
        nulli_t.append(conta(prime, ch))
        nulli_f.append(conta(prime, ch, BAX_PAGINE))
    p99 = sorted(nulli_f)[int(0.99 * (len(nulli_f) - 1))]
    decifrabili = sum(1 for p, w in prime.items() if p not in BAX_PAGINE and scheletro(w, BAX_CHIAVE) is not None)
    # descrittivo: parole interne che decifrano in un nome del lessico
    interne = [w for r in righe if r.tipo and r.tipo[0] == 'P' for w in r.parole[1:] if trascrizione.pulita(w)]
    nomi_interni = Counter(scheletro(w, BAX_CHIAVE) for w in interne if scheletro(w, BAX_CHIAVE) in LESSICO)
    esempi = OrderedDict((p, (w, scheletro(w, BAX_CHIAVE))) for p, w in prime.items() if p not in BAX_PAGINE and scheletro(w, BAX_CHIAVE) in LESSICO)
    return OrderedDict([
        ('pagine_erbario', len(prime)), ('prime_decifrabili_fuori_campione', decifrabili),
        ('S_tutte', s_tutte), ('nullo_tutte_media', statistics.mean(nulli_t)),
        ('p_tutte', sum(x >= s_tutte for x in nulli_t) / len(nulli_t)),
        ('S_fuori', s_fuori), ('nullo_fuori_media', statistics.mean(nulli_f)), ('nullo_fuori_p99', p99),
        ('p_fuori', sum(x >= s_fuori for x in nulli_f) / len(nulli_f)),
        ('batte_il_caso_fuori_campione', s_fuori > p99),
        ('esempi_fuori_campione', esempi),
        ('parole_interne', len(interne)), ('interne_con_nome_del_lessico', sum(nomi_interni.values())),
        ('interne_per_nome', dict(nomi_interni.most_common()))])


def voci_vatne():
    txt = os.path.join(CACHE, 'vatne_2021.txt')
    if not os.path.exists(txt):  # testo estratto con: pdftotext -layout vatne_2021.pdf vatne_2021.txt
        import subprocess
        subprocess.run(['pdftotext', '-layout', os.path.join(CACHE, 'vatne_2021.pdf'), txt], check=True)
    t = open(os.path.join(CACHE, 'vatne_2021.txt'), encoding='utf-8', errors='replace').read().splitlines()
    voci = []
    for l in t:
        m = re.match(r'^\s{0,3}(\d{1,3}[rv]\d?)\s{2,}(\S.*?)\s{2,}(\S.*?)(\s{2,}|$)', l)
        if m:
            voci.append(('f' + m.group(1), m.group(2)))
    return voci


def parte3(righe):
    per_pag = defaultdict(set)
    pagine_di = defaultdict(set)
    for r in righe:
        for w in r.parole:
            per_pag[r.pagina].add(w)
            pagine_di[w].add(r.pagina)
    voci = voci_vatne()
    tenute, escluse = [], []
    for pag, cif in voci:
        w = cif.split()[0].lower()
        if re.fullmatch(r'[a-z]+', w) and w in per_pag.get(pag, ()):
            tenute.append((pag, w))
        else:
            escluse.append((pag, cif))
    altrove = [(p, w) for p, w in tenute if pagine_di[w] - {p}]
    prime = prime_erbario(righe)
    sue = {p for p, _ in tenute}
    conf = [(p, w) for p, w in prime.items() if p not in sue]
    conf_altrove = [(p, w) for p, w in conf if pagine_di[w] - {p}]
    a, b = len(altrove), len(tenute) - len(altrove)
    c, d = len(conf_altrove), len(conf) - len(conf_altrove)
    p = fisher_minore(a, b, c, d)
    return OrderedDict([
        ('voci_nella_tabella', len(voci)), ('voci_tenute', len(tenute)), ('voci_escluse', len(escluse)),
        ('tenute', tenute), ('altrove', len(altrove)), ('quota_altrove', a / len(tenute) if tenute else None),
        ('esempi_altrove', [(p_, w, sorted(pagine_di[w] - {p_})[:6]) for p_, w in altrove[:15]]),
        ('confronto_prime_parole', len(conf)), ('confronto_altrove', len(conf_altrove)),
        ('quota_confronto_altrove', c / len(conf) if conf else None), ('p_fisher', p),
        ('affermazione_smentita', bool(tenute) and a / len(tenute) > 0.2),
        ('come_nomi', p < 0.01)])


def fisher_minore(a, b, c, d):
    """p unilaterale che la prima riga abbia una quota di 'altrove' cosi' bassa o piu' (ipergeometrica)."""
    n1, n2, k = a + b, c + d, a + c
    tot = math.comb(n1 + n2, k)
    return sum(math.comb(n1, x) * math.comb(n2, k - x) for x in range(0, a + 1) if 0 <= k - x <= n2) / tot


def main():
    controlla('bax_2014.pdf', SHA_BAX)
    controlla('vatne_2021.pdf', SHA_VATNE)
    righe = testo()
    ris = OrderedDict()
    ris['parte1_bax_occorrenze'] = p1 = parte1(righe)
    for k, v in p1.items():
        print('%-18s %-12s %-11s occ %4d pagine %3d | sulla pagina %d (%.2f; attesa %.2f, z %.1f) | sezioni %s | coerente %s' % (
            k, v['lettura'], v['oggetto'], v['occorrenze'], v['pagine'], v['sulla_pagina'], v['quota_sulla_pagina'] or 0,
            v['quota_attesa_parole_simili'], v['z'] or 0, v['sezioni'], v['coerente']), flush=True)
    coerenti = sum(v['coerente'] for v in p1.values())
    ris['bax_letture_reggono'] = coerenti >= len(p1) / 2
    print('Bax: parole coerenti come nomi %d su %d' % (coerenti, len(p1)), flush=True)
    ris['parte2_bax_chiave'] = p2 = parte2(righe)
    print('Bax, chiave: pagine d\'erbario %d | S_tutte %d (nullo %.2f, p %.4f) | S_fuori %d (nullo %.2f, p99 %d, p %.4f) | batte il caso fuori campione %s' % (
        p2['pagine_erbario'], p2['S_tutte'], p2['nullo_tutte_media'], p2['p_tutte'], p2['S_fuori'], p2['nullo_fuori_media'],
        p2['nullo_fuori_p99'], p2['p_fuori'], p2['batte_il_caso_fuori_campione']), flush=True)
    print('   esempi fuori campione: %s | parole interne con un nome del lessico: %d su %d (%s)' % (
        dict(list(p2['esempi_fuori_campione'].items())[:10]), p2['interne_con_nome_del_lessico'], p2['parole_interne'], p2['interne_per_nome']), flush=True)
    ris['parte3_vatne'] = p3 = parte3(righe)
    print('Vatne: voci %d, tenute %d | compaiono su altre pagine %d (%.2f) | prime parole di confronto altrove %.2f (%d) | p %.4f | affermazione smentita %s | come nomi %s' % (
        p3['voci_nella_tabella'], p3['voci_tenute'], p3['altrove'], p3['quota_altrove'] or 0, p3['quota_confronto_altrove'] or 0,
        p3['confronto_prime_parole'], p3['p_fisher'], p3['affermazione_smentita'], p3['come_nomi']), flush=True)
    for e in p3['esempi_altrove'][:10]:
        print('   ', e, flush=True)
    with open(os.path.join(RISULTATI, 'e133_letture_proposte.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e133 — Verifica sistematica delle letture proposte', '', 'Preregistrazione: `preregistrazioni/e133.md`. Fonti: Bax (2014); Vatne (2021).', '',
           '## Parte 1 — Le parole di Bax su tutte le occorrenze', '',
           '| pagina e parola | lettura | oggetto | occorrenze | pagine | sulla pagina proposta | attesa per parole simili (z) | sezioni | coerente |',
           '|---|---|---|---|---|---|---|---|---|']
    for k, v in p1.items():
        out.append('| %s | %s | %s | %d | %d | %d (%.2f) | %.2f (%.1f) | %s | %s |' % (
            k, v['lettura'], v['oggetto'], v['occorrenze'], v['pagine'], v['sulla_pagina'], v['quota_sulla_pagina'] or 0,
            v['quota_attesa_parole_simili'], v['z'] or 0, ', '.join('%s %d' % kv for kv in sorted(v['sezioni'].items(), key=lambda kv: -kv[1])),
            'sì' if v['coerente'] else 'no'))
    out += ['', 'Parole coerenti come nomi: %d su %d. Le letture reggono: **%s**.' % (coerenti, len(p1), 'sì' if ris['bax_letture_reggono'] else 'no'), '',
            '## Parte 2 — La chiave di Bax contro %d chiavi casuali' % CHIAVI_CASUALI, '',
            '| | pagine con un nome del lessico | nullo (media) | p |', '|---|---|---|---|',
            '| tutte le pagine d\'erbario (%d) | %d | %.2f | %.4f |' % (p2['pagine_erbario'], p2['S_tutte'], p2['nullo_tutte_media'], p2['p_tutte']),
            '| fuori campione (senza le 7 pagine di Bax) | %d | %.2f (99° percentile %d) | %.4f |' % (p2['S_fuori'], p2['nullo_fuori_media'], p2['nullo_fuori_p99'], p2['p_fuori']),
            '', 'Batte il caso fuori campione: **%s**. Prime parole decifrabili fuori campione: %d. Parole interne che decifrano in un nome del lessico: %d su %d.' % (
                'sì' if p2['batte_il_caso_fuori_campione'] else 'no', p2['prime_decifrabili_fuori_campione'], p2['interne_con_nome_del_lessico'], p2['parole_interne']),
            '', '## Parte 3 — Le parole di Vatne', '',
            'Voci nella tabella: %d; ritrovate identiche nella ZL sulla pagina indicata: %d. Compaiono anche su altre pagine: **%d (%.0f%%)**; '
            'prime parole di confronto: %.0f%% (%d). p (Fisher) = %.4f.' % (p3['voci_nella_tabella'], p3['voci_tenute'], p3['altrove'], 100 * (p3['quota_altrove'] or 0),
                                                                           100 * (p3['quota_confronto_altrove'] or 0), p3['confronto_prime_parole'], p3['p_fisher']),
            '', 'Affermazione "non si trovano altrove nel testo" smentita: **%s**. Si comportano come nomi: **%s**.' % (
                'sì' if p3['affermazione_smentita'] else 'no', 'sì' if p3['come_nomi'] else 'no')]
    with open(os.path.join(RISULTATI, 'e133_letture_proposte.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
