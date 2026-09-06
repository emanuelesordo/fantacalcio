from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'marker not found: {label}')
    s=s.replace(old,new,1)

rep('    home.html#/rosters\n    home.html#/auction\n','    home.html#/rosters\n    home.html#/strategy\n    home.html#/auction\n','route docs')
rep('      <a class="nav-btn" data-view="rosters" href="#/rosters"><span class="nav-glyph">◫</span><span>Rose</span></a>\n      <a class="nav-btn" data-view="auction" href="#/auction"><span class="nav-glyph">◆</span><span>Asta</span></a>','      <a class="nav-btn" data-view="rosters" href="#/rosters"><span class="nav-glyph">◫</span><span>Rose</span></a>\n      <a class="nav-btn" data-view="strategy" href="#/strategy"><span class="nav-glyph">◇</span><span>Strategia</span></a>\n      <a class="nav-btn" data-view="auction" href="#/auction"><span class="nav-glyph">◆</span><span>Asta</span></a>','main nav')
rep('      <!-- ASTA -->\n      <section id="view-auction" class="view no-page-scroll">','''      <!-- STRATEGIA -->
      <section id="view-strategy" class="view no-page-scroll">
        <div class="v9-strategy-page">
          <nav class="v9-drawer-tabs v9-strategy-tabs" aria-label="Strategia e statistiche">
            <button type="button" class="v9-drawer-tab active" data-v9-tab="strategy">CENTRO STRATEGICO</button>
            <button type="button" class="v9-drawer-tab" data-v9-tab="stats">STATISTICHE</button>
          </nav>
          <div class="v9-strategy-content">
            <div class="v9-pane v9-pane-strategy" data-v9-pane="strategy"></div>
            <div class="v9-pane v9-pane-stats" data-v9-pane="stats" hidden></div>
          </div>
        </div>
      </section>

      <!-- ASTA -->
      <section id="view-auction" class="view no-page-scroll">''','strategy view')
rep("      rosters: { id: 'rosters', hash: '#/rosters', leagueRequired: true },\n      auction: { id: 'auction', hash: '#/auction', leagueRequired: true },","      rosters: { id: 'rosters', hash: '#/rosters', leagueRequired: true },\n      strategy: { id: 'strategy', hash: '#/strategy', leagueRequired: true },\n      auction: { id: 'auction', hash: '#/auction', leagueRequired: true },",'route object')
rep("      rosters: { title: 'Rose', subtitle: 'Crediti, assegnazioni e capacità residua di tutte le squadre.' },\n      auction: { title: 'Asta live', subtitle: 'Cockpit operativo collegato allo stato autorevole del server.' },","      rosters: { title: 'Rose', subtitle: 'Crediti, assegnazioni e capacità residua di tutte le squadre.' },\n      strategy: { title: 'Strategia', subtitle: 'Centro Strategico privato, preferiti, benchmark e statistiche pre-asta.' },\n      auction: { title: 'Asta live', subtitle: 'Cockpit operativo collegato allo stato autorevole del server.' },",'route meta')
rep("        else if(state.view==='rosters')await loadRosters();\n        else if(state.view==='auction'||state.view==='tv')await loadAuction({quiet:!force});","        else if(state.view==='rosters')await loadRosters();\n        else if(state.view==='strategy'&&typeof window.loadStrategyView==='function')await window.loadStrategyView(force);\n        else if(state.view==='auction'||state.view==='tv')await loadAuction({quiet:!force});",'view loader')
rep("                  item.route === 'rosters' ? '◫' :\n                  item.route === 'auction' ? '◆' : '▣'","                  item.route === 'rosters' ? '◫' :\n                  item.route === 'strategy' ? '◇' :\n                  item.route === 'auction' ? '◆' : '▣'",'palette glyph')

pattern=r"  function activateTab\(name\)\{.*?\n  \}\n  function patchDrawer\(\)\{.*?\n  \}\n\n  async function loadRulesIntoSetup"
replacement='''  function activateTab(name){
    const tab=name==='stats'?'stats':'strategy';
    state.v9ActiveDrawerTab=tab;
    const view=document.getElementById('view-strategy');
    if(!view)return;
    view.querySelectorAll('[data-v9-tab]').forEach(b=>b.classList.toggle('active',b.dataset.v9Tab===tab));
    view.querySelectorAll('[data-v9-pane]').forEach(p=>p.hidden=p.dataset.v9Pane!==tab);
    if(state.view!=='strategy')return;
    if(tab==='stats')renderStats();else renderStrategy();
  }

  function bindStrategyView(){
    const view=document.getElementById('view-strategy');
    if(!view||view.dataset.v9Bound==='1')return;
    view.dataset.v9Bound='1';
    view.querySelectorAll('[data-v9-tab]').forEach(b=>b.addEventListener('click',()=>activateTab(b.dataset.v9Tab)));
  }

  window.loadStrategyView=async function(force=false){
    bindStrategyView();
    await loadV9(force===true);
    activateTab(state.v9ActiveDrawerTab==='stats'?'stats':'strategy');
  };

  async function loadRulesIntoSetup'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'V9 drawer replacement count={n}')

pattern=r"  const oldLive=renderAuctionLive;renderAuctionLive=function\(\.\.\.a\)\{.*?\n  const oldLoadAuction=loadAuction;loadAuction=async function\(\.\.\.a\)\{.*?return r\};\n"
replacement='''  const oldLive=renderAuctionLive;renderAuctionLive=function(...a){const r=oldLive(...a);queueMicrotask(()=>document.querySelector('.v8center')?.remove());return r};
  const oldLobby=renderAuctionLobby;renderAuctionLobby=function(...a){const r=oldLobby(...a);queueMicrotask(()=>document.querySelector('.v8center')?.remove());return r};
  const oldPrepared=renderAuctionPrepared;renderAuctionPrepared=function(...a){const r=oldPrepared(...a);queueMicrotask(()=>document.querySelector('.v8center')?.remove());return r};
  const oldLoadAuction=loadAuction;loadAuction=async function(...a){const r=await oldLoadAuction(...a);document.querySelector('.v8center')?.remove();return r};
'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'auction wrapper replacement count={n}')

pattern=r"  const v9DrawerStyle=document\.createElement\('style'\);v9DrawerStyle\.textContent=`.*?`;document\.head\.appendChild\(v9DrawerStyle\);"
replacement='''  const v9PageStyle=document.createElement('style');v9PageStyle.textContent=`
    #view-strategy{overflow:hidden!important}
    .v9-strategy-page{height:100%;min-height:0;display:grid;grid-template-rows:44px minmax(0,1fr);gap:8px}
    .v9-strategy-tabs{display:grid;grid-template-columns:minmax(150px,240px) minmax(150px,240px);justify-content:start;gap:5px;padding:5px;border:1px solid rgba(109,167,255,.16);border-radius:14px;background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.022))}
    .v9-strategy-tabs .v9-drawer-tab{height:32px!important;min-height:32px!important;padding:4px 10px!important;border-radius:9px!important;font-size:8px!important}
    .v9-strategy-content{min-height:0;height:100%;overflow:hidden}
    #view-strategy .v9-pane{height:100%;min-height:0;overflow:auto;overscroll-behavior:contain;padding:0 2px 12px}
    #view-strategy .v9-pane[hidden]{display:none!important}
    #view-strategy .v9scroll{grid-template-columns:repeat(12,minmax(0,1fr));align-items:start;gap:8px}
    #view-strategy .v9card{grid-column:span 4;padding:14px;border-radius:14px}
    #view-strategy .v9card:first-child{grid-column:span 5}
    #view-strategy .v9card:nth-child(2){grid-column:span 3}
    #view-strategy .v9card:nth-child(3){grid-column:span 4}
    #view-strategy .v9-pane-stats .v9card{grid-column:span 6}
    #view-strategy .v9-pane-stats .v9card:last-child{grid-column:1/-1}
    #view-strategy .v9card-scroll{max-height:360px}
    #view-strategy .v9bestcols .v9card-scroll{max-height:420px}
    @media(max-width:1050px){#view-strategy .v9card,#view-strategy .v9card:first-child,#view-strategy .v9card:nth-child(2),#view-strategy .v9card:nth-child(3),#view-strategy .v9-pane-stats .v9card{grid-column:span 6}}
    @media(max-width:700px){.v9-strategy-page{grid-template-rows:42px minmax(0,1fr)}.v9-strategy-tabs{grid-template-columns:1fr 1fr;padding:4px}.v9-strategy-tabs .v9-drawer-tab{font-size:7px!important}#view-strategy .v9scroll{grid-template-columns:1fr}#view-strategy .v9card,#view-strategy .v9card:first-child,#view-strategy .v9card:nth-child(2),#view-strategy .v9card:nth-child(3),#view-strategy .v9-pane-stats .v9card,#view-strategy .v9-pane-stats .v9card:last-child{grid-column:1}}
  `;document.head.appendChild(v9PageStyle);'''
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'drawer CSS replacement count={n}')

rep("  void loadV9(true).then(()=>{if(state.view==='auction')patchDrawer();if(state.view==='setup')loadRulesIntoSetup()});","  bindStrategyView();\n  if(state.view==='strategy')void window.loadStrategyView(true);\n  if(state.view==='setup')void loadRulesIntoSetup();",'V9 init')

p.write_text(s,encoding='utf-8')
