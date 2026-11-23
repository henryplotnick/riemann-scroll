#!/usr/bin/env python3
"""Fermat's Last Theorem variant of build.py: same output format.

usage: python3 -I fbuild.py <repo_root> <out_dir> <source_commit>
Reads the Lean libraries Definitions/, Theorems/, P2M/ and FinalCheck.lean.
Only reads files as bytes/text; never executes anything from the project.
"""
import gzip, io, json, os, re, sys

CHUNK_LINES = 5000
IMPORT_RE = re.compile(r'^\s*(?:(?:public|private|meta)\s+)*import\s+(?:all\s+)?([^\s]+)')


def main():
    root, out, commit = sys.argv[1], sys.argv[2], sys.argv[3]
    src = root
    paths = ['FinalCheck.lean']
    for lib in ('Definitions', 'Theorems', 'P2M'):
        for d, dirs, files in os.walk(os.path.join(src, lib)):
            dirs.sort()
            for f in sorted(files):
                if f.endswith('.lean'):
                    paths.append(os.path.relpath(os.path.join(d, f), src))
    paths.sort()
    mod_of = {p: p[:-5].replace(os.sep, '.') for p in paths}
    path_of = {m: p for p, m in mod_of.items()}
    print('files', len(paths), file=sys.stderr)

    # read imports (header only: imports must precede everything else in Lean)
    deps = {}
    for p in paths:
        ds = []
        with open(os.path.join(src, p), 'r', encoding='utf-8', errors='replace', newline='') as fh:
            in_block = False
            for line in fh:
                s = line.strip()
                if in_block:
                    if '-/' in s:
                        in_block = False
                    continue
                if not s or s.startswith('--'):
                    continue
                if s.startswith('/-'):
                    if '-/' not in s:
                        in_block = True
                    continue
                if s == 'module' or s.startswith('prelude'):
                    continue
                m = IMPORT_RE.match(line)
                if not m:
                    break
                q = path_of.get(m.group(1))
                if q is not None:
                    ds.append(q)
        deps[p] = ds

    # dependency-first order (iterative DFS post-order)
    order, state = [], {}

    def visit(start):
        if start in state:
            return
        stack = [(start, iter(deps[start]))]
        state[start] = 1
        while stack:
            node, it = stack[-1]
            for d in it:
                if d not in state:
                    state[d] = 1
                    stack.append((d, iter(deps[d])))
                    break
            else:
                state[node] = 2
                order.append(node)
                stack.pop()

    visit('FinalCheck.lean')
    n_main = len(order)
    for p in paths:
        visit(p)
    assert len(order) == len(paths) == len(set(order))
    pos = {p: i for i, p in enumerate(order)}
    for p in paths:
        for d in deps[p]:
            assert pos[d] < pos[p], (p, d)
    print('reachable from Main', n_main, 'other', len(paths) - n_main, file=sys.stderr)

    os.makedirs(os.path.join(out, 'c'), exist_ok=True)
    state_ = {'buf': [], 'n': 0, 'chunk': 0, 'gz': 0, 'raw': 0}

    def flush():
        if not state_['buf']:
            return
        data = ('\n'.join(state_['buf']) + '\n').encode('utf-8')
        bio = io.BytesIO()
        with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9, mtime=0) as g:
            g.write(data)
        b = bio.getvalue()
        with open(os.path.join(out, 'c', '%05d.gz' % state_['chunk']), 'wb') as fh:
            fh.write(b)
        state_['gz'] += len(b)
        state_['raw'] += len(data)
        state_['chunk'] += 1
        state_['buf'] = []

    def emit(line):
        state_['buf'].append(line)
        state_['n'] += 1
        if len(state_['buf']) == CHUNK_LINES:
            flush()

    PREFACE_LEN = 16
    preface_at = state_['n']
    for _ in range(PREFACE_LEN):
        emit('')  # placeholder; rewritten below once totals are known

    index = []  # (start_line0, path)
    src_lines = 0
    marks = {}
    for i, p in enumerate(order):
        if i == n_main and n_main < len(order):
            marks['appendix'] = state_['n']
            emit('')
            emit('-- ' + '#' * 76)
            emit('-- APPENDIX: the %d files below are in the published archive but are not' % (len(order) - n_main))
            emit('-- imported, directly or indirectly, by Main.lean.')
            emit('-- ' + '#' * 76)
        with open(os.path.join(src, p), 'rb') as fh:
            text = fh.read().decode('utf-8', errors='replace')
        lines = text.split('\n')
        if lines and lines[-1] == '':
            lines.pop()
        emit('')
        index.append((state_['n'], p))
        if p in ('FinalCheck.lean', 'Theorems/Thm_fermat_last_theorem.lean'):
            marks[p] = state_['n']
        emit('-- ════════ [%d/%d] %s ════════' % (i + 1, len(order), p.replace(os.sep, '/')))
        for ln in lines:
            emit(ln.rstrip('\r'))
        src_lines += len(lines)
    flush()
    total = state_['n']

    preface = [
        '-- ' + '=' * 76,
        "-- The Lean 4 proof of Fermat's Last Theorem published by Anthropic (written by",
        '-- Claude) in September 2026, combined into one continuous plain-text stream.',
        '--',
        '-- Source: github.com/anthropics/fermats-last-theorem @ %s' % commit[:12],
        '--   (Apache License 2.0; see LICENSE and NOTICE in that repository).',
        '-- Contents: %s files, %s source lines; %s lines here including the' % (
            format(len(order), ','), format(src_lines, ','), format(total, ',')),
        '--   one-line "-- ════════ [n/N] path ════════" header added before each file.',
        '-- Order: every file appears after the files it imports. The last file,',
        '--   FinalCheck.lean, is at line %s; the theorem itself is stated in' % format(marks['FinalCheck.lean'] + 1, ','),
        '--   Theorems/Thm_fermat_last_theorem.lean, at line %s.' % format(marks['Theorems/Thm_fermat_last_theorem.lean'] + 1, ','),
        '-- Nothing in the Lean files themselves has been changed. This page is an',
        '--   unofficial reading copy; all credit for the proof belongs to its authors.',
        '-- ' + '=' * 76,
        '',
        '',
    ]
    assert len(preface) == PREFACE_LEN
    # rewrite chunk 0 with the real preface
    p0 = os.path.join(out, 'c', '00000.gz')
    with gzip.open(p0, 'rb') as g:
        l0 = g.read().decode('utf-8').split('\n')
    l0[preface_at:preface_at + PREFACE_LEN] = preface
    bio = io.BytesIO()
    with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9, mtime=0) as g:
        g.write('\n'.join(l0).encode('utf-8'))
    with open(p0, 'wb') as fh:
        fh.write(bio.getvalue())

    bio = io.BytesIO()
    with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9, mtime=0) as g:
        g.write(''.join('%d\t%s\n' % (s, p.replace(os.sep, '/')) for s, p in index).encode('utf-8'))
    with open(os.path.join(out, 'files.gz'), 'wb') as fh:
        fh.write(bio.getvalue())

    meta = {
        'totalLines': total, 'chunkLines': CHUNK_LINES, 'chunks': state_['chunk'],
        'files': len(order), 'sourceLines': src_lines, 'filesFromMain': n_main,
        'mainLine': marks['FinalCheck.lean'], 'statementsLine': marks['Theorems/Thm_fermat_last_theorem.lean'],
        'appendixLine': marks.get('appendix'), 'commit': commit,
    }
    with open(os.path.join(out, 'meta.json'), 'w') as fh:
        json.dump(meta, fh)
    print(json.dumps(meta), file=sys.stderr)
    print('raw bytes', state_['raw'], 'gz bytes', state_['gz'], file=sys.stderr)


if __name__ == '__main__':
    main()
