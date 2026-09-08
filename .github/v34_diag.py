from pathlib import Path
import re

text=Path('home.html').read_text(encoding='utf-8')
terms=[
'auctioneer-console','auction-suggested-calls','giocatore del momento','strategicThresholdPrice','strategicExpectedPrice',
'renderAuctionSuggested','suggested calls','data-list-sort','v14-called-details','auction-statusbar','auction-timer',
'function renderAuctionLive','maxBid','auctionBidCapacity','auctionOwnCallTurn','main-nav','nav-btn'
]
out=[]
for term in terms:
    out.append('\n'+'='*90+'\nTERM: '+term+'\n'+'='*90+'\n')
    matches=list(re.finditer(re.escape(term),text,re.I))[:12]
    if not matches:
        out.append('NO MATCH\n')
        continue
    for i,m in enumerate(matches,1):
        a=max(0,m.start()-1800); b=min(len(text),m.end()+3000)
        snippet=text[a:b]
        out.append(f'\n--- MATCH {i} @ {m.start()} ---\n{snippet}\n')
Path('.github/V34_DIAG.txt').write_text(''.join(out),encoding='utf-8')
print('diagnostic written')
