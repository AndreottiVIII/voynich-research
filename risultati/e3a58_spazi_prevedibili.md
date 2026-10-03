# e3a58 — Dove cade lo spazio si indovina dai due segni vicini? E gli spazi incerti?

Preregistrazione: `preregistrazioni/e3a58.md`.

## Parte 1 — F1 della regola "coppia di segni" sugli spazi

Testi sensati: minimo 0.453, 10° percentile 0.525, mediana 0.639, 90° percentile 0.718, massimo 0.974. Il Voynich supera il 97% dei testi sensati.

| testo | F1 |
|---|---|
| Voynich | 0.862 (sottoinsiemi: 0.859, 0.863, 0.862, 0.840, 0.865) |
| gibberish umano | 0.282 |
| Naibbe (Greshko 2025), a capo | 0.883 |
| U2 (Whitehatnetizen 2026) | 0.860 |
| U3 (Whitehatnetizen 2026) | 0.815 |
| Timm e Schinner, seme 1 | 0.801 |

| testo sensato | F1 |
|---|---|
| Modern - Chinese (Pinyin) - Literary - NT - Matthew | 0.974 |
| Modern - Chinese (Pinyin) - Technical - Voynich Wiki | 0.927 |
| Historical - Greek - Technical - De odoribus | 0.857 |
| Conlangs - Lojban - Literary - Alice in Wonderland | 0.827 |
| Historical - Arabic - Literary - Quran | 0.807 |
| Conlangs - Toki Pona - Literary - NT - Sermon on the Mount | 0.785 |
| Conlangs - Lojban - Technical - Science News | 0.773 |
| Historical - Spanish - Literary - NT - Sagradas Escrituras | 0.718 |
| Historical - Portuguese - Technical - Coloquios dos simples | 0.715 |
| Conlangs - Toki Pona - Technical - Turkey-Mexico Wikia | 0.710 |
| Historical - Anglo-Saxon - Literary - NT - Hatton Gospels | 0.706 |
| Conlangs - Klingon - Literary - NT - Mark | 0.703 |
| Historical - Russian - Literary - NT - Codex Marianus | 0.702 |
| Modern - Maori - Literary - NT | 0.698 |
| Historical - Greek - Literary - NT - Textus Receptus | 0.695 |
| Historical - Italian - Technical - Della Pittura | 0.694 |
| Historical - German - Technical - German Herbarium | 0.694 |
| Historical - English - Technical - Secreta Alberti | 0.694 |
| Historical - French - Literary - NT - Martin | 0.688 |
| Modern - French - Literary - NT | 0.687 |
| Historical - Sanskrit - Technical - Charaka Samhita | 0.684 |
| Historical - Flemish - Literary - NT | 0.678 |
| Conlangs - Esperanto - Literary - NT | 0.674 |
| Modern - Tagalog - Literary - NT - Ang Dating Biblia | 0.674 |
| Historical - German - Literary - NT - Luther | 0.669 |
| Modern - French - Technical - Voynich Wiki | 0.667 |
| Modern - Wolof - Technical - Senegal Wiki | 0.662 |
| Historical - English - Literary - NT (KJV) | 0.659 |
| Historical - Spanish - Technical - De Materia Medica | 0.655 |
| Historical - Mayan (Yucatec) - Technical - Chilam Balam | 0.655 |
| Modern - English - Literary - NT | 0.650 |
| Modern - Turkish - Literary - NT | 0.647 |
| Modern - German - Literary - NT | 0.646 |
| Historical - Arabic - Technical - Avicenna | 0.643 |
| Modern - Italian - Literary - NT | 0.639 |
| Conlangs - Interlingua - Literary - NT | 0.639 |
| Historical - Sanskrit - Literary - Mahabharata | 0.637 |
| Historical - Anglo-Saxon - Technical - Leechbook | 0.633 |
| Historical - Italian - Literary - NT - Diodati | 0.626 |
| Modern - Maori - Technical - Polandball Wiki | 0.626 |
| Historical - Mayan (Kaqchikel) - Literary - Annals of the Cakchiquels | 0.625 |
| Modern - Spanish - Technical - Voynich Wiki | 0.621 |
| Conlangs - Esperanto - Technical - Voynich Wiki | 0.616 |
| Modern - Tagalog - Technical - Tuberculosis Wiki | 0.615 |
| Modern - Swahili - Technical - Lung Cancer Wiki | 0.612 |
| Conlangs - LOLCat - Literary - NT - Matthew | 0.610 |
| Historical - Nahuatl - Technical - Florentine Codex | 0.608 |
| Conlangs - Neo-Quenya - Technical - Europe-Taipei Wikia | 0.608 |
| Conlangs - Neo-Quenya - Literary - NT | 0.606 |
| Conlangs - Interlingua - Technical - EU Wiki | 0.606 |
| Modern - Hebrew - Literary - NT | 0.605 |
| Conlangs - Volapuk - Technical - History Wiki | 0.601 |
| Modern - Italian - Technical - Voynich Wiki | 0.597 |
| Conlangs - Volapuk - Literary - NT | 0.591 |
| Historical - Latin - Literary - NT (Vulgate) | 0.588 |
| Modern - English - Technical - Voynich Wiki | 0.577 |
| Historical - Flemish - Technical - Cruydeboeck | 0.575 |
| Modern - Turkish - Technical - Middle Ages Wiki | 0.573 |
| Modern - Portuguese - Technical - Voynich Wiki | 0.572 |
| Modern - Hebrew - Technical - Voynich Wiki | 0.568 |
| Historical - Latin (Abbreviated) - Literary - NT (Vulgate) | 0.564 |
| Modern - Arabic - Technical - Voynich Wiki | 0.557 |
| Modern - Arabic - Literary - NT | 0.547 |
| Conlangs - Klingon - Technical - Proxima Centauri B Wikia | 0.525 |
| Historical - Nahuatl - Literary - Nican Mopohua | 0.524 |
| Modern - Yoruba - Technical - Jupiter Wiki | 0.523 |
| Modern - Russian - Technical - Voynich Wiki | 0.505 |
| Modern - German - Technical - Voynich Wiki | 0.485 |
| Historical - Latin (Abbreviated) - Technical - Pliny's Natural History | 0.475 |
| Historical - Latin - Technical - Pliny's Natural History | 0.471 |
| Modern - Swahili - Literary - NT | 0.453 |

Esito parte 1: **spazi più prevedibili che nelle lingue**.

## Parte 2 — Spazi incerti (ZL)

| posizioni | quante | probabilità media di spazio | quota fra 0,3 e 0,7 |
|---|---|---|---|
| spazio (.) | 27442 | 0.818 | 0.196 |
| spazio incerto (,) | 2436 | 0.470 | 0.403 |
| nessuno spazio | 120652 | 0.041 | 0.042 |

Esito parte 2: **gli spazi incerti cadono dove la regola è incerta**.
