# e378 — La lingua B è la lingua A con un'altra chiave di sostituzione?

Preregistrazione: `preregistrazioni/e378.md`. Erbario: B 3462 parole; A diviso in due parti di pari dimensione, 10 volte.

| divisione | O(A1, A2) | O(A1, B) | O con la chiave migliore | R | controllo: O(A1, A2π) | controllo: O con la chiave | R controllo |
|---|---|---|---|---|---|---|---|
| 0 | 0.584 | 0.306 | 0.308 | 0.01 | 0.009 | 0.584 | 1.00 |
| 1 | 0.588 | 0.314 | 0.316 | 0.01 | 0.004 | 0.588 | 1.00 |
| 2 | 0.587 | 0.312 | 0.313 | 0.00 | 0.011 | 0.587 | 1.00 |
| 3 | 0.582 | 0.308 | 0.309 | 0.01 | 0.026 | 0.582 | 1.00 |
| 4 | 0.582 | 0.319 | 0.321 | 0.01 | 0.011 | 0.582 | 1.00 |
| 5 | 0.594 | 0.312 | 0.314 | 0.01 | 0.007 | 0.594 | 1.00 |
| 6 | 0.584 | 0.304 | 0.308 | 0.01 | 0.008 | 0.584 | 1.00 |
| 7 | 0.583 | 0.321 | 0.323 | 0.01 | 0.007 | 0.583 | 1.00 |
| 8 | 0.590 | 0.303 | 0.304 | 0.01 | 0.010 | 0.590 | 1.00 |
| 9 | 0.591 | 0.311 | 0.312 | 0.00 | 0.003 | 0.591 | 1.00 |

Medie: O stessa lingua 0.586, O fra A e B 0.311, O con la chiave 0.313; R 0.01; R controllo 1.00.
Lunghezza media delle parole (segni): A 4.04, B 4.37.
Scambi più frequenti nella chiave migliore (su 10 divisioni): p→f (10), f→p (6), cph→x (5), c→cph (4), cph→p (4), cfh→cph (4), cfh→x (3), c→cfh (3), x→c (3), x→cfh (3), b→c (2), j→v (2), u→b (2), b→cfh (2), cfh→c (2).

Esito: **B non è una sostituzione di A**.
