# -*- coding: utf-8 -*-
"""Esperimento 7: un testo vero, codificato, puo' sembrare il Voynich?

L'ipotesi "tokenizzata" in pratica: le unita' del Voynich non sono lettere ma
pezzi piu' grandi (gruppi di glifi per una lettera, codici per una parola,
sillabe). Prendiamo tre testi veri (Vitruvio per il latino tecnico, la Bibbia
latina e quella italiana), li codifichiamo in quattro modi e misuriamo il
risultato con gli stessi strumenti usati per il Voynich:

- cifrario verboso: il migliore di 300 tentativi nel riprodurre h2 e lunghezza
  delle parole del Voynich;
- codice parola per parola: ogni parola diventa la parola del Voynich di pari
  rango di frequenza (cosi' le lettere sono proprio quelle del Voynich);
- codice con varianti: come sopra, ma ogni parola ha piu' codici (piu' e'
  frequente, piu' ne ha) e se ne sceglie uno a caso;
- sillabe come parole: ogni sillaba diventa una parola del Voynich;
- codice con stile di pagina: il codice parola per parola, scritto da uno
  scriba che a ogni pagina cambia abitudini (ch->sh, k->t, q in testa...).

Scrive risultati/e07_codifiche.json e risultati/e07_codifiche.md.
"""
import json, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import generatori, lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 35000
N_TIPI = 30000


def pagine_voynich(corrente):
    pagine = OrderedDict()
    for r in corrente:
        ps = [p for p in r.parole if trascrizione.pulita(p)]
        if ps:
            pagine.setdefault(r.pagina, []).append(ps)
    return list(pagine.values())


def impronta(pagine, dividi):
    """Le misure che contano, su un testo gia' diviso in pagine e righe."""
    righe = [riga for pag in pagine for riga in pag]
    parole = [p for riga in righe for p in riga]
    vic = misure.vicinato(righe, dividi)
    dec = misure.decadimento(pagine, dividi, coppie_caso=100000, distanze=[0, 1, 6])
    tipi = Counter(parole[:N_TIPI])
    return {
        'parole': len(parole),
        'h2': misure.condizionate(misure.sequenza(parole, dividi), k_max=2)['h2'],
        'lung_media': sum(len(dividi(p)) if dividi else len(p) for p in parole) / len(parole),
        'tipi_su_parole': len(tipi) / min(N_TIPI, len(parole)),
        'hapax': sum(1 for c in tipi.values() if c == 1) / len(tipi),
        'identiche_immediate': sum(1 for r in righe for a, b in zip(r, r[1:]) if a == b)
                               / sum(len(r) - 1 for r in righe),
        'identiche_vs_riga': vic['identiche_rapporto'],
        'somiglianza_riga': 1 - dec[0]['distanza'],
        'somiglianza_riga_sotto': 1 - dec[1]['distanza'],
        'somiglianza_6_righe': 1 - dec[6]['distanza'],
    }


def main():
    rnd = random.Random(1)
    glifi_div = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    glifi = [g for g, _ in Counter(u for p in parole_v for u in glifi_div(p)).most_common()]
    modello = generatori.ModelloParole(parole_v, glifi_div)
    modifiche = generatori.Modifiche(parole_v, glifi_div)
    ris = OrderedDict()
    ris['Voynich (pagine e righe vere)'] = impronta(pagine_voynich(corrente), glifi_div)
    ris['Voynich (righe finte da 8 parole)'] = impronta(misure.pagine_finte(parole_v), glifi_div)
    bersaglio = ris['Voynich (pagine e righe vere)']
    stampa('Voynich', bersaglio)

    testi = [('Vitruvio', lingue.genere('Vitruvio, architettura')[:N]),
             ('Bibbia latina', lingue.parole('Latin')[:N]),
             ('Bibbia italiana', lingue.parole('Italian')[:N])]
    tabelle = {}
    for nome, testo in testi:
        r = ris[nome + ': testo in chiaro'] = impronta(misure.pagine_finte(testo), None)
        stampa(nome + ' in chiaro', r)

        punti, tabella, h2, lung, singole = generatori.cerca_verboso(
            testo, glifi, rnd, bersaglio['h2'], bersaglio['lung_media'])
        tabelle[nome] = {'tabella': tabella, 'lettere_con_un_glifo': singole}
        cifrato = generatori.cifra_verboso(testo, tabella)
        r = ris[nome + ': cifrario verboso'] = impronta(misure.pagine_finte(cifrato), misure.divisore(glifi))
        stampa(nome + ' verboso', r)

        codificato = generatori.codice_per_rango(testo, parole_v, modello, rnd)
        r = ris[nome + ': codice parola per parola'] = impronta(misure.pagine_finte(codificato), glifi_div)
        stampa(nome + ' codice', r)

        varianti = lambda f: min(8, 1 + int(math.log2(f)))
        omofonico = generatori.codice_per_rango(testo, parole_v, modello, rnd, varianti)
        r = ris[nome + ': codice con varianti'] = impronta(misure.pagine_finte(omofonico), glifi_div)
        stampa(nome + ' varianti', r)

        for regole, forza in [(3, 0.7), (6, 0.9)]:
            stile = generatori.codice_con_stile(testo, parole_v, modello, modifiche, rnd,
                                                misure.PAROLE_RIGA * misure.RIGHE_PAGINA, regole, forza)
            chiave = nome + ': codice con stile di pagina (%d regole, forza %.1f)' % (regole, forza)
            r = ris[chiave] = impronta(misure.pagine_finte(stile), glifi_div)
            stampa(nome + ' stile %d/%.1f' % (regole, forza), r)

        sill = generatori.in_sillabe(testo)[:N]
        sill_cod = generatori.codice_per_rango(sill, parole_v, modello, rnd)
        r = ris[nome + ': sillabe come parole'] = impronta(misure.pagine_finte(sill_cod), glifi_div)
        stampa(nome + ' sillabe', r)

    with open(os.path.join(RISULTATI, 'e07_codifiche.json'), 'w', encoding='utf-8') as f:
        json.dump({'impronte': ris, 'cifrari_verbosi': tabelle}, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, r):
    print('%-34s h2 %.2f lung %.2f tipi %.3f hapax %.2f ident %.4f (x%.2f riga) somigl. %.1f%% / %.1f%% / %.1f%%' % (
        nome, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_immediate'],
        r['identiche_vs_riga'], 100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'],
        100 * r['somiglianza_6_righe']))


def scrivi_tabella(ris):
    out = ['# Esperimento 7: testi veri codificati', '',
           'Tre testi (35.000 parole) codificati in quattro modi, misurati come il Voynich. '
           'Per i testi artificiali: righe finte da 8 parole, pagine da 20 righe.', '',
           '- **h2**: incertezza sulla lettera (glifo) successiva, bit.',
           '- **lung.**: lunghezza media delle parole in glifi (lettere per i testi in chiaro).',
           '- **tipi/parole**, **hapax**: varietà del vocabolario sulle prime 30.000 parole.',
           '- **identiche subito**: quota di parole uguali alla precedente; tra parentesi, '
           'rispetto a due parole a caso della stessa riga.',
           '- **somiglianza**: quanto due parole diverse si somigliano più del caso, nella '
           'stessa riga, fra una riga e quella sotto, a sei righe di distanza.', '',
           '| testo | h2 | lung. | tipi/parole | hapax | identiche subito | somiglianza: stessa riga | riga sotto | 6 righe sotto |',
           '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        grassetto = '**%s**' % nome if nome.startswith('Voynich') else nome
        out.append('| %s | %.2f | %.2f | %.3f | %.2f | %.2f%% (×%.2f) | %.1f%% | %.1f%% | %.1f%% |' % (
            grassetto, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'],
            100 * r['identiche_immediate'], r['identiche_vs_riga'], 100 * r['somiglianza_riga'],
            100 * r['somiglianza_riga_sotto'], 100 * r['somiglianza_6_righe']))
    with open(os.path.join(RISULTATI, 'e07_codifiche.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def compromesso_verboso(prove=150):
    """Il prezzo del cifrario verboso: per abbassare h2 servono piu' lettere
    scritte con due glifi, e ogni lettera a due glifi allunga le parole. Qui
    si provano cifrari a caso, con qualsiasi numero di lettere a un glifo, su
    tre testi, e si guarda dove finiscono rispetto al Voynich."""
    rnd = random.Random(7)
    glifi_div = misure.divisore(misure.GLIFI_EVA)
    parole_v = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    glifi = [g for g, _ in Counter(u for p in parole_v for u in glifi_div(p)).most_common()]
    dividi = misure.divisore(glifi)
    punti = []
    for nome, testo in [('Vitruvio', lingue.genere('Vitruvio, architettura')[:15000]),
                        ('Bibbia latina', lingue.parole('Latin')[:15000]),
                        ('Bibbia italiana', lingue.parole('Italian')[:15000])]:
        lettere = [c for c, _ in Counter(''.join(testo)).most_common()]
        singoli = glifi[:20]
        coppie = [a + b for a in glifi[:12] for b in glifi[:12]]
        for _ in range(prove):
            k = rnd.randint(0, min(len(lettere), len(singoli)))
            s, c = rnd.sample(singoli, k), rnd.sample(coppie, len(lettere) - k)
            tabella = {l: (s[i] if i < k else c[i - k]) for i, l in enumerate(lettere)}
            cifrato = generatori.cifra_verboso(testo, tabella)
            h2 = misure.condizionate(misure.sequenza(cifrato, dividi), k_max=2)['h2']
            lung = sum(len(dividi(p)) for p in cifrato) / len(cifrato)
            punti.append({'testo': nome, 'lettere_a_un_glifo': k, 'h2': h2, 'lung_media': lung})
    voy = misure.condizionate(misure.sequenza(parole_v, glifi_div), k_max=2)['h2']
    voy_lung = sum(len(glifi_div(p)) for p in parole_v) / len(parole_v)
    ris = {'cifrari': punti, 'voynich': {'h2': voy, 'lung_media': voy_lung}}
    with open(os.path.join(RISULTATI, 'e07_compromesso_verboso.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    vicini = [p for p in punti if p['h2'] <= voy + 0.15]
    if vicini:
        print('cifrari con h2 entro 0.15 dal Voynich: %d; lunghezza minima %.2f (Voynich %.2f)' % (
            len(vicini), min(p['lung_media'] for p in vicini), voy_lung))
    else:
        print('nessun cifrario arriva entro 0.15 bit dall\'h2 del Voynich; minimo %.2f' % min(p['h2'] for p in punti))
    disegna_compromesso(ris)


def disegna_compromesso(ris):
    import grafici
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.09, right=0.97, top=0.80, bottom=0.12)
        cif = ris['cifrari']
        ax.scatter([p['lung_media'] for p in cif], [p['h2'] for p in cif], s=26,
                   color=t['contesto'], edgecolor=t['sfondo'], linewidth=1.0,
                   label='cifrari verbosi di latino e italiano (450 prove)', zorder=2)
        v = ris['voynich']
        ax.scatter([v['lung_media']], [v['h2']], s=70, color=t['accento'], edgecolor=t['sfondo'],
                   linewidth=1.5, label='Voynich', zorder=3)
        ax.annotate('Voynich', (v['lung_media'], v['h2']), xytext=(9, -3), textcoords='offset points',
                    fontsize=9, color=t['inchiostro'])
        ax.set_xlabel('lunghezza media delle parole cifrate (glifi)')
        ax.set_ylabel('h2: incertezza sul glifo successivo (bit)')
        ax.legend(loc='upper right', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Il cifrario verboso non arriva al Voynich',
                       'Scrivere le lettere con due glifi rende il testo più prevedibile, ma allunga le parole.\n'
                       'Nessuna combinazione ha insieme la prevedibilità e le parole corte del Voynich.')
        grafici.salva(fig, RISULTATI, 'e07_compromesso_verboso', tema)


if __name__ == '__main__':
    if '--compromesso' in sys.argv:
        compromesso_verboso()
    else:
        main()
        compromesso_verboso()
