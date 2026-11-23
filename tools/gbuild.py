#!/usr/bin/env python3
"""Write graph.bin.gz: the file-level import graph, in the same file order as files.gz.

usage: python3 -I gbuild.py <site_dir> <project_src_dir>
Format (little-endian int32): n, E, offsets[n+1], targets[E]  (targets = files that node i imports)
"""
import gzip, io, os, re, struct, sys
from array import array

SITE, SRC = sys.argv[1], sys.argv[2]
IMPORT_RE = re.compile(r'^\s*(?:(?:public|private|meta)\s+)*import\s+(?:all\s+)?([^\s]+)')
paths = [l.split('\t')[1] for l in gzip.open(SITE + '/files.gz', 'rt', encoding='utf-8').read().split('\n') if l]
idx = {p[:-5].replace('/', '.'): i for i, p in enumerate(paths)}
offs, tg = array('i', [0]), array('i')
for i, p in enumerate(paths):
    ds = set()
    with open(os.path.join(SRC, p), encoding='utf-8', errors='replace') as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith('--'):
                continue
            m = IMPORT_RE.match(line)
            if not m:
                break
            j = idx.get(m.group(1))
            if j is not None:
                assert j < i, (p, m.group(1))
                ds.add(j)
    tg.extend(sorted(ds))
    offs.append(len(tg))
if sys.byteorder != 'little':
    offs.byteswap(); tg.byteswap()
raw = struct.pack('<ii', len(paths), len(tg)) + offs.tobytes() + tg.tobytes()
bio = io.BytesIO()
with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9, mtime=0) as g:
    g.write(raw)
open(SITE + '/graph.bin.gz', 'wb').write(bio.getvalue())
print('nodes', len(paths), 'edges', len(tg), 'raw', len(raw), 'gz', len(bio.getvalue()))
