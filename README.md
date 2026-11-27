# The Riemann Hypothesis in Lean, in one scroll

**Live site: <https://henryplotnick.github.io/riemann-scroll/>**

| Proof | Scroll | Map | Circle |
|---|---|---|---|
| Riemann Hypothesis, original (17.4M lines) | [read](https://henryplotnick.github.io/riemann-scroll/) | [map](https://henryplotnick.github.io/riemann-scroll/graph.html) | [circle](https://henryplotnick.github.io/riemann-scroll/radial.html) |
| Riemann Hypothesis, compact edition | [read](https://henryplotnick.github.io/riemann-scroll/rh-compact/) | [map](https://henryplotnick.github.io/riemann-scroll/rh-compact/graph.html) | [circle](https://henryplotnick.github.io/riemann-scroll/rh-compact/radial.html) |
| Riemann Hypothesis, readable edition | [read](https://henryplotnick.github.io/riemann-scroll/rh-readable/) | [map](https://henryplotnick.github.io/riemann-scroll/rh-readable/graph.html) | [circle](https://henryplotnick.github.io/riemann-scroll/rh-readable/radial.html) |
| Fermat's Last Theorem | [read](https://henryplotnick.github.io/riemann-scroll/fermat/) | [map](https://henryplotnick.github.io/riemann-scroll/fermat/graph.html) | [circle](https://henryplotnick.github.io/riemann-scroll/fermat/radial.html) |

*Also here, with a dropdown on every page to switch between them: the same three views of the
shorter RH proof ([`rh-compact/`](rh-compact/) and [`rh-readable/`](rh-readable/)) and of the
Lean proof of Fermat's Last Theorem ([`fermat/`](fermat/)).*

A single web page that shows the complete Lean 4 proof of the Riemann Hypothesis
(Levent Alpöge with Claude, released 20 November 2026) as one continuously
scrolling plain-text stream: 175,187 files, 17,374,215 lines of Lean.

- Every file appears after the files it imports; `Main.lean` is the last file.
- A one-line header marks the start of each file. The Lean text is unchanged.
- Scroll, drag the bar on the right, or jump by line number, percentage or file name.
  The URL tracks the current line (`#L123456`), so any position can be linked.

## Map of the proof

`graph.html` draws every file as one mark, in 203 columns: each file sits one column to the
right of the deepest file it imports, so the foundations are on the left and everything
funnels into `Main.lean`. Click a file to see what it rests on and what builds on it, then
jump to it in the text. The import graph (753,261 edges) is in `graph.bin.gz`.

Within a column, files can be arranged two ways (toggle at the top of the map):
- **By connection** (default): each file is placed near the files it imports and the files
  that import it, using repeated barycenter sweeps (`tools/bary.py`, saved in `order.bin.gz`).
  Import lines are on average 72% shorter vertically than in the folder layout.
- **By folder:** grouped by folder, then alphabetical.

## The proof as a circle

`radial.html` puts `Main.lean` at the centre. Ring 1 is what it imports, ring 2 is what those
import, and so on: a file's ring is the fewest import steps between it and `Main.lean`.
Every file is within 43 steps. Each file is drawn once, hanging off one file that imports it,
with a slice of the circle proportional to how many files branch out from it. Selecting a
file shows its shortest route back to `Main.lean`. It is computed in the browser from
`graph.bin.gz`.

## How it works

The combined text is about 1 GB, too large for a browser to open as one document.
It is stored in `c/` as 3,545 gzip chunks of 5,000 lines each (217 MB in total).
`index.html` fetches and unpacks only the chunks around the current position.

## Source

The archive exactly as published (<https://alpo.ge/remark.pdf>), taken from the first
commit (`40e56bab`) of <https://github.com/leanprover-community/riemann-hypothesis>.
This is an unofficial reading copy. All credit for the proof belongs to its authors.

## Rebuild the text chunks

```bash
git clone https://github.com/leanprover-community/riemann-hypothesis.git src
git -C src checkout 40e56bab026552e089d7afcfeff08d2defb9c005
python3 -I tools/build.py src . 40e56bab026552e089d7afcfeff08d2defb9c005
python3 -I tools/gbuild.py . src/src   # rebuild the map's graph data
python3 -I tools/bary.py . 64 40      # rebuild the connection ordering
```

## Preview locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

## Fermat's Last Theorem (`fermat/`)

The same scroll, map and circle pages for the complete Lean 4 proof of Fermat's Last Theorem
published by Anthropic in September 2026 (<https://github.com/anthropics/fermats-last-theorem>,
Apache License 2.0, commit `6e837e75`): 60,475 files and 13,499,329 lines. Colours follow the topic
in each file name (`Thm_ModularCurve_…` is `ModularCurve`), since the project keeps its files in three
flat folders. The circle is centred on `FinalCheck.lean`, the build target that checks the theorem.

```bash
git clone https://github.com/anthropics/fermats-last-theorem.git flt
git -C flt checkout 6e837e75355538c7f80bab5b956861e86c4eacc2
python3 -I tools/fbuild.py flt fermat 6e837e75355538c7f80bab5b956861e86c4eacc2
python3 -I tools/gbuild.py fermat flt
python3 -I tools/bary.py fermat 64 40 topics
python3 -I tools/mkfermat.py .   # regenerate fermat/*.html from the RH pages
python3 -m http.server 8000      # then open http://localhost:8000/fermat/
```

## The shorter RH proof (`rh-compact/`, `rh-readable/`)

The same pages for <https://github.com/lsernau/grh-lean> (Anthropic and Claude, November 2026,
based on Alpöge's proof; Apache License 2.0, commit `72fead10`), which proves the same five
theorems far more briefly. It comes in two editions:

| Edition | Files | Lines | Lines of code (no comments or blank lines) |
|---|---|---|---|
| compact (`grh-compact/`) | 794 | 112,827 | 76,151 |
| readable (`grh/`) | 803 | 477,124 | 299,902 |

Colours follow each edition's `GUIDE.md`. In the compact edition, the folders of `New/` are grouped by
which of the three main theorems they serve (A, short forms; B, enough forms; C, long forms). In the
readable edition, they follow the stages of the argument. The background library `Lib/` is grey.

```bash
git clone https://github.com/lsernau/grh-lean.git grh-lean
git -C grh-lean checkout 72fead102f663d5c7a407964a13dc0cf9d977207
C=72fead102f663d5c7a407964a13dc0cf9d977207
python3 -I tools/grhbuild.py grh-lean/grh-compact rh-compact $C compact
python3 -I tools/grhbuild.py grh-lean/grh rh-readable $C readable
python3 -I tools/gbuild.py rh-compact grh-lean/grh-compact/src
python3 -I tools/gbuild.py rh-readable grh-lean/grh/src
python3 -I tools/bary.py rh-compact 64 40 folders
python3 -I tools/bary.py rh-readable 64 40 folders
python3 -I tools/mkgrh.py .      # regenerate rh-compact/ and rh-readable/ pages from the RH pages
python3 -I tools/mkfermat.py .   # regenerate fermat/ pages likewise
python3 -m http.server 8000      # then open http://localhost:8000/rh-compact/
```
