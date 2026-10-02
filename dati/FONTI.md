# Fonti dei dati

## Trascrizioni del Voynich (in `trascrizioni/`)

Sono le trascrizioni pubblicate da René Zandbergen su
[voynich.nu](https://www.voynich.nu/transcr.html), nel formato IVTFF. Il sito
da questo ambiente non si raggiunge: le copie vengono dal repository pubblico
[Krymorn/The-Voynich-Transliteration-Tool](https://github.com/Krymorn/The-Voynich-Transliteration-Tool)
(commit `cb2d36894a901b9570dd05e96f309fedf9947c4e`), che le distribuisce con
le impronte SHA-256 degli originali. Le nostre copie coincidono con quelle
impronte. Gli autori le rendono liberamente disponibili per la ricerca.

| file | trascrizione | alfabeto | versione | SHA-256 |
|---|---|---|---|---|
| `ZL3b-n.txt` | Zandbergen-Landini, la più completa | EVA | 3b del 13/05/2025 | `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc` |
| `IT2a-n.txt` | Takahashi, dall'archivio interlineare di Stolfi | EVA di base | 2a, rivista 25/06/2025 | `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5` |
| `GC2a-n.txt` | Glen Claston | v101 | 2a, rivista 25/06/2025 | `b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f` |

## Testi di confronto (non nel repository, si rigenerano con `prepara.py`)

- **La Bibbia in 100 lingue**: [christos-c/bible-corpus](https://github.com/christos-c/bible-corpus),
  commit `44e5fca1bfb369a5da2ee23ebc6f421c88489c5c`, pubblico dominio (CC0).
  Da qui viene anche il cinese trascritto in pinyin (con la libreria `pypinyin`).
- **Testi tecnici latini** (ricette, agricoltura, piante, trattati):
  [cltk/lat_text_latin_library](https://github.com/cltk/lat_text_latin_library),
  commit `76229acaf02efd1964ac32009408a90b6f279758`, i testi della Latin Library.
- **Il cifrario Naibbe** (tabelle e Plinio cifrato di esempio):
  [greshko/naibbe-cipher](https://github.com/greshko/naibbe-cipher), commit
  `f2675ec5dd275268bc64dd48ea64fc0e0e9827a2`, licenza MIT modificata che chiede di citare
  Greshko, M. A. (2025), *The Naibbe cipher: a substitution cipher that encrypts Latin and
  Italian as Voynich Manuscript-like ciphertext*, Cryptologia,
  [doi:10.1080/01611194.2025.2566408](https://doi.org/10.1080/01611194.2025.2566408).
- **Il generatore ad autocitazione di Timm e Schinner** (programma Java e parametri pubblicati):
  [TorstenTimm/SelfCitationTextgenerator](https://github.com/TorstenTimm/SelfCitationTextgenerator),
  commit `a6ede2202dd7ad6285ce2c007bf22c2a0e7709b7`, licenza MIT. Timm, T. e Schinner, A. (2020),
  *A possible generating algorithm of the Voynich manuscript*, Cryptologia 44(1),
  [doi:10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999). Serve Java.
- **Il breviario romano in latino** (litanie, salmi, preci, preghiere):
  [DivinumOfficium/divinum-officium](https://github.com/DivinumOfficium/divinum-officium), commit
  `2dbc3c24ea7f96f014060aaa51caeec477f3c578`, licenza MIT; se ne scarica solo la cartella
  `web/www/horas/Latin`.
- **La decifrazione latina di Scott Schechter** (glossario EVA → latino e trascrizione usata):
  [scott-schechter/voynich-decoded](https://github.com/scott-schechter/voynich-decoded), commit
  `71f2f3c91e9113d285ab21e024f1dd70c1f43c44` (25/03/2026). Il repository non dichiara una licenza:
  non se ne copia niente qui, si scarica in cache e si legge.
- **La corrispondenza EVA → ebraico di Antenore Gatta**:
  [antenore/voynich-toolkit](https://github.com/antenore/voynich-toolkit), commit
  `cb137630762908517636b7f9ffb98bc5fe0dc05e`, licenza MIT; articolo su Zenodo,
  [doi:10.5281/zenodo.19226178](https://doi.org/10.5281/zenodo.19226178). L'esperimento 26 ne ricopia
  la tabella (`full_decode.py`: 17 segni più ii, i e ch, lettura da destra, due regole per l'iniziale);
  l'esperimento 27 le identificazioni delle piante (`champollion.py`, `FOLIO_PLANTS`: 58 fogli con nome
  italiano e grado di confidenza), a cui aggiunge i nomi latini.

## Letteratura e dati aggiunti nella fase nuova (in `cache/letteratura/`, non ridistribuiti)

Scaricati il 30/09/2026. Le copie restano fuori dal repository per rispetto dei diritti;
l'impronta permette di verificare di aver letto lo stesso file.

| file | fonte | SHA-256 |
|---|---|---|
| `arxiv_2608.17096.pdf` | Rozanova e Temerev 2026, <https://arxiv.org/pdf/2608.17096> (v1) | `8743a90036a624787117d3d97654c2d6730e273902bc5033a402127644378d4d` |
| `tiltman_1967.pdf` | Tiltman 1967, NSA DOCID 631091, via <https://web.archive.org/web/2020id_/https://www.nsa.gov/portals/75/documents/news-features/declassified-documents/tech-journals/voynich-manuscript-mysterious.pdf> | `2297136842d348b1b921862e0366a25074ad6552286788e3893b38892bf6deae` |
| `dimperio_1978.txt` | D'Imperio 1978, OCR di archive.org, item `DTIC_ADA070618` | `dc1115dd53aad6446022be78840890291067e161d0e361a86370ce885bcd1609` |
| `ignota_unmasqued.html` | glossario della Lingua Ignota ricompilato da Roth 1880, <https://web.archive.org/web/20120820002300id_/http://www.unmasqued.com/eclecticify/ignota.php> | `068ea3173d6d4bfcc11fbdb6f41267802096cbb731be6b82a6d3e1061171677c` |
| `feaster_2021_rightward_downward.html` | Feaster 2021, *Rightward and Downward in the Voynich Manuscript*, <https://griffonagedotcom.wordpress.com/2021/08/18/rightward-and-downward-in-the-voynich-manuscript/> (scaricato l'1/10/2026) | `3b3773d6fa793165e417225308bf835b8525a675d462c92dfd29ff78f73b6513` |
| `vogt_2012_line.pdf` | Vogt 2012, *The Line as a Functional Unit in the Voynich Manuscript: Some Statistical Observations*, <https://voynichthoughts.wordpress.com/wp-content/uploads/2012/11/the_voynich_line.pdf> | `be2730ebd6ba19b13894098ceef6294482ac3a7221499076b553e9cfac5cd2f2` |
| `smith_ponzi_2019.pdf` | Smith e Ponzi 2019, *Glyph Combinations across Word Breaks in the Voynich Manuscript* (preprint), <https://agnosticvoynich.wordpress.com/wp-content/uploads/2019/06/glyph-combinations-across-word-breaks-in-the-voynich-manuscript-preprint.pdf> | `6bb5e9103da8da403d847fa7df979b64b23690dc71b13121788fe1b21aa3f6d2` |

I `.txt` accanto ai PDF sono estratti con `pypdf` e servono solo per la ricerca nel testo.

## Testi sanscriti (e77, in `cache/sanscrito/`, non ridistribuiti)

Scaricati l'1/10/2026 dal clone GRETIL di ambuda-org, commit
`96e96220c686c9083d1646f85d5289cf0ab9e9ff`, cartella `1_sanskr/tei/`
(<https://github.com/ambuda-org/gretil>). Il sito GRETIL non era raggiungibile.

| file | testo | SHA-256 |
|---|---|---|
| `sa_manusmRti.xml` | *Manusmṛti* | `666c2d3c05a41b9bc449c50a5afffe575e278085269d93dccb0f480a61cdf7e1` |
| `sa_kAlidAsa-raghuvaMza.xml` | Kālidāsa, *Raghuvaṃśa* | `268de86e64d026ef9e67cb784902c6b08e73926315e16d44eb10357e80d93404` |
| `sa_daNDin-dazakumAracarita.xml` | Daṇḍin, *Daśakumāracarita* (scaricato, non usato nell'e77) | `3fd83daa8ca14faf855e76cf6a1b77219a395947d77367cf8855310e6cc9563e` |

## *Macer floridus* (e99, in `cache/macer/`, non ridistribuito)

| file | fonte | SHA-256 |
|---|---|---|
| `macer_1832_djvu.txt` | Macer floridus, *De viribus herbarum*, ed. L. Choulant, Lipsia 1832; OCR di archive.org, item `deviribusherbaru00mace`, file `deviribusherbaru00mace_djvu.txt` (scaricato l'1/10/2026) | `1baed87fec67e0c7d785fc7c92452bba8185f03e18b1b02b6b0378717161d8e3` |

## Testi senza senso scritti a mano (Gaskell e Bowern 2022) — e128

- Repository github.com/danielgaskell/voynich, commit d076a7d081f35098fa405928239595afd2e75927 (18/10/2022).
- File usato: `data/gibberish_transcriptions.zip`, SHA-256 a4bfa58af956603ab6607227ad640e01cb695c7b492c6914488bd30f6d0aebbe
  (38 trascrizioni Unicode). In `dati/cache/gaskell_bowern/`, non ridistribuito.
- Licenza: MIT modificata, con obbligo di citare Gaskell, D. E., Bowern, C. L. (2022), *Gibberish after all? Voynichese is
  statistically similar to human-produced samples of meaningless text*, CEUR Workshop Proceedings 3313.

## Letture proposte (e133) — in `dati/cache/letture_proposte/`, non ridistribuite

- Bax, S. (2014), *A proposed partial decoding of the Voynich script*. Il sito originale risponde 403 agli scaricamenti
  automatici; copia da web.archive.org (`/web/2014id_/` + URL stephenbax.net). `bax_2014.pdf`, SHA-256
  1ae1a2dae7af8f463de8e5b94d8905028f1c555a6ea59c011c4e553375c12c4e.
- Vatne, S. B. (2021), *Cracking the Voynich Cipher*, versione 1, sivbuggevatne.com/wp-content/uploads/2021/10/verson_1_75mb_2.pdf.
  `vatne_2021.pdf`, SHA-256 f7a91b48e898143edf3ca779ed1d5584ecf46a00fb8241832ad7777a40a99e72.
- Vatne, S. B. (2022), *Arranging the Voynich Plants by Name* (crackingthevoynichcipher.com), `vatne_2022_arranging.pdf`.
- Sherwood, E. & E., *The Voynich Botanical Plant Names Decoded* (edithsherwood.com, sito non raggiungibile; copia
  web.archive.org 2020), `sherwood_anagrammi.html`.
