# ia11 - rifarlo (la prova del nove)

Soglie nella preregistrazione `preregistrazioni/ia11.md`. AUC: media sui 10 libri v21 senza messaggio (b13-b22); intervalli al 95% col bootstrap sulle pagine (lo stesso ricampionamento per tutte le varianti); discesa = AUC di V0 meno AUC della variante.

## Validita
- riproduzione_ia01: {"V0a": 0.7512, "atteso": 0.751, "ok": true}
- V0_contro_V0a: {"differenza": -0.0008, "ok": true}
- A_controlli: true
- K_controlli: true
- K_vede_V0: true

## Lettura principale (V3 = eco + ordine)
- **non leggibile**
- dettagli: {"esito": "non leggibile", "quota_A": -0.2228, "quota_K": -0.1814, "A_ok": false, "K_ok": false, "K_leggibile": true, "paper_ok": false, "controllo_negativo_ok": true, "manipolazione_V3": false}

## Giudice A (sorpresa, rete GRU di ia01)

Controlli: {"ctrl:parole": 0.985119105970003, "ctrl:e192": 0.9567444368199196, "ctrl:righe": 0.5756347416919909}; negativo (media di 5 etichette) 0.5059; valido: True

| variante | AUC media (se) | IC 95% pagine | min-max | discesa da V0 (IC) | quota dell'eccesso tolta |
|---|---|---|---|---|---|
| V0a | 0.7512 (0.0070) | [0.7112, 0.7894] | 0.7212-0.7748 | - | - |
| V0 | 0.7504 (0.0046) | [0.7138, 0.7889] | 0.7272-0.7710 | - | - |
| V1 | 0.7739 (0.0039) | [0.7369, 0.8109] | 0.7537-0.7938 | -0.0235 ([-0.0289, -0.0174]) | -0.0938 |
| V2 | 0.7861 (0.0036) | [0.749, 0.8234] | 0.7620-0.7997 | -0.0357 ([-0.0446, -0.0271]) | -0.1426 |
| V3 | 0.8062 (0.0029) | [0.7686, 0.8442] | 0.7929-0.8198 | -0.0558 ([-0.0658, -0.0451]) | -0.2228 |
| V4 | 0.7952 (0.0031) | [0.7565, 0.8367] | 0.7780-0.8080 | -0.0448 ([-0.0623, -0.0248]) | -0.1791 |
| N1 | 0.8678 (0.0027) | [0.836, 0.898] | 0.8533-0.8845 | -0.1174 ([-0.1356, -0.0976]) | -0.4688 |
| VR | 0.5818 (0.0046) | [0.5716, 0.5963] | 0.5727-0.5874 | - | - |

## Giudice K (indipendente: n-grammi a caratteri con memoria di pagina)

Controlli: {"ctrl:parole": 0.9820556808156062, "ctrl:e192": 0.9351534163317321, "ctrl:righe": 0.571679247132634}; negativo (media di 5 etichette) 0.5085; valido: True

| variante | AUC media (se) | IC 95% pagine | min-max | discesa da V0 (IC) | quota dell'eccesso tolta |
|---|---|---|---|---|---|
| V0a | 0.7549 (0.0056) | [0.7206, 0.7918] | 0.7303-0.7826 | - | - |
| V0 | 0.7568 (0.0075) | [0.719, 0.7931] | 0.7129-0.7904 | - | - |
| V1 | 0.7865 (0.0075) | [0.7526, 0.8217] | 0.7476-0.8229 | -0.0297 ([-0.0379, -0.0227]) | -0.1157 |
| V2 | 0.7792 (0.0068) | [0.7439, 0.8146] | 0.7350-0.8102 | -0.0224 ([-0.029, -0.0165]) | -0.0872 |
| V3 | 0.8034 (0.0070) | [0.7693, 0.8361] | 0.7697-0.8402 | -0.0466 ([-0.0569, -0.038]) | -0.1814 |
| V4 | 0.8531 (0.0060) | [0.8242, 0.8816] | 0.8196-0.8843 | -0.0963 ([-0.111, -0.0813]) | -0.3749 |
| N1 | 0.8532 (0.0055) | [0.8248, 0.8825] | 0.8241-0.8768 | -0.0964 ([-0.1128, -0.0795]) | -0.3754 |
| VR | 0.5579 (0.0010) | [0.5507, 0.5698] | 0.5566-0.5598 | - | - |

## Giudici del paper (media sui libri; e231 e e266)

| variante | e231 | e266 | salita e231 | salita e266 | non peggiora (soglia +0.03) |
|---|---|---|---|---|---|
| V0 | 0.5785 | 0.6219 | - | - | - |
| V1 | 0.6078 | 0.6490 | 0.0293 | 0.0271 | True |
| V2 | 0.6262 | 0.6617 | 0.0477 | 0.0398 | False |
| V3 | 0.6573 | 0.6915 | 0.0788 | 0.0696 | False |
| V4 | 0.6977 | 0.7376 | 0.1192 | 0.1157 | False |
| N1 | 0.6952 | 0.7416 | 0.1167 | 0.1197 | False |
| VR | 0.5399 | 0.5560 | - | - | - |

## Verifica di manipolazione (le misure delle varianti contro quelle delle vere)

| testo | D (ia10, stesse famiglie) | D (altro seme) | costo di forma delle parole nuove (bit per glifo) | quota di parole nuove |
|---|---|---|---|---|
| vere | 0.1071 | 0.0946 | 3.4541 | 0.1526 |
| V0 | 0.0628 | 0.0566 | 3.6639 | 0.1450 |
| V1 | 0.0599 | 0.0548 | 3.6478 | 0.1439 |
| V2 | 0.0855 | 0.0609 | 3.6639 | 0.1450 |
| V3 | 0.0860 | 0.0586 | 3.6459 | 0.1437 |
| V4 | 0.0872 | 0.0597 | 3.5948 | 0.1187 |
| N1 | 0.0299 | 0.0268 | 3.6470 | 0.1434 |

| testo | copia netta (ia09, bit per parola) | quota locale | rho | contatto ultimo -> primo glifo (g di ia08, bit) |
|---|---|---|---|---|
| vere | 0.1060 | 0.2308 | 0.7010 | 0.1884 |
| V0 | 0.0524 | 0.0909 | 0.5846 | 0.1850 |
| V1 | 0.1144 | 0.0823 | 0.8257 | 0.1717 |
| V2 | 0.0511 | 0.0545 | 0.8126 | 0.1370 |
| V3 | 0.1121 | 0.0660 | 0.9324 | 0.1293 |
| V4 | 0.0999 | 0.0720 | 0.9189 | 0.1224 |
| N1 | 0.0424 | 0.0338 | 0.9615 | 0.0488 |

Letture di manipolazione: {"V1": {"eco_frazione_copia_netta": 1.158, "eco_frazione_quota_locale": -0.062, "riuscita": false}, "V2": {"ordine_frazione_D": 0.513, "ordine_frazione_D_altro_seme": 0.113, "contatto_differenza_da_V0": -0.048, "riuscita": false}, "V3": {"eco_frazione_copia_netta": 1.115, "eco_frazione_quota_locale": -0.178, "ordine_frazione_D": 0.524, "ordine_frazione_D_altro_seme": 0.052, "contatto_differenza_da_V0": -0.0557, "riuscita": false}, "V4": {"eco_frazione_copia_netta": 0.888, "eco_frazione_quota_locale": -0.135, "ordine_frazione_D": 0.549, "ordine_frazione_D_altro_seme": 0.08, "contatto_differenza_da_V0": -0.0626, "forma_frazione": 0.33, "quota_nuove_differenza_da_V3": -0.025, "riuscita": false}}

Eco per fascia (parole frequenti con parola uguale, rare con parola uguale, tutte con parola a una modifica, al netto del riferimento; fasce S1 S2 S3 R1 R2 R4 R8): {"vere": [0.0107, 0.0147, 0.0417, 0.0807, 0.1217, 0.1777, 0.2351, 0.0019, 0.0016, 0.0031, 0.0062, 0.0105, 0.0147, 0.0455, 0.0277, 0.0284, 0.0769, 0.1454, 0.1976, 0.2375, 0.1583], "V0": [0.0096, 0.0153, 0.0401, 0.0699, 0.0982, 0.1444, 0.2139, 0.0006, 0.0008, 0.003, 0.0051, 0.0086, 0.0136, 0.046, 0.0282, 0.0274, 0.0711, 0.1252, 0.1726, 0.2192, 0.1515], "V1": [0.0102, 0.0155, 0.0419, 0.0726, 0.1011, 0.1457, 0.2093, 0.0018, 0.0017, 0.0064, 0.01, 0.0138, 0.0164, 0.044, 0.0295, 0.0287, 0.0772, 0.1342, 0.181, 0.2233, 0.1507], "V2": [0.011, 0.0135, 0.0404, 0.0701, 0.098, 0.1445, 0.214, 0.0006, 0.0008, 0.003, 0.0052, 0.0086, 0.0136, 0.0459, 0.0267, 0.0259, 0.0743, 0.1252, 0.1726, 0.2191, 0.1515], "V3": [0.0112, 0.0133, 0.0416, 0.0727, 0.1004, 0.1434, 0.2084, 0.0019, 0.0018, 0.0065, 0.0101, 0.0137, 0.0166, 0.0451, 0.0283, 0.0277, 0.0807, 0.1334, 0.1801, 0.2231, 0.1513], "V4": [0.0111, 0.0131, 0.0413, 0.0722, 0.0997, 0.1423, 0.2045, 0.0018, 0.0017, 0.0064, 0.0098, 0.0137, 0.0172, 0.0477, 0.0285, 0.028, 0.0822, 0.1361, 0.1835, 0.2275, 0.1493], "N1": [0.0096, 0.0119, 0.0393, 0.0647, 0.0923, 0.1362, 0.2, 0.0006, 0.0007, 0.0029, 0.0048, 0.0078, 0.0122, 0.042, 0.0244, 0.0242, 0.071, 0.1199, 0.1668, 0.2127, 0.1378]}

Taratura per piega (parametri): {"0": {"eco": {"p": 0.0508, "tau": 25.0, "q": 0.7, "gamma": 0.0}, "ordine_V2": {"s": 0.5132, "lam": 0.5, "mu": 1.0}, "ordine_V3": {"s": 0.5405, "lam": 0.5, "mu": 1.0}, "forma": {"r": 0.2242}}, "1": {"eco": {"p": 0.0666, "tau": 25.0, "q": 0.7, "gamma": 0.0}, "ordine_V2": {"s": 0.3199, "lam": 0.5, "mu": 1.0}, "ordine_V3": {"s": 0.3239, "lam": 0.5, "mu": 1.0}, "forma": {"r": 0.1883}}, "2": {"eco": {"p": 0.0542, "tau": 25.0, "q": 0.7, "gamma": 0.0}, "ordine_V2": {"s": 0.3565, "lam": 0.5, "mu": 1.0}, "ordine_V3": {"s": 0.3931, "lam": 0.5, "mu": 1.0}, "forma": {"r": 0.2026}}, "3": {"eco": {"p": 0.0666, "tau": 25.0, "q": 0.7, "gamma": 0.0}, "ordine_V2": {"s": 0.5927, "lam": 0.5, "mu": 1.0}, "ordine_V3": {"s": 0.6014, "lam": 0.5, "mu": 1.0}, "forma": {"r": 0.2155}}, "4": {"eco": {"p": 0.0525, "tau": 25.0, "q": 0.7, "gamma": 0.0}, "ordine_V2": {"s": 0.6002, "lam": 0.5, "mu": 1.0}, "ordine_V3": {"s": 0.6844, "lam": 0.5, "mu": 1.0}, "forma": {"r": 0.2177}}}

- L3_forma_A: {"esito": "zona grigia", "discesa": 0.011, "ic": [-0.0009, 0.0232], "manipolazione_V4": false}

- L3_forma_K: {"discesa": -0.0497, "ic": [-0.0584, -0.0402]}

- L6_vere_ritoccate: {"vere_ritoccate_A": {"AUC": 0.5818, "ok": true}, "vere_ritoccate_K": {"AUC": 0.5579, "ok": true}}

Riproduzione dei modelli del testo di ia01: {"disponibile": true, "modelli": 10, "max_diff_perdita_validazione": 0.0, "max_diff_passi": 0, "profili_confrontati": 404, "profili_diff_massima": 0.0, "profili_diff_media": 0.0}
