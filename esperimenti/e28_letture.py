# -*- coding: utf-8 -*-
"""Esperimento 28: le parole uniche del Voynich e gli errori di lettura.

Con la regola delle giunture il generatore di Timm e Schinner rifa' quasi tutta la
lista di controllo (esperimento 23), ma ha meno parole uniche: nel Voynich il 68%
dei tipi compare una volta sola, nel generatore il 50%. I ritocchi fra segni
simili (k/t/p/f, in/iin, ol/or/al/ar, e/ee/ch, ch/sh) sono gia' il cuore del
generatore, e farne due invece di uno (esperimento 24) non basta.

Qui un'altra ipotesi. Una parte delle parole uniche potrebbe non venire dal testo,
ma da come e' stato scritto e letto: una a chiusa male che sembra una o, una r che
sembra una s, uno spazio che c'e' o non c'e'. Un errore cosi' crea una parola
nuova che nessuno copia dopo: proprio una parola unica. Dentro il generatore,
invece, ogni parola nuova puo' essere copiata e ripetuta.

1. Quanto e' incerta la lettura: la trascrizione di Zandbergen e Landini (ZL)
   contro quella di Takahashi (IT), riga per riga e parola per parola. Quali segni
   si scambiano, quanti spazi cambiano.
2. Le parole uniche e le letture incerte: quante parole uniche della ZL Takahashi
   legge in un altro modo, e quante, con la sua lettura, diventano parole che il
   testo usa gia'.
3. Il testo senza messaggio con errori di lettura: il generatore con le giunture
   (esperimento 23) piu' errori come quelli fra ZL e IT (un segno scambiato con uno
   simile, due parole unite, una parola divisa), a tre dosi: meta' del disaccordo
   fra ZL e IT (una stima degli errori di un solo lettore), tutto, il doppio. La
   lista di controllo dice se le parole uniche salgono al livello del Voynich e
   che cosa succede al resto.

Scrive risultati/e28_letture.json e .md.
"""
import difflib, json, math, os, random, sys
from collections import Counter, OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import misure, trascrizione
import e22_timm_schinner as e22
import e23_giunture as e23
from e07_codifiche import pagine_voynich, N_TIPI

RISULTATI = os.path.join(QUI, '..', 'risultati')
DOSI = (0.5, 1.0, 2.0)
SEMI = (19, 1)
SOLO_SEGNI = (2.0, 4.0)          # errori di lettura senza errori di spazio, solo sul primo seme


# --- 1. le due trascrizioni a confronto ------------------------------------------

def righe_di(quale):
    return OrderedDict(((r.pagina, r.numero), [p for p in r.parole if trascrizione.pulita(p)])
                       for r in trascrizione.testo_corrente(trascrizione.leggi(quale)))


def modifiche(a, b):
    """Le modifiche di un segno che portano a in b (a e b liste di segni, distanza 1)."""
    if len(a) == len(b):
        return [('scambio', x, y) for x, y in zip(a, b) if x != y]
    if len(a) + 1 == len(b):
        i = next((i for i in range(len(a)) if a[i] != b[i]), len(a))
        return [('aggiunta', None, b[i])]
    if len(a) == len(b) + 1:
        i = next((i for i in range(len(b)) if a[i] != b[i]), len(b))
        return [('tolta', a[i], None)]
    return []


def confronto(zl, it, glifi):
    """Allinea le righe comuni; per ogni parola della ZL, la lettura di Takahashi (o None)."""
    letture = {}
    conta = Counter()
    ops = Counter()
    distanze = Counter()
    for k in zl:
        if k not in it:
            conta['righe solo ZL'] += 1
            continue
        a, b = zl[k], it[k]
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                conta['uguali'] += i2 - i1
                for i in range(i1, i2):
                    letture[(k, i)] = a[i]
            elif op == 'replace' and i2 - i1 == j2 - j1:
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    conta['lette diversamente'] += 1
                    letture[(k, i)] = b[j]
                    ga, gb = glifi(a[i]), glifi(b[j])
                    d = misure.distanza(ga, gb)
                    distanze[min(d, 3)] += 1
                    if d == 1:
                        ops.update(modifiche(ga, gb))
            else:
                conta['spazi o parole diversi'] += i2 - i1
                if op == 'replace' and ''.join(a[i1:i2]) == ''.join(b[j1:j2]):
                    conta['unite' if i2 - i1 > j2 - j1 else 'divise'] += 1
    return letture, conta, ops, distanze


# --- 2. parole uniche e letture incerte ---------------------------------------------

def parole_uniche(zl, letture):
    """Sulle prime N_TIPI parole (come la lista di controllo): parole uniche, quante lette
    diversamente da Takahashi, e la quota di parole uniche se si prende la sua lettura
    quando e' una parola che il testo usa gia'."""
    posti = [(k, i) for k, r in zl.items() for i in range(len(r))][:N_TIPI]
    parole = [zl[k][i] for k, i in posti]
    conta = Counter(parole)
    uniche = [(k, i) for (k, i), p in zip(posti, parole) if conta[p] == 1]
    altre = [(k, i) for (k, i), p in zip(posti, parole) if conta[p] > 1]

    def diverse(ps):
        confrontate = [x for x in ps if x in letture]
        return sum(1 for x in confrontate if letture[x] != zl[x[0]][x[1]]) / len(confrontate)

    corrette = list(parole)
    for n, (k, i) in enumerate(posti):
        l = letture.get((k, i))
        if conta[parole[n]] == 1 and l and l != parole[n] and conta[l] > 0:
            corrette[n] = l
    c2 = Counter(corrette)
    return OrderedDict([
        ('tipi', len(conta)), ('hapax', sum(1 for v in conta.values() if v == 1) / len(conta)),
        ('uniche_lette_diversamente', diverse(uniche)), ('altre_lette_diversamente', diverse(altre)),
        ('uniche_che_diventano_note', sum(1 for a, b in zip(parole, corrette) if a != b)),
        ('hapax_con_la_lettura_di_takahashi', sum(1 for v in c2.values() if v == 1) / len(c2)),
    ])


def regolarita(pagine, glifi):
    """Quanto sono regolari le parole uniche rispetto alle altre: bit per segno secondo un
    modello a coppie di segni (con inizio e fine parola) imparato sulle parole ripetute del
    testo stesso, sulle prime N_TIPI parole. Piu' alto = meno regolare."""
    parole = [p for pg in pagine for r in pg for p in r][:N_TIPI]
    conta = Counter(parole)
    ripetute = [p for p in parole if conta[p] > 1]
    coppie, primi = Counter(), Counter()
    for p in ripetute:
        s = ['^'] + glifi(p) + ['$']
        coppie.update(zip(s, s[1:]))
        primi.update(s[:-1])
    v = len({x for p in ripetute for x in glifi(p)}) + 1

    def bit(p):
        s = ['^'] + glifi(p) + ['$']
        return -sum(math.log2((coppie[(a, b)] + 0.1) / (primi[a] + 0.1 * v)) for a, b in zip(s, s[1:])) / (len(s) - 1)

    uniche = [p for p, n in conta.items() if n == 1]
    return OrderedDict([('uniche', sum(map(bit, uniche)) / len(uniche)),
                        ('ripetute', sum(map(bit, ripetute)) / len(ripetute))])


# --- 3. errori di lettura sul testo senza messaggio ----------------------------------

class Errori:
    """Errori come quelli fra le due trascrizioni: un segno scambiato, aggiunto o tolto (con
    le frequenze osservate), due parole vicine unite, una parola divisa."""

    def __init__(self, ops, conta, parole):
        self.ops = list(ops.items())
        self.peso = sum(n for _, n in self.ops)
        self.p_lettura = conta['lette diversamente'] / parole
        self.p_unite = conta['unite'] / parole
        self.p_divise = conta['divise'] / parole

    def scegli(self, rnd):
        x = rnd.random() * self.peso
        for op, n in self.ops:
            x -= n
            if x < 0:
                return op
        return self.ops[-1][0]

    def ritocca(self, segni, rnd):
        for _ in range(20):
            tipo, da, a = self.scegli(rnd)
            if tipo == 'aggiunta':
                i = rnd.randrange(len(segni) + 1)
                return segni[:i] + [a] + segni[i:]
            posti = [i for i, s in enumerate(segni) if s == da]
            if posti:
                i = rnd.choice(posti)
                return segni[:i] + ([a] if tipo == 'scambio' else []) + segni[i + 1:]
        return segni

    def applica(self, pagine, dose, glifi, rnd, spazi=True):
        out = []
        for pagina in pagine:
            nuova = []
            for riga in pagina:
                r = []
                for p in riga:
                    if rnd.random() < self.p_lettura * dose:
                        p = ''.join(self.ritocca(glifi(p), rnd))
                    if not spazi:
                        r.append(p)
                        continue
                    if len(p) > 1 and rnd.random() < self.p_divise * dose:
                        segni = glifi(p)
                        if len(segni) > 1:
                            i = rnd.randrange(1, len(segni))
                            r += [''.join(segni[:i]), ''.join(segni[i:])]
                            continue
                    if r and rnd.random() < self.p_unite * dose:
                        r[-1] = r[-1] + p
                        continue
                    r.append(p)
                nuova.append([p for p in r if p])
            out.append(nuova)
        return out


def main():
    glifi = misure.divisore(misure.GLIFI_EVA)
    zl, it = righe_di('ZL'), righe_di('IT')
    letture, conta, ops, distanze = confronto(zl, it, glifi)
    parole_zl = sum(len(r) for k, r in zl.items() if k in it)
    ris = OrderedDict()
    ris['confronto'] = OrderedDict([('righe', len(zl)), ('righe_comuni', sum(1 for k in zl if k in it)),
                                    ('parole', parole_zl)] + [(k, v) for k, v in conta.items()])
    ris['distanze'] = {str(k): v for k, v in sorted(distanze.items())}
    ris['scambi'] = [[t, a, b, n] for (t, a, b), n in ops.most_common(20)]
    ris['parole_uniche'] = parole_uniche(zl, letture)
    print(json.dumps(ris, ensure_ascii=False, indent=1), flush=True)

    errori = Errori(ops, conta, parole_zl)
    tabella = os.path.join(e23.LAVORO, 'giunture.tsv')
    os.makedirs(e23.LAVORO, exist_ok=True)
    e23.tabella_giunture(tabella)
    classi = e23.compila()
    liste = OrderedDict()
    for nome, quale in (('Voynich (ZL)', 'ZL'), ('Voynich (Takahashi)', 'IT')):
        pagine = pagine_voynich(trascrizione.testo_corrente(trascrizione.leggi(quale)))
        liste[nome] = e22.lista_di_controllo(pagine, glifi)
        liste[nome]['regolarita'] = regolarita(pagine, glifi)
        e22.stampa(nome[:28], liste[nome])
    for seme in SEMI:
        pagine, _ = e23.genera(classi, tabella, 3.0, seme)
        for dose in (0.0,) + DOSI:
            testo = errori.applica(pagine, dose, glifi, random.Random(28 + seme)) if dose else pagine
            nome = 'generatore, seme %d, errori ×%g' % (seme, dose)
            liste[nome] = e22.lista_di_controllo(testo, glifi)
            liste[nome]['dose'] = dose
            liste[nome]['seme'] = seme
            liste[nome]['regolarita'] = regolarita(testo, glifi)
            e22.stampa(nome[:28], liste[nome])
        if seme == SEMI[0]:
            for dose in SOLO_SEGNI:
                testo = errori.applica(pagine, dose, glifi, random.Random(128 + seme), spazi=False)
                nome = 'generatore, seme %d, solo segni ×%g' % (seme, dose)
                liste[nome] = e22.lista_di_controllo(testo, glifi)
                liste[nome]['dose'] = dose
                liste[nome]['seme'] = seme
                liste[nome]['regolarita'] = regolarita(testo, glifi)
                e22.stampa(nome[:28], liste[nome])
    ris['liste'] = liste
    ris['tassi'] = {'lettura': errori.p_lettura, 'unite': errori.p_unite, 'divise': errori.p_divise}
    with open(os.path.join(RISULTATI, 'e28_letture.json'), 'w', encoding='utf-8') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
    scrivi_tabella(ris)


def pc(x, cifre=1):
    return ('%.*f%%' % (cifre, 100 * x)).replace('.', ',')


def migliaia(n):
    return '{:,}'.format(int(n)).replace(',', '.')


COLONNE = [('h2', 'h2', '%.2f'), ('spazio_spiegato', 'spazio', '%.0f%%'), ('tipi_su_parole', 'diverse', '%.0f%%'),
           ('hapax', 'uniche', '%.0f%%'), ('identiche_vs_riga', 'ripetute', '×%.2f'),
           ('somiglianza_riga', 'somiglianza riga', '%.1f%%'), ('somiglianza_6_righe', 'a 6 righe', '%.1f%%'),
           ('confine', 'legame fine-inizio', '%.3f')]


def scrivi_tabella(ris):
    c, u = ris['confronto'], ris['parole_uniche']
    n = c['parole']
    out = ['# Esperimento 28: le parole uniche e gli errori di lettura', '',
           '## Due trascrizioni a confronto', '',
           'Zandbergen-Landini (ZL) contro Takahashi (IT), sulle %s righe in paragrafi che hanno tutte e due '
           '(%s parole della ZL, senza quelle con segni illeggibili):' % (migliaia(c['righe_comuni']), migliaia(n)), '',
           '- lette allo stesso modo: %s;' % pc(c['uguali'] / n),
           '- lette diversamente, con lo stesso numero di parole: %s (a un segno di distanza %s di queste);' % (
               pc(c['lette diversamente'] / n), pc(ris['distanze']['1'] / c['lette diversamente'], 0)),
           '- con spazi o parole diversi: %s (%s volte Takahashi unisce due parole della ZL, %s ne divide una).' % (
               pc(c['spazi o parole diversi'] / n), migliaia(c['unite']), migliaia(c['divise'])), '',
           'Gli scambi più frequenti fra parole a un segno di distanza (ZL → IT): ' + ', '.join(
               '%s %s' % ({'scambio': '%s→%s' % (a, b), 'tolta': '%s tolta' % a, 'aggiunta': '%s aggiunta' % b}[t], k)
               for t, a, b, k in ris['scambi'][:12]) + '.', '',
           '## Le parole uniche', '',
           'Sulle prime %s parole della ZL (come nella lista di controllo): %s tipi, di cui %s compaiono una volta '
           'sola. Takahashi legge diversamente il %s delle parole uniche e il %s delle altre. Prendendo la sua '
           'lettura quando è una parola che il testo usa già (%s casi), le parole uniche scendono al %s.' % (
               migliaia(N_TIPI), migliaia(u['tipi']), pc(u['hapax']), pc(u['uniche_lette_diversamente']),
               pc(u['altre_lette_diversamente']), migliaia(u['uniche_che_diventano_note']),
               pc(u['hapax_con_la_lettura_di_takahashi'])), '',
           '## Il testo senza messaggio con errori di lettura', '',
           'Il generatore con la regola delle giunture (esperimento 23, forza 3), più errori come quelli fra le '
           'due trascrizioni: per parola, una lettura diversa con probabilità %s (un segno scambiato, aggiunto o '
           'tolto, con le frequenze osservate), due parole unite con probabilità %s, una divisa con probabilità %s; '
           'moltiplicate per la dose. "Solo segni": niente errori di spazio.' % (
               pc(ris['tassi']['lettura']), pc(ris['tassi']['unite']), pc(ris['tassi']['divise'])), '',
           '| testo | ' + ' | '.join(t for _, t, _ in COLONNE) + ' | bit per segno: uniche | ripetute |',
           '|---|' + '---|' * (len(COLONNE) + 2)]
    for nome, r in ris['liste'].items():
        celle = []
        for k, _, f in COLONNE:
            x = r[k] * 100 if f.endswith('%%') else r[k]
            celle.append((f % x).replace('.', ','))
        celle += [('%.2f' % r['regolarita'][k]).replace('.', ',') for k in ('uniche', 'ripetute')]
        out.append('| %s | %s |' % (nome.replace('×0.5', '×0,5'), ' | '.join(celle)))
    out += ['', 'Le ultime due colonne dicono quanto sono regolari le parole: bit per segno secondo un modello a '
            'coppie di segni imparato sulle parole ripetute dello stesso testo (prime %s parole). Più alto vuol dire '
            'meno regolare: parole uniche che seguono meno le abitudini delle parole ripetute.' % migliaia(N_TIPI)]
    with open(os.path.join(RISULTATI, 'e28_letture.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')


if __name__ == '__main__':
    if '--tabella' in sys.argv:
        with open(os.path.join(RISULTATI, 'e28_letture.json'), encoding='utf-8') as f:
            scrivi_tabella(json.load(f, object_pairs_hook=OrderedDict))
    else:
        main()
