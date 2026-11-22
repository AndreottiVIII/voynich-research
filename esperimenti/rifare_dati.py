# -*- coding: utf-8 -*-
"""IA32, modulo di supporto: l'imitatore "pieno" (una GRU 2 x 256 addestrata su quasi tutto il libro) e le sue istantanee.

In parole semplici
- Gli imitatori di ia20-ia24 si addestrano su circa il 70% dei fogli (5 pieghe) e si fermano al minimo di validazione: "lisciano" le statistiche
  esatte del libro. Qui c'e' UN modello solo per mondo, addestrato su tutti i fogli tranne una piccola parte tenuta fuori (`FUORI32`, predefinita 0,15) e una
  parte di validazione (`VAL32`, 0,07): serve per fermare l'addestramento e basta. I fogli tenuti fuori servono SOLO a misurare la copia e a addestrare
  il giudice nuovo dell'esame: il modello non li vede mai.
- L'addestramento va oltre il minimo di validazione: dopo l'arresto (pazienza `PAZIENZA32`) continua per altre epoche (`EXTRA32` = frazione dell'epoca
  scelta, almeno `EXTRA_MIN32`). Si salvano DUE istantanee: A (il minimo di validazione) e C (la fine delle epoche in piu'). Una manopola di scrittura
  ("s") le mescola (media dei pesi): s = 0 e' A, s = 1 e' C. La guardia anti-copia dice se C copia troppo.
- Niente codice nuovo per la rete: `gradini_modelli` (M1 = GRU a due strati) e `ia16_imitatore.dati_pagine` si importano senza modificarli; qui c'e'
  solo il giro di addestramento (copia di `addestra_modello` con le due istantanee).
Variabili: FUORI32, VAL32, NASCOSTO32 (256), EPOCHE32 (200), PAZIENZA32 (12), EXTRA32 (0,5), EXTRA_MIN32 (6), PICCOLO32 (solo prove), SEME_FOGLI32.
"""
import json
import math
import os
import random
import sys
import time
from collections import OrderedDict

for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ.setdefault(_v, '1')
import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import ia07_voynich_neurale as I7  # noqa: E402
import ia16_imitatore as I16  # noqa: E402
import gradini_modelli as GM  # noqa: E402

FUORI32 = float(os.environ.get('FUORI32', 0.15))
VAL32 = float(os.environ.get('VAL32', 0.07))
NASC32 = int(os.environ.get('NASCOSTO32', 256))
EPOCHE32 = int(os.environ.get('EPOCHE32', 200))
PAZIENZA32 = int(os.environ.get('PAZIENZA32', 12))
EXTRA32 = float(os.environ.get('EXTRA32', 0.5))
EXTRA_MIN32 = int(os.environ.get('EXTRA_MIN32', 6))
PICCOLO32 = os.environ.get('PICCOLO32') == '1'
SEME_FOGLI32 = int(os.environ.get('SEME_FOGLI32', 3232))


def fogli_del_libro():
    """[(foglio, sezione)] nell'ordine di comparsa nel libro (il libro e' quello del mondo attivo)."""
    out = OrderedDict()
    for x in I7.libro_vero():
        out.setdefault(x['foglio'], x['sezione'])
    return list(out.items())


def _scegli_ogni(lista, quota, resto_acc=0.0):
    """Sceglie circa `quota` degli elementi di `lista` distribuendoli in modo regolare (accumulatore). -> (scelti, rimasti)."""
    scelti, rimasti, acc = [], [], resto_acc
    for x in lista:
        acc += quota
        if acc >= 1.0 - 1e-9:
            scelti.append(x)
            acc -= 1.0
        else:
            rimasti.append(x)
    return scelti, rimasti


def divisione_fogli(fuori=None, val=None):
    """(fogli di addestramento, di validazione, tenuti fuori): ordine casuale dentro ogni sezione (seme fisso), poi scelta regolare, cosi' ogni sezione e'
    rappresentata in proporzione. Deterministica; dipende solo dall'elenco dei fogli e dalle quote."""
    fuori = FUORI32 if fuori is None else fuori
    val = VAL32 if val is None else val
    ff = fogli_del_libro()
    rnd = random.Random(SEME_FOGLI32)
    per_sez = OrderedDict()
    for f, s in ff:
        per_sez.setdefault(s, []).append(f)
    ordine = []
    for s in sorted(per_sez):
        l = list(per_sez[s])
        rnd.shuffle(l)
        ordine += l
    f_fuori, resto = _scegli_ogni(ordine, fuori)
    f_val, f_add = _scegli_ogni(resto, val / max(1e-9, 1 - fuori))
    return sorted(f_add), sorted(f_val), sorted(f_fuori)


def pagine_per_modello(fogli, ctx):
    dp = I16.dati_pagine()
    ins = set(fogli)
    return [GM.prepara_pagina(d, ctx, False) for d in dp.values() if d['foglio'] in ins]


def contesto(f_add):
    voc = I7.vocabolario()
    dp = I16.dati_pagine()
    K, S = (40, 12) if PICCOLO32 else (GM.K_TIPI, GM.S_CAND)
    ins = set(f_add)
    ctx = GM.Ctx(voc, GM.tipi_da_pagine([d for d in dp.values() if d['foglio'] in ins], GM.Ctx(voc, [], K=K, S=S)), K=K, S=S)
    return voc, ctx


def _epoca(m, ctx, add, opt, rng):
    perdita = conti = 0.0
    chiavi = [P['Tin'] * (1 + 0.3 * u) for P, u in zip(add, rng.uniform(size=len(add)))]
    ordine = sorted(range(len(add)), key=lambda i: chiavi[i])
    lotti = [ordine[a:a + GM.LOTTO] for a in range(0, len(ordine), GM.LOTTO)]
    rng.shuffle(lotti)
    for lotto in lotti:
        Ps = [add[i] for i in lotto]
        stati = [GM.StatoRiga() for _ in Ps]
        r = 0
        while True:
            att = [b for b, P in enumerate(Ps) if r < len(P['chunks'])]
            if not att:
                break
            nl, nt = GM.passa_tratto(m, ctx, [(Ps[b], Ps[b]['chunks'][r]) for b in att], [stati[b] for b in att], addestra=True, opt=opt)
            perdita += nl
            conti += nt
            r += 1
    return round(perdita / max(conti, 1) / math.log(2), 5)


def percorso(cartella, nome):
    return os.path.join(cartella, nome)


def addestra_pieno(cartella, seme=32001, nasc=None, messaggi=None):
    """Addestra il modello pieno e salva `pieno.pt` (istantanee A e C) e `pieno.json` in `cartella`. Si puo' riprendere: se `pieno.pt` c'e' non rifa niente."""
    import torch
    nasc = NASC32 if nasc is None else nasc
    os.makedirs(cartella, exist_ok=True)
    if os.path.exists(percorso(cartella, 'pieno.pt')) and os.path.exists(percorso(cartella, 'pieno.json')):
        return json.load(open(percorso(cartella, 'pieno.json'), encoding='utf-8'))
    inizio = time.time()
    f_add, f_val, f_fuori = divisione_fogli()
    voc, ctx = contesto(f_add)
    add, val, fuori = (pagine_per_modello(f, ctx) for f in (f_add, f_val, f_fuori))
    cfg = GM.cfg_completa(1, voc, ctx, PICCOLO32)
    if not PICCOLO32:
        cfg['nasc'] = int(nasc)
    torch.manual_seed(seme)
    rng = np.random.default_rng(seme)
    m = GM.costruisci(cfg)
    m.train()
    opt = torch.optim.AdamW(m.parameters(), lr=GM.LR, weight_decay=GM.DECADIMENTO)

    def say(s):
        if messaggi:
            try:
                messaggi(s)
            except OSError:
                pass
    curva_val, curva_add = [], []
    migliore, stato_A, ep_A = None, None, 0
    for epoca in range(1, EPOCHE32 + 1):
        curva_add.append(_epoca(m, ctx, add, opt, rng))
        v = round(GM.bpc_pagine(m, ctx, val), 5)
        curva_val.append(v)
        if migliore is None or v < migliore:
            migliore, ep_A = v, epoca
            stato_A = {k: t.detach().clone() for k, t in m.state_dict().items()}
        say('epoca %d: addestramento %.4f, validazione %.4f (migliore %.4f all\'epoca %d), %.0f s' % (epoca, curva_add[-1], v, migliore, ep_A, time.time() - inizio))
        if epoca - ep_A >= PAZIENZA32:
            break
    extra = max(EXTRA_MIN32, int(math.ceil(EXTRA32 * ep_A)))
    for e in range(extra):                                  # le epoche in piu' dopo l'arresto: l'istantanea C e' la fine
        epoca += 1
        curva_add.append(_epoca(m, ctx, add, opt, rng))
        curva_val.append(round(GM.bpc_pagine(m, ctx, val), 5))
        say('epoca %d (extra %d/%d): addestramento %.4f, validazione %.4f, %.0f s' % (epoca, e + 1, extra, curva_add[-1], curva_val[-1], time.time() - inizio))
    stato_C = {k: t.detach().clone() for k, t in m.state_dict().items()}
    ris = OrderedDict([('parametri', sum(p.numel() for p in m.parameters())), ('nascosto', cfg['nasc']), ('fogli', [len(f_add), len(f_val), len(f_fuori)]),
                       ('pagine', [len(add), len(val), len(fuori)]), ('epoca_A', ep_A), ('epoche_totali', epoca), ('extra', extra),
                       ('bpc_val_A', curva_val[ep_A - 1]), ('bpc_val_C', curva_val[-1]), ('bpc_add_A', curva_add[ep_A - 1]), ('bpc_add_C', curva_add[-1]),
                       ('curva_validazione', curva_val), ('curva_addestramento', curva_add), ('piccolo', PICCOLO32), ('seme', seme)])
    for nome, st in (('A', stato_A), ('C', stato_C)):
        m.load_state_dict(st)
        m.eval()
        ris['bpc_fuori_' + nome] = round(GM.bpc_pagine(m, ctx, fuori), 5) if fuori else None
    m.load_state_dict(stato_C)
    ris['secondi'] = round(time.time() - inizio, 1)
    torch.save(dict(stato_A=stato_A, stato_C=stato_C, cfg=m.cfg, segni=list(voc['segni']), tipi=ctx.lista_tipi, f_add=f_add, f_val=f_val, f_fuori=f_fuori),
               percorso(cartella, 'pieno.pt') + '.tmp')
    os.replace(percorso(cartella, 'pieno.pt') + '.tmp', percorso(cartella, 'pieno.pt'))
    json.dump(ris, open(percorso(cartella, 'pieno.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    return ris


class Pieno:
    """Il modello pieno caricato: `modello(s)` mescola le istantanee A (s = 0) e C (s = 1) media dei pesi."""

    def __init__(self, cartella):
        import torch
        d = torch.load(percorso(cartella, 'pieno.pt'), weights_only=False)
        voc = I7.vocabolario()
        assert list(d['segni']) == list(voc['segni']), 'elenco dei simboli diverso da quello del modello'
        cfg = d['cfg']
        self.ctx = GM.Ctx(voc, d['tipi'], K=cfg['K'], S=cfg['S'])
        self.cfg, self.A, self.C = cfg, d['stato_A'], d['stato_C']
        self.f_add, self.f_val, self.f_fuori = d['f_add'], d['f_val'], d['f_fuori']
        self._m = {}

    def modello(self, s):
        import torch
        s = round(float(min(1.0, max(0.0, s))), 3)
        if s not in self._m:
            m = GM.costruisci(self.cfg)
            st = {}
            for k, a in self.A.items():
                c = self.C[k]
                st[k] = ((1 - s) * a + s * c) if a.is_floating_point() else a.clone()
            m.load_state_dict(st)
            m.eval()
            if len(self._m) > 6:
                self._m.clear()
            self._m[s] = m
        return self._m[s]


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('cartella')
    ap.add_argument('--mondo', default='vero')
    a = ap.parse_args()
    import righello_testi as RT
    RT.attiva_mondo(a.mondo)
    print(json.dumps(addestra_pieno(a.cartella, messaggi=lambda s: print(s, flush=True)), default=float)[:600])
