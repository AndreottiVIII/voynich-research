# -*- coding: utf-8 -*-
"""Esperimento 33: acquisizione delle immagini della Beinecke (MS 408) via IIIF.

Manifest IIIF di Yale (oid 2002046). Le immagini si scaricano a larghezza fissa
(LARGHEZZA pixel) con l'Image API, dentro dati/cache/immagini/ (fuori dal repository);
nel repository resta dati/immagini.json con, per ogni immagine, l'etichetta della
Beinecke, il canvas, l'indirizzo e l'impronta SHA-256, cosi' chi rifa' il lavoro sa se
ha le stesse immagini.

Diritti (dal manifest): "Access: Public"; "The use of this image may be subject to the
copyright law of the United States ... The person using the image is liable for any
infringement." Il manoscritto e' del XV secolo; le immagini si usano per la ricerca e
non si ridistribuiscono.

    python esegui.py e33 -- 1v 3v 102r      # solo le immagini con quelle etichette (sottostringa)
    python esegui.py e33 -- --tutte
"""
import hashlib, json, os, sys, time, urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.join(QUI, '..')
CACHE = os.path.join(RADICE, 'dati', 'cache', 'immagini')
REGISTRO = os.path.join(RADICE, 'dati', 'immagini.json')
MANIFEST_URL = 'https://collections.library.yale.edu/manifests/2002046'
LARGHEZZA = 1500


def scarica(url, destinazione, tentativi=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'voynich-ricerca/1.0 (studio statistico)'})
            with urllib.request.urlopen(req, timeout=120) as r, open(destinazione, 'wb') as f:
                f.write(r.read())
            return
        except OSError as e:
            if i == tentativi - 1:
                raise
            print('  nuovo tentativo (%s)' % e, flush=True)
            time.sleep(5 * (i + 1))


def sha256(percorso):
    with open(percorso, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def nome_file(etichetta):
    return ''.join(c if c.isalnum() else '_' for c in etichetta).strip('_') + '.jpg'


def main():
    os.makedirs(CACHE, exist_ok=True)
    manifest = os.path.join(CACHE, 'manifest_2002046.json')
    if not os.path.exists(manifest):
        scarica(MANIFEST_URL, manifest)
    m = json.load(open(manifest, encoding='utf-8'))
    registro = json.load(open(REGISTRO, encoding='utf-8')) if os.path.exists(REGISTRO) else {}
    registro['_manifest'] = {'url': MANIFEST_URL, 'sha256': sha256(manifest), 'larghezza': LARGHEZZA}
    richieste = [a for a in sys.argv[1:] if not a.startswith('--')]
    tutte = '--tutte' in sys.argv
    for canvas in m['items']:
        etichetta = list(canvas['label'].values())[0][0]
        if not tutte and not any(etichetta == r or etichetta.startswith(r + ' ') for r in richieste):
            continue
        servizio = canvas['items'][0]['items'][0]['body']['service'][0]['@id']
        url = '%s/full/%d,/0/default.jpg' % (servizio, LARGHEZZA)
        dest = os.path.join(CACHE, nome_file(etichetta))
        if not os.path.exists(dest):
            print('scarico %s' % etichetta, flush=True)
            scarica(url, dest)
            time.sleep(1)                     # con garbo verso il server
        registro[etichetta] = {'canvas': canvas['id'], 'url': url, 'file': nome_file(etichetta),
                               'sha256': sha256(dest), 'byte': os.path.getsize(dest)}
    with open(REGISTRO, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(dict(sorted(registro.items())), f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('%d immagini nel registro' % (len(registro) - 1))


if __name__ == '__main__':
    main()
