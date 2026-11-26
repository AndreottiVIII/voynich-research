# -*- coding: utf-8 -*-
"""IA44: le tavole note dei gradi e le divisioni note dei segni, scritte PRIMA di guardare lo zodiaco del manoscritto.

Fonte delle tavole dei gradi: William Lilly, *Christian Astrology* (1647), pp. 116-118 ("Two necessary tables of the signs"), nella
lettura che ne da' Deborah Houlding su https://www.skyscript.co.uk/deginf.html (pagina letta il 26/11/2026; (c) Houlding 2004-2005: qui
si copiano solo i numeri delle tavole tradizionali, non il suo testo). Varianti di al-Biruni (Elements, v. 457-458) solo per il genere
di Ariete, Acquario e Pesci, come marcate in quella pagina. Un grado va da 1 a 30 (il grado 1 e' 0°00'-0°59'). Le tavole del
Seicento hanno altre versioni (Tolomeo, Alcabizio, Manilio): ogni versione provata si conta fra le ricerche; qui se ne provano SETTE,
e basta (le altre non si provano).

Controllo interno: genere e luminosita' devono dividere i 30 gradi di ogni segno senza buchi ne' doppioni (`controlla()`).
Divisioni note dei segni: elemento, modalita', caldo/freddo, secco/umido, pianeta dominante (domicilio diurno o notturno). Le
stagioni NON si provano (tre segni vicini: ogni parola ricorrente in pagine vicine le "troverebbe").
"""
import re
from collections import OrderedDict

SEGNI12 = ('Ariete', 'Toro', 'Gemelli', 'Cancro', 'Leone', 'Vergine', 'Bilancia', 'Scorpione', 'Sagittario', 'Capricorno', 'Acquario', 'Pesci')


def _g(s):
    """'1-8, 10-15, 23-30' -> set di gradi; '' (nessuno) -> set vuoto."""
    out = set()
    for pezzo in re.split(r'\s*,\s*', s.strip()):
        if not pezzo or pezzo == '-':
            continue
        if '-' in pezzo:
            a, b = pezzo.split('-')
            out |= set(range(int(a), int(b) + 1))
        else:
            out.add(int(pezzo))
    return out


# genere (Lilly): maschili | femminili
_GENERE = OrderedDict([
    ('Ariete', ('1-8, 10-15, 23-30', '9, 16-22')), ('Toro', ('6-11, 18-21, 25-30', '1-5, 12-17, 22-24')),
    ('Gemelli', ('6-16, 23-26', '1-5, 17-22, 27-30')), ('Cancro', ('1-2, 9-10, 13-23, 28-30', '3-8, 11-12, 24-27')),
    ('Leone', ('1-5, 9-15, 24-30', '6-8, 16-23')), ('Vergine', ('9-12, 21-30', '1-8, 13-20')),
    ('Bilancia', ('1-5, 16-20, 28-30', '6-15, 21-27')), ('Scorpione', ('1-4, 15-17, 26-30', '5-14, 18-25')),
    ('Sagittario', ('1-2, 6-12, 25-30', '3-5, 13-24')), ('Capricorno', ('1-11, 20-30', '12-19')),
    ('Acquario', ('1-5, 16-21, 26-27', '6-15, 22-25, 28-30')), ('Pesci', ('1-10, 21-23, 29-30', '11-20, 24-28'))])
# varianti di al-Biruni del genere
_GENERE_BIRUNI = {'Ariete': ('1-7, 10-15, 23-30', '8, 9, 16-22'), 'Acquario': ('1-5, 13-18, 28-30', '6-12, 19-27'),
                  'Pesci': ('1-10, 13-15, 21-30', '11, 12, 16-20')}
# luminosita' (Lilly): chiari | scuri | fumosi | vuoti
_LUCE = OrderedDict([
    ('Ariete', ('4-8, 17-20, 25-29', '1-3, 9-16', '', '21-24, 30')), ('Toro', ('4-7, 13-15, 21-28', '1-3, 29-30', '', '8-12, 16-20')),
    ('Gemelli', ('1-4, 8-12, 17-22', '5-7, 23-27', '', '13-16, 28-30')), ('Cancro', ('1-12, 21-28', '13-14', '19-20', '15-18, 29-30')),
    ('Leone', ('26-30', '1-10', '11-20', '21-25')), ('Vergine', ('6-8, 11-16', '1-5, 28-30', '17-22', '9-10, 23-27')),
    ('Bilancia', ('1-5, 11-18, 22-27', '6-10, 19-21', '', '28-30')), ('Scorpione', ('4-8, 15-22', '1-3, 30', '23-24', '9-14, 25-29')),
    ('Sagittario', ('1-9, 13-19, 24-30', '10-12', '20-23', '')), ('Capricorno', ('8-10', '1-7, 16-22, 26-30', '11-15', '23-25')),
    ('Acquario', ('5-9, 14-21, 26-30', '10-13', '1-4', '22-25')), ('Pesci', ('7-12, 26-28', '1-6, 13-22, 29-30', '', '23-25'))])
# altre categorie (Lilly): fossati | zoppi | "fortuna crescente"
_ALTRE = OrderedDict([
    ('Ariete', ('6, 11, 16, 23, 29', '', '19')), ('Toro', ('5, 12, 24, 25', '6-10', '3, 15, 27')),
    ('Gemelli', ('2, 12, 17, 26, 30', '', '11')), ('Cancro', ('12, 17, 23, 26, 30', '9-15', '1-4, 15')),
    ('Leone', ('6, 13, 15, 22, 23, 28', '18, 27, 28', '2, 5, 7, 19')), ('Vergine', ('8, 13, 16, 21, 22', '', '3, 14, 20')),
    ('Bilancia', ('1, 7, 20, 30', '', '3, 15, 21')), ('Scorpione', ('9, 10, 22, 23, 27', '19, 28', '7, 18, 20')),
    ('Sagittario', ('7, 12, 15, 24, 27, 30', '1, 7, 8, 18, 19', '13, 20')), ('Capricorno', ('7, 17, 22, 24, 29', '26-29', '12-14, 20')),
    ('Acquario', ('1, 12, 17, 22, 24, 29', '18, 19', '7, 16, 17, 20')), ('Pesci', ('4, 9, 24, 27, 28', '', '13, 20'))])


def controlla():
    """Genere (Lilly e Biruni) e luminosita' dividono 1-30 senza buchi ne' doppioni; ritorna la lista dei problemi (vuota se ok)."""
    tutto = set(range(1, 31))
    guai = []
    for s, (m, f) in _GENERE.items():
        a, b = _g(m), _g(f)
        if a & b or a | b != tutto:
            guai.append('genere Lilly %s' % s)
    for s, (m, f) in _GENERE_BIRUNI.items():
        a, b = _g(m), _g(f)
        if a & b or a | b != tutto:
            guai.append('genere Biruni %s' % s)
    for s, parti in _LUCE.items():
        ins = [_g(x) for x in parti]
        unione = set()
        for x in ins:
            if unione & x:
                guai.append('luce doppioni %s' % s)
            unione |= x
        if unione != tutto:
            guai.append('luce buchi %s: %s' % (s, sorted(tutto - unione)))
    return guai


def _vettore(insieme_1, insieme_0=None):
    """30 valori: 1 se il grado e' in insieme_1; 0 se e' in insieme_0 (o, se insieme_0 e' None, fuori da insieme_1); -1 altrimenti."""
    out = []
    for d in range(1, 31):
        if d in insieme_1:
            out.append(1)
        elif insieme_0 is None or d in insieme_0:
            out.append(0)
        else:
            out.append(-1)
    return out


def tavole(tutte=False):
    """Le tavole binarie: nome -> {segno: 30 valori (1, 0, -1 = grado escluso)}. Di norma le SEI provate (genere Lilly, genere con
    varianti al-Biruni, chiaro/scuro, chiaro/non chiaro, fossati, fortuna crescente). La settima (zoppi/no) esce dal programma prima
    di ogni numero sul manoscritto: ha gradi "zoppi" in soli 7 segni su 12 e, nella prova su dati finti (stesso programma, 10 prove
    con meta' delle righe con una parola di classe), non si vede (0 su 10; con il 70% delle righe 2 su 10). Con `tutte` c'e' anche quella."""
    T = OrderedDict()
    T['G1 maschile/femminile (Lilly)'] = OrderedDict((s, _vettore(_g(m), _g(f))) for s, (m, f) in _GENERE.items())
    T['G2 maschile/femminile (con varianti al-Biruni)'] = OrderedDict(
        (s, _vettore(_g(_GENERE_BIRUNI.get(s, (m, f))[0]), _g(_GENERE_BIRUNI.get(s, (m, f))[1]))) for s, (m, f) in _GENERE.items())
    T['L1 chiaro/scuro (fumosi e vuoti esclusi)'] = OrderedDict((s, _vettore(_g(p[0]), _g(p[1]))) for s, p in _LUCE.items())
    T['L2 chiaro/non chiaro'] = OrderedDict((s, _vettore(_g(p[0]))) for s, p in _LUCE.items())
    T['P1 fossato/no'] = OrderedDict((s, _vettore(_g(p[0]))) for s, p in _ALTRE.items())
    T['F1 fortuna crescente/no'] = OrderedDict((s, _vettore(_g(p[2]))) for s, p in _ALTRE.items())
    if tutte:
        T['Z1 zoppo/no'] = OrderedDict((s, _vettore(_g(p[1]))) for s, p in _ALTRE.items())
    return T


# divisioni note dei 12 segni (indice sulla ruota: 0 Ariete ... 11 Pesci)
def divisioni(tutte=False):
    """Le divisioni note dei segni provate: elemento, modalita', pianeta (nome -> 12 etichette di classe, una per segno della ruota).
    Con `tutte` anche caldo/freddo e secco/umido: con 10 segni e due classi da 5 non si vedono nemmeno con 40 parole piantate per
    classe (1 prova su 10 a 40 parole; prova su dati finti), e per questo escono dal programma prima di ogni numero sul manoscritto."""
    elemento = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]                    # fuoco, terra, aria, acqua
    modalita = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2]                    # cardinali, fissi, mobili
    caldo_freddo = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]                # caldi (fuoco, aria) | freddi (terra, acqua)
    secco_umido = [0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1]                 # secchi (fuoco, terra) | umidi (aria, acqua)
    # pianeta dominante: Marte Ariete e Scorpione; Venere Toro e Bilancia; Mercurio Gemelli e Vergine; Luna Cancro; Sole Leone;
    # Giove Sagittario e Pesci; Saturno Capricorno e Acquario
    pianeta = [0, 1, 2, 3, 4, 2, 1, 0, 5, 6, 6, 5]
    out = OrderedDict([('elemento', elemento), ('modalita', modalita), ('caldo/freddo', caldo_freddo), ('secco/umido', secco_umido),
                       ('pianeta', pianeta)])
    if not tutte:
        out = OrderedDict((k, v) for k, v in out.items() if k in ('elemento', 'modalita', 'pianeta'))
    return out
