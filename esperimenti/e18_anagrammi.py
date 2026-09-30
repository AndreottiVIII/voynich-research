# -*- coding: utf-8 -*-
"""Esperimento 18: le parole del Voynich sono anagrammi ordinati?

Un'idea che torna spesso (per esempio Hauer e Kondrak, 2016): ogni parola del
Voynich sarebbe una parola vera con le lettere rimesse in un ordine fisso,
come l'ordine alfabetico ("amor" -> "amor", "roma" -> "amor"). Chi legge
ricostruisce la parola dal contesto. Se fosse cosi', due cose si vedrebbero
dal testo senza sapere niente della lingua:

- esiste un ordine dei segni che quasi tutte le parole rispettano. Per ogni
  testo cerchiamo l'ordine dei segni che rispetta il maggior numero di coppie
  di segni dentro le parole (tutte le coppie, non solo quelle vicine) e
  misuriamo quante coppie rispetta. Un testo con le parole ordinate arriva al
  100%, qualunque sia l'ordine usato; nessun ordine scende sotto il 50%;
- due parole diverse non hanno mai gli stessi segni in ordine diverso. Nelle
  lingue succede (roma, amor, mora); con le parole ordinate mai.

Confronti: la Bibbia in circa 100 lingue e otto testi tecnici latini, tutti su
35.000 parole; il cifrario Naibbe; e due controlli costruiti dalla Bibbia
latina: le parole con le lettere in ordine alfabetico (anagrammi ordinati) e le
parole con le lettere mescolate a caso.

Scrive risultati/e18_anagrammi.json e .md; con --grafico il grafico.
"""
import json, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
PAROLE = 35000


def coppie(parole):
    """Per ogni coppia di segni diversi (a, b): quante volte, dentro una
    parola, a viene prima di b (tutte le coppie di posizioni). Parole diverse,
    ciascuna contata una volta."""
    P = Counter()
    for w in set(tuple(p) for p in parole):
        for i in range(len(w)):
            for j in range(i + 1, len(w)):
                if w[i] != w[j]:
                    P[w[i], w[j]] += 1
    return P


def ordine_migliore(P, rnd, partenze=8):
    """L'ordine dei segni che rispetta piu' coppie (ricerca locale per
    spostamenti, da piu' partenze). Restituisce (quota rispettata, ordine)."""
    simboli = sorted({a for a, _ in P} | {b for _, b in P})
    idx = {s: i for i, s in enumerate(simboli)}
    S = len(simboli)
    M = [[0] * S for _ in range(S)]
    for (a, b), c in P.items():
        M[idx[a]][idx[b]] = c
    totale = sum(P.values())
    # partenza sensata: per quota di "vittorie" di ogni segno sugli altri
    forza = [sum(M[i][j] for j in range(S)) / max(1, sum(M[i][j] + M[j][i] for j in range(S)))
             for i in range(S)]
    migliore = (-1, None)
    for k in range(partenze):
        ordine = sorted(range(S), key=lambda i: -forza[i]) if k == 0 else rnd.sample(range(S), S)
        migliorato = True
        while migliorato:
            migliorato = False
            for pos in range(S):
                x = ordine[pos]
                resto = ordine[:pos] + ordine[pos + 1:]
                # guadagno di mettere x in ogni posizione del resto
                # valore(x in posizione q) = somma M[x][y] per y dopo + M[y][x] per y prima
                prima = 0
                dopo = sum(M[x][y] for y in resto)
                valori = [prima + dopo]
                for y in resto:
                    prima += M[y][x]
                    dopo -= M[x][y]
                    valori.append(prima + dopo)
                q = max(range(len(valori)), key=lambda i: valori[i])
                attuale = valori[pos]
                if valori[q] > attuale:
                    ordine = resto[:q] + [x] + resto[q:]
                    migliorato = True
        rispettate = sum(M[ordine[i]][ordine[j]] for i in range(S) for j in range(i + 1, S))
        if rispettate > migliore[0]:
            migliore = (rispettate, [simboli[i] for i in ordine])
    return migliore[0] / totale, migliore[1]


def anagrammi(parole):
    """Quota delle parole diverse (di almeno 2 segni diversi) che hanno gli
    stessi segni di un'altra parola diversa, in un altro ordine."""
    tipi = {tuple(p) for p in parole if len(set(p)) >= 2}
    borse = Counter(tuple(sorted(w)) for w in tipi)
    return sum(1 for w in tipi if borse[tuple(sorted(w))] > 1) / len(tipi)


def rotazioni(parole):
    """Quota delle parole diverse (di almeno 2 segni diversi) che sono un'altra
    parola del testo "ruotata": un pezzo spostato da un capo all'altro
    (chol -> lcho)."""
    tipi = {tuple(p) for p in parole if len(set(p)) >= 2}
    return sum(1 for w in tipi if any(w[i:] + w[:i] in tipi for i in range(1, len(w)))) / len(tipi)


def misura(parole, rnd):
    q, ordine = ordine_migliore(coppie(parole), rnd)
    return OrderedDict([('ordine_rispettato', q), ('anagrammi', anagrammi(parole)),
                        ('rotazioni', rotazioni(parole)),
                        ('ordine', ordine), ('parole', len(parole)),
                        ('parole_diverse', len(set(tuple(p) for p in parole)))])


def main():
    rnd = random.Random(18)
    ris = OrderedDict()
    glifi = misure.divisore(misure.GLIFI_EVA)
    for quale, nome, dividi in (('ZL', 'Voynich (ZL, segni EVA)', glifi), ('GC', 'Voynich (v101)', list)):
        righe = trascrizione.testo_corrente(trascrizione.leggi(quale))
        ps = [dividi(p) for r in righe for p in r.parole if trascrizione.pulita(p)][:PAROLE]
        ris[nome] = misura(ps, rnd)
        stampa(nome, ris[nome])
    for lingua in ('A', 'B'):
        righe = trascrizione.testo_corrente(trascrizione.leggi('ZL'), lingua=lingua)
        ps = [glifi(p) for r in righe for p in r.parole if trascrizione.pulita(p)]
        ris['Voynich, lingua %s di Currier' % lingua] = misura(ps, rnd)
        stampa('Voynich, lingua ' + lingua, ris['Voynich, lingua %s di Currier' % lingua])
    naibbe = os.path.join(lingue.SORGENTI, 'naibbe-cipher', 'encrypted', 'nathist_output_ciphertext.txt')
    ps = [glifi(p) for r in open(naibbe, encoding='utf-8') for p in r.split()][:PAROLE]
    ris['Naibbe (Plinio cifrato)'] = misura(ps, rnd)
    stampa('Naibbe', ris['Naibbe (Plinio cifrato)'])
    latino = lingue.parole('Latin')[:PAROLE]
    ris['controllo: latino con le lettere in ordine alfabetico'] = misura([sorted(p) for p in latino], rnd)
    mescolate = []
    for p in latino:
        p = list(p)
        rnd.shuffle(p)
        mescolate.append(p)
    ris['controllo: latino con le lettere mescolate'] = misura(mescolate, rnd)
    for k in list(ris)[-2:]:
        stampa(k, ris[k])
    naturali = OrderedDict()
    for chiave, meta in lingue.indice().items():
        if meta.get('tipo_scrittura') not in ('alfabeto', 'abjad'):
            continue
        ps = lingue.parole(chiave)[:PAROLE]
        if len(ps) < PAROLE:
            continue
        naturali['Bibbia: ' + meta['lingua']] = misura([list(p) for p in ps], rnd)
    for nome in lingue.GENERI:
        ps = lingue.genere(nome)[:PAROLE]
        naturali[nome] = misura([list(p) for p in ps], rnd)
    ris['naturali'] = naturali
    valori = sorted(v['ordine_rispettato'] for v in naturali.values())
    an = sorted(v['anagrammi'] for v in naturali.values())
    ro = sorted(v['rotazioni'] for v in naturali.values())
    print('testi naturali (%d): ordine rispettato %.3f-%.3f (mediana %.3f); anagrammi %.3f-%.3f (mediana %.3f); '
          'rotazioni %.3f-%.3f (mediana %.3f)' % (
              len(valori), valori[0], valori[-1], valori[len(valori) // 2], an[0], an[-1], an[len(an) // 2],
              ro[0], ro[-1], ro[len(ro) // 2]))
    for k, v in sorted(naturali.items(), key=lambda x: -x[1]['anagrammi'])[:5]:
        stampa(k, v)
    for k, v in sorted(naturali.items(), key=lambda x: -x[1]['ordine_rispettato'])[:8]:
        stampa(k, v)
    with open(os.path.join(RISULTATI, 'e18_anagrammi.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, v):
    print('%-55s ordine rispettato %5.1f%%  anagrammi %5.2f%%  rotazioni %5.2f%%  (%d parole diverse)  %s' % (
        nome, 100 * v['ordine_rispettato'], 100 * v['anagrammi'], 100 * v['rotazioni'], v['parole_diverse'],
        ' '.join(v['ordine'][:30])), flush=True)


def scrivi_tabella(ris):
    nat = ris['naturali']
    fascia = lambda k: '%.1f–%.1f%% (mediana %.1f%%)' % (
        100 * min(v[k] for v in nat.values()), 100 * max(v[k] for v in nat.values()),
        100 * sorted(v[k] for v in nat.values())[len(nat) // 2])
    out = ['# Esperimento 18: le parole del Voynich sono anagrammi ordinati?', '',
           '- **ordine rispettato**: fra tutte le coppie di segni diversi dentro le parole (parole diverse, '
           'contate una volta), la quota che rispetta l\'ordine dei segni migliore per quel testo. Parole con le '
           'lettere in ordine fisso: 100%. Nessun ordine scende sotto il 50%.',
           '- **anagrammi**: quota delle parole diverse che hanno gli stessi segni di un\'altra parola del testo, '
           'in un altro ordine. Parole ordinate: 0%.',
           '- **rotazioni**: quota delle parole diverse che sono un\'altra parola con un pezzo spostato da un capo '
           'all\'altro (*chol* → *lcho*).', '',
           'Testi naturali (%d, 35.000 parole ciascuno): ordine rispettato %s; anagrammi %s; rotazioni %s.' % (
               len(nat), fascia('ordine_rispettato'), fascia('anagrammi'), fascia('rotazioni')), '',
           '| testo | ordine rispettato | anagrammi | rotazioni | parole diverse | ordine dei segni (i primi 20) |',
           '|---|---|---|---|---|---|']
    righe = [(k, v) for k, v in ris.items() if k != 'naturali']
    righe += sorted(nat.items(), key=lambda x: -x[1]['anagrammi'])[:5]
    righe += sorted(nat.items(), key=lambda x: -x[1]['ordine_rispettato'])[:5]
    for k, v in righe:
        out.append('| %s | %.1f%% | %.1f%% | %.1f%% | %d | %s |' % (
            k, 100 * v['ordine_rispettato'], 100 * v['anagrammi'], 100 * v['rotazioni'], v['parole_diverse'],
            ' '.join(v['ordine'][:20])))
    out += ['', 'Nella tabella, dopo il Voynich e i controlli: i cinque testi naturali con più anagrammi e i '
            'cinque con l\'ordine più rigido.']
    with open(os.path.join(RISULTATI, 'e18_anagrammi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


def disegna(ris):
    import grafici
    nat = ris['naturali']
    for tema in grafici.TEMI:
        fig, ax, t = grafici.figura(tema)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.80, bottom=0.12)
        ax.scatter([100 * v['ordine_rispettato'] for v in nat.values()],
                   [100 * v['anagrammi'] for v in nat.values()], s=26, color=t['contesto'],
                   edgecolor=t['sfondo'], linewidth=0.8, label='testi naturali', zorder=2)
        punti = [('Voynich (ZL, segni EVA)', 'Voynich', t['accento'], (8, 4)),
                 ('Voynich (v101)', 'Voynich (v101)', t['accento'], (8, -10)),
                 ('Naibbe (Plinio cifrato)', 'Naibbe', t['secondo'], (-44, -3)),
                 ('controllo: latino con le lettere in ordine alfabetico', 'latino con le lettere\nin ordine alfabetico',
                  t['inchiostro'], (-118, 10)),
                 ('controllo: latino con le lettere mescolate', 'latino con le lettere\nmescolate', t['inchiostro'],
                  (8, -8))]
        for chiave, etichetta, colore, spost in punti:
            v = ris[chiave]
            ax.scatter([100 * v['ordine_rispettato']], [100 * v['anagrammi']], s=60, color=colore,
                       edgecolor=t['sfondo'], linewidth=1.4, zorder=4 if colore == t['accento'] else 3,
                       marker='o' if colore != t['inchiostro'] else 'D')
            ax.annotate(etichetta, (100 * v['ordine_rispettato'], 100 * v['anagrammi']), xytext=spost,
                        textcoords='offset points', fontsize=8.5, color=colore if colore != t['inchiostro']
                        else t['secondario'])
        for n in ('Bibbia: Hebrew', 'Bibbia: Chinese (pinyin, una sillaba per parola)'):
            if n in nat:
                v = nat[n]
                ax.annotate(n.replace('Bibbia: ', '').replace(' (pinyin, una sillaba per parola)', ' (pinyin)')
                            .replace('Hebrew', 'ebraico').replace('Chinese', 'cinese'),
                            (100 * v['ordine_rispettato'], 100 * v['anagrammi']), xytext=(6, 4),
                            textcoords='offset points', fontsize=8, color=t['muto'])
        ax.set_xlim(45, 104)
        ax.set_ylim(-4, 92)
        ax.set_xlabel('coppie di segni che rispettano l\'ordine migliore (%)')
        ax.set_ylabel('parole che hanno un anagramma nel testo (%)')
        ax.legend(loc='upper right', frameon=False, fontsize=8, labelcolor=t['secondario'])
        grafici.titoli(fig, ax, t, 'Le parole del Voynich non sono anagrammi ordinati',
                       'Con le lettere in un ordine fisso si starebbe in basso a destra: tutto in ordine,\n'
                       'nessun anagramma. Il Voynich ha l\'ordine di una lingua e più anagrammi di quasi tutte.')
        grafici.salva(fig, RISULTATI, 'e18_anagrammi', tema)


if __name__ == '__main__':
    if '--grafico' in sys.argv:
        with open(os.path.join(RISULTATI, 'e18_anagrammi.json'), encoding='utf-8') as f:
            disegna(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
