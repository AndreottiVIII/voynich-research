# e3a69 — Una catena di segni addestrata su una lingua produce le proprietà del Voynich?

Preregistrazione: `preregistrazioni/e3a69.md`. Catena di ordine 2 su segni, spazio e fine riga.

| misura | lingue vere: mediana (90° perc.) | lingue riscritte dalla catena: mediana | Voynich vero | Voynich riscritto | gibberish vero | gibberish riscritto |
|---|---|---|---|---|---|---|
| rho frequenza-forma (e3a55) | 0.110 (0.202) | 0.294 | 0.596 | 0.613 | 0.087 | 0.432 |
| riempimento (e3a61) | 0.043 (0.086) | 0.155 | 0.435 | 0.441 | 0.093 | 0.152 |
| F1 degli spazi (e3a58) | 0.639 (0.718) | 0.667 | 0.855 | 0.866 | 0.281 | 0.266 |
| tagli sbagliati che sono parole (e3a67) | 0.067 (0.122) | 0.183 | 0.493 | 0.469 | 0.065 | 0.092 |

| testo sensato | rho frequenza-forma vero / catena | riempimento vero / catena | F1 degli spazi vero / catena | tagli sbagliati che sono parole vero / catena |
|---|---|---|---|---|
| Conlangs - Esperanto - Literary - NT | 0.130 / 0.236 | 0.042 / 0.174 | 0.674 / 0.694 | 0.073 / 0.240 |
| Conlangs - Esperanto - Technical - Voynich Wiki | -0.062 / 0.231 | 0.011 / 0.137 | 0.616 / 0.648 | 0.030 / 0.138 |
| Conlangs - Interlingua - Literary - NT | 0.110 / 0.332 | 0.030 / 0.153 | 0.639 / 0.667 | 0.087 / 0.211 |
| Conlangs - Interlingua - Technical - EU Wiki | 0.026 / 0.263 | 0.029 / 0.128 | 0.606 / 0.623 | 0.063 / 0.155 |
| Conlangs - Klingon - Literary - NT - Mark | 0.155 / 0.414 | 0.074 / 0.141 | 0.703 / 0.723 | 0.251 / 0.352 |
| Conlangs - Klingon - Technical - Proxima Centauri B Wikia | 0.147 / -0.101 | 0.065 / 0.138 | 0.525 / 0.673 | 0.135 / 0.215 |
| Conlangs - LOLCat - Literary - NT - Matthew | 0.185 / 0.325 | 0.076 / 0.166 | 0.610 / 0.650 | 0.125 / 0.233 |
| Conlangs - Lojban - Literary - Alice in Wonderland | -0.060 / 0.220 | 0.054 / 0.155 | 0.827 / 0.835 | 0.012 / 0.170 |
| Conlangs - Lojban - Technical - Science News | 0.023 / 0.184 | 0.053 / 0.197 | 0.773 / 0.833 | 0.013 / 0.110 |
| Conlangs - Neo-Quenya - Literary - NT | 0.114 / 0.301 | 0.076 / 0.187 | 0.606 / 0.637 | 0.094 / 0.212 |
| Conlangs - Neo-Quenya - Technical - Europe-Taipei Wikia | 0.060 / 0.178 | 0.033 / 0.114 | 0.608 / 0.624 | 0.056 / 0.080 |
| Conlangs - Toki Pona - Literary - NT - Sermon on the Mount | 0.226 / 0.311 | 0.198 / 0.221 | 0.785 / 0.811 | 0.088 / 0.322 |
| Conlangs - Toki Pona - Technical - Turkey-Mexico Wikia | 0.195 / 0.141 | 0.070 / 0.202 | 0.710 / 0.758 | 0.021 / 0.214 |
| Conlangs - Volapuk - Literary - NT | 0.129 / 0.315 | 0.039 / 0.178 | 0.591 / 0.600 | 0.081 / 0.196 |
| Conlangs - Volapuk - Technical - History Wiki | 0.164 / 0.236 | 0.033 / 0.144 | 0.601 / 0.667 | 0.069 / 0.124 |
| Historical - Anglo-Saxon - Literary - NT - Hatton Gospels | 0.119 / 0.343 | 0.047 / 0.167 | 0.706 / 0.716 | 0.090 / 0.217 |
| Historical - Anglo-Saxon - Technical - Leechbook | -0.017 / 0.314 | 0.037 / 0.110 | 0.633 / 0.671 | 0.061 / 0.133 |
| Historical - Arabic - Literary - Quran | 0.278 / 0.276 | 0.026 / 0.070 | 0.807 / 0.840 | 0.040 / 0.109 |
| Historical - Arabic - Technical - Avicenna | 0.202 / 0.280 | 0.032 / 0.127 | 0.643 / 0.665 | 0.079 / 0.174 |
| Historical - English - Literary - NT (KJV) | 0.174 / 0.253 | 0.044 / 0.192 | 0.659 / 0.675 | 0.085 / 0.244 |
| Historical - English - Technical - Secreta Alberti | 0.214 / 0.356 | 0.034 / 0.182 | 0.694 / 0.687 | 0.088 / 0.225 |
| Historical - Flemish - Literary - NT | 0.117 / 0.305 | 0.068 / 0.201 | 0.678 / 0.676 | 0.119 / 0.289 |
| Historical - Flemish - Technical - Cruydeboeck | 0.140 / 0.332 | 0.039 / 0.183 | 0.575 / 0.587 | 0.106 / 0.266 |
| Historical - French - Literary - NT - Martin | 0.094 / 0.260 | 0.052 / 0.168 | 0.688 / 0.703 | 0.103 / 0.240 |
| Historical - German - Literary - NT - Luther | 0.129 / 0.331 | 0.053 / 0.165 | 0.669 / 0.685 | 0.122 / 0.265 |
| Historical - German - Technical - German Herbarium | 0.123 / 0.330 | 0.054 / 0.151 | 0.694 / 0.705 | 0.103 / 0.247 |
| Historical - Greek - Literary - NT - Textus Receptus | 0.079 / 0.321 | 0.029 / 0.163 | 0.695 / 0.709 | 0.056 / 0.230 |
| Historical - Greek - Technical - De odoribus | 0.132 / 0.144 | 0.003 / 0.096 | 0.857 / 0.876 | 0.016 / 0.118 |
| Historical - Italian - Literary - NT - Diodati | 0.010 / 0.255 | 0.032 / 0.155 | 0.626 / 0.645 | 0.053 / 0.193 |
| Historical - Italian - Technical - Della Pittura | 0.076 / 0.328 | 0.044 / 0.145 | 0.694 / 0.696 | 0.067 / 0.206 |
| Historical - Latin (Abbreviated) - Literary - NT (Vulgate) | 0.069 / 0.294 | 0.048 / 0.172 | 0.564 / 0.579 | 0.050 / 0.163 |
| Historical - Latin (Abbreviated) - Technical - Pliny's Natural History | -0.027 / 0.332 | 0.046 / 0.169 | 0.475 / 0.554 | 0.054 / 0.139 |
| Historical - Latin - Literary - NT (Vulgate) | 0.030 / 0.339 | 0.031 / 0.152 | 0.588 / 0.575 | 0.072 / 0.206 |
| Historical - Latin - Technical - Pliny's Natural History | -0.037 / 0.215 | 0.032 / 0.163 | 0.471 / 0.530 | 0.061 / 0.159 |
| Historical - Mayan (Kaqchikel) - Literary - Annals of the Cakchiquels | 0.136 / 0.349 | 0.088 / 0.191 | 0.625 / 0.644 | 0.242 / 0.299 |
| Historical - Mayan (Yucatec) - Technical - Chilam Balam | 0.225 / 0.116 | 0.138 / 0.188 | 0.655 / 0.679 | 0.190 / 0.154 |
| Historical - Nahuatl - Literary - Nican Mopohua | -0.132 / 0.356 | 0.052 / 0.173 | 0.524 / 0.525 | 0.058 / 0.155 |
| Historical - Nahuatl - Technical - Florentine Codex | 0.096 / 0.367 | 0.044 / 0.177 | 0.608 / 0.636 | 0.066 / 0.142 |
| Historical - Portuguese - Technical - Coloquios dos simples | 0.020 / 0.257 | 0.065 / 0.167 | 0.715 / 0.720 | 0.105 / 0.194 |
| Historical - Russian - Literary - NT - Codex Marianus | 0.159 / 0.256 | 0.029 / 0.124 | 0.702 / 0.729 | 0.076 / 0.189 |
| Historical - Sanskrit - Literary - Mahabharata | 0.267 / 0.236 | 0.019 / 0.040 | 0.637 / 0.769 | 0.044 / 0.074 |
| Historical - Sanskrit - Technical - Charaka Samhita | 0.253 / 0.248 | 0.019 / 0.037 | 0.684 / 0.790 | 0.045 / 0.053 |
| Historical - Spanish - Literary - NT - Sagradas Escrituras | 0.107 / 0.337 | 0.039 / 0.170 | 0.718 / 0.728 | 0.071 / 0.217 |
| Historical - Spanish - Technical - De Materia Medica | -0.042 / 0.177 | 0.047 / 0.152 | 0.655 / 0.619 | 0.059 / 0.100 |
| Modern - Arabic - Literary - NT | 0.206 / 0.261 | 0.047 / 0.144 | 0.547 / 0.574 | 0.085 / 0.175 |
| Modern - Arabic - Technical - Voynich Wiki | -0.034 / 0.200 | 0.013 / 0.081 | 0.557 / 0.606 | 0.040 / 0.089 |
| Modern - Chinese (Pinyin) - Literary - NT - Matthew | 0.045 / 0.073 | 0.539 / 0.630 | 0.974 / 0.976 | 0.109 / 0.193 |
| Modern - Chinese (Pinyin) - Technical - Voynich Wiki | 0.112 / 0.036 | 0.390 / 0.511 | 0.927 / 0.961 | 0.085 / 0.079 |
| Modern - English - Literary - NT | 0.146 / 0.300 | 0.032 / 0.180 | 0.650 / 0.655 | 0.070 / 0.230 |
| Modern - English - Technical - Voynich Wiki | 0.041 / 0.353 | 0.014 / 0.151 | 0.577 / 0.590 | 0.045 / 0.176 |
| Modern - French - Literary - NT | 0.076 / 0.312 | 0.055 / 0.173 | 0.687 / 0.696 | 0.108 / 0.238 |
| Modern - French - Technical - Voynich Wiki | 0.015 / 0.246 | 0.017 / 0.130 | 0.667 / 0.695 | 0.064 / 0.168 |
| Modern - German - Literary - NT | 0.163 / 0.320 | 0.052 / 0.170 | 0.646 / 0.670 | 0.119 / 0.272 |
| Modern - German - Technical - Voynich Wiki | 0.139 / 0.446 | 0.030 / 0.166 | 0.485 / 0.519 | 0.085 / 0.183 |
| Modern - Hebrew - Literary - NT | 0.197 / 0.311 | 0.086 / 0.176 | 0.605 / 0.612 | 0.146 / 0.229 |
| Modern - Hebrew - Technical - Voynich Wiki | 0.082 / 0.122 | 0.021 / 0.132 | 0.568 / 0.625 | 0.035 / 0.080 |
| Modern - Italian - Literary - NT | 0.071 / 0.217 | 0.043 / 0.150 | 0.639 / 0.642 | 0.052 / 0.188 |
| Modern - Italian - Technical - Voynich Wiki | 0.123 / 0.203 | 0.015 / 0.144 | 0.597 / 0.634 | 0.031 / 0.117 |
| Modern - Maori - Literary - NT | 0.143 / 0.408 | 0.141 / 0.272 | 0.698 / 0.689 | 0.205 / 0.387 |
| Modern - Maori - Technical - Polandball Wiki | -0.066 / 0.373 | 0.088 / 0.130 | 0.626 / 0.675 | 0.067 / 0.126 |
| Modern - Portuguese - Technical - Voynich Wiki | -0.031 / 0.185 | 0.025 / 0.127 | 0.572 / 0.615 | 0.026 / 0.094 |
| Modern - Russian - Technical - Voynich Wiki | 0.007 / 0.315 | 0.012 / 0.085 | 0.505 / 0.536 | 0.020 / 0.095 |
| Modern - Spanish - Technical - Voynich Wiki | -0.013 / 0.302 | 0.027 / 0.153 | 0.621 / 0.633 | 0.047 / 0.164 |
| Modern - Swahili - Literary - NT | 0.082 / 0.379 | 0.063 / 0.207 | 0.453 / 0.471 | 0.067 / 0.237 |
| Modern - Swahili - Technical - Lung Cancer Wiki | 0.098 / 0.214 | 0.055 / 0.153 | 0.612 / 0.618 | 0.064 / 0.151 |
| Modern - Tagalog - Literary - NT - Ang Dating Biblia | 0.131 / 0.427 | 0.040 / 0.230 | 0.674 / 0.669 | 0.065 / 0.282 |
| Modern - Tagalog - Technical - Tuberculosis Wiki | 0.166 / 0.359 | 0.024 / 0.162 | 0.615 / 0.637 | 0.045 / 0.204 |
| Modern - Turkish - Literary - NT | 0.056 / 0.310 | 0.031 / 0.118 | 0.647 / 0.663 | 0.077 / 0.180 |
| Modern - Turkish - Technical - Middle Ages Wiki | -0.014 / 0.145 | 0.018 / 0.105 | 0.573 / 0.613 | 0.038 / 0.087 |
| Modern - Wolof - Technical - Senegal Wiki | 0.168 / 0.221 | 0.054 / 0.148 | 0.662 / 0.699 | 0.057 / 0.130 |
| Modern - Yoruba - Technical - Jupiter Wiki | 0.083 / 0.238 | 0.080 / 0.135 | 0.523 / 0.540 | 0.109 / 0.169 |

Esito (a): **in parte (3 misure su 4)**. Esito (b): **il Voynich non cambia**.
