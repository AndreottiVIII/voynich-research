# -*- coding: utf-8 -*-
"""Esperimento 20: i gruppi di segni a ogni grado di fusione.

Nell'esperimento 17 i gruppi di segni imparati dal testo hanno due gradi, 20 e
50 fusioni. Ma il cifrario verboso di prova si legge solo col grado giusto:
con 50 fusioni si', con 20 no. Se il Voynich fosse un cifrario verboso con un
numero di gruppi diverso, i due gradi potrebbero mancarlo. Qui si provano
nove gradi fra 10 e 150 fusioni, in latino e in italiano, e a ogni grado anche
un cifrario verboso di prova dello stesso tipo (in latino, con una sua chiave):
cosi' si vede per quali gradi il metodo lo rompe e se in quei gradi, o in
altri, il Voynich si legge.

Per ogni lingua e grado: controllo positivo e negativo con lo stesso numero di
simboli e la stessa lunghezza del Voynich letto a quel grado, come
nell'esperimento 17.

Scrive risultati/e20_gradi.json e .md; con --grafico il grafico.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import lingue, misure
import e17_ricottura as e17

RISULTATI = os.path.join(QUI, '..', 'risultati')
GRADI = (10, 20, 30, 40, 50, 60, 80, 100, 150)
LINGUE = OrderedDict([('Latin', 'latino'), ('Italian', 'italiano')])
RIPARTENZE = int(os.environ.get('RIPARTENZE', '3'))


def voynich_a_grado(fusioni):
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl = e17.righe_voynich('ZL')
    parole_zl = [glifi(p) for r in zl for p in r if p]
    return e17.in_unita(zl, e17.applica_gruppi(e17.impara_gruppi(parole_zl, fusioni), glifi))


def verboso_a_grado(fusioni, lettere, testo, add, lunghezza):
    """Un cifrario verboso di prova dello stesso tipo di quello dell'esperimento
    17 (con una sua chiave), lungo quanto il Voynich in segni EVA e letto a
    gruppi con il grado dato."""
    rnd = random.Random('e20-verboso')
    chiave = e17.cifrario_verboso(lettere, rnd)
    prova, n = [], 0
    for p in testo[add + 60000:]:
        prova.append(p)
        n += 2 * len(p)
        if n >= lunghezza:
            break
    righe = e17.in_righe(prova)
    righe_cif = [[''.join(''.join(rnd.choice(chiave[c])) for c in p) for p in riga] for riga in righe]
    glifi = misure.divisore(misure.GLIFI_EVA)
    parole_cif = [glifi(p) for riga in righe_cif for p in riga]
    return e17.in_unita(righe_cif, e17.applica_gruppi(e17.impara_gruppi(parole_cif, fusioni), glifi))


def un_lavoro(argomenti):
    chiave_l, nome, fusioni = argomenti
    rnd = random.Random('e20-%s-%d' % (chiave_l, fusioni))
    testo, add, lettere, modello, lessico = e17.prepara_lingua(chiave_l)
    altra = e17.STRANIERO
    altro = lingue.parole(altra)
    altro = e17.pulisci(altro, e17.alfabeto(altro))
    voy = voynich_a_grado(fusioni)
    simboli, L = len({u for x in voy for u in x}), sum(map(len, voy))
    r = OrderedDict([('simboli', simboli), ('lunghezza', L)])
    cif, vera = e17.cifra_abbinata(e17.in_righe(e17.prendi(testo[add:], L)), simboli, rnd)
    r['controllo positivo'] = e17.attacca(cif, modello, lessico, rnd, vera=vera, ripartenze=RIPARTENZE)
    cif, _ = e17.cifra_abbinata(e17.in_righe(e17.prendi(altro, L)), simboli, rnd)
    r['controllo negativo'] = e17.attacca(cif, modello, lessico, rnd, ripartenze=RIPARTENZE)
    r['Voynich'] = e17.attacca(voy, modello, lessico, rnd, ripartenze=RIPARTENZE)
    if chiave_l == 'Latin':
        lung_eva = sum(map(len, e17.modi_voynich()['segni EVA']))
        r['cifrario verboso'] = e17.attacca(verboso_a_grado(fusioni, lettere, testo, add, lung_eva), modello,
                                            lessico, rnd, ripartenze=RIPARTENZE)
    for k in ('controllo positivo', 'controllo negativo', 'Voynich', 'cifrario verboso'):
        if k in r:
            e17.stampa(nome, '%d fusioni, %s' % (fusioni, k), r[k])
    return nome, fusioni, r


def posizione(r, chiave='Voynich'):
    pos, neg = r['controllo positivo']['punteggio'], r['controllo negativo']['punteggio']
    return (r[chiave]['punteggio'] - neg) / (pos - neg)


def riuscito(r):
    """Il controllo positivo e' riuscito: solo allora la posizione vuol dire qualcosa."""
    return r['controllo positivo'].get('chiave_giusta', 0) >= 0.9


def main():
    lavori = [(k, n, f) for f in GRADI for k, n in LINGUE.items()]
    ris = OrderedDict((n, OrderedDict()) for n in LINGUE.values())
    percorso = os.path.join(RISULTATI, 'e20_gradi.json')
    with Pool(int(os.environ.get('PROCESSI', '4'))) as pool:
        for nome, fusioni, r in pool.imap_unordered(un_lavoro, lavori):
            ris[nome][str(fusioni)] = r
            with open(percorso, 'w', encoding='utf-8') as f:
                json.dump(ris, f, ensure_ascii=False, indent=1)
    for nome in ris:
        ris[nome] = OrderedDict(sorted(ris[nome].items(), key=lambda x: int(x[0])))
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def scrivi_tabella(ris):
    out = ['# Esperimento 20: i gruppi di segni a ogni grado di fusione', '',
           'Per ogni grado: il Voynich letto a gruppi (vedi esperimento 17), con controllo positivo e negativo '
           'dello stesso numero di simboli e della stessa lunghezza. **Posizione**: dove cade il punteggio fra il '
           'controllo negativo (0) e il positivo (1). In latino anche il cifrario verboso di prova, letto a gruppi '
           'con lo stesso grado. Dove il controllo positivo non riesce (chiave sotto il 90%) la posizione non vuol '
           'dire niente, e nel grafico non c\'è.', '',
           '| lingua | fusioni | gruppi | chiave (positivo) | punteggio positivo / Voynich / negativo | '
           'posizione del Voynich | copertura 6+ (positivo / Voynich / negativo) | cifrario verboso: posizione |',
           '|---|---|---|---|---|---|---|---|']
    for nome, gradi in ris.items():
        for f, r in gradi.items():
            out.append('| %s | %s | %d | %.0f%% | %.2f / %.2f / %.2f | %.2f | %.0f%% / %.0f%% / %.0f%% | %s |' % (
                nome, f, r['simboli'], 100 * r['controllo positivo']['chiave_giusta'],
                r['controllo positivo']['punteggio'], r['Voynich']['punteggio'], r['controllo negativo']['punteggio'],
                posizione(r), 100 * r['controllo positivo']['copertura_6'], 100 * r['Voynich']['copertura_6'],
                100 * r['controllo negativo']['copertura_6'],
                '%.2f' % posizione(r, 'cifrario verboso') if 'cifrario verboso' in r else '–'))
    with open(os.path.join(RISULTATI, 'e20_gradi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    import grafici
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.13)
        ax.axhline(1, color=t['muto'], linewidth=1.2, zorder=1)
        ax.axhline(0, color=t['muto'], linewidth=1.2, zorder=1)
        lat = ris['latino']
        xs = [int(f) for f in lat if 'cifrario verboso' in lat[f] and riuscito(lat[f])]
        ax.plot(xs, [posizione(lat[str(f)], 'cifrario verboso') for f in xs], color=t['inchiostro'],
                linewidth=1.4, marker='D', markersize=4, label='cifrario verboso di prova (latino)', zorder=2)
        forme = {'latino': 'o', 'italiano': 's'}
        for nome, gradi in ris.items():
            fs = [int(f) for f in gradi if riuscito(gradi[f])]
            ax.plot(fs, [posizione(gradi[str(f)]) for f in fs], color=t['accento'], linewidth=1.2,
                    marker=forme.get(nome, 'o'), markersize=5, label='Voynich, ' + nome, zorder=3)
        ax.text(min(GRADI) * 1.04, 1.03, 'la lingua stessa, cifrata', ha='left', va='bottom', fontsize=8,
                color=t['secondario'])
        ax.text(min(GRADI) * 1.04, 0.03, 'un\'altra lingua, cifrata', ha='left', va='bottom', fontsize=8,
                color=t['secondario'])
        ax.set_xscale('log')
        ax.set_xticks(list(GRADI))
        ax.set_xticklabels([str(g) for g in GRADI])
        ax.minorticks_off()
        ax.set_ylim(-0.6, 1.3)
        ax.set_xlabel('fusioni (più fusioni = gruppi più lunghi e più numerosi)')
        ax.set_ylabel('posizione fra negativo (0) e positivo (1)')
        ax.legend(loc='center left', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, TITOLO, SOTTOTITOLO)
        grafici.salva(fig, RISULTATI, 'e20_gradi', tema)


TITOLO = 'Il Voynich a gruppi di segni, a ogni grado'
SOTTOTITOLO = ('Il cifrario verboso di prova si legge quando i gruppi sono quelli giusti.\n'
               'Il Voynich, a qualsiasi grado, resta dove sta un testo in un\'altra lingua.')


if __name__ == '__main__':
    if '--grafico' in sys.argv or '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e20_gradi.json'), encoding='utf-8') as f:
            ris = json.load(f, object_pairs_hook=OrderedDict)
        (disegna if '--grafico' in sys.argv else scrivi_tabella)(ris)
    else:
        main()
