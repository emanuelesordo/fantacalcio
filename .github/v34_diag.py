from pathlib import Path
import re
text=Path('home.html').read_text(encoding='utf-8')
terms=['function renderAuctionCallQueue','renderAuctionCallQueue =','data-queue-remove','data-call-queue','auction-queue-row','auction-call-queue']
out=[]
for term in terms:
    out.append('\n'+'='*60+'\nTERM: '+term+'\n'+'='*60+'\n')
    for i,m in enumerate(list(re.finditer(re.escape(term),text,re.I))[:8],1):
        a=max(0,m.start()-1800);b=min(len(text),m.end()+3500)
        out.append(f'\n--- MATCH {i} @ {m.start()} ---\n{text[a:b]}\n')
Path('.github/V34_DIAG.txt').write_text(''.join(out),encoding='utf-8')
print('done',len(''.join(out)))
