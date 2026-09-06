from pathlib import Path

p = Path('home.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'marker not found: {label}')
    s = s.replace(old, new, 1)

# 1) TERMINA ASTA: dopo la mutation ricarica subito lo stato strutturale,
# così la UI passa a review/riepilogo senza attendere reconcile/re-entry nella tab.
old_finish = """            await auctionAction(
              {
                action:
                  'finishAuction',

                sessionId:
                  s.id
              },
              'Asta terminata. Riepilogo rose disponibile.'
            );"""
new_finish = """            await auctionAction(
              {
                action:
                  'finishAuction',

                sessionId:
                  s.id
              },
              'Asta terminata. Riepilogo rose disponibile.'
            );

            await loadAuction({
              quiet: true
            });"""
replace_once(old_finish, new_finish, 'finish auction immediate refresh')

# 2) Prezzi suggeritore: Number(null) === 0 causava SUGG/MAX a zero quando
# maxBid non era calcolabile/mostrato come —. Limita solo con un maxBid reale > 0.
old_prices = "function prices(p,score,o){const info=auctionMyTeamDashboardData(),pf=pref(p),ref=Math.max(1,Number(p.pfc||p.pma||p.quotation||1)),mk=market(p),prf=state.v8Profile?.profile||'balanced',mult=prf==='aggressive'?1.06:prf==='conservative'?.95:1,q=1+cl(trend(p),-.15,.15)*.25+(prs(p)/100-.65)*.08;let s=Math.max(1,Math.round(ref*mk*q*(.93+o/100*.15)*mult)),c=Math.max(s,Math.round(s*(1.10+Math.max(0,score-65)/500)));if(pf?.expected_spend!=null)s=Math.max(1,Math.round((s*2+Number(pf.expected_spend))/3));if(pf?.max_price!=null)c=Math.min(c,Math.max(1,Number(pf.max_price)));const mb=Number(info?.maxBid);if(Number.isFinite(mb)){c=Math.min(c,Math.max(0,mb));s=Math.min(s,c)}return{suggested:s,ceiling:c,marketFactor:mk}}"
new_prices = "function prices(p,score,o){const info=auctionMyTeamDashboardData(),pf=pref(p),ref=Math.max(1,Number(p.pfc||p.pma||p.quotation||1)),mk=market(p),prf=state.v8Profile?.profile||'balanced',mult=prf==='aggressive'?1.06:prf==='conservative'?.95:1,q=1+cl(trend(p),-.15,.15)*.25+(prs(p)/100-.65)*.08;let s=Math.max(1,Math.round(ref*mk*q*(.93+o/100*.15)*mult)),c=Math.max(s,Math.round(s*(1.10+Math.max(0,score-65)/500)));if(pf?.expected_spend!=null&&String(pf.expected_spend).trim()!=='')s=Math.max(1,Math.round((s*2+Number(pf.expected_spend))/3));if(pf?.max_price!=null&&String(pf.max_price).trim()!=='')c=Math.min(c,Math.max(1,Number(pf.max_price)));const rawMb=info?.maxBid,mb=rawMb===null||rawMb===undefined||String(rawMb).trim()===''?null:Number(rawMb);if(Number.isFinite(mb)&&mb>0){c=Math.min(c,mb);s=Math.min(s,c)}return{suggested:Math.max(1,s),ceiling:Math.max(1,c),marketFactor:mk}}"
replace_once(old_prices, new_prices, 'V8 strategic prices')

# 3) Layout suggeritore: ogni giocatore resta SEMPRE su una singola row.
# La griglia decide da sola 1/2 colonne in base alla larghezza disponibile,
# invece di forzare 2 colonne in base all'altezza viewport.
style = r'''
  <style id="v10-suggester-row-fix">
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-calls{
      max-height:170px!important;
      overflow:hidden!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-calls .auction-suggested-list{
      display:grid!important;
      grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))!important;
      grid-auto-flow:row!important;
      gap:3px!important;
      max-height:138px!important;
      overflow-y:auto!important;
      overflow-x:hidden!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-row{
      width:100%!important;
      min-width:0!important;
      min-height:29px!important;
      display:grid!important;
      grid-template-columns:auto minmax(0,1fr) auto auto!important;
      grid-template-rows:1fr!important;
      align-items:center!important;
      gap:4px!important;
      padding:3px 4px!important;
      overflow:hidden!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-row > *{
      min-width:0!important;
      grid-row:1!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-roles{
      display:flex!important;
      flex-wrap:nowrap!important;
      align-items:center!important;
      gap:2px!important;
      overflow:hidden!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-copy{
      min-width:0!important;
      overflow:hidden!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .v8n{
      min-width:0!important;
      overflow:hidden!important;
      flex-wrap:nowrap!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .v8n strong,
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-copy > small{
      min-width:0!important;
      overflow:hidden!important;
      text-overflow:ellipsis!important;
      white-space:nowrap!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .v8n em{
      max-width:108px!important;
      overflow:hidden!important;
      text-overflow:ellipsis!important;
      white-space:nowrap!important;
      flex:0 1 auto!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-prices{
      min-width:45px!important;
      width:auto!important;
      display:grid!important;
      justify-items:end!important;
      white-space:nowrap!important;
      flex:0 0 auto!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-suggest-actions{
      min-width:0!important;
      display:flex!important;
      flex-wrap:nowrap!important;
      align-items:center!important;
      justify-content:flex-end!important;
      gap:2px!important;
      white-space:nowrap!important;
      overflow:visible!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-dismiss{
      width:17px!important;
      min-width:17px!important;
      height:17px!important;
      min-height:17px!important;
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-suggested-action{
      width:auto!important;
      min-width:39px!important;
      height:21px!important;
      min-height:21px!important;
      padding:2px 4px!important;
      font-size:5.5px!important;
      white-space:nowrap!important;
    }
    @media (max-width:420px){
      html body.modern-glass #view-auction .auction-free-suggestions .v8n em{display:none!important}
      html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-prices{min-width:40px!important}
    }
  </style>
'''
if 'id="v10-suggester-row-fix"' in s:
    raise SystemExit('style already present')
replace_once('\n</head>', style + '\n</head>', 'head close')

p.write_text(s, encoding='utf-8')
