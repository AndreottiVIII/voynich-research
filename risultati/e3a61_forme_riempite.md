# e3a61 — Il vocabolario riempie le forme più probabili?

Preregistrazione: `preregistrazioni/e3a61.md`. Riempimento = quota delle K sequenze più probabili (K = tipi attestati di quella lunghezza, 3–7 segni) che sono parole attestate.

Testi sensati: minimo 0.003, 10° percentile 0.018, mediana 0.043, 90° percentile 0.086, massimo 0.539. Il Voynich supera il 99% dei testi sensati.

| testo | riempimento | per lunghezza (3, 4, 5, 6, 7) |
|---|---|---|
| Voynich | 0.434 (sottoinsiemi: 0.443, 0.432, 0.431, 0.434, 0.440) | 0.64, 0.57, 0.46, 0.34, 0.26 |
| gibberish umano | 0.093 | 0.34, 0.12, 0.03, 0.00, 0.00 |
| Naibbe (Greshko 2025), a capo | 0.453 | 0.57, 0.54, 0.48, 0.37, 0.32 |
| U2 (Whitehatnetizen 2026) | 0.422 | 0.67, 0.56, 0.46, 0.34, 0.20 |
| U3 (Whitehatnetizen 2026) | 0.409 | 0.64, 0.55, 0.44, 0.32, 0.17 |
| Timm e Schinner, seme 1 | 0.432 | 0.74, 0.63, 0.40, 0.24, 0.12 |

| testo sensato | riempimento | per lunghezza (3, 4, 5, 6, 7) |
|---|---|---|
| Modern - Chinese (Pinyin) - Literary - NT - Matthew | 0.539 | 0.53, 0.57, 0.44, 0.67, – |
| Modern - Chinese (Pinyin) - Technical - Voynich Wiki | 0.390 | 0.40, 0.38, 0.42, 0.40, 0.00 |
| Conlangs - Toki Pona - Literary - NT - Sermon on the Mount | 0.198 | 0.33, 0.24, 0.00, 0.00, 0.00 |
| Modern - Maori - Literary - NT | 0.141 | 0.43, 0.22, 0.09, 0.04, 0.05 |
| Historical - Mayan (Yucatec) - Technical - Chilam Balam | 0.138 | 0.30, 0.16, 0.04, 0.00, 0.03 |
| Modern - Maori - Technical - Polandball Wiki | 0.088 | 0.24, 0.11, 0.07, 0.00, 0.04 |
| Historical - Mayan (Kaqchikel) - Literary - Annals of the Cakchiquels | 0.088 | 0.27, 0.17, 0.05, 0.03, 0.01 |
| Modern - Hebrew - Literary - NT | 0.086 | 0.25, 0.10, 0.05, 0.01, 0.00 |
| Modern - Yoruba - Technical - Jupiter Wiki | 0.080 | 0.24, 0.12, 0.03, 0.02, 0.02 |
| Conlangs - Neo-Quenya - Literary - NT | 0.076 | 0.21, 0.15, 0.11, 0.02, 0.01 |
| Conlangs - LOLCat - Literary - NT - Matthew | 0.076 | 0.27, 0.10, 0.03, 0.01, 0.00 |
| Conlangs - Klingon - Literary - NT - Mark | 0.074 | 0.27, 0.17, 0.04, 0.02, 0.01 |
| Conlangs - Toki Pona - Technical - Turkey-Mexico Wikia | 0.070 | 0.24, 0.13, 0.00, 0.00, 0.00 |
| Historical - Flemish - Literary - NT | 0.068 | 0.20, 0.13, 0.07, 0.05, 0.01 |
| Conlangs - Klingon - Technical - Proxima Centauri B Wikia | 0.065 | 0.11, 0.17, 0.00, 0.03, 0.00 |
| Historical - Portuguese - Technical - Coloquios dos simples | 0.065 | 0.27, 0.07, 0.05, 0.02, 0.01 |
| Modern - Swahili - Literary - NT | 0.063 | 0.17, 0.17, 0.06, 0.03, 0.01 |
| Modern - French - Literary - NT | 0.055 | 0.23, 0.13, 0.03, 0.02, 0.01 |
| Modern - Swahili - Technical - Lung Cancer Wiki | 0.055 | 0.18, 0.14, 0.04, 0.01, 0.01 |
| Conlangs - Lojban - Literary - Alice in Wonderland | 0.054 | 0.15, 0.22, 0.02, 0.00, 0.00 |
| Modern - Wolof - Technical - Senegal Wiki | 0.054 | 0.20, 0.09, 0.01, 0.00, 0.00 |
| Historical - German - Technical - German Herbarium | 0.054 | 0.16, 0.09, 0.06, 0.03, 0.01 |
| Historical - German - Literary - NT - Luther | 0.053 | 0.18, 0.07, 0.07, 0.03, 0.02 |
| Conlangs - Lojban - Technical - Science News | 0.053 | 0.16, 0.19, 0.01, 0.00, 0.00 |
| Historical - French - Literary - NT - Martin | 0.052 | 0.22, 0.12, 0.02, 0.02, 0.01 |
| Modern - German - Literary - NT | 0.052 | 0.16, 0.09, 0.07, 0.03, 0.01 |
| Historical - Nahuatl - Literary - Nican Mopohua | 0.052 | 0.05, 0.14, 0.06, 0.03, 0.01 |
| Historical - Latin (Abbreviated) - Literary - NT (Vulgate) | 0.048 | 0.19, 0.03, 0.05, 0.02, 0.00 |
| Historical - Spanish - Technical - De Materia Medica | 0.047 | 0.26, 0.06, 0.02, 0.00, 0.00 |
| Historical - Anglo-Saxon - Literary - NT - Hatton Gospels | 0.047 | 0.12, 0.09, 0.06, 0.02, 0.00 |
| Modern - Arabic - Literary - NT | 0.047 | 0.17, 0.07, 0.02, 0.01, 0.00 |
| Historical - Latin (Abbreviated) - Technical - Pliny's Natural History | 0.046 | 0.19, 0.08, 0.05, 0.01, 0.01 |
| Historical - Italian - Technical - Della Pittura | 0.044 | 0.13, 0.12, 0.06, 0.01, 0.00 |
| Historical - English - Literary - NT (KJV) | 0.044 | 0.18, 0.09, 0.02, 0.00, 0.00 |
| Historical - Nahuatl - Technical - Florentine Codex | 0.044 | 0.15, 0.00, 0.07, 0.05, 0.01 |
| Modern - Italian - Literary - NT | 0.043 | 0.09, 0.09, 0.07, 0.02, 0.00 |
| Conlangs - Esperanto - Literary - NT | 0.042 | 0.05, 0.06, 0.08, 0.03, 0.01 |
| Modern - Tagalog - Literary - NT - Ang Dating Biblia | 0.040 | 0.12, 0.09, 0.05, 0.03, 0.00 |
| Conlangs - Volapuk - Literary - NT | 0.039 | 0.16, 0.09, 0.03, 0.01, 0.00 |
| Historical - Spanish - Literary - NT - Sagradas Escrituras | 0.039 | 0.21, 0.07, 0.02, 0.02, 0.01 |
| Historical - Flemish - Technical - Cruydeboeck | 0.039 | 0.18, 0.06, 0.04, 0.03, 0.01 |
| Historical - Anglo-Saxon - Technical - Leechbook | 0.037 | 0.09, 0.03, 0.05, 0.00, 0.00 |
| Historical - English - Technical - Secreta Alberti | 0.034 | 0.13, 0.07, 0.02, 0.01, 0.00 |
| Conlangs - Volapuk - Technical - History Wiki | 0.033 | 0.12, 0.05, 0.03, 0.01, 0.02 |
| Conlangs - Neo-Quenya - Technical - Europe-Taipei Wikia | 0.033 | 0.17, 0.06, 0.03, 0.00, 0.00 |
| Historical - Italian - Literary - NT - Diodati | 0.032 | 0.09, 0.07, 0.05, 0.01, 0.00 |
| Modern - English - Literary - NT | 0.032 | 0.09, 0.07, 0.03, 0.00, 0.00 |
| Historical - Latin - Technical - Pliny's Natural History | 0.032 | 0.17, 0.07, 0.04, 0.01, 0.01 |
| Historical - Arabic - Technical - Avicenna | 0.032 | 0.10, 0.04, 0.02, 0.02, 0.01 |
| Modern - Turkish - Literary - NT | 0.031 | 0.16, 0.07, 0.04, 0.01, 0.00 |
| Historical - Latin - Literary - NT (Vulgate) | 0.031 | 0.12, 0.05, 0.05, 0.02, 0.00 |
| Modern - German - Technical - Voynich Wiki | 0.030 | 0.14, 0.04, 0.03, 0.01, 0.02 |
| Conlangs - Interlingua - Literary - NT | 0.030 | 0.11, 0.07, 0.03, 0.02, 0.01 |
| Conlangs - Interlingua - Technical - EU Wiki | 0.029 | 0.12, 0.06, 0.03, 0.02, 0.00 |
| Historical - Russian - Literary - NT - Codex Marianus | 0.029 | 0.07, 0.05, 0.03, 0.01, 0.01 |
| Historical - Greek - Literary - NT - Textus Receptus | 0.029 | 0.18, 0.04, 0.02, 0.02, 0.01 |
| Modern - Spanish - Technical - Voynich Wiki | 0.027 | 0.09, 0.08, 0.03, 0.01, 0.01 |
| Historical - Arabic - Literary - Quran | 0.026 | 0.08, 0.03, 0.02, 0.01, 0.00 |
| Modern - Portuguese - Technical - Voynich Wiki | 0.025 | 0.11, 0.05, 0.03, 0.01, 0.00 |
| Modern - Tagalog - Technical - Tuberculosis Wiki | 0.024 | 0.13, 0.07, 0.01, 0.02, 0.00 |
| Modern - Hebrew - Technical - Voynich Wiki | 0.021 | 0.04, 0.03, 0.03, 0.00, 0.00 |
| Historical - Sanskrit - Literary - Mahabharata | 0.019 | 0.06, 0.02, 0.01, 0.00, 0.00 |
| Historical - Sanskrit - Technical - Charaka Samhita | 0.019 | 0.06, 0.02, 0.01, 0.00, 0.00 |
| Modern - Turkish - Technical - Middle Ages Wiki | 0.018 | 0.11, 0.05, 0.01, 0.00, 0.00 |
| Modern - French - Technical - Voynich Wiki | 0.017 | 0.14, 0.02, 0.02, 0.00, 0.00 |
| Modern - Italian - Technical - Voynich Wiki | 0.015 | 0.04, 0.01, 0.03, 0.00, 0.01 |
| Modern - English - Technical - Voynich Wiki | 0.014 | 0.11, 0.01, 0.00, 0.01, 0.00 |
| Modern - Arabic - Technical - Voynich Wiki | 0.013 | 0.03, 0.01, 0.02, 0.01, 0.01 |
| Modern - Russian - Technical - Voynich Wiki | 0.012 | 0.05, 0.03, 0.01, 0.01, 0.00 |
| Conlangs - Esperanto - Technical - Voynich Wiki | 0.011 | 0.08, 0.01, 0.01, 0.01, 0.00 |
| Historical - Greek - Technical - De odoribus | 0.003 | 0.03, 0.00, 0.00, 0.00, 0.00 |

Esito: **il vocabolario riempie le forme probabili più che nelle lingue**.
