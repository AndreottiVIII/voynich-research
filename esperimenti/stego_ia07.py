# -*- coding: utf-8 -*-
"""ia07, modulo di supporto: messaggio nascosto nelle scelte di un modello (steganografia neurale con codifica
aritmetica, come Ziegler, Deng e Rush 2019), con cifratura a parola chiave.

Idea. Chi scrive non tira a sorte i segni: legge un flusso di bit e lo usa come "numero a caso" del campionamento.
Tecnicamente fa il DECODIFICATORE aritmetico (Witten, Neal e Cleary 1987, con la gestione dell'intervallo a cavallo
della metà): a ogni passo l'intervallo corrente si divide in parti proporzionali alle probabilità del modello, e il
segno scelto è quello la cui parte contiene il numero letto dai bit. Chi legge (con lo stesso modello e la stessa
chiave) rifà le stesse divisioni con i segni che vede: è il CODIFICATORE aritmetico, e i bit che emette sono
esattamente quelli che lo scrittore ha usato (tranne gli ultimi, ancora indeterminati alla fine del libro).

- I bit del messaggio sono cifrati: pacchetto = lunghezza (4 byte) + testo compresso (zlib 9) + etichetta (8 byte di
  SHA-256 di chiave e testo compresso), messo in XOR con un flusso di chiave SHA-256(sale | chiave | contatore). Dopo
  il pacchetto il flusso continua con bit di riempimento, anch'essi da SHA-256 della chiave: il libro intero è scritto
  da bit che sembrano a caso. Un libro "senza messaggio" usa solo bit di riempimento (SHA-256 di un seme).
- Probabilità intere: chi scrive e chi legge devono usare le stesse identiche probabilità. Le probabilità del modello
  diventano interi con somma Q = 2^24 (ogni segno ammesso almeno 1); l'aritmetica è tutta su interi Python.
- Precisione P = 48 bit: dopo la rinormalizzazione l'intervallo è più largo di 2^46 > Q, quindi ogni segno ammesso ha
  una parte non vuota.

Funzioni pubbliche: interi(probabilita) -> cumulate; Scrittore(fonte).scegli(cumulate); Lettore().codifica(cumulate, s);
pacchetto(testo, chiave), bit_di_chiave(...), apri(bit, chiave).
"""
import hashlib, math, zlib
from bisect import bisect_right

P = 48
TOP = 1 << P
META, QUARTO = TOP >> 1, TOP >> 2
Q_BIT = 24
Q = 1 << Q_BIT
SALE = b'ia07/voynich-neurale/1'


# ---------------------------------------------------------------- probabilità intere

def interi(probs):
    """Lista di probabilità (float, somma circa 1) -> cumulate intere [0, c1, ..., Q]; ogni voce almeno 1."""
    n = len(probs)
    q = [1 + int(p * (Q - n)) for p in probs]
    resto = Q - sum(q)
    i = max(range(n), key=lambda j: (q[j], -j))
    q[i] += resto
    if q[i] < 1:
        raise ValueError('quantizzazione impossibile')
    cum = [0] * (n + 1)
    for j, x in enumerate(q):
        cum[j + 1] = cum[j] + x
    return cum


def softmax_interi(logit):
    """Logit (float) -> cumulate intere. Tutto in Python a doppia precisione: stesso risultato per chi scrive e chi legge."""
    m = max(logit)
    e = [math.exp(x - m) for x in logit]
    s = sum(e)
    return interi([x / s for x in e])


# ---------------------------------------------------------------- flussi di bit

class Flusso:
    """Bit pseudocasuali da SHA-256(sale | etichetta | contatore), letti uno alla volta; si può far precedere un prefisso."""

    def __init__(self, etichetta, prefisso=()):
        self.etichetta = etichetta if isinstance(etichetta, bytes) else etichetta.encode('utf-8')
        self.prefisso = list(prefisso)
        self.i = 0
        self.blocco, self.k, self.contatore = [], 0, 0

    def __call__(self):
        if self.i < len(self.prefisso):
            b = self.prefisso[self.i]
        else:
            if self.k >= len(self.blocco):
                h = hashlib.sha256(SALE + b'|r|' + self.etichetta + b'|' + self.contatore.to_bytes(8, 'big')).digest()
                self.contatore += 1
                self.blocco = [(x >> (7 - j)) & 1 for x in h for j in range(8)]
                self.k = 0
            b = self.blocco[self.k]
            self.k += 1
        self.i += 1
        return b


def _flusso_chiave(chiave, n):
    out, c = bytearray(), 0
    while len(out) < n:
        out += hashlib.sha256(SALE + b'|k|' + chiave.encode('utf-8') + b'|' + c.to_bytes(8, 'big')).digest()
        c += 1
    return bytes(out[:n])


def _in_bit(dati):
    return [(x >> (7 - j)) & 1 for x in dati for j in range(8)]


def _da_bit(bit):
    return bytes(sum(b << (7 - j) for j, b in enumerate(bit[i:i + 8])) for i in range(0, len(bit) - len(bit) % 8, 8))


def pacchetto(testo, chiave):
    """Testo -> bit cifrati del pacchetto (lunghezza, compresso, etichetta)."""
    compresso = zlib.compress(testo.encode('utf-8'), 9)
    chiaro = len(compresso).to_bytes(4, 'big') + compresso + hashlib.sha256(chiave.encode('utf-8') + compresso).digest()[:8]
    ks = _flusso_chiave(chiave, len(chiaro))
    return _in_bit(bytes(a ^ b for a, b in zip(chiaro, ks)))


def fonte_con_messaggio(testo, chiave):
    """Fonte di bit per chi scrive: il pacchetto cifrato e poi riempimento dalla chiave."""
    return Flusso(b'riempimento|' + chiave.encode('utf-8'), pacchetto(testo, chiave))


def fonte_senza_messaggio(seme):
    return Flusso(b'senza|%d' % seme)


def apri(bit, chiave):
    """Bit letti dal libro -> testo, oppure None (chiave sbagliata, libro senza messaggio o bit insufficienti)."""
    if len(bit) < 32:
        return None
    ks = _flusso_chiave(chiave, 4)
    n = int.from_bytes(bytes(a ^ b for a, b in zip(_da_bit(bit[:32]), ks)), 'big')
    tot = 4 + n + 8
    if 8 * tot > len(bit):
        return None
    chiaro = bytes(a ^ b for a, b in zip(_da_bit(bit[:8 * tot]), _flusso_chiave(chiave, tot)))
    compresso, etichetta = chiaro[4:4 + n], chiaro[4 + n:]
    if hashlib.sha256(chiave.encode('utf-8') + compresso).digest()[:8] != etichetta:
        return None
    try:
        return zlib.decompress(compresso).decode('utf-8')
    except Exception:
        return None


# ---------------------------------------------------------------- codifica aritmetica

class Scrittore:
    """Decodificatore aritmetico pilotato dai bit: sceglie i segni."""

    def __init__(self, fonte):
        self.fonte = fonte
        self.low, self.high = 0, TOP - 1
        self.value = 0
        for _ in range(P):
            self.value = (self.value << 1) | fonte()
        self.letti = P

    def scegli(self, cum):
        q = cum[-1]
        rng = self.high - self.low + 1
        target = ((self.value - self.low + 1) * q - 1) // rng
        s = bisect_right(cum, target) - 1
        self.high = self.low + rng * cum[s + 1] // q - 1
        self.low = self.low + rng * cum[s] // q
        while True:
            if self.high < META:
                pass
            elif self.low >= META:
                self.low -= META
                self.high -= META
                self.value -= META
            elif self.low >= QUARTO and self.high < META + QUARTO:
                self.low -= QUARTO
                self.high -= QUARTO
                self.value -= QUARTO
            else:
                break
            self.low <<= 1
            self.high = (self.high << 1) | 1
            self.value = (self.value << 1) | self.fonte()
            self.letti += 1
        return s


class Lettore:
    """Codificatore aritmetico: dai segni visti ai bit che li hanno scelti."""

    def __init__(self):
        self.low, self.high, self.sospesi = 0, TOP - 1, 0
        self.bit = []

    def _emetti(self, b):
        self.bit.append(b)
        self.bit.extend([1 - b] * self.sospesi)
        self.sospesi = 0

    def codifica(self, cum, s):
        q = cum[-1]
        rng = self.high - self.low + 1
        self.high = self.low + rng * cum[s + 1] // q - 1
        self.low = self.low + rng * cum[s] // q
        while True:
            if self.high < META:
                self._emetti(0)
            elif self.low >= META:
                self._emetti(1)
                self.low -= META
                self.high -= META
            elif self.low >= QUARTO and self.high < META + QUARTO:
                self.sospesi += 1
                self.low -= QUARTO
                self.high -= QUARTO
            else:
                break
            self.low <<= 1
            self.high = (self.high << 1) | 1


# ---------------------------------------------------------------- prova autonoma (distribuzioni a caso, nessun testo)

def prova(n_messaggi=20, passi=4000):
    import random
    esatti = respinti = 0
    for i in range(n_messaggi):
        rnd = random.Random(500 + i)
        testo = ''.join(rnd.choice('abcdefghilmnopqrstuvz ') for _ in range(rnd.randint(50, 400)))
        chiave = 'prova-%d' % i
        fonte = fonte_con_messaggio(testo, chiave)
        usati = []

        def registra():
            b = fonte()
            usati.append(b)
            return b
        sc, le = Scrittore(registra), Lettore()
        storia = []
        for _ in range(passi):
            n = rnd.randint(1, 40)
            logit = [rnd.gauss(0, 3) for _ in range(n)]
            cum = softmax_interi(logit)
            s = sc.scegli(cum)
            storia.append((cum, s))
        for cum, s in storia:
            le.codifica(cum, s)
        assert le.bit == usati[:len(le.bit)], 'i bit letti non sono quelli usati'
        assert len(usati) - len(le.bit) <= P + le.sospesi + 1
        esatti += apri(le.bit, chiave) == testo
        respinti += apri(le.bit, chiave + 'x') is None
    return esatti, respinti


if __name__ == '__main__':
    print('recupero esatto %d/20, chiave sbagliata respinta %d/20' % prova())
