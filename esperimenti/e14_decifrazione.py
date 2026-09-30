# -*- coding: utf-8 -*-
"""Esperimento 14: un tentativo di decifrazione, con i controlli.

Ipotesi: ogni segno del Voynich sta per una lettera di una lingua nota (piu'
segni possono valere la stessa lettera), e gli spazi separano le parole. Per
ogni lingua candidata si cerca la chiave che rende le parole del Voynich piu'
simili a parole di quella lingua (analisi/decifra.py).

Perche' il risultato voglia dire qualcosa servono tre confronti.
- Controllo positivo: un altro pezzo della stessa lingua, cifrato con una
  chiave omofonica casuale, decifrato con lo stesso codice. Se il metodo non lo
  rompe, un esito negativo sul Voynich non dice niente.
- Controllo negativo: il testo di un'altra lingua, cifrato e "decifrato" come
  se fosse questa. Dice quante parole vere escono per caso da una chiave
  ottimizzata su un testo che non e' in quella lingua.
- Lo zodiaco: in ogni pagina dello zodiaco sappiamo mese e segno. Se una
  chiave fosse giusta, i loro nomi (anche con una lettera sbagliata)
  dovrebbero comparire nella pagina giusta piu' che nelle altre.

Scrive risultati/e14_decifrazione.json e risultati/e14_decifrazione.md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import decifra, lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
ADDESTRAMENTO = 250000     # parole della Bibbia per il modello della lingua
PROVA = 35000              # parole per i controlli, prese dopo

CANDIDATE = OrderedDict([
    ('Latin', 'latino'), ('Italian', 'italiano'), ('German', 'tedesco'), ('English', 'inglese'),
    ('French', 'francese'), ('Spanish', 'spagnolo'), ('Czech', 'ceco'), ('Hungarian', 'ungherese'),
    ('Greek', 'greco'), ('Hebrew', 'ebraico'), ('Arabic', 'arabo'), ('Turkish', 'turco'),
    ('Malagasy', 'malgascio'), ('Potawatomi-PART', 'potawatomi'), ('Chinantec-NT', 'chinanteco'),
])

# Zodiaco: pagina -> (mese, segno) secondo le note della trascrizione ZL
ZODIACO = OrderedDict([
    ('f70v2', (3, 'pesci')), ('f70v1', (4, 'ariete')), ('f71r', (4, 'ariete')),
    ('f71v', (5, 'toro')), ('f72r1', (5, 'toro')), ('f72r2', (6, 'gemelli')),
    ('f72r3', (7, 'cancro')), ('f72v3', (8, 'leone')), ('f72v2', (9, 'vergine')),
    ('f72v1', (10, 'bilancia')), ('f73r', (11, 'scorpione')), ('f73v', (12, 'sagittario')),
])
SEGNI = ['ariete', 'toro', 'gemelli', 'cancro', 'leone', 'vergine', 'bilancia', 'scorpione',
         'sagittario', 'pesci']
NOMI = {   # mesi da marzo a dicembre, poi i segni nell'ordine di SEGNI
    'Latin': (['martius', 'aprilis', 'maius', 'iunius', 'iulius', 'augustus', 'september',
               'october', 'november', 'december'],
              ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpius',
               'sagittarius', 'pisces']),
    'Italian': (['marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre',
                 'novembre', 'dicembre'],
                ['ariete', 'toro', 'gemelli', 'cancro', 'leone', 'vergine', 'bilancia', 'scorpione',
                 'sagittario', 'pesci']),
    'German': (['märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november',
                'dezember'],
               ['widder', 'stier', 'zwillinge', 'krebs', 'löwe', 'jungfrau', 'waage', 'skorpion',
                'schütze', 'fische']),
    'French': (['mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre',
                'décembre'],
               ['bélier', 'taureau', 'gémeaux', 'cancer', 'lion', 'vierge', 'balance', 'scorpion',
                'sagittaire', 'poissons']),
    'Spanish': (['marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
                 'noviembre', 'diciembre'],
                ['aries', 'tauro', 'géminis', 'cáncer', 'leo', 'virgo', 'libra', 'escorpio',
                 'sagitario', 'piscis']),
    'English': (['march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november',
                 'december'],
                ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio',
                 'sagittarius', 'pisces']),
}

GLIFI_I = misure.GLIFI_EVA + ['iiin', 'iin', 'in', 'iiir', 'iir', 'ir']


def vicino(a, b):
    """Stesso nome, o al massimo una lettera diversa per i nomi di 5 lettere o piu'."""
    if a == b:
        return True
    return len(b) >= 5 and abs(len(a) - len(b)) <= 1 and misure.distanza(a, b) <= 1


def prova_zodiaco(chiave, cif, lingua, nomi, zl):
    """Pagine dello zodiaco in cui compare il nome giusto (mese o segno), e
    quante volte compaiono invece nomi di altri mesi o segni."""
    mesi, segni = nomi
    giuste = sbagliate = 0
    dettaglio = []
    for pagina, (mese, segno) in ZODIACO.items():
        parole = [p for r in zl if r.pagina == pagina for p in r.parole if trascrizione.pulita(p)]
        dec = {decifra.decifra_parola(p, chiave, cif, lingua) for p in parole}
        attesi = {mesi[mese - 3], segni[SEGNI.index(segno)]}
        altri = (set(mesi) | set(segni)) - attesi
        trovati = sorted(n for n in attesi if any(vicino(d, n) for d in dec))
        estranei = sorted(n for n in altri if any(vicino(d, n) for d in dec))
        giuste += bool(trovati)
        sbagliate += len(estranei)
        dettaglio.append({'pagina': pagina, 'trovati': trovati, 'nomi_di_altre_pagine': estranei})
    return {'pagine_con_nome_giusto': giuste, 'nomi_fuori_posto': sbagliate, 'pagine': dettaglio}


def main():
    rnd = random.Random(2026)
    zl = trascrizione.leggi('ZL')
    corrente = trascrizione.testo_corrente(zl)
    righe_v = trascrizione.righe_di_parole(corrente)
    parole_v = [p for r in righe_v for p in r]
    ris = OrderedDict()
    straniero = {'Latin': 'Italian'}   # per il controllo negativo; per le altre: il latino
    for chiave_l, nome in CANDIDATE.items():
        testo = lingue.parole(chiave_l)
        if len(testo) < ADDESTRAMENTO // 5:
            print('%s: testo troppo corto' % nome)
            continue
        add = min(ADDESTRAMENTO, int(len(testo) * 0.8))
        lingua = decifra.Lingua(testo[:add])
        r = ris[nome] = OrderedDict()
        # controllo positivo
        prova = testo[add:add + PROVA]
        cifrato, _ = decifra.cifra_omofonico(prova, rnd)
        cif = decifra.Cifrato(cifrato, decifra.dividi_unita)
        _, k = decifra.cerca(cif, lingua, rnd)
        r['controllo positivo'] = decifra.valuta(misure.a_blocchi(cifrato, 8), k, cif, lingua, rnd)
        # controllo negativo
        altro = lingue.parole(straniero.get(chiave_l, 'Latin'))[:PROVA]
        cifrato, _ = decifra.cifra_omofonico(altro, rnd)
        cif = decifra.Cifrato(cifrato, decifra.dividi_unita)
        _, k = decifra.cerca(cif, lingua, rnd)
        r['controllo negativo'] = decifra.valuta(misure.a_blocchi(cifrato, 8), k, cif, lingua, rnd)
        # il Voynich, con due modi di contare i segni
        for etichetta, unita in (('Voynich, glifi', misure.GLIFI_EVA), ('Voynich, glifi e serie di i', GLIFI_I)):
            cif = decifra.Cifrato(parole_v, misure.divisore(unita))
            punti, k = decifra.cerca(cif, lingua, rnd)
            v = decifra.valuta(righe_v, k, cif, lingua, rnd)
            v['punteggio'] = punti
            v['chiave'] = {u: lingua.simboli[k[i]] for u, i in cif.indice.items()}
            v['esempio'] = [' '.join(decifra.decifra_parola(p, k, cif, lingua) for p in riga)
                            for riga in righe_v[:4]]
            if chiave_l in NOMI:
                v['zodiaco'] = prova_zodiaco(k, cif, lingua, NOMI[chiave_l], zl)
            r[etichetta] = v
        stampa(nome, r)
        with open(os.path.join(RISULTATI, 'e14_decifrazione.json'), 'w', encoding='utf-8') as f:
            json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, r):
    for k, v in r.items():
        z = v.get('zodiaco')
        print('%-11s %-34s parole vere %5.1f%% (%5d diverse, prime 3 %3.0f%%)  lunghe %5.1f%%  coppie %5.1f%% (mescolate %5.1f%%)%s' % (
            nome, k, 100 * v['parole_vere'], v['parole_vere_diverse'], 100 * v['quota_tre_piu_frequenti'],
            100 * v['parole_lunghe_vere'], 100 * v['coppie_attestate'],
            100 * v['coppie_attestate_mescolate'],
            '  zodiaco: %d pagine giuste, %d nomi fuori posto' % (z['pagine_con_nome_giusto'], z['nomi_fuori_posto'])
            if z else ''))


def scrivi_tabella(ris):
    out = ['# Esperimento 14: un tentativo di decifrazione', '',
           'Sostituzione omofonica (più segni possono valere la stessa lettera), spazi = spazi fra parole. '
           'Per ogni lingua: chiave cercata con un modello a trigrammi di lettere della Bibbia in quella lingua.', '',
           '- **parole vere**: quota delle parole decifrate che sono parole della lingua; **lunghe**: lo stesso '
           'per le parole di almeno 4 lettere.',
           '- **coppie**: quota delle coppie di parole vicine (entrambe vere) che la lingua usa davvero; fra '
           'parentesi lo stesso con le parole rimescolate nella riga. Se il testo ha senso, la prima è molto più alta.',
           '- **zodiaco**: pagine (su 12) in cui compare il nome del mese o del segno giusto; nomi di altri mesi '
           'o segni comparsi per sbaglio.', '',
           '- **diverse**: quante parole vere diverse escono; **prime 3**: quanta parte delle parole vere '
           'coprono le tre più frequenti. Una chiave degenere schiaccia tutto su poche parole ripetute.', '',
           '| lingua | testo | parole vere | diverse | prime 3 | lunghe | coppie (mescolate) | zodiaco |',
           '|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        for k, v in r.items():
            z = v.get('zodiaco')
            out.append('| %s | %s | %.1f%% | %d | %.0f%% | %.1f%% | %.1f%% (%.1f%%) | %s |' % (
                nome, k, 100 * v['parole_vere'], v['parole_vere_diverse'], 100 * v['quota_tre_piu_frequenti'],
                100 * v['parole_lunghe_vere'], 100 * v['coppie_attestate'],
                100 * v['coppie_attestate_mescolate'],
                '%d giuste, %d fuori posto' % (z['pagine_con_nome_giusto'], z['nomi_fuori_posto']) if z else '–'))
    out += ['', '## Come "legge" il Voynich la chiave migliore, per alcune lingue', '']
    for nome in ('latino', 'italiano', 'tedesco'):
        if nome in ris:
            v = ris[nome]['Voynich, glifi']
            out += ['**%s**:' % nome, '', '```'] + v['esempio'] + ['```', '']
    with open(os.path.join(RISULTATI, 'e14_decifrazione.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def controllo_naibbe():
    """Un secondo controllo negativo, fatto apposta per il Voynich: il Plinio
    cifrato col Naibbe e' latino vero ma con parole che valgono una o due
    lettere, cioe' un testo che ha senso ma non secondo il modello di questo
    attacco. Quanto 'legge' l'attacco su un testo cosi' dice quanto conta cio'
    che legge sul Voynich."""
    rnd = random.Random(7)
    percorso = os.path.join(RISULTATI, 'e14_decifrazione.json')
    with open(percorso, encoding='utf-8') as f:
        ris = json.load(f, object_pairs_hook=OrderedDict)
    naibbe = os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
    righe = [r.split() for r in open(naibbe, encoding='utf-8') if r.strip()]
    righe = [r[i:i + 8] for r in righe for i in range(0, len(r), 8)]
    parole = [p for r in righe for p in r]
    for chiave_l, nome in (('Latin', 'latino'), ('Italian', 'italiano')):
        testo = lingue.parole(chiave_l)
        lingua = decifra.Lingua(testo[:min(ADDESTRAMENTO, int(len(testo) * 0.8))])
        cif = decifra.Cifrato(parole, misure.divisore(misure.GLIFI_EVA))
        _, k = decifra.cerca(cif, lingua, rnd)
        v = decifra.valuta(righe, k, cif, lingua, rnd)
        v['esempio'] = [' '.join(decifra.decifra_parola(p, k, cif, lingua) for p in r) for r in righe[:3]]
        ris[nome]['controllo Naibbe (Plinio cifrato)'] = v
        stampa(nome, {'controllo Naibbe (Plinio cifrato)': v})
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def disegna(ris):
    """Per ogni lingua: quante parole vere diverse escono dalla chiave migliore,
    per il controllo positivo, il Voynich e il controllo negativo."""
    import grafici
    nomi = list(ris)
    serie = [('controllo positivo', 'testo vero cifrato e decifrato', 'accento_s'),
             ('Voynich', 'Voynich (la migliore delle due letture dei segni)', 'secondo'),
             ('controllo negativo', 'un\'altra lingua cifrata e "decifrata"', 'contesto')]
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema, altezza=5.0)
        fig.subplots_adjust(left=0.09, right=0.98, top=0.80, bottom=0.18)
        colori = {'accento_s': t['accento'], 'secondo': t['secondo'], 'contesto': t['contesto']}
        for dx, (chiave, etichetta, colore) in zip((-0.18, 0, 0.18), serie):
            if chiave.startswith('Voynich'):
                # la piu' favorevole al Voynich fra le due letture dei segni
                ys = [max(max(ris[n][k]['parole_vere_diverse'] for k in ris[n] if k.startswith('Voynich')), 1)
                      for n in nomi]
                xs = [i + dx for i in range(len(nomi))]
            else:
                xs = [i + dx for i, n in enumerate(nomi) if chiave in ris[n]]
                ys = [max(ris[n][chiave]['parole_vere_diverse'], 1) for n in nomi if chiave in ris[n]]
            ax.scatter(xs, ys, s=40, color=colori[colore], edgecolor=t['sfondo'], linewidth=1.2,
                       label=etichetta, zorder=3)
        ax.set_yscale('log')
        ax.set_yticks([10, 30, 100, 300, 1000, 3000])
        ax.set_yticklabels(['10', '30', '100', '300', '1.000', '3.000'])
        ax.minorticks_off()
        ax.set_xticks(range(len(nomi)))
        ax.set_xticklabels(nomi, rotation=35, ha='right', fontsize=8.5)
        ax.set_ylabel('parole vere diverse nel testo decifrato')
        ax.legend(loc='center left', bbox_to_anchor=(0.0, 0.57), frameon=False, fontsize=8,
                  labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Nessuna lingua legge il Voynich',
                       'La chiave migliore per ogni lingua: una decifrazione vera trova centinaia o migliaia\n'
                       'di parole diverse, il Voynich poche decine, come un testo in un\'altra lingua.')
        grafici.salva(fig, RISULTATI, 'e14_decifrazione', tema)


if __name__ == '__main__':
    if '--naibbe' in sys.argv:
        controllo_naibbe()
    elif '--grafico' in sys.argv:
        with open(os.path.join(RISULTATI, 'e14_decifrazione.json'), encoding='utf-8') as f:
            disegna(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
