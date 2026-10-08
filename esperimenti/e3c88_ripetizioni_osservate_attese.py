# -*- coding: utf-8 -*-
"""Esperimento e3c88: la ripetizione immediata come rapporto osservato/atteso.

Nota A8 del revisore: la probabilità di ripetere per caso la parola precedente dipende da quanto il vocabolario è
concentrato (Σp²), non dalla sua grandezza; confrontare quote grezze (Voynich 1,0% contro lingue 0,1%) può ingannare.
Per ogni testo: quota osservata di coppie vicine identiche (parole di almeno 2 segni, stessa riga) e quasi identiche (a
una modifica, parole di almeno 3 segni), e due attese:
- atteso globale = Σ p_w² sulle parole di almeno 2 segni (due parole prese a caso dal testo);
- atteso nella riga = media su 20 rimescolamenti delle parole dentro ogni riga (stessa composizione delle righe).
Testi: Voynich ZL; 24 lingue naturali di Gaskell e Bowern (prime 10.000 parole, mediana per lingua); 6 scribi nordici
(Menota); 73 manoscritti tedeschi (ReF, prime 6.000 parole); Copiale; gibberish umano (insieme); generatori.

Preregistrazione: preregistrazioni/e3c88.md. Scrive risultati/e3c88_ripetizioni_osservate_attese.json e .md.
SOLO_CONTROLLI=1: prova del codice su testi finti (niente Voynich).
"""
import json, os, random, statistics, sys, zipfile
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure
import e134_generatori_esterni as e134
import e337_posizione as e337
import e375_coppie as e375
import e381_parole_intere as e381
import e3a55_frequenza_forma as e3a55
import e3a58_spazi_prevedibili as e3a58
import e3a86_ripetizioni_riga as e3a86
import e3c58_altri_scribi as e3c58
import e3c65_ripetizioni_scribi as e3c65
import e3c77_ref_finestra_deriva as e3c77
import e3c84_confronti_per_lingua as e3c84

RISULTATI = os.path.join(QUI, '..', 'risultati')
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
PERM = 20
D = misure.divisore(misure.GLIFI_EVA)


def conta(righe):
    rip = [0, 0]
    quasi = [0, 0]
    for r in righe:
        for a, b in zip(r, r[1:]):
            if len(a) >= 2 and len(b) >= 2:
                rip[0] += a == b
                rip[1] += 1
            if len(a) >= 3 and len(b) >= 3:
                quasi[0] += e3a86.una_modifica(a, b)
                quasi[1] += 1
    return rip, quasi


def misura(righe, rnd):
    righe = [[tuple(w) for w in r] for r in righe if r]
    rip, quasi = conta(righe)
    o_r = rip[0] / rip[1] if rip[1] else None
    o_q = quasi[0] / quasi[1] if quasi[1] else None
    tok = Counter(w for r in righe for w in r if len(w) >= 2)
    n = sum(tok.values())
    e_glob = sum((c / n) ** 2 for c in tok.values()) if n else None
    nr, nq = [], []
    for _ in range(PERM):
        a, b = conta([rnd.sample(r, len(r)) for r in righe])
        nr.append(a[0] / a[1] if a[1] else 0.0)
        nq.append(b[0] / b[1] if b[1] else 0.0)
    e_r, e_q = statistics.mean(nr), statistics.mean(nq)
    div = lambda x, y: (x / y) if (x is not None and y) else None
    return OrderedDict([('coppie', rip[1]), ('ripetizione', o_r), ('atteso_globale', e_glob), ('OE_globale', div(o_r, e_glob)),
                        ('atteso_riga', e_r), ('OE_riga', div(o_r, e_r)), ('quasi', o_q), ('quasi_atteso_riga', e_q), ('quasi_OE_riga', div(o_q, e_q))])


def gruppi_testi():
    """OrderedDict nome -> righe (parole come tuple di segni)."""
    out = OrderedDict()
    out['Voynich ZL'] = [r for p in e375.voynich() for r in p]
    for k, t in e381.testi().items():
        out['lingua: ' + k.replace('.txt', '')] = e3a58.righe_prime(t)
    for ms in e3c65.MANOSCRITTI:
        out['nordico: ' + ms] = [[tuple(w) for w in r] for _, _, rr in e3c58.leggi(ms) for r in rr]
    per_ms = OrderedDict()
    for sigla, rr in e3c77.pagine_ref():
        per_ms.setdefault(sigla, []).extend([[tuple(w) for w in r] for r in rr])
    for sigla, rr in per_ms.items():
        out['tedesco: ' + sigla] = rr
    out['Copiale (cifrato)'] = e3c65.righe_copiale()
    gib = []
    with zipfile.ZipFile(os.path.join(e3a55.GB, 'gibberish_transcriptions.zip')) as z:
        for nome in sorted(z.namelist()):
            if nome.endswith('.txt'):
                for l in z.read(nome).decode('utf-8', errors='ignore').splitlines():
                    r = [w for w in (e381.parola(p) for p in l.split()) if w]
                    if r:
                        gib.append(r)
    out['gibberish umano'] = gib
    e134.controlla()
    for k, v in e134.testi().items():
        if k != 'Voynich':
            out['generatore: ' + k] = [[w for w in (tuple(D(x)) for x in ps) if w] for _, ps in v]
    out['generatore: Timm e Schinner, seme 1'] = [[tuple(D(w)) for w in r] for p in e337.pagine_ts(1) for r in p]
    return out


def finti(rnd):
    """(a) vocabolario concentratissimo, parole indipendenti: quota grezza alta, O/E ≈ 1;
    (b) vocabolario vario con ripetizione voluta (20% delle parole ripete la precedente): O/E molto sopra 1."""
    voc_a = ['ab', 'cd', 'ef'] + ['w%d' % i for i in range(200)]
    pesi_a = [30, 20, 10] + [0.2] * 200
    a = [[tuple(rnd.choices(voc_a, pesi_a)[0]) for _ in range(8)] for _ in range(1500)]
    voc_b = ['w%d' % i for i in range(3000)]
    b = []
    for _ in range(1500):
        r = [tuple(rnd.choice(voc_b))]
        for _ in range(7):
            r.append(r[-1] if rnd.random() < 0.2 else tuple(rnd.choice(voc_b)))
        b.append(r)
    return a, b


def main():
    rnd = random.Random(3388)
    if SOLO_CONTROLLI:
        a, b = finti(rnd)
        for nome, t in (('(a) vocabolario concentrato, nessuna ripetizione voluta', a), ('(b) ripetizione voluta', b)):
            print(nome, json.dumps(misura(t, rnd), default=float))
        lat = e3a58.righe_prime(e381.testi()['Historical - Latin - Literary - NT (Vulgate).txt'])
        print('latino', json.dumps(misura(lat, rnd), default=float))
        return
    ris = OrderedDict()
    for k, t in gruppi_testi().items():
        ris[k] = misura(t, rnd)
        print(k, json.dumps(ris[k], default=float), flush=True)
    V = ris['Voynich ZL']
    # lingue: mediana per lingua (naturali), come e3c84
    per_l = {}
    for k, x in ris.items():
        if k.startswith('lingua: '):
            cat, ling = e3c84.etichetta(k[len('lingua: '):])
            if cat != 'Conlangs' and x['OE_riga'] is not None:
                per_l.setdefault(ling, []).append(x)
    lingue = OrderedDict((l, OrderedDict((s, statistics.median(x[s] for x in xs if x[s] is not None)) for s in ('ripetizione', 'OE_globale', 'OE_riga', 'quasi_OE_riga')))
                         for l, xs in sorted(per_l.items()))
    manoscritti = OrderedDict((k, x) for k, x in ris.items() if k.startswith(('nordico: ', 'tedesco: ')))

    def oltre(gruppo, s):
        return sorted(k for k, x in gruppo.items() if x[s] is not None and x[s] >= V[s])
    esiti = OrderedDict()
    for s in ('OE_riga', 'OE_globale', 'quasi_OE_riga'):
        ol, om = oltre(lingue, s), oltre(manoscritti, s)
        esiti[s] = OrderedDict([('voynich', V[s]), ('lingue_oltre', ol), ('manoscritti_oltre', om),
                                ('lingue_massimo', max(x[s] for x in lingue.values())), ('manoscritti_massimo', max(x[s] for x in manoscritti.values() if x[s] is not None)),
                                ('esito', 'regge: più di tutte le lingue e di tutti i 79 manoscritti' if not ol and not om else
                                 'da riformulare: %d lingue e %d manoscritti arrivano al Voynich' % (len(ol), len(om)))])
    out = OrderedDict([('testi', ris), ('lingue', lingue), ('esiti', esiti)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3c88_ripetizioni_osservate_attese.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    f = lambda v, fmt='%.2f': (fmt % v) if v is not None else '–'
    md = ['# e3c88 — La ripetizione immediata come rapporto osservato/atteso', '', 'Preregistrazione: `preregistrazioni/e3c88.md`. O/E nella riga = osservato / media di 20 rimescolamenti delle parole nella riga; O/E globale = osservato / Σp².', '',
          '| testo | coppie | ripetizione | O/E nella riga | O/E globale | quasi, O/E nella riga |', '|---|---|---|---|---|---|']
    for k, x in ris.items():
        if k.startswith('lingua: '):
            continue
        md.append('| %s | %d | %s | %s | %s | %s |' % (k, x['coppie'], f(x['ripetizione'], '%.4f'), f(x['OE_riga']), f(x['OE_globale']), f(x['quasi_OE_riga'])))
    md += ['', '## Lingue naturali (mediana per lingua)', '', '| lingua | ripetizione | O/E nella riga | O/E globale | quasi, O/E nella riga |', '|---|---|---|---|---|']
    for l, x in lingue.items():
        md.append('| %s | %s | %s | %s | %s |' % (l, f(x['ripetizione'], '%.4f'), f(x['OE_riga']), f(x['OE_globale']), f(x['quasi_OE_riga'])))
    md += ['', '## Esiti', '']
    for s, e in esiti.items():
        md.append('- **%s:** Voynich %.2f; massimo delle lingue %.2f, dei manoscritti %.2f; %s.' % (s, e['voynich'], e['lingue_massimo'], e['manoscritti_massimo'], e['esito']))
    open(os.path.join(RISULTATI, 'e3c88_ripetizioni_osservate_attese.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(esiti, ensure_ascii=False, indent=1, default=float))


if __name__ == '__main__':
    main()
