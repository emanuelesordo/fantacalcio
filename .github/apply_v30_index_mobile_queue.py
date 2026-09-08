from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

# Idempotent re-run support.
text=re.sub(r'\n<style id="v30-index-mobile-queue-style">.*?</style>\n','\n',text,flags=re.S)
text=re.sub(r'\n<script id="v30-index-mobile-queue-runtime">.*?</script>\n','\n',text,flags=re.S)

style=r'''
<style id="v30-index-mobile-queue-style">
/* V30: one shared PFC/PMA-vs-Index gradient for Listone and live auction. */
body.v10-index-owner #view-list tr.v30-index-market-row,
body.v10-index-owner #view-auction tr.v30-index-market-row{
  background:linear-gradient(90deg,hsl(var(--v30-market-hue) 74% 46% / var(--v30-market-alpha)),transparent 84%)!important;
  box-shadow:inset 3px 0 0 hsl(var(--v30-market-hue) 80% 50% / .76)!important;
  transition:background .18s ease,box-shadow .18s ease!important;
}

/* Banditore: all auction function buttons keep the same footprint; finish is reordered by JS. */
#view-auction .v30-auction-functions > button{
  width:100%!important;
  min-width:0!important;
  max-width:none!important;
  height:42px!important;
  min-height:42px!important;
  max-height:42px!important;
  padding:4px 6px!important;
  align-self:stretch!important;
}
#view-auction .v30-auction-functions > #auction-finish{grid-column:auto!important;grid-row:auto!important}

/* Mobile queue card between drawer shortcuts and bid console. */
@media(max-width:820px){
  body.v23-mobile-auction .v23-mobile-shell{
    grid-template-rows:auto auto auto minmax(0,1fr) auto!important;
  }
  .v30-mobile-queue{
    min-height:0!important;
    overflow:hidden!important;
    display:grid!important;
    grid-template-rows:32px minmax(0,1fr)!important;
    border:1px solid var(--line2)!important;
    border-radius:11px!important;
    background:rgba(9,31,54,.92)!important;
  }
  .v30-mobile-queue>header{
    min-width:0!important;
    display:flex!important;
    align-items:center!important;
    justify-content:space-between!important;
    gap:6px!important;
    padding:4px 7px!important;
    border-bottom:1px solid var(--line)!important;
  }
  .v30-mobile-queue>header strong{font-size:10px!important;letter-spacing:.04em!important}
  .v30-mobile-queue>header span{min-width:22px!important;text-align:center!important;padding:2px 5px!important;border-radius:99px!important;background:var(--primary)!important;font-size:8px!important;font-weight:900!important}
  .v30-mobile-queue-list{
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    -webkit-overflow-scrolling:touch!important;
    overscroll-behavior:contain!important;
    touch-action:pan-y!important;
    padding:4px!important;
    display:grid!important;
    align-content:start!important;
    gap:3px!important;
  }
  .v30-mobile-queue-row{
    min-height:43px!important;
    display:grid!important;
    grid-template-columns:56px minmax(0,1fr) 38px 58px 30px!important;
    gap:4px!important;
    align-items:center!important;
    padding:4px 5px!important;
    border:1px solid rgba(72,125,180,.50)!important;
    border-radius:7px!important;
    background:var(--panel2)!important;
  }
  .v30-mobile-queue-role{display:flex!important;gap:2px!important;flex-wrap:wrap!important;min-width:0!important}
  .v30-mobile-queue-role .rolebadge{min-width:22px!important;height:21px!important;padding:1px 4px!important;font-size:7px!important;font-style:normal!important}
  .v30-mobile-queue-copy{min-width:0!important}
  .v30-mobile-queue-copy strong{display:block!important;font-size:9px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
  .v30-mobile-queue-copy small{display:block!important;margin-top:1px!important;color:var(--soft)!important;font-size:6.5px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
  .v30-mobile-queue-pfc{text-align:center!important;color:#c5d6e8!important;font-size:8px!important;font-weight:900!important}
  .v30-mobile-queue-price{height:31px!important;min-height:31px!important;padding:2px 3px!important;text-align:center!important;font-size:11px!important;font-weight:900!important}
  .v30-mobile-queue-remove{width:30px!important;min-width:30px!important;height:30px!important;min-height:30px!important;padding:0!important;border-radius:8px!important;background:var(--danger)!important;font-size:16px!important}
  .v30-mobile-queue-empty{padding:12px!important;text-align:center!important;color:var(--soft)!important;font-size:8px!important}

  /* Mobile free agents: roles | identity | PFC/FMV/TIT | actions. */
  .v23-mobile-free-row{
    grid-template-columns:72px minmax(0,1fr) 68px 70px!important;
    gap:5px!important;
    min-height:68px!important;
  }
  .v30-mobile-free-stats{
    display:grid!important;
    gap:2px!important;
    align-content:center!important;
    text-align:right!important;
    font-variant-numeric:tabular-nums!important;
  }
  .v30-mobile-free-stats span{display:flex!important;justify-content:space-between!important;gap:3px!important;color:var(--soft)!important;font-size:6.5px!important;line-height:1.05!important}
  .v30-mobile-free-stats b{color:var(--text)!important;font-size:7.5px!important}
  .v30-mobile-free-actions{display:grid!important;grid-template-rows:1fr 1fr!important;gap:3px!important;align-self:stretch!important}
  .v30-mobile-free-actions button{width:100%!important;min-width:0!important;height:auto!important;min-height:29px!important;max-height:none!important;padding:2px 3px!important;border-radius:7px!important;font-size:7.5px!important}
  .v30-mobile-free-actions .v30-queue-add{background:var(--panel3)!important;border-color:var(--line2)!important}

  /* Direct-call opening-price modal. */
  dialog.v30-mobile-call-dialog{
    width:min(360px,calc(100vw - 24px))!important;
    max-width:none!important;
    padding:0!important;
    border:1px solid var(--line2)!important;
    border-radius:14px!important;
    background:#091d33!important;
    color:var(--text)!important;
    box-shadow:0 24px 75px rgba(0,0,0,.60)!important;
  }
  dialog.v30-mobile-call-dialog::backdrop{background:rgba(2,8,16,.72)!important;backdrop-filter:blur(4px)!important}
  .v30-mobile-call-form{display:grid!important;gap:10px!important;padding:14px!important}
  .v30-mobile-call-form header{display:flex!important;justify-content:space-between!important;align-items:start!important;gap:8px!important}
  .v30-mobile-call-form header strong{display:block!important;font-size:17px!important}
  .v30-mobile-call-form header small{display:block!important;margin-top:2px!important;color:var(--soft)!important;font-size:9px!important}
  .v30-mobile-call-form label{font-size:9px!important}
  .v30-mobile-call-form input{height:52px!important;min-height:52px!important;text-align:center!important;font-size:24px!important;font-weight:950!important}
  .v30-mobile-call-actions{display:grid!important;grid-template-columns:1fr 1.3fr!important;gap:6px!important}
  .v30-mobile-call-actions button{min-height:44px!important}

  @media(max-width:390px){
    .v23-mobile-free-row{grid-template-columns:64px minmax(0,1fr) 61px 62px!important;gap:4px!important}
    .v30-mobile-queue-row{grid-template-columns:50px minmax(0,1fr) 34px 54px 28px!important;gap:3px!important}
    .v30-mobile-queue-remove{width:28px!important;min-width:28px!important}
  }
}
</style>
'''

runtime=r'''
<script id="v30-index-mobile-queue-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V30_INDEX_MOBILE_QUEUE__)return;
  window.__FANTA_V30_INDEX_MOBILE_QUEUE__=1;

  const qs=(s,r=document)=>r.querySelector(s);
  const qsa=(s,r=document)=>[...r.querySelectorAll(s)];
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const num=v=>Number.isFinite(Number(v))?Number(v):null;
  const esc30=v=>{try{return typeof esc==='function'?esc(v):String(v??'')}catch{return String(v??'')}};
  const owner30=()=>String(state.dashboard?.currentUser?.username||state.session?.user?.username||'').trim().toLowerCase()==='emanuelesordo';
  const playerRoles30=p=>{try{return typeof playerRoles==='function'?playerRoles(p||{},state.auction?.settings?.fantasy_mode||state.setup?.fantasy_mode||'classic'):[]}catch{return[]}};
  const roleTone30=r=>{r=String(r||'').toLowerCase();if(['p','por'].includes(r))return'por';if(['d','b','dc','dd','ds'].includes(r))return'def';if(['e','m','c'].includes(r))return'mid';if(['w','t'].includes(r))return'wing';if(['a','pc'].includes(r))return'att';return'other'};
  const rolesHtml30=p=>playerRoles30(p).map(r=>`<i class="rolebadge v23-role-${roleTone30(r)}">${esc30(r)}</i>`).join('');
  const pfc30=p=>num(p?.pfc)??num(p?.quotation)??null;
  const fmv30=p=>{try{const v=typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):null;if(num(v)!=null)return num(v)}catch{}return num(p?.expected_fantasy_avg)??num(p?.strategic_features?.forecast_fantasy_avg)??null};
  const tit30=p=>{try{const v=typeof strategicPresencePercent==='function'?strategicPresencePercent(p):null;if(num(v)!=null)return num(v)}catch{}let v=num(p?.expected_titolarity)??num(p?.strategic_features?.forecast_presence);if(v!=null&&v<=1)v*=100;return v};
  const fmt30=(v,d=0)=>num(v)==null?'—':Number(v).toFixed(d).replace('.',',');

  /* ---------------------------------------------------------
     Shared continuous PFC/PMA vs Index gradient
     --------------------------------------------------------- */
  function paintRows30(root,players){
    if(!root)return;
    const by=new Map((players||[]).map(p=>[String(p.id),p]));
    root.querySelectorAll('tr[data-player-id]').forEach(row=>{
      row.classList.remove('v22-market-value-row','auction-market-value-row','v10-private-delta-row','v30-index-market-row');
      ['--v22-hue','--v22-alpha','--auction-market-hue','--auction-market-alpha','--v10-delta-hue','--v10-delta-alpha','--v30-market-hue','--v30-market-alpha'].forEach(k=>row.style.removeProperty(k));
      if(!owner30())return;
      const p=by.get(String(row.dataset.playerId));if(!p)return;
      let idx=null;try{idx=typeof strategicValueIndex==='function'?num(strategicValueIndex(p)):null}catch{}
      if(idx==null||idx<=0)return;
      const values=[num(p?.pfc),num(p?.pma)].filter(v=>v!=null&&v>=0);if(!values.length)return;
      const signed=values.reduce((s,v)=>s+(idx-v)/Math.max(1,idx),0)/values.length;
      const strength=clamp(Math.abs(signed)/.35,0,1);
      const hue=signed>=0?48+84*strength:48*(1-strength); // red 0 -> yellow 48 -> green 132
      const alpha=.045+.125*strength;
      row.classList.add('v30-index-market-row');
      row.style.setProperty('--v30-market-hue',hue.toFixed(1));
      row.style.setProperty('--v30-market-alpha',alpha.toFixed(3));
      const ref=values.reduce((a,b)=>a+b,0)/values.length;
      row.title=`Indice ${Math.round(idx)} cr · riferimento PFC/PMA ${ref.toFixed(1)} · ${signed>.03?'sotto Indice / conveniente':signed<-.03?'sopra Indice / caro':'zona soglia'}`;
    });
  }
  let paintFrame30=0;
  function paintAll30(){
    cancelAnimationFrame(paintFrame30);
    paintFrame30=requestAnimationFrame(()=>{
      paintRows30(document.getElementById('list-body'),state.list?.players||[]);
      paintRows30(document.getElementById('auction-player-body'),state.auction?.callCandidates||[]);
    });
  }

  /* Tooltip Index: clarify source of target and theoretical starter quota. */
  if(typeof strategicIndexTitle==='function'&&typeof window.v21IndexBreakdown==='function'){
    strategicIndexTitle=function(player){
      const x=window.v21IndexBreakdown(player);if(!x)return'Indice non disponibile';
      const value=Math.max(0,Math.round(x.value||0));
      const mantra=(state.auction?.settings?.fantasy_mode||state.setup?.fantasy_mode||state.list?.settings?.fantasyMode)==='mantra';
      const rules=state.v9Rules||{};
      const classicBase=rules.defense_rule_enabled?(rules.clean_sheet_bonus_enabled?73.2:73.0):(rules.clean_sheet_bonus_enabled?72.0:71.1);
      const adjustment=mantra?-.5:0;
      const source=`benchmark ${classicBase.toFixed(2)}${mantra?' - 0.50 Mantra':''}`;
      return `Indice ${value} cr · ${x.keeper?'POR':'MOV'} · target squadra ${x.targetAverage.toFixed(2)} (${source}) · target ruolo ${x.roleTarget.toFixed(2)} · quota teorica titolare ${x.equilibriumBudget.toFixed(1)} cr = ${x.budget.toFixed(0)} × ${x.roleTarget.toFixed(2)} / ${x.targetAverage.toFixed(2)} · FMV ${x.fmv.toFixed(2)} × ${x.games.toFixed(1)} gare = ${x.rawPoints.toFixed(1)} pt · peso utilizzo slot ${x.slot}: ${(x.usage*100).toFixed(0)}% → ${x.usefulPoints.toFixed(1)} pt utili · 1 pt = ${x.creditPerPoint.toFixed(3)} cr · nessun prezzo di mercato`;
    };
  }

  /* ---------------------------------------------------------
     Banditore function grid
     --------------------------------------------------------- */
  function normalizeBanditore30(){
    const finish=document.getElementById('auction-finish');if(!finish)return;
    const parent=finish.parentElement;if(!parent)return;
    parent.classList.add('v30-auction-functions');
    const directButtons=[...parent.children].filter(x=>x.tagName==='BUTTON');
    if(directButtons.at(-1)!==finish)parent.appendChild(finish);
  }

  /* ---------------------------------------------------------
     Mobile free agents + queue
     --------------------------------------------------------- */
  const phone30=()=>window.matchMedia('(max-width:820px)').matches&&document.body.classList.contains('v23-mobile-auction');
  const canCall30=()=>{const s=state.auction?.auctionSession;if(!s||s.current_player_id)return false;try{return typeof auctionOwnCallTurn==='function'&&auctionOwnCallTurn()}catch{return false}};
  const canQueue30=()=>{try{return typeof auctionCanManageCallQueue==='function'&&auctionCanManageCallQueue()}catch{return false}};
  const queueRows30=()=>{try{return typeof auctionQueueRows==='function'?auctionQueueRows():[]}catch{return[]}};
  const playerById30=id=>(state.auction?.callCandidates||[]).find(p=>String(p.id)===String(id))||queueRows30().find(q=>String(q.player_id)===String(id))?.player||null;

  function ensureQueueCard30(){
    const shell=qs('.v23-mobile-shell'),drawers=qs('.v23-mobile-drawers',shell);if(!shell||!drawers)return null;
    let card=qs('.v30-mobile-queue',shell);
    if(!card){
      card=document.createElement('section');card.className='v30-mobile-queue';card.innerHTML='<header><strong>CODA CHIAMATE</strong><span data-v30-queue-count>0</span></header><div class="v30-mobile-queue-list" data-v30-queue-list></div>';
      drawers.insertAdjacentElement('afterend',card);
    }
    return card;
  }

  function renderQueue30(){
    const card=ensureQueueCard30();if(!card)return;
    const list=qs('[data-v30-queue-list]',card),count=qs('[data-v30-queue-count]',card),rows=queueRows30();if(count)count.textContent=String(rows.length);
    if(!list)return;
    if(document.activeElement?.matches?.('[data-v30-queue-price]'))return;
    const oldTop=list.scrollTop;
    list.innerHTML=rows.length?rows.map(item=>{const p=item.player||playerById30(item.player_id)||{},editable=canQueue30();return `<div class="v30-mobile-queue-row" data-v30-queue-player="${esc30(item.player_id)}"><div class="v30-mobile-queue-role">${rolesHtml30(p)}</div><div class="v30-mobile-queue-copy"><strong>${esc30(p.name||'Giocatore')}</strong><small>${esc30(p.serie_a_team||'—')}</small></div><span class="v30-mobile-queue-pfc" title="PFC">${fmt30(pfc30(p),0)}</span><input class="v30-mobile-queue-price" data-v30-queue-price="${esc30(item.player_id)}" type="number" inputmode="numeric" min="1" step="1" value="${Math.max(1,Number(item.opening_bid||1))}" ${editable?'':'disabled'} aria-label="Prezzo base ${esc30(p.name||'giocatore')}"><button type="button" class="v30-mobile-queue-remove" data-v30-queue-remove="${esc30(item.player_id)}" ${editable?'':'disabled'} aria-label="Rimuovi ${esc30(p.name||'giocatore')} dalla coda">×</button></div>`}).join(''):'<div class="v30-mobile-queue-empty">Coda vuota · aggiungi un giocatore dagli svincolati.</div>';
    list.scrollTop=oldTop;
  }

  function freeCandidates30(){
    const input=qs('[data-v23-free-search]'),q=String(input?.value||'').trim();
    return (state.auction?.callCandidates||[]).filter(p=>(!p.status||p.status==='available')&&String(p.id)!==String(state.auction?.auctionSession?.current_player_id||'')).filter(p=>{if(!q)return true;try{return typeof playerSearchRank==='function'?playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null:String(p.name||'').toLowerCase().includes(q.toLowerCase())}catch{return true}}).sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'it')).slice(0,120);
  }

  function renderFree30(){
    const host=qs('[data-v23-free-list]');if(!host||!document.body.classList.contains('v23-free-open'))return;
    const queued=new Set(queueRows30().map(x=>String(x.player_id))),callable=canCall30(),queueable=canQueue30(),oldTop=host.scrollTop;
    host.innerHTML=freeCandidates30().map(p=>{const inQueue=queued.has(String(p.id)),fm=fmv30(p),tit=tit30(p);return `<div class="v23-mobile-drawer-row v23-mobile-free-row"><div class="v23-mobile-drawer-roles">${rolesHtml30(p)}</div><div class="v23-mobile-drawer-player"><strong>${esc30(p.name||'—')}</strong><small>${esc30(p.serie_a_team||'—')}</small></div><div class="v30-mobile-free-stats"><span>PFC <b>${fmt30(pfc30(p),0)}</b></span><span>FMV <b>${fmt30(fm,2)}</b></span><span>TIT <b>${fmt30(tit,0)}${tit==null?'':'%'}</b></span></div><div class="v30-mobile-free-actions"><button type="button" data-v30-mobile-direct="${esc30(p.id)}" ${callable?'':'disabled'}>CHIAMA</button><button type="button" class="v30-queue-add" data-v30-mobile-queue-add="${esc30(p.id)}" ${queueable&&!inQueue?'':'disabled'}>${inQueue?'IN CODA':'CODA'}</button></div></div>`}).join('')||'<div class="v23-mobile-empty">Nessun giocatore disponibile.</div>';
    host.scrollTop=oldTop;
  }

  function ensureCallDialog30(){
    let d=document.getElementById('v30-mobile-call-dialog');if(d)return d;
    d=document.createElement('dialog');d.id='v30-mobile-call-dialog';d.className='v30-mobile-call-dialog';d.innerHTML=`<form class="v30-mobile-call-form"><header><div><small>CHIAMATA DIRETTA</small><strong data-v30-call-name>Giocatore</strong><small data-v30-call-meta>—</small></div><button type="button" class="secondary" data-v30-call-cancel>×</button></header><label>Prezzo base<input data-v30-call-price type="number" inputmode="numeric" pattern="[0-9]*" min="1" step="1" value="1" autocomplete="off"></label><div class="v30-mobile-call-actions"><button type="button" class="secondary" data-v30-call-cancel>ANNULLA</button><button type="submit" class="good" data-v30-call-confirm>CHIAMA</button></div></form>`;
    document.body.appendChild(d);
    d.addEventListener('click',e=>{if(e.target.closest('[data-v30-call-cancel]'))d.close();});
    d.querySelector('form')?.addEventListener('submit',async e=>{
      e.preventDefault();const id=d.dataset.playerId,p=playerById30(id),input=qs('[data-v30-call-price]',d),button=qs('[data-v30-call-confirm]',d);if(!p||!canCall30())return;
      const price=Math.max(1,Math.floor(Number(input?.value||1)));if(input)input.value=String(price);if(button)button.disabled=true;
      try{
        const s=state.auction?.auctionSession;if(!s?.id)throw new Error('Sessione asta non disponibile.');
        const response=await api(ENDPOINTS.auction,{action:'callPlayer',sessionId:s.id,playerId:p.id,openingBid:price});
        state.auction.currentPlayer=p;if(response?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(response.state,{fromMutation:true});
        d.close();document.body.classList.remove('v23-free-open');const ui=qs('.v23-mobile-drawer-ui');if(ui)ui.hidden=true;
        if(typeof window.v11ScheduleAuctionRefresh==='function')window.v11ScheduleAuctionRefresh('mobile-direct-call',45);else if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(80);
      }catch(err){msg(err.message||'Chiamata non riuscita.','error')}finally{if(button)button.disabled=false;}
    });
    return d;
  }
  function openCallDialog30(p){
    const d=ensureCallDialog30();d.dataset.playerId=String(p.id);qs('[data-v30-call-name]',d).textContent=p.name||'Giocatore';qs('[data-v30-call-meta]',d).textContent=[playerRoles30(p).join('/'),p.serie_a_team].filter(Boolean).join(' · ');const input=qs('[data-v30-call-price]',d);if(input)input.value=String(Math.max(1,Number(state.auctionOpeningBid||1)));if(!d.open)d.showModal();requestAnimationFrame(()=>{try{input?.focus({preventScroll:true});input?.select()}catch{input?.focus();}});
  }

  async function addQueue30(id){
    if(!canQueue30()||typeof addPlayerToAuctionQueue!=='function')return;
    const promise=addPlayerToAuctionQueue(id,1);queueMicrotask(()=>{renderQueue30();renderFree30();});try{await promise}finally{renderQueue30();renderFree30();}
  }
  async function removeQueue30(id){
    if(!canQueue30()||typeof saveAuctionCallQueueItems!=='function')return;
    const items=queueRows30().filter(x=>String(x.player_id)!==String(id)).map(x=>({playerId:x.player_id,openingBid:Number(x.opening_bid||1)}));await saveAuctionCallQueueItems(items);renderQueue30();renderFree30();
  }
  async function priceQueue30(id,value){
    if(!canQueue30()||typeof saveAuctionCallQueueItems!=='function')return;
    const price=Math.max(1,Math.floor(Number(value||1))),items=queueRows30().map(x=>({playerId:x.player_id,openingBid:String(x.player_id)===String(id)?price:Number(x.opening_bid||1)}));await saveAuctionCallQueueItems(items);renderQueue30();
  }

  function syncMobile30(){
    if(!phone30())return;
    ensureQueueCard30();renderQueue30();if(document.body.classList.contains('v23-free-open'))renderFree30();
  }

  document.addEventListener('click',e=>{
    const direct=e.target.closest?.('[data-v30-mobile-direct]');if(direct){e.preventDefault();e.stopPropagation();const p=playerById30(direct.dataset.v30MobileDirect);if(p&&canCall30())openCallDialog30(p);return;}
    const add=e.target.closest?.('[data-v30-mobile-queue-add]');if(add){e.preventDefault();e.stopPropagation();void addQueue30(add.dataset.v30MobileQueueAdd);return;}
    const remove=e.target.closest?.('[data-v30-queue-remove]');if(remove){e.preventDefault();e.stopPropagation();void removeQueue30(remove.dataset.v30QueueRemove);return;}
  },true);
  document.addEventListener('input',e=>{if(e.target?.matches?.('[data-v23-free-search]'))queueMicrotask(renderFree30);},true);
  document.addEventListener('focusin',e=>{if(e.target?.matches?.('[data-v30-queue-price]'))requestAnimationFrame(()=>e.target.select());},true);
  document.addEventListener('change',e=>{if(e.target?.matches?.('[data-v30-queue-price]'))void priceQueue30(e.target.dataset.v30QueuePrice,e.target.value);},true);

  function scheduleUi30(){requestAnimationFrame(()=>{normalizeBanditore30();paintAll30();syncMobile30();});}
  if(typeof renderListTable==='function'){const old=renderListTable;renderListTable=function(...a){const r=old(...a);scheduleUi30();return r;};}
  if(typeof renderAuctionPlayers==='function'){const old=renderAuctionPlayers;renderAuctionPlayers=function(...a){const r=old(...a);scheduleUi30();return r;};}
  if(typeof renderAuctionLive==='function'){const old=renderAuctionLive;renderAuctionLive=function(...a){const r=old(...a);scheduleUi30();return r;};}
  if(typeof applyAuctionHotState==='function'){const old=applyAuctionHotState;applyAuctionHotState=function(...a){const r=old(...a);scheduleUi30();return r;};}

  const auctionView=document.getElementById('view-auction');if(auctionView){let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;normalizeBanditore30();syncMobile30();});}).observe(auctionView,{subtree:true,childList:true});}
  window.addEventListener('hashchange',()=>setTimeout(scheduleUi30,0));
  setInterval(()=>{if(phone30())syncMobile30();},900);
  scheduleUi30();
})();
</script>
'''

if '</head>' not in text or '</body>' not in text:
    raise RuntimeError('home.html closing markers not found')
text=text.replace('</head>',style+'\n</head>',1)
text=text.replace('</body>',runtime+'\n</body>',1)
p.write_text(text,encoding='utf-8')
