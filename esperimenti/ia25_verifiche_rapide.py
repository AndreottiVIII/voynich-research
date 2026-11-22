# -*- coding: utf-8 -*-
"""Esperimento IA25 (ia25): le verifiche rapide chieste dalla revisione esterna (REVIEW_FABLE.md, parti A e D).

Cinque letture indipendenti dentro un solo esperimento, ognuna con le sue domande, i suoi controlli (positivo e negativo) e le sue regole di lettura
scritte prima (preregistrazioni/ia25.md). Nessuna parte e' una decifrazione: si controlla quanto sono solide le misure e le letture gia' fatte.
  Parte 1  copia netta (ia09) con un riferimento "della stessa sezione, lingua e mano / dello stesso fascicolo" invece di "una pagina a caso":
           quanta parte della "copia" e' vocabolario di sezione?                              (verifiche_riferimento.py)
  Parte 2  il v21 e il Naibbe VERO con un'eco leggera di pagina nella metrica di distanza di ia14/ia19, con la scomposizione della distanza per misura e la
           distanza senza Λ.                                                                 (verifiche_cifrari.py)
  Parte 3  gli imitatori M1 (ia20) ed E2 (ia22) riscritti a temperature 0,8 / 0,9 / 1,0 / 1,1 (modelli gia' in cache), con un controllo su un processo noto:
           lo scarto di forma delle parole nuove e' solo l'effetto della temperatura 1?        (verifiche_temperatura.py)
  Parte 4  k90 (ia03), R_rel (ia02), contatto (ia08) e copia netta (ia09) con un'altra trascrizione (Takahashi, Claston) e altri alfabeti dei glifi; con le lingue
           nelle stesse due versioni.                                                         (verifiche_trascrizioni.py)
  Parte 5  il metro "vero contro vero": intervallo del vero per le misure di struttura di ia20 (meta' contro meta' dei fogli, ricampionamento di pagine e fogli) e
           rilettura descrittiva dei verdetti "al vero" di ia20-ia24.                         (verifiche_vero_vero.py)
Importa, senza modificarli: ia07, ia16, ia20, ia22 (libri e modelli gia' in dati/cache), imitatore_misure, gradini_modelli, echi_modelli, ia09, ia10, ia14, ia19,
ia02, ia03, e3c95. Non tocca il voynichizzatore.

Uscite (solo numeri e aggregati): risultati/ia25_verifiche_rapide.json e .md e, una riga per lavoro, risultati/ia25_corse.jsonl (con RIPRENDI=1 i lavori fatti non
si rifanno). Libri, modelli e numeri per pagina in dati/cache/ia25 (protetti: non si committano).

    nohup bash strumenti/coda.sh ia25 "PY=dati/cache/.venv_lm/Scripts/python,PROCESSI=8:ia25" > /dev/null 2>&1 &
    SOLO_CONTROLLI=1 PICCOLO20=1 PICCOLO22=1 USCITA=<cartella fuori dal repo> python esperimenti/ia25_verifiche_rapide.py     (prova sul libro latino)

Variabili (oltre a SOLO_CONTROLLI, USCITA, CACHE20, CACHE22, PICCOLO20, PICCOLO22 che si importano da ia07, ia20, ia22): PARTI25 (cifre, senza virgole: 12345, oppure 13),
FASI25 (E = esecuzione, S = sintesi; predefinito ES), PROCESSI, RIPRENDI, FILTRO (sottostringhe separate da |), CACHE25, N_LIBRI25 (libri per tipo, 10),
N_CTRL25 (libri del controllo di temperatura per temperatura, 3), RIF25 (riferimenti della parte 1: 012, aggiungere 3 per il bifoglio), TEMPI25 (indici delle
temperature 0-3, predefinito 0123), ISTANZE25 (istanze per testo della parte 2, 3), SEMI25 (semi di rete della parte 4, 3), LINGUE25 (solo prova: sottostringhe dei
nomi delle lingue), EPOCHE25 e PAZIENZA25 (addestramento del controllo: 150 e 10), NSPLIT25 e NBOOT25 (parte 5: 200 e 1000). I valori predefiniti sono quelli preregistrati.
"""
import json
import os
import sys
import time
import statistics
from collections import OrderedDict
from multiprocessing import get_context

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'voynichizzatore'))
import verifiche_comune as C  # noqa: E402
import verifiche_riferimento as V1  # noqa: E402
import verifiche_cifrari as V2  # noqa: E402
import verifiche_temperatura as V3  # noqa: E402
import verifiche_trascrizioni as V4  # noqa: E402
import verifiche_vero_vero as V5  # noqa: E402

I7, I14, I19, I20 = C.I7, V2.I14, V2.I19, C.I20
NOME = 'ia25_verifiche_rapide'
SOLO_CONTROLLI = C.SOLO_CONTROLLI
USCITA = C.USCITA
RISULTATI = C.RISULTATI
PARTI = [int(x) for x in os.environ.get('PARTI25', '12345') if x in '12345']
FASI = os.environ.get('FASI25', 'ES')
N_LIBRI25 = V3.N_LIBRI25
RIFS = [x for x in os.environ.get('RIF25', '012') if x in '0123']
if '0' not in RIFS:
    RIFS = ['0'] + RIFS                                      # la pagina a caso serve sempre (e' il riferimento di ia09)


# ---------------------------------------------------------------- l'elenco dei lavori

def chiave_lavoro(args):
    t = args[0]
    if t == 'cifr':
        return V2.chiave_job(args[1])
    if t == 'gru':
        return 'gru|%s|%s|%s' % (args[1]['tipo'], args[1]['nome'], args[1]['seme'])
    return '|'.join(str(a) for a in args)


def nomi_parte1():
    nomi = ['vere'] + ['V21:%d' % k for k in I7.CHIAVI_V21]
    for t in ('M1', 'M5', 'E2'):
        nomi += ['%s:%d' % (t, i) for i in range(1, N_LIBRI25 + 1)]
    return nomi + ['sint:sez', 'sint:pag']


def fasi_parte(parte):
    """Elenco di fasi (ognuna e' una lista di lavori che possono girare insieme); le fasi si fanno una dopo l'altra."""
    if parte == 1:
        return [[('rif', n) for n in nomi_parte1()]]
    if parte == 2:
        return [[('cifr', j) for j in V2.lavori25(V2.descrittori25())]]
    if parte == 3:
        n3 = V3.nomi_libri3()
        a = [('addestra_c3', k) for k in range(I7.PIEGHE)] + [('O', 'O2', s) for s in I7.SEMI_O] + [('caso', 0)]
        a += [('libro3', t, tk, i) for t in V3.TIPI3 for tk in V3.TKEYS for i in range(1, N_LIBRI25 + 1)]
        a += [('ident3', t, i) for t in V3.TIPI3 for i in sorted(set(V3.CTRL_IDENTITA_LIBRI(N_LIBRI25)))]
        b = [('libro_c3', tk, i) for tk in V3.TKEYS for i in range(1, V3.N_CTRL25 + 1)]
        c = [('M3', n) for n in ['vere'] + n3] + [('D3', f) for f in range(I7.PIEGHE)] + [('K3', f) for f in range(I7.PIEGHE)] + [('forma_c3', f) for f in range(I7.PIEGHE)]
        return [a, b, c]
    if parte == 4:
        return [[('trasc', v) for v in V4.VAR_ALL], None]            # la seconda fase (reti) si prepara al momento
    if parte == 5:
        return [[('vv_pagine',)]]
    return []


def lavori_gru_parte4():
    """I lavori di rete della parte 4, con i flussi gia' codificati (si preparano nel processo principale, che carica le lingue)."""
    testi, semi = OrderedDict(), {}
    for v in V4.VAR_ALL:
        n = 'V:' + v
        testi[n] = V4.blocchi_variante(v)
        semi[n] = V4.semi_di(v)
    lett, fuse = V4.testi_lingue()
    for n, bl in fuse.items():
        testi['L:' + n + '+f'] = bl
        semi['L:' + n + '+f'] = list(range(1, V4.SEMI25 + 1))
    C.crea_cartelle()
    C.scrivi_json(os.path.join(C.MISURE25, 'lingue25.json'), dict(lettere=list(lett), fuse=list(fuse)))
    return V4.prepara_lavori_gru(testi, semi)


def nomi_gru_noti():
    """Le chiavi dei lavori di rete se i nomi delle lingue sono gia' salvati (cosi' con RIPRENDI non si ricarica niente se tutto e' fatto)."""
    p = os.path.join(C.MISURE25, 'lingue25.json')
    if not os.path.exists(p):
        return None
    ling = json.load(open(p, encoding='utf-8'))['fuse']
    chiavi = []
    for v in V4.VAR_ALL:
        for s in V4.semi_di(v):
            chiavi += ['gru|R|V:%s|%d' % (v, s), 'gru|K|V:%s|%d' % (v, s)]
    for n in ling:
        for s in range(1, V4.SEMI25 + 1):
            chiavi += ['gru|R|L:%s+f|%d' % (n, s), 'gru|K|L:%s+f|%d' % (n, s)]
    return chiavi


# ---------------------------------------------------------------- esecuzione

def imposta_boot(t):
    """ia14 (importato qui per la parte 2) porta il numero di ricampionamenti di ia09 a 200, ia09 e ia20 usano 1000: ogni lavoro usa il suo (BOOT, se impostato, vale per tutti)."""
    b = int(os.environ['BOOT']) if 'BOOT' in os.environ else (200 if t == 'cifr' else 1000)
    if C.A9.BOOT != b:
        C.A9.BOOT = b
        C.A9._W.clear()


def lavoro25(args):
    inizio = time.time()
    chiave = chiave_lavoro(args)
    try:
        t = args[0]
        imposta_boot(t)
        if t == 'rif':
            r = V1.lavoro_rif(args[1], RIFS)
        elif t == 'cifr':
            r = V2.lavoro(args[1])
        elif t == 'libro3':
            r = V3.lavoro_libro(args[1], args[2], args[3])
        elif t == 'ident3':
            r = V3.lavoro_identita(args[1], args[2])
        elif t == 'addestra_c3':
            r = V3.lavoro_addestra_c3(args[1])
        elif t == 'libro_c3':
            r = V3.lavoro_libro_c3(args[1], args[2])
        elif t == 'M3':
            r = V3.lavoro_M(args[1])
        elif t == 'D3':
            r = V3.lavoro_D(args[1], V3.nomi_libri3())
        elif t == 'K3':
            r = V3.lavoro_K(args[1], V3.nomi_libri3() + V3.nomi_riferimento_K())
        elif t == 'forma_c3':
            r = V3.lavoro_forma_c3(args[1])
        elif t in ('O', 'caso'):
            r = I7.lavoro(tuple(args))
        elif t == 'trasc':
            r = V4.lavoro_conteggi(args[1])
        elif t == 'gru':
            r = V4.lavoro_gru(args[1])
        elif t == 'vv_pagine':
            r = V5.lavoro_pagine()
        else:
            raise ValueError(t)
        r['lavoro'] = chiave
        return r
    except Exception as e:                                                # noqa: BLE001
        import traceback
        return OrderedDict([('lavoro', chiave), ('errore', '%s: %s' % (type(e).__name__, str(e)[:300])), ('traccia', traceback.format_exc()[-1500:]),
                            ('secondi', round(time.time() - inizio, 1))])


def avvia_processo():
    I7.avvia_processo()


def esegui(lavori, processi, percorso, fatte):
    filtro = [x for x in os.environ.get('FILTRO', '').split('|') if x]
    da_fare = [a for a in lavori if chiave_lavoro(a) not in fatte and (not filtro or any(x in chiave_lavoro(a) for x in filtro))]
    if not da_fare:
        return []
    out, inizio = [], time.time()
    with get_context('spawn').Pool(min(processi, len(da_fare)), initializer=avvia_processo) as pool:
        for k, r in enumerate(pool.imap_unordered(lavoro25, da_fare), 1):
            out.append(r)
            with open(percorso, 'a', encoding='utf-8', newline='\n') as f:
                f.write(json.dumps(C.pulisci(r), ensure_ascii=False, default=float) + '\n')
            if r.get('errore'):
                print('ERRORE %s: %s\n%s' % (r['lavoro'], r['errore'], r.get('traccia', '')), flush=True)
            else:
                fatte.add(r['lavoro'])
                breve = {x: r[x] for x in ('epoca_scelta', 'AUC_e231', 'AUC_e266', 'copia_netta', 'contatto') if x in r}
                print('[%d/%d %.1f min] %s: %s (%.0f s)' % (k, len(da_fare), (time.time() - inizio) / 60, r['lavoro'], breve, r.get('secondi', r.get('tempo', 0))), flush=True)
        pool.close()
        pool.join()
    return out


# ---------------------------------------------------------------- sintesi

def leggi_json(nome):
    p = os.path.join(RISULTATI, nome)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def sintesi(percorso, versioni):
    corse = OrderedDict((c['lavoro'], c) for c in C.leggi_corse(percorso) if not c.get('errore'))
    errori = [OrderedDict(lavoro=c['lavoro'], errore=c['errore']) for c in C.leggi_corse(percorso) if c.get('errore') and c['lavoro'] not in corse]
    out = OrderedDict(esperimento='ia25', solo_controlli=SOLO_CONTROLLI, versioni=versioni, parti=PARTI, errori=errori)
    md = ['# ia25 - le verifiche rapide', '',
          'Non e\' una decifrazione: si controlla quanto sono solide misure e letture gia\' fatte. Tutti i numeri; nessun testo. Preregistrazione: `preregistrazioni/ia25.md`.', '']
    if 1 in PARTI:
        o = V1.analisi(corse, RIFS, N_LIBRI25, dict(ia20=leggi_json('ia20_imitatore_gradini.json'), ia22=leggi_json('ia22_eco_e_legame.json')) if not SOLO_CONTROLLI else None)
        out['parte1'] = o
        md += V1.scrivi_md(o, RIFS) + ['']
    if 2 in PARTI:
        c25 = [c for c in corse.values() if c['lavoro'].startswith('cifr|')]
        o = V2.analisi(c25, C.leggi_corse(I19.CORSE_IA14), C.leggi_corse(os.path.join(RISULTATI, 'ia19_corse.jsonl')),
                       leggi_json('ia14_quale_cifrario.json'))
        out['parte2'] = o
        md += V2.scrivi_md(o) + ['']
    if 3 in PARTI:
        o = V3.analisi(corse)
        out['parte3'] = o
        md += V3.scrivi_md(o) + ['']
    if 4 in PARTI:
        conteggi = OrderedDict((c['var'], c) for c in corse.values() if c['lavoro'].startswith('trasc|'))
        gru = OrderedDict((k, c) for k, c in corse.items() if k.startswith('gru|'))
        p = os.path.join(C.MISURE25, 'lingue25.json')
        ling = json.load(open(p, encoding='utf-8')) if os.path.exists(p) else dict(lettere=[], fuse=[])
        c3 = C.leggi_corse(os.path.join(RISULTATI, 'ia03_corse.jsonl'))
        c2 = C.leggi_corse(os.path.join(RISULTATI, 'ia02_corse.jsonl'))
        lett = V4.lingue_da_file(c3, c2, ling['lettere'], V4.SEMI25)
        rif3 = OrderedDict(Voynich=[(c['seme'], (lambda m: m['k90_interpolato'] if m['k90_interpolato'] is not None else I14.K90_NON_DEFINITO)(V4.I3.misure_corsa(c, 'B')))
                                    for c in c3 if c.get('testo') == 'Voynich' and c['seme'] <= V4.SEMI25]) if not SOLO_CONTROLLI else None
        j20 = leggi_json('ia20_imitatore_gradini.json')
        o = V4.analisi(conteggi, gru, lett, ling['fuse'], rif3, (j20['vero'] if j20 and not SOLO_CONTROLLI else None))
        out['parte4'] = o
        md += V4.scrivi_md(o) + ['']
    if 5 in PARTI and os.path.exists(V5.percorso_pagine()):
        Q = V5.carica_pagine()
        o = V5.analisi_vero_vero(Q)
        cv = corse.get('vv_pagine')
        if cv:
            co = cv['coerenza']
            ok = (abs(co['copia_netta'][0] - co['copia_netta'][1]) <= 1e-9 and abs(co['lam'][0] - co['lam'][1]) <= 1e-9 and
                  abs(co['contatto'][0] - co['contatto'][1]) <= V5.SOGLIE['contatto_per_pagina_tol'])
            o['controlli']['coerenza_numeri_per_pagina'] = OrderedDict(copia_netta=co['copia_netta'], lam=co['lam'], contatto=co['contatto'], riuscito=bool(ok))
        o['letture_valide'] = bool(o['controlli']) and all(v.get('riuscito') for v in o['controlli'].values())
        rl = V5.rileggi({m: o['misure'][m] for m in o['misure']}, RISULTATI)
        o['rilettura'] = rl
        out['parte5'] = o
        md += V5.scrivi_md(o, rl) + ['']
    tempi = OrderedDict()
    for tipo in sorted({k.split('|')[0] for k in corse}):
        s = [v.get('secondi', v.get('tempo')) for k, v in corse.items() if k.startswith(tipo + '|') and v.get('secondi', v.get('tempo'))]
        if s:
            tempi[tipo] = OrderedDict(lavori=len(s), media_minuti=round(statistics.mean(s) / 60, 1), massimo_minuti=round(max(s) / 60, 1), totale_minuti=round(sum(s) / 60, 1))
    out['tempi'] = tempi
    C.scrivi_json(os.path.join(USCITA, NOME + '.json'), out)
    with open(os.path.join(USCITA, NOME + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(md) + '\n')
    return out


def main():
    import numpy
    import torch
    avvia_processo()
    versioni = OrderedDict([('python', sys.version.split()[0]), ('torch', torch.__version__), ('numpy', numpy.__version__)])
    try:
        import sklearn
        versioni['sklearn'] = sklearn.__version__
    except Exception:                                                     # noqa: BLE001
        pass
    os.makedirs(USCITA, exist_ok=True)
    C.crea_cartelle()
    righe, voc = I7.libro_vero(), I7.vocabolario()
    print('libro (%s): %d righe, %d pagine, %d segni; parti %s; riferimenti %s; PICCOLO %s' % ('controlli: latino' if SOLO_CONTROLLI else 'Voynich', len(righe),
                                                                                           len(I7.per_pagina(righe)), len(voc['unita']), PARTI, RIFS, C.PICCOLO), flush=True)
    percorso = os.path.join(USCITA, 'ia25_corse.jsonl')
    if os.environ.get('RIPRENDI') == '1':
        fatte = {c['lavoro'] for c in C.leggi_corse(percorso) if not c.get('errore')}
    else:
        open(percorso, 'w').close()
        fatte = set()
    processi = int(os.environ.get('PROCESSI', 4))
    if 'E' in FASI:
        for parte in PARTI:
            for n, fase in enumerate(fasi_parte(parte), 1):
                if fase is None:                                   # parte 4, reti
                    noti = nomi_gru_noti()
                    if noti is not None and all(k in fatte for k in noti):
                        continue
                    fase = [('gru', j) for j in lavori_gru_parte4() if j['tipo'] != 'scarto']
                print('== parte %d, fase %d: %d lavori' % (parte, n, len(fase)), flush=True)
                esegui(fase, processi, percorso, fatte)
    if 'S' in FASI:
        o = sintesi(percorso, versioni)
        for k, x in o.items():
            if k.startswith('parte') and isinstance(x, dict) and 'letture' in x:
                print('%s: letture valide %s; %s' % (k, x.get('letture_valide'), list(x['letture'])[:6]), flush=True)


if __name__ == '__main__':
    main()
