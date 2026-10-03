# -*- coding: utf-8 -*-
"""Esperimento e3a64: nei punti in cui lo spazio e' facoltativo (regola dell'e3a58 fra 0,2 e 0,8), la quota di spazi
nell'ultimo terzo della riga contro il primo, dentro gli strati della coppia di segni; nullo per rimescolamento.

Preregistrazione: preregistrazioni/e3a64.md. Scrive risultati/e3a64_spazi_fine_riga.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e386_salto_disegno as e386
import e3a58_spazi_prevedibili as e3a58

RISULTATI = os.path.join(QUI, '..', 'risultati')
PERM = 2000


def punti(righe_sep):
    """[(prima, dopo, separatore, posizione relativa)] per le righe pulite."""
    out = []
    for _, _, _, ws, seps in righe_sep:
        if any(w is None for w in ws) or '|' in seps:
            continue
        s, tipo = [], {}
        for j, w in enumerate(ws):
            if s:
                tipo[len(s)] = seps[j - 1]
            s += list(w)
        if len(s) < 10:
            continue
        out += [(s[i - 1], s[i], tipo.get(i, ''), i / len(s)) for i in range(1, len(s))]
    return out


def differenza(strati):
    num = den = 0.0
    for xs in strati.values():
        a = [y for t, y in xs if t == 1]
        c = [y for t, y in xs if t == 3]
        if a and c:
            w = len(a) * len(c) / (len(a) + len(c))
            num += w * (sum(c) / len(c) - sum(a) / len(a))
            den += w
    return num / den if den else 0.0


def main():
    rnd = random.Random(3164)
    pp = punti(e386.righe())
    reg = e3a58.Regola([(a, b, t == '.') for a, b, t, _ in pp if t != ','])
    strati = defaultdict(list)
    n_fac = 0
    for a, b, t, x in pp:
        if t == ',':
            continue
        p = reg.p(a, b)
        if not 0.2 <= p <= 0.8:
            continue
        n_fac += 1
        terzo = 1 if x < 1 / 3 else (3 if x > 2 / 3 else 2)
        if terzo != 2:
            strati[a, b].append((terzo, int(t == '.')))
    d = differenza(strati)
    nul = []
    for _ in range(PERM):
        s2 = {}
        for k, xs in strati.items():
            tt = [t for t, _ in xs]
            rnd.shuffle(tt)
            s2[k] = list(zip(tt, [y for _, y in xs]))
        nul.append(differenza(s2))
    p = (1 + sum(1 for v in nul if abs(v) >= abs(d))) / (1 + PERM)
    esito = ('lo scriba stringe a fine riga' if d < 0 else 'allarga a fine riga') if p < 0.01 else 'nessun effetto'
    grezzo = OrderedDict()
    for terzo in (1, 3):
        ys = [y for xs in strati.values() for t, y in xs if t == terzo]
        grezzo['terzo %d' % terzo] = OrderedDict([('punti', len(ys)), ('quota_spazi', sum(ys) / len(ys))])
    virg = OrderedDict()
    for nome, f in (('primo terzo', lambda x: x < 1 / 3), ('ultimo terzo', lambda x: x > 2 / 3)):
        sel = [t for _, _, t, x in pp if f(x) and t in ('.', ',')]
        virg[nome] = OrderedDict([('spazi_e_virgole', len(sel)), ('quota_virgole', sel.count(',') / len(sel))])
    out = OrderedDict([('punti_facoltativi', n_fac), ('strati', sum(1 for xs in strati.values() if {t for t, _ in xs} == {1, 3})), ('grezzo', grezzo),
                       ('differenza_pesata', d), ('p', p), ('virgole', virg), ('esito', esito)])
    print(json.dumps(out, ensure_ascii=False, indent=1), flush=True)
    json.dump(out, open(os.path.join(RISULTATI, 'e3a64_spazi_fine_riga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3a64 — Verso la fine della riga lo scriba stringe gli spazi facoltativi?', '', 'Preregistrazione: `preregistrazioni/e3a64.md`. Punti facoltativi: probabilità della regola fra 0,2 e 0,8.', '',
          'Punti facoltativi: %d; strati con punti in entrambi i terzi: %d.' % (n_fac, out['strati']), '',
          '| terzo della riga | punti facoltativi | quota di spazi (grezza) |', '|---|---|---|']
    md += ['| %s | %d | %.3f |' % (k, x['punti'], x['quota_spazi']) for k, x in grezzo.items()]
    md += ['', 'Differenza pesata dentro gli strati (ultimo − primo): **%+.4f**, p = %.4f.' % (d, p), '',
           '| terzo | spazi e virgole | quota di virgole |', '|---|---|---|']
    md += ['| %s | %d | %.3f |' % (k, x['spazi_e_virgole'], x['quota_virgole']) for k, x in virg.items()]
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e3a64_spazi_fine_riga.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
