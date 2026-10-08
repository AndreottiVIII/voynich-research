# -*- coding: utf-8 -*-
"""Esperimento e3c92: correzione per confronti multipli delle prove principali del white paper (rianalisi).

Nota A3 del revisore: centinaia di prove con z e p, nessuna correzione e nessuna famiglia dichiarata. Qui:
- si dichiarano le famiglie (una per scoperta) e, per ognuna, le prove principali citate nel paper, lette dai file dei
  risultati (valori salvati, nessuna misura nuova);
- p a due code dalla z (normale); per le misure date con un intervallo bootstrap (e3c86, per bifoglio) z = stima /
  (semiampiezza / 1,96); per le prove a permutazione con p salvato (e3a02) si usa quel p (p = 0 → 1/10.000);
- correzione di Holm dentro ogni famiglia (α = 0,05) e, più severa, Bonferroni su tutti i 715 esperimenti del registro
  (α = 0,05 / 715).
Le frasi di confronto con un insieme di riferimento ("oltre tutte le 24 lingue") non sono prove contro un nullo e non
entrano: sono descrittive (e3c84).

Preregistrazione: preregistrazioni/e3c92.md. Scrive risultati/e3c92_confronti_multipli.json e .md.
"""
import json, math, os
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = os.path.join(QUI, '..', 'risultati')
ESPERIMENTI_NEL_REGISTRO = 715
ALFA = 0.05


def carica(n):
    return json.load(open(os.path.join(RISULTATI, n), encoding='utf-8'))


def p_da_z(z):
    return math.erfc(abs(z) / math.sqrt(2))


def z_da_ic(stima, ic):
    sd = (ic[1] - ic[0]) / (2 * 1.96)
    return stima / sd


def prove():
    e386 = carica('e386_salto_disegno.json')['tipi']
    e380 = carica('e380_sandhi.json')['parte2']
    e3a02 = carica('e3a02_chi_si_adatta_2.json')
    e389 = carica('e389_varianti_bordo.json')
    e340 = carica('e340_autocitazione.json')['testi']['Voynich']
    e3a33 = carica('e3a33_margine_corretto.json')['per_inizio']
    e3c86 = carica('e3c86_intervalli_bifoglio.json')['misure']
    e314 = carica('e314_bifogli.json')
    pp = lambda p: max(p, 1e-4)
    F = OrderedDict()
    F['giuntura e raccordo'] = [
        ('giuntura E fra parole vicine (e386)', 'z', e386['spazio normale']['z']),
        ('qo-/o- davanti ai gallows secondo la parola prima (e380)', 'z', e380['qo-/o- davanti a gallows']['z']),
        ('-l/-r secondo la parola dopo (e380)', 'z', e380['-l/-r finale']['z']),
        ('sguardo avanti: cambia la fine della prima parola (e3a02 A)', 'p', pp(e3a02['parte_A']['cambia_a']['p'])),
        ('sguardo avanti: si adatta la parola dopo (e3a02 B)', 'p', pp(e3a02['parte_B']['cambia_b']['p']))]
    F['bordi della riga'] = [
        ('-m a fine riga (e389)', 'z', e389['fine riga']['segni']['m']['z']),
        ('-r cala a fine riga (e389)', 'z', e389['fine riga']['segni']['r']['z']),
        ('y- a inizio riga (e389)', 'z', e389['inizio riga']['segni']['y']['z']),
        ('s- a inizio riga (e389)', 'z', e389['inizio riga']['segni']['s']['z'])]
    F['copia dalla riga sopra'] = [('parola uguale o quasi nelle due righe sopra, oltre il lessico del paragrafo (e340)', 'z', e340['z_E1p'])]
    F['margine sinistro'] = [('inizio %s evitato sotto lo stesso inizio (e3a33)' % k, 'z', e3a33[k]['z']) for k in ('qo', 'o', 'd', 'ch', 'y')]
    F['stato breve'] = [('K accanto (e3c86, per bifoglio)', 'z', z_da_ic(e3c86['stato breve K1']['valore'], e3c86['stato breve K1']['bifoglio']['IC95'])),
                        ('K a 2–3 parole (e3c86, per bifoglio)', 'z', z_da_ic(e3c86['stato breve K2-3']['valore'], e3c86['stato breve K2-3']['bifoglio']['IC95']))]
    F['deriva lungo la riga'] = [('deriva %s (e3c86, per bifoglio)' % k, 'z', z_da_ic(e3c86['deriva %s' % k]['valore'], e3c86['deriva %s' % k]['bifoglio']['IC95']))
                                 for k in ('qo/o', 'k/t', 'sh/ch', '-ey/-dy')]
    F['struttura del libro'] = [('identità di bifoglio (e314)', 'z', e314['e314']['a']['bifoglio']['z']),
                                ('lingue A e B: parola chedy (e315)', 'z', e314['e315']['prime_20'][0]['z'])]
    return F


def holm(ps):
    ordine = sorted(range(len(ps)), key=lambda i: ps[i])
    agg, m, prec = [0.0] * len(ps), len(ps), 0.0
    for r, i in enumerate(ordine):
        prec = max(prec, min(1.0, (m - r) * ps[i]))
        agg[i] = prec
    return agg


def main():
    F = prove()
    soglia_b = ALFA / ESPERIMENTI_NEL_REGISTRO
    out = OrderedDict()
    for fam, lista in F.items():
        ps = [p_da_z(v) if t == 'z' else v for _, t, v in lista]
        ph = holm(ps)
        out[fam] = [OrderedDict([('prova', n), ('statistica', '%s = %.4g' % (t, v)), ('p', p), ('p_Holm', h),
                                 ('regge_Holm', h < ALFA), ('regge_Bonferroni_715', p < soglia_b)]) for (n, t, v), p, h in zip(lista, ps, ph)]
    tutte = [x for v in out.values() for x in v]
    esito = OrderedDict([('prove', len(tutte)), ('reggono_Holm', sum(x['regge_Holm'] for x in tutte)),
                         ('reggono_Bonferroni_715', sum(x['regge_Bonferroni_715'] for x in tutte)),
                         ('non_reggono_Bonferroni_715', [x['prova'] for x in tutte if not x['regge_Bonferroni_715']])])
    json.dump(OrderedDict([('famiglie', out), ('soglia_Bonferroni', soglia_b), ('esito', esito)]),
              open(os.path.join(RISULTATI, 'e3c92_confronti_multipli.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3c92 — Confronti multipli: le prove principali con Holm per famiglia e Bonferroni su 715 esperimenti', '',
          'Preregistrazione: `preregistrazioni/e3c92.md`. Soglia di Bonferroni: p < %.1e (|z| > %.2f).' % (soglia_b, -_qnorm(soglia_b / 2)), '',
          '| famiglia | prova | statistica | p | p di Holm | regge (Holm) | regge (Bonferroni 715) |', '|---|---|---|---|---|---|---|']
    for fam, lista in out.items():
        for x in lista:
            md.append('| %s | %s | %s | %.1e | %.1e | %s | %s |' % (fam, x['prova'], x['statistica'], x['p'], x['p_Holm'], 'sì' if x['regge_Holm'] else 'no', 'sì' if x['regge_Bonferroni_715'] else 'no'))
    md += ['', 'Esito: %d prove; reggono con Holm %d; con Bonferroni su 715 esperimenti %d. Non reggono a Bonferroni: %s.' % (
        esito['prove'], esito['reggono_Holm'], esito['reggono_Bonferroni_715'], '; '.join(esito['non_reggono_Bonferroni_715']) or 'nessuna')]
    open(os.path.join(RISULTATI, 'e3c92_confronti_multipli.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(json.dumps(esito, ensure_ascii=False, indent=1))


def _qnorm(p):
    # inversa della normale standard (Acklam), solo per stampare la soglia in z
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    q = math.sqrt(-2 * math.log(p))
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


if __name__ == '__main__':
    main()
