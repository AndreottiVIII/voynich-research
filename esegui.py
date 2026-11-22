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
# variabili d'ambiente che cambiano che cosa fa un esperimento: si registrano nella provenienza
VARIABILI = ('LINGUE_SOLO', 'PROCESSI', 'RIPARTENZE', 'RIPRENDI', 'NAIBBE', 'BIBLE_CORPUS', 'LATIN_LIBRARY',
             'SEMI', 'TESTI', 'PASSI', 'RETI', 'SEMI_GRANDI', 'AVVIO', 'LR_AD', 'PASSI_AD', 'PAZIENZA_AD',
             'MODELLI', 'RIPETIZIONI', 'SAFE_MODE', 'SOGLIE', 'CHIAVI', 'CHIAVI_MSG', 'FRAZIONI', 'NEG', 'SEMI_B',
             'OGNI', 'PAZIENZA', 'NASCOSTO', 'CADUTA', 'PASSI_B', 'PAZIENZA_B', 'NASC_B', 'LUNG_B', 'LUNG', 'LOTTO',
             'FILTRO', 'SOLO_CONTROLLI', 'PAGINE', 'RIGHE_PAGINA', 'CERVELLI', 'CAS_AVVIO_SU', 'MIN_VALUTABILI',
             'TG_ALTO', 'MARGINE_TG', 'SOGLIA_NEG', 'PROVA', 'PROVA_RIP', 'NUOVA', 'ACCETTA_LACUNE',
             'VERIFICA_AMMESSE', 'LIMITE_MAX_ORE', 'PROVA_SPECIALI', 'THREAD', 'FASI',
             'PASSI_A', 'OGNI_A', 'PAZIENZA_A', 'NASCOSTO_A', 'CADUTA_A', 'EPOCHE_MAX', 'STRATI', 'N_SENZA', 'N_CON',
             'PAGELLA', 'NULLI', 'BOOT', 'FRAZ_NUOVE',
             'GENERATORI', 'RIM_TESTO', 'SCALA_COPIA', 'RIGHE_PAGINA_EN',
             'NV', 'KS', 'GIRI', 'S_RIM', 'NULL_REP', 'PERM', 'USCITA_CACHE',
             'CACHE11', 'LIBRI_TARA', 'LIBRI_MANIP', 'VARIANTI', 'NRIM_TARA',
             'ISTANZE', 'PROCEDIMENTI', 'LINGUE14', 'NATIVI', 'USCITA_CACHE14',
             'NRIF', 'SPOSTAMENTI', 'LIVELLI_ARG', 'LIVELLI_TEC', 'MIN_PAGINE_GRUPPO',
             'RIP_TUTTO', 'N_OBIETTIVI', 'LIBRI13', 'CACHE13',
             'MANI_Q', 'MANI_M', 'MANI_R', 'MANI_RGRU', 'MANI_RGRU_CTRL', 'MANI_SEMI_GRU', 'MANI_SEMI_GRU_CTRL',
             'MANI_MIN_PAROLE', 'MANI_MIN_PAGINE', 'MANI_MIN_SEGNI',
             'BRACCI', 'ASSEGNA', 'LR_PRE', 'LR_CAS', 'LR_EMB', 'PUNTI', 'RISCALDA', 'PRIORITA_MAX',
             'SOGLIA_CIFRATO_BIT', 'SOGLIA_CHIARO_BIT', 'MARGINE_CHIARO', 'SOGLIA_NEG_BIT', 'S_ALTO', 'S_BASSO',
             'S_VICINO', 'MODELLO_DIR', 'USCITA',
             'CACHE16', 'TAGLIE16', 'EPOCHE16', 'PAZIENZA16', 'N_LIBRI16', 'N_ABL16', 'N_STRUTTURA16', 'PICCOLO16',
             'CORSE_IA07', 'LIBRI_IA07', 'MODELLI_A16', 'MODELLI_IA07',
             'ECO_FRAZIONI', 'ECO_BERSAGLIO', 'TARA_TOL', 'TARA_PASSI', 'FAMIGLIA_PHI', 'LOC_MIN', 'N_FAMIGLIE',
             'CACHE17', 'REPLICHE17', 'PIEGHE17', 'N_ABL17', 'EPOCHE17C', 'PAZIENZA17C', 'COPIE_SINT17', 'N_SEMI17',
             'COMBINATI19', 'CONTROLLI19', 'USCITA_CACHE19', 'CORSE_IA14', 'P_RIGA_ECO',
             'CACHE20', 'PASSI20', 'EPOCHE20', 'PAZIENZA20', 'N_LIBRI20', 'PICCOLO20', 'EPOCHE_SENS20',
             'PASSO_VETRINA20', 'MODELLI_A20',
             'PERCORSO', 'TESTO_PROVA', 'MODELLO_PARTENZA', 'REPLICA_PARTENZA', 'CACHE21', 'N_GIRI21', 'C21',
             'CVAL21', 'PESO21', 'EPOCHE_AFFINA21', 'LR_AFFINA21', 'L_MON21', 'N_FIN21', 'N_STR21', 'EPOCHE_ES21',
             'PAZIENZA_ES21', 'STRUTTURA21', 'GUARDIE21', 'PICCOLO21', 'RIFAI', 'ETICHETTA',
             'CACHE22', 'EPOCHE22', 'PAZIENZA22', 'N_LIBRI22', 'PICCOLO22', 'EPOCHE_SENS22', 'TIPI22', 'RIF22',
             'CACHE23', 'EPOCHE23', 'PAZIENZA23', 'N_LIBRI23', 'PICCOLO23', 'EPOCHE_SENS23', 'TIPI23', 'RIF23',
             'CACHE24', 'EPOCHE24', 'PAZIENZA24', 'N_LIBRI24', 'PICCOLO24', 'EPOCHE_SENS24', 'TIPI24', 'RIF24',
             'FASI28', 'N_TABELLA28', 'N_CONTROLLO28', 'N_PPC28', 'N_PPC_CTRL28', 'N_LIBRI28', 'NT28', 'CACHE28',
             'COMPONENTI28', 'V21_28', 'PICCOLO28', 'LIBRI_DIR28', 'MISURE_DIR28', 'NAIBBE_CSV28',
             'CACHE29', 'MODELLI29', 'PERM29', 'RIP_POT29', 'RIP_NEG29', 'SOTTO29', 'DIREZIONE29', 'PICCOLO29',
             'PARTI25', 'FASI25', 'CACHE25', 'N_LIBRI25', 'N_CTRL25', 'RIF25', 'TEMPI25', 'ISTANZE25', 'SEMI25',
             'LINGUE25', 'EPOCHE25', 'PAZIENZA25', 'NSPLIT25', 'NBOOT25',
             'CACHE27', 'N_LIBRI27', 'N_LIBRI_VAR27', 'VARIANTI27', 'VAR_LIBRI27', 'BOOT27', 'MAXIT27', 'N_INNER27',
             'SEMI_CTRL27', 'PICCOLO27', 'RIF27', 'RIGHELLO27',
             'CACHE30', 'PICCOLO30', 'TIPI30', 'NP30', 'NL30', 'NH30', 'NPATCH30', 'N_LIBRI30', 'COND30', 'SEMI_Q30',
             'TAGLIA_Q30', 'EPOCHE_Q30', 'PIEGHE30', 'REPL30')


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
    nome = nome.lower()
    if nome.startswith('ia'):
        # serie del paper "Voynich e IA" (dal 18/11/2026): ia01, ia02, ...
        codice = nome
    else:
        codice = 'e' + nome.lstrip('e').zfill(2)
    trovati = glob.glob(os.path.join(ESPERIMENTI, '%s_*.py' % codice))
    if len(trovati) != 1:
        sys.exit('esperimento %s: trovati %d file' % (nome, len(trovati)))
    return codice, trovati[0]


def a_lf(dopo, codice):
    """Riporta a LF i .json e .md dell'esperimento scritti in risultati/ durante l'esecuzione.
    Si guardano solo i file che cominciano col codice (eNN_), cosi' due esperimenti lanciati
    in parallelo non si attribuiscono i file a vicenda."""
    toccati = []
    for percorso in glob.glob(os.path.join(RISULTATI, '**', codice + '_*.*'), recursive=True):
        if os.path.getmtime(percorso) < dopo:
            continue
        if os.path.splitext(percorso)[1] in ('.json', '.md', '.txt', '.csv'):
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
    # una corsa con argomenti (--esplorativo, --naibbe...) ha la sua provenienza e non
    # sovrascrive quella della corsa principale
    etichetta = codice + ''.join('_' + a.strip('-') for a in argomenti if a.startswith('--'))
    # ETICHETTA distingue corse parallele dello stesso esperimento (es. ia21 vero e cieco)
    if os.environ.get('ETICHETTA'):
        etichetta += '_' + os.environ['ETICHETTA']
    # la provenienza si fotografa prima di partire: commit e dati sono quelli con cui gira
    prov = registro.provenienza(script)
    inizio = time.time()
    print('== %s (%s)' % (codice, os.path.basename(script)), flush=True)
    with open(os.path.join(PROVENIENZA, etichetta + '.log'), 'w', encoding='utf-8', newline='\n') as log:
        proc = subprocess.Popen([sys.executable, script] + argomenti, cwd=QUI, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding='utf-8', errors='replace')
        for riga in proc.stdout:
            sys.stdout.write(riga)
            log.write(riga)
            log.flush()                       # il log si legge anche mentre l'esperimento gira
        uscita = proc.wait()
    durata = time.time() - inizio
    scritti = [p for p in a_lf(inizio - 1, codice) if not p.startswith('risultati/provenienza/')]
    prov['variabili'] = {k: env[k] for k in VARIABILI if k in env}
    prov.update({'esperimento': codice, 'argomenti': argomenti, 'uscita': uscita,
                 'inizio': time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(inizio)),
                 'durata_s': round(durata, 1), 'file_scritti': scritti})
    with open(os.path.join(PROVENIENZA, etichetta + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(prov, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print('== %s: uscita %d, %.0f s, %d file' % (codice, uscita, durata, len(scritti)), flush=True)
    return uscita


def main():
    # l'output dell'esecutore puo' contenere lettere di ogni alfabeto (ebraico, greco...): su
    # Windows, se e' rediretto su file, la codifica predefinita non le accetta
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
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
