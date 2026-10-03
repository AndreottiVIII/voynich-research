# -*- coding: utf-8 -*-
"""Esperimento 240: il generatore "copia e modifica" migliore (e233/e235) con l'operatore di variante empirico (operazioni
osservate fra parole vicine della stessa pagina nel Voynich, e239) al posto di generatori.Modifiche.

Preregistrazione: preregistrazioni/e240.md. Scrive risultati/e240_operatore_empirico.json e .md.
"""
import json, os, random, statistics, sys
from collections import Counter, OrderedDict, defaultdict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import e224_generatore_completo as e224
import e227d_prefissi_staccati as e227d
import e231_discriminatore as e231
import e232_meno_pagina as e232
import e233_frequenti_esatte as e233
import e234_tema_variato as e234
import e236_due_fonti as e236
import e237_riuso_pagina as e237
import e239_operatore_variante as e239

RISULTATI = os.path.join(QUI, '..', 'risultati')
SEMI, RIFERIMENTO = (2, 3), 0.889
D = e237.D


def classe(i, n):
    return 'iniziale' if i == 0 else ('finale' if i == n - 1 else 'interna')


def operazioni(pagine):
    """Counter di (tipo, a, b, classe di posizione) dalle varianti della pagina (come e239)."""
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
                            ops[('S', s[i], u[i], classe(i, len(s)))] += 1
                        elif len(u) == len(s) + 1:
                            i = next(t for t in range(len(u)) if u[:t] == s[:t] and u[t + 1:] == s[t:])
                            ops[('I', None, u[i], classe(i, len(u)))] += 1
                        else:
                            i = next(t for t in range(len(s)) if s[:t] == u[:t] and s[t + 1:] == u[t:])
                            ops[('D', s[i], None, classe(i, len(s)))] += 1
                sulla[u] = k
                sulla.move_to_end(u)
    return ops


class OperatoreEmpirico:
    """Stessa interfaccia di generatori.Modifiche (modifica, valida); le modifiche si estraggono fra quelle applicabili con
    peso pari alla loro frequenza fra le varianti del Voynich."""

    def __init__(self, vecchio, ops):
        self.vecchio = vecchio
        self.sd = defaultdict(list)          # (segno, classe) -> [(tipo, b, peso)]
        self.ins = defaultdict(list)         # classe -> [(b, peso)]
        for (t, a, b, cl), w in sorted(ops.items(), key=lambda kv: str(kv[0])):
            if t == 'I':
                self.ins[cl].append((b, w))
            else:
                self.sd[(a, cl)].append((t, b, w))

    def valida(self, u):
        return self.vecchio.valida(u)

    def modifica(self, u, rnd):
        u = tuple(u)
        n = len(u)
        cand, pesi = [], []
        for i in range(n):
            for t, b, w in self.sd.get((u[i], classe(i, n)), ()):
                if t == 'S':
                    cand.append(u[:i] + (b,) + u[i + 1:])
                elif n > 1:
                    cand.append(u[:i] + u[i + 1:])
                else:
                    continue
                pesi.append(w)
        for i in range(n + 1):
            for b, w in self.ins.get(classe(i, n + 1), ()):
                cand.append(u[:i] + (b,) + u[i:])
                pesi.append(w)
        if not cand:
            return self.vecchio.modifica(u, rnd)
        return rnd.choices(cand, pesi)[0]


def main():
    c = e224.contesto()
    freq = Counter(c['voy'])
    vpag = e231.voynich()
    rif = e231.riferimenti(vpag)
    pv = OrderedDict((p, rr) for p, (_, rr) in vpag.items())
    ops = operazioni(pv)
    c2 = dict(c, mod=OperatoreEmpirico(c['mod'], ops))
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
        op = e239.operatore(gp)
        r['operatore'] = OrderedDict([('tipi', op['tipi']), ('copertura_25', op['copertura_25']), ('prime_10', op['prime_25'][:10])])
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
    json.dump(ris, open(os.path.join(RISULTATI, 'e240_operatore_empirico.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    v, pv_ = ris['Voynich'], ris['profilo_Voynich']
    md = ['# e240 — Il generatore con l\'operatore di variante empirico', '',
          "Generatore \"copia e modifica\" migliore (e233/e235: κ 1, χ 0,2, η 1) con le modifiche estratte dalle %d operazioni osservate fra "
          "varianti della stessa pagina nel Voynich; spezzature e prefissi staccati dopo la generazione. AUC del discriminatore dell'e231 "
          'sui semi 2–3; riferimento (stesso generatore con l\'operatore vecchio, e235) %.3f. Preregistrazione: `preregistrazioni/e240.md`.' % (len(ops), RIFERIMENTO), '',
          '| | AUC | tipi su parole (pagina) | fra le 100 | uniche nel testo | somiglianza vicine | lunghezza media | R | V | F | A | N |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|',
          '| **Voynich** | | %s | %s |' % (' | '.join('%.3f' % v[k] for k in cols), ' | '.join('%.1f%%' % (100 * pv_[k]) for k in e237.CLASSI))]
    for s, r in zip(SEMI, verifica):
        md.append('| seme %d | %.3f | %s | %s |' % (s, r['AUC'], ' | '.join('%.3f' % r[k] for k in cols),
                                                  ' | '.join('%.1f%%' % (100 * r['profilo'][k]) for k in e237.CLASSI)))
    md += ['', 'AUC media: %.3f. Pagella dell\'e224 (seme 2): %d/18, riga riprodotta: %s; mancano: %s.' % (
        auc, pg['pagella'], 'sì' if pg['riga'] else 'no', ', '.join(pg['mancano']) or 'nessuna'), '',
           'Operazioni più frequenti nelle varianti generate (seme 2): %s.' % ', '.join('%s %.1f%%' % (o, 100 * q) for o, q in verifica[0]['operatore']['prime_10']), '',
           'Caratteristiche più pesanti (seme 2; coefficiente positivo = più nel generatore):', '',
           '| caratteristica | coefficiente | Voynich | generatore |', '|---|---|---|---|']
    for n, cf, a, b in verifica[0]['piu_pesanti']:
        md.append('| %s | %+.2f | %.4f | %.4f |' % (n, cf, a, b))
    md += ['', 'Esito: **%s**.' % esito]
    open(os.path.join(RISULTATI, 'e240_operatore_empirico.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')


if __name__ == '__main__':
    main()
