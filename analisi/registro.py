# -*- coding: utf-8 -*-
"""Provenienza di un risultato: con che codice, su quali dati, con quali versioni.

Il blocco di provenienza sta in un file a parte (risultati/provenienza/eNN.json) e
non dentro il .json dei risultati: cosi' i risultati restano confrontabili byte per
byte con quelli delle esecuzioni precedenti, e "git diff risultati/" e' gia' la
verifica della replica (vedi DECISIONI.md, D-003).
"""
import hashlib, importlib.metadata, os, platform, subprocess, sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.normpath(os.path.join(QUI, '..'))
TRASCRIZIONI = os.path.join(RADICE, 'dati', 'trascrizioni')
SORGENTI = os.path.join(RADICE, 'dati', 'cache', 'sorgenti')
PACCHETTI = ['numpy', 'scipy', 'matplotlib', 'scikit-learn', 'scikit-image', 'rapidfuzz', 'pypinyin']


def sha256(percorso):
    h = hashlib.sha256()
    with open(percorso, 'rb') as f:
        for blocco in iter(lambda: f.read(1 << 20), b''):
            h.update(blocco)
    return h.hexdigest()


def _git(*argomenti, cwd=RADICE):
    try:
        return subprocess.check_output(['git'] + list(argomenti), cwd=cwd,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def commit():
    """Commit del repository e, se ci sono modifiche non salvate, i file toccati."""
    sporchi = _git('status', '--porcelain', '--', 'analisi', 'esperimenti', 'prepara.py')
    return {'commit': _git('rev-parse', 'HEAD'),
            'modifiche_non_salvate': sporchi.splitlines() if sporchi else []}


def dati():
    """Impronte delle trascrizioni e commit di ogni sorgente scaricata da prepara.py."""
    out = {'trascrizioni': {f: sha256(os.path.join(TRASCRIZIONI, f))
                            for f in sorted(os.listdir(TRASCRIZIONI))}}
    if os.path.isdir(SORGENTI):
        out['sorgenti'] = {d: _git('rev-parse', 'HEAD', cwd=os.path.join(SORGENTI, d))
                           for d in sorted(os.listdir(SORGENTI))
                           if os.path.isdir(os.path.join(SORGENTI, d, '.git'))}
    return out


def ambiente():
    versioni = {}
    for p in PACCHETTI:
        try:
            versioni[p] = importlib.metadata.version(p)
        except importlib.metadata.PackageNotFoundError:
            versioni[p] = None
    java = None
    try:
        r = subprocess.run(['java', '-version'], capture_output=True, text=True)
        java = (r.stderr or r.stdout).splitlines()[0]
    except (OSError, IndexError):
        pass
    return {'python': sys.version.split()[0], 'piattaforma': platform.platform(),
            'pacchetti': versioni, 'java': java,
            'PYTHONHASHSEED': os.environ.get('PYTHONHASHSEED')}


def provenienza(script=None):
    out = {'codice': commit(), 'dati': dati(), 'ambiente': ambiente()}
    if script:
        out['script'] = {'file': os.path.relpath(script, RADICE).replace(os.sep, '/'),
                         'sha256': sha256(script)}
    return out
