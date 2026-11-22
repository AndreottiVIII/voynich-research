# -*- coding: utf-8 -*-
"""Vettori visivi di ia29: un modello di immagini preaddestrato (pesi pubblici, senza account) che gira sul processore.

Modelli (cartelle in dati/cache/ia29/modelli/, con le impronte SHA-256 accanto):
- `dino`: DINOv2 small (facebook/dinov2-small, Apache 2.0, 22 milioni di parametri). Vettore = token CLS (384 numeri) dell'ultimo strato; in piu'
  si tiene la media dei token delle zone (384 numeri) per una variante. Immagine ridimensionata a 224 pixel di larghezza e altezza multipla di 14.
- `clip`: parte visiva di CLIP ViT-B/32 (laion/CLIP-ViT-B-32-laion2B-s34B-b79K, MIT), vettore proiettato (512 numeri); immagine completata a
  quadrato col colore mediano e portata a 224 x 224. Solo variante di robustezza.

Varianti dell'immagine (si applicano prima del modello; il testo e' gia' coperto da `immagini_dati.mascherata`):
- `grigio` (principale): livelli di grigio con contrasto automatico (1% alle due code), cioe' la sola forma, senza colore ne' luminosita' della pergamena;
- `colore`: i tre canali.

Il modulo importa torch e transformers: va usato con l'ambiente dati/cache/.venv_immagini.
"""
import hashlib, json, os, sys, time

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
MODELLI = os.path.join(QUI, '..', 'dati', 'cache', 'ia29', 'modelli')
CARTELLE = {'dino': 'dinov2-small', 'clip': 'clip-laion-b32'}
_M = {}


def _prepara_pil(im, variante):
    from PIL import Image, ImageOps
    im = im.convert('RGB')
    if variante == 'grigio':
        g = ImageOps.autocontrast(im.convert('L'), cutoff=1)
        return Image.merge('RGB', (g, g, g))
    if variante == 'colore':
        return im
    raise ValueError(variante)


def _tensore_dino(im):
    import torch
    w0, h0 = im.size
    W = 224
    H = int(min(448, max(224, round(W * h0 / w0 / 14) * 14)))
    a = np.asarray(im.resize((W, H), resample=3), dtype=np.float32) / 255.0
    a = (a - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    return torch.from_numpy(a.transpose(2, 0, 1).copy())


def _tensore_clip(im):
    import torch
    from PIL import Image
    w0, h0 = im.size
    s = max(w0, h0)
    fondo = tuple(int(x) for x in np.median(np.asarray(im).reshape(-1, 3), axis=0))
    q = Image.new('RGB', (s, s), fondo)
    q.paste(im, ((s - w0) // 2, (s - h0) // 2))
    a = np.asarray(q.resize((224, 224), resample=3), dtype=np.float32) / 255.0
    a = (a - np.array([0.48145466, 0.4578275, 0.40821073], np.float32)) / np.array([0.26862954, 0.26130258, 0.27577711], np.float32)
    return torch.from_numpy(a.transpose(2, 0, 1).copy())


def carica(modello):
    if modello in _M:
        return _M[modello]
    import torch
    from transformers import AutoModel, CLIPVisionModelWithProjection
    p = os.path.join(MODELLI, CARTELLE[modello])
    if modello == 'dino':
        m = AutoModel.from_pretrained(p).eval()
    else:
        m = CLIPVisionModelWithProjection.from_pretrained(p).eval()
    _M[modello] = m
    return m


def vettori(immagini, modello, variante, batch=8, fili=None):
    """immagini: lista di PIL (gia' mascherate). Restituisce dict nome -> array (n x d): 'cls' e, per dino, 'patch'; per clip 'proj'."""
    import torch
    if fili:
        torch.set_num_threads(int(fili))
    m = carica(modello)
    out = {}
    for i in range(0, len(immagini), batch):
        pezzo = [_prepara_pil(im, variante) for im in immagini[i:i + batch]]
        if modello == 'dino':
            # immagini di forma diversa: un tensore per forma
            gruppi = {}
            for j, im in enumerate(pezzo):
                gruppi.setdefault(im.size, []).append(j)
            res = {}
            for _, js in gruppi.items():
                x = torch.stack([_tensore_dino(pezzo[j]) for j in js])
                with torch.no_grad():
                    h = m(pixel_values=x).last_hidden_state
                for k, j in enumerate(js):
                    res[j] = (h[k, 0].numpy(), h[k, 1:].mean(0).numpy())
            cls = np.stack([res[j][0] for j in range(len(pezzo))])
            pat = np.stack([res[j][1] for j in range(len(pezzo))])
            out.setdefault('cls', []).append(cls)
            out.setdefault('patch', []).append(pat)
        else:
            x = torch.stack([_tensore_clip(im) for im in pezzo])
            with torch.no_grad():
                e = m(pixel_values=x).image_embeds
            out.setdefault('proj', []).append(e.numpy())
    return {k: np.concatenate(v) for k, v in out.items()}


def impronta_file(percorso):
    h = hashlib.sha256()
    with open(percorso, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def con_cache(cartella, nome_cache, chiavi, crea, descrizione):
    """Vettori in cache npz (chiavi = nomi ordinati delle immagini). crea(chiavi_mancanti) -> dict nome_array -> matrice."""
    os.makedirs(cartella, exist_ok=True)
    p = os.path.join(cartella, nome_cache + '.npz')
    if os.path.exists(p):
        d = np.load(p, allow_pickle=False)
        if list(d['chiavi']) == list(chiavi):
            return {k: d[k] for k in d.files if k != 'chiavi'}
    t = time.time()
    r = crea(chiavi)
    np.savez(p, chiavi=np.array(chiavi), **r)
    with open(os.path.join(cartella, nome_cache + '.json'), 'w', encoding='utf-8') as f:
        json.dump({'descrizione': descrizione, 'immagini': len(chiavi), 'secondi': round(time.time() - t, 1)}, f, ensure_ascii=False, indent=1)
    return r
