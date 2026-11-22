# -*- coding: utf-8 -*-
"""Controllo positivo di ia29: un erbario a stampa vero, di pubblico dominio, con testo in una lingua nota e un disegno per ogni voce.

Fonte (scelta il 22/11/2026 con una sola ricerca in rete): Leonhart Fuchs, "De historia stirpium commentarii insignes" (Basilea, Isingrin, 1542), in
latino, 509 xilografie a piena pagina colorate a mano. Copia della Biblioteca nazionale centrale di Roma digitalizzata da Google, su Internet Archive:
identificativo `bub_gb_1uALRWuzDAoC`, 944 immagini, licenza dichiarata sulla scheda: Public Domain Mark 1.0
(http://creativecommons.org/publicdomain/mark/1.0/). Scaricati: il testo OCR con le coordinate delle parole (`..._djvu.xml`, 13 MB) e le immagini
delle pagine a 600 pixel di larghezza (`.../page/n<indice>_w600.jpg`, circa 100 KB l'una). Niente di tutto questo finisce nel repo o in `risultati/`.

Che cosa e' una "unita" (pagina del controllo): un disegno (pagina di xilografia: pochi segni OCR, molto inchiostro o colore) e il testo latino della
voce (le pagine di testo, con almeno 100 parole OCR, che stanno subito prima o subito dopo il disegno: `direzione`). Il testo ha un OCR rumoroso
(latino del Cinquecento, s lunga, abbreviazioni): e' un controllo severo, non un caso comodo. Le didascalie stampate dentro i disegni (nomi delle piante)
sono coperte come i riquadri delle parole del Voynich (stesse funzioni, coordinate dell'OCR).

Registro: dati/cache/ia29/controllo_fuchs/registro.json (impronta SHA-256 e dimensione di ogni file scaricato).
"""
import hashlib, html, json, os, re, sys, time, unicodedata, urllib.request

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import immagini_dati as ID_  # noqa: E402

IDENT = 'bub_gb_1uALRWuzDAoC'
URL_XML = 'https://archive.org/download/%s/%s_djvu.xml' % (IDENT, IDENT)
URL_PAGINA = 'https://archive.org/download/%s/page/n%%d_w600.jpg' % IDENT
AGENTE = 'voynich-ricerca/1.0 (studio statistico)'
MIN_TESTO, MAX_DIDASCALIA, MIN_INCHIOSTRO = 100, 30, 0.04


def cartella(cache):
    return os.path.join(cache, 'controllo_fuchs')


def _registro(cache):
    p = os.path.join(cartella(cache), 'registro.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def _salva_registro(cache, r):
    json.dump(r, open(os.path.join(cartella(cache), 'registro.json'), 'w', encoding='utf-8'), indent=1)


def _scarica(url, dest, tentativi=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': AGENTE})
            with urllib.request.urlopen(req, timeout=180) as r, open(dest, 'wb') as f:
                f.write(r.read())
            return
        except OSError:
            if i == tentativi - 1:
                raise
            time.sleep(5 * (i + 1))


def ocr(cache):
    """Lista (una voce per immagine) di dict(w, h, parole=[(testo, x0, y0, x1, y1)]) dal file djvu.xml (scaricato una volta)."""
    os.makedirs(cartella(cache), exist_ok=True)
    pj = os.path.join(cartella(cache), 'ocr.json')
    if os.path.exists(pj):
        return json.load(open(pj, encoding='utf-8'))
    px = os.path.join(cartella(cache), 'djvu.xml')
    if not os.path.exists(px):
        _scarica(URL_XML, px)
        reg = _registro(cache)
        reg['djvu.xml'] = {'url': URL_XML, 'sha256': hashlib.sha256(open(px, 'rb').read()).hexdigest(), 'byte': os.path.getsize(px)}
        _salva_registro(cache, reg)
    x = open(px, encoding='utf-8', errors='replace').read()
    out = []
    for o in re.split(r'<OBJECT ', x)[1:]:
        w = int(re.search(r'width="(\d+)"', o).group(1))
        h = int(re.search(r'height="(\d+)"', o).group(1))
        ps = []
        for c, t in re.findall(r'<WORD coords="([^"]*)"[^>]*>([^<]*)</WORD>', o):
            a = [int(v) for v in c.split(',')[:4]]
            ps.append((html.unescape(t).strip(), a[0], min(a[1], a[3]), a[2], max(a[1], a[3])))
        out.append({'w': w, 'h': h, 'parole': ps})
    json.dump(out, open(pj, 'w', encoding='utf-8'))
    return out


def parole_pulite(parole):
    """Minuscole senza segni, s lunga e v/u, j/i fusi (come si fa per il latino antico), solo lettere a-z, almeno 3 lettere."""
    out = []
    for t, *_ in parole:
        s = unicodedata.normalize('NFKD', t.lower().replace('ſ', 's'))
        s = re.sub(r'[^a-z]', '', s).replace('v', 'u').replace('j', 'i')
        if len(s) >= 3:
            out.append(s)
    return out


def unita(o, direzione='prima', massimo_testo=2):
    """Candidati (indice immagine, [indici pagine di testo]) per la regola di appaiamento. direzione 'prima': il testo viene subito prima del
    disegno; 'dopo': subito dopo. Il disegno e' una pagina con meno di MAX_DIDASCALIA parole OCR vicina a una pagina di testo (almeno MIN_TESTO)."""
    n = [len(x['parole']) for x in o]
    T = [k for k in range(len(o)) if n[k] >= MIN_TESTO]
    Ts = set(T)
    out = []
    for k in range(len(o)):
        if n[k] >= MAX_DIDASCALIA:
            continue
        if direzione == 'prima':
            t = []
            j = k - 1
            while j >= 0 and j in Ts and len(t) < massimo_testo:
                t.append(j)
                j -= 1
            t = t[::-1]
        else:
            t = []
            j = k + 1
            while j in Ts and len(t) < massimo_testo:
                t.append(j)
                j += 1
        if t:
            out.append((k, t))
    return out


def scarica_immagini(cache, indici, ritardo=0.3, fili=6):
    """Scarica le pagine mancanti (Internet Archive le prepara al momento: 5-10 secondi l'una, quindi a gruppi di `fili` richieste insieme)."""
    from concurrent.futures import ThreadPoolExecutor
    d = os.path.join(cartella(cache), 'pagine')
    os.makedirs(d, exist_ok=True)
    reg = _registro(cache)
    manca = [k for k in indici if not (os.path.exists(os.path.join(d, 'n%d.jpg' % k)) and os.path.getsize(os.path.join(d, 'n%d.jpg' % k)) > 5000)]

    def uno(k):
        p = os.path.join(d, 'n%d.jpg' % k)
        _scarica(URL_PAGINA % k, p)
        time.sleep(ritardo)
        return k
    with ThreadPoolExecutor(max_workers=fili) as ex:
        for k in ex.map(uno, manca):
            p = os.path.join(d, 'n%d.jpg' % k)
            reg['pagine/n%d.jpg' % k] = {'url': URL_PAGINA % k, 'sha256': hashlib.sha256(open(p, 'rb').read()).hexdigest(), 'byte': os.path.getsize(p)}
    _salva_registro(cache, reg)


def percorso_immagine(cache, k):
    return os.path.join(cartella(cache), 'pagine', 'n%d.jpg' % k)


def inchiostro(im):
    """Quota di pixel "di disegno" (scuri rispetto alla pergamena o colorati): serve a scartare le pagine bianche."""
    a = np.asarray(im.convert('HSV')).astype(float)
    V, S = a[..., 2], a[..., 1]
    med = float(np.median(V))
    return float(np.mean((V < 0.75 * med) | (S > 90)))


def immagine_mascherata(cache, o, k):
    """Immagine PIL della pagina k con le didascalie dell'OCR coperte."""
    from PIL import Image
    im = Image.open(percorso_immagine(cache, k)).convert('RGB')
    s = im.size[0] / float(o[k]['w'])
    bb = [(x0 * s, y0 * s, x1 * s, y1 * s) for _, x0, y0, x1, y1 in o[k]['parole']]
    return ID_.mascherata(im, bb)


def costruisci(cache, direzione='prima', scarica=True):
    """Lista ordinata di unita' valide: dict(k, testo_k, parole, pos, n). Scarica le immagini candidate (una volta) e scarta quelle senza disegno."""
    o = ocr(cache)
    cand = unita(o, direzione)
    if scarica:
        scarica_immagini(cache, [k for k, _ in cand])
    from PIL import Image
    out = []
    for k, t in cand:
        p = percorso_immagine(cache, k)
        if not os.path.exists(p):
            continue
        if inchiostro(Image.open(p).convert('RGB')) < MIN_INCHIOSTRO:
            continue
        ps = parole_pulite([w for j in t for w in o[j]['parole']])
        if len(ps) < 60:
            continue
        out.append({'k': k, 'testo_k': t, 'parole': ps, 'pos': k, 'n': len(ps)})
    return out


def meta_controllo(unita_):
    """Metadati per la statistica: nessuna sezione, mano, lingua, fascicolo (un solo gruppo); posizione e lunghezza."""
    return [dict(sezione='-', lingua='-', mano='-', fascicolo='-', bifoglio='-', pos=u['pos'], n=u['n']) for u in unita_]
