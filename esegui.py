# -*- coding: utf-8 -*-
"""Esegue uno o piu' esperimenti in condizioni fissate e ne registra la provenienza.

    python esegui.py e01 e05            # esegue esperimenti/e01_*.py ed e05_*.py
    python esegui.py e14 -- --naibbe    # gli argomenti dopo -- passano all'esperimento

Che cosa fissa, e perche' (DECISIONI.md, D-002 e D-003):
- PYTHONHASHSEED=0: l'ordine di iterazione dei set di stringhe dipende dal seme di hash;
- PYTHONUTF8=1: su Windows la codifica predefinita non e' UTF-8;
- fine riga LF nei .json e .md scritti in risultati/: su Windows Python scrive CRLF, e i
  risultati non sarebbero confrontabili byte per byte con quelli prodotti su Linux;
- git senza conversione dei fine riga, per i download di prepara.py;
- il JDK in JAVA_HOME (o in ~/tools/jdk-*), per gli esperimenti sul generatore Java.

Per ogni esperimento scrive risultati/provenienza/eNN.json (commit, impronte dei dati,
versioni, durata) e risultati/provenienza/eNN.log (tutto l'output).
"""
import glob, json, os, subprocess, sys, time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, 'analisi'))
import registro

ESPERIMENTI = os.path.join(QUI, 'esperimenti')
RISULTATI = os.path.join(QUI, 'risultati')
PROVENIENZA = os.path.join(RISULTATI, 'provenienza')


def ambiente():
    env = dict(os.environ)
    env.update({'PYTHONHASHSEED': '0', 'PYTHONUTF8': '1', 'PYTHONIOENCODING': 'utf-8',
                'GIT_CONFIG_COUNT': '2',
                'GIT_CONFIG_KEY_0': 'core.autocrlf', 'GIT_CONFIG_VALUE_0': 'false',
                'GIT_CONFIG_KEY_1': 'core.eol', 'GIT_CONFIG_VALUE_1': 'lf'})
    java = env.get('JAVA_HOME')
    if not java:
        trovati = sorted(glob.glob(os.path.join(os.path.expanduser('~'), 'tools', 'jdk-*')))
        java = trovati[-1] if trovati else None
    if java:
        env['JAVA_HOME'] = java
        env['PATH'] = os.path.join(java, 'bin') + os.pathsep + env.get('PATH', '')
    return env


def trova(nome):
    codice = nome.lower().lstrip('e').zfill(2)
    trovati = glob.glob(os.path.join(ESPERIMENTI, 'e%s_*.py' % codice))
    if len(trovati) != 1:
        sys.exit('esperimento %s: trovati %d file' % (nome, len(trovati)))
    return 'e' + codice, trovati[0]


def a_lf(dopo, codice):
    """Riporta a LF i .json e .md dell'esperimento scritti in risultati/ durante l'esecuzione.
    Si guardano solo i file che cominciano col codice (eNN_), cosi' due esperimenti lanciati
    in parallelo non si attribuiscono i file a vicenda."""
    toccati = []
    for percorso in glob.glob(os.path.join(RISULTATI, '**', codice + '_*.*'), recursive=True):
        if os.path.splitext(percorso)[1] not in ('.json', '.md', '.txt', '.csv'):
            continue
        if os.path.getmtime(percorso) < dopo:
            continue
        with open(percorso, 'rb') as f:
            dati = f.read()
        if b'\r\n' in dati:
            with open(percorso, 'wb') as f:
                f.write(dati.replace(b'\r\n', b'\n'))
        toccati.append(os.path.relpath(percorso, QUI).replace(os.sep, '/'))
    return sorted(toccati)


def esegui(nome, argomenti, env):
    codice, script = trova(nome)
    os.makedirs(PROVENIENZA, exist_ok=True)
    inizio = time.time()
    print('== %s (%s)' % (codice, os.path.basename(script)), flush=True)
    with open(os.path.join(PROVENIENZA, codice + '.log'), 'w', encoding='utf-8', newline='\n') as log:
        proc = subprocess.Popen([sys.executable, script] + argomenti, cwd=QUI, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding='utf-8', errors='replace')
        for riga in proc.stdout:
            sys.stdout.write(riga)
            log.write(riga)
        uscita = proc.wait()
    durata = time.time() - inizio
    scritti = [p for p in a_lf(inizio - 1, codice) if not p.startswith('risultati/provenienza/')]
    prov = registro.provenienza(script)
    prov.update({'esperimento': codice, 'argomenti': argomenti, 'uscita': uscita,
                 'inizio': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(inizio)),
                 'durata_s': round(durata, 1), 'file_scritti': scritti})
    with open(os.path.join(PROVENIENZA, codice + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(prov, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('== %s: uscita %d, %.0f s, %d file' % (codice, uscita, durata, len(scritti)), flush=True)
    return uscita


def main():
    argv = sys.argv[1:]
    passanti = []
    if '--' in argv:
        i = argv.index('--')
        argv, passanti = argv[:i], argv[i + 1:]
    if not argv:
        sys.exit(__doc__)
    env = ambiente()
    os.environ.update({k: env[k] for k in ('PATH', 'JAVA_HOME') if k in env})
    errori = [n for n in argv if esegui(n, passanti, env) != 0]
    sys.exit(1 if errori else 0)


if __name__ == '__main__':
    main()
