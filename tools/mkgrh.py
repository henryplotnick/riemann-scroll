#!/usr/bin/env python3
"""Make rh-compact/ and rh-readable/ {index,graph,radial}.html from the original RH pages.

usage: python3 -I mkgrh.py <site_dir>
Colours follow each edition's own GUIDE.md: the folders of New/ by their role in the
argument, and the background library Lib/ in grey. Every replacement must match the
expected number of times, so a change to the source pages fails loudly.
"""
import re, sys

site = sys.argv[1] if __name__ == '__main__' else None
CORE = ["'Main.lean'", "'Statements.lean'", "'New/Main.lean'"]
EDITIONS = {
    'compact': {
        'dir': 'rh-compact', 'repo_dir': 'grh-compact', 'label': 'compact',
        'groups': [
            ("New: short forms (theorem A)", ['New/Curve/', 'New/Columns/', 'New/TwistedHecke/', 'New/Core/', 'New/Seesaw/']),
            ("New: enough forms (theorem B)", ['New/Filling/', 'New/RealPlace/', 'New/DiscreteSeries/']),
            ("New: long forms (theorem C)", ['New/Heights/', 'New/Rows/', 'New/Exchange/', 'New/Trace/', 'New/GaloisRep/',
                                             'New/Forms/', 'New/SiegelWeil/', 'New/Weil/', 'New/Selmer/', 'New/Patching/', 'New/Lift/']),
            ("New: main inequality, endgame, data", ['New/Endgame/', 'New/Data/'] + [c.strip("'") for c in CORE]),
        ],
        'other': 'Lib: background library',
    },
    'readable': {
        'dir': 'rh-readable', 'repo_dir': 'grh', 'label': 'readable',
        'groups': [
            ("Reduction and main inequality", ['New/Reduction/'] + [c.strip("'") for c in CORE]),
            ("Derivatives of theta functions", ['New/Derivatives/']),
            ("Upper bound: a composite lift", ['New/UpperBound/']),
            ("Spanning: a second moment", ['New/Spanning/']),
            ("Lower bound: the determinant", ['New/Determinant/']),
            ("Lower bound: one lift", ['New/OneLift/']),
            ("Lower bound: congruences", ['New/Congruences/']),
        ],
        'other': 'Lib: background library, and the appendix',
    },
}
GROUP_TEST = "for(g=0;g<NG-1;g++) if(GROUPS[g][0].some(function(k){return p.lastIndexOf(k,0)===0})) break;"


def groups_js(ed):
    rows = ["  [%s,%s]" % ('[' + ','.join("'%s'" % k for k in keys) + ']', repr(lab)) for lab, keys in ed['groups']]
    rows.append("  [null,%r]" % ed['other'])
    return 'var GROUPS=[\n' + ',\n'.join(rows) + '\n];'


def make(name, ed, reps):
    s = open(f'{site}/{name}').read()
    s, k = re.subn(r'var GROUPS=\[.*?\n\];', lambda m: groups_js(ed), s, count=1, flags=re.S)
    assert k == (0 if name == 'index.html' else 1), name
    reps = reps + [
        ("var HERE=''", "var HERE='%s'" % ed['dir'], 1),
        ("<h1><span>RH</span>", "<h1><span>RH · %s</span>" % ed['label'], 1),
    ]
    if name != 'index.html':
        reps += [
            ("for(g=0;g<NG-1;g++) if(p.lastIndexOf(GROUPS[g][0],0)===0) break;", GROUP_TEST, 1),
            # the catch-all group (Lib) is always the neutral grey, however many groups come before it
            ("col.push(g('--g'+i))", "col.push(g('--g'+(i===NG-1?7:i)))", 1),
            ('Loading 175,187 files and their imports…', 'Loading the files and their imports…', 1),
        ]
    for a, b, n in reps:
        c = s.count(a)
        assert c == n, (ed['dir'], name, a[:70], c)
        s = s.replace(a, b)
    left = re.findall(r'175,187|17\.4 million|alpo\.ge/remark|leanprover-community/riemann', s)
    assert not left, (ed['dir'], name, left)
    open(f"{site}/{ed['dir']}/{name}", 'w').write(s)


for key, ed in (EDITIONS.items() if __name__ == '__main__' else []):
    ttl = "the Riemann Hypothesis (%s edition)" % ed['label']
    src = ('<a href="https://github.com/lsernau/grh-lean" rel="noopener">lsernau/grh-lean</a>, folder '
           '<code>%s/</code> (Apache License 2.0). Its <code>GUIDE.md</code> is the place to start reading. '
           'This is an unofficial reading copy.' % ed['repo_dir'])
    make('index.html', ed, [
        ('<title>The Riemann Hypothesis in Lean, in one scroll</title>',
         '<title>The Riemann Hypothesis in Lean (%s edition), in one scroll</title>' % ed['label'], 1),
        ('All 17.4 million lines of the Lean 4 proof of the Riemann Hypothesis as one continuously scrolling plain-text page.',
         'The %s edition of the shorter Lean 4 proof of the Riemann Hypothesis as one continuously scrolling plain-text page.' % ed['label'], 1),
        ('<button id="bTop" title="Start of the text (Statements.lean)">Statements</button>',
         '<button id="bTop" title="Start of the text">Start</button>', 1),
        ('title="Dependency graph of all 175,187 files">Map</a>', 'title="Dependency graph of every file">Map</a>', 1),
        ('''The complete Lean 4 source of the proof of the Riemann Hypothesis released by
    Levent Alpöge (with Claude) on 20 November 2026, joined into a single plain-text stream:''',
         '''The %s edition of the shorter Lean 4 proof of the Riemann Hypothesis and GRH, published
    by Anthropic and Claude in November 2026 and based on Levent Alpöge's proof, joined into a single
    plain-text stream:''' % ed['label'], 1),
        ('''The archive as published (<a href="https://alpo.ge/remark.pdf" rel="noopener">announcement</a>),
    taken from the first commit of
    <a href="https://github.com/leanprover-community/riemann-hypothesis" rel="noopener">leanprover-community/riemann-hypothesis</a>.
    This is an unofficial reading copy; credit for the proof belongs to its authors.''', src, 1),
    ])
    make('graph.html', ed, [
        ('<title>Map of the Lean proof of the Riemann Hypothesis</title>', '<title>Map of the Lean proof of %s</title>' % ttl, 1),
        ('Interactive dependency graph of the 175,187 Lean files in the proof of the Riemann Hypothesis.',
         'Interactive dependency graph of the Lean files in the proof of %s.' % ttl, 1),
    ])
    make('radial.html', ed, [
        ('<title>The Lean proof of the Riemann Hypothesis as a circle</title>', '<title>The Lean proof of %s as a circle</title>' % ttl, 1),
        ('Radial tree of the 175,187 Lean files in the proof of the Riemann Hypothesis, with Main.lean at the centre.',
         'Radial tree of the Lean files in the proof of %s, with Main.lean at the centre.' % ttl, 1),
    ])
print('ok')
