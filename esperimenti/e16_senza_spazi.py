# -*- coding: utf-8 -*-
"""Esperimento 16: la decifrazione ignorando gli spazi.

L'esperimento 12 dice che molti spazi del Voynich sono regole di scrittura o
sono facoltativi: forse non separano le parole del testo in chiaro. Qui lo
stesso attacco dell'esperimento 14 (sostituzione omofonica), ma su ogni riga
presa come una sequenza continua di segni, senza spazi, contro un modello di
lettere della lingua anch'esso senza spazi.

Per giudicare una chiave si divide il testo decifrato in parole col
vocabolario della lingua (programmazione dinamica: si cerca la divisione che
copre piu' lettere con parole vere di almeno 3 lettere) e si misura la quota
di lettere coperte. Controllo positivo e negativo come nell'esperimento 14, piu'
il tetto: quanto si copre del testo in chiaro stesso.

Esito: questo attacco NON rompe il controllo positivo (resta lontano dal
tetto, e sotto il controllo negativo). Senza spazi una sostituzione omofonica
e' molto piu' difficile, e servirebbe un risolutore ben piu' potente (ricottura
simulata con modelli di lingua piu' lunghi, come per i cifrari dello Zodiac).
Quindi il numero sul Voynich non dice niente: l'esperimento resta qui perche'
si veda che e' stato provato e perche' non ha funzionato. Solo latino.

Scrive risultati/e16_senza_spazi.json e risultati/e16_senza_spazi.md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
import decifra, lingue, misure, trascrizione

RISULTATI = os.path.join(QUI, '..', 'risultati')
LINGUE = OrderedDict([('Latin', 'latino')])
ADDESTRAMENTO = 250000
LUNGHEZZA_RIGA = 7          # parole per riga finta, come nel Voynich


def righe_continue(parole, per_riga=LUNGHEZZA_RIGA):
    """Il testo in righe da per_riga parole, ciascuna scritta senza spazi."""
    return [''.join(parole[i:i + per_riga]) for i in range(0, len(parole) - per_riga + 1, per_riga)]


def copertura(stringa, vocabolario, massimo=16):
    """Quante lettere della stringa si coprono al meglio con parole vere
    (di almeno 3 lettere), senza sovrapposizioni."""
    n = len(stringa)
    migliore = [0] * (n + 1)
    for i in range(1, n + 1):
        m = migliore[i - 1]
        for l in range(3, min(massimo, i) + 1):
            if stringa[i - l:i] in vocabolario:
                m = max(m, migliore[i - l] + l)
        migliore[i] = m
    return migliore[n]


def valuta(righe, chiave, cif, lingua):
    coperte = tot = 0
    for r in righe:
        d = decifra.decifra_parola(r, chiave, cif, lingua)
        coperte += copertura(d, lingua.vocabolario)
        tot += len(d)
    return coperte / tot


def main():
    rnd = random.Random(16)
    corrente = trascrizione.testo_corrente(trascrizione.leggi('ZL'))
    righe_v = [''.join(r) for r in trascrizione.righe_di_parole(corrente)]
    glifi = misure.divisore(misure.GLIFI_EVA)
    ris = OrderedDict()
    for chiave_l, nome in LINGUE.items():
        testo = lingue.parole(chiave_l)
        add = min(ADDESTRAMENTO, int(len(testo) * 0.8))
        # modello di lettere senza spazi: le "parole" sono righe continue
        lingua = decifra.Lingua(righe_continue(testo[:add]))
        lingua.vocabolario = set(testo[:add])       # per la copertura servono le parole vere
        r = ris[nome] = OrderedDict()
        prova = righe_continue(testo[add:add + 30000])
        cifrato, _ = decifra.cifra_omofonico(prova, rnd)
        cif = decifra.Cifrato(cifrato, decifra.dividi_unita, minimo=1)
        _, k = decifra.cerca(cif, lingua, rnd, ripartenze=4, giri=8)
        r['controllo positivo'] = valuta(cifrato, k, cif, lingua)
        r['tetto (testo in chiaro)'] = sum(copertura(x, lingua.vocabolario) for x in prova) / sum(len(x) for x in prova)
        altro = righe_continue(lingue.parole('Italian' if chiave_l == 'Latin' else 'Latin')[:30000])
        cifrato, _ = decifra.cifra_omofonico(altro, rnd)
        cif = decifra.Cifrato(cifrato, decifra.dividi_unita, minimo=1)
        _, k = decifra.cerca(cif, lingua, rnd, ripartenze=4, giri=8)
        r['controllo negativo'] = valuta(cifrato, k, cif, lingua)
        cif = decifra.Cifrato(righe_v, glifi, minimo=1)
        _, k = decifra.cerca(cif, lingua, rnd, ripartenze=4, giri=8)
        r['Voynich'] = valuta(righe_v, k, cif, lingua)
        r['esempio'] = [decifra.decifra_parola(x, k, cif, lingua) for x in righe_v[:4]]
        print('%-9s lettere coperte da parole vere: tetto %.1f%%  positivo %.1f%%  negativo %.1f%%  Voynich %.1f%%' % (
            nome, 100 * r['tetto (testo in chiaro)'], 100 * r['controllo positivo'], 100 * r['controllo negativo'],
            100 * r['Voynich']))
        with open(os.path.join(RISULTATI, 'e16_senza_spazi.json'), 'w', encoding='utf-8') as f:
            json.dump(ris, f, ensure_ascii=False, indent=1)
    out = ['# Esperimento 16: la decifrazione ignorando gli spazi', '',
           'Righe come sequenze continue di segni; sostituzione omofonica contro un modello di lettere '
           'senza spazi. Quota di lettere del testo decifrato coperte da parole vere (almeno 3 lettere).', '',
           '| lingua | tetto: il testo in chiaro | controllo positivo | controllo negativo | Voynich |',
           '|---|---|---|---|---|']
    for nome, r in ris.items():
        out.append('| %s | %.1f%% | %.1f%% | %.1f%% | %.1f%% |' % (
            nome, 100 * r['tetto (testo in chiaro)'], 100 * r['controllo positivo'], 100 * r['controllo negativo'],
            100 * r['Voynich']))
    out += ['', '**Esito: il metodo non funziona.** Il controllo positivo resta lontano dal tetto e sotto il '
            'controllo negativo: l\'attacco non rompe nemmeno un testo latino cifrato apposta, quindi il '
            'numero sul Voynich non dice niente. Serve un risolutore più potente.']
    out += ['', 'Le prime righe del Voynich "decifrate" come latino:', '', '```'] + ris['latino']['esempio'] + ['```']
    with open(os.path.join(RISULTATI, 'e16_senza_spazi.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
