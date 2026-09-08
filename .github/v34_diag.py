from pathlib import Path
import re

text=Path('home.html').read_text(encoding='utf-8')
terms=[
'class="auctioneer-console','auctioneer-console-head','auctioneer-console-body','renderAuctioneer',
'function renderAuctionSuggestedCalls','auctionSuggestedCallScore','function prices(','const prices=','function opp(',
'auction-player-hero','auction-status-timer','v14-called-details','data-v23-current','v23-mobile-player',
'auctionQueueRows','auctionMyTeamDashboardData','maxBid','getAuctionBidCapacity',
'<nav','id="main-nav"','data-view="list"','data-view="rosters"','data-view="auction"',
'function renderAuctionLive','function renderAuctionStatus','auction-statusbar'
]
out=[]
for term in terms:
    out.append('\n'+'='*90+'\nTERM: '+term+'\n'+'='*90+'\n')
    matches=list(re.finditer(re.escape(term),text,re.I))[:15]
    if not matches:
        out.append('NO MATCH\n')
        continue
    for i,m in enumerate(matches,1):
        a=max(0,m.start()-3000); b=min(len(text),m.end()+5000)
        out.append(f'\n--- MATCH {i} @ {m.start()} ---\n{text[a:b]}\n')
Path('.github/V34_DIAG.txt').write_text(''.join(out),encoding='utf-8')
print('diagnostic written')
