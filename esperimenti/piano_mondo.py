# -*- coding: utf-8 -*-
"""IA34, modulo di supporto: il mondo "struttura" (controllo positivo con struttura di sezione e di riga) e il suo oracolo stimato.

In parole semplici
- `markov2` (IA26) e' una catena di glifi: non ha vocabolario di sezione ne' legame fra righe vicine, quindi non puo' fare da controllo positivo per un'IA che deve rifare la
  struttura del libro. Qui c'e' un mondo di regola NOTA con quella struttura, costruito sulla disposizione e sulle frequenze del libro vero (stesse pagine, righe, paragrafi):
    * ogni parola "fresca" viene dal **vocabolario della sua sezione** (sezione e lingua della pagina), con le frequenze del libro in quella sezione;
    * con probabilita' `eco` (0,30) la parola e' una di quelle della **riga sopra**, in una posizione vicina (la stessa o quella prima o dopo), a volte ritoccata
      (`ritocco` 0,5: un glifo cambiato, aggiunto o tolto, come in `righello_testi.sintetico_tec2`);
    * con probabilita' `tema` (0,15) e' una delle 15 parole "di tema" scelte a caso nel vocabolario di sezione all'inizio di ogni pagina (frequenza almeno 3);
    * l'ultima parola di ogni riga viene, con probabilita' `fine` (0,5), dalla distribuzione delle parole che chiudono le righe di quella sezione; la prima parola di
      un paragrafo, con probabilita' `ini` (0,5), dalla distribuzione di quelle che li aprono.
  Le parole sono parole vere del libro (nel latino di prova: parole latine): i glifi hanno la statistica del libro. I parametri sono fissati qui, prima di ogni prova.
- Un mondo si usa come gli altri mondi di IA26: `righello_testi.attiva_mondo('struttura')` lo rende "il vero" del processo. **`righello_testi` non si modifica**: questo modulo
  registra il mondo in `RT.MONDI` e avvolge `RT.righe_sintetiche` (un mondo per processo; va importato prima di ogni attivazione).
- **L'oracolo stimato** del mondo e' lo STESSO generatore con gli STESSI parametri, ma con le frequenze (vocabolario di sezione, parole di fine riga, parole d'inizio paragrafo)
  contate solo sui fogli d'addestramento. Quindi i parametri (eco, tema, ...) si danno per noti; si stima solo quello che un'IA deve imparare dai conteggi. Con 2 o 4 volte il
  testo: il testo del mondo piu' campioni della vera regola sulla disposizione dei fogli d'addestramento. Il **gemello** e' la vera regola (frequenze del libro intero) con semi nuovi.
Nessun risultato e' scritto qui.
"""
import bisect
import os
import random
import sys
import zlib
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import righello_testi as RT  # noqa: E402

PAR_STRUTTURA = OrderedDict([('eco', 0.30), ('ritocco', 0.5), ('tema', 0.15), ('n_tema', 15), ('freq_min_tema', 3), ('fine', 0.5), ('ini', 0.5)])
NOME_MONDO = 'struttura'


def seme_str(*a):
    return zlib.crc32(':'.join(str(x) for x in a).encode('utf-8')) % (1 << 31)


def chiave_di(x):
    return (x['sezione'], x['lingua'])


class Campionatore:
    """Frequenze (Counter) -> estrazione pesata, con il ripiego sul totale se la chiave non c'e'."""

    def __init__(self, righe_conteggi):
        self.parole, self.fine, self.ini = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
        for x in righe_conteggi:
            ws = x['parole']
            if not ws:
                continue
            k = chiave_di(x)
            for kk in (k, None):
                self.parole[kk].update(ws)
                self.fine[kk][ws[-1]] += 1
                if x['ini']:
                    self.ini[kk][ws[0]] += 1
        self._c = {}

    def _cum(self, tab, k):
        t = tab if k in tab and tab[k] else None
        key = (id(tab), k if t is not None else None)
        if key not in self._c:
            cnt = tab[k] if t is not None else tab[None]
            voc = sorted(cnt)
            cum, s = [], 0.0
            for w in voc:
                s += cnt[w]
                cum.append(s)
            self._c[key] = (voc, cum, s)
        return self._c[key]

    def estrai(self, tab, k, rng):
        voc, cum, s = self._cum(tab, k)
        if not voc:
            return None
        return voc[min(bisect.bisect_right(cum, rng.random() * s), len(voc) - 1)]

    def vocabolario_tema(self, k, freq_min):
        cnt = self.parole[k] if self.parole.get(k) else self.parole[None]
        voc = sorted(w for w, c in cnt.items() if c >= freq_min)
        return voc or sorted(cnt)


def _modifica(w, rng, divisore, unita):
    u = divisore(w)
    for _ in range(12):
        tp = rng.choice((1, 2, 3))
        if tp == 1:
            i = rng.randrange(len(u))
            nuovo = rng.choice(unita)
            if nuovo == u[i]:
                continue
            u2 = list(u)
            u2[i] = nuovo
        elif tp == 2:
            i = rng.randrange(len(u) + 1)
            u2 = list(u[:i]) + [rng.choice(unita)] + list(u[i:])
        else:
            if len(u) < 2:
                continue
            i = rng.randrange(len(u))
            u2 = list(u[:i]) + list(u[i + 1:])
        w2 = ''.join(u2)
        if w2 != w and divisore(w2) == u2:
            return w2
    return w


def sintetico_struttura(righe_layout, righe_conteggi, seme, divisore, unita, par=None):
    """Il mondo struttura sulla disposizione `righe_layout` (dizionari come `I7.libro_vero()`: pagina, sezione, lingua, ini, parole = solo il numero di parole conta) con le
    frequenze contate su `righe_conteggi`. -> lista di righe (come `righe_layout`, con le parole nuove)."""
    par = par or PAR_STRUTTURA
    rng = random.Random(seme)
    C = Campionatore(righe_conteggi)
    out, pag, sopra, topici = [], None, None, []
    for x in righe_layout:
        k = chiave_di(x)
        if x['pagina'] != pag:
            pag, sopra = x['pagina'], None
            voc = C.vocabolario_tema(k, par['freq_min_tema'])
            topici = rng.sample(voc, min(par['n_tema'], len(voc)))
        n = len(x['parole'])
        ps = []
        for j in range(n):
            if j == n - 1 and rng.random() < par['fine']:
                w = C.estrai(C.fine, k, rng)
            elif j == 0 and x['ini'] and rng.random() < par['ini']:
                w = C.estrai(C.ini, k, rng)
            elif sopra and rng.random() < par['eco']:
                a = min(max(j + rng.choice((-1, 0, 1)), 0), len(sopra) - 1)
                w = sopra[a]
                if rng.random() < par['ritocco']:
                    w = _modifica(w, rng, divisore, unita)
            elif topici and rng.random() < par['tema']:
                w = rng.choice(topici)
            else:
                w = C.estrai(C.parole, k, rng)
            ps.append(w)
        sopra = ps
        y = dict(x)
        y['parole'] = ps
        out.append(y)
    return out


# ---------------------------------------------------------------- registrazione del mondo in righello_testi (senza modificarlo)

_originale = RT.righe_sintetiche


def _righe_sintetiche(base, nome, gemello=False):
    if nome != NOME_MONDO:
        return _originale(base, nome, gemello)
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    return sintetico_struttura(base, base, seme_str('ia34', 'mondo', nome, 'gemello' if gemello else 'vero'), D, unita)


def registra():
    if NOME_MONDO not in RT.MONDI:
        RT.MONDI[NOME_MONDO] = dict(gen='struttura', par=dict(PAR_STRUTTURA))
    RT.righe_sintetiche = _righe_sintetiche


registra()


# ---------------------------------------------------------------- l'oracolo stimato e il gemello

def t_da_righe(righe):
    """Righe (dizionari) -> lista (pagina, inizio, [parole]) come `I7.leggi_file`."""
    return [(x['pagina'], bool(x['ini']), list(x['parole'])) for x in righe]


def libro_oracolo(righe_mondo, base, f_add, mult, seme):
    """Un libro dell'oracolo stimato: la regola del mondo con le frequenze contate sui fogli d'addestramento del TESTO DEL MONDO (+ (mult - 1) campioni della vera regola sulla
    disposizione di quei fogli). `righe_mondo`: il testo del mondo; `base`: il libro da cui il mondo e' costruito (serve solo per i campioni in piu')."""
    D = I7.divisore()
    unita = sorted({u for x in righe_mondo for w in x['parole'] for u in D(w)})
    ins = set(f_add)
    conteggi = [x for x in righe_mondo if x['foglio'] in ins]
    if mult > 1:
        lay_add = [x for x in base if x['foglio'] in ins]
        for j in range(1, mult):
            conteggi += sintetico_struttura(lay_add, base, seme_str('ia34extra', j), D, unita)
    return t_da_righe(sintetico_struttura(righe_mondo, conteggi, seme, D, unita))


def libro_gemello(base, seme):
    """Un altro campione della vera regola (frequenze del libro intero) sulla disposizione del libro."""
    D = I7.divisore()
    unita = sorted({u for x in base for w in x['parole'] for u in D(w)})
    return t_da_righe(sintetico_struttura(base, base, seme, D, unita))


if __name__ == '__main__':
    pass
