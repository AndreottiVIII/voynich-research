# -*- coding: utf-8 -*-
"""Esperimento IA5 (ia05): le letture di e3c95 dipendono dalla rete scelta? Stesso disegno di e3c95 (stessi testi, stesse
divisioni in addestramento, validazione e prova, stesso addestramento con arresto anticipato, stesse misure), ma con
reti di grandezza diversa e un piccolo transformer.

Reti (RETI):
- gru64, gru128, gru256, gru512: GRU a caratteri, 1 strato, 64/128/256/512 unità nascoste (immersione 32, caduta 0,3
  sull'uscita). gru128 è la rete di e3c95: con gli stessi semi deve dare le stesse curve (verifica interna);
- gru2x256: GRU a 2 strati di 256 unità (caduta 0,3 solo sull'uscita);
- transformer: 2 strati, dimensione 128, 4 teste, contesto 64, caduta TF_CADUTA su immersione, uscite dei blocchi e
  prima dell'uscita; AdamW passo TF_LR con riscaldamento lineare di TF_RISCALDAMENTO passi. Non porta stato fra le
  finestre: in valutazione ogni segno si predice con gli ultimi 33-64 segni (finestre di 64 che avanzano di
  TF_PASSO_VAL segni; il GRU porta lo stato per tutta la prova).

Testi: Voynich (intero, A, B), 20 lingue naturali, 3 generatori in EVA (Timm e Schinner, voynichizzatore v21, Naibbe),
gibberish, controllo positivo (latino cifrato con sostituzione) e controllo negativo (Voynich a segni rimescolati);
più, per D, le versioni a parole rimescolate nella riga del Voynich intero, delle 20 lingue, dei 3 generatori e del
gibberish. Alfabeti, divisioni (dividi_blocchi) e rimescolamenti sono quelli di e3c95 (si importa e3c95_imparabilita).
Semi 1-5 (SEMI). Corsa = (rete, testo, seme).

Misure (come e3c95): H1, BPC, G = 1 - BPC/H1, E90 (letture dell'addestramento), scarto, D; in più, per grandezza, la
crescita di G: DG512 = G(gru512) - G(gru64) seme per seme (stessi blocchi) e DGmax = G della migliore delle 5 reti GRU
(media sui semi comuni a tutte le reti GRU, 1-3) meno G(gru64).

Preregistrazione: preregistrazioni/ia05.md. Scrive risultati/ia05_reti_grandi.json e .md e, una riga per corsa,
risultati/ia05_corse.jsonl (con RIPRENDI=1 le corse già fatte non si rifanno).
Variabili per le prove: PASSI, OGNI, PAZIENZA, SEMI, RETI (nomi separati da virgola), TESTI (sottostringhe separate
da |, "=Nome" per il nome esatto), SOLO_CONTROLLI=1 (niente Voynich né imitazioni in EVA), USCITA (cartella d'uscita),
TF_CADUTA, TF_LR, TF_RISCALDAMENTO, TF_PASSO_VAL, PROCESSI (non cambia i risultati).
"""
import json, math, os, random, statistics, sys, time
from collections import OrderedDict
from multiprocessing import get_context

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
os.environ.setdefault('SEMI', '1,2,3,4,5')       # prima di importare e3c95: i semi sono 1-5
import e3c95_imparabilita as e95                 # noqa: E402

N_ADD, N_VAL, N_PROVA = e95.N_ADD, e95.N_VAL, e95.N_PROVA
PASSI, OGNI, PAZIENZA = e95.PASSI, e95.OGNI, e95.PAZIENZA
SEMI = e95.SEMI
LUNG, LOTTO = e95.LUNG, e95.LOTTO
EMB, CADUTA = e95.EMB, e95.CADUTA
LR, DECADIMENTO, TAGLIO = e95.LR, e95.DECADIMENTO, e95.TAGLIO
SOGLIA_POSITIVO = 0.03   # fissa, non si cambia da ambiente (preregistrata)
SOLO_CONTROLLI = e95.SOLO_CONTROLLI
USCITA = e95.USCITA
NOME = 'ia05_reti_grandi'

TF_CADUTA = float(os.environ.get('TF_CADUTA', 0.1))
TF_LR = float(os.environ.get('TF_LR', 2e-3))
TF_RISCALDAMENTO = int(os.environ.get('TF_RISCALDAMENTO', 100))
TF_PASSO_VAL = int(os.environ.get('TF_PASSO_VAL', 32))
TF_DIM, TF_TESTE, TF_STRATI = 128, 4, 2
GRANDI = ('gru512', 'gru2x256', 'transformer')   # reti costose: meno semi (SEMI_GRANDI)
SEMI_GRANDI = tuple(int(x) for x in os.environ.get('SEMI_GRANDI', '1,2,3').split(','))
TF_SENZA_RIMESCOLATI = os.environ.get('TF_SENZA_RIMESCOLATI', '1') == '1'   # il transformer non fa le corse per D

RETI = OrderedDict([
    ('gru64', dict(tipo='gru', nascosto=64, strati=1)),
    ('gru128', dict(tipo='gru', nascosto=128, strati=1)),
    ('gru256', dict(tipo='gru', nascosto=256, strati=1)),
    ('gru512', dict(tipo='gru', nascosto=512, strati=1)),
    ('gru2x256', dict(tipo='gru', nascosto=256, strati=2)),
    ('transformer', dict(tipo='transformer')),
])
# costo relativo di una corsa (secondi misurati nelle prove, per ordinare i lavori dai più lunghi ai più corti)
COSTO = {'gru64': 1.0, 'gru128': 0.6, 'gru256': 0.75, 'gru512': 2.2, 'gru2x256': 1.3, 'transformer': 6.0}
RIFERIMENTO_E95 = os.path.join(QUI, '..', 'risultati', 'e3c95_corse.jsonl')


def reti_scelte():
    filtro = [s for s in os.environ.get('RETI', '').split(',') if s]
    for s in filtro:
        if s not in RETI:
            sys.exit('rete sconosciuta: %s' % s)
    return [r for r in RETI if not filtro or r in filtro]


# ---------------------------------------------------------------- testi

def selezione(t):
    """Nomi dei testi di ia05 fra quelli del catalogo di e3c95: Voynich (intero, A, B), lingue, generatori e
    gibberish, i due controlli, e le versioni a parole rimescolate (per D) di Voynich intero, lingue, generatori e
    gibberish."""
    sel = []
    for nome, v in t.items():
        r = v['ruolo']
        if r in ('voynich', 'lingua', 'generatore'):
            sel.append(nome)
        elif r == 'controllo':
            sel.append(nome)
        elif r == 'rimescolato':
            orig = nome.replace(', parole rimescolate nella riga', '')
            if orig in t and t[orig]['ruolo'] in ('voynich', 'lingua', 'generatore') and \
                    orig not in ('Voynich A', 'Voynich B'):
                sel.append(nome)
    filtro = [s for s in os.environ.get('TESTI', '').split('|') if s]
    if filtro:
        sel = [k for k in sel if any((k == s[1:]) if s.startswith('=') else (s in k) for s in filtro)]
    return sel


def catalogo():
    """Catalogo completo di e3c95 (serve per gli alfabeti dei gruppi, che devono restare quelli di e3c95) e nomi scelti."""
    filtro = os.environ.pop('TESTI', None)
    try:
        t = e95.catalogo()
    finally:
        if filtro is not None:
            os.environ['TESTI'] = filtro
    return t, selezione(t)


def prepara(t, nomi):
    """Flussi codificati per (testo, seme): come e95.prepara, ma solo per i testi scelti e senza prove di altri testi.
    Gli alfabeti sono calcolati sul catalogo intero, quindi identici a quelli di e3c95."""
    alfabeti = {}
    for g in {v['gruppo'] for v in t.values()}:
        membri = [v for v in t.values() if v['gruppo'] == g]
        esplicito = [v['alfabeto'] for v in membri if v.get('alfabeto')]
        alfabeti[g] = esplicito[0] if esplicito else e95.frequenti([v['blocchi'] for v in membri])
    lavori, scarti = [], []
    for nome in nomi:
        v = t[nome]
        voc = sorted(alfabeti[v['gruppo']] | {' ', '\n', e95.RARO})
        idx = {s: i for i, s in enumerate(voc)}
        for seme in SEMI:
            d = e95.dividi_blocchi(v['blocchi'], seme)
            if d is None:
                scarti.append(nome)
                break
            if v['trasforma']:
                rnd = random.Random(7919 * seme + 1)
                f = e95.rimescola_parole if v['trasforma'] == 'parole' else e95.rimescola_lettere
                d = [f(x, rnd) for x in d]
            add, val, prova = (e95.flusso(x)[:q] for x, q in zip(d, (N_ADD, N_VAL, N_PROVA)))

            def cod(seq):
                return [idx.get(s, idx[e95.RARO]) for s in seq]
            lavori.append(dict(testo=nome, seme=seme, V=len(voc), add=cod(add), val=cod(val), prova=cod(prova)))
    return lavori, scarti


# ---------------------------------------------------------------- modelli

def avvia_processo():
    import torch
    torch.set_num_threads(int(os.environ.get('THREAD', 1)))
    torch.use_deterministic_algorithms(True)


def costruisci(rete, V):
    import torch.nn as nn
    import torch.nn.functional as F
    cfg = RETI[rete]

    class GRU(nn.Module):
        # stesso ordine di creazione di e3c95 (immersione, GRU, caduta, uscita): con 1 strato e 128 unità i pesi
        # iniziali sono identici a quelli di e3c95
        def __init__(self):
            super().__init__()
            self.emb = nn.Embedding(V, EMB)
            self.gru = nn.GRU(EMB, cfg['nascosto'], num_layers=cfg['strati'], batch_first=True)
            self.caduta = nn.Dropout(CADUTA)
            self.out = nn.Linear(cfg['nascosto'], V)

        def forward(self, x):
            y, _ = self.gru(self.emb(x))
            return self.out(self.caduta(y))

    class Blocco(nn.Module):
        def __init__(self, d, teste, p):
            super().__init__()
            self.teste = teste
            self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
            self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
            self.m1, self.m2 = nn.Linear(d, 4 * d), nn.Linear(4 * d, d)
            self.att_caduta, self.caduta = nn.Dropout(p), nn.Dropout(p)

        def forward(self, x, maschera):
            B, T, D = x.shape
            h = D // self.teste
            q, k, v = self.qkv(self.ln1(x)).split(D, dim=2)
            q, k, v = (z.view(B, T, self.teste, h).transpose(1, 2) for z in (q, k, v))
            att = (q @ k.transpose(-2, -1)) / math.sqrt(h)
            att = att.masked_fill(~maschera[:T, :T], float('-inf')).softmax(-1)
            y = (self.att_caduta(att) @ v).transpose(1, 2).reshape(B, T, D)
            x = x + self.caduta(self.proj(y))
            return x + self.caduta(self.m2(F.gelu(self.m1(self.ln2(x)))))

    class Transformer(nn.Module):
        def __init__(self):
            super().__init__()
            import torch
            self.tok, self.pos = nn.Embedding(V, TF_DIM), nn.Embedding(LUNG, TF_DIM)
            self.caduta = nn.Dropout(TF_CADUTA)
            self.blocchi = nn.ModuleList(Blocco(TF_DIM, TF_TESTE, TF_CADUTA) for _ in range(TF_STRATI))
            self.ln = nn.LayerNorm(TF_DIM)
            self.out = nn.Linear(TF_DIM, V)
            self.register_buffer('maschera', torch.tril(torch.ones(LUNG, LUNG, dtype=torch.bool)), persistent=False)
            self.register_buffer('posizioni', torch.arange(LUNG), persistent=False)

        def forward(self, x):
            T = x.shape[1]
            h = self.caduta(self.tok(x) + self.pos(self.posizioni[:T]))
            for b in self.blocchi:
                h = b(h, self.maschera)
            return self.out(self.caduta(self.ln(h)))

    return GRU() if cfg['tipo'] == 'gru' else Transformer()


def bpc_gru(m, p):
    """BPC su tutta la sequenza con lo stato portato dall'inizio alla fine (come e3c95)."""
    import torch
    import torch.nn.functional as F
    m.eval()
    with torch.no_grad():
        logit = m(p[None, :-1])[0]
        bpc = F.cross_entropy(logit, p[1:]).item() / math.log(2)
    m.train()
    return bpc


def finestre_valutazione(N):
    """Per una sequenza di N segni: elenco di (partenza, quanti_ultimi_bersagli_da_contare). Finestre di LUNG+1 segni
    (LUNG in ingresso); la prima conta tutti i LUNG bersagli, le altre solo gli ultimi TF_PASSO_VAL (l'ultima gli
    ultimi che mancano), così ogni segno si predice una volta sola."""
    out = [(0, LUNG)]
    ultimo = LUNG                      # indice dell'ultimo bersaglio già contato
    while ultimo < N - 1:
        nuovo = min(ultimo + TF_PASSO_VAL, N - 1)
        out.append((nuovo - LUNG, nuovo - ultimo))
        ultimo = nuovo
    return out


def bpc_transformer(m, p):
    """BPC con finestre che avanzano di TF_PASSO_VAL segni: ogni segno è predetto con gli ultimi 33-64 segni con
    TF_PASSO_VAL = 32 (i primi LUNG segni con quelli che ci sono)."""
    import torch
    import torch.nn.functional as F
    finestra = torch.arange(LUNG + 1)
    fin = finestre_valutazione(len(p))
    m.eval()
    tot = 0.0
    with torch.no_grad():
        for i in range(0, len(fin), 128):
            gruppo = fin[i:i + 128]
            partenze = torch.tensor([a for a, _ in gruppo])
            xs = p[partenze[:, None] + finestra]
            logit = m(xs[:, :-1])
            perd = F.cross_entropy(logit.reshape(-1, logit.shape[-1]), xs[:, 1:].reshape(-1),
                                   reduction='none').view(len(gruppo), LUNG)
            for j, (_, n) in enumerate(gruppo):
                tot += perd[j, LUNG - n:].sum().item()
    m.train()
    return tot / (len(p) - 1) / math.log(2)


def corsa(lavoro):
    import numpy as np
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    inizio = time.time()
    rete, seme, V = lavoro['rete'], lavoro['seme'], lavoro['V']
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = costruisci(rete, V)
    gru = RETI[rete]['tipo'] == 'gru'
    lr = LR if gru else TF_LR
    opt = torch.optim.AdamW(m.parameters(), lr=lr, weight_decay=DECADIMENTO)
    add = torch.tensor(lavoro['add'], dtype=torch.long)
    prove_t = OrderedDict([('@val', torch.tensor(lavoro['val'], dtype=torch.long)),
                           ('', torch.tensor(lavoro['prova'], dtype=torch.long))])
    finestra = torch.arange(LUNG + 1)
    valuta = bpc_gru if gru else bpc_transformer
    curve = {k: [] for k in prove_t}
    perdita, perdite = 0.0, []
    for passo in range(1, PASSI + 1):
        if not gru and passo <= TF_RISCALDAMENTO:
            for g in opt.param_groups:
                g['lr'] = lr * passo / TF_RISCALDAMENTO
        partenze = torch.from_numpy(rng.integers(0, len(add) - LUNG - 1, size=LOTTO))
        xb = add[partenze[:, None] + finestra]
        logit = m(xb[:, :-1])
        loss = F.cross_entropy(logit.reshape(-1, V), xb[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(m.parameters(), TAGLIO)
        opt.step()
        perdita += loss.item()
        if passo % OGNI == 0:
            for k, p in prove_t.items():
                curve[k].append(round(valuta(m, p), 5))
            perdite.append(round(perdita / OGNI / math.log(2), 5))
            perdita = 0.0
            v = curve['@val']
            if len(v) - 1 - v.index(min(v)) >= PAZIENZA:
                break
    return dict(rete=rete, testo=lavoro['testo'], seme=seme, V=V, parametri=sum(p.numel() for p in m.parameters()),
                h1=round(e95.h1(lavoro['add'], lavoro['prova'], V), 5), validazione=curve['@val'], curva=curve[''],
                curve_altre={}, addestramento=perdite, passi=passo, segni_per_valutazione=OGNI * LOTTO * LUNG,
                segni_addestramento=len(lavoro['add']), secondi=round(time.time() - inizio, 1))


# ---------------------------------------------------------------- analisi

def controlli(tab, corse=(), soglia=None):
    """C+ e C- come in e3c95 (e95.controlli). Differenza di C+: media dei semi di BPC(cifrato) - BPC(latino), appaiata
    seme per seme. Superato se |media| <= SOGLIA_POSITIVO (0,03). In e3c95 la soglia era 0,02 con 10 semi e deviazione
    standard appaiata 0,014 (circa 4,5 errori standard); nelle prove le reti più grandi hanno una deviazione standard
    appaiata fino a 0,02 e qui i semi sono 3-5, quindi si porta a 0,03. Si riporta anche l'esito con 0,02."""
    soglia = SOGLIA_POSITIVO if soglia is None else soglia
    out = OrderedDict()
    a, b = 'Latin', 'Latin, cifrato con una sostituzione (controllo positivo)'
    if a in tab and b in tab:
        ba = {c['seme']: e95.bpc_scelta(c) for c in corse if c['testo'] == a}
        bb = {c['seme']: e95.bpc_scelta(c) for c in corse if c['testo'] == b}
        ds_ = [bb[s] - ba[s] for s in sorted(set(ba) & set(bb))]
        d = statistics.mean(ds_)
        dsa = statistics.stdev(ds_) if len(ds_) > 1 else None
        out['positivo'] = dict(differenza_bpc=d, ds_appaiata=dsa, errore_standard=dsa / math.sqrt(len(ds_)) if dsa
                               is not None else None, semi=len(ds_), soglia=soglia, superato=abs(d) <= soglia,
                               superato_con_soglia_e3c95_0_02=abs(d) <= 0.02)
    neg = 'Voynich, segni rimescolati (controllo negativo)'
    if neg in tab and 'Voynich' in tab:
        g_lingue = [v['G']['media'] for v in tab.values() if v['ruolo'] == 'lingua']
        gn, gv = tab[neg]['G'], tab['Voynich']['G']
        out['negativo'] = dict(G_rimescolato=gn['media'], G_voynich=gv['media'], G_min_lingue=min(g_lingue),
                               superato=gn['media'] < min(g_lingue) and gv['media'] - gn['media'] >
                               5 * max(gn['ds'], gv['ds']))
    return out


def per_seme(corse, k):
    """{(rete, testo): {seme: misura}} per la misura k di misure_corsa (G, bpc, E90...)."""
    out = {}
    for c in corse:
        out.setdefault((c['rete'], c['testo']), {})[c['seme']] = e95.misure_corsa(c)[k]
    return out


def differenza_appaiata(dati, testo, a, b):
    """Media e ds della differenza (b - a) seme per seme; None se mancano dati."""
    da, db = dati.get((a, testo)), dati.get((b, testo))
    if not da or not db:
        return None
    ds = [db[s] - da[s] for s in sorted(set(da) & set(db)) if da[s] is not None and db[s] is not None]
    return e95.media_ds(ds) if len(ds) > 1 else None


def verifica_128(corse):
    """Le corse gru128 contro quelle di e3c95 (stessi testi, stessi semi): curve uguali?"""
    if not os.path.exists(RIFERIMENTO_E95):
        return None
    rif = {}
    for l in open(RIFERIMENTO_E95, encoding='utf-8'):
        if l.strip():
            c = json.loads(l)
            rif[c['testo'], c['seme']] = c
    n = identiche = 0
    massimo = 0.0
    per_testo = OrderedDict()
    for c in corse:
        if c['rete'] != 'gru128' or (c['testo'], c['seme']) not in rif:
            continue
        r = rif[c['testo'], c['seme']]
        n += 1
        stessa = c['curva'] == r['curva'] and c['validazione'] == r['validazione']
        identiche += stessa
        dm = abs(e95.bpc_scelta(c) - e95.bpc_scelta(r))
        massimo = max(massimo, dm)
        p = per_testo.setdefault(c['testo'], dict(n=0, identiche=0, max_diff_bpc=0.0))
        p['n'] += 1
        p['identiche'] += stessa
        p['max_diff_bpc'] = max(p['max_diff_bpc'], dm)
    if not n:
        return None
    # tolleranza se non sono identiche: la differenza di BPC nel punto scelto resta sotto 0,01 e quella delle medie
    # di G sotto 0,005 (circa il rumore dei semi: errore standard di G fra 5 semi circa 0,006)
    return dict(corse_confrontate=n, curve_identiche=identiche, max_diff_bpc_punto_scelto=massimo,
                tolleranza_bpc=0.01, superata=identiche == n or massimo <= 0.01, per_testo=per_testo)


def distanze_profilo(tab, chiavi, voynich='Voynich'):
    """Testi ordinati per distanza dal Voynich sul profilo `chiavi`: ogni misura divisa per la sua deviazione standard
    fra le lingue (della stessa rete); distanza euclidea. Esclusi i rimescolati, le parti del Voynich, la
    sensibilità e i testi senza una delle misure (come e95.analizza)."""
    lingue_n = [n for n, v in tab.items() if v['ruolo'] == 'lingua']
    ds_l = {}
    for k in chiavi:
        vs = [tab[n][k]['media'] for n in lingue_n if tab[n].get(k)]
        if len(vs) < 3:
            return None
        ds_l[k] = statistics.stdev(vs)
    if voynich not in tab or not all(tab[voynich].get(k) for k in chiavi):
        return None
    dist = []
    for n, v in tab.items():
        if v['ruolo'] in ('rimescolato', 'voynich', 'sensibilita') or not all(v.get(k) for k in chiavi):
            continue
        d = math.sqrt(sum(((v[k]['media'] - tab[voynich][k]['media']) / ds_l[k]) ** 2 for k in chiavi))
        dist.append(dict(testo=n, ruolo=v['ruolo'], distanza=d))
    return sorted(dist, key=lambda x: x['distanza'])


def lettura_vicini(tab, nomi_generatori):
    """Lettura 2: i testi più vicini al Voynich intero, sul profilo (G, E90, D) se la rete ha D (cioè ha le corse a
    parole rimescolate) e sempre sul profilo (G, E90). Ritorna, per ogni profilo, i 6 più vicini, la classe del più
    vicino, quanti generatori stanno fra i 3 più vicini e se sono proprio i 3 generatori."""
    out = OrderedDict()
    for etichetta, chiavi in (('G_E90_D', ('G', 'E90', 'D')), ('G_E90', ('G', 'E90'))):
        lista = distanze_profilo(tab, chiavi)
        if not lista:
            continue
        primi = lista[:3]
        prima_non_gen = next((x for x in lista if x['testo'] not in nomi_generatori), None)
        out[etichetta] = dict(
            piu_vicini=[(x['testo'], x['ruolo'], round(x['distanza'], 3)) for x in lista[:6]],
            classe_del_piu_vicino=lista[0]['ruolo'],
            generatori_fra_i_3_piu_vicini=sum(1 for x in primi if x['testo'] in nomi_generatori),
            prima_non_generatore=(prima_non_gen['testo'], round(prima_non_gen['distanza'], 3))
            if prima_non_gen else None,
            restano_i_generatori=all(x['testo'] in nomi_generatori for x in primi))
    return out


def analizza(t, corse, reti):
    nomi_gen = {'Timm e Schinner (seme 1)', "Voynichizzatore v21 (libro d'esempio)", 'Naibbe'}
    dati_G = per_seme(corse, 'G')
    per_rete = OrderedDict()
    for r in reti:
        cs = [c for c in corse if c['rete'] == r]
        if not cs:
            continue
        tab, _, confronti, profili = e95.analizza(t, cs)
        per_rete[r] = dict(tab=tab, confronti=confronti, profili=profili, controlli=controlli(tab, cs),
                           parametri=cs[0]['parametri'], corse=len(cs),
                           corse_al_limite=sum(1 for c in cs if c['passi'] >= PASSI),
                           secondi_per_corsa=statistics.mean(c['secondi'] for c in cs),
                           vicini=lettura_vicini(tab, nomi_gen))
    # lettura 1: crescita di G con la grandezza
    testi = [n for n in t if any(n in x['tab'] for x in per_rete.values())]
    gru = [r for r in per_rete if RETI[r]['tipo'] == 'gru']
    crescita = OrderedDict()
    for n in testi:
        ruolo = t[n]['ruolo']
        if ruolo == 'rimescolato':
            continue
        e = OrderedDict(ruolo=ruolo)
        e['DG512'] = differenza_appaiata(dati_G, n, 'gru64', 'gru512')
        e['DG256'] = differenza_appaiata(dati_G, n, 'gru64', 'gru256')
        e['DG2x256_su_256'] = differenza_appaiata(dati_G, n, 'gru256', 'gru2x256')
        e['DG_transformer_su_gru128'] = differenza_appaiata(dati_G, n, 'gru128', 'transformer')
        # DGmax sui semi comuni a tutte le reti GRU presenti per questo testo (1-3 con il disegno preregistrato)
        presenti = [r for r in gru if dati_G.get((r, n))]
        comuni = sorted(set.intersection(*(set(dati_G[(r, n)]) for r in presenti))) if presenti else []
        if 'gru64' in presenti and len(presenti) > 1 and comuni:
            medie = {r: statistics.mean(dati_G[(r, n)][s_] for s_ in comuni) for r in presenti}
            migliore = max(medie, key=medie.get)
            e['rete_migliore'] = migliore
            e['semi_comuni'] = comuni
            e['DGmax'] = medie[migliore] - medie['gru64']
        crescita[n] = e
    lingue_n = [n for n in crescita if crescita[n]['ruolo'] == 'lingua']
    lettura1 = OrderedDict()
    for k in ('DG512', 'DG256', 'DGmax'):
        v = [crescita[n][k]['media'] if isinstance(crescita[n].get(k), dict) else crescita[n].get(k)
             for n in lingue_n]
        v = [x for x in v if x is not None]
        if len(v) < 3:
            continue
        info = OrderedDict(lingue_mediana=statistics.median(v), lingue_minimo=min(v), lingue_massimo=max(v),
                           lingue_con_crescita_positiva=sum(1 for x in v if x > 0), lingue=len(v),
                           lingue_guadagnano=statistics.median(v) >= SOGLIA_CRESCITA and
                           sum(1 for x in v if x > 0) >= 0.75 * len(v))
        for n in ('Voynich', 'Voynich A', 'Voynich B', 'Timm e Schinner (seme 1)', "Voynichizzatore v21 (libro d'esempio)",
                  'Naibbe', 'Gibberish (Gaskell e Bowern)', 'Voynich, segni rimescolati (controllo negativo)',
                  'Latin, cifrato con una sostituzione (controllo positivo)'):
            if n in crescita:
                x = crescita[n].get(k)
                x = x['media'] if isinstance(x, dict) else x
                if x is not None:
                    info[n] = e95.posizione(x, v)
                    info[n]['valore'] = x
                    if n.startswith('Voynich') and 'controllo' not in n:
                        # regola preregistrata: se le lingue guadagnano, il Voynich "cresce meno" se sta sotto
                        # l'intervallo delle lingue o, dentro, con al più il 25% delle lingue sotto di lui;
                        # se le lingue non guadagnano la domanda non ha risposta (None)
                        info[n]['cresce_meno'] = (info[n]['dentro'] == 'sotto' or info[n]['frazione_sotto'] <= 0.25)                             if info['lingue_guadagnano'] else None
        lettura1[k] = info
    # lettura 3: E90 e scarto del Voynich rispetto alle lingue, per rete
    lettura3 = OrderedDict()
    for r, x in per_rete.items():
        tab = x['tab']
        ling = [n for n in tab if tab[n]['ruolo'] == 'lingua']
        e = OrderedDict()
        for k in ('E90', 'scarto'):
            vals = [tab[n][k]['media'] for n in ling if tab[n].get(k)]
            if not vals:
                continue
            for n in ('Voynich', 'Voynich A', 'Voynich B'):
                if n in tab and tab[n].get(k):
                    p = e95.posizione(tab[n][k]['media'], vals)
                    p['valore'] = tab[n][k]['media']
                    p['sotto_tutte_le_lingue'] = tab[n][k]['media'] < min(vals)
                    e['%s, %s' % (k, n)] = p
        lettura3[r] = e
    # avvertenza sul limite dei passi, per rete
    for r, x in per_rete.items():
        x['frazione_al_limite'] = x['corse_al_limite'] / x['corse']
        x['riserva_limite_passi'] = x['frazione_al_limite'] > 0.25
    # lettura 4: il transformer dice lo stesso? (a) G del Voynich dentro l'intervallo delle lingue, (b) E90 del Voynich
    # sotto tutte le lingue, (c) i 3 più vicini sul profilo (G, E90) sono i 3 generatori, (d) C+ e C- riusciti
    lettura4 = None
    if 'transformer' in per_rete:
        x = per_rete['transformer']
        pg = x['confronti'].get('G', {}).get('Voynich')
        e90 = lettura3['transformer'].get('E90, Voynich')
        vic = (x['vicini'] or {}).get('G_E90')
        ctrl = x['controlli']
        lettura4 = OrderedDict(
            a_G_dentro_le_lingue=None if not pg else pg['dentro'] == 'dentro',
            b_E90_sotto_tutte_le_lingue=None if not e90 else e90['sotto_tutte_le_lingue'],
            c_i_3_piu_vicini_sono_i_generatori=None if not vic else vic['restano_i_generatori'],
            d_controlli_riusciti=None if not ctrl.get('positivo') or not ctrl.get('negativo')
            else bool(ctrl['positivo']['superato'] and ctrl['negativo']['superato']),
            frazione_corse_al_limite=x['frazione_al_limite'], riserva_limite_passi=x['riserva_limite_passi'])
        val = [v for k, v in lettura4.items() if k[0] in 'abcd']
        lettura4['dice_lo_stesso'] = None if any(v is None for v in val) else all(val)
    return per_rete, crescita, lettura1, lettura3, lettura4


SOGLIA_CRESCITA = 0.01   # G: le lingue "guadagnano" con la grandezza se la mediana di DG512 è almeno questa e
                         # almeno il 75% delle lingue ha DG512 positivo


def f3(d, k='media'):
    return '–' if not d else '%.3f' % d[k]


def scrivi(t, corse, reti, versioni):
    per_rete, crescita, lettura1, lettura3, lettura4 = analizza(t, corse, reti)
    verifica = verifica_128(corse)
    ris = OrderedDict(
        esperimento='ia05',
        parametri=dict(N_ADD=N_ADD, N_VAL=N_VAL, N_PROVA=N_PROVA, PASSI=PASSI, OGNI=OGNI, PAZIENZA=PAZIENZA,
                       SEMI=SEMI, SEMI_GRANDI=SEMI_GRANDI, GRANDI=GRANDI, TF_SENZA_RIMESCOLATI=TF_SENZA_RIMESCOLATI, LUNG=LUNG, LOTTO=LOTTO, EMB=EMB, CADUTA=CADUTA, LR=LR, DECADIMENTO=DECADIMENTO,
                       TAGLIO=TAGLIO, SOGLIA_POSITIVO=SOGLIA_POSITIVO, SOGLIA_CRESCITA=SOGLIA_CRESCITA,
                       TF_CADUTA=TF_CADUTA, TF_LR=TF_LR, TF_RISCALDAMENTO=TF_RISCALDAMENTO,
                       TF_PASSO_VAL=TF_PASSO_VAL, TF_DIM=TF_DIM, TF_TESTE=TF_TESTE, TF_STRATI=TF_STRATI,
                       reti={r: RETI[r] for r in reti}, SOLO_CONTROLLI=SOLO_CONTROLLI),
        versioni=versioni,
        verifica_gru128_contro_e3c95=verifica,
        controlli={r: x['controlli'] for r, x in per_rete.items()},
        per_rete=OrderedDict((r, dict(parametri=x['parametri'], corse=x['corse'],
                                      corse_al_limite=x['corse_al_limite'], frazione_al_limite=x['frazione_al_limite'],
                                      riserva_limite_passi=x['riserva_limite_passi'],
                                      secondi_per_corsa=x['secondi_per_corsa'], testi=x['tab'],
                                      confronti=x['confronti'], profili=x['profili'], lettura2=x['vicini']))
                             for r, x in per_rete.items()),
        lettura1_crescita_di_G=lettura1, crescita_per_testo=crescita, lettura3_E90_e_scarto=lettura3,
        lettura4_transformer=lettura4)
    with open(os.path.join(USCITA, NOME + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(ris, f, ensure_ascii=False, indent=1)
        f.write('\n')

    r = ['# IA5 (ia05) — reti più grandi e un piccolo transformer', '',
         'Stesso disegno di e3c95 (%d segni di addestramento, %d di validazione, %d di prova, al massimo %d passi, '
         'arresto con pazienza %d); semi %s; reti: %s.' % (N_ADD, N_VAL, N_PROVA, PASSI, PAZIENZA,
                                                           ', '.join(map(str, SEMI)), ', '.join(per_rete)),
         'Valori: media dei semi (deviazione standard fra i semi).', '']
    # le righe dei controlli stanno all'inizio, come in e3c95
    r += ['## Controlli', '']
    for rete, x in per_rete.items():
        for k, v in x['controlli'].items():
            r.append('- controllo %s: %s, %s' % (k, rete, ', '.join(
                '%s %s' % (a, ('%.4f' % b) if isinstance(b, float) else b) for a, b in v.items())))
    r += ['', '## Verifica interna: gru128 contro e3c95', '']
    if verifica:
        r.append('- %d corse confrontate, %d con curve identiche, differenza massima di BPC nel punto scelto %.5f '
                 '(tolleranza %.2f): %s' % (verifica['corse_confrontate'], verifica['curve_identiche'],
                                            verifica['max_diff_bpc_punto_scelto'], verifica['tolleranza_bpc'],
                                            'superata' if verifica['superata'] else 'NON superata'))
    else:
        r.append('- non confrontabile (manca gru128 o il riferimento)')
    r += ['', '## Reti', '', '| rete | parametri (alfabeto del primo testo) | corse | al limite dei passi | riserva (>25%) | s/corsa |', '|---|---|---|---|---|---|']
    for rete, x in per_rete.items():
        r.append('| %s | %d | %d | %d | %s | %.0f |' % (rete, x['parametri'], x['corse'], x['corse_al_limite'],
                                                       'sì' if x['riserva_limite_passi'] else 'no',
                                                       x['secondi_per_corsa']))
    nomi = [n for n in t if any(n in x['tab'] for x in per_rete.values()) and t[n]['ruolo'] != 'rimescolato']
    for k, titolo in (('G', 'G'), ('E90', 'E90 (letture)'), ('D', 'D (bit per segno)'), ('bpc', 'BPC'),
                      ('scarto', 'scarto')):
        r += ['', '## %s per rete' % titolo, '', '| testo | ruolo | %s |' % ' | '.join(per_rete),
              '|---|---|%s|' % '|'.join('---' for _ in per_rete)]
        for n in nomi:
            cel = []
            for rete, x in per_rete.items():
                d = x['tab'].get(n, {}).get(k)
                cel.append('–' if not d else '%.3f (%.3f)' % (d['media'], d['ds']))
            r.append('| %s | %s | %s |' % (n, t[n]['ruolo'], ' | '.join(cel)))
    r += ['', '## Lettura 1: crescita di G con la grandezza', '',
          'DG512 = G(gru512) - G(gru64), seme per seme. Le lingue "guadagnano" se la mediana è almeno %.2f e almeno '
          'il 75%% ha crescita positiva.' % SOGLIA_CRESCITA, '']
    for k, info in lettura1.items():
        r.append('- %s, lingue: mediana %.3f, da %.3f a %.3f, %d su %d positive: le lingue %s' % (
            k, info['lingue_mediana'], info['lingue_minimo'], info['lingue_massimo'],
            info['lingue_con_crescita_positiva'], info['lingue'],
            'guadagnano' if info['lingue_guadagnano'] else 'NON guadagnano abbastanza'))
        for n, p in info.items():
            if isinstance(p, dict) and 'valore' in p:
                cm = p.get('cresce_meno', 'assente')
                r.append('  - %s: %+.3f, %s l\'intervallo delle lingue, lingue sotto: %.0f%%%s' % (
                    n, p['valore'], p['dentro'], 100 * p['frazione_sotto'],
                    '' if cm == 'assente' else ', il Voynich cresce meno delle lingue: %s' % (
                        'non valutabile (le lingue non guadagnano)' if cm is None else ('sì' if cm else 'no'))))
    r += ['', '| testo | DG256 | DG512 | DGmax (rete) | DG2x256 su 256 | DG transformer su gru128 |', '|---|---|---|---|---|---|']
    for n, e in crescita.items():
        r.append('| %s | %s | %s | %s | %s | %s |' % (
            n, f3(e.get('DG256')), '–' if not e.get('DG512') else '%.3f (%.3f)' % (e['DG512']['media'], e['DG512']['ds']),
            '–' if e.get('DGmax') is None else '%.3f (%s)' % (e['DGmax'], e['rete_migliore']),
            f3(e.get('DG2x256_su_256')), f3(e.get('DG_transformer_su_gru128'))))
    r += ['', '## Lettura 2: testi più vicini al Voynich sul profilo (G, E90, D), per rete', '',
          'Ogni misura divisa per la sua deviazione standard fra le lingue, a quella rete; distanza euclidea.', '']
    for rete, x in per_rete.items():
        for etichetta, v in x['vicini'].items():
            r.append('- %s, profilo %s: %s. Generatori fra i 3 più vicini: %d (restano i generatori: %s); primo non '
                     'generatore: %s' % (rete, etichetta.replace('_', ', '),
                                         '; '.join('%s (%s) %.2f' % q for q in v['piu_vicini']),
                                         v['generatori_fra_i_3_piu_vicini'],
                                         'sì' if v['restano_i_generatori'] else 'no',
                                         '–' if not v['prima_non_generatore'] else '%s %.2f' % v['prima_non_generatore']))
    r += ['', '## Lettura 3: E90 e scarto del Voynich rispetto alle lingue, per rete', '']
    for rete, e in lettura3.items():
        for k, p in e.items():
            r.append('- %s, %s: %.3f, %s l\'intervallo delle lingue [%.3f, %.3f]%s' % (
                rete, k, p['valore'], p['dentro'], p['minimo'], p['massimo'],
                ' (sotto tutte le lingue)' if p['sotto_tutte_le_lingue'] else ''))
    r += ['', '## Lettura 4: il transformer dice lo stesso?', '']
    if lettura4:
        for k, v in lettura4.items():
            r.append('- %s: %s' % (k, v if not isinstance(v, float) else '%.3f' % v))
    else:
        r.append('- transformer non presente')
    r += ['', '## Posizione rispetto alle lingue (G, D), per rete', '']
    for rete, x in per_rete.items():
        for k in ('G', 'D'):
            for n, p in x['confronti'].get(k, {}).items():
                if p and n in ('Voynich', 'Voynich A', 'Voynich B'):
                    r.append('- %s, %s, %s: %.3f, %s l\'intervallo delle lingue [%.3f, %.3f], lingue sotto: %.0f%%' % (
                        rete, k, n, x['tab'][n][k]['media'], p['dentro'], p['minimo'], p['massimo'],
                        100 * p['frazione_sotto']))
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(r) + '\n')
    return ris


# ---------------------------------------------------------------- esecuzione

def main():
    import torch
    import numpy
    versioni = dict(python=sys.version.split()[0], torch=torch.__version__, numpy=numpy.__version__)
    os.makedirs(USCITA, exist_ok=True)
    reti = reti_scelte()
    t, nomi = catalogo()
    print('testi scelti: %d (su %d del catalogo di e3c95); reti: %s; semi: %s' % (len(nomi), len(t), ', '.join(reti),
                                                                                   SEMI), flush=True)
    for nome in nomi:
        v = t[nome]
        print('  %-70s %-13s blocchi %4d segni %7d' % (nome, v['ruolo'], len(v['blocchi']),
                                                      e95.lunghezza(v['blocchi'])), flush=True)
    base, scarti = prepara(t, nomi)
    if scarti:
        print('troppo corti, esclusi: %s' % ', '.join(scarti), flush=True)
    lavori = [dict(l, rete=r) for r in reti for l in base if l['testo'] not in scarti
              and (r not in GRANDI or l['seme'] in SEMI_GRANDI)
              and not (r == 'transformer' and TF_SENZA_RIMESCOLATI and t[l['testo']]['ruolo'] == 'rimescolato')]
    percorso = os.path.join(USCITA, 'ia05_corse.jsonl')
    corse = []
    if os.environ.get('RIPRENDI') == '1' and os.path.exists(percorso):
        corse = [json.loads(l) for l in open(percorso, encoding='utf-8') if l.strip()]
    else:
        open(percorso, 'w').close()
    fatte = {(c['rete'], c['testo'], c['seme']) for c in corse}
    da_fare = [l for l in lavori if (l['rete'], l['testo'], l['seme']) not in fatte]
    da_fare.sort(key=lambda l: -COSTO[l['rete']])        # le corse più lunghe per prime: la coda finale è corta
    print('corse: %d da fare, %d già fatte' % (len(da_fare), len(fatte)), flush=True)
    processi = int(os.environ.get('PROCESSI', 8))
    inizio = time.time()
    with get_context('spawn').Pool(processi, initializer=avvia_processo) as pool:
        for i, c in enumerate(pool.imap_unordered(corsa, da_fare), 1):
            corse.append(c)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(c, ensure_ascii=False) + '\n')
            m = e95.misure_corsa(c)
            print('[%d/%d %.0f min] %s | %s seme %d: H1 %.3f BPC %.3f G %.3f epoche %.1f (%d passi, %.0f s)' % (
                i, len(da_fare), (time.time() - inizio) / 60, c['rete'], c['testo'], c['seme'], m['h1'], m['bpc'],
                m['G'], m['epoche_scelte'], c['passi'], c['secondi']), flush=True)
    # solo le corse della selezione attuale entrano nell'analisi
    chiavi = {(l['rete'], l['testo'], l['seme']) for l in lavori}
    corse = [c for c in corse if (c['rete'], c['testo'], c['seme']) in chiavi]
    ris = scrivi(t, corse, reti, versioni)
    for rete, ctrl in ris['controlli'].items():
        for k, v in ctrl.items():
            print('controllo %s: %s %s' % (k, rete, v), flush=True)
    print('verifica gru128 contro e3c95: %s' % {k: v for k, v in (ris['verifica_gru128_contro_e3c95'] or {}).items()
                                                if k != 'per_testo'}, flush=True)


if __name__ == '__main__':
    main()
