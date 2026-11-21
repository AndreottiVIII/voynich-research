# -*- coding: utf-8 -*-
"""Esperimento IA18 (ia18): un piccolo modello linguistico che conosce molte lingue reimpara il Voynich?

Domanda: conoscere le lingue umane aiuta a imparare il Voynich? Si prende un modello aperto già preaddestrato su molte lingue
(Qwen2.5-0.5B, licenza Apache 2.0) e lo stesso modello con i pesi casuali (stessa architettura, inizializzazione della
configurazione). Entrambi si rifiniscono (fine-tuning completo, tutti i pesi) sullo stesso testo, con gli stessi dati, le
stesse finestre, lo stesso numero di passi. Si misura la curva di apprendimento in bit per carattere sulla validazione, in
funzione dei caratteri letti; il guadagno del preaddestramento (G) è la differenza fra i due bracci.

Trattamento dei testi, uguale per tutti: ogni testo diventa una sequenza di caratteri su un alfabeto comune di 29 segni
(le 26 lettere a-z, lo spazio, l'a capo e "?" per i segni rari); ogni segno è UN token del modello (nessuna spezzatura in
sottoparole): 1 token = 1 carattere per costruzione, e i bit per carattere sono i bit per token. Il vocabolario del modello si
riduce a questi 29 token più il token di inizio (le righe corrispondenti della matrice di immersione preaddestrata per il
braccio preaddestrato; casuali per l'altro). Si riporta anche quanti token per carattere darebbe la tokenizzazione naturale del
modello sugli stessi testi (descrittivo).
  - Voynich e generatori in EVA: le lettere EVA (non fuse) come lettere a-z.
  - Latino: le 20 lettere più frequenti (le altre diventano "?"). In chiaro: lettere vere. Cifrato: sostituzione semplice
    segno per segno sulle 20 lettere standard dell'EVA (a c d e f g h i k l m n o p q r s t x y), chiave diversa per seme.
  - Gibberish di Gaskell e Bowern: le lettere come sono (i 26 segni più frequenti).
  - Controlli negativi: i segni rimescolati fra tutte le parole (lunghezze delle parole e righe invariate), come in e3c95/ia04.

Per ogni testo e seme si usa lo stesso taglio di e3c95 (e95.dividi_blocchi: 40.000 caratteri di addestramento, 5.000 di
validazione, 10.000 di prova, in blocchi diversi). Il punto scelto è quello con la validazione più bassa fra i punti della
curva; la BPC della prova si legge lì.

Fasi: 0 taratura del passo di apprendimento di ciascun braccio (latino cifrato, seme 0, una lettura: non entra nei risultati);
1 controlli del latino (chiaro, cifrato, rimescolato) con il primo seme, con CANCELLO: se non passano, il resto non parte (uscita
3); se la corsa con l'assegnazione "letterale" dei segni non passa, si prova l'assegnazione "frequenza" (stessa fase); 2 tutti gli
altri testi e semi.

Preregistrazione: preregistrazioni/ia18.md. Scrive risultati/ia18_modello_lingue.json e .md, una riga per corsa (testo, seme,
braccio) in risultati/ia18_corse.jsonl e una per corsa di taratura in risultati/ia18_taratura.jsonl (solo numeri; con RIPRENDI=1
le corse già fatte non si rifanno). I pesi rifiniti di alcune corse stanno in dati/cache/ia18/rifiniti/ (non vanno nel repo).
SOLO_CONTROLLI=1: nessun testo del Voynich né imitazioni in EVA (solo per provare il codice). AUTOTEST=1: prova l'analisi con
numeri inventati (nessun modello, nessun testo reale).
"""
import json, math, os, random, statistics, sys, time
from collections import OrderedDict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e3c95_imparabilita as e95   # noqa: E402  (taglio, flusso, rimescolo, caricamento delle lingue)

NOME = 'ia18_modello_lingue'
N_ADD, N_VAL, N_PROVA = e95.N_ADD, e95.N_VAL, e95.N_PROVA
SEMI = tuple(int(s) for s in os.environ.get('SEMI', '1,2,3').split(','))
SOLO_CONTROLLI = os.environ.get('SOLO_CONTROLLI') == '1'
USCITA = os.environ.get('USCITA', os.path.join(QUI, '..', 'risultati'))
MODELLO_DIR = os.environ.get('MODELLO_DIR', os.path.join(QUI, '..', 'dati', 'cache', 'ia18', 'modelli_base', 'Qwen2.5-0.5B'))
RIFINITI_DIR = os.environ.get('RIFINITI_DIR', os.path.join(QUI, '..', 'dati', 'cache', 'ia18', 'rifiniti'))
SALVA_TESTI = [s for s in os.environ.get('SALVA_TESTI', '=Voynich').split('|') if s]   # di quali testi (primo seme) si salvano i pesi

# addestramento (uguale per i due bracci salvo il passo di apprendimento)
LUNG = int(os.environ.get('LUNG', 128))             # caratteri per finestra
LOTTO = int(os.environ.get('LOTTO', 2))             # finestre per passo
EPOCHE = float(os.environ.get('EPOCHE_MAX', 2))     # letture del testo di addestramento (40.000 caratteri) in tutto
PUNTI_EPOCHE = tuple(float(x) for x in os.environ.get('PUNTI', '0.1,0.25,0.5,0.75,1,1.5,2').split(','))
LR_DATI = {'pre': float(os.environ.get('LR_PRE', 0)) or None, 'cas': float(os.environ.get('LR_CAS', 0)) or None}   # None = taratura
GRIGLIA = {'pre': (5e-5, 1e-4, 2e-4), 'cas': (2e-4, 5e-4, 1e-3)}   # passi provati nella taratura
EPOCHE_TARATURA, PUNTI_TARATURA, SEME_TARATURA = 1.0, (0.5, 1.0), 0
LR_EMB = float(os.environ.get('LR_EMB', 1e-3))      # passo delle righe dell'alfabeto (immersione, legata all'uscita)
RISCALDA = int(os.environ.get('RISCALDA', 10))      # passi di riscaldamento lineare
DECADIMENTO, TAGLIO, BETA2 = 0.01, 1.0, 0.95
THREAD = int(os.environ.get('THREAD', 4))
BRACCI = [b for b in os.environ.get('BRACCI', 'pre,cas').split(',') if b]
ETICHETTA_BRACCIO = {'pre': 'preaddestrato', 'cas': 'pesi casuali'}
ASSEGNE = [a for a in os.environ.get('ASSEGNA', 'letterale,frequenza').split(',') if a]
PRIORITA_MAX = int(os.environ.get('PRIORITA_MAX', 2))   # 1 = solo i testi di priorità 1 (scala ridotta)
FORZA = os.environ.get('FORZA') == '1'              # continua anche se il cancello della fase 1 non passa (solo per prove)

# alfabeto comune
LETTERE = 'abcdefghijklmnopqrstuvwxyz'
ALFABETO_EVA = 'acdefghiklmnopqrstxy'      # le 20 lettere standard dell'EVA (alfabeto del latino cifrato)
ORDINE_RIF = 'etaoinshrdlcumwfgypbvkjxqz'  # ordine di frequenza delle lettere in inglese (solo per l'assegnazione "frequenza")
SEGNI = list(LETTERE) + [' ', '\n', '?']   # i 29 segni; l'indice è il numero del segno
INDICE = {s: i for i, s in enumerate(SEGNI)}
V = len(SEGNI) + 1                         # 29 segni + inizio
INIZIO = len(SEGNI)
SEME_CIFRA, SEME_PERMUTA = 18000, 18500

# soglie (vedi preregistrazioni/ia18.md; provvisorie fino alla fase 1, poi confermate o riscritte con un commit prima della fase 2)
SOGLIA_CIFRATO_BIT = float(os.environ.get('SOGLIA_CIFRATO_BIT', 0.15))   # C+: guadagno minimo (BPC prova) del latino cifrato
SOGLIA_CHIARO_BIT = float(os.environ.get('SOGLIA_CHIARO_BIT', 0.50))     # C+: guadagno minimo del latino in chiaro
MARGINE_CHIARO = float(os.environ.get('MARGINE_CHIARO', 0.10))           # C+: il chiaro supera il cifrato di almeno tanto
SOGLIA_NEG_BIT = float(os.environ.get('SOGLIA_NEG_BIT', 0.05))           # C-: guadagno massimo ammesso sui rimescolati
S_ALTO = float(os.environ.get('S_ALTO', 0.75))                           # posizione sulla scala (0 = negativi, 1 = cifrato)
S_BASSO = float(os.environ.get('S_BASSO', 0.25))
S_VICINO = float(os.environ.get('S_VICINO', 0.15))
SCALA_MIN = 0.10                                                         # larghezza minima della scala (bit)
SOGLIA_AREA_MIN = 0.25                                                   # letture da cui si calcola l'area fra le curve

RIF = dict(latino='Latino in chiaro', cifrato='Latino cifrato (sostituzione semplice)',
           neg_v='Voynich, lettere rimescolate (controllo negativo)', neg_l='Latino, lettere rimescolate (controllo negativo)')
FASE1 = (RIF['latino'], RIF['cifrato'], RIF['neg_l'])
GENERATORI = ('Timm e Schinner (seme 1)', "Voynichizzatore v21 (libro d'esempio)", 'Naibbe', 'Gibberish (Gaskell e Bowern)')

import numpy as np   # noqa: E402
import torch   # noqa: E402
import torch.nn as nn   # noqa: E402
import torch.nn.functional as F   # noqa: E402


# ---------------------------------------------------------------- testi

def lettere_di(blocchi):
    """Dalle parole con glifi EVA fusi (cth, ckh, ch, sh...) alle parole in lettere EVA."""
    return [[[tuple(''.join(w)) for w in r] for r in b] for b in blocchi]


def catalogo_lingue():
    """Latino, gibberish (e le altre lingue) dal catalogo di e3c95, senza il Voynich e senza il filtro TESTI."""
    salvato_t, salvato_c = os.environ.pop('TESTI', None), e95.SOLO_CONTROLLI
    e95.SOLO_CONTROLLI = True
    try:
        return e95.catalogo()
    finally:
        e95.SOLO_CONTROLLI = salvato_c
        if salvato_t is not None:
            os.environ['TESTI'] = salvato_t


def filtra(nomi, variabile):
    filtro = [s for s in os.environ.get(variabile, '').split('|') if s]
    if not filtro:
        return list(nomi)
    return [k for k in nomi if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro)]


def testi():
    """Testi dell'esperimento: nome -> dict(blocchi, ruolo, trasforma, max_segni, priorita, letterale)."""
    cat = catalogo_lingue()
    t = OrderedDict()

    def metti(nome, blocchi, ruolo, trasforma=None, max_segni=26, priorita=1, letterale=False):
        t[nome] = dict(blocchi=blocchi, ruolo=ruolo, trasforma=trasforma, max_segni=max_segni, priorita=priorita,
                       letterale=letterale)
    lat = cat['Latin']['blocchi']
    metti(RIF['latino'], lat, 'controllo_chiaro', max_segni=20, letterale=True)     # lettere vere, mai riassegnate
    metti(RIF['cifrato'], lat, 'controllo_cifrato', trasforma='cifra', max_segni=20)
    metti(RIF['neg_l'], lat, 'controllo_negativo', trasforma='lettere', max_segni=20)
    metti('Gibberish (Gaskell e Bowern)', cat['Gibberish (Gaskell e Bowern)']['blocchi'], 'generatore')
    if 'English' in cat:
        metti('Inglese cifrato (sostituzione semplice)', cat['English']['blocchi'], 'cifrato_altro', trasforma='cifra',
              max_segni=20, priorita=2)
    if not SOLO_CONTROLLI:
        v = lettere_di(e95.voynich_pagine())
        metti('Voynich', v, 'voynich')
        metti(RIF['neg_v'], v, 'controllo_negativo', trasforma='lettere')
        metti('Timm e Schinner (seme 1)', lettere_di(e95.timm_schinner()), 'generatore')
        metti("Voynichizzatore v21 (libro d'esempio)", lettere_di(e95.libro_v21()), 'generatore')
        metti('Naibbe', lettere_di(e95.naibbe()), 'generatore', priorita=2)
        metti('Voynich A', lettere_di(e95.voynich_pagine('A')), 'voynich', priorita=2)
        metti('Voynich B', lettere_di(e95.voynich_pagine('B')), 'voynich', priorita=2)
        metti('Voynich, alfabeto permutato a caso (sensibilità)', v, 'sensibilita', trasforma='permuta', priorita=2)
    return OrderedDict((k, t[k]) for k in filtra(t, 'TESTI') if t[k]['priorita'] <= PRIORITA_MAX)


def segni_tenuti(blocchi, max_segni):
    """I segni con almeno lo 0,1% (come e3c95), al massimo `max_segni`, i più frequenti. Gli altri diventano '?'."""
    conti = {}
    for b in blocchi:
        for r in b:
            for w in r:
                for s in w:
                    conti[s] = conti.get(s, 0) + 1
    tot = sum(conti.values())
    ok = [s for s in sorted(conti, key=lambda s: (-conti[s], s)) if conti[s] / tot >= 0.001]
    return ok[:max_segni]


def mappa_segni(spec, seme):
    """Mappa dai segni tenuti del testo ai segni dell'alfabeto comune (lettere a-z)."""
    tenuti = segni_tenuti(spec['blocchi'], spec['max_segni'])
    liberi = [x for x in LETTERE if x not in tenuti]
    m = {}
    for s in sorted(tenuti):
        m[s] = s if s in LETTERE else liberi.pop(0)    # un segno fuori da a-z (maiuscola, cifra...) prende una lettera libera
    if spec['trasforma'] == 'cifra':
        if len(tenuti) > len(ALFABETO_EVA):
            raise RuntimeError('troppi segni da cifrare nell\'alfabeto EVA: %d' % len(tenuti))
        chiave = list(ALFABETO_EVA)
        random.Random(SEME_CIFRA + seme).shuffle(chiave)
        m = {s: chiave[i] for i, s in enumerate(sorted(tenuti))}
    elif spec['trasforma'] == 'permuta':
        imm = [m[s] for s in sorted(tenuti)]
        random.Random(SEME_PERMUTA + seme).shuffle(imm)
        m = {s: imm[i] for i, s in enumerate(sorted(tenuti))}
    return m


def codifica_testo(spec, seme):
    """(add, val, prova) come liste di numeri di segno, più H1 e il testo in lettere (per contare i token naturali)."""
    parti = e95.dividi_blocchi(spec['blocchi'], seme)
    if parti is None:
        return None
    if spec['trasforma'] == 'lettere':
        rnd = random.Random(7919 * seme + 1)
        parti = [e95.rimescola_lettere(x, rnd) for x in parti]
    m = mappa_segni(spec, seme)
    cod, stringhe = [], []
    for x, q in zip(parti, (N_ADD, N_VAL, N_PROVA)):
        fl = [s if s in (' ', '\n') else m.get(s, '?') for s in e95.flusso(x)][:q]
        cod.append([INDICE[s] for s in fl])
        stringhe.append(''.join(fl))
    add, val, prova = cod
    return dict(add=add, val=val, prova=prova, h1=h1(add, prova), segni_usati=len(set(add)), stringa_add=stringhe[0])


def h1(add, prova):
    """Entropia a un segno: frequenze dell'addestramento più 0,5 su ogni segno (come e3c95), bit per carattere sulla prova."""
    conti = [0.5] * len(SEGNI)
    for s in add:
        conti[s] += 1
    tot = sum(conti)
    return -sum(math.log2(conti[s] / tot) for s in prova[1:]) / (len(prova) - 1)


# ---------------------------------------------------------------- modello

def indici_modello():
    """Numeri dei token del modello per i 29 segni e per il token di inizio (da vocab.json e config.json)."""
    voc = json.load(open(os.path.join(MODELLO_DIR, 'vocab.json'), encoding='utf-8'))
    cfg = json.load(open(os.path.join(MODELLO_DIR, 'config.json'), encoding='utf-8'))
    nomi = {' ': 'Ġ', '\n': 'Ċ'}
    return [voc[nomi.get(s, s)] for s in SEGNI] + [cfg['bos_token_id']]


def ordine_avvio(add):
    """Per l'assegnazione 'frequenza': permutazione delle 26 lettere. La k-esima lettera del testo per frequenza (a pari
    frequenza, l'ordine alfabetico) prende la riga di immersione preaddestrata della k-esima lettera di ORDINE_RIF."""
    conti = [0] * 26
    for s in add:
        if s < 26:
            conti[s] += 1
    testo = sorted(range(26), key=lambda i: (-conti[i], i))
    return testo, [INDICE[c] for c in ORDINE_RIF]


class Modello(nn.Module):
    def __init__(self, corpo):
        super().__init__()
        self.corpo = corpo

    def forward(self, x):
        h = self.corpo(input_ids=x, use_cache=False).last_hidden_state
        return F.linear(h, self.corpo.embed_tokens.weight)       # uscita legata all'immersione


def costruisci(braccio, seme, avvio=None):
    """Corpo del modello (Qwen2, da config.json) con vocabolario ridotto a V token e uscita legata all'immersione.
    'pre': pesi preaddestrati (per l'immersione, le righe dei V token); `avvio` = (testo, riferimento) per l'assegnazione
    "frequenza". 'cas': stessa architettura, pesi dalla configurazione (normale con scarto 0,02, norme a 1)."""
    from transformers import AutoConfig, AutoModel
    cfg = AutoConfig.from_pretrained(MODELLO_DIR)
    cfg.vocab_size = V
    cfg.use_cache = False
    torch.manual_seed(seme)
    corpo = AutoModel.from_config(cfg).float()
    if braccio == 'pre':
        from safetensors.torch import load_file
        sd = load_file(os.path.join(MODELLO_DIR, 'model.safetensors'))     # bfloat16 su disco; si converte in float32
        stato = {k[len('model.'):]: v.float() for k, v in sd.items() if k.startswith('model.') and k != 'model.embed_tokens.weight'}
        emb = sd['model.embed_tokens.weight'].float()[torch.tensor(indici_modello())].clone()
        del sd
        if avvio is not None:
            testo, rif = avvio
            nuova = emb.clone()
            for k in range(26):
                nuova[testo[k]] = emb[rif[k]]
            emb = nuova
        stato['embed_tokens.weight'] = emb
        corpo.load_state_dict(stato, strict=True)
    return Modello(corpo)


def gruppi_parametri(m, lr_corpo):
    emb = m.corpo.embed_tokens.weight
    return [dict(params=[p for p in m.parameters() if p is not emb], lr=lr_corpo), dict(params=[emb], lr=LR_EMB)]


def valuta(m, flusso, per_lotto=24):
    """BPC (bit per carattere) su blocchi di LUNG caratteri non sovrapposti, ciascuno preceduto dal token di inizio."""
    m.eval()
    n = len(flusso) // LUNG
    x = torch.tensor(flusso[:n * LUNG], dtype=torch.long).view(n, LUNG)
    tot = 0.0
    with torch.no_grad():
        for i in range(0, n, per_lotto):
            xb = x[i:i + per_lotto]
            ing = torch.cat([torch.full((xb.shape[0], 1), INIZIO, dtype=torch.long), xb[:, :-1]], 1)
            logit = m(ing)[:, :, :len(SEGNI)]                    # i segni; il token di inizio non si predice
            tot += F.cross_entropy(logit.reshape(-1, len(SEGNI)), xb.reshape(-1), reduction='sum').item()
    m.train()
    return tot / (n * LUNG) / math.log(2)


def piano_passi(epoche, punti):
    """(passi in cui si valuta, passi in tutto, passi per lettura del testo di addestramento)."""
    per_epoca = N_ADD / (LUNG * LOTTO)
    return sorted({0} | {max(1, int(round(e * per_epoca))) for e in punti}), int(round(epoche * per_epoca)), per_epoca


TMP_DIR = os.environ.get('TMP_DIR', os.path.join(QUI, '..', 'dati', 'cache', 'ia18', 'tmp'))
PROGRESSO = os.environ.get('PROGRESSO', os.path.join(QUI, '..', 'dati', 'cache', 'ia18', 'progresso.log'))


def progresso(riga):
    """Una riga di avanzamento di una corsa, in un file (i processi figli non hanno sempre un'uscita valida)."""
    try:
        os.makedirs(os.path.dirname(PROGRESSO), exist_ok=True)
        with open(PROGRESSO, 'a', encoding='utf-8', newline='\n') as f:
            f.write(time.strftime('%H:%M:%S ') + riga + '\n')
    except OSError:
        pass


def avvia_processo():
    torch.set_num_threads(THREAD)
    torch.use_deterministic_algorithms(True)


def corsa(l):
    """Una corsa: un testo, un seme, un braccio, un passo di apprendimento. Restituisce un dict di soli numeri."""
    inizio = time.time()
    braccio, seme = l['braccio'], l['seme']
    avvio = ordine_avvio(l['add']) if (braccio == 'pre' and l['assegna'] == 'frequenza' and not l['letterale']) else None
    m = costruisci(braccio, seme, avvio)
    opt = torch.optim.AdamW(gruppi_parametri(m, l['lr']), betas=(0.9, BETA2), weight_decay=DECADIMENTO)
    base = [g['lr'] for g in opt.param_groups]
    add = torch.tensor(l['add'], dtype=torch.long)
    rng = np.random.default_rng(10 * seme + 7)            # stesse finestre nei due bracci
    passi_val, passi_tot, per_epoca = piano_passi(l['epoche'], l['punti'])
    curva, migliore, stato, perdite, diverso, passo = [], None, None, [], False, 0
    os.makedirs(TMP_DIR, exist_ok=True)
    percorso_migliore = os.path.join(TMP_DIR, 'migliore_%d.pt' % os.getpid())
    for passo in range(0, passi_tot + 1):
        if passo in passi_val:
            v = valuta(m, l['val'])
            letture = passo * LOTTO * LUNG / N_ADD
            curva.append(dict(passo=passo, letture=round(letture, 4), val=round(v, 5)))
            if migliore is None or v < migliore:
                migliore = v
                stato = percorso_migliore          # il punto migliore sta su disco (1,4 GB in meno in memoria)
                torch.save(m.state_dict(), stato)
            if l.get('stampa'):
                progresso('[%s | %s | seme %d | %s | passo %g] passo %d (%.2f letture): validazione %.4f bit (%.0f s)' % (
                    l['testo'][:28], ETICHETTA_BRACCIO[braccio], seme, l['assegna'], l['lr'], passo, letture, v, time.time() - inizio))
        if passo == passi_tot:
            break
        for g, b in zip(opt.param_groups, base):
            g['lr'] = b * min(1.0, (passo + 1) / RISCALDA)
        partenze = torch.from_numpy(rng.integers(0, len(add) - LUNG, size=LOTTO))
        y = add[partenze[:, None] + torch.arange(LUNG)]
        ing = torch.cat([torch.full((LOTTO, 1), INIZIO, dtype=torch.long), y[:, :-1]], 1)
        perdita = F.cross_entropy(m(ing)[:, :, :len(SEGNI)].reshape(-1, len(SEGNI)), y.reshape(-1))
        if not math.isfinite(perdita.item()):
            diverso = True
            break
        opt.zero_grad(set_to_none=True)
        perdita.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        perdite.append(perdita.item() / math.log(2))
    if stato is not None:
        m.load_state_dict(torch.load(stato))
        os.remove(stato)
    bpc_prova = valuta(m, l['prova']) if l['fase'] != 'taratura' else None
    if l.get('salva'):
        os.makedirs(RIFINITI_DIR, exist_ok=True)
        p = os.path.join(RIFINITI_DIR, '%s_s%d_%s_%s.pt' % (''.join(c if c.isalnum() else '_' for c in l['testo'])[:40], seme,
                                                             braccio, l['assegna']))
        torch.save({k: x.to(torch.bfloat16) for k, x in m.state_dict().items()}, p)
    return dict(testo=l['testo'], seme=seme, braccio=braccio, assegna=l['assegna'], fase=l['fase'], lr=l['lr'], curva=curva,
                bpc_val=round(migliore, 5) if migliore is not None else None,
                bpc_prova=round(bpc_prova, 5) if bpc_prova is not None else None, h1=round(l['h1'], 5), passi=passo,
                passi_tot=passi_tot, addestramento_finale_bit=round(statistics.mean(perdite[-20:]), 4) if perdite else None,
                diverso=diverso, secondi=round(time.time() - inizio, 1), thread=THREAD)


# ---------------------------------------------------------------- analisi

def media_ds(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(media=statistics.mean(xs), ds=statistics.stdev(xs) if len(xs) > 1 else 0.0, n=len(xs))


def interpola(curva, x):
    """Valore della curva (letture -> validazione) in x, interpolando linearmente; fuori dal campo, il bordo."""
    p = [(c['letture'], c['val']) for c in curva]
    if x <= p[0][0]:
        return p[0][1]
    for (a, va), (b, vb) in zip(p, p[1:]):
        if a <= x <= b:
            return va + (vb - va) * (x - a) / (b - a) if b > a else va
    return p[-1][1]


def area_fra_curve(cr, cp, da, a):
    """Media, fra le letture `da` e `a`, della differenza (casuale - preaddestrato) delle due curve di validazione
    (trapezi su una griglia di 200 intervalli, interpolazione lineare)."""
    xs = [da + (a - da) * i / 200 for i in range(201)]
    d = [interpola(cr, x) - interpola(cp, x) for x in xs]
    return sum((d[i] + d[i + 1]) / 2 for i in range(200)) / 200


def letture_per_soglia(curva, soglia):
    """Prime letture (interpolate) a cui la validazione scende a `soglia` o sotto; None se non ci arriva."""
    p = [(c['letture'], c['val']) for c in curva]
    if p and p[0][1] <= soglia:
        return p[0][0]
    for (a, va), (b, vb) in zip(p, p[1:]):
        if vb <= soglia:
            return a + (b - a) * (va - soglia) / (va - vb) if va > vb else b
    return None


def analizza(nomi, corse):
    """Per testo: guadagno del preaddestramento seme per seme e aggregato (le corse sono già filtrate per assegnazione)."""
    per_t = {}
    for r in corse:
        per_t.setdefault(r['testo'], {}).setdefault(r['seme'], {})[r['braccio']] = r
    out = OrderedDict()
    for T in nomi:
        semi = [s for s in sorted(per_t.get(T, {})) if 'pre' in per_t[T][s] and 'cas' in per_t[T][s]]
        if not semi:
            continue
        righe = []
        for s in semi:
            p, c = per_t[T][s]['pre'], per_t[T][s]['cas']
            h = p['h1']
            fine = min(c['curva'][-1]['letture'], p['curva'][-1]['letture'])
            soglia = h - 0.5 * (h - min(p['bpc_val'], c['bpc_val']))      # a metà strada fra H1 e il punto migliore
            righe.append(dict(seme=s, h1=h, bpc_pre=p['bpc_prova'], bpc_cas=c['bpc_prova'], G=c['bpc_prova'] - p['bpc_prova'],
                              G_val=c['bpc_val'] - p['bpc_val'],
                              area=area_fra_curve(c['curva'], p['curva'], SOGLIA_AREA_MIN, fine),
                              g_relativo=(c['bpc_prova'] - p['bpc_prova']) / c['bpc_prova'],
                              quota_di_H1=(c['bpc_prova'] - p['bpc_prova']) / (h - p['bpc_prova']) if h > p['bpc_prova'] else None,
                              letture_pre=letture_per_soglia(p['curva'], soglia), letture_cas=letture_per_soglia(c['curva'], soglia),
                              soglia_bit=soglia, val0_pre=p['curva'][0]['val'], val0_cas=c['curva'][0]['val'],
                              diverso=bool(p.get('diverso') or c.get('diverso')), secondi=p['secondi'] + c['secondi']))
        lp = [x['letture_pre'] for x in righe]
        lc = [x['letture_cas'] for x in righe]
        out[T] = OrderedDict(
            semi=semi, G=media_ds([x['G'] for x in righe]), G_val=media_ds([x['G_val'] for x in righe]),
            area=media_ds([x['area'] for x in righe]), g_relativo=media_ds([x['g_relativo'] for x in righe]),
            quota_di_H1=media_ds([x['quota_di_H1'] for x in righe]),
            bpc_pre=media_ds([x['bpc_pre'] for x in righe]), bpc_cas=media_ds([x['bpc_cas'] for x in righe]),
            h1=media_ds([x['h1'] for x in righe]),
            letture_pre=media_ds(lp) if all(v is not None for v in lp) else None,
            letture_cas=media_ds(lc) if all(v is not None for v in lc) else None,
            letture_pre_non_raggiunte=sum(1 for v in lp if v is None), letture_cas_non_raggiunte=sum(1 for v in lc if v is None),
            divergenze=sum(1 for x in righe if x['diverso']), per_seme=righe)
    return out


def controlli(per):
    """Controlli positivi e negativi (soglie scritte nella preregistrazione)."""
    ctrl = OrderedDict()
    cif = per[RIF['cifrato']]['G']['media'] if RIF['cifrato'] in per else None
    if cif is not None:
        sem = [x['G'] for x in per[RIF['cifrato']]['per_seme']]
        ctrl['cifrato'] = dict(G=cif, G_minimo_fra_semi=min(sem), soglia=SOGLIA_CIFRATO_BIT,
                               superato=bool(cif >= SOGLIA_CIFRATO_BIT and min(sem) > 0))
    if RIF['latino'] in per:
        chi = per[RIF['latino']]['G']['media']
        sem = [x['G'] for x in per[RIF['latino']]['per_seme']]
        ctrl['chiaro'] = dict(G=chi, G_minimo_fra_semi=min(sem), soglia=SOGLIA_CHIARO_BIT,
                              margine_sul_cifrato=(chi - cif) if cif is not None else None, soglia_margine=MARGINE_CHIARO,
                              superato=bool(chi >= SOGLIA_CHIARO_BIT and min(sem) > 0 and cif is not None
                                            and chi - cif >= MARGINE_CHIARO))
    negs = [T for T in (RIF['neg_v'], RIF['neg_l']) if T in per]
    if negs:
        d = {T: per[T]['G']['media'] for T in negs}
        ctrl['negativo'] = dict(G=d, soglia=SOGLIA_NEG_BIT, superato=bool(all(v <= SOGLIA_NEG_BIT for v in d.values())))
    ctrl['tutti_superati'] = bool(all(c['superato'] for c in ctrl.values() if isinstance(c, dict))
                                  and 'cifrato' in ctrl and 'chiaro' in ctrl and 'negativo' in ctrl)
    return ctrl


def scala(per, ctrl, misura='G'):
    """Posizione s di ogni testo sulla scala 0 (guadagno medio dei negativi) - 1 (guadagno del latino cifrato). `misura` è
    'G' (guadagno finale sulla prova) o 'area' (area fra le curve di validazione). Vuota se la scala è più stretta di SCALA_MIN."""
    if RIF['cifrato'] not in per or not any(T in per for T in (RIF['neg_v'], RIF['neg_l'])):
        return OrderedDict()
    g0 = statistics.mean(per[T][misura]['media'] for T in (RIF['neg_v'], RIF['neg_l']) if T in per)
    g1 = per[RIF['cifrato']][misura]['media']
    if g1 - g0 < SCALA_MIN:
        return OrderedDict()
    return OrderedDict((T, dict(s=(x[misura]['media'] - g0) / (g1 - g0), s_ds=x[misura]['ds'] / (g1 - g0))) for T, x in per.items())


def fascia(s, gen):
    """Fascia preregistrata di una posizione s, dati i generatori (dict nome -> s)."""
    raggiungono = [G for G, v in gen.items() if v >= S_ALTO]
    if s >= S_ALTO:
        return 'alta' if not raggiungono else 'alta, ma la raggiunge anche un generatore', raggiungono
    return ('bassa' if s <= S_BASSO else 'intermedia'), raggiungono


def letture(per, ctrl, sc, sc_area):
    """Letture preregistrate per i testi 'voynich' e 'sensibilita', con il cancello contro i generatori, la coerenza fra le
    parti A e B, la sensibilità all'assegnazione delle lettere e la coerenza fra G e area."""
    out = OrderedDict()
    if not sc or not ctrl.get('tutti_superati'):
        return out
    gen = {T: sc[T]['s'] for T in GENERATORI if T in sc}
    gen_area = {T: sc_area[T]['s'] for T in GENERATORI if T in sc_area}
    for T, x in per.items():
        if T not in sc or x.get('ruolo') not in ('voynich', 'sensibilita'):
            continue
        s = sc[T]['s']
        raggiungono = [G for G, v in gen.items() if v >= S_ALTO]
        vicini = [G for G, v in gen.items() if abs(v - s) <= S_VICINO]
        if s >= S_ALTO and not raggiungono:
            lett = 'vantaggio alto come un cifrato semplice di una lingua nota, e nessun generatore lo raggiunge (lettura 1)'
        elif s >= S_ALTO:
            lett = 'vantaggio alto, ma lo raggiunge anche %s: il metodo non distingue (lettura 2)' % ', '.join(raggiungono)
        elif s <= S_BASSO:
            lett = 'vantaggio quasi nullo, come i testi senza lingua (lettura 3)'
        else:
            lett = 'vantaggio parziale (lettura 4); ' + ('vicino a ' + ', '.join(vicini) if vicini else 'non vicino a nessun generatore')
        d = dict(s=s, s_ds=sc[T]['s_ds'], lettura=lett, generatori_che_raggiungono=raggiungono, generatori_vicini=vicini)
        if T in sc_area:
            sa = sc_area[T]['s']
            d['s_per_area'] = sa
            d['fascia_G'] = fascia(s, gen)[0]
            d['fascia_area'] = fascia(sa, gen_area)[0]
            d['coerente_con_l_area'] = d['fascia_G'].split(',')[0] == d['fascia_area'].split(',')[0]
        out[T] = d
    # coerenza fra le parti e sensibilità all'assegnazione delle lettere (lettura 1: servono entrambe)
    if 'Voynich' in out:
        v = out['Voynich']
        for altro, chiave_ in (('Voynich A', 'differenza_da_A'), ('Voynich B', 'differenza_da_B'),
                               ('Voynich, alfabeto permutato a caso (sensibilità)', 'differenza_dal_permutato')):
            if altro in sc:
                v[chiave_] = sc[altro]['s'] - v['s']
                v[chiave_ + '_entro_soglia'] = abs(v[chiave_]) <= S_VICINO
        if v['s'] >= S_ALTO and not v['generatori_che_raggiungono']:
            mancanze = [k for k in ('differenza_da_A', 'differenza_da_B', 'differenza_dal_permutato') if k in v and not v[k + '_entro_soglia']]
            if mancanze:
                v['lettura'] += '; MA non coerente: ' + ', '.join(mancanze)
    return out


def corse_per(corse, assegna, specs, fasi=('fase1', 'fase2')):
    """Le corse principali di una assegnazione; i testi che restano sempre letterali (latino in chiaro) valgono per tutte."""
    fissi = {T for T, sp in specs.items() if sp.get('letterale')}
    return [c for c in corse if c['fase'] in fasi and (c['assegna'] == assegna or (c['assegna'] == 'letterale' and c['testo'] in fissi))]


def esito_cancello(corse, assegna, specs):
    """Controlli del latino con il primo seme (fase 1) per una assegnazione: dict con le G e l'esito."""
    c1 = [c for c in corse_per(corse, assegna, specs, ('fase1',)) if c['seme'] == SEMI[0]]
    per = analizza(FASE1, c1)
    if not all(T in per for T in FASE1):
        return dict(assegna=assegna, completo=False, superato=False)
    ctrl = controlli(per)
    return dict(assegna=assegna, completo=True, superato=bool(ctrl['tutti_superati']), controlli=ctrl,
                G={T: per[T]['G']['media'] for T in FASE1})


# ---------------------------------------------------------------- scrittura

def f3(x, n=3):
    return '–' if x is None else ('%.' + str(n) + 'f') % x


def md_ds(d, n=3):
    return '–' if d is None else '%s (%s)' % (f3(d['media'], n), f3(d['ds'], n))


def impronta_modello():
    """SHA-256 di model.safetensors, dal file scritto al momento dello scarico (se c'è)."""
    p = os.path.join(os.path.dirname(os.path.normpath(MODELLO_DIR)), 'sha256_%s.txt' % os.path.basename(os.path.normpath(MODELLO_DIR)))
    try:
        for riga in open(p, encoding='utf-8'):
            if 'model.safetensors' in riga:
                return riga.split()[0]
    except OSError:
        pass
    return None


def token_naturali(stringhe):
    """Token per carattere della tokenizzazione naturale del modello sugli stessi testi (descrittivo)."""
    from tokenizers import Tokenizer
    tk = Tokenizer.from_file(os.path.join(MODELLO_DIR, 'tokenizer.json'))
    return {T: len(tk.encode(s, add_special_tokens=False).ids) / len(s) for T, s in stringhe.items()}


def scrivi(specs, corse, assegna, lr, tpc, info_testi, taratura, cancelli):
    nomi = list(specs)
    principali = corse_per(corse, assegna, specs)
    per = analizza(nomi, principali)
    for T in per:
        per[T]['ruolo'] = specs[T]['ruolo']
    ctrl = controlli(per)
    sc = scala(per, ctrl)
    sc_area = scala(per, ctrl, 'area')
    lett = letture(per, ctrl, sc, sc_area)
    passi_val, passi_tot, per_epoca = piano_passi(EPOCHE, PUNTI_EPOCHE)
    ris = OrderedDict(
        esperimento='ia18', modello='Qwen2.5-0.5B (Apache 2.0), vocabolario ridotto a %d token' % V, assegnazione=assegna,
        parametri=dict(LUNG=LUNG, LOTTO=LOTTO, EPOCHE_MAX=EPOCHE, PASSI=passi_tot, PASSI_PER_LETTURA=per_epoca,
                       PUNTI_EPOCHE=PUNTI_EPOCHE, LR=lr, LR_EMB=LR_EMB, RISCALDA=RISCALDA, DECADIMENTO=DECADIMENTO, TAGLIO=TAGLIO,
                       BETA2=BETA2, SEMI=SEMI, THREAD=THREAD, SOLO_CONTROLLI=SOLO_CONTROLLI, N_ADD=N_ADD, N_VAL=N_VAL,
                       N_PROVA=N_PROVA, SOGLIA_CIFRATO_BIT=SOGLIA_CIFRATO_BIT, SOGLIA_CHIARO_BIT=SOGLIA_CHIARO_BIT,
                       MARGINE_CHIARO=MARGINE_CHIARO, SOGLIA_NEG_BIT=SOGLIA_NEG_BIT, S_ALTO=S_ALTO, S_BASSO=S_BASSO,
                       S_VICINO=S_VICINO, SOGLIA_AREA_MIN=SOGLIA_AREA_MIN, SCALA_MIN=SCALA_MIN, GRIGLIA=GRIGLIA, ORDINE_RIF=ORDINE_RIF,
                       MODELLO=os.path.basename(os.path.normpath(MODELLO_DIR)), BRACCI=BRACCI, ASSEGNE=ASSEGNE, PRIORITA_MAX=PRIORITA_MAX),
        versioni=dict(python=sys.version.split()[0], torch=torch.__version__, numpy=np.__version__, **tpc,
                      modello_sha256=impronta_modello()),
        testi=info_testi, taratura=taratura, cancelli=cancelli, controlli=ctrl, scala=sc, scala_per_area=sc_area, letture=lett, bersagli=per)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')
    r = ['# ia18 — un modello che sa le lingue reimpara il Voynich', '']
    sintesi = []
    if 'cifrato' in ctrl:
        c = ctrl['cifrato']
        sintesi.append('controllo positivo, latino cifrato: %s (guadagno %.3f bit per carattere, minimo fra semi %.3f; soglia %.2f)' % (
            'riuscito' if c['superato'] else 'FALLITO', c['G'], c['G_minimo_fra_semi'], c['soglia']))
    if 'chiaro' in ctrl:
        c = ctrl['chiaro']
        sintesi.append('controllo positivo, latino in chiaro: %s (guadagno %.3f bit, minimo fra semi %.3f; soglia %.2f; sopra il '
                       'cifrato di %s, soglia %.2f)' % ('riuscito' if c['superato'] else 'FALLITO', c['G'], c['G_minimo_fra_semi'],
                                                        c['soglia'], f3(c['margine_sul_cifrato']), c['soglia_margine']))
    if 'negativo' in ctrl:
        c = ctrl['negativo']
        sintesi.append('controllo negativo: %s (guadagno massimo ammesso %.2f bit: %s)' % (
            'riuscito' if c['superato'] else 'FALLITO', c['soglia'], '; '.join('%s %.3f' % (T, v) for T, v in c['G'].items())))
    r += sintesi
    r += ['', 'Assegnazione dei segni ai token: %s. Modello: Qwen2.5-0.5B, vocabolario ridotto a %d token (29 segni + inizio), '
          'fine-tuning completo di tutti i pesi dei due bracci (preaddestrato; pesi casuali dalla configurazione). Finestre di %d '
          'caratteri, %d finestre per passo, %d passi (%.1f letture di 40.000 caratteri), passo di apprendimento %s (preaddestrato) '
          'e %s (casuale), %g per le righe dell\'alfabeto. Semi %s.' % (
              assegna, V - 1, LUNG, LOTTO, passi_tot, EPOCHE, lr.get('pre'), lr.get('cas'), LR_EMB, ', '.join(map(str, SEMI))),
          'Valori: media dei semi (deviazione standard). BPC = bit per carattere sulla prova nel punto con la validazione più bassa. '
          'G = BPC(pesi casuali) - BPC(preaddestrato): guadagno del preaddestramento; posizione s = (G - G dei negativi) / '
          '(G del latino cifrato - G dei negativi).', '']
    if taratura:
        r += ['## Taratura del passo di apprendimento (latino cifrato, seme 0, una lettura; validazione finale in bit)', '',
              '| braccio | ' + ' | '.join('%g' % x for x in sorted({t['lr'] for t in taratura['corse']})) + ' | scelto |',
              '|---|' + '---|' * (len({t['lr'] for t in taratura['corse']}) + 1)]
        for b in ('pre', 'cas'):
            lrs = sorted({t['lr'] for t in taratura['corse'] if t['braccio'] == b})
            vals = {t['lr']: t['bpc_val'] for t in taratura['corse'] if t['braccio'] == b}
            r.append('| %s | %s | %g |' % (ETICHETTA_BRACCIO[b], ' | '.join(f3(vals.get(x)) if x in vals else '–' for x in sorted(
                {t['lr'] for t in taratura['corse']})), taratura['scelto'].get(b) or 0))
        r.append('')
    r += ['## Guadagno del preaddestramento, testo per testo', '',
          '| testo | ruolo | semi | BPC preaddestrato | BPC casuale | H1 | G (bit) | area fra le curve (bit) | G / BPC casuale | '
          'letture a metà strada: preaddestrato | casuale | posizione s |', '|---|---|---|---|---|---|---|---|---|---|---|---|']
    for T, x in per.items():
        r.append('| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            T, x['ruolo'], len(x['semi']), md_ds(x['bpc_pre']), md_ds(x['bpc_cas']), md_ds(x['h1']), md_ds(x['G']), md_ds(x['area']),
            md_ds(x['g_relativo']), md_ds(x['letture_pre'], 2) if x['letture_pre'] else 'non raggiunta',
            md_ds(x['letture_cas'], 2) if x['letture_cas'] else 'non raggiunta', f3(sc.get(T, {}).get('s'), 2)))
    if lett:
        r += ['', '## Letture preregistrate', '']
        for T, d in lett.items():
            r.append('- %s: s = %.2f (ds %.2f)%s: %s' % (T, d['s'], d['s_ds'], (', per area %.2f' % d['s_per_area']) if 's_per_area' in d else '',
                                                           d['lettura'] + ('' if d.get('coerente_con_l_area', True) else ' [la lettura dipende dalla misura: per area è %s]' % d['fascia_area'])))
    elif not ctrl.get('tutti_superati'):
        r += ['', 'Letture sul Voynich: nessuna (i controlli non sono tutti superati: "non leggibile").']
    r += ['', '## Token per carattere', '', '| testo | usati | tokenizzazione naturale del modello (descrittivo) |', '|---|---|---|']
    for T, d in info_testi.items():
        r.append('| %s | 1,000 | %s |' % (T, f3(d.get('token_naturali_per_carattere'))))
    r += ['', '## Curve di validazione (media dei semi, bit per carattere; colonne = letture del testo di addestramento)', '']
    by = {}
    for c in principali:
        by.setdefault((c['testo'], c['braccio']), []).append(c)
    intestazione = False
    for T in per:
        for b in BRACCI:
            cs = by.get((T, b), [])
            if not cs:
                continue
            if not intestazione:
                r.append('| testo | braccio | ' + ' | '.join('%.2f' % p['letture'] for p in cs[0]['curva']) + ' |')
                r.append('|---|---|' + '---|' * len(cs[0]['curva']))
                intestazione = True
            n = min(len(c['curva']) for c in cs)
            r.append('| %s | %s | ' % (T, ETICHETTA_BRACCIO[b]) + ' | '.join(
                f3(statistics.mean(c['curva'][i]['val'] for c in cs), 2) for i in range(n)) + ' |')
    r.append('')
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris, sintesi


# ---------------------------------------------------------------- prova dell'analisi con numeri inventati

def corse_inventate(nomi):
    """Corse sintetiche (nessun modello, nessun testo reale) per provare analisi e scrittura."""
    rnd = random.Random(5)
    base = {RIF['latino']: (0.9, 3.4), RIF['cifrato']: (0.35, 3.4), RIF['neg_v']: (0.0, 3.9), RIF['neg_l']: (0.0, 3.4)}
    out = []
    passi_val, passi_tot, per_epoca = piano_passi(EPOCHE, PUNTI_EPOCHE)
    for T in nomi:
        g, h = base.get(T, (rnd.uniform(0.05, 0.4), 3.7))
        for s in SEMI:
            for b in BRACCI:
                fin = h - 0.4 - (0 if b == 'cas' else g) + rnd.gauss(0, 0.01)
                cur = [dict(passo=p, letture=round(p * LOTTO * LUNG / N_ADD, 4),
                            val=round(fin + (h - fin) * math.exp(-p / (per_epoca * (1.0 if b == 'pre' else 2.0))) + rnd.gauss(0, 0.005), 5))
                       for p in passi_val]
                out.append(dict(testo=T, seme=s, braccio=b, assegna='letterale', fase='fase1' if T in FASE1 and s == SEMI[0] else 'fase2',
                                lr=1e-4, curva=cur, bpc_val=min(c['val'] for c in cur), bpc_prova=fin + 0.01, h1=h, passi=passi_tot,
                                passi_tot=passi_tot, addestramento_finale_bit=fin, diverso=False, secondi=1.0, thread=1))
    return out


# ---------------------------------------------------------------- esecuzione

def chiave(c):
    return (c['testo'], c['seme'], c['braccio'], c['assegna'], c['fase'], c.get('lr'))


def esegui_lavori(pool, lavori, corse, percorso, inizio):
    """Esegue le corse non ancora fatte, una riga per corsa nel file, e le aggiunge a `corse`."""
    fatte = {chiave(c) for c in corse}
    da_fare = [l for l in lavori if (l['testo'], l['seme'], l['braccio'], l['assegna'], l['fase'], l['lr']) not in fatte]
    print('  %d corse da fare, %d già fatte' % (len(da_fare), len(lavori) - len(da_fare)), flush=True)
    for i, c in enumerate(pool.imap(corsa, da_fare), 1):
        corse.append(c)
        with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(c, ensure_ascii=False) + '\n')
        print('  [%d/%d, %.0f min] %s | seme %d | %s | %s | passo %g: validazione %s, prova %s (%d passi, %.0f s)%s' % (
            i, len(da_fare), (time.time() - inizio) / 60, c['testo'], c['seme'], ETICHETTA_BRACCIO[c['braccio']], c['assegna'], c['lr'],
            f3(c['bpc_val']), f3(c['bpc_prova']), c['passi'], c['secondi'], ' DIVERGENTE' if c['diverso'] else ''), flush=True)
    return corse


def leggi_corse(percorso):
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        return [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    if os.path.exists(percorso) and os.path.getsize(percorso) > 0 and os.environ.get('NUOVA') != '1':
        raise SystemExit('%s ha già corse: usa RIPRENDI=1 per continuare, NUOVA=1 per ricominciare da capo' % percorso)
    open(percorso, 'w').close()
    return []


def main():
    os.makedirs(USCITA, exist_ok=True)
    if os.environ.get('AUTOTEST') == '1':
        nomi = [RIF['latino'], RIF['cifrato'], RIF['neg_v'], RIF['neg_l'], 'Voynich', 'Voynich A', 'Timm e Schinner (seme 1)',
                "Voynichizzatore v21 (libro d'esempio)", 'Naibbe', 'Gibberish (Gaskell e Bowern)']
        ruoli = dict(zip(nomi, ['controllo_chiaro', 'controllo_cifrato', 'controllo_negativo', 'controllo_negativo', 'voynich', 'voynich',
                               'generatore', 'generatore', 'generatore', 'generatore']))
        specs = OrderedDict((n, dict(ruolo=ruoli[n])) for n in nomi)
        ris, sint = scrivi(specs, corse_inventate(nomi), 'letterale', {'pre': 1e-4, 'cas': 5e-4}, {}, {n: {} for n in nomi}, None, [])
        print('\n'.join(sint))
        for T, d in ris['letture'].items():
            print(T, d['lettura'])
        return
    specs = testi()
    print('testi: %d; semi %s; bracci %s; assegnazioni %s' % (len(specs), SEMI, BRACCI, ASSEGNE), flush=True)
    dati, info, stringhe = {}, OrderedDict(), {}
    for T, sp in specs.items():
        print('  %-62s %-18s priorità %d' % (T, sp['ruolo'], sp['priorita']), flush=True)
        for s in (SEME_TARATURA,) + SEMI if T == RIF['cifrato'] else SEMI:
            d = codifica_testo(sp, s)
            if d is None:
                raise RuntimeError('testo %s seme %d: troppo corto' % (T, s))
            if s == SEMI[0]:
                stringhe[T] = d['stringa_add']
            del d['stringa_add']
            dati[T, s] = d
        info[T] = dict(ruolo=sp['ruolo'], priorita=sp['priorita'], segni_usati=statistics.mean(dati[T, s]['segni_usati'] for s in SEMI),
                       h1=statistics.mean(dati[T, s]['h1'] for s in SEMI))
    nat = token_naturali(stringhe)
    for T in info:
        info[T]['token_naturali_per_carattere'] = nat[T]
    tpc = {}
    try:
        import transformers
        tpc['transformers'] = transformers.__version__
    except ImportError:
        pass
    percorso = os.path.join(USCITA, 'ia18_corse.jsonl')
    percorso_t = os.path.join(USCITA, 'ia18_taratura.jsonl')
    corse = leggi_corse(percorso)
    corse_t = leggi_corse(percorso_t)
    inizio = time.time()
    processi = int(os.environ.get('PROCESSI', 1))

    def lavoro(T, s, b, assegna, lr, fase, **extra):
        d = dati[T, s]
        assegna = 'letterale' if specs[T]['letterale'] else assegna     # il latino in chiaro non si riassegna mai
        return dict(testo=T, seme=s, braccio=b, assegna=assegna, lr=lr, fase=fase, add=d['add'], val=d['val'], prova=d['prova'],
                    h1=d['h1'], letterale=specs[T]['letterale'], epoche=EPOCHE, punti=PUNTI_EPOCHE, salva=False, stampa=True, **extra)
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        # fase 0: taratura del passo di apprendimento di ciascun braccio
        lr = {b: LR_DATI[b] for b in BRACCI}
        taratura = None
        if any(lr[b] is None for b in BRACCI):
            print('fase 0: taratura del passo di apprendimento (latino cifrato, seme %d, %.0f lettura)' % (SEME_TARATURA, EPOCHE_TARATURA),
                  flush=True)
            T = RIF['cifrato']
            lavori = [lavoro(T, SEME_TARATURA, b, 'letterale', x, 'taratura', ) for b in BRACCI if lr[b] is None for x in GRIGLIA[b]]
            for l in lavori:
                l['epoche'], l['punti'] = EPOCHE_TARATURA, PUNTI_TARATURA
            corse_t = esegui_lavori(pool, lavori, corse_t, percorso_t, inizio)
            scelto = {}
            for b in BRACCI:
                if lr[b] is None:
                    ok = [c for c in corse_t if c['braccio'] == b and not c['diverso'] and c['bpc_val'] is not None]
                    scelto[b] = min(ok, key=lambda c: (c['curva'][-1]['val'], c['lr']))['lr']
                    lr[b] = scelto[b]
            taratura = dict(scelto=scelto, corse=[dict(braccio=c['braccio'], lr=c['lr'], bpc_val=c['curva'][-1]['val'],
                                                         diverso=c['diverso']) for c in corse_t])
            print('  passi scelti: %s' % scelto, flush=True)
        # fase 1: controlli del latino con il primo seme e cancello
        cancelli, scelta = [], None
        for assegna in ASSEGNE:
            print('fase 1: controlli del latino, seme %d, assegnazione %s' % (SEMI[0], assegna), flush=True)
            lavori = [lavoro(T, SEMI[0], b, assegna, lr[b], 'fase1') for T in FASE1 if T in specs for b in BRACCI]
            corse = esegui_lavori(pool, lavori, corse, percorso, inizio)
            c = esito_cancello(corse, assegna, specs)
            cancelli.append(c)
            print('  cancello (%s): %s; G %s' % (assegna, 'passato' if c['superato'] else 'NON passato',
                                                 {k: round(v, 3) for k, v in c.get('G', {}).items()}), flush=True)
            if c['superato']:
                scelta = assegna
                break
        if scelta is None and not FORZA:
            scelta = ASSEGNE[0]
            scrivi(specs, corse, scelta, lr, tpc, info, taratura, cancelli)
            print('CANCELLO: i controlli del latino non passano con nessuna assegnazione; il resto non parte (FORZA=1 per ignorarlo).',
                  flush=True)
            sys.exit(3)
        scelta = scelta or ASSEGNE[0]
        # fase 2: tutti gli altri testi e semi; prima la priorità 1 per tutti i semi (il risultato principale), poi la priorità 2
        print('fase 2: assegnazione %s' % scelta, flush=True)
        lavori = []
        for pr in (1, 2):
            for s in SEMI:
                for T, sp in specs.items():
                    if sp['priorita'] != pr or (s == SEMI[0] and T in FASE1):
                        continue      # i controlli del latino con il primo seme sono già fatti in fase 1
                    for b in BRACCI:
                        l = lavoro(T, s, b, scelta, lr[b], 'fase2')
                        l['salva'] = s == SEMI[0] and any((T == f[1:]) if f.startswith('=') else (f in T) for f in SALVA_TESTI)
                        lavori.append(l)
        corse = esegui_lavori(pool, lavori, corse, percorso, inizio)
    ris, sint = scrivi(specs, corse, scelta, lr, tpc, info, taratura, cancelli)
    for riga in sint:
        print(riga, flush=True)


if __name__ == '__main__':
    main()
