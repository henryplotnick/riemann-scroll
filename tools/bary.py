#!/usr/bin/env python3
"""Barycenter ordering for the map: place each file near the files it is connected to.

usage: python3 -I bary.py <site_dir> [sweeps] [combined_sweeps] [topics|folders]
Reads graph.bin.gz + files.gz from the site, writes order.bin.gz there:
little-endian uint16 per node = its slot within its layer (top to bottom).
"""
import gzip, struct, sys
import numpy as np

GROUPS = ['Development/AbelianVarietyTheory/', 'Development/AutomorphicArithmetic/', 'Formalism/',
          'Development/AutomorphicSpectrum/', 'GroundTheory/', 'Development/WeilBound/', 'ReciprocityTheory/']
TOPICS = ['ModularCurve', 'AlgebraicGeometry', 'CerednikDrinfeld', 'AutomorphicForm', 'AlgebraicCurve',
          'LanglandsTunnell', 'WeierstrassCurve']


def main():
    site = sys.argv[1]
    sweeps = int(sys.argv[2]) if len(sys.argv) > 2 else 24
    BOTH = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    raw = gzip.open(site + '/graph.bin.gz').read()
    n, E = struct.unpack_from('<ii', raw)
    off = np.frombuffer(raw, '<i4', n + 1, 8).astype(np.int64)
    tg = np.frombuffer(raw, '<i4', E, 8 + 4 * (n + 1)).astype(np.int64)
    paths = [l.split('\t')[1] for l in gzip.open(site + '/files.gz', 'rt', encoding='utf-8').read().split('\n') if l]
    src = np.repeat(np.arange(n), np.diff(off))  # importer
    dst = tg                                      # imported

    layer = np.zeros(n, np.int64)
    for i in range(n):
        a, b = off[i], off[i + 1]
        if b > a:
            layer[i] = layer[tg[a:b]].max() + 1
    L = int(layer.max()) + 1
    lw = np.bincount(layer, minlength=L)

    # starting point = the folder layout the page already uses
    if len(sys.argv) > 4 and sys.argv[4] == 'topics':   # Fermat project: colour by topic in the file name
        import re
        tre = re.compile(r'^(?:Def|Thm|S|D)_([A-Za-z0-9]+)(?:_|\.lean$)')
        def g_of(p):
            m = tre.match(p.rsplit('/', 1)[-1])
            return TOPICS.index(m.group(1)) if m and m.group(1) in TOPICS else len(TOPICS)
        grp = np.array([g_of(p) for p in paths])
    elif len(sys.argv) > 4 and sys.argv[4] == 'folders':  # any project: start from second-level folders
        names = sorted({'/'.join(p.split('/')[:2]) for p in paths})
        grp = np.array([names.index('/'.join(p.split('/')[:2])) for p in paths])
    else:
        grp = np.array([next((g for g, k in enumerate(GROUPS) if p.startswith(k)), len(GROUPS)) for p in paths])
    alpha = np.argsort(np.argsort(np.array(paths, dtype=object)))
    order0 = np.lexsort((alpha, grp, layer))
    members = [None] * L
    slot = np.zeros(n, np.int64)
    s = 0
    for Lx in range(L):
        members[Lx] = order0[s:s + lw[Lx]]
        slot[members[Lx]] = np.arange(lw[Lx])
        s += lw[Lx]

    def ycoord():
        return slot - lw[layer] / 2.0

    def cost(y):
        return float(np.abs(y[src] - y[dst]).sum())

    # edges grouped by the layer of each endpoint, for the two sweep directions
    by_src = [np.nonzero(layer[src] == Lx)[0] for Lx in range(L)]
    by_dst = [np.nonzero(layer[dst] == Lx)[0] for Lx in range(L)]

    def place(Lx, nodes_side, other_side, idx, y):
        mem = members[Lx]
        if len(mem) < 2 or len(idx) == 0:
            return
        a = nodes_side[idx]
        tot = np.bincount(a, weights=y[other_side[idx]], minlength=n)[mem]
        cnt = np.bincount(a, minlength=n)[mem]
        cur = y[mem]
        bc = np.where(cnt > 0, tot / np.maximum(cnt, 1), cur)
        new = mem[np.lexsort((cur, bc))]   # ties keep current order
        members[Lx] = new
        slot[new] = np.arange(len(new))
        y[new] = np.arange(len(new)) - len(new) / 2.0

    def place_both(Lx, y):
        mem = members[Lx]
        i1, i2 = by_src[Lx], by_dst[Lx]
        if len(mem) < 2 or (len(i1) == 0 and len(i2) == 0):
            return
        tot = (np.bincount(src[i1], weights=y[dst[i1]], minlength=n)
               + np.bincount(dst[i2], weights=y[src[i2]], minlength=n))[mem]
        cnt = (np.bincount(src[i1], minlength=n) + np.bincount(dst[i2], minlength=n))[mem]
        cur = y[mem]
        bc = np.where(cnt > 0, tot / np.maximum(cnt, 1), cur)
        new = mem[np.lexsort((cur, bc))]
        members[Lx] = new
        slot[new] = np.arange(len(new))
        y[new] = np.arange(len(new)) - len(new) / 2.0

    y = ycoord()
    c0 = cost(y)
    best, best_slot = c0, slot.copy()
    print('start (folder layout): mean |dy| per edge %.1f' % (c0 / E), file=sys.stderr)
    for it in range(sweeps):
        if it >= sweeps - BOTH:
            rng = range(L) if it % 2 == 0 else range(L - 1, -1, -1)
            for Lx in rng:
                place_both(Lx, y)
        elif it % 2 == 0:
            for Lx in range(1, L):            # left to right: follow what each file imports
                place(Lx, src, dst, by_src[Lx], y)
        else:
            for Lx in range(L - 2, -1, -1):   # right to left: follow what imports each file
                place(Lx, dst, src, by_dst[Lx], y)
        c = cost(y)
        tag = ''
        if c < best:
            best, best_slot, tag = c, slot.copy(), ' *'
        print('sweep %2d  mean |dy| per edge %.1f%s' % (it + 1, c / E, tag), file=sys.stderr)

    # sanity: each layer's slots are a permutation
    for Lx in range(L):
        m = np.nonzero(layer == Lx)[0]
        assert sorted(best_slot[m].tolist()) == list(range(len(m)))
    with open(site + '/order.bin.gz', 'wb') as raw_fh:
        with gzip.GzipFile(fileobj=raw_fh, mode='wb', compresslevel=9, mtime=0) as fh:
            fh.write(best_slot.astype('<u2').tobytes())
    print('best mean |dy| %.1f (%.0f%% shorter than folder layout)' % (best / E, 100 * (1 - best / c0)), file=sys.stderr)


if __name__ == '__main__':
    main()
