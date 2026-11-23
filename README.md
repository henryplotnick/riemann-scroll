# The Riemann Hypothesis in Lean, in one scroll

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
```

## Preview locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```
