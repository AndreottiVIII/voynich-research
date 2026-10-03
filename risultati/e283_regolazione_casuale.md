# e283 — Regolazione congiunta preliminare: ricerca casuale sui parametri dell'e241

96 configurazioni casuali più l'e241 e 24 di affinamento sul seme 1 (obiettivo AUC dell'e266, pagella non oltre 1 sotto l'e241); verifica sui semi 7, 8, 9. Preregistrazione: `preregistrazioni/e283.md`.

e241 sul seme 1: pagella 14, riga sì, AUC e266 0.956, e231 0.882. Scelta: **a017**, AUC e266 0.910, e231 0.840, pagella 15.

Parametri scelti: alfa 1.232, kappa 1.808, chi 0.002, nu 0.354, lam 1.377, eta 0.186, gamma 0.000, delta 0.336, psi 0.031, phi 0.000, sigma_post 0.041, pi_post 0.341, k 8.

| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| 7 | e241 | 15/18 | sì | ripetizione, profilo pagina, verticale | 0.887 | 0.966 |
| 7 | a017 | 13/18 | sì | omogeneità, deriva, verticale, formule, bordo di riga | 0.868 | 0.938 |
| 8 | e241 | 15/18 | no | spazio, ripetizione, verticale | 0.854 | 0.953 |
| 8 | a017 | 14/18 | sì | omogeneità, verticale, formule, bordo di riga | 0.891 | 0.935 |
| 9 | e241 | 15/18 | sì | spazio, ripetizione, verticale | 0.879 | 0.965 |
| 9 | a017 | 13/18 | sì | omogeneità, deriva, verticale, formule, bordo di riga | 0.910 | 0.969 |

Medie: e241 pagella 45 (somma), riga in 2 semi, AUC 0.873 / 0.961; scelta pagella 40, riga in 3 semi, AUC 0.890 / 0.948.

Correlazione fra parametro e AUC dell'e266 sul seme 1 (negativa = alzarlo aiuta): alfa -0.24, kappa -0.29, chi +0.50, nu +0.51, lam -0.16, eta +0.36, gamma +0.72, delta -0.41, psi +0.01, phi +0.46, sigma_post +0.30, pi_post -0.22, k +0.11.

Le 10 migliori sul seme 1:

| config. | pagella | riga | AUC e266 | AUC e231 |
|---|---|---|---|---|
| a017 | 15 | sì | 0.910 | 0.840 |
| a002 | 11 | sì | 0.913 | 0.868 |
| a021 | 11 | sì | 0.919 | 0.841 |
| a022 | 12 | sì | 0.929 | 0.828 |
| a008 | 13 | sì | 0.933 | 0.870 |
| a016 | 14 | no | 0.934 | 0.851 |
| c051 | 14 | sì | 0.936 | 0.874 |
| a013 | 13 | sì | 0.940 | 0.877 |
| a010 | 14 | no | 0.943 | 0.879 |
| a014 | 13 | sì | 0.946 | 0.891 |

Esito: **non migliore**.
