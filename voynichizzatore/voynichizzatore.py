# -*- coding: utf-8 -*-
"""Voynichizzatore, strumento unico (3/10/2026): un testo normale diventa un manoscritto "alla Voynich" con il testo
nascosto (fino alla v9 nelle scelte di grafia, dalla v10 nella scelta delle parole di ogni pagina); con la chiave il testo torna esatto. Le versioni (corpo e modello delle scelte) stanno
nel registro versioni.py; senza --versione si usa l'ultima.

    python voynichizzatore/voynichizzatore.py codifica testo.txt --chiave PAROLA --uscita manoscritto.txt [--versione v5]
    python voynichizzatore/voynichizzatore.py decodifica manoscritto.txt --chiave PAROLA [--uscita testo.txt] [--versione v5]
    python voynichizzatore/voynichizzatore.py valuta manoscritto.txt --chiave PAROLA [--versione v5]
    python voynichizzatore/voynichizzatore.py versioni
"""
import argparse, json, os, sys
from collections import OrderedDict

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import v0, versioni


def corpo(chiave, versione):
    return versioni.senza_messaggio(versione, chiave)


def valuta(righe_con, chiave, versione):
    import e231_discriminatore as e231
    import e232_meno_pagina as e232
    import e251_lessico_sezione as e251
    import e266_discriminatore_forte as e266
    import e293_banco as e293
    k = e251._prepara()

    def misura(rr):
        pg = e251.pagella_grezza(k['c'], rr)
        return OrderedDict([('pagella', pg['pagella']), ('riga', pg['riga']), ('mancano', pg['mancano']), ('estesa', e293.pagella_estesa(rr)),
                            ('AUC_e231', e231.confronto(k['vpag'], e232.pagine_di(rr), k['rif'])['AUC']),
                            ('AUC_e266', e266.confronto(k['vt266'], e266.tabella(e251.righe_ini(rr), k['rif266']))['AUC'])])
    return OrderedDict([('senza messaggio', misura(corpo(chiave, versione))), ('con il messaggio', misura(righe_con))])


def main():
    ultima = list(versioni.VERSIONI)[-1]
    ap = argparse.ArgumentParser(description='Voynichizzatore')
    ap.add_argument('azione', choices=('codifica', 'decodifica', 'valuta', 'versioni', 'pdf'))
    ap.add_argument('file', nargs='?')
    ap.add_argument('--chiave')
    ap.add_argument('--uscita')
    ap.add_argument('--versione', default=ultima, choices=list(versioni.VERSIONI))
    a = ap.parse_args()
    if a.azione == 'versioni':
        for v, d in versioni.VERSIONI.items():
            print('%s: corpo %s, %s' % (v, dict(d['corpo']), 'messaggio nel sacco' if d.get('canale') == 'sacco' else 'modello delle scelte %s' % d['modello']))
        return
    if a.azione == 'pdf':        # dal manoscritto in EVA alle pagine scritte col nostro carattere
        import pagine
        if not a.file:
            raise SystemExit('serve il file del manoscritto')
        uscita = a.uscita or os.path.splitext(a.file)[0] + '.pdf'
        print('scritto %s: %d pagine' % (uscita, pagine.pdf(a.file, uscita)))
        return
    if not a.file or not a.chiave:
        raise SystemExit('servono il file e --chiave')
    if a.azione == 'codifica':
        righe, info = versioni.codifica(a.versione, open(a.file, encoding='utf-8').read().replace('\r\n', '\n'), a.chiave)
        v0.salva(righe, a.uscita or 'manoscritto.txt')
        print('versione %s; scritto %s: %d righe; %s' % (a.versione, a.uscita or 'manoscritto.txt', len(righe), info))
    elif a.azione == 'decodifica':
        try:
            testo = versioni.decodifica(a.versione, v0.carica(a.file), a.chiave)
        except Exception:
            raise SystemExit('niente da leggere: chiave o versione sbagliata, o manoscritto alterato')
        if a.uscita:
            open(a.uscita, 'w', encoding='utf-8', newline='\n').write(testo)
            print('testo scritto in %s (%d caratteri)' % (a.uscita, len(testo)))
        else:
            sys.stdout.reconfigure(encoding='utf-8', newline='\n')
            sys.stdout.write(testo + '\n')
    else:
        ris = valuta(v0.carica(a.file), a.chiave, a.versione)
        for n, r in ris.items():
            print('%-18s pagella %d/18 riga %s mancano %s | AUC e231 %.3f e266 %.3f | estesa %s' % (
                n, r['pagella'], r['riga'], r['mancano'], r['AUC_e231'], r['AUC_e266'],
                {m: round(x, 3) if isinstance(x, float) else x for m, x in r['estesa'].items()}), flush=True)
        json.dump(ris, open(os.path.splitext(a.file)[0] + '_valutazione.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)


if __name__ == '__main__':
    main()
