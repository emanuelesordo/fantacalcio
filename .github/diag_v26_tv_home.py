from pathlib import Path
import re

text=Path('home.html').read_text(encoding='utf-8')
lines=text.splitlines()
terms=['view-tv','renderTv','renderTV','renderTele','tv-','view-home','home-layout','renderHome','renderRosters','rosters-grid']
out=[]
for term in terms:
    out.append(f'===== {term} =====')
    hits=[i for i,l in enumerate(lines) if term.lower() in l.lower()]
    for i in hits[:20]:
        a=max(0,i-18); b=min(len(lines),i+80)
        out.append(f'--- lines {a+1}-{b} ---')
        out.extend(f'{j+1}: {lines[j]}' for j in range(a,b))
    if not hits: out.append('(no hits)')
Path('.github/V26_TV_HOME_DIAG.txt').write_text('\n'.join(out),encoding='utf-8')
