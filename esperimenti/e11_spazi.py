# -*- coding: utf-8 -*-
"""Esperimento 11: gli spazi del Voynich separano davvero delle parole?

Due misure, sul Voynich, sulle lingue e sui testi cifrati col Naibbe.

1. Quanto si puo' prevedere lo spazio dal segno che lo precede (o dai due
   segni). Nelle lingue una parola puo' finire con molte lettere diverse, e le
   stesse lettere stanno anche dentro le parole: lo spazio e' poco prevedibile.
   Se nel Voynich certi segni stanno quasi solo a fine parola, lo spazio e'
   una regola di scrittura, come le forme finali di certe lettere.

2. Il legame attraverso lo spazio: quanto l'ultimo segno di una parola dice
   sul primo della successiva, oltre il caso (parole rimescolate dentro la
   riga), usando solo le parole interne della riga, perche' la prima e
   l'ultima di ogni riga del Voynich hanno forme proprie. Lo confrontiamo con
   il legame fra due segni consecutivi dentro la stessa parola: se il legame
   attraverso lo spazio si avvicina a quello interno, lo spazio non separa
   unita' indipendenti.

Scrive risultati/e11_spazi.json e risultati/e11_spazi.md.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
NAIBBE = os.environ.get('NAIBBE', os.path.join(lingue.SORGENTI, 'naibbe-cipher'))
N = 35000


def interno(righe, dividi=None):
    """Informazione mutua fra due segni consecutivi dentro la stessa parola."""
    coppie = []
    for r in righe:
        for p in r:
            u = dividi(p) if dividi else list(p)
            coppie += list(zip(u, u[1:]))
    return misure.informazione_mutua(coppie)


def misura(righe, dividi=None):
    s1 = misure.spazi(righe, dividi, 1)
    s2 = misure.spazi(righe, dividi, 2)
    c = misure.confine(righe, dividi, solo_interne=True)
    i = interno(righe, dividi)
    return {'spazio_spiegato_1': s1['spiegata'], 'spazio_spiegato_2': s2['spiegata'],
            'quota_spazi': s1['quota_spazi'], 'confine': c['im_confine_eccesso'],
            'interno': i, 'confine_su_interno': c['im_confine_eccesso'] / i}


def coppie_sopra_il_caso(righe, dividi, n=15, semi=0):
    """Le coppie (fine parola, inizio parola seguente) piu' in eccesso rispetto
    alle parole rimescolate dentro la riga (parole interne)."""
    u = [[tuple(dividi(p)) for p in r][1:-1] for r in righe if len(r) > 3]
    vere = Counter((a[-1], b[0]) for r in u for a, b in zip(r, r[1:]))
    rnd = random.Random(semi)
    attese = Counter()
    for _ in range(20):
        for r in u:
            m = rnd.sample(r, len(r))
            attese.update((a[-1], b[0]) for a, b in zip(m, m[1:]))
    out = []
    for k, v in vere.items():
        e = attese[k] / 20
        if v >= 30 and e > 0:
            out.append((v / e, k, v, e))
    out.sort(reverse=True)
    return [{'fine': k[0], 'inizio': k[1], 'osservate': v, 'attese': round(e, 1), 'rapporto': round(x, 2)}
            for x, k, v, e in out[:n]], \
           [{'fine': k[0], 'inizio': k[1], 'osservate': v, 'attese': round(e, 1), 'rapporto': round(x, 2)}
            for x, k, v, e in sorted(out)[:n]]


def main():
    glifi_div = misure.divisore(misure.GLIFI_EVA)
    ris = OrderedDict()
    for q, nome, div in [('ZL', 'Voynich (Zandbergen-Landini, glifi)', glifi_div),
                         ('IT', 'Voynich (Takahashi, glifi)', glifi_div),
                         ('GC', 'Voynich (Glen Claston, v101)', None)]:
        righe = trascrizione.righe_di_parole(trascrizione.testo_corrente(trascrizione.leggi(q)))
        ris[nome] = misura(righe, div)
        stampa(nome, ris[nome])
    righe_zl = trascrizione.righe_di_parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    ufficiale = open(os.path.join(NAIBBE, 'encrypted', 'nathist_output_ciphertext.txt'), encoding='utf-8').read().split()
    ris['Naibbe (cifrato ufficiale, Plinio XVI)'] = misura(misure.a_blocchi(ufficiale, 8), glifi_div)
    stampa('Naibbe ufficiale', ris['Naibbe (cifrato ufficiale, Plinio XVI)'])
    nat = OrderedDict()
    for nome in lingue.GENERI:
        nat[nome] = misura(misure.a_blocchi(lingue.genere(nome), 8))
    for chiave, meta in sorted(lingue.indice().items()):
        if meta['tipo_scrittura'] not in ('alfabeto', 'abjad') or chiave.endswith('-tok'):
            continue
        parole = lingue.parole(chiave)[:N]
        if len(parole) == N:
            nat['Bibbia: ' + meta['lingua']] = misura(misure.a_blocchi(parole, 8))
    su, giu = coppie_sopra_il_caso(righe_zl, glifi_div)
    with open(os.path.join(RISULTATI, 'e11_spazi.json'), 'w', encoding='utf-8') as f:
        json.dump({'voynich_e_cifrati': ris, 'naturali': nat, 'coppie_in_eccesso': su,
                   'coppie_in_difetto': giu}, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris, nat, su, giu)


def stampa(nome, r):
    print('%-42s spazio spiegato %.0f%% / %.0f%%  confine %.3f  interno %.3f  rapporto %.1f%%' % (
        nome, 100 * r['spazio_spiegato_1'], 100 * r['spazio_spiegato_2'], r['confine'], r['interno'],
        100 * r['confine_su_interno']))


def scrivi_tabella(ris, nat, su, giu):
    def intervallo(chiave, perc=False):
        v = sorted(r[chiave] for r in nat.values())
        f = (lambda x: '%.0f%%' % (100 * x)) if perc else (lambda x: '%.3f' % x)
        return '%s – %s (mediana %s)' % (f(v[0]), f(v[-1]), f(v[len(v) // 2]))
    out = ['# Esperimento 11: gli spazi', '',
           '- **spazio spiegato**: quanta dell\'incertezza su "qui viene uno spazio?" sparisce sapendo il '
           'segno precedente (o i due segni precedenti).',
           '- **confine**: quanto l\'ultimo segno di una parola dice sul primo della successiva, oltre il '
           'caso; solo parole interne alla riga (bit).',
           '- **interno**: lo stesso fra due segni consecutivi dentro una parola (bit).',
           '- **rapporto**: confine diviso interno.', '',
           '| testo | spazio spiegato (1 segno) | (2 segni) | confine | interno | rapporto |',
           '|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %.0f%% | %.0f%% | %.3f | %.3f | %.1f%% |' % (
            nome, 100 * r['spazio_spiegato_1'], 100 * r['spazio_spiegato_2'], r['confine'], r['interno'],
            100 * r['confine_su_interno']))
    out.append('| %d testi naturali, intervallo | %s | %s | %s | %s | %s |' % (
        len(nat), intervallo('spazio_spiegato_1', True), intervallo('spazio_spiegato_2', True),
        intervallo('confine'), intervallo('interno'), intervallo('confine_su_interno', True)))
    out += ['', '## Nel Voynich: fine parola → inizio della parola seguente', '',
            'Coppie più frequenti del caso (parole interne, rimescolate dentro la riga 20 volte):', '',
            '| fine | inizio | osservate | attese | × |', '|---|---|---|---|---|']
    out += ['| %s | %s | %d | %.1f | %.2f |' % (c['fine'], c['inizio'], c['osservate'], c['attese'], c['rapporto'])
            for c in su]
    out += ['', 'Coppie più rare del caso:', '', '| fine | inizio | osservate | attese | × |', '|---|---|---|---|---|']
    out += ['| %s | %s | %d | %.1f | %.2f |' % (c['fine'], c['inizio'], c['osservate'], c['attese'], c['rapporto'])
            for c in giu]
    with open(os.path.join(RISULTATI, 'e11_spazi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
