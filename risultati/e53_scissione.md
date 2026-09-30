# e53 — Parole scritte in due pezzi e firma di fine parola

Modello dell'e51 (q 0,10, λ 0,75, K 0). d = probabilità di scrivere una parola in due pezzi a una giuntura morbida; "finali" = sostituzioni di fine parola del generatore. Medie su tre semi. Validità (finali accese = e51): sì. Fuori campione: V1, V4, V6 (autocorrelazione delle lunghezze ≥ 0,08), V7 (Zipf ±0,10); V3 e V5 sono bersagli. Preregistrazione: `preregistrazioni/e53.md`.

| testo | h2 | ripetizione | somigl. riga | 6 righe | legame | uniche | unioni/caso | R | quota pagina | autocorr. lunghezze | Zipf | compatibile | validazione |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | 2.24 | 1.01 | 3.8% | 3.4% | 0.188 | 0.68 | 1.96 | 1.02 | 0.061 | 0.150 | -1.04 | | |
| finali accese, d 0.00 | 2.38 | 0.76 | 3.4% | 3.2% | 0.190 | 0.64 | 1.41 | 0.74 | 0.086 | 0.040 | -0.91 | sì | V1, V4 |
| finali accese, d 0.03 | 2.39 | 0.77 | 3.3% | 3.1% | 0.221 | 0.65 | 1.47 | 0.74 | 0.085 | 0.051 | -0.91 | sì | V1, V4 |
| finali accese, d 0.06 | 2.40 | 0.80 | 3.1% | 3.0% | 0.256 | 0.64 | 1.53 | 0.74 | 0.084 | 0.058 | -0.92 | no | V1, V4, V5 (bersaglio) |
| finali accese, d 0.10 | 2.41 | 0.81 | 2.9% | 2.9% | 0.305 | 0.64 | 1.59 | 0.75 | 0.083 | 0.065 | -0.93 | no | V1, V4, V5 (bersaglio) |
| finali spente, d 0.00 | 2.32 | 0.70 | 4.6% | 4.3% | 0.217 | 0.63 | 1.51 | 0.72 | 0.115 | 0.062 | -0.90 | no | V1, V4, V5 (bersaglio) |
| finali spente, d 0.03 | 2.33 | 0.73 | 4.4% | 4.2% | 0.263 | 0.63 | 1.64 | 0.73 | 0.114 | 0.076 | -0.90 | sì | V1, V4, V5 (bersaglio) |
| finali spente, d 0.06 | 2.34 | 0.75 | 4.2% | 4.0% | 0.302 | 0.63 | 1.70 | 0.73 | 0.112 | 0.084 | -0.91 | sì | V1, V4, V6, V5 (bersaglio) |
| finali spente, d 0.10 | 2.35 | 0.77 | 4.0% | 4.0% | 0.356 | 0.63 | 1.83 | 0.74 | 0.110 | 0.094 | -0.91 | sì | V1, V4, V6, V5 (bersaglio) |
