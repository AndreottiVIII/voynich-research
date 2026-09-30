# -*- coding: utf-8 -*-
"""Confronta i risultati attuali con quelli di un commit di riferimento.

    python verifica_replica.py                 # tutti i risultati/*.json contro il tag "origine"
    python verifica_replica.py e01 e05 --rif HEAD~3

Per ogni esperimento dice se il .json e' identico byte per byte; se non lo e', confronta
i numeri uno per uno e riporta quanti differiscono, lo scarto massimo (assoluto e
relativo) e i primi percorsi diversi. Scrive risultati/replica.md.
"""
import json, math, os, subprocess, sys

QUI = os.path.dirname(os.path.abspath(__file__))
RISULTATI = os.path.join(QUI, 'risultati')


def al_riferimento(rif, relativo):
    try:
        return subprocess.check_output(['git', 'show', '%s:%s' % (rif, relativo)], cwd=QUI,
                                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None


def appiattisci(x, percorso='', out=None):
    out = {} if out is None else out
    if isinstance(x, dict):
        for k, v in x.items():
            appiattisci(v, '%s/%s' % (percorso, k), out)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            appiattisci(v, '%s[%d]' % (percorso, i), out)
    else:
        out[percorso] = x
    return out


def confronta(vecchio, nuovo):
    a, b = appiattisci(vecchio), appiattisci(nuovo)
    solo_a, solo_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
    diversi, max_ass, max_rel = [], 0.0, 0.0
    for k in sorted(set(a) & set(b)):
        x, y = a[k], b[k]
        if x == y:
            continue
        numeri = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (x, y))
        if numeri and math.isfinite(x) and math.isfinite(y):
            ass = abs(x - y)
            rel = ass / max(abs(x), abs(y))
            max_ass, max_rel = max(max_ass, ass), max(max_rel, rel)
            diversi.append((k, x, y, rel))
        else:
            diversi.append((k, x, y, None))
    return {'valori': len(set(a) & set(b)), 'diversi': diversi, 'solo_vecchio': solo_a,
            'solo_nuovo': solo_b, 'max_ass': max_ass, 'max_rel': max_rel}


def main():
    argv = sys.argv[1:]
    rif = 'origine'
    if '--rif' in argv:
        i = argv.index('--rif')
        rif = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    nomi = sorted(f for f in os.listdir(RISULTATI) if f.endswith('.json'))
    if argv:
        nomi = [f for f in nomi if any(f.startswith(a.lower()) for a in argv)]
    righe = ['# Verifica della replica', '',
             'Riferimento: `%s`. "Identico" = stesso file byte per byte.' % rif, '',
             '| risultato | esito | valori | diversi | scarto rel. max | note |', '|---|---|---|---|---|---|']
    for nome in nomi:
        with open(os.path.join(RISULTATI, nome), 'rb') as f:
            nuovo = f.read()
        vecchio = al_riferimento(rif, 'risultati/' + nome)
        if vecchio is None:
            righe.append('| %s | nuovo | | | | assente nel riferimento |' % nome)
            continue
        if vecchio == nuovo:
            righe.append('| %s | identico | | 0 | 0 | |' % nome)
            continue
        c = confronta(json.loads(vecchio), json.loads(nuovo))
        note = []
        if c['solo_vecchio'] or c['solo_nuovo']:
            note.append('struttura diversa: %d solo nel vecchio, %d solo nel nuovo'
                        % (len(c['solo_vecchio']), len(c['solo_nuovo'])))
        for k, x, y, _ in c['diversi'][:3]:
            note.append('`%s`: %r → %r' % (k, x, y))
        esito = 'stessi valori' if not c['diversi'] and not note else 'diverso'
        righe.append('| %s | %s | %d | %d | %.2e | %s |' % (nome, esito, c['valori'], len(c['diversi']),
                                                              c['max_rel'], '; '.join(note)))
    testo = '\n'.join(righe) + '\n'
    print(testo)
    with open(os.path.join(RISULTATI, 'replica.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(testo)


if __name__ == '__main__':
    main()
