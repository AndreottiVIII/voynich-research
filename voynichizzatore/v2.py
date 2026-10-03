# -*- coding: utf-8 -*-
"""Voynichizzatore, versione 2 (3/10/2026): il nascondiglio della v1 (scelte di grafia con la codifica aritmetica) dentro un
corpo migliore. Corpo predefinito: la configurazione dell'e288 (penalita' per le ripetizioni immediate 0,5, copia per indice
dalla riga sopra 0,10, spezzature 0,04), 18/18 su due semi di verifica e 17/18 sul terzo. Con --parametri si usa un file di
parametri della regolazione congiunta (e253 o e289).

    python voynichizzatore/v2.py codifica testo.txt --chiave PAROLA --uscita manoscritto.txt [--parametri file.json]
    python voynichizzatore/v2.py decodifica manoscritto.txt --chiave PAROLA [--uscita testo.txt]
    python voynichizzatore/v2.py valuta manoscritto.txt --chiave PAROLA [--parametri file.json]
"""
import argparse, json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
sys.path.insert(0, os.path.join(QUI, '..', 'analisi'))
sys.path.insert(0, os.path.join(QUI, '..', 'esperimenti'))
import v0, v1, corpo2

CORPO_E288 = OrderedDict([('rip', 0.5), ('phi', 0.10), ('sigma_post', 0.04)])


def corpo(chiave, parametri=None):
    import e233_frequenti_esatte as e233
    import e236_due_fonti as e236
    import e251_lessico_sezione as e251
    import e268_prime_righe as e268
    k = e251._prepara()
    x = parametri or CORPO_E288
    seme = v0.numero(chiave, 'corpo') % 1000003
    if 'alfa' in x:                      # parametri completi della regolazione congiunta (e253, e289)
        import e253_regolazione_congiunta as e253
        prm = e253.prm_di(x)
        prm.update(beta=x.get('beta', 0.0), eps=x.get('eps', 1.0), vsim=x.get('vsim', 0.0), sigma=x.get('sigma_in', 0.0))
        inter = e253.interruttori() if x.get('inter') else None
        pp = e268.prime_per_pagina(k['c']) if x.get('rho') else None
    else:
        prm = dict(e251.CONF, gamma=0.0, rip=x.get('rip', 1.0), phi=x.get('phi', 0.0))
        inter, pp = None, None
    e233.SIGMA_POST, e233.PI_POST = x.get('sigma_post', 0.09), x.get('pi_post', 0.30)
    return e236.dopo(corpo2.genera_v2(k['c2'], prm, seme, inter=inter, prime_per_pag=pp), k['freq'], 100 + seme)


def valuta(righe_con, chiave, parametri=None):
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    k = e251._prepara()

    def misura(rr):
        pg = e251.pagella_grezza(k['c'], rr)
        return OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']),
                            ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                            ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    return OrderedDict([('senza messaggio', misura(corpo(chiave, parametri))), ('con il messaggio', misura(righe_con))])


def main():
    ap = argparse.ArgumentParser(description='Voynichizzatore v2')
    ap.add_argument('azione', choices=('codifica', 'decodifica', 'valuta'))
    ap.add_argument('file')
    ap.add_argument('--chiave', required=True)
    ap.add_argument('--uscita')
    ap.add_argument('--parametri')
    a = ap.parse_args()
    parametri = OrderedDict(json.load(open(a.parametri, encoding='utf-8'))) if a.parametri else None
    if a.azione == 'codifica':
        righe, info = v1.codifica(open(a.file, encoding='utf-8').read(), a.chiave, righe=corpo(a.chiave, parametri))
        v0.salva(righe, a.uscita or 'manoscritto.txt')
        print('scritto %s: %d righe; %s' % (a.uscita or 'manoscritto.txt', len(righe), info))
    elif a.azione == 'decodifica':
        try:
            testo = v1.decodifica(v0.carica(a.file), a.chiave)
        except Exception:
            raise SystemExit('niente da leggere: chiave sbagliata o manoscritto alterato')
        if a.uscita:
            open(a.uscita, 'w', encoding='utf-8', newline='\n').write(testo)
            print('testo scritto in %s (%d caratteri)' % (a.uscita, len(testo)))
        else:
            sys.stdout.reconfigure(encoding='utf-8', newline='\n')
            sys.stdout.write(testo + '\n')
    else:
        ris = valuta(v0.carica(a.file), a.chiave, parametri)
        for n, r in ris.items():
            print('%-18s pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f' % (n, r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266']), flush=True)
        json.dump(ris, open(os.path.splitext(a.file)[0] + '_valutazione.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
