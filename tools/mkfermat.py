#!/usr/bin/env python3
"""Make fermat/{index,graph,radial}.html from the Riemann Hypothesis pages.

usage: python3 -I mkfermat.py <site_dir>
Every replacement must match exactly the expected number of times, so a change to the
source pages that breaks this script fails loudly instead of leaving RH text behind.
"""
import re, sys

site = sys.argv[1]
GROUPS = """var GROUPS=[
  ['ModularCurve','ModularCurve'],
  ['AlgebraicGeometry','AlgebraicGeometry'],
  ['CerednikDrinfeld','CerednikDrinfeld'],
  ['AutomorphicForm','AutomorphicForm'],
  ['AlgebraicCurve','AlgebraicCurve'],
  ['LanglandsTunnell','LanglandsTunnell'],
  ['WeierstrassCurve','WeierstrassCurve'],
  [null,'All other topics']
];"""
GROUP_TEST = ("var tm=/^(?:Def|Thm|S|D)_([A-Za-z0-9]+)(?:_|\\.lean$)/.exec(p.slice(p.lastIndexOf('/')+1));\n"
              "    for(g=0;g<NG-1;g++) if(tm&&tm[1]===GROUPS[g][0]) break;")
SWITCH = ('<a class="btn" href="../{page}" title="The same view of the Riemann Hypothesis proof">RH</a>\n  ')


def edit(name, reps, switch_before):
    s = open(f'{site}/{name}').read()
    rh_link = '<a class="btn" href="fermat/%s" title="The same view of the Fermat\'s Last Theorem proof">FLT</a>\n  ' % name
    assert s.count(rh_link) == 1, (name, 'FLT link')
    s = s.replace(rh_link, '')
    s = re.sub(r'var GROUPS=\[.*?\n\];', lambda m: GROUPS, s, count=1, flags=re.S)
    for a, b, n in reps:
        c = s.count(a)
        assert c == n, (name, a, c)
        s = s.replace(a, b)
    s = s.replace(switch_before, SWITCH.format(page=name) + switch_before, 1)
    left = re.findall(r'Main\.lean|Riemann|Alpö|alpo\.ge|175,187|17\.4 million|leanprover-community/riemann', s)
    left = [x for x in left if x != 'Riemann']  # the RH switch button's title is fine
    assert not left, (name, left)
    open(f'{site}/fermat/{name}', 'w').write(s)


common = [
    ("<h1><span>RH</span>", "<h1><span>FLT</span>", 1),
]
edit('index.html', common + [
    ('<title>The Riemann Hypothesis in Lean, in one scroll</title>',
     "<title>Fermat's Last Theorem in Lean, in one scroll</title>", 1),
    ('All 17.4 million lines of the Lean 4 proof of the Riemann Hypothesis as one continuously scrolling plain-text page.',
     "All 13.5 million lines of the Lean 4 proof of Fermat's Last Theorem as one continuously scrolling plain-text page.", 1),
    ('<button id="bTop" title="Start of the text (Statements.lean)">Statements</button>',
     '<button id="bTop" title="Start of the text">Start</button>', 1),
    ('<button id="bMain" title="The final theorem, Main.lean, at the very end">Main theorem</button>',
     '<button id="bMain" title="The statement of Fermat\'s Last Theorem, near the very end">The theorem</button>', 1),
    ("$('bMain').onclick=function(){ if(meta){ goLine(meta.mainLine); sc.focus() } };",
     "$('bMain').onclick=function(){ if(meta){ goLine(meta.statementsLine); sc.focus() } };", 1),
    ('title="Dependency graph of all 175,187 files">Map</a>', 'title="Dependency graph of all 60,475 files">Map</a>', 1),
    ('''The complete Lean 4 source of the proof of the Riemann Hypothesis released by
    Levent Alpöge (with Claude) on 20 November 2026, joined into a single plain-text stream:''',
     '''The complete Lean 4 source of the proof of Fermat's Last Theorem published by
    Anthropic (written by Claude) in September 2026, joined into a single plain-text stream:''', 1),
    ('''The archive as published (<a href="https://alpo.ge/remark.pdf" rel="noopener">announcement</a>),
    taken from the first commit of
    <a href="https://github.com/leanprover-community/riemann-hypothesis" rel="noopener">leanprover-community/riemann-hypothesis</a>.
    This is an unofficial reading copy; credit for the proof belongs to its authors.''',
     '''<a href="https://github.com/anthropics/fermats-last-theorem" rel="noopener">anthropics/fermats-last-theorem</a>
    (Apache License 2.0), libraries <code>Definitions</code>, <code>Theorems</code>, <code>P2M</code> and
    <code>FinalCheck.lean</code>. A theorem is stated in <code>Theorems/Thm_X.lean</code> and proved in
    <code>P2M/Sol/S_X.lean</code>. This is an unofficial reading copy.''', 1),
], '<a id="bMap"')

edit('graph.html', common + [
    ('<title>Map of the Lean proof of the Riemann Hypothesis</title>', "<title>Map of the Lean proof of Fermat's Last Theorem</title>", 1),
    ('Interactive dependency graph of the 175,187 Lean files in the proof of the Riemann Hypothesis.',
     "Interactive dependency graph of the 60,475 Lean files in the proof of Fermat's Last Theorem.", 1),
    ('title="The proof as a circle around Main.lean">Circle view</a>', 'title="The proof as a circle around FinalCheck.lean">Circle view</a>', 1),
    ('Loading 175,187 files and their imports…', 'Loading 60,475 files and their imports…', 1),
    ("    for(g=0;g<NG-1;g++) if(p.lastIndexOf(GROUPS[g][0],0)===0) break;", "    " + GROUP_TEST, 1),
    ("ctx.fillText('Main.lean, layer '", "ctx.fillText('FinalCheck.lean, layer '", 1),
    ('everything funnels into Main.lean on the far right.', 'everything funnels into FinalCheck.lean on the far right.', 1),
    ("[['Main.lean',n-1],", "[['FinalCheck.lean',n-1],['The theorem',THM],", 1),
    ("'Up and down: files are grouped by folder, then alphabetical. Within a folder, height means nothing.'",
     "'Up and down: files are grouped by topic (the first word of the file name), then alphabetical. Within a topic, height means nothing.'", 1),
    ('title="Files grouped by folder, then alphabetical">By folder</button>', 'title="Files grouped by topic, then alphabetical">By topic</button>', 1),
    ("'Folders (click to show one)'", "'Topics (click to show one)'", 1),
    ("var folderOrder=null,", "var THM=-1,folderOrder=null,", 1),
    ("    grp[i]=g; gcount[g]++; }", "    grp[i]=g; gcount[g]++; if(p==='Theorems/Thm_fermat_last_theorem.lean') THM=i; }", 1),
], '<a class="btn" href="index.html">')

edit('radial.html', common + [
    ('<title>The Lean proof of the Riemann Hypothesis as a circle</title>', "<title>The Lean proof of Fermat's Last Theorem as a circle</title>", 1),
    ('Radial tree of the 175,187 Lean files in the proof of the Riemann Hypothesis, with Main.lean at the centre.',
     "Radial tree of the 60,475 Lean files in the proof of Fermat's Last Theorem, with FinalCheck.lean at the centre.", 1),
    ("Radial tree of the proof's files around Main.lean.", "Radial tree of the proof's files around FinalCheck.lean.", 1),
    ('Loading 175,187 files and their imports…', 'Loading 60,475 files and their imports…', 1),
    ("    for(g=0;g<NG-1;g++) if(p.lastIndexOf(GROUPS[g][0],0)===0) break;", "    " + GROUP_TEST, 1),
    ("if(p==='Main.lean') MAIN=i;", "if(p==='FinalCheck.lean') MAIN=i;", 1),
    ("/* breadth-first from Main.lean along imports: ring = fewest import steps from Main.", "/* breadth-first from the root along imports: ring = fewest import steps from it.", 1),
    ("/* the route back to Main.lean */", "/* the route back to the root */", 1),
    ("/* Main.lean */", "/* the root */", 1),
    ("ctx.strokeText('Main.lean',mx,my+9); ctx.fillStyle=ink.fg; ctx.fillText('Main.lean',mx,my+9);",
     "ctx.strokeText('FinalCheck.lean',mx,my+9); ctx.fillStyle=ink.fg; ctx.fillText('FinalCheck.lean',mx,my+9);", 1),
    ("'Main.lean is the dot in the centre. Ring 1 is what it imports, ring 2 is what those import, and so on outwards. A file’s ring is the fewest import steps between it and Main.lean.'",
     "'FinalCheck.lean, the file that checks the finished theorem, is the dot in the centre. Ring 1 is what it imports (the statement of the theorem), ring 2 is what that imports, and so on outwards. A file’s ring is the fewest import steps between it and FinalCheck.lean.'", 1),
    ("'rings, counting Main.lean as ring 0'", "'rings, counting FinalCheck.lean as ring 0'", 1),
    ("[['Main.lean',MAIN],", "[['FinalCheck.lean',MAIN],", 1),
    ("the route back to Main.lean.'", "the route back to FinalCheck.lean.'", 1),
    ("' from Main.lean')));", "' from FinalCheck.lean')));", 1),
    ("'Shortest route to Main.lean ('", "'Shortest route to FinalCheck.lean ('", 1),
    ("'Folders (click to show one)'", "'Topics (click to show one)'", 1),
    ("  /* children ordered by folder,", "  /* children ordered by topic,", 1),
], '<a class="btn sp" href="graph.html">')
print('ok')
