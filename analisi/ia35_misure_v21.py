"""Misure tenute fuori di IA35 per i 10 libri v21 gia' valutati nella corsa di IA35 (nessun calcolo nuovo sul Voynich: solo aggregazione dei lavori M| e NM| gia' fatti)."""
import os, sys, json
os.environ.pop('SOLO_CONTROLLI', None)
REPO = sys.argv[1]
sys.path.insert(0, os.path.join(REPO, 'esperimenti'))
os.chdir(REPO)
import ia35_sezione as X
v21 = X.v21_disponibili()
X.attiva_main('vero', [])
X.attiva_main('vero', v21)
A = X.analisi_esame('vero', {}, v21, v21)
rif, prof, nm_rif, nm = A['rif'], A['prof'], A['nm_rif'], A['nm']
out = {}
for m in X.SL.FUORI_MISURE35:
    if m in X.SM.NOMI_NM8:
        vero, s_ = (nm_rif['vero'] or {}).get(m), (nm_rif['sigma'] or {}).get(m)
        vals = [(nm.get('NM|%s' % l) or nm.get(l) or {}).get(m) for l in v21]
    else:
        vero, s_ = rif['vero'].get(m), (rif['scala'].get(m) or 0) * X.SIGMA_DA_SCALA
        vals = [prof[l].get(m) for l in v21]
    val = X.media(vals)
    out[m] = None if (val is None or not s_ or vero is None) else round((val - vero) / s_, 2)
print(len(v21), 'libri v21')
print(json.dumps(out, ensure_ascii=False))
print('entro 2 sigma:', sum(1 for z in out.values() if z is not None and abs(z) <= 2), 'su', sum(1 for z in out.values() if z is not None))
