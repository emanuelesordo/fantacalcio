from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

# Remove a previous V25 block if the workflow is re-run.
text=re.sub(r'\n<style id="v25-auction-layout-mobile-style">.*?</style>\n', '\n', text, flags=re.S)
text=re.sub(r'\n<script id="v25-auction-layout-mobile-runtime">.*?</script>\n', '\n', text, flags=re.S)

# The live app header is hidden during the auction, so the mobile mode selector
# must live in the visible auction status bar, not in .app-head.
old="const host=qs('.app-head .head-actions')||qs('.head-actions');"
new="const host=qs('#view-auction .auction-statusbar')||qs('.app-head .head-actions')||qs('.head-actions');"
if old in text:
    text=text.replace(old,new)

style=r'''
<style id="v25-auction-layout-mobile-style">
/* V25: final authority for live auction selection row and free-agent table. */
#view-auction .auction-caller-controls{
  display:grid!important;
  grid-template-columns:minmax(0,1fr) 68px 82px!important;
  grid-template-rows:auto!important;
  gap:4px!important;
  align-items:end!important;
  width:100%!important;
  min-width:0!important;
}
#view-auction .auction-caller-controls .auction-command-search{
  grid-column:1!important;grid-row:1!important;min-width:0!important;
}
#view-auction .auction-caller-controls .auction-command-base{
  grid-column:2!important;grid-row:1!important;min-width:0!important;
}
#view-auction .auction-caller-controls #auction-call-confirm,
#view-auction .auction-caller-controls .auction-top-call{
  grid-column:3!important;grid-row:1!important;
  width:82px!important;min-width:82px!important;max-width:82px!important;
  height:32px!important;min-height:32px!important;margin:0!important;
  align-self:end!important;padding:2px 5px!important;font-size:8.5px!important;
}

#view-auction .auction-free-fixed,
#view-auction .auction-free-fixed .drawer-table,
#view-auction .auction-free-table-wrap{
  width:100%!important;min-width:0!important;max-width:100%!important;
}
#view-auction .auction-free-fixed .player-table,
#view-auction .auction-free-table{
  width:100%!important;min-width:0!important;max-width:100%!important;
  table-layout:auto!important;border-spacing:0!important;
}
#view-auction .auction-free-table col{width:auto!important}
#view-auction .auction-free-table col.auction-col-role{width:46px!important}
#view-auction .auction-free-table col.auction-col-name{width:1%!important}
#view-auction .auction-free-table col.auction-col-badge{width:54px!important}
#view-auction .auction-free-table col.auction-col-presence{width:52px!important}
#view-auction .auction-free-table col.auction-col-pfc,
#view-auction .auction-free-table col.auction-col-pma,
#view-auction .auction-free-table col.auction-col-delta,
#view-auction .auction-free-table col.auction-col-fm,
#view-auction .auction-free-table col.auction-col-index{width:48px!important}
#view-auction .auction-free-table col.auction-col-favorite{width:48px!important}
#view-auction .auction-free-table col.auction-col-action{width:62px!important}

#view-auction .auction-free-table th,
#view-auction .auction-free-table td{
  min-width:0!important;box-sizing:border-box!important;
  padding-left:3px!important;padding-right:3px!important;
  white-space:nowrap!important;
}
#view-auction .auction-free-table th:nth-child(2),
#view-auction .auction-free-table td:nth-child(2){
  width:1%!important;max-width:190px!important;
}
#view-auction .auction-free-table td:nth-child(2) .player-main{
  min-width:0!important;width:max-content!important;max-width:185px!important;
}
#view-auction .auction-free-table td:nth-child(2) .player-name,
#view-auction .auction-free-table td:nth-child(2) strong{
  max-width:150px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;
}
#view-auction .auction-free-table th:nth-last-child(2),
#view-auction .auction-free-table td:nth-last-child(2){
  min-width:46px!important;width:46px!important;overflow:visible!important;
}
#view-auction .auction-free-table th:last-child,
#view-auction .auction-free-table td:last-child{
  min-width:60px!important;width:60px!important;overflow:visible!important;
}
#view-auction .auction-free-table .num,
#view-auction .auction-free-table td:nth-child(n+4):nth-child(-n+9){
  font-size:9.5px!important;font-variant-numeric:tabular-nums!important;
}

/* The mobile profile switch belongs to the visible live-auction header. */
#view-auction .auction-statusbar .v23-header-mode{
  display:none;align-items:center;gap:2px;padding:2px;
  border:1px solid rgba(87,132,182,.55);border-radius:8px;background:rgba(5,20,36,.82);
}
#view-auction .auction-statusbar .v23-header-mode button{
  min-height:26px!important;height:26px!important;padding:2px 6px!important;
  border-radius:6px!important;background:transparent!important;color:var(--soft)!important;
  font-size:7px!important;letter-spacing:.03em!important;
}
#view-auction .auction-statusbar .v23-header-mode button.active{
  background:var(--primary)!important;color:#fff!important;
}

/* Mobile navigation: every tab always carries both its icon and its label. */
@media(max-width:820px){
  body.modern-glass #main-nav .nav-btn,
  #main-nav .nav-btn{
    display:grid!important;grid-template-rows:22px auto!important;place-items:center!important;
    gap:2px!important;min-width:68px!important;min-height:50px!important;padding:4px 7px!important;
    border-radius:13px!important;
  }
  #main-nav .nav-btn .nav-glyph{
    display:grid!important;width:22px!important;height:22px!important;place-items:center!important;
    font-size:17px!important;line-height:1!important;
  }
  #main-nav .nav-btn > span:last-child{
    display:block!important;font-size:8px!important;font-weight:800!important;line-height:1!important;
  }
  body.auction-live #view-auction .auction-statusbar .v23-header-mode{
    display:flex!important;
  }
}
</style>
'''

runtime=r'''
<script id="v25-auction-layout-mobile-runtime">
(()=>{
  const qs=(s,r=document)=>r.querySelector(s);
  const isPhone=()=>window.matchMedia('(max-width:820px)').matches;

  function enforceCallRow(){
    const host=qs('#view-auction .auction-caller-controls');
    const search=host?.querySelector('.auction-command-search');
    const base=host?.querySelector('.auction-command-base');
    const call=qs('#view-auction #auction-call-confirm');
    if(!host||!search||!base||!call)return;
    if(call.parentElement!==host) host.appendChild(call);
    call.classList.add('auction-top-call');
  }

  function moveMobileModeToLiveHeader(){
    if(!isPhone()||!document.body.classList.contains('auction-live'))return;
    const mode=qs('.v23-header-mode');
    const status=qs('#view-auction .auction-statusbar');
    if(mode&&status&&mode.parentElement!==status) status.appendChild(mode);
  }

  function refresh(){
    enforceCallRow();
    moveMobileModeToLiveHeader();
  }

  const observer=new MutationObserver(()=>requestAnimationFrame(refresh));
  observer.observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('resize',refresh,{passive:true});
  window.addEventListener('hashchange',refresh);
  document.addEventListener('DOMContentLoaded',refresh,{once:true});
  setTimeout(refresh,0);
})();
</script>
'''

if '</head>' not in text or '</body>' not in text:
    raise RuntimeError('home.html closing markers not found')
text=text.replace('</head>', style+'\n</head>',1)
text=text.replace('</body>', runtime+'\n</body>',1)
p.write_text(text,encoding='utf-8')
