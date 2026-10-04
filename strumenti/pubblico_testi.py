# -*- coding: utf-8 -*-
"""I testi in inglese del pacchetto pubblico (istruzioni, strumento da riga di comando, prova di rilettura, messaggi).
Li usa strumenti/costruisci_pubblico.py. I commenti nel codice del pacchetto restano in italiano."""

TEST_KEY = 'read-back test on another computer'

SOURCE = ('ZL transliteration (Zandbergen-Landini) of the Voynich manuscript, version 3b of 13 May 2025, from https://www.voynich.nu/ '
          '(public domain, made available under the Creative Commons CC0 licence). Here: running paragraph text only, words without '
          'unreadable characters, with page, paragraph start, section and Currier language.')

# messaggi del nascondiglio: (italiano, inglese)
MESSAGES = [
    ("print('%d pagine' % (k + 1), flush=True)", "print('%d pages' % (k + 1), flush=True)"),
    ('chiave errata, o manoscritto senza messaggio', 'wrong key, or manuscript without a message'),
    ('chiave errata, o manoscritto alterato', 'wrong key, or altered manuscript'),
    ('chiave sbagliata o manoscritto senza messaggio', 'wrong key, or manuscript without a message'),
    ('testo troppo lungo per questo libro: servono %d bit, il libro ne porta %d', 'text too long for this book: it needs %d bits, the book carries %d'),
    ('errore: la decodifica di controllo non restituisce il testo', 'error: the check decoding does not return the text'),
]

TEST_TEXT = """This is the test text of the Voynichizer.

If you are reading these lines after pulling them out of a manuscript written on another computer, reading back works
across machines: the character of each page, the word weights and the arithmetic coding gave the same numbers here and
there. The text contains accented letters (à, è, é, ì, ò, ù, ñ, ü), numbers (1404, 1438, 240 leaves) and a few signs
(—, «», ’), to check that everything comes back, byte for byte.

A herbal, a sky of stars, women in green pools, roots in jars: nobody knows what the book says, or whether it says
anything at all.
"""

TOOL = '''# -*- coding: utf-8 -*-
"""Voynichizer (voynichizzatore): turns any text into a "Voynich-like" manuscript (in EVA), with the text hidden in the
choice of the words on each page; with the key, the text comes back exactly.

    python voynichizzatore.py encode text.txt --key "a long passphrase" --out manuscript.txt
    python voynichizzatore.py decode manuscript.txt --key "a long passphrase" --out text.txt
    python voynichizzatore.py empty --key "a long passphrase" --out manuscript.txt      (a manuscript with no message)
    python voynichizzatore.py pdf manuscript.txt --out book.pdf                         (the pages, in Voynich-like script)
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
VERSIONE = '%s'
ALIAS = {'codifica': 'encode', 'decodifica': 'decode', 'vuoto': 'empty'}


def main():
    ap = argparse.ArgumentParser(description='Voynichizer: hide a text in a Voynich-like manuscript and read it back with the key')
    ap.add_argument('action', choices=('encode', 'decode', 'empty', 'pdf', 'codifica', 'decodifica', 'vuoto'))
    ap.add_argument('file', nargs='?', help='text to hide (encode) or manuscript to read (decode, pdf)')
    ap.add_argument('--key', '--chiave', dest='key', help='the key (use a long passphrase)')
    ap.add_argument('--out', '--uscita', dest='out', help='output file')
    a = ap.parse_args()
    action = ALIAS.get(a.action, a.action)
    if action != 'empty' and not a.file:
        raise SystemExit('a file is required')
    if action == 'pdf':
        import pagine
        out = a.out or os.path.splitext(a.file)[0] + '.pdf'
        print('written %%s: %%d pages' %% (out, pagine.pdf(a.file, out)))
        return
    if not a.key:
        raise SystemExit('--key is required')
    import canale_sacco, v0
    if action == 'decode':
        try:
            text = canale_sacco.decodifica(v0.carica(a.file), a.key, VERSIONE)
        except Exception as e:
            raise SystemExit('nothing to read: %%s' %% e)
        if a.out:
            open(a.out, 'w', encoding='utf-8', newline='\\n').write(text)
            print('text written to %%s (%%d characters)' %% (a.out, len(text)))
        else:
            sys.stdout.reconfigure(encoding='utf-8', newline='\\n')
            sys.stdout.write(text + '\\n')
        return
    text = None
    if action == 'encode':
        text = open(a.file, encoding='utf-8').read().replace('\\r\\n', '\\n')
    rows, info = canale_sacco.codifica(text, a.key, VERSIONE)
    v0.salva(rows, a.out or 'manuscript.txt')
    print('written %%s: %%d lines; message %%d bits out of %%d available' %% (a.out or 'manuscript.txt', len(rows), info['bit_messaggio'], info['capacita_bit']))


if __name__ == '__main__':
    main()
'''

TEST = '''# -*- coding: utf-8 -*-
"""Read-back test on another computer. Usage: python prova.py
1. reads prova/manoscritto_di_prova.txt (written on the computer that prepared the package) and compares it with
   prova/testo_di_prova.txt;
2. writes a new manuscript here with the same text and key, and reads it back;
3. says whether the manuscript written here is identical to the bundled one (it does not have to be)."""
import os, platform, sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
KEY = %r


def main():
    import canale_sacco, v0, voynichizzatore
    import numpy, scipy, sklearn
    v = voynichizzatore.VERSIONE
    text = open(os.path.join(QUI, 'prova', 'testo_di_prova.txt'), encoding='utf-8').read()
    print('Python %%s on %%s %%s; numpy %%s, scipy %%s, scikit-learn %%s' %% (platform.python_version(), platform.system(), platform.machine(),
                                                                       numpy.__version__, scipy.__version__, sklearn.__version__))
    bundled = v0.carica(os.path.join(QUI, 'prova', 'manoscritto_di_prova.txt'))
    try:
        one = canale_sacco.decodifica(bundled, KEY, v) == text
    except Exception as e:
        one = False
        print('   error while reading back: %%s' %% e)
    print('1. the manuscript written elsewhere reads back here: %%s' %% ('YES' if one else 'NO'))
    print('   (now writing a new manuscript: a couple of minutes)')
    again, _ = canale_sacco.codifica(text, KEY, v, verifica=False)
    v0.salva(again, os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt'))
    two = canale_sacco.decodifica(v0.carica(os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt')), KEY, v) == text
    print('2. a manuscript written here reads back here: %%s' %% ('YES' if two else 'NO'))
    a = open(os.path.join(QUI, 'prova', 'manoscritto_di_prova.txt'), encoding='utf-8').read()
    b = open(os.path.join(QUI, 'prova', 'manoscritto_rifatto.txt'), encoding='utf-8').read()
    print('3. the manuscript written here is identical to the bundled one: %%s (it does not have to be)' %% ('YES' if a == b else 'NO'))


if __name__ == '__main__':
    main()
'''

README = """# Voynichizer (voynichizzatore)

Takes any text and a key, and writes a "Voynich-like" manuscript in EVA (the alphabet used to transliterate the Voynich
manuscript, Beinecke MS 408). With the same key, the text comes back exactly.

    python voynichizzatore.py encode text.txt --key "a long passphrase" --out manuscript.txt
    python voynichizzatore.py decode manuscript.txt --key "a long passphrase" --out text.txt
    python voynichizzatore.py empty --key "a long passphrase" --out manuscript.txt
    python voynichizzatore.py pdf manuscript.txt --out book.pdf

Requires Python 3.12 with `numpy`, `scipy`, `scikit-learn` and, for the PDF, `matplotlib` (`pip install -r requirements.txt`). Writing a manuscript
takes a couple of minutes; reading it back takes a few seconds.

## What you get

- A whole book of 207 pages and about 4,200 lines, whatever the length of the text; one line of the file per line of
  the manuscript, `<page.line> words.separated.by.dots`, with `@` in front of the lines that open a paragraph.
- The manuscript is EVA text. The `pdf` command then writes it out as a book, one page per page, in a Voynich-like
  script: the font `VoynichizzatoreEVA.ttf` was drawn for this project by a program (`carattere.py`), stroke by stroke;
  it imitates the shapes of the Voynich signs and is not a copy of any existing font. The PDF has text only, no drawings.
- It holds about 80,000 bits, i.e. roughly 20,000 characters of text after compression. If the text is longer, the
  program says so. If it is shorter, the rest of the book is filled so that you cannot see where the message ends.

## How it works, briefly

- **The words of each page** come from the lexicon of the corresponding section of the Voynich, with a preference for
  certain glyphs (the "character" of the page) borrowed from another page; in addition there are new words, invented
  with the shape of the words that occur only once in the Voynich.
- **The message** (compressed and encrypted with the key) decides how many times each known word appears on each page.
  There is no correspondence between the words of the manuscript and the words of the text: there is nothing to
  translate word by word.
- **The arrangement** of the words in the lines follows the shape of the words (line start and end, first lines of
  paragraphs) and a few weak links between neighbouring words. It carries no information: to read the message you only
  need the words of each page and the key.
- **The layout** of each page (how many lines, how many words per line, where paragraphs start) is drawn from the
  statistics of the Voynich: no page has the layout of a real page. The words are then arranged so that the width of
  each line in characters behaves as in the Voynich, where lines with more words have shorter words.

## How close it is to the Voynich (measurements, with their limits)

Measured by hiding the same Latin text with 12 different keys. The "judges" are two classifiers that try to tell
generated pages from real ones by looking at about 220 page statistics: 0.5 means they are guessing, 1 that they never
fail.

| measure | value |
|---|---|
| judge 1 (statistics of glyphs, words, lines) | 0.55 ± 0.01 |
| judge 2 (plus: word pairs, position in the line, first lines, page profile) | 0.60 ± 0.01 |
| scorecard of 18 properties of the text (17 attainable: the Voynich itself fails one when measured the same way) | 15 to 16 |
| 8 further properties | 5 to 6 |
| lines much wider than the others on their page (over 1.5 times the median; Voynich 2.9%) | 2.8% |
| lines somewhat wider (over 1.25 times the median; Voynich 6.0%) | 11.5% |
| the text comes back exactly | 12 times out of 12 |
| wrong key rejected | 12 times out of 12 |

A manuscript with a message and one without cannot be told apart by these measures.

**What this does NOT mean.** It is not "indistinguishable from the Voynich":

- the second judge still recognises it a little (about one key in two gives a manuscript above 0.60);
- some known properties never come out right: the width of the lines (see the table), the page profile, the spelling choices agreeing within a line as
  measured on 12 classes, the similarity between words of the same line (a little too high);
- the model was tuned on the same statistics these judges look at; a judge built independently has not been tried;
- almost all words are Voynich words: anyone who knows the program can tell that a manuscript was made with the
  program. What they cannot tell is whether there is a message inside.

## Security

- The key goes through scrypt, the text is encrypted with a SHAKE-256 stream and carries an HMAC-SHA256 tag: with the
  wrong key the program answers "wrong key".
- These are standard building blocks, but the whole **has not been reviewed by an expert**: do not use it for real
  secrets. Security depends on the key: use a long passphrase, not a dictionary word.
- Writing and reading use floating-point computations: use the same version of the program to write and to read.
  (This is v20. Manuscripts written with the previous published version, v17, are read by this one: the two differ
  only in how the words are arranged on the page, which carries no information.)
  Reading a manuscript on a computer other than the one that wrote it has not been verified yet (see the test below).

## Read-back test on another computer

    python prova.py

It reads the bundled test manuscript (written on another computer), then writes a new one and reads it back. At the
end it prints three lines: if the first says YES, a manuscript written elsewhere reads back here too.

## Sources

- **Text of the Voynich** (`voynich_zl3b.json`): from the ZL transliteration by René Zandbergen and Gabriel Landini,
  version 3b of 13 May 2025, published at https://www.voynich.nu/ , where the transliterations are stated to be in the
  public domain and are made available under the Creative Commons CC0 licence. Only the running paragraph text is
  included here, with the readable words.
- The manuscript is kept at the Beinecke Rare Book and Manuscript Library, Yale University (MS 408).

## Licence

The program is under the MIT licence (file `LICENSE`). The Voynich text in `voynich_zl3b.json` is in the public domain
(CC0). Comments in the source code are in Italian.
"""
