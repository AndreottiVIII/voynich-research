# Research experiment log: summary

Generated on 2026-10-08 from the `voynich` repository (read only; QUADERNO snapshot up to the 4/10/2026 entries). Full log: `registro.csv`, one row per experiment id, **715 rows** (707 compiled up to e3c83, plus e3c84–e3c91 added by hand on 8/10/2026).

## Scope and definitions

- **Included:** e01–e399 (including suffixed ids such as e112b, e163b, e212c, e300b) and the series e3a01–e3a99, e3b01–e3b99, e3c01–e3c83. **Excluded:** e400 and above (the "voynichizzatore" generator project) and QUADERNO entries titled "vz:". The e3a/e3b/e3c series exist because numbers from 400 up were taken by the generator project.
- **Rows:** every id with any trace (preregistration, code, results, provenance record, QUADERNO entry), plus ids planned in `STATO_LAVORI.md`/`DECISIONI.md` but never run (e29, e215, e254, e267, e282, e284: NOT_RUN).
- **Tested claim:** the affirmative answer to the preregistered question (usually the preregistration title). `question_en` is phrased as a yes/no question whose "yes" is that claim, so the class must be read together with it (for example, a control experiment asking "is effect X due to paragraphs?" is REFUTED when the answer is no).
- **Classes:** CONFIRMED = yes; REFUTED = no; MIXED = preregistered label "in part", or sub-criteria in opposite directions; NULL/INCONCLUSIVE = "uncertain", insufficient data, or test invalid because preregistered validity checks (controls) failed; DESCRIPTIVE = no yes/no criterion (descriptive preregistration, or not preregistered); NOT_RUN = planned or preregistered but not executed, abandoned, or stopped before results; SUPERSEDED = the preregistered outcome or the headline conclusion was later withdrawn or reversed by a later experiment or notebook entry (the original class is in `notes` as `orig=`). Later work that only narrows or reinterprets a result is noted as "qualified by" and the class is kept. UNKNOWN = could not be determined (none).
- **Post-hoc overrides:** where the author overrode a preregistered label after the run (for example, a criterion "phrased too sharply"), `outcome_class` follows the **literal preregistered label**. `deviation` is "yes", and the author's later reading is given in `deviation`/`notes`.
- **e01–e28** are the work imported from the previous repository (tag `origine`, commit `ee2a23d`). They were **not preregistered** and were re-run here as a replication check. They are classed DESCRIPTIVE except e08 (calibration failed: NULL/INCONCLUSIVE) and e16 (method invalid, superseded by e17). Their date is the import date.
- **Date:** the date written in the preregistration ("Scritta il …"); otherwise the first commit of the preregistration, the planning document, or the first commit of code/results (the source is noted in `notes`).
- `outcome_text_it` is copied verbatim (only markdown marks removed) from the QUADERNO, the results file or the document given in `notes` (`src:`); an automatic check confirmed every phrase is present in the sources.
- **Method:** a script extracted, for each id, the preregistration, the QUADERNO entries (own and later mentions, including corrections) and the results headers. Twelve parallel classification passes followed written rules and were validated by script (ids, classes, verbatim text). A final cross-batch review harmonised the SUPERSEDED and post-hoc decisions (rows marked "reviewed in the final cross-batch review").

## Counts by outcome class

| class | all rows | preregistered only |
|---|---|---|
| CONFIRMED | 166 | 166 |
| REFUTED | 259 | 259 |
| MIXED | 68 | 68 |
| NULL/INCONCLUSIVE | 71 | 70 |
| NOT_RUN | 18 | 3 |
| DESCRIPTIVE | 56 | 27 |
| SUPERSEDED | 69 | 68 |
| UNKNOWN | 0 | 0 |
| **total** | **707** | **661** |

- Experiments actually run (all classes except NOT_RUN): **689**; with a preregistration: 658.
- Original class of the 69 SUPERSEDED experiments: CONFIRMED 41, DESCRIPTIVE 3, MIXED 9, NULL/INCONCLUSIVE 3, REFUTED 13. Of these, 4 were superseded only because of a method error, and the corrected rerun upheld the conclusion (UPHELD: e154, e3a26, e3a27, e3b27).

## Counts by series

| series | CONFIRMED | REFUTED | MIXED | NULL/INCONCLUSIVE | NOT_RUN | DESCRIPTIVE | SUPERSEDED | UNKNOWN | total |
|---|---|---|---|---|---|---|---|---|---|
| e01-e99 | 20 | 25 | 8 | 9 | 2 | 32 | 2 | 0 | 98 |
| e100-e199 | 10 | 61 | 9 | 18 | 2 | 3 | 9 | 0 | 112 |
| e200-e299 | 18 | 66 | 4 | 5 | 7 | 6 | 9 | 0 | 115 |
| e300-e399 | 37 | 26 | 15 | 13 | 1 | 7 | 2 | 0 | 101 |
| e3a | 43 | 24 | 12 | 2 | 2 | 4 | 12 | 0 | 99 |
| e3b | 22 | 22 | 12 | 12 | 1 | 1 | 29 | 0 | 99 |
| e3c | 16 | 35 | 8 | 12 | 3 | 3 | 6 | 0 | 83 |
| **all** | 166 | 259 | 68 | 71 | 18 | 56 | 69 | 0 | 707 |

## Deviations from the preregistration

Experiments with a declared deviation: **80**. Of these, 19 are post-hoc overrides of a preregistered label or criterion (listed in the next section); the others are mostly code errors found and rerun, controls or nulls found defective after the run, or thresholds/measures adjusted.

- **e36** (REFUTED): D-007, preregistered positive control found defective in a code test (Voynich numbers seen); corrected version added before official run, both reported
- **e37** (MIXED): minor, page threshold (>=10 useful words) fixed after prereg, declared before the run
- **e39** (CONFIRMED): two preregistered controls (Isidore XVII, Columella XII) dropped as too short
- **e48** (REFUTED): first run failed (parallel e47 run recompiled the generator classes); rerun alone, method unchanged
- **e53** (MIXED): criterion declared ill-chosen after the run (one-sided thresholds let bond excess 0.30-0.36 pass); two-sided bands adopted from e56
- **e68** (MIXED): D-011, generator blocked at eta=1; filter excluded for line-initial words and all eta values rerun
- **e72** (CONFIRMED): validity bound pi_A,s missed (0.342 < 0.35) but start side read, weights taken as lower bounds
- **e76** (CONFIRMED): first run had 'within'/'across' labels swapped (R inverted); fixed in a separate commit and rerun
- **e78** (CONFIRMED): D-013, drift measured at the maximum available distance for short texts (technical block)
- **e82** (CONFIRMED): first null paired a line with itself and the negative control failed (z −3.2); null fixed (D-014) and rerun with the same criteria
- **e85** (SUPERSEDED): unforeseen design confound (parity of 2nd/last paragraph line) found after running; exploratory control removed the effect
- **e93** (MIXED): preregistered reading reversed by judgement using an unplanned last-word comparison (same drop, 1.24)
- **e105** (REFUTED): design defect declared after running (unconditional null uninformative for 2 candidates; only conditional version used)
- **e111** (REFUTED): meter reading declared ill-posed after running (true verses fail it); criterion found non-discriminating
- **e115** (REFUTED): tercile null found invalid after running (removes order in languages too); only the within-line null used
- **e117** (NULL/INCONCLUSIVE): design defect found after running (fill measure saturated in all texts, languages included)
- **e123b** (REFUTED): phase-index criterion found unstable near zero deficit after running (outcome unaffected)
- **e127** (REFUTED): two failed runs of part 2 (rare OCR characters; drift on short text) fixed and rerun; part 1 identical
- **e130** (MIXED): page bootstrap found to distort MI-based intervals after running (agreement/closure intervals ignored; criterion measures little affected)
- **e133** (MIXED): Part 1 rule ('reggono', 7/10 coherent) declared ill-posed after running (6 of 7 coherent words occur once)
- **e134** (REFUTED): first run stopped by a table-formatting error after computation, fixed (ef24971) and rerun with identical results; in-line agreement criterion found non-discriminating in 29-line-block format
- **e137** (SUPERSEDED): single-chain null found defective after running (ignored section/hand heterogeneity); rule outcome 'yes' not accepted
- **e154** (SUPERSEDED): measure (I) recognised after running as not independent of vocabulary
- **e156** (NULL/INCONCLUSIVE): positive control found ill-designed after running (A compared with itself rewritten)
- **e163** (NULL/INCONCLUSIVE): first run crashed on page fRos (no folio number), fixed and rerun (QUADERNO l.3653); random-key null judged after running not to account for key adaptation
- **e171** (REFUTED): bootstrap interval found biased upward after running (central estimate 0.75 outside it); prudent reading 'at most partial weakening ~25%'
- **e173** (SUPERSEDED): line-length confound found by exploratory check after running; rule outcome not accepted pending e173b
- **e177** (NULL/INCONCLUSIVE): first run stopped when saving JSON (numpy values), fixed in separate commit and rerun with identical values
- **e184** (REFUTED): colour mask found after running to include parchment tones; outcome limited to 'not with these measures'
- **e191** (SUPERSEDED): rule outcome not accepted by judgement in the same entry (low power: 70% Huffman control z 0.4; gain attributed to within-word links)
- **e193** (DESCRIPTIVE): two execution fixes in separate commits (blocks taken from all ZL loci; f57v sequence taken from the ring line per prereg)
- **e195** (SUPERSEDED): rule outcome 'spazi spuri' not accepted after the run (exploratory length stratification removes it); decision deferred to the preregistered e195b
- **e212b** (SUPERSEDED): controls found defective after the run (positive not deciphered for Hindi/Burmese; Finnish negative control was Finnish itself)
- **e212c** (REFUTED): stopped halfway by Davide's decision; partial values read from the log, no results file; Burmese not run
- **e227** (MIXED): a quick code test computed Voynich values before the prereg commit (declared; prereg text untouched)
- **e248** (REFUTED): declared defect — uniqueness of the gallows-stripped body computed on the whole word; outcome unaffected
- **e256** (REFUTED): declared defect — oscillation measure is 0 by construction (non-informative)
- **e259** (DESCRIPTIVE): operationalization of 'much more' (≥2× reduction) fixed while writing the code, before results (declared)
- **e278** (REFUTED): declared defect — reference group 4.5× larger, comparison not size-matched (e278b suggested)
- **e279b** (NULL/INCONCLUSIVE): positive control built wrongly (message misaligned with 5-bit groups); declared author error, redone as e279c
- **e320** (REFUTED): secondary one-edit measure found invalid after running (author's error); decision uses the exact measure as preregistered
- **e321** (MIXED): (a) result in a direction the criterion did not foresee (z +8.2), labelled 'incerto' by judgement
- **e346** (SUPERSEDED): first run stopped for slowness, code optimized (same method); 'in between' outcome not among prereg labels; unequal units and split-word texts declared after running
- **e354** (REFUTED): validity criterion on the positive control added after the result, as a reading
- **e356** (MIXED): part (c) intermediate case (1 of 5 choices) not defined in prereg; labelled 'in parte'
- **e374** (CONFIRMED): threshold declared badly calibrated (z only, not effect size), outcome kept; meaningful-text tokenization bug found later, redone in e381
- **e375** (NULL/INCONCLUSIVE): positive-control texts had split words (tokenization bug) found after running; redone in e381, control holds
- **e377** (REFUTED): tokenization bug in the meaningful-text reference found after running; redone in e381, outcome unchanged
- **e384** (CONFIRMED): author declared the criterion badly chosen (range set by small noisy texts) and reads the opposite
- **e3a26** (SUPERSEDED): null found defective after running (e3a31); z recomputed with a corrected null in e3a33
- **e3a27** (SUPERSEDED): same defective null as e3a26 (found in e3a31); z recomputed in e3a33
- **e3a28** (SUPERSEDED): null found biased for inner columns after running; redone in e3a29
- **e3a31** (SUPERSEDED): null found defective after running (declared in the same entry); redone in e3a33
- **e3a46** (SUPERSEDED): author declared the preregistered measure diluted after running
- **e3a58** (CONFIRMED): threshold changed from max to 90th pct of languages after control-only code test, before seeing the Voynich (declared in the prereg)
- **e3a66** (REFUTED): first run stopped on a code error in the descriptive table before any result; fixed and rerun without other changes
- **e3a89** (MIXED): pair threshold lowered 2,000→500 after a control-only code test, before new Voynich data (declared in the prereg)
- **e3a90** (MIXED): rule defect declared (ratio meaningless when excesses are ~0); Naibbe's literal 'like the Voynich' overridden by judgement
- **e3a99** (REFUTED): method bias (leave-one-out counts push negative) found after running; calibration not foreseen, done in e3b01
- **e3b01** (SUPERSEDED): null found limited after running (ignores page/hand spacing propensity); redone in e3b02
- **e3b07** (SUPERSEDED): criterion defect declared after running (removing similar pairs lowers all agreement; comparison should be near minus far)
- **e3b27** (SUPERSEDED): control found unfair after running (last lines are shorter), outcome reported only 'alla lettera'; redone in e3b28
- **e3b33** (REFUTED): half-life criterion declared fragile after running (B missed the threshold by 0.0002); follow-up contrast in e3b34
- **e3b41** (SUPERSEDED): bootstrap resampled paragraphs, not pages as preregistered (declared, QUADERNO l.12434)
- **e3b42** (SUPERSEDED): bootstrap resampled paragraphs, not pages as preregistered (declared, QUADERNO l.12434)
- **e3b51** (SUPERSEDED): absolute comparison judged unfair after the result; whole-word similar-pair exclusion later found biased (QUADERNO l.12734)
- **e3b52** (SUPERSEDED): whole-word similar-pair exclusion later found to bias the measure (QUADERNO l.12734)
- **e3b53** (SUPERSEDED): whole-word similar-pair exclusion later found to bias the measure (QUADERNO l.12734)
- **e3b54** (SUPERSEDED): whole-word similar-pair exclusion found biased after running; redone as e3b56 (QUADERNO l.12734)
- **e3b59** (SUPERSEDED): null found much less sensitive in hand 1 after the result (QUADERNO l.12910)
- **e3b60** (SUPERSEDED): null found much less sensitive in hand 1 after the result (QUADERNO l.12910)
- **e3b64** (CONFIRMED): first execution had a code error (out-of-class words broke pairs); corrected and rerun (QUADERNO l.12994)
- **e3b65** (REFUTED): author judges the rule's label 'neighbouring lines similar, not memory' to reflect low power instead
- **e3b75** (SUPERSEDED): prereg did not foresee an interval entirely below 0 (effect -0.090); declared and described as alternation
- **e3b98** (SUPERSEDED): first run stopped on Esperanto (R undefined, not handled); code fixed, retested on fake texts and rerun (declared error)
- **e3c06** (SUPERSEDED): prereg did not foresee an interval entirely below 0; declared
- **e3c21** (NULL/INCONCLUSIVE): prereg did not foresee S below 0 (-0.051); declared, outcome left as 'incerto'
- **e3c54** (REFUTED): author declares the criterion word 'manca' wrong ('nessun accordo chiaro' is not absence; herbal A and 'rest' underpowered); error repeated and fixed in e3c83
- **e3c69** (CONFIRMED): literal preregistered label 'ritmo fisso trovato: P=2, stesso primo segno'; design error declared (distance-1 effect not foreseen), resolved by judgement as no list rhythm
- **e3c83** (REFUTED): declared criterion error; literal label 'il salto del disegno azzera lo stato' given to a CI containing 0 (A +0.08, CI -0.02 to +0.17); read as unknown

## Post-hoc overrides of a preregistered label (outcome the original criterion gives vs. author's reading)

| id | class in the log | literal preregistered outcome | author's post-hoc reading |
|---|---|---|---|
| e53 | MIXED | MIXED | criterion declared ill-chosen after the run (one-sided thresholds let a bond excess of 0.30-0.36 pass); two-sided bands used from e56 |
| e85 | SUPERSEDED | CONFIRMED ('distici', z 6.7) | position effect, reading withdrawn in the same entry -> SUPERSEDED |
| e93 | MIXED | MIXED ('meno legata' by a hair; B undecided) | border-form effect, first word from page vocabulary (closer to REFUTED) |
| e111 | REFUTED | REFUTED (criterion not met at any level) | criterion non-discriminating (fails the syllable-cipher control too): closer to NULL/INCONCLUSIVE |
| e133 | MIXED | MIXED (Part 1 'reggono'; Parts 2-3 no) | Part 1 rule ill-posed; neither proposal holds (REFUTED) |
| e137 | SUPERSEDED | CONFIRMED ('numerazione: sì') | null defective; redone in e137b ('indeciso') -> SUPERSEDED |
| e173 | SUPERSEDED | CONFIRMED ('le scelte seguono la dimensione') | confound found; suspended, then e173b/e177 (largely mechanical) -> SUPERSEDED |
| e191 | SUPERSEDED | CONFIRMED ('ridondanza da messaggio') | not accepted (low power, within-word links); e191b -> SUPERSEDED |
| e195 | SUPERSEDED | CONFIRMED ('spazi spuri') | not accepted pending e195b (word-length effect) -> SUPERSEDED |
| e321 | MIXED | (a) outside the foreseen categories (z +8.2) | (a) labelled 'incerto' by judgement; overall MIXED |
| e354 | REFUTED | REFUTED ('senza direzione') | positive control judged too weak after the result: low power (NULL/INCONCLUSIVE) |
| e374 | CONFIRMED | CONFIRMED (gibberish F1 z 3.2 > 3) | threshold badly calibrated; effect negligible in gibberish |
| e384 | CONFIRMED | CONFIRMED ('passa a capo come nella prosa') | criterion badly chosen; the junction does not cross the line break (REFUTED), as later tests assume |
| e3a90 | MIXED | MIXED (Naibbe 'come il Voynich') | rule defect (ratio of near-zero excesses); no comparison text has the signature (REFUTED) |
| e3b33 | REFUTED | REFUTED ('non si ritrova') | half-life criterion fragile (B missed the threshold by 0.0002); contrast tested in e3b34 |
| e3b65 | REFUTED | REFUTED ('righe vicine che si somigliano, non memoria') | low power (NULL/INCONCLUSIVE) |
| e3c54 | REFUTED | REFUTED ('la finestra manca in qualche sezione') | 'not clear' is not 'absent' (MIXED); criterion phrased too sharply |
| e3c69 | CONFIRMED | CONFIRMED ('ritmo fisso trovato: P = 2') | design error: the peak comes from the adjacent word, no list rhythm (REFUTED) |
| e3c83 | REFUTED | REFUTED ('il salto del disegno azzera lo stato') | CI contains 0: neither shown nor reset (NULL/INCONCLUSIVE); criterion phrased too sharply |

## Superseded experiments

- **e16** → e17 (original class NULL/INCONCLUSIVE)
- **e85** → QUADERNO l.1291, l.1530 (original class CONFIRMED)
- **e123** → e123b (original class CONFIRMED)
- **e137** → e137b (original class CONFIRMED)
- **e154** → e154b (original class CONFIRMED) — UPHELD
- **e173** → e173b, e177 (original class CONFIRMED)
- **e173b** → e175, e177 (original class CONFIRMED)
- **e186** → e186b, e186c (original class CONFIRMED)
- **e186b** → e186c (original class MIXED)
- **e191** → e191b (original class CONFIRMED)
- **e195** → e195b (original class CONFIRMED)
- **e206b** → e3b06 (original class CONFIRMED)
- **e210** → e210b (original class DESCRIPTIVE)
- **e212b** → e212c (original class CONFIRMED)
- **e217** → e217b (original class CONFIRMED)
- **e223** → e223b (original class CONFIRMED)
- **e247** → e247d (original class CONFIRMED)
- **e247b** → e247d (original class REFUTED)
- **e247c** → e247d (original class REFUTED)
- **e279** → e279c (original class CONFIRMED)
- **e332** → e334 (original class CONFIRMED)
- **e346** → e382 (original class REFUTED)
- **e3a17** → e3a20 (original class CONFIRMED)
- **e3a18** → e3a20 (original class MIXED)
- **e3a19** → e3a20 (original class CONFIRMED)
- **e3a26** → e3a31, e3a33 (original class CONFIRMED) — UPHELD
- **e3a27** → e3a31, e3a33 (original class CONFIRMED) — UPHELD
- **e3a28** → e3a29 (original class MIXED)
- **e3a31** → e3a33 (original class NULL/INCONCLUSIVE)
- **e3a46** → e3a47 (original class REFUTED)
- **e3a65** → e3a72 (original class MIXED)
- **e3a69** → e3a71 (original class MIXED)
- **e3a74** → e3b46 (original class CONFIRMED)
- **e3a97** → e3b68 (original class CONFIRMED)
- **e3b01** → e3b03 (original class CONFIRMED)
- **e3b02** → e3b03 (original class CONFIRMED)
- **e3b07** → e3b08 (original class MIXED)
- **e3b10** → e3b66 (original class REFUTED)
- **e3b13** → e3b36 (original class CONFIRMED)
- **e3b14** → e3b34 (original class MIXED)
- **e3b21** → e3b33; e3b34 (original class REFUTED)
- **e3b23** → e3b34 (original class REFUTED)
- **e3b27** → e3b28 (original class REFUTED) — UPHELD
- **e3b30** → e3b32 (original class CONFIRMED)
- **e3b31** → e3b32; QUADERNO l.12202 (original class CONFIRMED)
- **e3b37** → e3b83 (original class CONFIRMED)
- **e3b38** → e3b55; e3b71 (original class CONFIRMED)
- **e3b39** → e3b55; e3b71 (original class CONFIRMED)
- **e3b41** → e3b55; e3b71 (original class CONFIRMED)
- **e3b42** → e3b55; e3b71 (original class CONFIRMED)
- **e3b44** → e3b55; e3b71 (original class CONFIRMED)
- **e3b51** → e3b54 (original class REFUTED)
- **e3b52** → e3b54 (original class REFUTED)
- **e3b53** → e3b54 (original class MIXED)
- **e3b54** → e3b56; e3b62; e3b70 (original class CONFIRMED)
- **e3b56** → e3b62; e3b70 (original class CONFIRMED)
- **e3b59** → e3b62; e3c81 (original class CONFIRMED)
- **e3b60** → QUADERNO l.12910; e3b62 (original class CONFIRMED)
- **e3b75** → e3b76 (original class REFUTED)
- **e3b82** → e3c14, e3c26 (original class DESCRIPTIVE)
- **e3b84** → e3b85 (original class CONFIRMED)
- **e3b96** → e3c30; e3c31 (original class CONFIRMED)
- **e3b98** → e3c30; e3c31 (original class REFUTED)
- **e3c01** → e3c45 (original class REFUTED)
- **e3c06** → e3c07; QUADERNO l.13967 (original class NULL/INCONCLUSIVE)
- **e3c23** → e3c24 (original class CONFIRMED)
- **e3c28** → e3c30; e3c31 (original class CONFIRMED)
- **e3c46** → e3c48 (original class DESCRIPTIVE)
- **e3c47** → e3c48 (original class MIXED)

## Preregistration but no results file (4)

- e122: e122.md (NOT_RUN)
- e212c: e212c.md (REFUTED)
- e281: e281.md (NOT_RUN)
- e289: e289.md (NOT_RUN)

## Results but no preregistration (31)

- Imported, not preregistered (28): e01, e02, e03, e04, e05, e06, e07, e08, e09, e10, e11, e12, e13, e14, e15, e16, e17, e18, e19, e20, e21, e22, e23, e24, e25, e26, e27, e28.
- e45: e45_allineamento.json, e45_allineamento.md (NOT_RUN)
- e54: e54_firma_pagina.json, e54_firma_pagina.md (DESCRIPTIVE)
- e61: e61_pagella.json, e61_pagella.md (DESCRIPTIVE)

## Neither preregistration nor results (15)

- e29 (NOT_RUN): e29 riformulato, e36–e38 anticipati
- e33 (DESCRIPTIVE): Scaricate 211 immagini su 213: rifiutate con 403 le foto del dorso e del taglio, che non servono.
- e194 (NOT_RUN): Prova di fattibilità per l'e194 (ch/sh sulle immagini piene): misura ingenua non adatta
- e215 (NOT_RUN): l'esperimento non si lancia
- e254 (NOT_RUN): e254 (ciclo avversario, obiettivo AUC ≤ 0,6)
- e267 (NOT_RUN): e267, modulo etichette: le etichette sono un sistema a parte che copia le etichette vicine;
- e282 (NOT_RUN): e282, codice per categorie con riempitivi.
- e284 (NOT_RUN): B, controllo del "prestito" (quanto l'AUC scende solo perché si copia dalla pagina vera) → e284, da fare.
- e398 (NOT_RUN): Esperimento abbandonato, niente esito.
- e3a45 (NOT_RUN): Senza la larghezza fisica delle righe non si può fare bene. Non eseguito.
- e3a73 (NOT_RUN): Il test non può quindi dire nulla sul cifrario, e lo abbandono.
- e3b81 (NOT_RUN): abbandonato prima della preregistrazione (prova senza potere di distinguere)
- e3c56 (NOT_RUN): l'esperimento non si fa; il numero e3c56 resta senza preregistrazione né risultati.
- e3c67 (NOT_RUN): Esperimento non fatto; numero e3c67 senza preregistrazione né risultati.
- e3c82 (NOT_RUN): Secondo la regola, esperimento non fatto; numero e3c82 senza preregistrazione né risultati.

## Numbers never used, and follow-ups announced but never run (not rows of the log)

- **Numbers with no trace** in preregistrations, code, results, QUADERNO or planning documents: e32, e168, e208, e220, e287, e290. e209 has no files or entry; it is cited once in `rassegna/voynichizzatore_progetto.md` in a list of message tests, probably a slip (CHECK).
- **Follow-ups announced in the QUADERNO but never preregistered or run:** e213b (QUADERNO l.5551, redo of e213 with a longer positive control), e278b (l.6089, subsamples of equal size), e285d (l.6653, check of e285c). A redo of e207 was also proposed and not done.
- **Out of the requested range:** e3c84 and e3c85 (new reanalyses for the revision, 8/10/2026) and e400–e418 (generator project).

## Caveats for the appendix

- The class depends on how the question is framed (rule 1 above); read it together with `question_en`. Two-sided "A or B?" preregistrations were framed on the first alternative (marked CHECK where relevant).
- Several QUADERNO entries are cross-cutting corrections without their own id (for example l.1530 summary of withdrawn readings, l.12434 bootstrap by paragraph in e3b41/e3b42, l.12734 biased similar-pair exclusion, l.12910 insensitive null in hand 1, l.13967 unbalanced median split in e3b80/e3c06, l.14058 linear-regression limit in e3c09). They are cited in the notes of the affected ids.
- QUADERNO l.10092 (a generator-project entry) declares the report-card property "gradiente" ill-posed: the real Voynich scores 17/18. Step criteria of the 18/18 plan (e243, e243b, e251, e252, e253, e268, e268b) should be read with this in mind; none of their outcomes changes, because all were well below threshold.
- In many entries "71 lingue" means 71 texts, 15 of them constructed languages (external review, QUADERNO l.15981). The Italian quotes are kept verbatim.
- `DOSSIER_WHITE_PAPER.md` §15.5 still states e300 as "page order keeps writing order"; e308 explains that effect mainly by recto/verso of the same leaf (e300/e300b are CONFIRMED with CHECK).

## Items to verify (CHECK, 110)

- **e33** (DESCRIPTIVE): no preregistration; data-acquisition utility (also QUADERNO l.246: first 25 images), not a hypothesis test
- **e34** (CONFIRMED): possibly superseded by e195/e195b: same narrower-space effect vanishes when stratified by word length; e34 not explicitly retracted
- **e42** (REFUTED): either/or prereg, classified on the batch (L) claim
- **e45** (NOT_RUN): no prereg; technical pilot only. Alignment unreliable (scales 1.60-2.04, about half of labels misplaced), so the ink measurement was not run (D-010)
- **e50** (REFUTED): MIXED arguable, but the compatibility criterion (c) failed
- **e58** (NULL/INCONCLUSIVE): strong effect, validity failed only by the letter
- **e64** (NULL/INCONCLUSIVE): could be read as REFUTED; validity not full
- **e71** (NULL/INCONCLUSIVE): multi-part prereg; generator part definite
- **e72** (CONFIRMED): strictly unreadable; partly corrected by e139 (o- not line-initial)
- **e73** (CONFIRMED): partly corrected by e139: o- is not a line-initial sign (y-, d-, s- are)
- **e78** (CONFIRMED): predicted line-border pass failed (Manusmrti end 148 vs 55); MIXED arguable
- **e85** (SUPERSEDED): retraction is in own entry; could be REFUTED
- **e89** (MIXED): could be read as REFUTED
- **e91** (DESCRIPTIVE): has predictions, could be REFUTED
- **e93** (MIXED): CONFIRMED by rule, REFUTED by conclusion
- **e99** (CONFIRMED): could be DESCRIPTIVE
- **e111** (REFUTED): criterion also fails for the syllable-cipher control ('il criterio non distingue'); could be NULL/INCONCLUSIVE
- **e118** (MIXED): could be REFUTED
- **e122b** (NULL/INCONCLUSIVE): heading reads negative; could be REFUTED
- **e139** (REFUTED): dichotomous prereg question, yes-claim taken as 'o- positional'
- **e141** (CONFIRMED): dichotomous prereg question, yes-claim taken as 'composed in place' (first criterion)
- **e142** (NULL/INCONCLUSIVE): 'nessuna prova' read as 'not shown' (low power); could be REFUTED
- **e144** (REFUTED): MIXED if the three Reddit claims are counted separately
- **e157** (NULL/INCONCLUSIVE): prereg reads invalidity as 'habits insufficient', could be REFUTED
- **e162** (REFUTED): claim direction taken from prereg title (visibility); (a) line kept = yes
- **e179** (REFUTED): three-way criterion, 'no preference' could be read as NULL/INCONCLUSIVE
- **e186** (SUPERSEDED): candidates were preliminary by design; could stay CONFIRMED qualified by e186b/c
- **e191** (SUPERSEDED): orig class is the formal rule label, never accepted
- **e201** (CONFIRMED): possibly superseded by e3b49/e3b50 ('ridimensiona l'e201': saving explained by neighbouring signs)
- **e206** (CONFIRMED): possibly superseded by e3b06 (line choices reread as short-range memory)
- **e211** (MIXED): 'intermedio' (between categories) mapped to MIXED
- **e212b** (SUPERSEDED): orig class is the formal candidate label
- **e212c** (REFUTED): partial execution, could be classed NOT_RUN
- **e226** (MIXED): 'intermedia' (between categories) mapped to MIXED
- **e227** (MIXED): two sub-questions, A inconclusive, B mixed
- **e247c** (SUPERSEDED): e247d did not recompute e247c's line-shift residual itself
- **e254** (NOT_RUN): see notes
- **e259** (DESCRIPTIVE): fixed binary reading; alternatively REFUTED for 'Voynich says little per word'
- **e259b** (DESCRIPTIVE): as e259, could be read as REFUTED
- **e293** (DESCRIPTIVE): could be read as CONFIRMED
- **e300** (CONFIRMED): possibly superseded by e308 (l.7246: consecutive similarity is mostly recto/verso of same leaf; binding maybe not in writing order)
- **e300b** (CONFIRMED): possibly superseded by e308 (l.7246 explains e300's consecutive-page similarity mainly by recto/verso of the same leaf)
- **e301** (MIXED): preregistered label is positive
- **e307** (CONFIRMED): possibly superseded by e315 (l.7384 'Correzione della mia lettura dell'e307': axis is not the A/B axis); prereg outcomes unaffected
- **e309** (CONFIRMED): three-way criteria with no stated hypothesis; claim direction taken from the e307 reading
- **e314** (MIXED): main sub-question (a) confirmed
- **e317** (NULL/INCONCLUSIVE): could be MIXED
- **e321** (MIXED): (a) label incerto
- **e322** (CONFIRMED): binary habit-vs-layout question; claim taken as layout
- **e332** (SUPERSEDED): e332's distance measure itself not retracted, only the topic reading
- **e338** (CONFIRMED): possibly superseded by e340/e345 for E2 (same column): mostly from line edges, 'non una copia in colonna'; E1 holds within paragraph (e340)
- **e346** (SUPERSEDED): multi-way prereg outcome, classified on the 'like gibberish' claim
- **e351** (REFUTED): label 'no' but low power stressed (30 herbal bifolios). One bifolio (D-2, f26/f31, language B) closer to quire H. Group e351-e352
- **e354** (REFUTED): see notes
- **e382** (REFUTED): multi-way prereg outcome, classified on 'like gibberish' claim
- **e384** (CONFIRMED): literal prereg label = 'passes', but Q -0.02 (z -0.7) and author reads 'does not cross the line break', as later tests assume (e395, e3a05, e3a43). Exception in text-only pages (e3a06)
- **e390** (MIXED): graded 'how much' criterion; MIXED used for the middle category
- **e3a03** (REFUTED): possibly superseded by e3a07 (dossier corrected)
- **e3a07** (REFUTED): two-alternative question; 'yes' taken as 'grammar'
- **e3a29** (MIXED): could be REFUTED per author's reading
- **e3a52** (MIXED): no overall criterion
- **e3a70** (MIXED): possibly superseded by e3a76 ('Rilettura dell'e3a70': excess partly due to order-1 measure)
- **e3a76** (DESCRIPTIVE): categorical outcome, no yes/no claim (could be read as CONFIRMED); possibly superseded by e3a85 (secondary reading on generators' order-2 corrected)
- **e3a79** (CONFIRMED): the title question is answered yes, but the prereg's unifying hypothesis (first word copied less) did not hold ('non regge')
- **e3a81** (REFUTED): REFUTED answers the title question; the written prediction (R<0.25 for both) was confirmed. Replicated with IT in e3b79
- **e3a83** (CONFIRMED): possibly superseded by e3a87 (reading corrected: effect stays, but line-above copying is uniform, not memory)
- **e3a86** (MIXED): possibly superseded by e3a87 (joint 'single behaviour' reading with e3a83 corrected)
- **e3a90** (MIXED): see notes
- **e3b01** (SUPERSEDED): claim direction (calibration with 3 outcomes)
- **e3b03** (MIXED): neither 'sparisce' nor 'resta'; author reads it as length
- **e3b18** (CONFIRMED): e3b35 (IT) failed to replicate (cross-class link +0.005, CI above 0) and wrote 'Correzione della lettura dell'e3b18'; later e3c43 (clean measure) 'Conferma l'e3b18'. Possibly SUPERSEDED
- **e3b22** (NULL/INCONCLUSIVE): e3b34 explicitly corrects the reading of e3b22 ('longer memory in B' not demonstrated); preregistered outcome (insufficient data) unaffected; possibly SUPERSEDED
- **e3b24** (CONFIRMED): possibly superseded by e3b34 (same half-life method declared fragile for e3b21-e3b23; e3b24 not named)
- **e3b35** (MIXED): e3b66 declares 'memory resets at line break' (e3b10, e3b35, e3b63) wrong, i.e. sub-result 2 partially superseded
- **e3b40** (REFUTED): e3b71 'Correzione delle e3b38-e3b44' covers it by range, but concerns choice memory across line breaks, not edge forms
- **e3b43** (CONFIRMED): e3b71 'Correzione delle e3b38-e3b44' covers it by range, but concerns choice memory across line breaks, not copying
- **e3b58** (CONFIRMED): e3b69 says word-shuffle null p-values of e3b54-e3b63 are ~2x too optimistic; e3b58 (z 3.1) is in that range and was not re-tested
- **e3b62** (MIXED): e3b70 corrects reading of e3b54-e3b62 (real scribe); e3c27 corrects class pattern
- **e3b63** (REFUTED): e3b65/e3b66 declare its headline reading 'line-break reset confirmed' (normal pages) wrong; preregistered text-only outcome unaffected (cf. e3b71)
- **e3b64** (CONFIRMED): e3b65 shows part of the effect is similarity of neighbouring lines (normal pages not significant with that control); direction later supported by e3b66/e3b67; possibly superseded
- **e3b65** (REFUTED): e3b66/e3b67 later find memory passing line break and gap in part
- **e3b66** (CONFIRMED): e3c39 (clean measure) not confirmed, 'stima non confermata'; possibly superseded
- **e3b67** (CONFIRMED): e3c83 says the e3b67 reading 'non è confermata né smentita' with the later clean measure (few data); possibly superseded
- **e3b80** (CONFIRMED): possibly superseded by e3c12 (correction: consumption mainly in sh/ch, not all choices)
- **e3b82** (SUPERSEDED): partial correction (qo/o, -ey/-dy stay about 10)
- **e3b97** (CONFIRMED): possibly superseded by e3c30/e3c31 (flat-shape separation from languages partly a line-length effect)
- **e3c01** (SUPERSEDED): partial correction (adjacent words only)
- **e3c07** (CONFIRMED): possibly superseded by e3c12 (letter-consumption mainly in sh/ch)
- **e3c15** (CONFIRMED): possibly superseded by e3c30/e3c31 (flat-shape separation from languages partly a line-length effect)
- **e3c20** (CONFIRMED): two-sided prereg question (start vs margin); claim framed as reading (1)
- **e3c21** (NULL/INCONCLUSIVE): label 'incerto' but data contradict a restart; could be read as REFUTED
- **e3c24** (REFUTED): two-sided prereg question (before or after); claim framed as e3c23's planned-space reading
- **e3c30** (REFUTED): heading says 'non è dimostrata', but prereg label is 'non è propria' (REFUTED)
- **e3c31** (REFUTED): e3c32 heading says 'correzione dell'e3c31', but it retracts only the side claim that short lines have higher agreement; prereg outcome unaffected
- **e3c33** (REFUTED): possibly superseded by e3c66, which corrects the descriptive 'equal up to 3 words then collapse' (state decays gradually)
- **e3c39** (NULL/INCONCLUSIVE): ZL label alone would be REFUTED; classed inconclusive per heading
- **e3c42** (REFUTED): label says 'non dimostrata' (could be NULL/INCONCLUSIVE) but heading and reading state absence
- **e3c44** (CONFIRMED): possibly superseded in part by e3c51 ('correzione per sh/ch in GC'): with bias correction sh/ch (2/1) is no longer clear; -ey/-dy, gallows and qo/o hold
- **e3c45** (NULL/INCONCLUSIVE): e3c48 says this uncorrected comparison 'va rifatto con la correzione'; no redo of e3c45 found in QUADERNO
- **e3c49** (MIXED): inconclusive + supportive sub-outcomes; could be NULL/INCONCLUSIVE overall
- **e3c50** (REFUTED): possibly superseded by e3c58 ('cambia la lettura dell'e3c50'); e3c79 finds that window copy-like
- **e3c51** (NULL/INCONCLUSIVE): label 'nessun accordo chiaro' could be read as REFUTED; e3c59 retracts e3c51's reading (window tied to the word, not the letter form)
- **e3c52** (MIXED): per-choice labels, no single claim; as a replication ZL/IT it would be CONFIRMED
- **e3c53** (REFUTED): prereg has a declared pre-execution fix (gibberish hand = text); unclear if after prereg commit
- **e3c59** (CONFIRMED): possibly superseded by e3c79 ('correzione parziale della lettura dopo l'e3c59'): similar size/shape but copy-like mechanism; the test outcome itself is unaffected
- **e3c66** (MIXED): two-part prereg; A qualified by e3c74 (4-6-word value includes slow cross-line component)
- **e3c68** (REFUTED): possibly superseded by e3c72, but 'ritirata l'osservazione dell'e3c68' retracts only the non-preregistered side observation (distortion)
- **e3c69** (CONFIRMED): literal label kept as class
- **e3c71** (MIXED): the formal Esito label alone is positive
- **e3c78** (REFUTED): margin sub-criterion literally 'in parte' (3 of 72 MSS with one avoided start; author: chance level); could be MIXED

