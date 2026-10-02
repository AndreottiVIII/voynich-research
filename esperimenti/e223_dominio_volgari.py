# -*- coding: utf-8 -*-
"""Esperimento 223: come l'e213 (una chiave, modelli di dominio per sezione, verifica fuori campione), con corpora di
dominio ricavati dai testi Wikipedia di Hermes in italiano, tedesco, francese, spagnolo e catalano.

Preregistrazione: preregistrazioni/e223.md. Scrive risultati/e223_dominio_volgari.json e .md.
"""
import json, os, random, sys
from collections import OrderedDict
from multiprocessing import Pool

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, QUI)
import generatori, ricottura, trascrizione
import e17_ricottura as e17
import e131_procedimento_riga as e131
import e145_abitudini as e145
import e152_righe_in_ordine as e152
import e153_righe_rifinite as e153
import e160_testo_ripulito as e160
import e162_messaggio_nei_temi as e162
import e192_generatore_misto as e192
import e213_decifrazione_di_dominio as e213

RISULTATI = os.path.join(QUI, '..', 'risultati')
CORPORA = os.path.join(QUI, '..', 'dati', 'cache', 'hermes_wikipedia')
BRANO, MINIMO, MAX_DOMINIO, SFONDO = 150, 3, 150000, 250000
CHIAVI = {
    'Italian': {'piante': 'pianta piante foglie foglia radice radici fiore fiori semi seme erba erbe fusto', 'ricette': 'acqua bollire cuocere olio sale miele vino ricetta mescolare polvere aceto',
                'astronomia': 'stella stelle luna sole pianeta pianeti costellazione cielo zodiaco segno orbita'},
    'German': {'piante': 'pflanze pflanzen blätter blatt wurzel wurzeln blüte blüten samen kraut kräuter stängel', 'ricette': 'wasser kochen öl salz honig wein rezept mischen pulver essig',
               'astronomia': 'stern sterne mond sonne planet planeten sternbild himmel tierkreis umlaufbahn'},
    'French': {'piante': 'plante plantes feuilles feuille racine racines fleur fleurs graines herbe tige', 'ricette': 'eau bouillir cuire huile sel miel vin recette mélanger poudre vinaigre',
               'astronomia': 'étoile étoiles lune soleil planète planètes constellation ciel zodiaque orbite'},
    'Spanish': {'piante': 'planta plantas hojas hoja raíz raíces flor flores semillas hierba tallo', 'ricette': 'agua hervir cocer aceite sal miel vino receta mezclar polvo vinagre',
                'astronomia': 'estrella estrellas luna sol planeta planetas constelación cielo zodíaco órbita'},
    'Catalan': {'piante': 'planta plantes fulles fulla arrel arrels flor flors llavors herba tija', 'ricette': 'aigua bullir coure oli sal mel vi recepta barrejar pols vinagre',
                'astronomia': 'estrella estrelles lluna sol planeta planetes constel·lació cel zodíac òrbita'},
}


def corpora_lingua(lingua):
    parole = open(os.path.join(CORPORA, lingua + '.txt'), encoding='utf-8', errors='ignore').read().split()
    chiavi = {d: set(v.split()) for d, v in CHIAVI[lingua].items()}
    dom = {d: [] for d in chiavi}
    sfondo = []
    for i in range(0, len(parole) - BRANO, BRANO):
        b = parole[i:i + BRANO]
        conti = {d: sum(w in k for w in b) for d, k in chiavi.items()}
        d, c = max(conti.items(), key=lambda x: x[1])
        if c >= MINIMO and len(dom[d]) < MAX_DOMINIO:
            dom[d] += b
        elif c == 0 and len(sfondo) < SFONDO:
            sfondo += b
    return dom, sfondo


def modelli(lingua):
    dom, sfondo = corpora_lingua(lingua)
    tutte = sfondo + [w for v in dom.values() for w in v]
    lettere = e17.alfabeto(tutte)
    pul = lambda ws: e17.pulisci(ws, lettere)
    sf = pul(sfondo)
    tutte_lettere = ''.join(sorted(lettere))
    mod, ctrl = OrderedDict(), OrderedDict()
    for d in e213.DOMINI:
        c = pul(dom[d])
        k = int(len(c) * 0.8)
        mod[d] = ricottura.ModelloLettere(''.join(c[:k] * 3 + sf) + tutte_lettere, n=5)
        ctrl[d] = c[k:]
    return mod, ctrl, {d: len(v) for d, v in dom.items()}


def una(args):
    lingua, voy, neg = args
    rnd = random.Random('e223-' + lingua)
    mod, ctrl, dim = modelli(lingua)
    simboli = len({u for _, rr in voy for r in rr for u in r})
    pos = e213.controllo_positivo(voy, ctrl, rnd, simboli)
    r = OrderedDict([('parole_di_dominio', dim)])
    for nome, pagine in (('controllo positivo', pos), ('Voynich ripulito', voy), ('controllo negativo (generatore)', neg)):
        r[nome] = e213.prova('%s, %s' % (lingua, nome), pagine, mod, rnd)
    return lingua, r


def main():
    pv = e213.pagine_voynich()
    voy = e213.a_unita([(e213.dominio_di(s), rr) for p, (s, rr) in pv.items() if e213.dominio_di(s)])
    vp = trascrizione.parole(trascrizione.testo_corrente(trascrizione.leggi('ZL')))
    P, starts, q, L = e145.pagine(), e131.inizi(), e145.quote(), e152.lift()
    e162.THETA, e162.C, e153.K, e153.LAM = 0.3, 1.0, 3, 1.0
    e192._ATT, e192._NU = set(vp), 0.4
    e153.variante = e192.variante
    per_g = OrderedDict()
    for pag, ini, ps in e162.genera(P, starts, q, L, generatori.Modifiche(vp, e162.D), 1, None):
        per_g.setdefault(pag, []).append((ini, ps))
    pul_g = e160.ripulisci(list(per_g.values()))
    neg = e213.a_unita([(e213.dominio_di(pv[p][0]), [[w if trascrizione.pulita(w) else None for w in ps] for _, ps in rr])
                        for p, rr in zip(per_g, pul_g) if p in pv and e213.dominio_di(pv[p][0])])
    ris = OrderedDict()
    with Pool(int(os.environ.get('PROCESSI', '2'))) as pool:
        for lingua, r in pool.imap(una, [(l, voy, neg) for l in CHIAVI]):
            ris[lingua] = r
            json.dump(ris, open(os.path.join(RISULTATI, 'e223_dominio_volgari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    righe, esiti = [], OrderedDict()
    for lingua, r in ris.items():
        zp, zv, zn = (r[k]['z'] or 0 for k in ('controllo positivo', 'Voynich ripulito', 'controllo negativo (generatore)'))
        esiti[lingua] = 'non valido' if zp <= 4 else ('lettura di dominio, da esaminare' if zv > 4 and zv - zn >= 3 else 'nessuna lettura')
        righe.append('| %s | %s | %.1f | %.1f | %.1f | %s |' % (lingua, r['parole_di_dominio'], zp, zv, zn, esiti[lingua]))
    json.dump({'lingue': ris, 'esiti': esiti}, open(os.path.join(RISULTATI, 'e223_dominio_volgari.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    md = ['# e223 — Decifrazione guidata dal contenuto in lingue volgari', '', 'z della discriminazione fra sezioni fuori campione. Preregistrazione: `preregistrazioni/e223.md`.', '',
          '| lingua | parole di dominio | z positivo | z Voynich | z generatore | esito |', '|---|---|---|---|---|---|'] + righe
    md += ['', 'Esempi decifrati del Voynich:', '']
    for lingua, r in ris.items():
        md.append('- %s: %s' % (lingua, '; '.join('%s: %s' % (d, ' / '.join(x[:60] for x in v)) for d, v in r['Voynich ripulito']['esempi'].items())))
    open(os.path.join(RISULTATI, 'e223_dominio_volgari.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print(esiti)


if __name__ == '__main__':
    main()
