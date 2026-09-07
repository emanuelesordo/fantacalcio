from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v15-range-listone-runtime' in s:
    raise SystemExit('V15 already applied')

runtime=r'''
<script id="v15-range-listone-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V15_RANGE_LISTONE__)return;
  window.__FANTA_V15_RANGE_LISTONE__=1;

  const V15_ROLE_ORDER=['Por','B','Dd','Dc','Ds','E','M','C','T','W','A','Pc'];
  const V15_NUMERIC={
    slot:{label:'Slot',step:1,get:p=>Number(p?.slot)},
    presence:{label:'%Tit',step:1,get:p=>v15Presence(p)},
    pfc:{label:'PFC',step:1,get:p=>Number(p?.pfc)},
    pma:{label:'PMA',step:1,get:p=>Number(p?.pma)},
    delta:{label:'Delta',step:1,get:p=>v15Delta(p)},
    index:{label:'Indice cr',step:1,get:p=>Number(typeof strategicValueIndex==='function'?strategicValueIndex(p):0)},
    threshold:{label:'Soglia',step:1,get:p=>Number(typeof strategicThresholdPrice==='function'?strategicThresholdPrice(p):0)},
    expected:{label:'Prezzo atteso',step:1,get:p=>Number(typeof strategicExpectedPrice==='function'?strategicExpectedPrice(p):0)},
    fmv:{label:'FMV',step:.01,get:p=>v15Fmv(p)}
  };

  state.v15TextFilters=state.v15TextFilters||{name:'',team:'',badge:'',favorite:''};
  state.v15Ranges=state.v15Ranges||{};
  state.v15RangeDatasetKey=state.v15RangeDatasetKey||'';

  const esc15=v=>typeof esc==='function'?esc(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const finite=v=>Number.isFinite(Number(v))?Number(v):null;
  const clamp15=(v,a,b)=>Math.max(a,Math.min(b,v));
  const fmt15=(v,step=1)=>{const n=Number(v);if(!Number.isFinite(n))return '—';return step<1?n.toFixed(step<=.01?2:1).replace('.',','):String(Math.round(n))};
  const mode15=()=>typeof fantasyMode==='function'?fantasyMode():'classic';
  const roles15=p=>typeof playerRoles==='function'?playerRoles(p,mode15()):[];
  const roleRank15=r=>{const i=V15_ROLE_ORDER.findIndex(x=>x.toLowerCase()===String(r||'').toLowerCase());return i<0?999:i};
  const playerRoleRank15=p=>{const r=roles15(p);return r.length?Math.min(...r.map(roleRank15)):999};
  const v15Presence=p=>{
    const n=typeof strategicPresencePercent==='function'?Number(strategicPresencePercent(p)):Number(p?.expected_titolarity);
    return Number.isFinite(n)?n:0;
  };
  const v15Fmv=p=>{
    const n=typeof strategicExpectedFantasyAverage==='function'?Number(strategicExpectedFantasyAverage(p)):Number(p?.expected_fantasy_avg);
    return Number.isFinite(n)?n:0;
  };
  const v15Delta=p=>{
    const d=finite(p?.pfc_pma_delta);if(d!==null)return d;
    const a=finite(p?.pfc),b=finite(p?.pma);return a!==null&&b!==null?a-b:null;
  };
  const v15Favorite=p=>{
    const source=String(p?.source_player_id||p?.id||'');
    const pref=state.v7Preferences?.get?.(source)||null;
    return Boolean(pref?.is_favorite||pref?.strategy==='top');
  };
  const prob15=v=>{
    if(typeof importedProbabilityPercent==='function')return Number(importedProbabilityPercent(v)||0);
    const n=Number(v);return Number.isFinite(n)?(n<=1?n*100:n):0;
  };
  function signals15(p){
    const out=[];const next=Math.max(1,Number(state.v13NextRound||1));const until=Math.max(0,Number(p?.unavailable_until_round||0));
    if(p?.market_flag===true)out.push({key:'market',emoji:'🔄',label:'Mercato'});
    if(p?.uncertain_return===true||until>=next)out.push({key:'injury',emoji:'🚑',label:p?.uncertain_return===true?'Rientro incerto':`Indisponibile fino G${until}`});
    if(p?.new_arrival===true)out.push({key:'new',emoji:'🆕',label:'Nuovo arrivo'});
    const pen=prob15(p?.penalty_probability);if(pen>0)out.push({key:'penalties',emoji:pen>=67?'🎯':'⚽',label:`Rigori ${Math.round(pen)}%`});
    const fk=prob15(p?.free_kick_probability);if(fk>0)out.push({key:'free_kicks',emoji:'🥅',label:`Piazzati ${Math.round(fk)}%`});
    return out;
  }
  const badges15=p=>{const a=signals15(p);return a.length?`<span class="auction-signal-list">${a.map(x=>`<span class="auction-signal-badge" title="${esc15(x.label)}" aria-label="${esc15(x.label)}">${x.emoji}</span>`).join('')}</span>`:'<span class="auction-signal-empty">—</span>'};

  function datasetKey15(players){
    return `${state.selectedLeague?.id||''}|${players.length}|${players.slice(0,8).map(p=>`${p.id}:${p.pfc}:${p.pma}:${p.expected_fantasy_avg}`).join(';')}|${state.v13NextRound||1}`;
  }
  function rangeBounds15(key,players){
    const def=V15_NUMERIC[key],vals=players.map(def.get).filter(Number.isFinite);
    if(!vals.length)return {min:0,max:def.step,step:def.step};
    let min=Math.min(...vals),max=Math.max(...vals),step=def.step;
    if(step>=1){min=Math.floor(min);max=Math.ceil(max);}else{min=Math.floor(min/step)*step;max=Math.ceil(max/step)*step;}
    if(min===max)max=min+step;
    return {min,max,step};
  }
  function ensureRanges15(players){
    const key=datasetKey15(players);
    if(state.v15RangeDatasetKey===key&&Object.keys(state.v15Ranges||{}).length)return;
    const old=state.v15Ranges||{},next={};
    Object.keys(V15_NUMERIC).forEach(k=>{
      const b=rangeBounds15(k,players),prev=old[k];
      next[k]={...b,lo:prev?clamp15(Number(prev.lo),b.min,b.max):b.min,hi:prev?clamp15(Number(prev.hi),b.min,b.max):b.max};
      if(next[k].lo>next[k].hi){next[k].lo=b.min;next[k].hi=b.max;}
    });
    state.v15Ranges=next;state.v15RangeDatasetKey=key;
  }
  function rangeIsFull15(key){const r=state.v15Ranges?.[key];return !r||Math.abs(r.lo-r.min)<1e-9&&Math.abs(r.hi-r.max)<1e-9}
  function rangeLabel15(key){const r=state.v15Ranges?.[key],d=V15_NUMERIC[key];if(!r)return 'tutto';return rangeIsFull15(key)?'tutto':`${fmt15(r.lo,d.step)}–${fmt15(r.hi,d.step)}`}
  function rangeMatch15(p,key){const r=state.v15Ranges?.[key],d=V15_NUMERIC[key];if(!r)return true;const v=d.get(p);return Number.isFinite(v)&&v>=r.lo-1e-9&&v<=r.hi+1e-9}

  function activeRole15(p){
    if(!state.listRoles||state.listRoles.has('all'))return true;
    const wanted=[...state.listRoles].map(x=>String(x).toLowerCase());
    return roles15(p).some(r=>wanted.includes(String(r).toLowerCase()));
  }
  function textMatch15(p){
    const f=state.v15TextFilters||{};
    if(f.name&&!String(p?.name||'').toLowerCase().includes(String(f.name).trim().toLowerCase()))return false;
    if(f.team&&String(p?.serie_a_team||'')!==f.team)return false;
    if(f.badge&&!signals15(p).some(x=>x.key===f.badge))return false;
    if(f.favorite==='yes'&&!v15Favorite(p))return false;
    if(f.favorite==='no'&&v15Favorite(p))return false;
    return true;
  }
  function filter15(p){return activeRole15(p)&&textMatch15(p)&&Object.keys(V15_NUMERIC).every(k=>rangeMatch15(p,k))}

  function sortValue15(p,key){
    if(key==='role')return playerRoleRank15(p);
    if(key==='name')return p?.name||'';
    if(key==='team')return p?.serie_a_team||'';
    if(key==='badge')return signals15(p).map(x=>x.key).join(',');
    if(key==='favorite')return v15Favorite(p)?1:0;
    return V15_NUMERIC[key]?V15_NUMERIC[key].get(p):'';
  }
  function rows15(){
    const all=state.list?.players||[];ensureRanges15(all);
    const dir=state.listSort?.direction==='desc'?-1:1,key=state.listSort?.key||'name';
    return all.filter(filter15).sort((a,b)=>{
      const av=sortValue15(a,key),bv=sortValue15(b,key);let c;
      if(typeof av==='number'&&typeof bv==='number')c=av-bv;else c=String(av).localeCompare(String(bv),'it',{sensitivity:'base'});
      if(c===0)c=String(a?.name||'').localeCompare(String(b?.name||''),'it',{sensitivity:'base'});
      return c*dir;
    });
  }

  const sortButton15=(key,label)=>`<button type="button" class="v15-sort" data-v15-sort="${key}">${label}<span>${state.listSort?.key===key?(state.listSort.direction==='desc'?'↓':'↑'):'↕'}</span></button>`;
  const textSearch15=(key,ph)=>`<input type="search" class="v15-text-filter" data-v15-text="${key}" value="${esc15(state.v15TextFilters?.[key]||'')}" placeholder="${ph}" autocomplete="off">`;
  const select15=(key,options)=>`<select class="v15-text-filter v15-select" data-v15-text="${key}"><option value="">tutti</option>${options.map(([v,l])=>`<option value="${esc15(v)}" ${String(state.v15TextFilters?.[key]||'')===String(v)?'selected':''}>${esc15(l)}</option>`).join('')}</select>`;
  function rangeControl15(key){
    const r=state.v15Ranges[key],d=V15_NUMERIC[key];if(!r)return '';
    return `<div class="v15-range" data-v15-range-box="${key}">
      <button type="button" class="v15-range-toggle" data-v15-range-toggle="${key}" title="Seleziona intervallo ${esc15(d.label)}"><span data-v15-range-label="${key}">${rangeLabel15(key)}</span><i>⌄</i></button>
      <div class="v15-range-popover" data-v15-range-popover="${key}" hidden>
        <div class="v15-range-values"><b data-v15-lo-label="${key}">${fmt15(r.lo,d.step)}</b><span>${esc15(d.label)}</span><b data-v15-hi-label="${key}">${fmt15(r.hi,d.step)}</b></div>
        <div class="v15-dual-range">
          <div class="v15-range-base"></div>
          <div class="v15-range-fill" data-v15-range-fill="${key}"></div>
          <input type="range" data-v15-range="${key}" data-bound="lo" min="${r.min}" max="${r.max}" step="${r.step}" value="${r.lo}" aria-label="Minimo ${esc15(d.label)}">
          <input type="range" data-v15-range="${key}" data-bound="hi" min="${r.min}" max="${r.max}" step="${r.step}" value="${r.hi}" aria-label="Massimo ${esc15(d.label)}">
        </div>
        <div class="v15-range-ends"><small>${fmt15(r.min,d.step)}</small><button type="button" data-v15-range-reset="${key}">azzera</button><small>${fmt15(r.max,d.step)}</small></div>
      </div>
    </div>`;
  }

  function header15(){
    const players=state.list?.players||[];ensureRanges15(players);
    const teams=[...new Set(players.map(p=>p?.serie_a_team).filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b),'it'));
    return `<tr class="v15-sort-row">
      <th class="v15-role-col">${sortButton15('role','Ruoli')}</th><th>${sortButton15('name','Nome')}</th><th>${sortButton15('team','Squadra')}</th><th>${sortButton15('badge','Badge')}</th><th>${sortButton15('slot','Slot')}</th><th>${sortButton15('presence','%Tit')}</th><th>${sortButton15('pfc','PFC')}</th><th>${sortButton15('pma','PMA')}</th><th>${sortButton15('delta','Delta')}</th><th>${sortButton15('index','Indice cr')}</th><th>${sortButton15('threshold','Soglia')}</th><th>${sortButton15('expected','Prezzo atteso')}</th><th>${sortButton15('fmv','FMV')}</th><th>${sortButton15('favorite','Preferito')}</th>
    </tr><tr class="v15-filter-row">
      <th class="v15-role-col"><span class="v15-role-note">filtrato sopra</span></th>
      <th>${textSearch15('name','cerca')}</th>
      <th>${select15('team',teams.map(x=>[x,x]))}</th>
      <th>${select15('badge',[['market','mercato'],['injury','indisp.'],['new','nuovo'],['penalties','rigori'],['free_kicks','piazzati']])}</th>
      <th>${rangeControl15('slot')}</th><th>${rangeControl15('presence')}</th><th>${rangeControl15('pfc')}</th><th>${rangeControl15('pma')}</th><th>${rangeControl15('delta')}</th><th>${rangeControl15('index')}</th><th>${rangeControl15('threshold')}</th><th>${rangeControl15('expected')}</th><th>${rangeControl15('fmv')}</th>
      <th>${select15('favorite',[['yes','sì'],['no','no']])}</th>
    </tr>`;
  }

  function heart15(p){const yes=v15Favorite(p),source=String(p?.source_player_id||p?.id||'');return `<button type="button" class="v13-heart ${yes?'active':''}" data-v13-fav="${esc15(source)}" data-v13-player="${esc15(p?.id||'')}" aria-pressed="${yes?'true':'false'}" title="${yes?'Rimuovi dai preferiti':'Aggiungi ai preferiti'}">${yes?'♥':'♡'}</button>`}
  function row15(p){
    const rs=roles15(p),sig=badges15(p),d=v15Delta(p),presence=v15Presence(p),fmv=v15Fmv(p),idx=typeof strategicValueIndex==='function'?strategicValueIndex(p):0,thr=typeof strategicThresholdPrice==='function'?strategicThresholdPrice(p):0,exp=typeof strategicExpectedPrice==='function'?strategicExpectedPrice(p):0;
    return `<tr data-player-id="${esc15(p?.id||'')}">
      <td class="v15-role-col">${rs.map(r=>`<span class="rolebadge" data-role="${esc15(r)}">${esc15(r)}</span>`).join('')}</td>
      <td class="v15-name"><strong>${esc15(p?.name||'—')}</strong></td><td>${esc15(p?.serie_a_team||'—')}</td><td class="v15-badges">${sig}</td><td class="num">${esc15(p?.slot??'—')}</td><td class="num">${Math.round(presence)}%</td><td class="num"><strong>${fmt15(p?.pfc,1)}</strong></td><td class="num">${fmt15(p?.pma,1)}</td><td class="num ${d>0?'positive':d<0?'negative':''}">${d==null?'—':`${d>0?'+':''}${fmt15(d,1)}`}</td><td class="num strategic-index-value" title="${typeof strategicIndexTitle==='function'?esc15(strategicIndexTitle(p)):''}">${fmt15(idx,1)}</td><td class="num">${fmt15(thr,1)}</td><td class="num">${fmt15(exp,1)}</td><td class="num">${fmt15(fmv,.01)}</td><td class="v15-fav-cell">${heart15(p)}</td>
    </tr>`;
  }

  function body15(){const body=document.getElementById('list-body');if(!body)return;const rows=rows15();body.innerHTML=rows.map(row15).join('')||'<tr><td colspan="14" class="soft" style="text-align:center;height:60px">Nessun giocatore.</td></tr>';}
  function full15(){if(!state.list)return;const thead=document.querySelector('#view-list .player-table thead');if(thead)thead.innerHTML=header15();body15();requestAnimationFrame(updateAllRangeVisuals15);}
  renderListTable=full15;

  function updateRangeVisual15(key){
    const r=state.v15Ranges?.[key],d=V15_NUMERIC[key];if(!r)return;
    document.querySelectorAll(`[data-v15-range-label="${key}"]`).forEach(x=>x.textContent=rangeLabel15(key));
    document.querySelectorAll(`[data-v15-lo-label="${key}"]`).forEach(x=>x.textContent=fmt15(r.lo,d.step));
    document.querySelectorAll(`[data-v15-hi-label="${key}"]`).forEach(x=>x.textContent=fmt15(r.hi,d.step));
    const span=Math.max(r.step,r.max-r.min),a=(r.lo-r.min)/span*100,b=(r.hi-r.min)/span*100;
    document.querySelectorAll(`[data-v15-range-fill="${key}"]`).forEach(x=>{x.style.left=`${a}%`;x.style.width=`${Math.max(0,b-a)}%`;});
  }
  function updateAllRangeVisuals15(){Object.keys(V15_NUMERIC).forEach(updateRangeVisual15)}
  function closeRanges15(except=''){document.querySelectorAll('[data-v15-range-popover]').forEach(x=>{if(x.dataset.v15RangePopover!==except)x.hidden=true});document.querySelectorAll('[data-v15-range-box]').forEach(x=>x.classList.toggle('open',x.dataset.v15RangeBox===except&&!x.querySelector('[data-v15-range-popover]')?.hidden));}

  const view=document.querySelector('#view-list');
  view?.addEventListener('click',e=>{
    const sort=e.target.closest?.('[data-v15-sort]');
    if(sort){e.preventDefault();const key=sort.dataset.v15Sort;state.listSort=state.listSort?.key===key?{key,direction:state.listSort.direction==='asc'?'desc':'asc'}:{key,direction:'asc'};full15();return;}
    const toggle=e.target.closest?.('[data-v15-range-toggle]');
    if(toggle){e.preventDefault();e.stopPropagation();const key=toggle.dataset.v15RangeToggle,pop=view.querySelector(`[data-v15-range-popover="${key}"]`),open=pop?.hidden!==false;closeRanges15(open?key:'');if(pop)pop.hidden=!open;toggle.closest('.v15-range')?.classList.toggle('open',open);if(open)updateRangeVisual15(key);return;}
    const reset=e.target.closest?.('[data-v15-range-reset]');
    if(reset){e.preventDefault();e.stopPropagation();const key=reset.dataset.v15RangeReset,r=state.v15Ranges[key];if(r){r.lo=r.min;r.hi=r.max;view.querySelectorAll(`[data-v15-range="${key}"][data-bound="lo"]`).forEach(x=>x.value=r.lo);view.querySelectorAll(`[data-v15-range="${key}"][data-bound="hi"]`).forEach(x=>x.value=r.hi);updateRangeVisual15(key);body15();}return;}
  },true);

  view?.addEventListener('input',e=>{
    const range=e.target.closest?.('[data-v15-range]');
    if(range){e.stopImmediatePropagation();const key=range.dataset.v15Range,bound=range.dataset.bound,r=state.v15Ranges[key];if(!r)return;let v=Number(range.value);if(bound==='lo'){r.lo=Math.min(v,r.hi);range.value=r.lo}else{r.hi=Math.max(v,r.lo);range.value=r.hi}updateRangeVisual15(key);body15();return;}
    const text=e.target.closest?.('[data-v15-text]');
    if(text&&text.tagName!=='SELECT'){e.stopImmediatePropagation();state.v15TextFilters[text.dataset.v15Text]=text.value;body15();}
  },true);
  view?.addEventListener('change',e=>{
    const text=e.target.closest?.('[data-v15-text]');if(text){e.stopImmediatePropagation();state.v15TextFilters[text.dataset.v15Text]=text.value;body15();}
  },true);
  document.addEventListener('click',e=>{if(!e.target.closest?.('.v15-range'))closeRanges15('')});

  function toolbar15(){
    const row=document.querySelector('#view-list .v12-toolbar-row');if(!row)return;
    row.querySelector('.filters')?.setAttribute('hidden','');
    const rolebar=document.getElementById('list-rolebar'),btn=document.getElementById('v13-import-button'),file=document.getElementById('v13-import-file');
    if(rolebar&&btn){let tools=row.querySelector('.v15-role-tools');if(!tools){tools=document.createElement('div');tools.className='v15-role-tools';row.appendChild(tools)}if(file)tools.appendChild(file);tools.appendChild(btn);}
  }
  if(typeof loadList==='function'){
    const oldLoad15=loadList;
    loadList=async function(...args){const r=await oldLoad15(...args);toolbar15();full15();return r;};
  }

  const css=document.createElement('style');css.id='v15-range-listone-style';css.textContent=`
    #view-list .table-wrap{position:relative!important;overflow:auto!important;min-height:0!important;isolation:isolate}
    #view-list .player-table{width:100%!important;min-width:0!important;max-width:100%!important;table-layout:auto!important;border-collapse:separate!important;border-spacing:0!important}
    #view-list .player-table thead{position:relative;z-index:20}
    #view-list .v15-sort-row th{position:sticky!important;top:0!important;z-index:22!important;height:30px!important;padding:2px 4px!important;background:#0d2b46!important;border-bottom:1px solid rgba(91,151,216,.35)!important}
    #view-list .v15-filter-row th{position:sticky!important;top:30px!important;z-index:21!important;height:30px!important;padding:2px 3px!important;background:#0a253e!important;border-bottom:1px solid rgba(91,151,216,.38)!important;overflow:visible!important}
    #view-list .v15-sort{width:100%!important;height:24px!important;min-height:24px!important;padding:1px 3px!important;border:0!important;background:transparent!important;box-shadow:none!important;color:var(--soft)!important;font-size:7px!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:3px!important;white-space:nowrap!important}
    #view-list .v15-text-filter,#view-list .v15-range-toggle{width:100%!important;height:23px!important;min-height:23px!important;margin:0!important;padding:1px 4px!important;border-radius:5px!important;border:1px solid rgba(91,151,216,.28)!important;background:rgba(5,22,38,.92)!important;color:var(--text)!important;font-size:7px!important}
    #view-list input[type=search].v15-text-filter{text-align:left!important}
    #view-list .v15-select{text-overflow:ellipsis!important}
    #view-list .v15-range{position:relative;min-width:54px}
    #view-list .v15-range-toggle{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:3px!important;white-space:nowrap!important}
    #view-list .v15-range-toggle i{font-style:normal;color:var(--soft);transition:transform .15s ease}
    #view-list .v15-range.open .v15-range-toggle i{transform:rotate(180deg)}
    #view-list .v15-range-popover{position:absolute;top:25px;left:50%;transform:translateX(-50%);width:190px;padding:8px;border:1px solid rgba(104,164,225,.48);border-radius:8px;background:#081f35;box-shadow:0 12px 32px rgba(0,0,0,.48);z-index:80}
    #view-list .v15-filter-row th:nth-child(n+10) .v15-range-popover{left:auto;right:0;transform:none}
    #view-list .v15-range-values{display:grid;grid-template-columns:48px 1fr 48px;gap:4px;align-items:center;margin-bottom:7px;font-size:8px}
    #view-list .v15-range-values b:first-child{text-align:left}#view-list .v15-range-values b:last-child{text-align:right}#view-list .v15-range-values span{text-align:center;color:var(--soft);font-size:6px;text-transform:uppercase}
    #view-list .v15-dual-range{position:relative;height:24px;margin:0 7px}
    #view-list .v15-range-base,#view-list .v15-range-fill{position:absolute;left:0;right:0;top:11px;height:3px;border-radius:99px;background:rgba(255,255,255,.14)}
    #view-list .v15-range-fill{right:auto;background:#4f9bea}
    #view-list .v15-dual-range input[type=range]{position:absolute;left:0;top:3px;width:100%!important;height:18px!important;margin:0!important;padding:0!important;background:transparent!important;pointer-events:none;-webkit-appearance:none;appearance:none}
    #view-list .v15-dual-range input[type=range]::-webkit-slider-runnable-track{height:3px;background:transparent}
    #view-list .v15-dual-range input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:14px;height:14px;margin-top:-5px;border-radius:50%;border:2px solid #9ed0ff;background:#1765ad;pointer-events:auto;cursor:ew-resize}
    #view-list .v15-dual-range input[type=range]::-moz-range-track{height:3px;background:transparent}
    #view-list .v15-dual-range input[type=range]::-moz-range-thumb{width:12px;height:12px;border-radius:50%;border:2px solid #9ed0ff;background:#1765ad;pointer-events:auto;cursor:ew-resize}
    #view-list .v15-range-ends{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:5px;color:var(--soft);font-size:6px}
    #view-list .v15-range-ends small:last-child{text-align:right}#view-list .v15-range-ends button{height:18px!important;min-height:18px!important;padding:1px 5px!important;font-size:6px!important}
    #view-list .v15-role-note{display:block;text-align:center;color:var(--soft);font-size:5.8px;white-space:nowrap}
    #view-list .v15-role-col{min-width:96px!important;width:96px!important;max-width:110px!important;white-space:nowrap!important}
    #view-list tbody .v15-role-col{display:table-cell!important}
    #view-list tbody .v15-role-col .rolebadge{display:inline-flex!important;min-width:25px!important;height:18px!important;padding:1px 4px!important;margin-right:2px!important;font-size:6.5px!important;vertical-align:middle!important}
    #view-list .player-table tbody td{height:35px!important;padding:4px 5px!important;font-size:9.5px!important;white-space:nowrap!important}
    #view-list .player-table tbody td.num{font-size:10.5px!important;font-weight:780!important;font-variant-numeric:tabular-nums!important}
    #view-list .v15-name strong{font-size:9.8px!important}
    #view-list .v15-badges{min-width:54px!important;text-align:center!important}
    #view-list .v15-fav-cell{min-width:42px!important;text-align:center!important}
    #view-list .v12-toolbar-row{grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important}
    #view-list .v12-toolbar-row .filters{display:none!important}
    #view-list .v15-role-tools{display:flex;align-items:center;gap:4px;justify-content:flex-end}
    #view-list #list-rolebar{min-width:0;overflow-x:auto!important;white-space:nowrap!important}
    #view-list #v13-import-button{height:28px!important;min-height:28px!important;white-space:nowrap!important}
  `;document.head.appendChild(css);

  toolbar15();if(state.view==='list'&&state.list)full15();
})();
</script>
'''
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
