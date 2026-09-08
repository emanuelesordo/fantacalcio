from pathlib import Path
import re
s=Path('home.html').read_text(encoding='utf-8')
lines=s.splitlines()
out=[]

def block_for(term,before=20,after=80,limit=10):
    out.append(f'===== {term} =====')
    n=0
    for i,line in enumerate(lines):
        if term.lower() in line.lower():
            n+=1
            a=max(0,i-before);b=min(len(lines),i+after)
            out.extend(f'{j+1}: {lines[j]}' for j in range(a,b))
            out.append('---')
            if n>=limit:break
    out.append(f'hits={n}')

for t in [
    'function auctionPlayerMatchesCurrentRolePhase',
    'function auctionRolePhaseLabel',
    'function auctionCurrentRolePhase',
    'rolePhase',
    'auction-queue-autoplay',
    'setCallQueuePaused',
    'patchAuctionCallQueueUi',
    'data-queue-pause',
    'auction-queue-pause',
    'callQueueSettings',
]: block_for(t)
Path('.github/V31_QUEUE_ROLES_DIAG.txt').write_text('\n'.join(out),encoding='utf-8')
