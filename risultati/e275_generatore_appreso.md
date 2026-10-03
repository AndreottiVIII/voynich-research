# e275 — Un generatore "appreso" dal modello a mistura dell'e259b

Pesi (base, cache, varianti, lettere, lettere della pagina): 0.05, 0.01, 0.06, 0.08, 0.79. Preregistrazione: `preregistrazioni/e275.md`.

| variante | seme | pagella | riga | mancano | AUC e231 | AUC e266 | R | V | N | R parole rare |
|---|---|---|---|---|---|---|---|---|---|---|
| (a) campionamento puro | 7 | 8/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, verticale, formule, bordo di riga | 0.999 | 1.000 | 33.4% | 36.2% | 15.4% | 29.4 |
| (a) campionamento puro | 8 | 8/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, verticale, formule, bordo di riga | 0.997 | 1.000 | 33.4% | 35.9% | 15.6% | 24.6 |
| (a) campionamento puro | 9 | 9/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, formule, bordo di riga | 0.996 | 1.000 | 33.7% | 35.9% | 15.5% | 28.7 |
| (b) con scelte di riga e fine riga | 7 | 8/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, verticale, formule, bordo di riga | 0.994 | 1.000 | 30.1% | 37.1% | 16.5% | 19.1 |
| (b) con scelte di riga e fine riga | 8 | 9/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, formule, bordo di riga | 0.992 | 0.998 | 30.2% | 37.0% | 16.8% | 17.9 |
| (b) con scelte di riga e fine riga | 9 | 8/18 | no | omogeneità, gradiente, legame, unioni, deriva, profilo pagina, lunghezze vicine, verticale, formule, bordo di riga | 0.988 | 0.998 | 30.4% | 37.0% | 16.2% | 21.3 |

Medie: (a) campionamento puro: pagella 8.3, AUC e231 0.997, e266 1.000; (b) con scelte di riga e fine riga: pagella 8.3, AUC e231 0.991, e266 0.998.

Esempio (b, seme 7): qotedy cheo ky daiin qokedaiin tchy oteed kaiin chey qotedaiin / shaiin otsheedy qotaiin char ar otcheor cho qotaiilcheeo shy shaiin raiin / qokedy cthdy oteeo otool qotodaiin oteedy sheo sheedaiiin chy

Esito: **non promettente**.
