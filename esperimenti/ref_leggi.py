# -*- coding: utf-8 -*-
"""Lettura del Referenzkorpus Frühneuhochdeutsch (ReF 1.0.2, CC-BY-SA 4.0; dati/cache/ref, non committati), formato
CorA-XML: parole al livello diplomatico (tok_dipl, campo utf) ordinate secondo le righe vere (layoutinfo: pagine,
colonne, righe con intervalli di tok_dipl). Un segno = un carattere con i suoi segni combinati (accenti, trattini
d'abbreviazione). Ogni parola porta anche la forma normalizzata del token (tok_anno, campo ascii) e se il diplomatico ha
un segno d'abbreviazione.

Uso: manoscritti(da, a, medium) -> [(sigla, intestazione, [(pagina, [righe di Parola])])]
"""
import glob, os, re, unicodedata
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
CARTELLA = os.path.join(QUI, '..', 'dati', 'cache', 'ref', 'ReF-v1.0.2')
ABBR = set('̄̅ˢ͗ͤͦᵉͥͮꝰꝑͣͤͥͦͧͮͯ') | {'ᵃ'}


class Parola(tuple):
    def __new__(cls, segni, norm, abbreviata):
        p = super().__new__(cls, segni)
        p.norm, p.abbreviata = norm, abbreviata
        return p


def segni(s):
    out = []
    for c in unicodedata.normalize('NFD', s):
        if unicodedata.category(c) == 'Mn' and out:
            out[-1] += c
        else:
            out.append(c)
    return tuple(unicodedata.normalize('NFC', g) for g in out)


def intestazione(testo):
    h = re.search(r'<header>(.*?)</header>', testo, re.S)
    out = {}
    if h:
        for riga in h.group(1).split('\n'):
            if ':' in riga:
                k, v = riga.split(':', 1)
                out[k.strip()] = v.strip()
    return out


def leggi(percorso):
    t = open(percorso, encoding='utf-8').read()
    h = intestazione(t)
    dipl, ordine = {}, []
    for m in re.finditer(r'<token id="([^"]+)"[^>]*>(.*?)</token>', t, re.S):
        corpo = m.group(2)
        an = re.search(r'<tok_anno [^>]*ascii="([^"]*)"', corpo)
        norm = an.group(1).lower() if an else ''
        for d in re.finditer(r'<tok_dipl id="([^"]+)"[^>]*utf="([^"]*)"', corpo):
            u = d.group(2)
            abbr = any(c in ABBR for c in unicodedata.normalize('NFD', u))
            dipl[d.group(1)] = len(ordine)
            ordine.append(Parola(segni(u), norm, abbr))
    righe = OrderedDict()
    for m in re.finditer(r'<line id="([^"]+)"[^>]*range="([^"]+)"', t):
        a, _, b = m.group(2).partition('..')
        if a in dipl and (b or a) in dipl:
            righe[m.group(1)] = (dipl[a], dipl[b or a])
    colonne = {}
    for m in re.finditer(r'<column id="([^"]+)"[^>]*range="([^"]+)"', t):
        colonne[m.group(1)] = m.group(2)
    pagine = []
    for m in re.finditer(r'<page id="([^"]+)"[^>]*range="([^"]+)"', t):
        rr = []
        for c in re.split(r'[,\s]+', m.group(2)):
            ca, _, cb = c.partition('..')
            for cid in [ca] + ([cb] if cb else []):
                rng = colonne.get(cid)
                if not rng:
                    continue
                la, _, lb = rng.partition('..')
                ids = list(righe)
                if la in righe:
                    i0 = ids.index(la)
                    i1 = ids.index(lb) if lb in righe else i0
                    for lid in ids[i0:i1 + 1]:
                        a, b = righe[lid]
                        r = [w for w in ordine[a:b + 1] if w and any(g.strip() and g not in '/.·,;:=[]‍' for g in w)]
                        if r:
                            rr.append(r)
        if rr:
            pagine.append((m.group(1), rr))
    return h, pagine


def manoscritti(da='14,2', a='15,2', medium='Handschrift'):
    periodi = ['14,1', '14,2', '15,1', '15,2', '16,1', '16,2', '17,1', '17,2']
    validi = set(periodi[periodi.index(da):periodi.index(a) + 1])
    out = []
    for f in sorted(glob.glob(os.path.join(CARTELLA, '*', '*.xml'))):
        testa = open(f, encoding='utf-8').read(20000)
        if 'medium: ' + medium not in testa:
            continue
        tm = re.search(r'^time: (\S+)', testa, re.M)
        if not tm or tm.group(1) not in validi:
            continue
        h, pagine = leggi(f)
        out.append((os.path.basename(f)[:-4], h, pagine))
    return out
