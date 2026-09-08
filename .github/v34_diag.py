from pathlib import Path
import re

text=Path('home.html').read_text(encoding='utf-8')
terms=[
'class="auctioneer-console','auctioneer-console-head','renderAuctioneer',
'function renderAuctionSuggestedCalls','auctionSuggestedCallScore','function prices(','function opp(',
'auction-player-hero','auction-status-timer','v14-called-details','data-v23-current','v23-mobile-player',
'auctionQueueRows','auctionMyTeamDashboardData','maxBid','id="main-nav"',
'data-view="list"','data-view="rosters"','data-view="auction"','function renderAuctionLive'
]
out=[]
for term in terms:
    out.append('\n'+'='*60+'\nTERM: '+term+'\n'+'='*60+'\n')
    matches=list(re.finditer(re.escape(term),text,re.I))[:3]
    if not matches:
        out.append('NO MATCH\n')
        continue
    for i,m in enumerate(matches,1):
        a=max(0,m.start()-900); b=min(len(text),m.end()+1800)
        out.append(f'\n--- MATCH {i} @ {m.start()} ---\n{text[a:b]}\n')
Path('.github/V34_DIAG.txt').write_text(''.join(out),encoding='utf-8')
print('diagnostic written',len(''.join(out)))
