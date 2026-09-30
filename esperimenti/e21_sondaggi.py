# -*- coding: utf-8 -*-
"""Esperimento 21: sondaggi sulle strade rimaste aperte.

Un'analisi preliminare, su campioni di 20.000 parole: per ogni strada si
costruisce un testo come lo produrrebbe quell'ipotesi, partendo da testi veri,
e lo si misura con la lista di controllo del Voynich. Non e' una decifrazione:
serve a vedere quali strade vanno nella direzione giusta e quali no.

1. Abbreviazioni: il latino scritto con le abbreviazioni dei manoscritti
   (-us, -um, -rum, -bus, -que, per, pro, con, et, le vocali nasali con la
   tilde...), in due gradi. Ogni abbreviazione e' un segno solo.
2. Lettere nulle: segni che non valgono niente, inseriti a caso o secondo una
   regola fissa (in testa alle parole che cominciano per vocale, in coda a
   quelle che finiscono per vocale).
3. Trasposizioni: le lettere del testo rimescolate con una trasposizione a
   colonne (lasciando gli spazi dov'erano), o rimescolate, capovolte e
   ordinate dentro ogni parola.
4. Testi che non sono prosa: elenchi veri in latino (genealogie, censimenti,
   elenchi di citta' e di offerte della Bibbia; la Notitia Dignitatum, un elenco
   di cariche; i Fasti di Idazio, un elenco di consoli), anche cifrati con un
   codice parola per parola come nell'esperimento 7.
5. Nessun messaggio: l'autocitazione di Timm e Schinner (ogni parola e' una
   copia ritoccata di una parola delle righe sopra), in due varianti veloci:
   modifiche guidate dalla forma delle parole del Voynich, o dalla sola
   lunghezza. Non e' l'algoritmo completo degli autori.

Scrive risultati/e21_sondaggi.json e .md.
"""
import json, math, os, random, re, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, lingue, misure, trascrizione
from e07_codifiche import impronta, pagine_voynich

RISULTATI = os.path.join(QUI, '..', 'risultati')
N = 20000


def profilo(pagine, dividi=None):
    r = impronta(pagine, dividi)
    r['spazio_spiegato'] = misure.spazi([riga for pag in pagine for riga in pag], dividi)['spiegata']
    return r


# ---------------------------------------------------------------- 1. abbreviazioni

PAROLE_INTERE = {'et': '⁊', 'est': '÷', 'quod': 'ꝙ', 'non': 'ñ', 'per': 'ꝑ', 'pro': 'ꝓ', 'qui': 'ꝗ'}
PREFISSI = [('prae', 'ṗ'), ('pre', 'ṗ'), ('con', 'ꝯ'), ('com', 'ꝯ'), ('per', 'ꝑ'), ('pro', 'ꝓ')]
SUFFISSI_LEGGERI = [('rum', 'ꝝ'), ('bus', 'ƀ'), ('que', 'ꝗ'), ('us', 'ꝰ'), ('um', 'ū')]
SUFFISSI_PESANTI = SUFFISSI_LEGGERI[:3] + [('tur', 'ꞇ')] + SUFFISSI_LEGGERI[3:] + [('ur', 'ᵲ')]
TILDE = {'a': 'ã', 'e': 'ẽ', 'i': 'ĩ', 'o': 'õ', 'u': 'ũ'}


def abbrevia(parola, pesante):
    if parola in PAROLE_INTERE:
        return PAROLE_INTERE[parola] if pesante or parola == 'et' else parola
    testa, coda = '', ''
    if pesante:
        for p, s in PREFISSI:
            if parola.startswith(p) and len(parola) > len(p) + 1:
                testa, parola = s, parola[len(p):]
                break
    for p, s in (SUFFISSI_PESANTI if pesante else SUFFISSI_LEGGERI):
        if parola.endswith(p) and len(parola) > len(p):
            parola, coda = parola[:-len(p)], s
            break
    if pesante:   # vocale + m/n davanti a consonante: la vocale con la tilde
        parola = re.sub(r'([aeiou])[mn](?=[^aeiou])', lambda m: TILDE[m.group(1)], parola)
    return testa + parola + coda


# ---------------------------------------------------------------- 2. nulle

def nulle_a_caso(parole, rnd, p=0.1, segni='αβγ'):
    return [''.join((rnd.choice(segni) if rnd.random() < p else '') + c for c in w) for w in parole]


def nulle_a_regola(parole):
    return [('χ' if w[0] in 'aeiou' else '') + w + ('ψ' if w[-1] in 'aeiou' else '') for w in parole]


# ---------------------------------------------------------------- 3. trasposizioni

def trasposizione_a_colonne(parole, rnd, colonne=7):
    """Le lettere, scritte in righe da `colonne` e rilette per colonne in un
    ordine a caso; poi ritagliate nelle stesse lunghezze delle parole."""
    lettere = ''.join(parole)
    ordine = rnd.sample(range(colonne), colonne)
    letto = ''.join(lettere[c::colonne] for c in ordine)
    out, i = [], 0
    for w in parole:
        out.append(letto[i:i + len(w)])
        i += len(w)
    return out


def dentro_le_parole(parole, modo, rnd):
    if modo == 'capovolte':
        return [w[::-1] for w in parole]
    if modo == 'ordinate':
        return [''.join(sorted(w)) for w in parole]
    out = []
    for w in parole:
        l = list(w)
        rnd.shuffle(l)
        out.append(''.join(l))
    return out


# ---------------------------------------------------------------- 4. elenchi

ELENCHI_BIBBIA = [('GEN', [5, 10, 11, 36]), ('NUM', [1, 2, 3, 7, 26, 33]), ('JOS', [15, 18, 19, 21]),
                  ('1CH', list(range(1, 10))), ('EZR', [2]), ('NEH', [7, 10, 11, 12])]


def elenchi_bibbia():
    percorso = os.path.join(lingue.SORGENTE, 'bibles', 'Latin.xml')
    testo = open(percorso, encoding='utf-8').read()
    versi = re.findall(r"<seg id='b\.([0-9A-Z]+)\.(\d+)\.\d+' type='verse'>(.*?)</seg>", testo, re.S)
    scelti = {(b, c) for b, cs in ELENCHI_BIBBIA for c in cs}
    return lingue.normalizza(' '.join(t for b, c, t in versi if (b, int(c)) in scelti)).split()


def latin_library(*nomi):
    pezzi = []
    for nome in nomi:
        with open(os.path.join(lingue.LATIN_LIBRARY, nome), encoding='utf-8', errors='ignore') as f:
            righe = [r for r in f if 'Latin Library' not in r and 'Classics Page' not in r]
        pezzi.append(lingue.normalizza(' '.join(righe)))
    return ' '.join(pezzi).split()


# ---------------------------------------------------------------- 5. autocitazione

def autocitazione_bilanciata(struttura, semi_righe, parole_v, dividi, rnd, lam=1.0, tau=1.5, lontano=0.05):
    """Come generatori.autocitazione, ma ogni modifica si accetta con la
    regola di Metropolis rispetto a un modello del Voynich: probabilita'
    della lunghezza (distribuzione delle lunghezze del Voynich) e forma della
    parola (trigrammi di segni). Cosi' le copie ritoccate non si accorciano ne'
    si allungano a ogni generazione, e restano parole dall'aspetto voynichese."""
    modifiche = generatori.Modifiche(parole_v, dividi)
    lung = Counter(len(dividi(w)) for w in parole_v)
    tot_l = sum(lung.values())
    trig = generatori.ModelloParole(parole_v, dividi).conti
    tot_t = {k: sum(v.values()) for k, v in trig.items()}

    def logp(u):
        v = ['^', '^'] + list(u) + ['$']
        s = math.log((lung.get(len(u), 0) + 0.5) / tot_l)
        for i in range(2, len(v)):
            c = trig.get((v[i - 2], v[i - 1]))
            s += math.log(((c[v[i]] if c else 0) + 0.1) / ((tot_t.get((v[i - 2], v[i - 1]), 0)) + 3.0))
        return s

    scritte = [tuple(dividi(w)) for riga in semi_righe for w in riga]
    pagine_out = []
    for righe_pagina in struttura:
        pagina = []
        for n_parole in righe_pagina:
            riga = []
            for _ in range(n_parole):
                if (pagina or riga) and rnd.random() >= lontano:
                    candidate = [(0, riga)] if riga else []
                    candidate += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                    pesi = [math.exp(-d / tau) for d, _ in candidate]
                    _, sorgente = rnd.choices(candidate, weights=pesi)[0]
                    fonte = rnd.choice(sorgente)
                else:
                    fonte = rnd.choice(scritte)
                nuova, lp = fonte, logp(fonte)
                for _ in range(generatori.poisson(rnd, lam)):
                    prova = modifiche.modifica(nuova, rnd)
                    if prova == nuova or not modifiche.valida(prova):
                        continue
                    lp2 = logp(prova)
                    if lp2 >= lp or rnd.random() < math.exp(lp2 - lp):
                        nuova, lp = prova, lp2
                riga.append(nuova)
                scritte.append(nuova)
            pagina.append(riga)
        pagine_out.append([[''.join(u) for u in riga] for riga in pagina])
    return pagine_out


def autocitazione_per_lunghezza(struttura, semi_righe, parole_v, dividi, rnd, lam=1.5, tau=1.5, lontano=0.1):
    """L'altra variante: modifiche scelte in modo simmetrico (una sostituzione
    di segno meta' delle volte, altrimenti un segno aggiunto o tolto in testa o
    in coda, con la stessa probabilita'), accettate secondo la sola
    distribuzione delle lunghezze del Voynich. Le parole restano lunghe il
    giusto e il vocabolario non si impoverisce, ma la forma delle parole e'
    controllata solo dalle coppie di segni ammesse."""
    mod = generatori.Modifiche(parole_v, dividi)
    lung = Counter(len(dividi(w)) for w in parole_v)
    testa, coda = list(mod.testa.items()), list(mod.coda.items())

    def passo(u):
        x = rnd.random()
        if x < 0.5:
            posti = [i for i, g in enumerate(u) if mod.sostituzioni[g]]
            if not posti:
                return u
            i = rnd.choice(posti)
            scelte = mod.sostituzioni[u[i]]
            v = u[:i] + (rnd.choices(list(scelte), weights=list(scelte.values()))[0],) + u[i + 1:]
            return v if mod.valida(v) else u
        x = (x - 0.5) * 4
        if x < 1:
            v = (rnd.choices([g for g, _ in testa], weights=[c for _, c in testa])[0],) + u
        elif x < 2:
            v = u[1:]
        elif x < 3:
            v = u + (rnd.choices([g for g, _ in coda], weights=[c for _, c in coda])[0],)
        else:
            v = u[:-1]
        if not v or not mod.valida(v):
            return u
        r = (lung.get(len(v), 0) + 0.5) / (lung.get(len(u), 0) + 0.5)
        return v if rnd.random() < min(1.0, r) else u

    scritte = [tuple(dividi(w)) for riga in semi_righe for w in riga]
    pagine_out = []
    for righe_pagina in struttura:
        pagina = []
        for n_parole in righe_pagina:
            riga = []
            for _ in range(n_parole):
                if (pagina or riga) and rnd.random() >= lontano:
                    candidate = [(0, riga)] if riga else []
                    candidate += [(d, pagina[-d]) for d in range(1, len(pagina) + 1)]
                    _, sorgente = rnd.choices(candidate, weights=[math.exp(-d / tau) for d, _ in candidate])[0]
                    u = rnd.choice(sorgente)
                else:
                    u = rnd.choice(scritte)
                for _ in range(generatori.poisson(rnd, lam)):
                    u = passo(u)
                riga.append(u)
                scritte.append(u)
            pagina.append(riga)
        pagine_out.append([[''.join(u) for u in riga] for riga in pagina])
    return pagine_out


# ---------------------------------------------------------------- tutto insieme

def main():
    rnd = random.Random(21)
    glifi = misure.divisore(misure.GLIFI_EVA)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    parole_v = trascrizione.parole(corrente)
    ris = OrderedDict()

    def misura(nome, pagine, dividi=None, gruppo=''):
        ris[nome] = profilo(pagine, dividi)
        ris[nome]['gruppo'] = gruppo
        stampa(nome, ris[nome])

    misura('Voynich (pagine vere)', pagine_voynich(corrente), glifi, 'Voynich')
    misura('Voynich (righe finte da 8 parole)', misure.pagine_finte(parole_v[:N]), glifi, 'Voynich')
    latino = lingue.parole('Latin')[:N]
    misura('latino (Vangeli)', misure.pagine_finte(latino), None, 'riferimento')
    # 1. abbreviazioni
    for pesante, nome in ((False, 'leggere'), (True, 'pesanti')):
        misura('latino con abbreviazioni ' + nome, misure.pagine_finte([abbrevia(w, pesante) for w in latino]),
               None, 'abbreviazioni')
    # 2. nulle
    misura('latino con nulle a caso (10%)', misure.pagine_finte(nulle_a_caso(latino, rnd)), None, 'nulle')
    misura('latino con nulle a regola', misure.pagine_finte(nulle_a_regola(latino)), None, 'nulle')
    # 3. trasposizioni
    misura('latino, trasposizione a colonne', misure.pagine_finte(trasposizione_a_colonne(latino, rnd)), None,
           'trasposizioni')
    for modo in ('mescolate', 'capovolte', 'ordinate'):
        misura('latino, lettere %s dentro le parole' % modo,
               misure.pagine_finte(dentro_le_parole(latino, modo, rnd)), None, 'trasposizioni')
    # 4. elenchi, in chiaro e con un codice parola per parola
    modello = generatori.ModelloParole(parole_v, glifi)
    for nome, parole in (('elenchi della Bibbia latina', elenchi_bibbia()[:N]),
                         ('Notitia Dignitatum (cariche)', latin_library('notitia1.txt', 'notitia2.txt')[:N]),
                         ('Fasti di Idazio (consoli)', latin_library('hydatiusfasti.txt')[:N])):
        misura(nome + ', ' + str(len(parole)) + ' parole', misure.pagine_finte(parole), None, 'elenchi')
        codice = generatori.codice_per_rango(parole, parole_v, modello, random.Random(7))
        misura(nome + ', con un codice', misure.pagine_finte(codice), glifi, 'elenchi')
    # 5. nessun messaggio
    pagine = pagine_voynich(corrente)
    struttura = [[len(r) for r in pag] for pag in pagine]
    semi = pagine[0][:3]
    gen = autocitazione_bilanciata(struttura, semi, parole_v, glifi, random.Random(5), lam=1.2)
    misura('autocitazione, modifiche guidate dalla forma delle parole', gen, glifi, 'nessun messaggio')
    gen = autocitazione_per_lunghezza(struttura, semi, parole_v, glifi, random.Random(5))
    misura('autocitazione, modifiche guidate dalla lunghezza', gen, glifi, 'nessun messaggio')
    with open(os.path.join(RISULTATI, 'e21_sondaggi.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def stampa(nome, r):
    print('%-58s h2 %.2f  lung %.2f  diverse %.2f  hapax %.2f  ripetute x%.2f  somigl. %.1f%%/%.1f%%/%.1f%%  '
          'spazio %.0f%%' % (nome, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_vs_riga'],
                             100 * r['somiglianza_riga'], 100 * r['somiglianza_riga_sotto'],
                             100 * r['somiglianza_6_righe'], 100 * r['spazio_spiegato']), flush=True)


def scrivi_tabella(ris):
    pct = lambda x: '%.1f%%' % (100 * x)
    out = ['# Esperimento 21: sondaggi sulle strade rimaste aperte', '',
           'Campioni di al più %d parole, in righe da 8 parole e pagine da 20 righe (il Voynich anche con le sue '
           'pagine vere). Misure come nella lista di controllo:' % N, '',
           '- **h2**: incertezza sul segno successivo, in bit (Voynich 2,2; latino 3,3);',
           '- **lunghezza** media delle parole in segni; **diverse**: parole diverse su parole; **hapax**: parole '
           'diverse usate una volta sola;',
           '- **ripetute**: parola identica alla precedente, rispetto a due parole qualsiasi della riga (Voynich '
           '×1,0; lingue ×0,12 in mediana);',
           '- **somiglianza**: quanto si somigliano nella grafia due parole diverse della stessa riga, della riga '
           'sotto e di 6 righe sotto, rispetto a due parole qualsiasi (Voynich 3,8%, 3,5%, 3,4%; lingue vicino a 0);',
           '- **spazio**: quota dell\'incertezza sullo spazio che il segno precedente toglie (Voynich 66%, lingue 17% '
           'in mediana).', '',
           '| strada | testo | h2 | lunghezza | diverse | hapax | ripetute | somiglianza (riga / sotto / 6 righe) '
           '| spazio |', '|---|---|---|---|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %s | %.2f | %.2f | %.2f | %.2f | ×%.2f | %s / %s / %s | %.0f%% |' % (
            r['gruppo'], nome, r['h2'], r['lung_media'], r['tipi_su_parole'], r['hapax'], r['identiche_vs_riga'],
            pct(r['somiglianza_riga']), pct(r['somiglianza_riga_sotto']), pct(r['somiglianza_6_righe']),
            100 * r['spazio_spiegato']))
    with open(os.path.join(RISULTATI, 'e21_sondaggi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e21_sondaggi.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
