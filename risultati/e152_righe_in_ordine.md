# e152 — Un generatore che scrive ogni riga in ordine

Inizio con regola, tema di riga di k parole della pagina, varianti (Poisson μ), scelta per giuntura (λ), abitudini AR(1) (ρ 0,6, σ 0,8). Medie su tre semi. Preregistrazione: `preregistrazioni/e152.md`. Voynich: S(1) 0,52, R 0,006, A 1,044, 5 scelte per riga, r 0,207.

| combinazione | pagella | riga e pagina | R | S(1) | A | scelte per riga | r consecutive | copia 1ª / 2ª | e94 | riga riprodotta | completo |
|---|---|---|---|---|---|---|---|---|---|---|---|
| k 2, mu 0.5 | 9/18 | 6/12 | -0.01 | 0.66 | 1.028 | 5.0 | 0.169 | 0.81 / 1.20 | 1.09 | sì | no |
| k 2, mu 1.0 | 7/18 | 5/12 | 0.03 | 0.64 | 1.019 | 5.0 | 0.172 | 0.88 / 1.51 | 1.07 | sì | no |
| k 4, mu 0.5 | 8/18 | 6/12 | -0.02 | 0.61 | 1.021 | 5.0 | 0.170 | 0.92 / 1.31 | 1.04 | sì | no |
| k 4, mu 1.0 | 6/18 | 6/12 | 0.01 | 0.66 | 1.009 | 5.0 | 0.173 | 1.03 / 1.38 | 1.05 | sì | no |
| ablazione: senza giunture (k 2, mu 0.5) | 10/18 | 5/12 | -0.03 | 0.65 | 0.996 | 5.0 | 0.170 | 0.86 / 1.40 | 1.05 | no | no |

| combinazione | h2 | spazio | uniche | tipi | ripetizione | omogeneità | gradiente | legame | unioni | curva piatta | deriva | profilo pagina | lunghezze vicine | Zipf | forma parole | verticale | formule | bordo di riga |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| k 2, mu 0.5 | · 2.43 | ✓ 0.597 | ✓ 0.612 | ✓ 0.241 | ✓ 1.11 | · 0.197 | ·  | · 0.0432 | ·  | ✓  | ✓ 0.0622 | ✓ 1.02 | ✓ 0.452 | · -0.905 | ✓ 0.251 | · 1 | · 169 | ·  |
| k 2, mu 1.0 | · 2.58 | · 0.534 | ✓ 0.666 | · 0.307 | ✓ 1.13 | · 0.185 | ·  | · 0.0714 | ✓  | ✓  | ✓ 0.0551 | · 0.796 | ✓ 0.427 | · -0.851 | ✓ 0.676 | · 1 | · 168 | ·  |
| k 4, mu 0.5 | · 2.44 | ✓ 0.595 | ✓ 0.622 | · 0.251 | ✓ 1.11 | · 0.108 | ·  | · 0.0719 | ·  | ✓  | ✓ 0.0687 | ✓ 1.02 | ✓ 0.267 | · -0.915 | ✓ 0.253 | · 1 | · 46.2 | ·  |
| k 4, mu 1.0 | · 2.58 | · 0.534 | ✓ 0.675 | · 0.314 | ✓ 1.1 | · 0.101 | ·  | · 0.099 | ·  | ·  | ✓ 0.0598 | ✓ 0.873 | ✓ 0.263 | · -0.863 | ✓ 0.686 | · 0.998 | · 36.6 | ·  |
| ablazione: senza giunture (k 2, mu 0.5) | · 2.44 | ✓ 0.597 | ✓ 0.602 | ✓ 0.237 | ✓ 1.12 | · 0.193 | ·  | · 0.00111 | ✓  | ✓  | ✓ 0.0731 | ✓ 0.981 | ✓ 0.431 | · -0.911 | ✓ 0.246 | · 1 | · 141 | ·  |

Riga riprodotta: **k 2, mu 0.5, k 2, mu 1.0, k 4, mu 0.5, k 4, mu 1.0**. Completi: **nessuno**.
