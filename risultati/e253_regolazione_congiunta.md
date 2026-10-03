# e253 — Passo 4 del piano 18/18: regolazione congiunta con tutti i meccanismi

128 configurazioni casuali più l'e241 e 32 di affinamento sul seme 1 (obiettivo AUC dell'e266, pagella non inferiore all'e241 e riga); verifica sui semi 7, 8, 9. Preregistrazione: `preregistrazioni/e253.md`.

e241 sul seme 1: pagella 14, AUC e266 0.956. Scelta **a031**: pagella 14, AUC e266 0.916, e231 0.834.

Parametri scelti: alfa 1.332, kappa 1.105, chi 0.130, nu 0.553, lam 0.904, eta 1.378, gamma 0.040, delta 0.159, psi 0.060, sigma_post 0.057, pi_post 0.303, phi 0.084, theta 0.392, rho 0.059, rip 0.597, k 8, k_tema 3, mazzo False, inter False.

| seme | configurazione | pagella | riga | mancano | AUC e231 | AUC e266 |
|---|---|---|---|---|---|---|
| 7 | e241 | 15/18 | sì | ripetizione, profilo pagina, verticale | 0.887 | 0.966 |
| 7 | a031 | 16/18 | no | omogeneità, curva piatta | 0.870 | 0.934 |
| 8 | e241 | 15/18 | no | spazio, ripetizione, verticale | 0.854 | 0.953 |
| 8 | a031 | 16/18 | sì | curva piatta, verticale | 0.876 | 0.939 |
| 9 | e241 | 15/18 | sì | spazio, ripetizione, verticale | 0.879 | 0.965 |
| 9 | a031 | 16/18 | sì | omogeneità, curva piatta | 0.887 | 0.957 |

Medie: e241 pagella 45, riga in 2 semi, AUC 0.873 / 0.961; scelta pagella 48, riga in 2 semi, AUC 0.878 / 0.943.

Correlazione fra parametro e AUC dell'e266 sul seme 1 (negativa = alzarlo aiuta): alfa -0.36, kappa +0.02, chi +0.16, nu -0.04, lam +0.27, eta -0.31, gamma +0.60, delta -0.11, psi -0.39, sigma_post +0.24, pi_post +0.09, phi +0.25, theta -0.59, rho +0.41, rip -0.11, k +0.10, k_tema +0.31, mazzo +0.20, inter +0.44.

Esito: **non migliore**.
