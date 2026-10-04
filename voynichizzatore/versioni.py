# -*- coding: utf-8 -*-
"""Registro delle versioni del voynichizzatore: per ognuna il corpo (parametri di corpo4.genera_v4 piu' gli errori sparsi
dell'e297) e il modello delle scelte del nascondiglio ('v1' o 'v3'). Usato dallo strumento (voynichizzatore.py) e dal banco
di prova (e293).

Parametri del corpo: rip, phi, sigma_post, pi_post, beta, eps, vsim, omega, rho, tau, errori (vedi corpo2/3/4 ed e297);
classi, circola, chiave, max_rara, posizione, vicine (ritocchi dopo la generazione, corpo5); lam_fin, lam_pre, lam_cl (bordi legati e classi concordi nella riga, corpo6); delta, alfa (parole di base dal lessico
globale; peso delle parole della pagina, e232); theta, chi, k_tema (tema della pagina, variante della parola
precedente; e251b, e232); galli_su, galli_giu (p/f nelle prime righe, corpo5.galli_prime).
"""
import os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))

E288 = OrderedDict([('rip', 0.5), ('phi', 0.10), ('sigma_post', 0.04)])
V4 = OrderedDict(E288, lam_fin=1.0, lam_pre=1.0, lam_cl=0.3)      # prova_v6: pagella estesa 34 -> 39 sui semi 1-2
V5 = OrderedDict(V4, delta=0.2)                                    # prova_v6: 39, AUC 0,863/0,944 -> 0,816/0,923
V6 = OrderedDict(V5, rip=0.4)                                      # prova_v7: 39, AUC 0,816/0,923 -> 0,782/0,903
#   ma al banco (semi 7-9) peggiore della v5: pagella estesa 55 contro 57, AUC 0,827/0,936 contro 0,816/0,917. NON confermata.
V7 = OrderedDict(V5, galli_su=1.0, galli_giu=0.7)                  # prova_v8 (semi 1-2): AUC e266 0,923 -> 0,861, G8 0,87 -> 0,67
# impianto "pezzi" (e400-e407): sacco di pagina dal modello e disposizione; parametri in pezzi_parametri_<versione>.json
V8 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v8')])     # e406 (P3); banco: 0,604 / 0,715, pagella 41/54
V9 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v9')])     # e407 (U3): parole nuove come unioni, confine, verticale
V10 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v10')])   # e408 (R1): peso proprio del legame fra finali; canale nel sacco (e409)
V11 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v11')])   # e410 (G2): cancello della riga (prima lettera, distanza 2, cinque scelte)
V12 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v12')])   # e412 (M2): coppia esatta un po' evitata, differenza fra le due meta' della pagina
V13 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v13')])   # e413 (S2): kappa sul sacco completo, esponente sulla frequenza, unioni ben formate
V14 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v14')])   # e414 (J1): unioni con la giuntura probabile
V15 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v15')])   # v14 con la cifratura robusta (scrypt, SHAKE-256, HMAC)
V16 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v16')])   # v15 con la gabbia di ogni pagina presa da un'altra pagina (e415)
V17 = OrderedDict([('impianto', 'pezzi'), ('parametri', 'v17')])   # v15 con la gabbia di ogni pagina estratta da un modello statistico (e415)
VERSIONI = OrderedDict([
    ('v2', OrderedDict([('corpo', E288), ('modello', 'v1')])),
    ('v3', OrderedDict([('corpo', E288), ('modello', 'v3')])),
    ('v4', OrderedDict([('corpo', V4), ('modello', 'v3')])),
    ('v5', OrderedDict([('corpo', V5), ('modello', 'v3')])),
    ('v6', OrderedDict([('corpo', V6), ('modello', 'v3')])),
    ('v7', OrderedDict([('corpo', V7), ('modello', 'v3')])),
    ('v8', OrderedDict([('corpo', V8), ('modello', 'v3')])),
    ('v9', OrderedDict([('corpo', V9), ('modello', 'v3')])),
    ('v10', OrderedDict([('corpo', V10), ('modello', None), ('canale', 'sacco')])),
    ('v11', OrderedDict([('corpo', V11), ('modello', None), ('canale', 'sacco')])),
    ('v12', OrderedDict([('corpo', V12), ('modello', None), ('canale', 'sacco')])),
    ('v13', OrderedDict([('corpo', V13), ('modello', None), ('canale', 'sacco')])),
    ('v14', OrderedDict([('corpo', V14), ('modello', None), ('canale', 'sacco')])),
    ('v15', OrderedDict([('corpo', V15), ('modello', None), ('canale', 'sacco')])),
    ('v16', OrderedDict([('corpo', V16), ('modello', None), ('canale', 'sacco')])),
    ('v17', OrderedDict([('corpo', V17), ('modello', None), ('canale', 'sacco')])),
])


def corpo(parametri, seme):
    """Il corpo (righe dopo spezzature e prefissi, poi gli errori sparsi) con i parametri dati e il seme dato."""
    if parametri.get('impianto') == 'pezzi':
        import pezzi
        return pezzi.corpo(seme, parametri['parametri'])
    import corpo6
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    import e268_prime_righe as e268
    import e297_errori_sparsi as e297
    k = e251._prepara()
    x = parametri
    e233.SIGMA_POST, e233.PI_POST = x.get('sigma_post', 0.09), x.get('pi_post', 0.30)
    prm = dict(e251.CONF, gamma=0.0, rip=x.get('rip', 1.0), phi=x.get('phi', 0.0), beta=x.get('beta', 0.0), eps=x.get('eps', 1.0),
               vsim=x.get('vsim', 0.0), omega=x.get('omega', 0.0), rho=x.get('rho', 0.0), tau=x.get('tau', 0.0),
               lam_fin=x.get('lam_fin', 0.0), lam_pre=x.get('lam_pre', 0.0), lam_cl=x.get('lam_cl', 0.0))
    for nome in ('delta', 'alfa', 'theta', 'chi', 'k_tema'):
        if nome in x:
            prm[nome] = x[nome]
    rr = e236.dopo(corpo6.genera_v6(k['c2'], prm, seme, prime_per_pag=e268.prime_per_pagina(k['c']) if x.get('rho') else None), k['freq'], 100 + seme)
    rr = e297.errori(k['c2'], rr, x.get('errori', 0.0), seme)
    if x.get('classi') or x.get('circola'):
        import corpo5
        corpo5.CHIAVE, corpo5.MAX_RARA = x.get('chiave', 'stretta'), x.get('max_rara', 5)
        corpo5.POSIZIONE, corpo5.VICINE = x.get('posizione', False), x.get('vicine', 0)
        rr = corpo5.circola(corpo5.classi_riga(rr, x.get('classi', 0.0), seme), x.get('circola', 0.0), seme)
    if x.get('galli_su') or x.get('galli_giu'):
        import corpo5
        rr = corpo5.galli_prime(rr, x.get('galli_su', 0.0), x.get('galli_giu', 0.0), seme)
    return rr


_ORIG = {}


def canale(modello):
    """Imposta nel processo il modello delle scelte ('v1' o 'v3') e restituisce il modulo v1 (codifica e decodifica)."""
    import v1
    if not _ORIG:
        _ORIG.update(posti=v1.posti_contesto, modello=v1.MODELLO)
    if modello == 'v3':
        import v3
        v1.posti_contesto, v1.MODELLO = v3.posti_contesto_v3, os.path.join(QUI, 'modello_scelte_v3.json')
    else:
        v1.posti_contesto, v1.MODELLO = _ORIG['posti'], _ORIG['modello']
    return v1


def chiave_di(chiave, seme):
    return chiave if seme is None else '%s%d' % (chiave, seme)


def codifica(versione, testo, chiave, seme=None):
    """Il manoscritto con il testo nascosto: (righe, informazioni). Con il nascondiglio nelle scelte di grafia il seme fissa il
    corpo (senza seme viene dalla chiave); con il nascondiglio nel sacco (e409) il corpo dipende da messaggio e chiave, e il
    seme, se dato, entra nella chiave."""
    import v0
    d = VERSIONI[versione]
    if d.get('canale') == 'sacco':
        import canale_sacco
        return canale_sacco.codifica(testo, chiave_di(chiave, seme), d['corpo']['parametri'])
    v1 = canale(d['modello'])
    return v1.codifica(testo, chiave, righe=corpo(d['corpo'], v0.numero(chiave, 'corpo') % 1000003 if seme is None else seme))


def decodifica(versione, righe, chiave, seme=None):
    d = VERSIONI[versione]
    if d.get('canale') == 'sacco':
        import canale_sacco
        return canale_sacco.decodifica(righe, chiave_di(chiave, seme), d['corpo']['parametri'])
    return canale(d['modello']).decodifica(righe, chiave)


def senza_messaggio(versione, chiave):
    """Il manoscritto della stessa versione e chiave senza testo nascosto (per la valutazione)."""
    import v0
    d = VERSIONI[versione]
    if d.get('canale') == 'sacco':
        import canale_sacco
        return canale_sacco.codifica(None, chiave, d['corpo']['parametri'])[0]
    return corpo(d['corpo'], v0.numero(chiave, 'corpo') % 1000003)
