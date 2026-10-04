# e3c55 — La finestra secondo quanto si somigliano le due parole

Preregistrazione: `preregistrazioni/e3c55.md`. K corretto con le distanze 1–3 nella riga insieme; distanza = Levenshtein fra le parole coperte.

| testo | distanza fra le parole | coppie | K osservato | K nullo | K corretto (IC 95%) | K corretto a 1 / 2 / 3 parole |
|---|---|---|---|---|---|---|
| Voynich ZL | 2 | 5231 | +0.118 | -0.011 | +0.129 (+0.091 – +0.166) | +0.139 / +0.106 / +0.145 |
| Voynich ZL | 3 | 6382 | +0.111 | -0.008 | +0.119 (+0.089 – +0.148) | +0.184 / +0.097 / +0.050 |
| Voynich ZL | 4+ | 9753 | +0.077 | -0.014 | +0.091 (+0.064 – +0.116) | +0.100 / +0.093 / +0.077 |
| Voynich ZL | **differenza 2 meno 4+** | | | | +0.038 (-0.005 – +0.083) | uguale per parole simili e diverse |
| Voynich IT | 2 | 5319 | +0.122 | -0.008 | +0.130 (+0.093 – +0.170) | +0.156 / +0.091 / +0.145 |
| Voynich IT | 3 | 6491 | +0.105 | -0.007 | +0.112 (+0.084 – +0.140) | +0.158 / +0.072 / +0.093 |
| Voynich IT | 4+ | 9927 | +0.084 | -0.013 | +0.097 (+0.071 – +0.121) | +0.117 / +0.089 / +0.077 |
| Voynich IT | **differenza 2 meno 4+** | | | | +0.033 (-0.013 – +0.080) | uguale per parole simili e diverse |
| Timm e Schinner (riferimento) | 2 | 3413 | +0.061 | -0.024 | +0.084 (+0.034 – +0.136) | +0.088 / +0.061 / +0.110 |
| Timm e Schinner (riferimento) | 3 | 3959 | +0.048 | -0.021 | +0.069 (+0.022 – +0.113) | +0.151 / +0.006 / +0.034 |
| Timm e Schinner (riferimento) | 4+ | 5702 | -0.014 | -0.035 | +0.021 (-0.019 – +0.061) | +0.012 / +0.003 / +0.058 |
| Timm e Schinner (riferimento) | **differenza 2 meno 4+** | | | | +0.063 (+0.002 – +0.126) | legato alla somiglianza |

Esito: **accordo uguale per parole simili e diverse (stato)**.
