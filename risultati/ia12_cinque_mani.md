# ia12 — le cinque mani

Soglie e regole nella preregistrazione `preregistrazioni/ia12.md`. Conti (ia09, ia10): per ogni coppia di mani 5 sotto-testi con le stesse parole per mano, modelli addestrati sul solo sotto-testo; rete (ia03): una rete per gruppo. Solo numeri e aggregati.

## Gruppi (mano, lingua)

| gruppo | pagine | parole | segni | leggibile (conti) | leggibile (rete) |
|---|---|---|---|---|---|
| 1A | 112 | 10481 | 53659 | si | no |
| 2B | 46 | 10806 | 59049 | si | si |
| 3? | 1 | 45 | 228 | no | no |
| 3A | 2 | 750 | 4151 | no | no |
| 3B | 28 | 10908 | 62814 | si | si |
| 4? | 5 | 367 | 1913 | no | no |
| 5B | 7 | 873 | 4955 | no | no |
| ?B | 1 | 460 | 2628 | no | no |

Pagine con piu' di una mano: 0. Parole per mano in ogni sotto-testo Q: 8300; sotto-testi 5; permutazioni 2000.

## Controlli

- negativo_conti: NON superato
- negativo_rete: superato
- positivo_netto: superato
- positivo_rho: superato
- positivo_lambda: NON superato
- positivo_g10: superato
- positivo_D10: superato
- positivo_k90: superato
- positivo_GR: superato
- **validita per misura**: netto NO, rho NO, lambda NO, g10 NO, D10 NO, k90 si, GR si

## Voynich, 1A_2B (conti, descrittivo: mano e lingua insieme)

| misura | 1A | 2B | differenza |
|---|---|---|---|
| netto | +0.084 | +0.151 | -0.067 |
| rho | +0.798 | +0.769 | +0.030 |
| lambda | +0.250 | +0.097 | +0.153 |
| g10 | +0.011 | +0.016 | -0.005 |
| D10 | +0.021 | +0.086 | -0.065 |
| A_gram | +0.021 | +0.040 | -0.018 |
| A_cn | +0.085 | +0.133 | -0.048 |
| G0 | -0.017 | -0.006 | -0.011 |

## Voynich, 1A_3B (conti, descrittivo: mano e lingua insieme)

| misura | 1A | 3B | differenza |
|---|---|---|---|
| netto | +0.090 | +0.149 | -0.059 |
| rho | +0.898 | +0.878 | +0.020 |
| lambda | +0.270 | +0.210 | +0.061 |
| g10 | +0.032 | +0.031 | +0.001 |
| D10 | +0.024 | +0.055 | -0.031 |
| A_gram | +0.010 | +0.019 | -0.008 |
| A_cn | +0.091 | +0.139 | -0.049 |
| G0 | -0.025 | -0.014 | -0.011 |

## Voynich, 2B_3B (conti, 5 sotto-testi)

| misura | 2B | 3B | differenza (x meno y) | p dentro la lingua | p dentro lingua e sezione | minimo | esito |
|---|---|---|---|---|---|---|---|
| netto | +0.089 | +0.056 | +0.034 | 0.0020 | 0.1249 | 0.02 | non leggibile (un controllo non e' superato) |
| rho | +0.701 | +0.685 | +0.016 | 0.5892 | 0.2504 | 0.20 | non leggibile (un controllo non e' superato) |
| lambda | +0.098 | +0.162 | -0.065 | 0.5567 | 0.9020 | 0.20 | non leggibile (un controllo non e' superato) |
| g10 | +0.074 | +0.045 | +0.028 | 0.0010 | 0.3283 | 0.02 | non leggibile (un controllo non e' superato) |
| D10 | +0.148 | +0.123 | +0.025 | 0.0160 | 0.5122 | 0.05 | non leggibile (un controllo non e' superato) |

## Voynich, A_B (conti, descrittivo: mano e lingua insieme)

| misura | tutte A | tutte B | differenza |
|---|---|---|---|
| netto | +0.099 | +0.167 | -0.069 |
| rho | +0.880 | +0.878 | +0.001 |
| lambda | +0.419 | +0.156 | +0.263 |
| g10 | +0.036 | +0.020 | +0.016 |
| D10 | +0.029 | +0.056 | -0.027 |
| A_gram | +0.014 | +0.021 | -0.008 |
| A_cn | +0.099 | +0.155 | -0.056 |
| G0 | -0.017 | -0.007 | -0.010 |

## Voynich, 2B_3B (rete)

| misura | x | y | differenza | errore standard | mani finte (max) | esito |
|---|---|---|---|---|---|---|
| k90 | +2.000 | +2.000 | +0.000 | +0.000 | +0.000 | descrittiva |
| k90_interpolato | +1.767 | +1.815 | -0.048 | +0.035 | +0.212 | nessuna differenza misurabile |
| GL | +0.028 | +0.026 | +0.002 | +0.005 | +0.032 | nessuna differenza misurabile |
| GR_corte | +0.015 | +0.010 | +0.004 | +0.003 | +0.012 | nessuna differenza misurabile |
| GR | +0.014 | +0.010 | +0.005 | +0.003 | +0.012 | descrittiva |

## Rete, ogni gruppo (media sui semi)

| gruppo | semi | segni | k90 | k90_interpolato | GL | GR_corte | GR |
|---|---|---|---|---|---|---|---|
| 2B | 10 | 59049 | +2.000 | +1.767 | +0.028 | +0.015 | +0.014 |
| 3B | 10 | 62814 | +2.000 | +1.815 | +0.026 | +0.010 | +0.010 |
