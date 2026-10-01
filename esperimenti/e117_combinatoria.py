# -*- coding: utf-8 -*-
"""Esperimento 117: inizio e fine della parola si combinano liberamente (tavola) o con vincoli (lingua)?

Preregistrazione: preregistrazioni/e117.md. Scrive risultati/e117_combinatoria.json e .md.
"""
import json, math, os, random, statistics, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
import e71_bordo_riga as e71

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEME, RICOMBINAZIONI, NI, NF = 117, 100, 12, 20
D = misure.divisore(misure.GLIFI_EVA)


def entropia(c):
    n = sum(c.values())
    return -sum(k / n * math.log2(k / n) for k in c.values() if k)


def misure_tipi(coppie):
    ci = Counter(a for a, _ in coppie)
    cf = Counter(b for _, b in coppie)
    ini = [a for a, _ in ci.most_common(NI)]
    fin = [b for b, _ in cf.most_common(NF)]
    celle = {(a, b) for a, b in coppie if a in ini and b in fin}
    riemp = len(celle) / (len(ini) * len(fin))
    sel = [(a, b) for a, b in coppie if a in ini and b in fin]
    im = misure.informazione_mutua(sel)
    dip = im / min(entropia(Counter(a for a, _ in sel)), entropia(Counter(b for _, b in sel)))
    return riemp, dip


def una(nome, parole, dividi):
    tipi = {tuple(dividi(w)) for w in parole}
    coppie = [(u[0], ''.join(u[-2:])) for u in tipi if len(u) >= 3]
    riemp, dip = misure_tipi(coppie)
    rnd = random.Random(SEME)
    r_n, d_n = [], []
    fini = [b for _, b in coppie]
    for _ in range(RICOMBINAZIONI):
        rnd.shuffle(fini)
        x, y = misure_tipi(list(zip([a for a, _ in coppie], fini)))
        r_n.append(x)
        d_n.append(y)
    return OrderedDict([('tipi', len(coppie)), ('riempimento', riemp), ('riempimento_atteso', statistics.mean(r_n)),
                        ('riempimento_rapporto', riemp / statistics.mean(r_n)), ('dipendenza', dip), ('dipendenza_attesa', statistics.mean(d_n))])


def main():
    voy = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    t = OrderedDict()
    t['Voynich ZL'] = (voy, D)
    t['Timm e Schinner'] = ([w for _, ps in e71.righe_file(os.path.join(e71.CACHE, 'seme_19', 'generate', 'generated_text.txt')) for w in ps], D)
    t['Naibbe'] = (open(os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt'), encoding='utf-8').read().split()[:35000], D)
    import e99_macer as e99
    import e104_sillabe_varianti as e104
    caps = e99.capitoli()
    sill = [[[s for w in ps for s in generatori.sillabe(w)] for ps in cap] for cap in caps]
    cif = e104.costruisci(sill, voy, generatori.Modifiche(voy, D), 0.6, 1)
    t['cifrato a sillabe (e104, mu 0,6)'] = ([w for p in cif for r in p for w in r], D)
    bibbie = OrderedDict([('Latin', 'latina'), ('Italian', 'italiana'), ('English', 'inglese'), ('Turkish', 'turca'), ('Hungarian', 'ungherese'), ('Finnish', 'finlandese')])
    for k, n in bibbie.items():
        t['Bibbia ' + n] = (lingue.parole(k)[:35000], e71.lettere)
    ris = OrderedDict()
    for nome, (ps, dv) in t.items():
        ris[nome] = una(nome, ps, dv)
        r = ris[nome]
        print('%-34s tipi %5d | riempimento %.2f (atteso %.2f, rapporto %.2f) | dipendenza %.3f (attesa %.3f)' % (
            nome, r['tipi'], r['riempimento'], r['riempimento_atteso'], r['riempimento_rapporto'], r['dipendenza'], r['dipendenza_attesa']), flush=True)
    lb = [ris['Bibbia ' + n] for n in bibbie.values()]
    v = ris['Voynich ZL']
    piu = v['riempimento_rapporto'] > max(x['riempimento_rapporto'] for x in lb) and v['dipendenza'] < min(x['dipendenza'] for x in lb)
    ris['piu_combinatorio_di_ogni_lingua'] = piu
    print('piu\' combinatorio di ogni lingua:', piu)
    with open(os.path.join(RISULTATI, 'e117_combinatoria.json'), 'w', encoding='utf-8') as fo:
        json.dump(ris, fo, ensure_ascii=False, indent=1)
    out = ['# e117 — Le parti della parola si combinano come in una tavola?', '', 'Inizio = primo segno, fine = ultimi due; %d × %d '
           'combinazioni più frequenti fra i tipi. Preregistrazione: `preregistrazioni/e117.md`.' % (NI, NF), '',
           '| testo | tipi | riempimento | atteso | rapporto | dipendenza | attesa |', '|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        if isinstance(r, dict):
            out.append('| %s | %d | %.2f | %.2f | %.2f | %.3f | %.3f |' % (nome, r['tipi'], r['riempimento'], r['riempimento_atteso'],
                                                                   r['riempimento_rapporto'], r['dipendenza'], r['dipendenza_attesa']))
    out += ['', 'Più combinatorio di ogni lingua: **%s**.' % ('sì' if piu else 'no')]
    with open(os.path.join(RISULTATI, 'e117_combinatoria.md'), 'w', encoding='utf-8') as fo:
        fo.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
