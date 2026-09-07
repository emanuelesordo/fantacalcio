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
#view-auction .auction-free-table col.auction-col-name{width:var(--v25-name-width,150px)!important}
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
  width:var(--v25-name-width,150px)!important;
  min-width:var(--v25-name-width,150px)!important;
  max-width:190px!important;
  text-align:left!important;
}
#view-auction .auction-free-table td:nth-child(2) .player-main{
  min-width:0!important;width:100%!important;max-width:100%!important;
}
#view-auction .auction-free-table td:nth-child(2) .player-name,
#view-auction .auction-free-table td:nth-child(2) strong{
  display:block!important;max-width:100%!important;
  overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important;
}

/* Every column except player name is centered inside its own track. */
#view-auction .auction-free-table thead th:not(:nth-child(2)),
#view-auction .auction-free-table tbody td:not(:nth-child(2)){
  text-align:center!important;
}
#view-auction .auction-free-table thead th:not(:nth-child(2)) [data-auction-sort]{
  justify-content:center!important;text-align:center!important;
}
#view-auction .auction-free-table thead th:nth-child(2) [data-auction-sort]{
  justify-content:flex-start!important;text-align:left!important;
}
#view-auction .auction-free-table tbody td:not(:nth-child(2)) .rolebadge,
#view-auction .auction-free-table tbody td:not(:nth-child(2)) button,
#view-auction .auction-free-table tbody td:not(:nth-child(2)) .badge{
  margin-left:auto!important;margin-right:auto!important;
}
#view-auction .auction-free-filter-row th:not(:nth-child(2)) > select,
#view-auction .auction-free-filter-row th:not(:nth-child(2)) > input,
#view-auction .auction-free-filter-row th:not(:nth-child(2)) .auction-range-toggle{
  text-align:center!important;text-align-last:center!important;
}
#view-auction .auction-free-filter-row th:nth-child(2) input[type=search]{
  text-align:left!important;text-align-last:auto!important;
}
#view-auction .auction-range-toggle{
  justify-content:center!important;position:relative!important;padding-right:18px!important;
}
#view-auction .auction-range-toggle i{
  position:absolute!important;right:5px!important;top:50%!important;transform:translateY(-50%)!important;
}
#view-auction .auction-range.open .auction-range-toggle i{
  transform:translateY(-50%) rotate(180deg)!important;
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

/* Range popovers float above the scrollable table instead of being clipped by it. */
#view-auction .auction-range-popover.v25-floating-range{
  position:fixed!important;
  width:220px!important;
  min-width:220px!important;
  max-width:calc(100vw - 16px)!important;
  z-index:10000!important;
  transform:none!important;
  right:auto!important;
  bottom:auto!important;
  overflow:visible!important;
}
#view-auction .auction-range-popover.v25-floating-range .auction-dual-range{
  min-height:28px!important;
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
  const qsa=(s,r=document)=>[...r.querySelectorAll(s)];
  const isPhone=()=>window.matchMedia('(max-width:820px)').matches;
  const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));

  function enforceCallRow(){
    const host=qs('#view-auction .auction-caller-controls');
    const search=host?.querySelector('.auction-command-search');
    const base=host?.querySelector('.auction-command-base');
    const call=qs('#view-auction #auction-call-confirm');
    if(!host||!search||!base||!call)return;
    if(call.parentElement!==host) host.appendChild(call);
    call.classList.add('auction-top-call');
  }

  function sizeNameColumn(){
    const table=qs('#view-auction .auction-free-table');
    if(!table)return;
    const names=qsa('tbody td:nth-child(2) .player-name',table);
    let natural=0;
    names.forEach(node=>{natural=Math.max(natural,node.scrollWidth||0);});
    const width=clamp(Math.ceil(natural+34),128,190);
    table.style.setProperty('--v25-name-width',`${width}px`);
  }

  function moveMobileModeToLiveHeader(){
    if(!isPhone()||!document.body.classList.contains('auction-live'))return;
    const mode=qs('.v23-header-mode');
    const status=qs('#view-auction .auction-statusbar');
    if(mode&&status&&mode.parentElement!==status) status.appendChild(mode);
  }

  function rangePopover(key){
    return qs(`#view-auction [data-auction-range-popover="${key}"]`);
  }

  function rangeToggle(key){
    return qs(`#view-auction [data-auction-range-toggle="${key}"]`);
  }

  function positionRangePopover(toggle,pop){
    if(!toggle||!pop||pop.hidden)return;
    pop.classList.add('v25-floating-range');
    const rect=toggle.getBoundingClientRect();
    const width=Math.min(220,Math.max(160,window.innerWidth-16));
    const left=clamp(rect.left+rect.width/2-width/2,8,Math.max(8,window.innerWidth-width-8));
    const estimatedHeight=Math.max(88,pop.offsetHeight||88);
    let top=rect.bottom+5;
    if(top+estimatedHeight>window.innerHeight-8){
      top=Math.max(8,rect.top-estimatedHeight-5);
    }
    pop.style.setProperty('left',`${Math.round(left)}px`,'important');
    pop.style.setProperty('top',`${Math.round(top)}px`,'important');
    pop.style.setProperty('right','auto','important');
    pop.style.setProperty('bottom','auto','important');
    pop.style.setProperty('transform','none','important');
  }

  function closeFloatingRanges(){
    qsa('#view-auction .auction-range-popover.v25-floating-range').forEach(pop=>{
      pop.hidden=true;
      pop.classList.remove('v25-floating-range');
      pop.closest('[data-auction-range-box]')?.classList.remove('open');
    });
  }

  function repositionOpenRanges(){
    qsa('#view-auction .auction-range-popover.v25-floating-range').forEach(pop=>{
      if(pop.hidden)return;
      const key=pop.dataset.auctionRangePopover;
      positionRangePopover(rangeToggle(key),pop);
    });
  }

  function refresh(){
    enforceCallRow();
    sizeNameColumn();
    moveMobileModeToLiveHeader();
    repositionOpenRanges();
  }

  let refreshQueued=false;
  function scheduleRefresh(){
    if(refreshQueued)return;
    refreshQueued=true;
    requestAnimationFrame(()=>{refreshQueued=false;refresh();});
  }

  document.addEventListener('click',event=>{
    const toggle=event.target.closest('#view-auction [data-auction-range-toggle]');
    if(toggle){
      const key=toggle.dataset.auctionRangeToggle;
      const pop=rangePopover(key);
      const wasOpen=Boolean(pop&&!pop.hidden);
      setTimeout(()=>{
        const current=rangePopover(key);
        if(!current)return;
        if(wasOpen){
          if(!current.hidden) current.hidden=true;
          current.classList.remove('v25-floating-range');
          current.closest('[data-auction-range-box]')?.classList.remove('open');
          return;
        }
        if(current.hidden) current.hidden=false;
        current.closest('[data-auction-range-box]')?.classList.add('open');
        positionRangePopover(toggle,current);
      },0);
      return;
    }
    if(event.target.closest('#view-auction .auction-range-popover'))return;
    setTimeout(closeFloatingRanges,0);
  },true);

  const observer=new MutationObserver(scheduleRefresh);
  observer.observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('resize',scheduleRefresh,{passive:true});
  window.addEventListener('hashchange',scheduleRefresh);
  document.addEventListener('scroll',scheduleRefresh,true);
  document.addEventListener('DOMContentLoaded',scheduleRefresh,{once:true});
  setTimeout(scheduleRefresh,0);
})();
</script>
'''

if '</head>' not in text or '</body>' not in text:
    raise RuntimeError('home.html closing markers not found')
text=text.replace('</head>', style+'\n</head>',1)
text=text.replace('</body>', runtime+'\n</body>',1)
p.write_text(text,encoding='utf-8')
