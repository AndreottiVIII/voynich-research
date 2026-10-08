# The Voynichizer (voynichizzatore): technical dossier

Compiled 8/10/2026 from the private repository `C:\Users\davide\voynich` (read-only) and the public copy
`C:\Users\davide\voynichizzatore`. Describes the published version **v21** unless stated otherwise. Every number has a
source in brackets. Abbreviations used for sources:

- **Q** = `QUADERNO.md` (line number of the entry heading or of the line).
- **DIA** = `voynichizzatore/DIARIO.md`. **SW** = `voynichizzatore/SITO_WEB.md`. **PUB** = `voynichizzatore/PUBBLICAZIONE.md`.
- **PROG** = `rassegna/voynichizzatore_progetto.md`. **P18** = `rassegna/piano_18.md`.
- **README** = public `README.md` (identical in `pubblico/voynichizzatore/` and in the public repo).
- **HOW** = public web page `docs/how.html` ("How it works", describes v21 at public commit `4b1383c`).
- Code files are cited as `file.py:Lnn`. The public modules `disposizione.py`, `pezzi.py`, `sacco.py`,
  `parole_nuove.py`, `v0.py`, `v1.py`, `pezzi_parametri_v21.json` are byte-identical to the private
  `voynichizzatore/` ones. `canale_sacco.py` and `pagine.py` differ only in the language of error messages. The public
  `modello.py` is a reduced copy (segmenter and links only).
- **R-v21** = `risultati/e409b_messaggio_nel_sacco_v21f1_chiavi_1_12.{md,json}` and `..._13_24.{md,json}`. These are
  the v21 measurements (`v21f1` = `v21`: the two parameter files are identical).

Items marked **[compiler]** were computed or observed while compiling this dossier and are not stated in the project
documents.

---

## 1. Summary

- **What it does.** It takes any UTF-8 text and a key and writes a whole book of 207 folios in EVA transliteration:
  - same folio names, sections and Currier languages as MS 408;
  - about 4,050–4,260 lines (HOW, "The layout of each page").

  With the key the text comes back exactly; with a wrong key it is rejected.
- **Where the message is.** The text is compressed (zlib) and encrypted (scrypt → SHAKE-256 keystream, truncated
  HMAC). It then decides only one thing: **how many times each "known" Voynich word appears on each page**. An
  arithmetic decoder turns the ciphertext bits into a multinomial sample from a key-dependent distribution.
- **What carries no information.** Everything else comes from the key and from Voynich statistics: page layout,
  invented words, word order.
- **Capacity.** About 80,000–86,000 bits per book, about 2.7 bits per known word.
- **Evaluation of v21** (24 keys):
  - two logistic-regression "judges": AUC **0.554 ± 0.004** (e231) and **0.601 ± 0.005** (e266);
  - scorecard 16.0 of 18 (17 attainable), extra properties 5.4 of 8, line gate 24 of 24;
  - exact read-back 24/24 (Q15905).
- **Message vs no message.** Books with a message and books with filler only could not be told apart (e409b). That
  test was run on an earlier body and cipher (see §4.6).

---

## 2. Pipeline, end to end (v21)

### 2.1 Source data

- **Text model source.** `voynich_zl3b.json` in the public package: the ZL transliteration (Zandbergen–Landini) v3b of
  13 May 2025. It is stated to be public domain / CC0 (README L88–93; PUB §7, L101–118).
  - Only the running paragraph text is used. Words with unreadable characters are dropped.
  - Labels and circular text are not used (HOW, "The source").
- **Counts** (HOW, "The source"):
  - 207 pages with running text;
  - 4,130 lines, 740 of them opening a paragraph;
  - 34,863 running words, 7,022 distinct;
  - **known words** (≥ 2 occurrences): 2,246, covering 86.3% of the tokens;
  - **one-off words** (hapax): 4,776, 13.7% of the tokens.
- **Page type** = (section, Currier language), taken from the ZL `$I` and `$L` fields (`pezzi.py:L24–34`).
  - Hands (`$H`) are **not** used, although Davide's design choice of 3/10 was to imitate "sections, hands, A/B"
    (PROG §1).
- **Glyph segmentation.** EVA, with `ch sh cth ckh cph cfh` treated as single glyphs (`misure.divisore(GLIFI_EVA)`).

### 2.2 Key derivation and per-use randomness

- **Master key** (`canale_sacco.py:L29–38`):

  ```
  k = scrypt(key_utf8, salt=b'voynichizzatore/canale-sacco/1', n=2^15, r=8, p=1, maxmem=2^26, dklen=32)
  ```

  This costs 32 MiB of memory per evaluation (HOW, "The key").
- **Random generators.** Every random choice uses its own generator, one per page and per use
  (`canale_sacco.py:L69–73`):

  ```
  random.Random(int.from_bytes(HMAC-SHA256(k, "sacco|<use>|<page>")[:16]))
  ```

  This is Python's Mersenne Twister.
- **The uses** (HOW table):
  - `carattere`: which real page lends its "character". This is the **only one needed to decode**.
  - `impaginazione`: layout.
  - `posti`: which places hold invented words.
  - `ordine`: initial shuffle of the known words.
  - `nuove`: the invented words.
  - `disposizione`: one generator for the whole book, seeded with `getrandbits(31)` (`canale_sacco.py:L269–270`).
- **Before v15** the keystream and the seeds came from `SHA-256(salt:key)[:8]` → `random.Random` (`v0.py:L31–32,
  L121–123`). This was not cryptographic (PUB §4 item 5, L69–71).

### 2.3 Compression, framing, encryption

`bit_cifrati` and `testo_dai_bit` (`canale_sacco.py:L45–66`).

- **Plaintext frame:**

  ```
  len(z) (4 bytes, big-endian) || HMAC-SHA256(k, b'etichetta' || z)[:8] || z
  ```

  where `z = zlib.compress(text.encode('utf-8'), 9)`. The overhead is 12 bytes.
- **Encryption.** The frame is XORed with `SHAKE-256(k || b'flusso')`. The next 30,000 bytes of the same keystream
  follow as **filler**. Bits are taken MSB first.
- **Book without a message** (`empty`). The bit stream is the keystream alone.
- **Decoding.** XOR, then a length check:
  - a bad length raises "wrong key, or manuscript without a message";
  - a failed tag raises "wrong key, or altered manuscript".

  The tag is 64 bits.
- **Example.** Isidore, *Etymologiae* XVII (opening, 11,207 bytes) compresses to 4,776 bytes, giving **38,304 bits**
  framed (R-v21 JSON fields `byte_testo`, `byte_compressi`, `bit_messaggio`). The pre-v15 framing, without the tag,
  gave 38,240 bits (Q8846). (The 4,776 compressed bytes equal the hapax count only by coincidence.)

### 2.4 Page layout ("gabbia statistica", since v17)

`statistiche_gabbia` and `gabbia_statistica` (`canale_sacco.py:L145–192`; e415, Q15213).

- **Pool of statistics.** For each page type, falling back to section and then to the whole book when fewer than 5
  pages are available, the program keeps:
  - the number of lines per page;
  - the page "width", i.e. the median number of words per line;
  - paragraph lengths in lines.

  For the whole book it also keeps the ratio (words in a line / page width) by line role: first, middle, last, or only
  line of a paragraph.
- **Drawing a page,** with the generator `impaginazione`:
  1. draw the number of lines and the width;
  2. draw paragraph lengths until the page is full; a leftover single line is appended as the last line of the
     previous paragraph, because the Voynich running text has no one-line paragraphs;
  3. draw the words of each line as `max(1, round(width × ratio))`.
- **No generated page has the layout of a real page** (direct check in e415, Q15229–15231).
  - Books are about 5% longer: for example 36,571 words and 4,190 lines, against 34,863 and 4,130 (Q15231).
- **Earlier layouts:**
  - v8–v15 copied the real page's layout;
  - v16 copied the layout of another real page of the same type.

### 2.5 Which places get invented words

Code: `sacco.py:L39–52`, `canale_sacco.py:L243–246`.

- **Eight place classes:** first line of a paragraph or not × first, second, middle or last word of the line
  (`disposizione.posizione`, `disposizione.py:L34–35`).
- **Share of hapax per class in the Voynich** (HOW, "Which places get invented words"):

  | | first word | second word | middle | last word |
  |---|---|---|---|---|
  | other lines | 0.175 | 0.090 | 0.087 | 0.212 |
  | first line of a paragraph | 0.477 | 0.200 | 0.189 | 0.308 |

- **Rule.** A place is "new" with probability `min(0.95, share[class] × m)`.
  - `m` is the hapax rate of the page that lends its character, divided by the book mean.
  - The draws use the generator `posti`.
- **The remaining n places take known words.** n depends only on the key.

### 2.6 Distribution of the known words of a page

Code: `sacco.py:L21–35, L77–101`; `canale_sacco.py:L76–85`.

- **Lexicon of page p.** All occurrences of known words on the *other* pages of the same section × language.
  - It falls back to the section, then to the book, if there are fewer than 500 occurrences.
  - A page never draws from itself.
  - Size: 283–2,246 types, median 1,170 (HOW).
- **"Character" of the page** (e404b, Q7933). With the generator `carattere`, the program picks another real page q of
  the same type with at least 40 known words. For each glyph g it computes

  ```
  δ_g = log[(c_q(g) + α f(g)) / (n_q + α) / f(g)],   α = 50
  ```

  where f(g) is the frequency of g in the section lexicon.
- **Weight of a word w:**

  ```
  c(w)^γ · exp(κ Σ_g n_g(w) δ_g),   γ = 0.97579,   κ = 0.64352
  ```

  The values of γ and κ are in `pezzi_parametri_v21.json` (tuned in e413, Q13920).
- **Integer weights.** Weights are rescaled to integers on a scale of 2^40 (minimum 1) (`SCALA`,
  `canale_sacco.py:L22`). They are sorted by descending weight, with ties broken by the word, so that encoder and
  decoder see the same ordered list.
- **Repetition parameter.** θ (in-page repetition) appears in the parameter file (2279.85) but is **not used** by the
  bag channel. e409 removed it to obtain a pure multinomial (`preregistrazioni/e409.md` L32–34).

### 2.7 "Il messaggio nel sacco": bits → word counts

Code: `_passi`, `conteggi_dai_bit`, `bit_dai_conteggi` (`canale_sacco.py:L88–139`); the coder is in `v1.py:L129–188`.
Preregistration: `preregistrazioni/e409.md`.

- **Multinomial as a chain of binomials.** For a page with n known-word places and ordered integer weights
  w₁ ≥ … ≥ w_m (total W), the counts are drawn as

  ```
  c₁ ~ Bin(n, w₁/W),   c₂ ~ Bin(n − c₁, w₂/(W − w₁)), …
  ```

  The last type takes the remainder. This is exactly one multinomial draw of size n.
- **Each binomial is a run of binary decisions.** Having placed j copies, the decision "stop here?" has probability

  ```
  h_j = P(X = j) / P(X ≥ j),   X ~ Bin(remaining, w/remaining weight)
  ```

  - h_j is computed in double precision and quantised to 16 bits, clamped to [1, 65,535] out of 65,536
    (`v1.TOT = 2^16`).
  - Symbol 0 means "stop" (`canale_sacco.py:L117`).
- **Coder.** Each decision is a symbol of a binary arithmetic coder (Witten–Neal–Cleary, 32-bit registers with
  underflow handling, `v1.PREC = 32`, `v1.py:L24–25`).
  - **Encoding** runs the arithmetic *decoder* (`Nasconditore`), fed by the ciphertext-plus-filler bit stream. It
    therefore "samples" the decisions.
  - **Decoding** runs the arithmetic *encoder* (`Rilettore`) on the observed decisions to recover the bits.
- **Bit order.** Bits are consumed in page order. The Isidore text (38,304 bits) fills about 124–131 of the 207 pages
  (R-v21 JSON `pagine_usate`); filler covers the rest.
- **Capacity of a book** = bits consumed after the last page − 32 (`canale_sacco.py:L271`).
  - If the message is longer, encoding stops with "text too long for this book" (`L276–277`).
  - After encoding, a full check decoding is run (`L278–279`).
- **Rationale stated by the project** (PROG §2, L24–46; HOW, "The design principle"):
  - uniformly random bits fed to an arithmetic decoder yield an exact sample of the model, up to quantisation;
  - so the book is a sample of the model, with "perfect" security *relative to the model* in Cachin's (1998) sense
    (arithmetic-coding steganography, Ziegler, Deng and Rush 2019).
  - Corollary (PROG §2): capacity is fixed by the model's entropy and cannot be raised without changing the
    statistics.

### 2.8 Invented words (the "one-off" model)

Code: `parole_nuove.FormeUniche` (`parole_nuove.py:L98–240`); parameters in `pezzi_parametri_v21.json` →
`forme`. Development: e403, e403b, e405, e407, e413, e414 (Q7753, Q7839, Q8040, Q8560, Q13920, Q14020).

- **Training set.** The model is learned on the 4,776 hapax.
- **Length.** For the place class, a length L in glyphs is drawn from the lengths of the hapax in that class.
- **Glyph sequence.**
  - Four-glyph contexts seen at least 3 times are used (`quattro=True`, `MINIMO_CONTESTO = 3`). There are 1,044 such
    contexts (HOW).
  - The model backs off to trigram contexts (422).
  - Counts are the class counts plus 0.1 × the counts of all classes (`DECIMO`).
- **Acceptance of a candidate.** It must have at least 2 glyphs and length L (up to 400 tries, otherwise the closest
  length). It must be **neither a Voynich word (any frequency) nor already used in the book** (`L181–186`).
- **Joins.**
  - With probability 0.25, a word of 6 glyphs or more is instead the join of two known words of the same page whose
    lengths sum to L (`unioni`).
  - A join is accepted only if every glyph triple occurs in the hapax (`unioni_valide`) and both cross-junction
    triples have conditional probability ≥ 0.05 (`giuntura`, e414) (`L188–216`).
  - Rationale: in the Voynich, 2.7 of the 8.8 percentage points of "attested joins" come from hapax that are two
    words written together (Q8565–8568).
- **Choice by page profile.** Six candidates are drawn (`CANDIDATE`). One is chosen with weight

  ```
  exp(0.3701 · Σ_g profile(g))
  ```

  - profile(g) is the smoothed (α = 50) log-ratio of glyph g between this page's known words and the book;
  - only glyphs with at least 1% book share are used (`comuni=True`, `COMUNE = 0.01`) (`L158–163, L218–240`).
- **Consequence for decoding.** Invented words are never Voynich words, so they can never be confused with known
  words.

### 2.9 Arrangement of the words (carries no information)

Code: `disposizione.py`; links from `modello.legami()`. Development: e401, e401b, e407, e408, e410, e412, e416b,
e417, e418.

- **Place affinity.** A multinomial logistic regression (scikit-learn, C = 1), fitted on all Voynich tokens, maps
  binary word features to the 8 place classes (`L38–42, L48–74`). Features (578 binary features, HOW):
  - first glyph and first two glyphs;
  - last glyph and last two glyphs;
  - length capped at 9;
  - prefix and ending from a segmentation into the 150 most frequent pieces (`modello.segmentatore`: up to 4 glyphs
    each, penalty 2.0);
  - presence of p and of f.

  It is based on features, not word identity, so it also applies to invented words (`conosci`, `L108–123`).
- **Link tables between neighbours.** Observed/expected ratios, clipped to [0.2, 5], keeping only cells with expected
  count ≥ 5 (`modello.py`; `disposizione.py:L88–93`).
- **Score of an arrangement.** A weighted sum. The v21 weights are in `pezzi_parametri_v21.json`; the code is
  `legame` and `pagina` (`disposizione.py:L125–368`).

  | term | weight |
  |---|---|
  | log P(place class \| word), every word | 1 |
  | (ending, prefix) and (prefix, prefix) links | 1.0031 (`bordi`) |
  | (ending, ending) link | 0 (`fin_fin`) |
  | pair forms a word of the generated book when joined: log(0.0916/0.0485) if yes, log(0.9084/0.9515) if no | 0.9793 (`unione`, `vocabolario_testo`) |
  | (last glyph, first glyph) link | 0.7419 (`confine`) |
  | pair seen on other Voynich pages: clipped log((seen + 0.5)/(expected + 0.5)) | −0.3658 (`coppia`) |
  | identical neighbours | −0.4166 (`identica`) |
  | similarity (1 − normalised edit distance) with the word at the **same index** in the line above | 0.1524 (`verticale`) |
  | first glyph of a non-paragraph line equal to the first glyph of the line above | −0.9481 (`prima_lettera`) |
  | similarity of words two places apart | 0.30 (`distanza2`) |
  | five spelling choices (ch/sh, k/t, -l/-r, qo-/o-, -dy/-ey) agreeing within a line; product of (long − short) for consecutive lines | 0.0444 (`scelte`); 0.0484 (`scelte_sopra`) |
  | glyph-content difference between the two halves of the page (sum of squared differences / glyphs) | 1.1027 (`meta`) |
  | squared deviation of the line width in characters from the expected width (11-node curve fitted on the Voynich, rescaled to the page total) | penalty 0.01 (`larghezza`, `larghezza_curva`) |

- **Sampler.** Starting from a random order, the program proposes 60 × N random swaps per page (N = words on the
  page), with Metropolis acceptance at temperature 1 (`PASSATE = 60`, `L329–363`).
  - This takes about 87 of the 105 s of an encoding (HOW, "Capacity, time, memory").
- **Defect corrected in v21** (e418, Q15905).
  - From v12 to v20 the per-line counts used by `scelte` and `scelte_sopra` were never initialised: three lines sat
    after a `return`.
  - v21 sets `conti_iniziali: true` (`L241–250`).
  - The defect was found by the website chat, reading the public code (SW §13, L216–220).

### 2.10 Output formats

- **EVA file** (`v0.salva` and `v0.carica`, `v0.py:L177–196`).
  - UTF-8 text. Comment lines start with `#`.
  - Then one line per manuscript line: `<folio.line> w1.w2.w3`, with a leading `@` on lines that open a paragraph.
  - Size about 260 KB (SW §4).
- **The PDF cannot be read back.** Only the EVA file can be decoded (SW §5, L65–67).
- **Command-line PDF** (`pagine.py`, command `pdf`).
  - 6 × 8.6 in pages, one per folio, on a parchment-coloured background, text only.
  - Font `VoynichizzatoreEVA.ttf` v1.1, drawn stroke by stroke by `carattere.py` with fontTools.
    - Compound glyphs are at private code points from U+E000 and are also available as GSUB ligatures.
    - It is not Landini's EVA Hand 1 font, which is not licensed for commercial use.
  - A full book takes about 9–10 s and about 0.6 MB (DIA L736–758; Q15591).
- **Website illustrated book** (made by the site, not by the program).
  - The site's own engine composes each folio on vellum with the real drawing of the folio of the same name, lifted
    from Yale photographs (153 cleaned drawings).
  - The PDF is made in the browser with jsPDF 4.2.1: 207 pages, about 8 MB (SW §13, L247–252; HOW, "The script and the
    illustrated book").
- **Not generated:** labels, circular or radial text, images generated from scratch. These were planned in PROG §1
  and §6 but not implemented (HOW, "Known limits").

### 2.11 Decoding

Code: `canale_sacco.py:L283–307`.

- **Steps:**
  1. derive k;
  2. for each page in manuscript order, recompute the distribution (lexicon, character page via the `carattere`
     generator, integer weights);
  3. count the occurrences of the distribution's words on that page;
  4. run the arithmetic encoder over the same decision chain;
  5. XOR the bits, check the length and the tag, decompress.
- **Robustness** (HOW, "Reading back"):
  - moving words within a page, or replacing an invented word with any word outside the page lexicon, has no effect;
  - adding, removing, changing or moving a known word breaks decoding.
  - There is no error correction.
- **Wrong key.** Rejected 24/24 for v21 (Q15905).

### 2.12 Determinism, platforms, timing

- **On one PC the output is byte-deterministic,** including across `PYTHONHASHSEED` values 0 and 12345 (SW §12,
  L173–175).
- **Pyodide in the browser** (Python 3.14.2; NumPy 2.4.6; SciPy 1.18.0; scikit-learn 1.8.0):
  - the arrangement differs (4,047 of 4,050 lines differ);
  - the **words of every page are identical** (207/207);
  - read-back works in both directions (SW §12, L160–179).
  - Reason given: counts depend only on integer-rounded quantities, while the arrangement compares floating-point
    scores (HOW, "Determinism").
- **The site acceptance test passed** (SW §13, L229–237):
  - 5 cases: short English; Italian with accents; mixed Unicode with emoji; 32,014 characters = 76,888 bits, 91% of
    capacity; empty book;
  - each case read back crosswise PC ↔ browser.
- **Read-back on a second physical computer** (`prova.py`): **not reported as done** in any document read (README
  L79; DIA L904).
- **Timings on a PC:**
  - encode about 105 s (model 9 s, counts 7 s, arrangement 87 s, check 2 s);
  - decode about 5 s;
  - pdf about 9–10 s.
  - In the browser, encoding takes about 3½–4½ min and needs about 400–480 MB of memory (SW §4; HOW).
- **Dependencies.** `requirements.txt` lists numpy, scipy, scikit-learn, matplotlib and fonttools **without pinned
  versions**.
  - The README warns to use the same program version for writing and reading (README L75–79).

---

## 3. Capacity and version history

### 3.1 Capacity

| channel / version | capacity | source |
|---|---|---|
| first tool `analisi/voynichizzatore.py` (word-by-word arithmetic coding with exact fractions) | "about 4 bits per word" (single-page tests) | Q4781–4810 |
| v0: direct XOR into the 5 spelling choices at key-permuted places | 57,696 choice places; Isidore used 66% | Q6657–6669 |
| v1–v9: arithmetic coding over a logistic model of the 5 spelling choices | about 0.8 bit per place, **about 46,000 bits** per book (56,850 places) | Q6710–6713; e409 prereg L8 |
| research upper bounds | spelling choices about 47,000 bits; "three channels" about 93,000; loose limit about 380,000 (e259b) | PROG §5 L205–206, §11 L324–325 |
| prediction before e409 | 100,000–250,000 bits | `preregistrazioni/e409.md` L52 |
| bag channel, v9 body (e409) | 80,300 bits mean (4 keys); Isidore used 131 of 207 pages | Q8846–8848 |
| v12 | 80,200 | Q10531 |
| v13 | 82,300 | Q13940 |
| v14 | "about 82,000" | DIA L628 |
| v20, website test (5 keys) | 80,344–84,678 | SW §13 L213 |
| **v21, the 24 measurement keys** | mean **83,440**; range **81,116–85,905** **[compiler]** (keys 1–12 mean 83,164; keys 13–24 mean 83,715) | R-v21 JSON `capacita_bit` |
| per known word | "about 2.7 bits" | HOW, "Capacity" (not independently recomputed) |

- **Characters per book.** Stated as roughly 20,000 characters of ordinary prose after compression; more if the
  text compresses well (README L23; SW §4).

### 3.2 Version history

Judge values are AUC e231 / e266. "bench" means 3 keys or seeds (e293); "12k" means 12 keys; "24k" means 24 keys.

| version | what changed | key numbers | source |
|---|---|---|---|
| "v2" of `analisi/voynichizzatore.py` (named "v2" in PROG §2) | word-level arithmetic coding over an explicit model (layout from real pages, start words, page reservoir, variants, copy from the line above, junctions, the 5 choices); exact fractions | about 4 bits/word; repetition defects ("chol" at 11%) | Q4781, Q4826–4829 |
| v0 (`voynichizzatore/v0.py`) | body = generator e241, seed from the key; message XOR-forced into the 5 spelling choices | with message 0.958 / 0.980 vs 0.893 / 0.951 without; line gate lost | Q6657 |
| v1 | arithmetic coding over a logistic model of the choices (context, line position, line state) | 0.889 / 0.957 (no cost over body); about 46,000 bits | Q6702 |
| v2 (`voynichizzatore/v2.py`) | v1 channel in the e288 body | 0.831 / 0.933 with message | Q6756 |
| v3 | k/t choice model also knows the line position | bench 0.817 / 0.934, scorecard 52/54 | Q6831 |
| v4, v5 | bound line edges and line choices (v4); + 20% base words from the global lexicon (v5) | v5 bench 0.816 / 0.917, scorecard 49/54, extended 57/78; line gate lost | Q7008 |
| v6 | stronger repetition penalty | not confirmed (0.827 / 0.936) | Q7079 |
| v7 | p/f in first lines | registered, **never benched** | DIA L20–22 |
| v8 (e406) | "generator by pieces" (*a pezzi*): page bag (section lexicon + borrowed character + invented words) + learned arrangement; old channel | bench 0.604 / 0.715, scorecard 41/54 | Q8111, Q8188 |
| v9 (e407) | joins, last→first glyph link, vertical term | bench 0.668 / 0.719 (old channel damages it) | Q8560, Q8630 |
| **v10** (e408 + e409) | **message in the bag** (word counts); ending-ending link weight | bench 0.550 / 0.662; 12k 0.572 / 0.690 | Q8837, Q9152, Q10704 |
| v11 (e410) | line-gate terms (first glyph, distance-2, choices) | 12k 0.579 / 0.634, gate 9/12 | Q9443, Q10704 |
| v12 (e412) | two halves of the page made different | 12k 0.576 / 0.619, gate 11/12 | Q10340, Q10518 |
| v13 (e413) | κ and γ refitted on the full bag | 12k 0.582 / 0.605 | Q13920 |
| v14 (e414) | joins accepted only with a probable junction | keys 1–12 0.566 / 0.591; fresh 13–24 0.584 / 0.609; 24k 0.575 / 0.600 | Q14020, Q14118 |
| v15 | scrypt + SHAKE-256 + HMAC | 12k 0.570 / 0.601 | Q15213 |
| v16 | layout of another real page | 12k 0.564 / 0.598 | Q15213 |
| v17 | statistical layout; **first public release** (MIT, 4/10 about 10:45) | 12k 0.563 / 0.601, gate 11/12; 24k 0.559 / 0.597, gate 18/24 | Q15213, Q15879; DIA L714 |
| v18, v19 (e416, e416b) | line-width term (power law; 11-node curve) | gate 8/12 and 4/12 → not adopted; parameter files only | Q15688 |
| v20 (e417) | v19 + `distanza2` retuned to 0.30 | 12k 0.554 / 0.599; 24k 0.560 / 0.607, gate 24/24 | Q15841, Q15879 |
| **v21** (e418) | `conti_iniziali` fix, same weights | **24k 0.554 ± 0.004 / 0.601 ± 0.005**, scorecard 16.0, extended 5.4, gate 24/24 | Q15905 |

- **Compatibility.** v21 reads v17 and v20 manuscripts, because the word counts are identical in the three versions
  (README L76–78; SW §13 L253–255).

---

## 4. Evaluation

### 4.1 The two judges

- **e231** (`preregistrazioni/e231.md`; `esperimenti/e231_discriminatore.py`):
  - L2 logistic regression (C = 1) after standardisation fitted inside each fold;
  - 10-fold cross-validation with `StratifiedGroupKFold`, so that a real page and the generated page with the same
    folio name always share a fold;
  - repeated with seeds 231–235; AUC of the out-of-fold probabilities, averaged over the seeds (`L128–144`).
- **Unit.** A page with at least 40 clean words. There are 202 real/generated pairs (`risultati/e231_discriminatore.json`).
- **The classifier is retrained for every generated book.** It is a two-sample classifier test (Lopez-Paz and Oquab
  2017 is listed as the precedent to cite in `white_paper/revisione/PIANO_V2.md` L42–47), not a fixed pre-trained
  detector.
- **Interpretation thresholds** (e231 prereg L47–52):
  - 0.5 = guessing, 1 = never wrong;
  - **≤ 0.6 "indistinguishable"**, **≥ 0.7 "distinguishable"**, in between "partially distinguishable".
- **e231 features: 209**, in groups G1–G5 (`e231_discriminatore.py:L73–125`):

  | group | content | features |
  |---|---|---|
  | G1 | frequencies of the 30 most frequent Voynich glyphs | 30 |
  | G2 | frequencies of the 150 most frequent glyph pairs inside words | 150 |
  | G3 | mean and standard deviation of word length; types per token in the page; share unique in the page; share unique in the *own* text; share in the own top 100 | 6 |
  | G4 | first glyph of lines (10), last glyph of lines (10), similarity of neighbours, share of neighbour pairs whose join is attested in the own text | 22 |
  | G5 | vertical similarity: same-index word in the line above minus the other words of that line, inner words only | 1 |

  No feature tests membership of the Voynich vocabulary (prereg L30).
- **e266 = e231 + 19 features = 228** (`preregistrazioni/e266.md`; `e266_discriminatore_forte.py:L72–106`):

  | group | content | features |
  |---|---|---|
  | G6 | pairs seen elsewhere in the own text; identical neighbours; similarity at distance 2 | 3 |
  | G7 | mean length of the first, second and last word of lines; share of first words in y/d/s; last words in m/n/l/r/y | 9 |
  | G8 | p, f, t, k excess in the first lines of paragraphs; word length in first lines | 5 |
  | G9 | Jensen–Shannon distance of the page's glyphs from the book's; JSD between the two halves of the page | 2 |

- **Controls:**
  - Currier A vs B pages: 1.000 for both judges;
  - random labels: 0.527 (e231) and 0.519 (e266) (Q4950; Q5967).
  - Reference generators: e192 0.970 / 0.985; e241 0.874 / 0.937.
- **"Bag only" judge** (e402, Q7720–7723): the e266 judge restricted to G1, G2, G3 and the page-to-book JSD. v21 scores
  0.552 (keys 1–12) and 0.543 (keys 13–24) (R-v21).

### 4.2 The scorecard ("pagella", 18 properties)

- **Origin.** 17 properties from e61 (`esperimenti/e61_pagella.py:L75–94`), whose bands were "chosen after seeing the
  results" of the earlier experiments (docstring L4–5; Q660–663). The 18th is the line edge from e78/e71 (Q1096),
  added in `e224.valuta` (`e224_generatore_completo.py:L190–201`).
- **How it is measured** (`e106.misura`, `RIGHE_PAGINA = 29`):
  - on the whole generated book, cut into pseudo-pages of 29 lines;
  - each value is compared with a Voynich reference value.
- **Raw values in the table below** are the Voynich reference and the v21 mean over 24 keys **[compiler, from R-v21
  JSON `valori`/`valori_Voynich`]**.

| # | property (raw measure) | passes if | Voynich ref | v21 mean |
|---|---|---|---|---|
| 1 | h2, conditional entropy of the next glyph | ±0.15 | 2.236 | 2.284 |
| 2 | space predictability (`spazio_spiegato`) | ±0.08 | 0.664 | 0.639 |
| 3 | hapax share (`hapax_34000`) | ±0.08 | 0.678 | 0.738 |
| 4 | types/tokens, whole text | ±0.04 | 0.210 | 0.205 |
| 5 | repetition: identical word after itself, relative to the line (`identiche_vs_riga`) | ±0.2 | 1.009 | 0.943 |
| 6 | homogeneity: within-line similarity | ±0.008 | 0.0385 | 0.0414 (missed 1/24) |
| 7 | gradient: similarity at 6 lines / within-line similarity | 0.70–0.97 | ref 0.0335 / 0.0385 | 0.0255 / 0.0414 (missed 24/24) |
| 8 | link: last glyph → first glyph (`confine`) | ±0.05 | 0.188 | 0.180 |
| 9 | attested joins / chance | 1.5–2.5 | 0.0877 / 0.0446 | 0.0795 / 0.0373 |
| 10 | flat curve: hapax at 1,000 − hapax at 34,000 | ≤ 0.10 | 0.057 | −0.024 |
| 11 | drift: vocabulary turnover between near and far blocks | ≥ 0.05 | 0.106 | 0.095 |
| 12 | page profile V3: R in 0.8–1.25 and share within 0.5×–1.5× | both | R 1.017, share 0.0605 | R 0.656, share 0.041 (missed 24/24) |
| 13 | autocorrelation of neighbouring word lengths | ≥ 0.08 | 0.150 | 0.142 |
| 14 | Zipf slope | ±0.10 | −1.041 | −1.005 |
| 15 | word shape V8: glyphs at first, second, second-last, last position vs the A–B distance | ≤ 1.0 | 0 | 0.040 |
| 16 | vertical: same position in the line above | ≥ 1.015 | 1.028 | 1.035 |
| 17 | formulas: 2–3 word sequences recurring ≥ 10 pages apart | 0.5×–1.5× | 5.195 | 4.576 |
| 18 | line edge: JSD ratios at line start and end (e71) | 0.5×–2× of Voynich | not stored in the JSON (e78 gives the end value as 55.5, PROG L134) | start 23.6, end 54.5 |

- **Only 17 properties are attainable.**
  - Measured with this very procedure, the real Voynich has gradient 0.0262 / 0.0385 = **0.683** and fails the 0.70
    band. The reference 0.0335 comes from a different page division.
  - The Voynich scores 17/18 (e411, Q10092; e400 V row = 17.0/18).
  - Other references that differ slightly from direct measurement: page profile R 1.017 → 1.059; formulas 5.20 → 6.39
    (Q10094).
- **v21 scorecard:** 16.0 (24 keys; 23 keys at 16 and one at 15). It misses the gradient and the page profile always,
  and homogeneity once **[compiler, R-v21 JSON]**.

### 4.3 The eight extra properties ("materie aggiunte", e293)

- **Defined in** `esperimenti/e293_banco.py:L26–28, L52–83` and preregistration e293 (Q6831–6837).
- **Control.** The Voynich passes all 8.
- **Columns:** pass rule; Voynich value; v21 mean over 24 keys; keys that miss it.

| property | measure | passes if | Voynich | v21 mean | v21 missed (of 24) |
|---|---|---|---|---|---|
| rare words per page | e211 R, herbal pages | R ≤ 5 | 1.96 | 2.87 | 1 |
| types/tokens within the page | — | ±0.03 | 0.756 | 0.763 | 0 |
| words unique within the page | — | ±0.04 | 0.636 | 0.642 | 0 |
| spread of word lengths (page standard deviation) | — | ±0.04 | 1.579 | 1.627 | 20 |
| first lines as a register of their own | e273 z | > 3 | 4.72 | 2.26 | 18 |
| spelling choices by line | e206b classes with z > 3 | ≥ 10 of 12 | 12 | 7.8 | 23 |
| agreement of word endings | e285c excess | ±0.012 | 0.0433 | 0.0454 | 0 |
| pairs seen elsewhere | — | ±0.02 | 0.2213 | 0.2287 | 1 |

- v21 values and miss counts are **[compiler, R-v21 JSON]**. Summary: 5.5 (keys 1–12) and 5.2 (keys 13–24) (R-v21 md).
- The README states "5 to 6".

### 4.4 The line gate ("cancello della riga")

- **Rule.** Defined in `e224.valuta` (`L200`). The gate passes only if all five conditions hold:
  1. **S1 ≤ 0.7**: a line rarely starts with the first glyph of the line above (e82, e83);
  2. **R_riga < 0.1**: the junction link across a line break, relative to the link inside the line (e74);
  3. **A ≥ 1.0**: similarity at distance 2 / similarity at distance 1, inner words (e110);
  4. **at least 3 of the 5 spelling choices** have per-line variance excess with z > 3 (e135);
  5. **correlation between consecutive lines within 0.207 ± 0.07** (e146; `e145.VOY_R1`).
- **Voynich values:** S1 0.531, A 1.047, r 0.207 (Q9474).
- **v21 over 24 keys:** passes 24/24. Means: S1 0.515, R_riga 0.007, A 1.028, choices 4.9, r 0.190 **[compiler]**.

### 4.5 v21 headline results

- **Text measured.** Isidore XVII, 38,304 bits. Keys "e409-1" … "e409-24".
- **Selection vs fresh keys.** Keys 1–12 were also used to choose between variants during development; keys 13–24
  never were (HOW, "How close it is"; rule "confirm every new version on fresh keys before citing it": DIA L871).

| measure | keys 1–12 | keys 13–24 (fresh) | all 24 |
|---|---|---|---|
| AUC e231 | 0.554 ± 0.006 | 0.554 ± 0.005 | **0.554 ± 0.004** (range 0.517–0.580) |
| AUC e266 | 0.596 ± 0.008 | 0.606 ± 0.006 | **0.601 ± 0.005** (range 0.551–0.632) |
| keys with e266 > 0.60 | 6 | 8 | 14 |
| scorecard (17 attainable) | 16.0 | 15.9 | 16.0 |
| extra properties (of 8) | 5.5 | 5.2 | 5.4 |
| line gate | 12/12 | 12/12 | 24/24 |
| exact read-back; wrong key rejected | 12; 12 | 12; 12 | 24; 24 |

- **Sources.** R-v21 md files and Q15921–15929. Means and standard errors were re-derived **[compiler]** from the
  per-key lists and match.
- **e266 per-group AUC, keys 1–12:** G1 0.49, G2 0.54, G3 0.60, G4 0.56, G5 0.54, G6 0.53, G7 0.56, G8 0.62, G9 0.47.
  - G8 (first lines of paragraphs) is the group the judge sees best (R-v21 md).
- **Heaviest e266 features** (first key; HOW, "The two judges"):
  - pairs seen elsewhere (0.236 vs 0.224);
  - attested joins (0.084 vs 0.092);
  - glyph pairs l+ch, d+y, r+ch;
  - lines starting with t;
  - words unique in the text (0.154 vs 0.145).
- **Line widths** (keys 1–12): lines wider than 1.25 × the page median are 11.6% (Voynich 6.0%); wider than 1.5 ×,
  2.8% (Voynich 2.9%) (Q15931).
- **Copying from the Voynich.** About 0.4–0.5% of the word trigrams of a v21 book also occur in the Voynich
  **[compiler, R-v21 JSON `trigrammi_dal_Voynich`]**. e406 gave 0.7–1.1% for v8 (Q8118–8120).
- **Published wording** (README L43–58):
  - judge 1 "0.55 ± 0.01", judge 2 "0.60 ± 0.01";
  - scorecard 16; extra properties "5 to 6";
  - "A manuscript with a message and one without cannot be told apart by these measures."

### 4.6 Message vs no message (e409, e409b)

- **Test design** (`preregistrazioni/e409.md` L42–55, L77–84). Same channel and keys:
  - (a) Isidore hidden in the bag;
  - (b) filler bits only;
  - (c) the old spelling-choice channel.
- **Results with 12 keys** (keys 1–4 in e409, 5–12 in e409b; Q8999–9019; `risultati/e409b_messaggio_nel_sacco_chiavi_5_12.md`):

  | case | e231 | e266 |
  |---|---|---|
  | (a) message | 0.560 (s.d. 0.023) | 0.682 (s.d. 0.026) |
  | (b) filler only | 0.547 (s.d. 0.026) | 0.671 (s.d. 0.032) |
  | **difference (a) − (b)** | **+0.013 (s.e. 0.010)** | **+0.011 (s.e. 0.012)** |

  - The difference is within the 0.02 predicted.
  - Exact read-back 12/12; wrong key rejected 12/12.
  - The first 4 keys alone had shown 0.037 / 0.042, judged to be key-to-key noise.
- **Comparison with the old channel** (4 keys): it scored 0.677 / 0.737 against 0.560 / 0.697 for (a); it lost the
  "link" property in 4/4 (Q8850–8858).
- **Earlier evidence** (e400 N1, Q7319, Q7334–7337): the old channel alone, on the *real* Voynich, already gave
  0.622 / 0.630, because it rewrites 51.7% of the words.
- **Caveat (important for the paper).** The (a)-vs-(b) comparison was run **only on the v9 body with the pre-v15
  cipher** (SHA-256-seeded Mersenne Twister keystream; `e409b_..._5_12.md` L3 "Corpo di partenza: v9").
  - All later replications (v10–v21) ran case (a) only (`CASI=a`; R-v21 md has no (b) row).
  - For v21 the claim rests on the construction argument (§2.7) plus the v9-era measurement. **It was not re-measured
    on v21.**
- **Framing requested by Davide for the white papers** (DIA L639–657):
  - a book with and a book without a message are indistinguishable by the project's measures, "the same situation as
    the real Voynich";
  - therefore these statistics alone cannot decide whether the Voynich has meaning.
  - Cautions to state together with it:
    - it holds only for these judges and this scorecard;
    - the generated book is recognisable as generated;
    - the capacity is far below that of plain text.

### 4.7 Reference points from the control ladder (e400, Q7302–7346)

These are e231 / e266 AUCs for real-Voynich texts with one level broken:

| text | AUC e231 / e266 |
|---|---|
| Voynich unchanged | 0.500 / 0.500 |
| **lines shuffled within each page** | **0.481 / 0.595** |
| words shuffled within each line | 0.984 / 0.990 |
| words shuffled within each page | 0.989 / 0.998 |
| words redrawn from section × language | 0.998 / 1.000 |

- The strong judge's effective floor for anything without the real line order is therefore about 0.60. v21's 0.601
  equals "the real Voynich with its lines shuffled" **[compiler's reading]**.
- **Real bag + learned arrangement** (e401b): 0.533 / 0.659 (Q7625).

### 4.8 What the evaluation does not establish (declared in the project)

- **The judges and the scorecard are the project's own.** The model weights were tuned ("on the panel", seed 11) on
  statistics that are also judge features. Keys 1–12 were used for selection. An **independently built judge has
  never been tried** (Q10435–10437; README L65; HOW, "Known limits").
- **Not "indistinguishable from the Voynich".** Judge 2 is above 0.60 for 14 of 24 keys, and several properties are
  never reproduced (README L60–67; SW §8).
- **Recognisable as the program's output.** Almost all words are Voynich words, so a book is recognisable as made with
  the program. What cannot be told is whether a message is inside (README L66–67).

---

## 5. Security caveats stated in the project

- **No expert review.** "Standard building blocks, but the whole has not been reviewed by an expert: do not use it for
  real secrets" (README L71–74; SW §8 L117–118; Q15238).
- **Fixed scrypt salt.** A dictionary of guessed keys can be precomputed once and tried on every book (HOW,
  "Security"; SW §13 L221–223).
- **scrypt cost.** n = 2^15, r = 8, p = 1. Raising the cost is noted as a possible future version (DIA L872–874).
- **Key advice.** Use at least 6 random words or 12 random characters. A common word falls quickly to brute force
  (DIA L873; SW §13 L227–228).
- **No nonce.** The keystream depends only on the key, so two books with the same key share a keystream. Use a
  different key per message (HOW, "Security"; SW §13 L221–223).
- **What is hidden.** The program hides *that there is a message*, not that the program was used (HOW, "Security").
- **Integrity.** The tag is 64 bits, so a wrong key passes it with probability 2^-64 (HOW, "Reading back").
- **Before v15** the encryption was a SHA-256-seeded Python PRNG with no authentication: "non è crittografia robusta"
  (PUB §4 item 5).
- **Floating point.** Writing and reading must use the same program version (README L75–79).
- **[compiler, unverified, not in project documents].** HOW states that recovering the bits needs the key, because the
  page distributions depend on it. However, the only key-dependent input to a page's distribution is the choice of
  the character page q from a public, finite set (pages of the same type with ≥ 40 known words). An attacker might
  rank candidate q by likelihood of the observed counts. That would not break the encryption, but it is relevant to
  the "same key → same keystream" caveat and deserves analysis before any security claim.

---

## 6. Public artefacts

- **Public repository:** https://github.com/AndreottiVIII/voynichizzatore
  - Licence: MIT, "Copyright (c) 2026 Davide Caniatti" (`LICENSE`).
  - The Voynich text is CC0 (README L96–99). Code comments are in Italian.
  - First public commit `86193ef` (v17, 4/10/2026); then `7a802d3` (English texts), `c08394b` (pdf command), `9771a83`
    (font 1.1), `182056e` (binary font fix), `261e175` (v20).
  - **v21 = commit `4b1383c`** ("v21: fix a defect in the arrangement…", 4 Oct 2026 17:35 +0200).
  - Later commits add the website in `docs/`; latest seen: `33b48a2` "README: link to the website".
  - **No git tags exist** (`git tag` is empty).
- **Website:** https://andreottiviii.github.io/voynichizzatore/ (GitHub Pages, branch `gh-pages`; SW §14).
  - Pages: Write, Read, How it works, Research, About.
  - Runs v21 in the browser (`docs/engine/v21/`, files listed with SHA-256 in `manifest.json`), using Pyodide 314.0.7
    and `@noble/hashes` 2.4.0 for scrypt.
  - The Research page carries the white-paper PDF under CC BY 4.0 (SW §14 L277–282).
- **Private side.**
  - The package is built by `strumenti/costruisci_pubblico.py` → `pubblico/voynichizzatore/` (DIA L723–724).
  - v21 results commit in the private repo: `4d72cbb` (e418). Package update: `77a425c`.
- **Read-back test file:** `prova.py` with `prova/manoscritto_di_prova.txt`, key "read-back test on another computer".

---

## 7. Limitations and open problems (as stated)

1. **Strong judge at the threshold.** e266 is 0.601 ± 0.005 over 24 keys; 0.606 on the fresh keys (Q15905; HOW).
2. **Never reproduced:**
   - page profile (V3 R about 0.66 vs a 0.8–1.25 band; missed 24/24);
   - spelling choices by line on 12 classes (7.8 of 12 vs ≥ 10; missed 23/24).

   Often missed:
   - first lines as a register (18/24);
   - spread of word lengths (20/24).

   The gradient is a defective band (Q10704–10728; R-v21).
3. **Lines too wide.** 11.6% of lines exceed 1.25 × the median (Voynich 6.0%). Closing this would require deciding the
   words per line after choosing the words (DIA L850–851; Q15873).
4. **Two research findings not reproduced as such:**
   - **Vertical copy.** It is modelled as same-index similarity (weight 0.152). Research found copying by *physical*
     position (e228/e228b, Q4913–4940) and the "same column" effect mostly vanishing without line edges (e340,
     Q7929–7931). [compiler: modelling choice worth stating]
   - **Session (bifolio) effects** (e350, Q8090–8091). These are not modelled; pages are generated independently in
     manuscript order.
5. **Scope.**
   - Running paragraph text only: no labels, circular or radial text.
   - Hands are not modelled.
   - The illustrated book uses real drawings; the font has one fixed shape per glyph (HOW, "Known limits"; DIA L753–755).
6. **Not reviewed or not repeated:**
   - read-back on a second computer;
   - cryptographic review;
   - an independent judge;
   - message-vs-filler (a)/(b) comparison on v21 (§4.6) (DIA L904; PUB §9; README L79).
7. **Failed ideas, declared:**
   - page character by position in the word (e411 H1);
   - neighbourhood between lines (H2);
   - negative exact-pair weight alone (e412 M1);
   - unions filtered by presence only (e413 S1);
   - joint κ/γ on three targets (e414 J2);
   - line-width terms without retuning (v18, v19).
8. **Wording rules for publication** (SW §8 L101–119):
   - never "indistinguishable from the Voynich";
   - never "deciphered";
   - say "made to be indistinguishable" (goal) and "our measures can hardly tell it apart" (result) (SW §13 L239–241).

---

## 8. Ambiguities and items not found

- **Capacity range.** The README says "about 80,000 and 85,000 bits". The 24 v21 measurement keys range from 81,116 to
  85,905; the website test keys (v20) from 80,344 to 84,678. Use a measured range with its source.
- **The name "v2"** refers to two different programs: `analisi/voynichizzatore.py` (PROG §2) and
  `voynichizzatore/v2.py` (Q6756).
- **v7** is in the registry but was never benched.
- **v18 and v19** exist only as parameter files and are not in `versioni.py`.
- **Message vs filler.** Measured only for v9 with the old cipher (§4.6).
- **Bench vs replication numbers.** Bench numbers (3 keys) for v10–v12 are optimistic compared with the 12-key
  replications (Q10718–10720). v14 and v20 also looked better on keys 1–12 than on fresh keys (Q14129; Q15898). Only
  the 24-key figures should be cited.
- **The current white paper is out of date.** `white_paper/en/sezioni/04_discussione.tex` L48–56 still describes the v1
  channel (0.8 bit per choice, 46,000 bits). `VERIFICA_NOTE_REVISORE.md` L48 flags this for rewriting.
- **"About 2.7 bits per known word"** (HOW) was not recomputed here: the known-word count per book is not stored in
  the result JSON.
- **Line-edge Voynich reference.** The Voynich reference values of the 18th scorecard property are not in the R-v21
  JSON (`valori_Voynich` lacks them). Only "55.5" for the line end appears, in PROG L134.
- **Not found:**
  - a scrypt or HMAC test-vector check on the Python side (the site checks RFC 7914 in the browser, HOW);
  - any measurement of the old-channel capacity for v8–v9 specifically;
  - a public tag or release object for v21.
