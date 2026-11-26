# -*- coding: utf-8 -*-
"""IA43, prove del codice (non e' un esperimento): solo su libri v21 senza messaggio con chiavi di prova (3xx) e su numeri finti. Nessun numero sul Voynich.

    python esperimenti/tetto_prove.py piantare     (il piantare: posti, dosi annidate, forme, recupero con la chiave)
    python esperimenti/tetto_prove.py criteri      (direzioni, soglie, k, tetto su numeri finti)

I libri di partenza (`base_302.pkl`, ...) stanno in dati/cache/ia43_prove/basi e si fanno con `tetto_piantare.genera_base`.
"""
import os
import random
import sys
from collections import Counter

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import tetto_piantare as P  # noqa: E402
import tetto_criteri as C  # noqa: E402

BASI = os.path.join(QUI, '..', 'dati', 'cache', 'ia43_prove', 'basi')
ok_tutti = [True]


def verifica(cond, msg):
    print(('  ok   ' if cond else '  FALLITO ') + msg, flush=True)
    if not cond:
        ok_tutti[0] = False


def prova_piantare():
    t = P.leggi_base('302', BASI)
    n_par = sum(len(ps) for _, _, ps in t)
    print('libro 302: %d righe, %d parole, %d tipi' % (len(t), n_par, len({w for _, _, ps in t for w in ps})))
    msg = P.testo_chiaro()
    print('messaggio: %d parole, %d tipi, prime: %s' % (len(msg), len(set(msg)), ' '.join(msg[:8])))
    verifica(len(msg) > 25000, 'testo in chiaro abbastanza lungo (Macer + Isidoro; il libro ha 35-36 mila posti: il testo ricomincia)')
    # dose 0: niente cambia
    t0, i0 = P.pianta(t, '302', 'a', 0.0, 1)
    verifica(t0 == t and i0['posti_sostituiti'] == 0, 'dose 0: il libro non cambia')
    # struttura invariata
    for f, alt in (('a', 1), ('a', 3), ('a', 10), ('b', 1), ('b', 3), ('b', 6), ('c', 1), ('c', 10), ('z', 1)):
        tt, info = P.pianta(t, '302', f, 0.4, alt)
        stessa = [(p, i, len(ps)) for p, i, ps in tt] == [(p, i, len(ps)) for p, i, ps in t]
        cambiati = sum(a != b for (_, _, x), (_, _, y) in zip(t, tt) for a, b in zip(x, y))
        verifica(stessa, 'forma %s alt %d: pagine, inizi e parole per riga identici' % (f, alt))
        verifica(abs(info['posti_sostituiti'] / n_par - 0.4) < 0.01, 'forma %s alt %d: quota di posti sostituiti %.3f (attesa 0,40)' % (f, alt, info['posti_sostituiti'] / n_par))
        verifica(0.3 * info['posti_sostituiti'] < cambiati <= info['posti_sostituiti'], 'forma %s alt %d: parole diverse dalla base %d su %d posti (alcune coincidono)' % (f, alt, cambiati, info['posti_sostituiti']))
    # dosi annidate
    _, i5 = P.pianta(t, '302', 'a', 0.05, 1)
    _, i40 = P.pianta(t, '302', 'a', 0.40, 1)
    _, ib = P.pianta(t, '302', 'b', 0.40, 1)
    verifica(set(i5['posti']) <= set(i40['posti']), 'posti a 5% dentro quelli a 40%')
    verifica(i40['posti'] == ib['posti'], 'stessi posti per tutte le forme')
    _, i303 = P.pianta(P.leggi_base('303', BASI), '303', 'a', 0.40, 1)
    verifica(set(i303['posti']) != set(i40['posti']), 'posti diversi per basi diverse')
    # dose piena: tutti i posti
    t1, i1 = P.pianta(t, '302', 'a', 1.0, 1)
    verifica(i1['posti_sostituiti'] == n_par, 'dose 100%: tutti i posti')
    # recupero con la chiave
    for alt, minimo in ((1, 0.99), (3, 0.75), (10, 0.55)):
        tt, info = P.pianta(t, '302', 'a', 1.0, alt)
        r = P.recuperato(tt, info)
        verifica(r >= minimo, 'forma a, %d alternative, 100%%: tipi latini ritrovati con la chiave %.3f (>= %.2f; i tipi rari condividono parole)' % (alt, r, minimo))
    tt, info = P.pianta(t, '302', 'a', 0.40, 1)
    giusta = P.recuperato(tt, info)
    tutti = set(P.posti(tt)) - set(info['posti'])
    sbagliati = random.Random(1).sample(sorted(tutti), len(info['posti']))
    sba = P.recuperato(tt, info, posti_alt=sbagliati)
    verifica(giusta >= 0.99 and sba < 0.05, 'forma a 40%%: chiave giusta %.3f, chiave sbagliata (altri posti) %.3f' % (giusta, sba))
    # c: stesse parole di a dentro ogni pagina, ordine diverso
    ta, ia_ = P.pianta(t, '302', 'a', 0.40, 1)
    tc, ic = P.pianta(t, '302', 'c', 0.40, 1)
    per_a, per_c = {}, {}
    for (i, j), w in zip(ia_['posti'], ia_['parole_messaggio']):
        per_a.setdefault(t[i][0], []).append(w)
    for (i, j), w in zip(ic['posti'], ic['parole_messaggio']):
        per_c.setdefault(t[i][0], []).append(w)
    verifica(all(Counter(per_a[p]) == Counter(per_c[p]) for p in per_a), 'c: dentro ogni pagina le stesse parole di a')
    verifica(sum(per_a[p] != per_c[p] for p in per_a) > 0.9 * len(per_a), 'c: l\'ordine dentro la pagina cambia (quasi sempre)')
    # z: stesse parole di a su tutto il libro, ordine e pagine diversi
    tz, iz = P.pianta(t, '302', 'z', 0.40, 1)
    verifica(Counter(iz['parole_messaggio']) == Counter(ia_['parole_messaggio']) and iz['parole_messaggio'] != ia_['parole_messaggio'], 'z: stesso lessico di a su tutto il libro, ordine rimescolato')
    # b: parole delle tavole Naibbe (tavole usate: le prime alt)
    tab = P._tavole()
    unig = {v for k, v in tab.items() if k.startswith('unigram_')}
    for alt in (1, 3, 6):
        tt, info = P.pianta(t, '302', 'b', 1.0, alt)
        parole = [tt[i][2][j] for i, j in info['posti']]
        verifica(len(set(parole)) > 100, 'forma b, %d tavole: %d parole diverse' % (alt, len(set(parole))))
        verifica(len(set(parole) & unig) > 0, 'forma b, %d tavole: ci sono parole di una lettera sola' % alt)
    # confronto tavole: con 1 sola tavola meno parole diverse che con 6
    def n_diverse(alt):
        tt, info = P.pianta(t, '302', 'b', 1.0, alt)
        return len({tt[i][2][j] for i, j in info['posti']})
    n1, n6 = n_diverse(1), n_diverse(6)
    verifica(n1 < n6, 'forma b: con 1 tavola meno parole diverse (%d) che con 6 (%d)' % (n1, n6))


def prova_criteri():
    rnd = random.Random(43)
    nomi = ['m%d' % i for i in range(8)]
    neg = {n: [rnd.gauss(0, 1) for _ in range(24)] for n in nomi}
    # misure 0-3 salgono di 4 sd con il messaggio, misura 4 scende, 5 non cambia, 6 sale ma piano, 7 manca
    shift = {'m0': 4, 'm1': 4, 'm2': 4, 'm3': 4, 'm4': -4, 'm5': 0, 'm6': 1}
    cal = {n: [shift.get(n, 0) + rnd.gauss(0, 1) for _ in range(6)] for n in nomi[:7]}
    cal['m7'] = [None] * 6
    d = C.direzioni(neg, cal)
    verifica(all(d[n]['valida'] for n in ('m0', 'm1', 'm2', 'm3', 'm4')), 'direzioni: le cinque misure che si spostano forte sono valide')
    verifica(d['m4']['segno'] == -1 and d['m0']['segno'] == 1, 'direzioni: segni giusti')
    verifica(not d['m5']['valida'] and not d['m7']['valida'], 'direzioni: la misura ferma e quella senza valori non sono valide')
    sog = C.soglie(neg, d)
    verifica(set(sog) == {n for n in d if d[n]['valida']}, 'soglie solo per le misure valide')
    verifica(abs(sog['m0'] - max(neg['m0'])) < 1e-12 and abs(sog['m4'] - min(neg['m4'])) < 1e-12, 'soglie: massimo (o minimo) dei libri senza messaggio')
    libri = [{n: neg[n][i] for n in nomi} for i in range(24)]
    k, fa = C.scegli_k(libri, d)
    verifica(k is not None and fa[k] <= 0.05, 'k scelto %s con falsi allarmi %.3f' % (k, fa.get(k, -1)))
    # libri piantati a varie dosi: sposto m0-m4 di dose * 4 sd
    vis = {}
    for dose in C.DOSI_PRESCRITTE:
        lib = []
        for _ in range(12):
            b = {n: rnd.gauss(0, 1) + (shift.get(n, 0) * dose) for n in nomi[:7]}
            lib.append(b)
        vis[dose] = sum(C.libri_visti(lib, sog, d, k))
    print('  libri visti per dose (finti):', vis)
    t = C.tetto(vis)
    verifica(t is not None and 0.20 <= t <= 1.0, 'tetto sui numeri finti (spostamento di 4 sd a dose piena, 5 misure su 7): %s' % t)
    verifica(vis[1.0] == 12 and vis[0.05] <= 2, 'a dose piena si vedono tutti, a 5% quasi nessuno')
    verifica(C.tetto({0.05: 12, 0.1: 3, 0.2: 12, 0.4: 12, 0.7: 12, 1.0: 12}) == 0.2, 'tetto: conta da dove in su tutti i libri sono visti')
    verifica(C.tetto({0.05: 0, 0.1: 0, 0.2: 0, 0.4: 5, 0.7: 8, 1.0: 11}) == 1.0, 'tetto: solo la dose piena')
    verifica(C.tetto({0.05: 0, 1.0: 3}) is None, 'tetto: nessuno')
    # un libro senza messaggio non si vede
    nuovi = [{n: rnd.gauss(0, 1) for n in nomi[:7]} for _ in range(200)]
    fa_nuovi = sum(C.libri_visti(nuovi, sog, d, k)) / 200.0
    verifica(fa_nuovi <= 0.10, 'libri nuovi senza messaggio visti: %.3f' % fa_nuovi)
    verifica(C.lettura_tetto(0.10).startswith('tetto basso') and C.lettura_tetto(None).startswith('nessun tetto'), 'letture del tetto')


def prova_esito():
    """L'analisi e le tabelle di `ia43_tetto` su risultati FINTI (nessun libro, nessuna misura vera): serve a provare che analisi_base, esito e scrivi_esito girano e danno cio' che deve."""
    cart = os.path.join(QUI, '..', 'dati', 'cache', 'ia43_prove', 'uscita_finta')
    os.makedirs(cart, exist_ok=True)
    os.environ.update(PROVA43='1', N_NEG43='24', N_PIA43='12', N_CAL43='6', FORME43='abc', DOSI43='5-10-20-40-70-100', ALT43='1-3-10', ALT_B43='1-3-6', DOSI_CTL43='2-5-10-20-40-100', DOSI_BASSE43='1-2',
                      MIN_VISTI43='11', USCITA43=cart, CACHE43=os.path.join(cart, 'cache'))
    import ia43_tetto as I
    from collections import OrderedDict
    import tetto_batteria as T
    rnd = random.Random(4343)
    nomi_M = list(T.NOMI_M)
    forza = {n: (4.0 if i % 3 == 0 else (-4.0 if i % 3 == 1 else 0.0)) for i, n in enumerate(nomi_M)}
    forza.update({'e231': 3.0, 'e266': 3.0, 'N': 3.0, 'b': 3.0})
    fatt = {'a': 1.0, 'b': 0.7, 'c': 0.3, 'z': 0.5}

    def valori_libro(spec, base):
        f, dose = I.cella(spec) or (None, 0), I.dose_di(spec) / 100.0
        forma = f[0] if isinstance(f, tuple) else f
        out = OrderedDict()
        for n, v in base.items():
            out[n] = v + (forza.get(n, 0.0) * fatt.get(forma, 0.0) * dose if forma else 0.0)
        return out
    corse = OrderedDict()
    base_di = {}
    for nome, spec in I.elenco().items():
        k = spec[-1]
        if k not in base_di:
            base_di[k] = OrderedDict((n, rnd.gauss(0, 1)) for n in nomi_M + ['e231', 'e266', 'N'])
        v = valori_libro(spec, base_di[k])
        corse['M|%s' % nome] = OrderedDict([('lavoro', 'M|%s' % nome), ('nome', nome), ('misure', OrderedDict((n, v[n]) for n in nomi_M))])
        corse['J|%s' % nome] = OrderedDict([('lavoro', 'J|%s' % nome), ('nome', nome), ('giudici', OrderedDict((n, v[n]) for n in ('e231', 'e266', 'N')))])
    for lav in I.lavori_fase2():
        if lav[0] == 'B':
            nomi = lav[2]
            vals = []
            for n in nomi:
                spec = I.elenco()[n]
                f = I.cella(spec)
                forma = f[0] if f else None
                vals.append(rnd.gauss(0, 1) + (forza['b'] * fatt.get(forma, 0.0) * I.dose_di(spec) / 100.0 if forma else 0.0))
            corse['B|%s' % lav[1]] = OrderedDict([('lavoro', 'B|%s' % lav[1]), ('nomi', nomi), ('per_libro', vals)])
    corse['V'] = OrderedDict([('lavoro', 'V'), ('misure', OrderedDict((n, rnd.gauss(0, 1)) for n in nomi_M))])
    A = I.analisi_base(corse)
    verifica(A['k_B']['a'] is not None and A['k_B']['b'] is not None and A['k_B']['c'] is None, 'k trovato per a e b; per c (spostamento finto troppo piccolo: nessuna misura valida) la batteria è cieca: %s' % dict(A['k_B']))
    n_val = {f: sum(d['valida'] for d in A['dirz'][f].values()) for f in 'abc'}
    verifica(n_val['a'] >= 15, 'misure valide per la forma a: %s' % n_val)
    verifica(A['fa_B']['a'][A['k_B']['a']] <= 0.05, 'falsi allarmi dei libri senza messaggio al piu\' 5%')
    ris = I.esito(corse, A)
    ca = ris['celle']['a1']
    print('  cella a1: libri visti', dict(ca['visti_batteria']), 'tetto', ca['tetto'], '| c1:', ris['celle']['c1']['tetto'], '| b1:', ris['celle']['b1']['tetto'])
    verifica(ris['controllo_positivo']['passa'] is True, 'controllo positivo passato sui numeri finti')
    verifica(ca['visti_batteria'][100] == 12 and ca['visti_batteria'][5] <= 3, 'a dose piena 12 libri visti, a 5% pochi')
    verifica(ca['tetto'] is not None and (ris['celle']['c1']['tetto'] is None or ris['celle']['c1']['tetto'] >= ca['tetto']), 'forma a: tetto non più alto di quello di c')
    verifica(ris['vero']['a']['visto'] is False, 'il "vero" finto (senza messaggio) non è visto')
    I.scrivi_esito(ris)
    md = open(os.path.join(cart, 'ia43_tetto_prova.md'), encoding='utf-8').read()
    verifica('| a1 |' in md and 'tetto' in md and 'Controllo positivo' in md, 'tabella scritta (%d righe)' % md.count(chr(10)))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    {'piantare': prova_piantare, 'criteri': prova_criteri, 'esito': prova_esito}[cmd]()
    print('TUTTO OK' if ok_tutti[0] else 'CI SONO PROVE FALLITE')
    sys.exit(0 if ok_tutti[0] else 1)
