# -*- coding: utf-8 -*-
"""Esperimento 241: come l'e240, ma l'operatore di variante empirico e' condizionato ai segni vicini (segno prima e dopo
il punto della modifica), con ripiego sull'operatore dell'e240 quando nessuna operazione col contesto e' applicabile.

Preregistrazione: preregistrazioni/e241.md. Scrive risultati/e241_operatore_contesto.json e .md.
"""
import json, os, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e239_operatore_variante as e239
import e240_operatore_empirico as e240

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI, RIFERIMENTO = (2, 3), 0.889
D = e237.D


def vicino(u, i):
    return u[i] if 0 <= i < len(u) else ('^' if i < 0 else '$')


def operazioni_contesto(pagine):
    tutte = Counter(w for rr in pagine.values() for r in rr for w in r)
    inventario = sorted({x for w in tutte for x in D(w)})
    ops = Counter()
    for rr in pagine.values():
        sulla = OrderedDict()
        for k, r in enumerate(rr):
            for w in r:
                u = tuple(D(w))
                if sulla and u not in sulla:
                    vic = e237.vicini(u, inventario)
                    fonti = [x for x in sulla if x in vic]
                    if fonti:
                        m = max(sulla[x] for x in fonti)
                        s = next(x for x in fonti if sulla[x] == m)
                        if len(s) == len(u):
                            i = next(t for t in range(len(s)) if s[t] != u[t])
                            ops[('S', s[i], u[i], vicino(s, i - 1), vicino(s, i + 1))] += 1
                        elif len(u) == len(s) + 1:
                            i = next(t for t in range(len(u)) if u[:t] == s[:t] and u[t + 1:] == s[t:])
                            ops[('I', None, u[i], vicino(u, i - 1), vicino(u, i + 1))] += 1
                        else:
                            i = next(t for t in range(len(s)) if s[:t] == u[:t] and s[t + 1:] == u[t:])
                            ops[('D', s[i], None, vicino(s, i - 1), vicino(s, i + 1))] += 1
                sulla[u] = k
                sulla.move_to_end(u)
    return ops


class OperatoreContesto:
    def __init__(self, ripiego, ops):
        self.ripiego = ripiego
        self.sd = defaultdict(list)       # (a, prima, dopo) -> [(tipo, b, peso)]
        self.ins = defaultdict(list)      # (prima, dopo) -> [(b, peso)]
        for (t, a, b, p, q), w in sorted(ops.items(), key=lambda kv: str(kv[0])):
            if t == 'I':
                self.ins[(p, q)].append((b, w))
            else:
                self.sd[(a, p, q)].append((t, b, w))

    def valida(self, u):
        return self.ripiego.valida(u)

    def modifica(self, u, rnd):
        u = tuple(u)
        n = len(u)
        cand, pesi = [], []
        for i in range(n):
            for t, b, w in self.sd.get((u[i], vicino(u, i - 1), vicino(u, i + 1)), ()):
                if t == 'S':
                    cand.append(u[:i] + (b,) + u[i + 1:])
                elif n > 1:
                    cand.append(u[:i] + u[i + 1:])
                else:
                    continue
                pesi.append(w)
        for i in range(n + 1):
            for b, w in self.ins.get((vicino(u, i - 1), vicino(u, i)), ()):
                cand.append(u[:i] + (b,) + u[i:])
                pesi.append(w)
        if not cand:
            return self.ripiego.modifica(u, rnd)
        return rnd.choices(cand, pesi)[0]


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ops = operazioni_contesto(pv)
    ripiego = e240.OperatoreEmpirico(c['mod'], e240.operazioni(pv))
    c2 = dict(c, mod=OperatoreContesto(ripiego, ops))
    conf = dict(e224.BASE, eta=1.0, kappa=1.0, chi=0.2)
    cols = ('tipi_su_parole_pagina', 'fra_le_100', 'uniche_nel_testo', 'somiglianza_vicine', 'lunghezza_media')
    ris = OrderedDict([('operazioni_distinte', len(ops)), ('Voynich', e234.descrittive(pv)), ('profilo_Voynich', e237.profilo(pv))])
    verifica = []
    for s in SEMI:
        rr = e236.dopo(e233.genera(c2, conf, s), freq, 100 + s)
        gp = e232.pagine_di(rr)
        r = e231.confronto(vpag, gp, rif)
        r.update(e234.descrittive(gp))
        r['profilo'] = e237.profilo(gp)
        if s == SEMI[0]:
            r['pagella_e224'] = e236.pagella(c, rr)
        verifica.append(r)
        print('seme %d: AUC %.3f %s | profilo %s' % (s, r['AUC'], ' '.join('%s %.3f' % (k, r[k]) for k in cols),
                                                   {k: round(v, 3) for k, v in r['profilo'].items() if k in e237.CLASSI}), flush=True)
    auc = statistics.mean(x['AUC'] for x in verifica)
    esito = 'indistinguibile' if auc <= 0.6 else 'migliore' if auc <= RIFERIMENTO - 0.05 else 'non migliore'
    pg = verifica[0]['pagella_e224']
    ris.update([('verifica', verifica), ('AUC_verifica', auc), ('riferimento_e235', RIFERIMENTO), ('esito', esito)])
    print('AUC media %.3f | pagella %d/18 riga %s mancano %s -> %s' % (auc, pg['pagella'], pg['riga'], pg['mancano'], esito), flush=True)
    json.dump(ris, open(os.path.join(RISULTATI, 'e241_operatore_contesto.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v, pv_ = ris['Voynich'], ris['profilo_Voynich']
    md = ['# e241 — Operatore di variante empirico condizionato ai segni vicini', '',
          "Come l'e240, con le %d operazioni contate insieme al segno prima e dopo; ripiego sull'operatore dell'e240. AUC del discriminatore "
          "dell'e231 sui semi 2–3; riferimento (e235) %.3f; e240: 0,908 e pagella 16/18. Preregistrazione: `preregistrazioni/e241.md`." % (len(ops), RIFERIMENTO), '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s | %s |' % (' | '.join('%.3f' % v[k] for k in cols), ' | '.join('%.1f%%' % (100 * pv_[k]) for k in e237.CLASSI))]
    for s, r in zip(SEMI, verifica):
        md.append('| seme %d | %.3f | %s | %s |' % (s, r['AUC'], ' | '.join('%.3f' % r[k] for k in cols),
                                                  ' | '.join('%.1f%%' % (100 * r['profilo'][k]) for k in e237.CLASSI)))
    md += ['', 'AUC media: %.3f. Pagella dell\'e224 (seme 2): %d/18, riga riprodotta: %s; mancano: %s.' % (
        auc, pg['pagella'], 'sì' if pg['riga'] else 'no', ', '.join(pg['mancano']) or 'nessuna'), '',
           'Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e241_operatore_contesto.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
