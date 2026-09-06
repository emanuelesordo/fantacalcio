from pathlib import Path
import re
p=Path('home.html')
s=p.read_text(encoding='utf-8')
# Remove broken separate V14 runtime; its strategy-access string patches remain elsewhere.
s=re.sub(r'\n<script id="v14-list-strategy-player-runtime">.*?</script>\n','\n',s,count=1,flags=re.S)

# V13: add canonical role order before sort-value function.
marker="  function v13SortValue(p,key){\n"
insert="""  const v13RoleOrder=['Por','B','Dd','Dc','Ds','E','M','C','T','W','A','Pc'];
  const v13RoleRank=r=>{const i=v13RoleOrder.findIndex(x=>x.toLowerCase()===String(r||'').toLowerCase());return i<0?999:i};
  function v13PlayerRoleRank(p){const rs=v13Roles(p);return rs.length?Math.min(...rs.map(v13RoleRank)):999}

  function v13SortValue(p,key){
"""
if marker not in s: raise SystemExit('sort marker missing')
s=s.replace(marker,insert,1)
s=s.replace("      role:v13Roles(p).join('/'),name:p?.name||'',team:p?.serie_a_team||'',badge:v13SignalKeys(p).join(','),slot:Number(p?.slot??999),presence:v13Presence(p),pfc:Number(p?.pfc??-1),pma:Number(p?.pma??-1),delta:v13Delta(p)??-999,index:strategicValueIndex(p),threshold:v13Threshold(p),expected:v13Expected(p),fmv:v13Fmv(p),favorite:v13Favorite(p)?1:0",
            "      role:v13PlayerRoleRank(p),name:p?.name||'',team:p?.serie_a_team||'',badge:v13SignalKeys(p).join(','),slot:Number(p?.slot??999),presence:v13Presence(p),pfc:Number(p?.pfc??-1),pma:Number(p?.pma??-1),delta:v13Delta(p)??-999,index:strategicValueIndex(p),threshold:v13Threshold(p),expected:v13Expected(p),fmv:v13Fmv(p),favorite:v13Favorite(p)?1:0",1)
# Role filtered only by rolebar; slot numeric/range.
s=s.replace("    if(f.role&&f.role!=='all'&&!roles.split('/').includes(String(f.role).toLowerCase()))return false;\n",'',1)
s=s.replace("    if(f.slot&&f.slot!=='all'&&String(p?.slot??'')!==String(f.slot))return false;",
            "    if(f.slot&&!v13NumericMatch(Number(p?.slot),f.slot))return false;",1)
# Header: no role filter duplicate and slot uses range input.
s=s.replace("      <th>${filterSelect('role',roles.map(x=>[String(x).toLowerCase(),x]))}</th>","      <th><span class=\"v14-role-filter-note\">↑ ruoli</span></th>",1)
s=s.replace("      <th>${filterSelect('slot',slots.map(x=>[String(x),String(x)]))}</th>","      <th>${filterInput('slot','1-3')}</th>",1)
# Render body helper; avoid header replacement during typing.
old="""  renderListTable=function(){
    if(!state.list)return;
    const all=state.list.players||[],controls={search:$('list-search'),team:$('list-team'),slot:$('list-slot'),flag:$('list-flag')};
    let rows=typeof filterPlayers==='function'?filterPlayers(all,controls,state.listRoles,v13Mode()):all;
    rows=rows.filter(v13FilterMatch);rows=v13SortPlayers(rows);
    const thead=document.querySelector('#view-list .player-table thead');if(thead)thead.innerHTML=v13Header(all);
    const body=document.getElementById('list-body');if(body)body.innerHTML=rows.map(v13Row).join('')||'<tr><td colspan="14" class="soft" style="text-align:center;height:60px">Nessun giocatore.</td></tr>';
  };

  document.querySelector('#view-list')?.addEventListener('input',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;renderListTable();});
  document.querySelector('#view-list')?.addEventListener('change',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;renderListTable();});
"""
new="""  function v13Rows(){
    if(!state.list)return [];
    const all=state.list.players||[];
    const roleFiltered=(!state.listRoles||state.listRoles.has('all'))?all:all.filter(p=>v13Roles(p).some(r=>state.listRoles.has(r)||state.listRoles.has(String(r).toLowerCase())));
    return v13SortPlayers(roleFiltered.filter(v13FilterMatch));
  }
  function v13RenderBody(){
    const body=document.getElementById('list-body');if(!body)return;
    const rows=v13Rows();body.innerHTML=rows.map(v13Row).join('')||'<tr><td colspan="14" class="soft" style="text-align:center;height:60px">Nessun giocatore.</td></tr>';
  }
  renderListTable=function(){
    if(!state.list)return;
    const thead=document.querySelector('#view-list .player-table thead');if(thead)thead.innerHTML=v13Header(state.list.players||[]);
    v13RenderBody();
  };

  document.querySelector('#view-list')?.addEventListener('input',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;v13RenderBody();});
  document.querySelector('#view-list')?.addEventListener('change',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;v13RenderBody();});
"""
if old not in s: raise SystemExit('render block missing')
s=s.replace(old,new,1)
# Import into rolebar row; hide redundant toolbar filters.
s=s.replace("    const row=document.querySelector('#view-list .v12-toolbar-row')||document.querySelector('#view-list .v12-toolbar');if(!row||row.querySelector('#v13-import-button'))return;",
            "    const row=document.querySelector('#view-list #list-rolebar')||document.querySelector('#view-list .v12-toolbar-row');if(!row||row.querySelector('#v13-import-button'))return;",1)
# Add compact toolbar call in loadList and initialization.
s=s.replace("loadList=async function(...args){const r=await oldLoadListV13(...args);await v13LoadMeta();v13MountImport();renderListTable();return r;};",
            "loadList=async function(...args){const r=await oldLoadListV13(...args);await v13LoadMeta();v13MountImport();const f=document.querySelector('#view-list .v12-toolbar-row .filters');if(f)f.hidden=true;renderListTable();return r;};",1)
s=s.replace("void v13LoadMeta(true).then(()=>{if(state.view==='list'){v13MountImport();renderListTable();}});",
            "void v13LoadMeta(true).then(()=>{if(state.view==='list'){v13MountImport();const f=document.querySelector('#view-list .v12-toolbar-row .filters');if(f)f.hidden=true;renderListTable();}});",1)
# Style refinements.
s=s.replace("    #view-list .player-table th,#view-list .player-table td{width:auto!important;min-width:0!important;max-width:none!important;white-space:nowrap!important}",
            "    #view-list .player-table th,#view-list .player-table td{width:auto!important;min-width:max-content!important;max-width:none!important;white-space:nowrap!important}\n    #view-list .player-table th:first-child,#view-list .player-table td:first-child{min-width:96px!important;width:96px!important}\n    #view-list .v12-toolbar-row .filters[hidden]{display:none!important}\n    #view-list #list-rolebar{display:flex!important;align-items:center!important;gap:3px!important;flex-wrap:nowrap!important}\n    #view-list #v13-import-button{margin-left:auto!important}\n    #view-list .v14-role-filter-note{font-size:6px;color:var(--soft);opacity:.7}",1)

# Owner-only called-player detail runtime using only globals.
card=r'''
<script id="v14-called-player-detail-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V14_CALLED__)return;window.__FANTA_V14_CALLED__=1;
  const owner=()=>String(state.dashboard?.currentUser?.username||state.session?.user?.username||'').trim().toLowerCase()==='emanuelesordo';
  const fmt=(v,d=2)=>{const n=Number(v);return Number.isFinite(n)?n.toFixed(d):'—'};
  function expectedGames(p){const next=Math.max(1,Math.min(38,Number(state.v13NextRound||1))),remaining=Math.max(0,39-next),until=Math.max(0,Number(p?.unavailable_until_round||0)),miss=until>=next?Math.min(remaining,until-next+1):0,available=Math.max(0,remaining-miss),pres=typeof strategicPresencePercent==='function'?Number(strategicPresencePercent(p)||0):Number(p?.expected_titolarity||0);return available*Math.max(0,Math.min(100,pres))/100;}
  function html(p){const sf=p?.strategic_features||{},roles=typeof playerRoles==='function'?playerRoles(p,typeof fantasyMode==='function'?fantasyMode():'classic'):[],delta=Number.isFinite(Number(p?.pfc_pma_delta))?Number(p.pfc_pma_delta):Number(p?.pfc||0)-Number(p?.pma||0),idx=typeof strategicValueIndex==='function'?strategicValueIndex(p):null,thr=typeof strategicThresholdPrice==='function'?strategicThresholdPrice(p):null,exp=typeof strategicExpectedPrice==='function'?strategicExpectedPrice(p):null,fmv=typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):p?.expected_fantasy_avg,pres=typeof strategicPresencePercent==='function'?strategicPresencePercent(p):p?.expected_titolarity,signals=typeof auctionPlayerSignalBadges==='function'?auctionPlayerSignalBadges(p):'—';return `<section class="v14-called-details"><div class="v14-called-title"><strong>DATI GIOCATORE</strong><span>${signals}</span></div><div class="v14-called-grid"><span><small>Ruoli</small><b>${roles.map(r=>`<i class="rolebadge" data-role="${esc(r)}">${esc(r)}</i>`).join(' ')||'—'}</b></span><span><small>Squadra</small><b>${esc(p?.serie_a_team||'—')}</b></span><span><small>Slot</small><b>${esc(p?.slot??'—')}</b></span><span><small>% Tit.</small><b>${Number.isFinite(Number(pres))?Math.round(Number(pres))+'%':'—'}</b></span><span><small>PFC</small><b>${fmt(p?.pfc,0)}</b></span><span><small>PMA</small><b>${fmt(p?.pma,0)}</b></span><span><small>Δ PFC-PMA</small><b>${delta>=0?'+':''}${fmt(delta,0)}</b></span><span><small>FMV</small><b>${fmt(fmv,2)}</b></span><span><small>Indice</small><b>${idx??'—'} cr</b></span><span><small>Soglia</small><b>${thr??'—'} cr</b></span><span><small>Prezzo atteso</small><b>${exp?Math.round(exp):'—'} cr</b></span><span><small>Gare attese</small><b>${fmt(expectedGames(p),1)}</b></span><span><small>Trend</small><b>${esc(sf.trend_direction||'—')}</b></span><span><small>Volatilità</small><b>${Number.isFinite(Number(sf.volatility))?Math.round(Number(sf.volatility)*100)+'%':'—'}</b></span><span><small>FV ultimo anno</small><b>${fmt(p?.last_year_fantasy_avg,2)}</b></span><span><small>FV ultimi 5</small><b>${fmt(p?.last_five_year_fantasy_avg,2)}</b></span></div></section>`;}
  function mount(){document.querySelectorAll('.v14-called-details').forEach(x=>x.remove());if(!owner()||state.view!=='auction')return;const p=state.auction?.currentPlayer;if(!p)return;const command=document.querySelector('.auction-middle-column .auction-command-bar')||document.querySelector('.auction-command-bar');if(command)command.insertAdjacentHTML('afterend',html(p));}
  if(typeof renderAuctionLive==='function'){const old=renderAuctionLive;renderAuctionLive=function(...a){const r=old(...a);queueMicrotask(mount);return r;};}
  const st=document.createElement('style');st.textContent=`.v14-called-details{padding:5px 6px;border:1px solid rgba(91,151,216,.32);border-radius:8px;background:linear-gradient(145deg,rgba(18,50,80,.78),rgba(7,27,48,.88));display:grid;gap:4px;overflow:hidden}.v14-called-title{display:flex;justify-content:space-between;gap:6px;font-size:6px;color:#a9c7e7;letter-spacing:.08em}.v14-called-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px}.v14-called-grid>span{padding:3px 4px;border:1px solid rgba(91,151,216,.14);border-radius:5px;background:rgba(8,31,54,.48);min-width:0}.v14-called-grid small,.v14-called-grid b{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v14-called-grid small{font-size:5px;color:var(--soft)}.v14-called-grid b{font-size:7px;margin-top:1px;font-weight:900}.v14-called-grid .rolebadge{display:inline-flex!important;font-style:normal}@media(max-width:900px){.v14-called-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}`;document.head.appendChild(st);queueMicrotask(mount);
})();
</script>
'''
s=s.replace('</body>',card+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('scope fixed')
