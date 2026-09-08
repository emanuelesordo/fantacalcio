from pathlib import Path
import re
s=Path('home.html').read_text(encoding='utf-8')
patterns=['queue.*pause','pause.*queue','offusca','auctionQueueRows','allowed.*role','phase.*role','role.*phase','call.*role','auction-phase','auction.*phase']
out=[]
lines=s.splitlines()
for pat in patterns:
    rx=re.compile(pat,re.I)
    out.append(f'===== {pat} =====')
    hits=0
    for i,line in enumerate(lines):
        if rx.search(line):
            hits+=1
            a=max(0,i-4);b=min(len(lines),i+7)
            out.extend(f'{j+1}: {lines[j]}' for j in range(a,b))
            out.append('---')
            if hits>=30: break
    out.append(f'hits={hits}')
Path('.github/V31_QUEUE_ROLES_DIAG.txt').write_text('\n'.join(out),encoding='utf-8')
