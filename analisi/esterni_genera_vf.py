# -*- coding: utf-8 -*-
"""Genera il testo del generatore di voynich-fingerprint (Sachak 2026, github.com/SachekDenis/voynich-fingerprint,
commit a6d7558, licenza MIT) con la configurazione congelata pubblicata (frozen/FROZEN_CONFIG.json, versione 3),
addestrata come nel loro protocollo sui fogli pari di IT2a, e lo scrive per l'e3c93.

Il loro codice usa solo la libreria standard; si esegue con l'ambiente di questo progetto, isolato:
    .venv/Scripts/python -I analisi/esterni_genera_vf.py
Prima va copiato dati/trascrizioni/IT2a-n.txt in data/ del loro repository (lo fa questo script, controllando
l'impronta). Un file per seme (7, 21, 44, i semi del loro protocollo); paragrafi separati da una riga vuota.
Numero di paragrafi: quelli del corpo del testo nei fogli pari e dispari insieme (un libro intero).
"""
import hashlib, json, os, shutil, sys

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni', 'voynich-fingerprint')
OUT = os.path.join(QUI, '..', 'dati', 'cache', 'generatori_esterni')
IT2A = os.path.join(QUI, '..', 'dati', 'trascrizioni', 'IT2a-n.txt')
sys.path.insert(0, os.path.join(REPO, 'analysis'))


def main():
    dest = os.path.join(REPO, 'data', 'IT2a-n.txt')
    if not os.path.exists(dest):
        shutil.copyfile(IT2A, dest)
    assert hashlib.sha256(open(dest, 'rb').read()).digest() == hashlib.sha256(open(IT2A, 'rb').read()).digest()
    import freeze_and_verify as F
    import tune_artgen as T
    cfg = json.load(open(os.path.join(REPO, 'frozen', 'FROZEN_CONFIG.json'), encoding='utf-8'))
    assert cfg['version'] == 3 and cfg['seeds'] == [7, 21, 44]
    tr, te = T.split_by_folio()
    n_par = len(tr) + len(te)
    g, _, real2 = F.build(cfg)
    for s in cfg['seeds']:
        doc = g.document(
            n_paragraphs=n_par, seed=s,
            p_copy=cfg['p_copy'], recency_alpha=cfg['recency_alpha'],
            recency_window=cfg['recency_window'], buffer_size=cfg['buffer_size'],
            cross_onset=cfg['cross_onset'], use_onset=cfg['use_onset'],
            gallows_scale=cfg['gallows_scale'], p_repeat=cfg['p_repeat'],
            p_pair=cfg['p_pair'], copy_decay=cfg['copy_decay'],
            line_fit=cfg['line_fit'])
        testo = '\n\n'.join('\n'.join(' '.join(r) for r in p if r) for p in doc if any(p)) + '\n'
        f = os.path.join(OUT, 'vf_seme%d.txt' % s)
        with open(f, 'w', encoding='utf-8', newline='\n') as fo:
            fo.write(testo)
        print('seme %d: paragrafi %d, righe %d, parole %d, sha256 %s' % (
            s, len(doc), sum(len(p) for p in doc), sum(len(r) for p in doc for r in p),
            hashlib.sha256(testo.encode('utf-8')).hexdigest()), flush=True)
    print('paragrafi del corpo (pari + dispari): %d; paragrafi dispari %s' % (n_par, real2.get('paras')))


if __name__ == '__main__':
    main()
