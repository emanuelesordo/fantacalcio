from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v14-list-strategy-player-runtime' in s:
    raise SystemExit('V14 already applied')

# Keep strategy route in place; access UI can show/hide content but must not bounce home.
s=s.replace("  const v10StrategicAllowed=()=>state.v10StrategicAccess?.allowed===true;",
            "  const v10StrategicAllowed=()=>state.v10StrategicAccess?.allowed===true||v10IsIndexOwner();",1)
s=s.replace("    if(state.view==='strategy'&&!allowed&&state.v10StrategicAccess){\n      if(location.hash!=='#/setup') location.hash='#/home';\n    }",
            "    if(state.view==='strategy'&&!allowed&&state.v10StrategicAccess){\n      const view=document.getElementById('view-strategy');\n      if(view&&!view.querySelector('.v14-strategy-denied')){view.insertAdjacentHTML('beforeend','<div class=\"v14-strategy-denied panel\">Centro Strategico non abilitato per questo account.</div>');}\n    }",1)

runtime=r'''
<script id="v14-list-strategy-player-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V14__)return;
  window.__FANTA_V14__=1;

  const roleOrder=['Por','B','Dd','Dc','Ds','E','M','C','T','W','A','Pc'];
  const roleRank=r=>{const i=roleOrder.findIndex(x=>x.toLowerCase()===String(r||'').toLowerCase());return i<0?999:i};
  const activeRoleMatch=p=>{
    if(!state.listRoles||state.listRoles.has('all'))return true;
    const roles=typeof playerRoles==='function'?playerRoles(p,typeof fantasyMode==='function'?fantasyMode():'classic'):[];
    return roles.some(r=>state.listRoles.has(r)||state.listRoles.has(String(r).toLowerCase()));
  };

  /* Role sort follows Fantacalcio/Mantra football order, not alphabetic order. */
  const oldV13SortValue=typeof v13SortValue==='function'?v13SortValue:null;
  if(oldV13SortValue){
    v13SortValue=function(p,key){
      if(key==='role'){
        const roles=typeof playerRoles==='function'?playerRoles(p,typeof fantasyMode==='function'?fantasyMode():'classic'):[];
        return roles.length?Math.min(...roles.map(roleRank)):999;
      }
      return oldV13SortValue(p,key);
    };
  }

  /* Header: role is filtered by the rolebar above. Slot becomes numeric/range input. */
  const oldV13Header=typeof v13Header==='function'?v13Header:null;
  if(oldV13Header){
    v13Header=function(players){
      const teams=[...new Set(players.map(p=>p.serie_a_team).filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b),'it'));
      return `<tr class="v13-sort-row">
        <th>${sortHead('role','Ruoli')}</th><th>${sortHead('name','Nome')}</th><th>${sortHead('team','Squadra')}</th><th>${sortHead('badge','Badge')}</th><th>${sortHead('slot','Slot')}</th><th>${sortHead('presence','%Tit')}</th><th>${sortHead('pfc','PFC')}</th><th>${sortHead('pma','PMA')}</th><th>${sortHead('delta','Delta')}</th><th>${sortHead('index','Indice cr')}</th><th>${sortHead('threshold','Soglia')}</th><th>${sortHead('expected','Prezzo atteso')}</th><th>${sortHead('fmv','FMV')}</th><th>${sortHead('favorite','Preferito')}</th>
      </tr><tr class="v13-filter-row">
        <th><span class="v14-role-filter-note">↑ ruoli</span></th>
        <th>${filterInput('name','nome')}</th>
        <th>${filterSelect('team',teams.map(x=>[x,x]))}</th>
        <th>${filterSelect('badge',[['market','mercato'],['injury','indisp.'],['new','nuovo'],['penalties','rigori'],['free_kicks','piazzati']])}</th>
        <th>${filterInput('slot','1-3')}</th>
        <th>${filterInput('presence','60-90')}</th><th>${filterInput('pfc','10-30')}</th><th>${filterInput('pma','10-30')}</th><th>${filterInput('delta','-5:10')}</th><th>${filterInput('index','20-50')}</th><th>${filterInput('threshold','20-50')}</th><th>${filterInput('expected','20-50')}</th><th>${filterInput('fmv','6.2-7.1')}</th>
        <th>${filterSelect('favorite',[['yes','sì'],['no','no']])}</th>
      </tr>`;
    };
  }

  /* Slot now supports ranges/comparators too. */
  const oldV13FilterMatch=typeof v13FilterMatch==='function'?v13FilterMatch:null;
  if(oldV13FilterMatch){
    v13FilterMatch=function(p){
      const f=state.v13Filters||{},savedSlot=f.slot;
      f.slot='';
      const base=oldV13FilterMatch(p);
      f.slot=savedSlot;
      if(!base)return false;
      if(savedSlot&&!v13NumericMatch(Number(p?.slot),savedSlot))return false;
      return true;
    };
  }

  function v14FilteredSortedRows(){
    const all=state.list?.players||[];
    let rows=all.filter(activeRoleMatch).filter(v13FilterMatch);
    return v13SortPlayers(rows);
  }
  function v14RenderBody(){
    const body=document.getElementById('list-body');if(!body)return;
    const rows=v14FilteredSortedRows();
    body.innerHTML=rows.map(v13Row).join('')||'<tr><td colspan="14" class="soft" style="text-align:center;height:60px">Nessun giocatore.</td></tr>';
  }
  function v14RenderHeader(){
    const thead=document.querySelector('#view-list .player-table thead');
    if(thead)thead.innerHTML=v13Header(state.list?.players||[]);
  }

  /* Replace V13 full rerender so typing keeps focus/caret. */
  renderListTable=function(){v14RenderHeader();v14RenderBody();};

  const listView=document.querySelector('#view-list');
  listView?.addEventListener('input',e=>{
    const el=e.target.closest?.('[data-v13-filter]');if(!el||el.tagName==='SELECT')return;
    state.v13Filters[el.dataset.v13Filter]=el.value;
    v14RenderBody();
  },true);
  listView?.addEventListener('change',e=>{
    const el=e.target.closest?.('[data-v13-filter]');if(!el)return;
    state.v13Filters[el.dataset.v13Filter]=el.value;
    v14RenderBody();
  },true);

  /* Prevent older delegated V13 input handler from rebuilding the header. */
  listView?.addEventListener('input',e=>{
    if(e.target.closest?.('[data-v13-filter]'))e.stopImmediatePropagation();
  },true);

  /* Toolbar: only role buttons + import. Hide redundant global filters. */
  function v14Toolbar(){
    const row=document.querySelector('#view-list .v12-toolbar-row');if(!row)return;
    const filters=row.querySelector('.filters');if(filters){
      const ids=['list-search','list-team','list-slot','list-flag'];
      ids.forEach(id=>{const el=document.getElementById(id);if(!el)return;if(id==='list-search')el.value='';else el.value='all';});
      filters.hidden=true;
    }
    const rolebar=document.getElementById('list-rolebar');
    const importBtn=document.getElementById('v13-import-button');
    const importInput=document.getElementById('v13-import-file');
    if(rolebar&&importBtn){
      let tools=row.querySelector('.v14-role-tools');
      if(!tools){tools=document.createElement('div');tools.className='v14-role-tools';row.appendChild(tools);}
      if(importInput)tools.appendChild(importInput);
      tools.appendChild(importBtn);
    }
  }

  if(typeof loadList==='function'){
    const oldLoadList14=loadList;
    loadList=async function(...args){const r=await oldLoadList14(...args);queueMicrotask(()=>{v14Toolbar();v14RenderHeader();v14RenderBody();});return r;};
  }

  /* Strategy route: owner must always load his strategy view; no automatic home bounce. */
  const isOwner=()=>String(state.dashboard?.currentUser?.username||state.session?.user?.username||'').trim().toLowerCase()==='emanuelesordo';
  window.addEventListener('hashchange',()=>{
    if(location.hash==='#/strategy'&&isOwner())queueMicrotask(()=>window.loadStrategyView?.(true));
  });

  function fmt(v,d=2){const n=Number(v);return Number.isFinite(n)?n.toFixed(d):'—'}
  function playerDetailsHtml(p){
    const sf=p?.strategic_features||{},roles=typeof playerRoles==='function'?playerRoles(p,typeof fantasyMode==='function'?fantasyMode():'classic'):[];
    const delta=Number.isFinite(Number(p?.pfc_pma_delta))?Number(p.pfc_pma_delta):Number(p?.pfc||0)-Number(p?.pma||0);
    const games=typeof v13ExpectedGames==='function'?v13ExpectedGames(p):null;
    const idx=typeof strategicValueIndex==='function'?strategicValueIndex(p):null;
    const thr=typeof strategicThresholdPrice==='function'?strategicThresholdPrice(p):null;
    const exp=typeof strategicExpectedPrice==='function'?strategicExpectedPrice(p):null;
    const fmv=typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):p?.expected_fantasy_avg;
    const pres=typeof strategicPresencePercent==='function'?strategicPresencePercent(p):p?.expected_titolarity;
    const signals=typeof auctionPlayerSignalBadges==='function'?auctionPlayerSignalBadges(p):'—';
    return `<section class="v14-called-details">
      <div class="v14-called-title"><strong>DATI GIOCATORE</strong><span>${signals}</span></div>
      <div class="v14-called-grid">
        <span><small>Ruoli</small><b>${roles.map(r=>`<i class="rolebadge" data-role="${esc(r)}">${esc(r)}</i>`).join(' ')||'—'}</b></span>
        <span><small>Squadra</small><b>${esc(p?.serie_a_team||'—')}</b></span>
        <span><small>Slot</small><b>${esc(p?.slot??'—')}</b></span>
        <span><small>% Tit.</small><b>${Number.isFinite(Number(pres))?Math.round(Number(pres))+'%':'—'}</b></span>
        <span><small>PFC</small><b>${fmt(p?.pfc,0)}</b></span>
        <span><small>PMA</small><b>${fmt(p?.pma,0)}</b></span>
        <span><small>Δ PFC-PMA</small><b>${delta>=0?'+':''}${fmt(delta,0)}</b></span>
        <span><small>FMV</small><b>${fmt(fmv,2)}</b></span>
        <span><small>Indice</small><b>${idx??'—'} cr</b></span>
        <span><small>Soglia</small><b>${thr??'—'} cr</b></span>
        <span><small>Prezzo atteso</small><b>${exp?Math.round(exp):'—'} cr</b></span>
        <span><small>Gare attese</small><b>${games==null?'—':fmt(games,1)}</b></span>
        <span><small>Trend</small><b>${esc(sf.trend_direction||'—')} ${Number.isFinite(Number(sf.trend_raw))?`(${Number(sf.trend_raw)>0?'+':''}${fmt(sf.trend_raw,2)})`:''}</b></span>
        <span><small>Volatilità</small><b>${Number.isFinite(Number(sf.volatility))?Math.round(Number(sf.volatility)*100)+'%':'—'}</b></span>
        <span><small>FV ultimo anno</small><b>${fmt(p?.last_year_fantasy_avg,2)}</b></span>
        <span><small>FV ultimi 5</small><b>${fmt(p?.last_five_year_fantasy_avg,2)}</b></span>
      </div>
    </section>`;
  }
  function v14CalledCard(){
    document.querySelectorAll('.v14-called-details').forEach(x=>x.remove());
    if(!isOwner()||state.view!=='auction')return;
    const p=state.auction?.currentPlayer;if(!p)return;
    const command=document.querySelector('.auction-middle-column .auction-command-bar')||document.querySelector('.auction-command-bar');
    if(command)command.insertAdjacentHTML('afterend',playerDetailsHtml(p));
  }
  if(typeof renderAuctionLive==='function'){
    const oldRender14=renderAuctionLive;
    renderAuctionLive=function(...args){const r=oldRender14(...args);queueMicrotask(v14CalledCard);return r;};
  }

  const style=document.createElement('style');style.id='v14-list-strategy-player-style';style.textContent=`
    #view-list .v12-toolbar-row{display:flex!important;align-items:center!important;gap:8px!important;min-height:34px!important}
    #view-list .v12-toolbar-row #list-rolebar{flex:1 1 auto!important;min-width:0!important}
    #view-list .v12-toolbar-row .filters[hidden]{display:none!important}
    #view-list .v14-role-tools{display:flex;align-items:center;gap:4px;flex:0 0 auto}
    #view-list .v13-filter-row th:first-child{min-width:96px!important;width:96px!important}
    #view-list .v13-sort-row th:first-child,#view-list tbody td:first-child{min-width:96px!important;width:96px!important}
    #view-list tbody td:first-child{overflow:visible!important;white-space:nowrap!important}
    #view-list tbody td:first-child .rolebadge{margin-right:2px!important}
    #view-list .v14-role-filter-note{font-size:6px;color:var(--soft);opacity:.7}
    #view-list .v13-filter-row input{min-width:44px!important}
    #view-list .v13-filter-row th:nth-child(2) input{min-width:88px!important}
    #view-list .v13-filter-row th:nth-child(3) select{min-width:72px!important}
    .v14-strategy-denied{margin:12px;padding:16px}
    body.v10-index-owner .v14-called-details{display:grid}
    .v14-called-details{display:none;min-height:0;padding:5px 6px;border:1px solid rgba(91,151,216,.32);border-radius:8px;background:linear-gradient(145deg,rgba(18,50,80,.78),rgba(7,27,48,.88));gap:4px;overflow:hidden}
    .v14-called-title{display:flex;align-items:center;justify-content:space-between;gap:6px;color:#a9c7e7;font-size:6px;letter-spacing:.08em}
    .v14-called-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px}
    .v14-called-grid>span{min-width:0;padding:3px 4px;border:1px solid rgba(91,151,216,.14);border-radius:5px;background:rgba(8,31,54,.48)}
    .v14-called-grid small,.v14-called-grid b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .v14-called-grid small{font-size:5px;color:var(--soft)}
    .v14-called-grid b{font-size:7px;margin-top:1px;font-weight:900}
    .v14-called-grid .rolebadge{display:inline-flex!important;font-style:normal}
    .auction-middle-column:has(.v14-called-details){grid-template-rows:auto auto minmax(0,1fr)!important}
    @media(max-width:900px){.v14-called-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;document.head.appendChild(style);

  queueMicrotask(()=>{v14Toolbar();if(state.view==='list'){v14RenderHeader();v14RenderBody();}if(state.view==='auction')v14CalledCard();});
})();
</script>
'''

s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('V14 patch written')
