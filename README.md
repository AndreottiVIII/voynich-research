# How the Voynich manuscript is written — research record

This repository is the research record behind the preprint
**"Hiding a Message in a Voynich-like Book: the manuscript's writing rules, measured against languages and medieval
scribes, and reproduced by a steganographic generator"** by Davide Caniatti (2026), in
[`white_paper/en/main.pdf`](white_paper/en/main.pdf).

It contains no decipherment of the Voynich manuscript (Beinecke MS 408), and claims none.

## What is here

| path | content |
|---|---|
| `white_paper/en/` | LaTeX sources of the paper, bibliography, and `figure/genera_figure.py`, which redraws the figures |
| `preregistrazioni/` | one preregistration per experiment (hypothesis, measure, criterion), written before the run; in Italian |
| `esperimenti/` | the code of each experiment, `eNN_*.py` |
| `analisi/` | shared modules (reading the transliterations, measures) |
| `risultati/` | results of each experiment (`.json`, `.md`) and, in `risultati/provenienza/`, a provenance record per run: code version, data fingerprints, environment, seeds, output |
| `QUADERNO.md` | the laboratory notebook, dated entries, append-only, negative results and errors included; in Italian |
| `DECISIONI.md` | method decisions |
| `white_paper/revisione/registro_esperimenti.csv` | the log of all 716 experiments with their outcomes |
| `dati/trascrizioni/` | the three Voynich transliterations used (ZL3b, IT2a, GC2a, IVTFF format, public domain) |
| `pubblico/voynichizzatore/` | a snapshot of the voynichizer; the maintained version is at [AndreottiVIII/voynichizzatore](https://github.com/AndreottiVIII/voynichizzatore) |

The working language of the project was Italian; the paper is in English.

## Re-running an experiment

- Python 3.12.10, packages in `requirements.txt`.
- `python esegui.py eNN` runs experiment `eNN` with `PYTHONHASHSEED=0` and fixed seeds, and writes its provenance record.
  With the same software versions it is meant to give the same numbers.
- Comparison corpora are not included, because of their size or their licences. `prepara.py` downloads the main ones at
  fixed commits into `dati/cache/`; Appendix E of the paper and `dati/FONTI.md` list all sources and licences.

## About this public copy

This is a copy of the working repository, made with `strumenti/copia_pubblica.sh`:

- author and committer e-mail addresses are replaced by the GitHub no-reply address; names and dates are unchanged;
- the notes of the external reviewer of version 1 of the paper, and our point-by-point verification of them, are not
  included; the changes they led to are listed in Appendix C of the paper;
- commit hashes therefore differ from those of the working repository. The provenance records in `risultati/provenienza/`
  cite the working repository's hashes; `risultati/provenienza/MAPPA_COMMIT_PUBBLICI.txt` maps each of them to the
  corresponding commit here (one line per commit: working hash, public hash).

The previous Italian README (September 2026) is kept as `README_settembre_2026_it.md`.

## Licence

- **Code** (Python, shell and PowerShell scripts): MIT licence, see [`LICENSE`](LICENSE).
- **Everything else written or produced by the project** (paper and its LaTeX sources, preregistrations, notebook,
  results, figures, documentation): Creative Commons Attribution 4.0 International, see
  [`LICENSE-CC-BY-4.0.md`](LICENSE-CC-BY-4.0.md).
- **Third-party material keeps its own licence:** the transliterations in `dati/trascrizioni/` (public domain, from
  [voynich.nu](https://www.voynich.nu/transcr.html)); the voynichizer snapshot in `pubblico/voynichizzatore/` and its font
  (MIT, see the `LICENSE` there).
