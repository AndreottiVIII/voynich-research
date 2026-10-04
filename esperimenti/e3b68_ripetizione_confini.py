# -*- coding: utf-8 -*-
"""Esperimento e3b68: ripetizione di una parola (uguale o a una modifica) a cavallo del salto del disegno e dell'a capo,
contro gli abbinamenti con le righe vicine (disegno dell'e3b66/e3b67).

Preregistrazione: preregistrazioni/e3b68.md. Scrive risultati/e3b68_ripetizione_confini.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import trascrizione
import e395_takahashi as e395
import e3a86_ripetizioni_riga as e3a86
import e3b65_a_capo_controllo as e3b65
import e3b67_salto_potenza as e3b67

RISULTATI = os.path.join(QUI, '..', 'risultati')
BOOT = 2000
DIST = (1, 2, 3)


def simili(a, b):
    return a is not None and b is not None and len(a) >= 3 and len(b) >= 3 and (a == b or e3a86.una_modifica(a, b))


def cavallo(a, b):
    """(ripetute, coppie) a cavallo fra a e b a distanza 1-3; le illeggibili interrompono."""
    seq = a + b
    n = len(a)
    r = t = 0
    for i in range(n):
        for d in DIST:
            j = i + d
            if j < n or j >= len(seq) or seq[i] is None or seq[j] is None or any(seq[k] is None for k in range(i + 1, j)):
                continue
            t += 1
            r += simili(seq[i], seq[j])
    return r, t


def dentro(s):
    r = t = 0
    for i in range(len(s)):
        for d in DIST:
            j = i + d
            if j >= len(s) or s[i] is None or s[j] is None or any(s[k] is None for k in range(i + 1, j)):
                continue
            t += 1
            r += simili(s[i], s[j])
    return r, t


def somme(casi, vero, controlli):
    """{pagina: {chiave: (ripetute, coppie)}}."""
    out = {}
    for pg, cc in casi.items():
        acc = {k: [0, 0] for k in (vero,) + controlli + ('dentro',)}
        for prima, altri in cc:
            for k in (vero,) + controlli:
                if altri.get(k) is None:
                    continue
                r, t = cavallo(prima, altri[k])
                acc[k][0] += r
                acc[k][1] += t
            for s in (prima, altri[vero]):
                r, t = dentro(s)
                acc['dentro'][0] += r
                acc['dentro'][1] += t
        out[pg] = acc
    return out


def quota(sm, pagine, k):
    r = sum(sm[pg][k][0] for pg in pagine)
    t = sum(sm[pg][k][1] for pg in pagine)
    return r / t if t else None


def analisi(casi, vero, controlli, rnd):
    sm = somme(casi, vero, controlli)
    pagine = [pg for pg in sm if all(sm[pg][k][1] for k in (vero,) + controlli)]

    def dd(pp):
        q = [quota(sm, pp, k) for k in (vero,) + controlli]
        if None in q:
            return None
        return q[0] - sum(q[1:]) / len(controlli)
    d = dd(pagine)
    boot = sorted(x for x in (dd([rnd.choice(pagine) for _ in pagine]) for _ in range(BOOT)) if x is not None)
    qq = OrderedDict((k, OrderedDict([('quota', quota(sm, pagine, k)), ('coppie', sum(sm[pg][k][1] for pg in pagine))])) for k in (vero,) + controlli + ('dentro',))
    ecc_dentro = qq['dentro']['quota'] - sum(qq[k]['quota'] for k in controlli) / len(controlli)
    return OrderedDict([('pagine', len(pagine)), ('quote', qq), ('D', d), ('IC95', [boot[int(0.025 * len(boot))], boot[int(0.975 * len(boot)) - 1]]), ('eccesso_dentro', ecc_dentro)])


def main():
    rnd = random.Random(3268)
    sezione = {}
    for r in trascrizione.leggi('ZL'):
        sezione.setdefault(r.pagina, r.sezione)
    ris = OrderedDict()
    for q in ('ZL', 'IT'):
        righe = [(pg, npar, ws, seps) for st, pg, npar, ws, seps in e395.righe(q)]
        ris['salto, %s' % q] = analisi(e3b67.casi(righe), 'sotto', ('precedente', 'seguente'), rnd)
        normali = [x for x in righe if sezione.get(x[0]) != 'T']
        ris['a capo, %s' % q] = analisi(e3b65.casi_capo(normali), 'sotto', ('sopra', 'due'), rnd)
    for k, x in ris.items():
        print(k, json.dumps(x, ensure_ascii=False), flush=True)
    es = OrderedDict()
    for conf in ('salto', 'a capo'):
        z, it = ris['%s, ZL' % conf], ris['%s, IT' % conf]
        if z['IC95'][0] > 0 and it['D'] > 0:
            es[conf] = 'la ripetizione passa il confine'
        elif z['IC95'][0] <= 0 <= z['IC95'][1] and z['IC95'][1] < z['eccesso_dentro'] / 3:
            es[conf] = 'il confine azzera la ripetizione'
        else:
            es[conf] = 'incerto'
    out = OrderedDict([('confini', ris), ('esiti', es)])
    json.dump(out, open(os.path.join(RISULTATI, 'e3b68_ripetizione_confini.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e3b68 — La ripetizione di una parola passa il salto del disegno e l\'a capo?', '', 'Preregistrazione: `preregistrazioni/e3b68.md`. Quota di coppie uguali o a una modifica a distanza 1–3.', '',
          '| confine | pagine | vero (coppie) | controllo 1 (coppie) | controllo 2 (coppie) | dentro i tratti (coppie) | D (IC 95%) | eccesso dentro |', '|---|---|---|---|---|---|---|---|']
    for k, x in ris.items():
        qq = list(x['quote'].values())
        md.append('| %s | %d | %.4f (%d) | %.4f (%d) | %.4f (%d) | %.4f (%d) | %+.4f (%+.4f – %+.4f) | %+.4f |' % (k, x['pagine'], qq[0]['quota'], qq[0]['coppie'], qq[1]['quota'], qq[1]['coppie'], qq[2]['quota'], qq[2]['coppie'],
                                                                                                      qq[3]['quota'], qq[3]['coppie'], x['D'], x['IC95'][0], x['IC95'][1], x['eccesso_dentro']))
    md += [''] + ['Esito %s: **%s**.' % (k, v) for k, v in es.items()]
    open(os.path.join(RISULTATI, 'e3b68_ripetizione_confini.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
