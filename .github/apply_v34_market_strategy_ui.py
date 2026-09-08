from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

text=re.sub(r'\n<style id="v34-market-strategy-style">.*?</style>\n','\n',text,flags=re.S)
text=re.sub(r'\n<script id="v34-market-strategy-runtime">.*?</script>\n','\n',text,flags=re.S)

# The auctioneer console must never be forced open after a mutation.
text=text.replace("              state.auctionAdminConsoleOpen = true;\n              msg('Asta avviata definitivamente.', 'success');",
                  "              state.auctionAdminConsoleOpen = false;\n              msg('Asta avviata definitivamente.', 'success');")

style=r'''
<style id="v34-market-strategy-style">
/* V34 · live auction: remove the fixed cockpit banner and reclaim its row. */
body.auction-live #view-auction .auction-statusbar{display:none!important}
body.auction-live #view-auction .auction-cockpit{grid-template-rows:minmax(0,1fr) auto!important}
body.auction-live .v33-manual-live-banner,
body.auction-live .v33-manual-flow-banner{display:none!important}

/* Manual flow: no visual timer. The called-player card receives the freed room. */
body.v34-manual-flow #view-auction .auction-status-timer,
body.v34-manual-flow #view-auction .auction-timer,
body.v34-manual-flow [data-v23-timer],
body.v34-manual-flow .v23-mobile-timer{display:none!important}
body.v34-manual-flow #view-auction .auction-player-hero{
  min-height:clamp(150px,25vh,250px)!important;
  height:auto!important;
  align-content:center!important;
}
body.v34-manual-flow .v23-mobile-current{grid-template-columns:minmax(0,1fr)!important}
body.v34-manual-flow .v23-mobile-player{grid-column:1/-1!important;min-width:0!important}

/* Manual mode keeps the queue fully usable; only autoplay/timers are disabled. */
body.v34-manual-flow #view-auction .auction-call-queue,
body.v34-manual-flow #view-auction .auction-call-queue[hidden],
body.v34-manual-flow .v30-mobile-queue,
body.v34-manual-flow .v30-mobile-queue[hidden]{display:grid!important}

/* Explicit queue call: green tick beside remove. */
.v34-queue-call{
  width:30px!important;min-width:30px!important;height:30px!important;min-height:30px!important;
  padding:0!important;border-radius:8px!important;background:var(--good,#1d9b62)!important;
  border-color:rgba(80,230,160,.72)!important;color:#fff!important;font-size:15px!important;font-weight:950!important;
}
@media(max-width:820px){
  .v30-mobile-queue-row{grid-template-columns:56px minmax(0,1fr) 38px 58px 30px 30px!important}
  @media(max-width:390px){.v30-mobile-queue-row{grid-template-columns:50px minmax(0,1fr) 34px 52px 28px 28px!important}.v34-queue-call{width:28px!important;min-width:28px!important}}
}

/* Smartphone navigation: only Listone / Rose / Asta for every role. */
@media(max-width:820px){
  #main-nav .nav-btn{display:none!important}
  #main-nav .nav-btn[data-view="list"],
  #main-nav .nav-btn[data-view="rosters"],
  #main-nav .nav-btn[data-view="auction"]{display:grid!important}
  #main-nav{grid-template-columns:repeat(3,minmax(0,1fr))!important;grid-auto-columns:auto!important}
}

/* Unknown Deal column. Hidden on phone: mobile Listone remains TIT/PFC/PMA/FMV only. */
.v34-ud-col{text-align:center!important;font-variant-numeric:tabular-nums!important;white-space:nowrap!important}
.v34-ud-col button{min-width:0!important;width:100%!important;padding:2px 3px!important;background:transparent!important;border:0!important;color:inherit!important;font:inherit!important}
.v34-ud-positive{color:#73e3a5!important;font-weight:950!important}
.v34-ud-negative{color:#ff8a86!important;font-weight:950!important}
.v34-ud-neutral{color:#f2d16b!important;font-weight:950!important}
@media(max-width:820px){.v34-ud-col{display:none!important}}

/* New suggester vocabulary: UD / O / MAX only. */
.auction-suggested-row.is-must-have{outline:2px solid rgba(242,193,78,.86)!important;outline-offset:-2px!important}
.auction-suggested-row .v34-suggest-metrics{display:grid!important;grid-template-columns:repeat(3,minmax(42px,1fr))!important;gap:3px!important;min-width:150px!important}
.auction-suggested-row .v34-suggest-metric{display:grid!important;place-items:center!important;min-height:34px!important;padding:3px 5px!important;border:1px solid var(--line2)!important;border-radius:7px!important;background:rgba(7,29,51,.74)!important}
.auction-suggested-row .v34-suggest-metric small{font-size:6px!important;line-height:1!important;color:var(--soft)!important;font-weight:900!important}
.auction-suggested-row .v34-suggest-metric b{font-size:11px!important;line-height:1.15!important;font-variant-numeric:tabular-nums!important}
.auction-suggested-row .v34-suggest-metric.ud.pos b{color:#73e3a5!important}.auction-suggested-row .v34-suggest-metric.ud.neg b{color:#ff8a86!important}.auction-suggested-row .v34-suggest-metric.ud.zero b{color:#f2d16b!important}
.auction-suggested-row .auction-v7-prices{display:none!important}
.auction-suggested-row .v8n em{display:none!important}
@media(max-width:820px){.auction-suggested-row .v34-suggest-metrics{min-width:132px!important;grid-template-columns:repeat(3,1fr)!important}.auction-suggested-row .v34-suggest-metric{padding:2px!important}}

/* Numeric cells remain centered in all tables. */
table td[data-type="number"],table th[data-type="number"],table td.num,table th.num,
#view-list td:not(:first-child),#view-auction .auction-free-table td:not(:nth-child(2)){text-align:center}
</style>
'''

runtime=r'''
<script id="v34-market-strategy-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V34_MARKET_STRATEGY__)return;
  window.__FANTA_V34_MARKET_STRATEGY__=1;

  const qs=(s,r=document)=>r.querySelector(s),qsa=(s,r=document)=>[...r.querySelectorAll(s)];
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const num=v=>Number.isFinite(Number(v))?Number(v):null;
  const esc34=v=>{try{return typeof esc==='function'?esc(v):String(v??'')}catch{return String(v??'')}};
  const MARKET_API=`${SUPABASE_URL}/functions/v1/strategy-market-api`;
  state.v34MarketContext=state.v34MarketContext||{teams:[],assignments:[],key:'',loadedAt:0};
  state.v34UdSort=state.v34UdSort||{list:0,auction:0};
  if(typeof state.v34AuctioneerOpen!=='boolean')state.v34AuctioneerOpen=false;

  function session34(){return typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession}
  function manual34(){const v=session34()?.setup_snapshot?.manual_auction_flow;return v===true||String(v).toLowerCase()==='true'}
  function mode34(){return state.auction?.settings?.fantasy_mode||state.setup?.fantasy_mode||state.list?.settings?.fantasyMode||'classic'}
  function roles34(p){try{return typeof playerRoles==='function'?playerRoles(p||{},mode34()):[]}catch{return mode34()==='mantra'?(p?.mantra_roles||[]):[p?.classic_role].filter(Boolean)}}
  function fmv34(p){try{const v=typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):null;if(num(v)!=null)return num(v)}catch{}return num(p?.expected_fantasy_avg)??0}
  function tit34(p){try{const v=typeof strategicPresencePercent==='function'?strategicPresencePercent(p):null;if(num(v)!=null)return num(v)}catch{}let v=num(p?.expected_titolarity);if(v!=null&&v<=1)v*=100;return v??0}
  function idx34(p){try{return Math.max(0,num(typeof strategicValueIndex==='function'?strategicValueIndex(p):null)??0)}catch{return 0}}
  function market34(p){const pma=num(p?.pma),pfc=num(p?.pfc);if(pma!=null&&pfc!=null)return .75*pma+.25*pfc;if(pma!=null)return pma;if(pfc!=null)return pfc;return num(p?.quotation)??0}
  function ud34(p){return idx34(p)-market34(p)}
  window.v34UnknownDeal=ud34;

  function overlap34(a,b){const A=new Set(roles34(a).map(x=>String(x).toLowerCase())),B=roles34(b).map(x=>String(x).toLowerCase());return B.some(x=>A.has(x))}
  function similarity34(a,b){
    if(!overlap34(a,b))return 0;
    const af=Math.max(.1,fmv34(a)),bf=Math.max(.1,fmv34(b)),at=tit34(a),bt=tit34(b);
    const fm=clamp(1-Math.abs(af-bf)/Math.max(.55,af*.16),0,1);
    const tt=clamp(1-Math.abs(at-bt)/22,0,1);
    return .62*fm+.38*tt;
  }

  async function loadMarket34(force=false){
    const leagueId=state.selectedLeague?.id||state.dashboard?.league?.id||state.auction?.league?.id||'';
    const s=session34();if(!leagueId||!s||s.status!=='live')return;
    const key=`${leagueId}:${s.id}:${s.version||0}`;
    if(!force&&state.v34MarketContext.key===key&&Date.now()-Number(state.v34MarketContext.loadedAt||0)<5000)return;
    if(state.v34MarketLoading)return;
    state.v34MarketLoading=true;
    try{
      const r=await api(MARKET_API,{action:'getMarketContext'},{quiet:true});
      state.v34MarketContext={teams:r?.teams||[],assignments:r?.assignments||[],key,loadedAt:Date.now()};
      patchAll34();
      if(typeof renderAuctionLive==='function'&&state.view==='auction')renderAuctionLive();
    }catch(e){console.warn('V34 market context',e)}finally{state.v34MarketLoading=false}
  }

  function marketStats34(p){
    const free=(state.auction?.callCandidates||[]).filter(x=>String(x.id)!==String(p.id));
    const bought=state.v34MarketContext?.assignments||[];
    const similarFree=free.filter(x=>similarity34(p,x)>=.58);
    const similarBought=bought.filter(x=>similarity34(p,x)>=.58);
    const teams=state.v34MarketContext?.teams||state.auction?.teams||[];
    const myId=state.auction?.myTeam?.teamId||null;
    const opponents=teams.filter(t=>String(t.id)!==String(myId));
    const interested=opponents.filter(t=>!similarBought.some(a=>String(a.team_id)===String(t.id))).length;
    const demandRatio=interested/Math.max(1,opponents.length);
    return{remainingSimilar:similarFree.length+1,boughtSimilar:similarBought.length,interested,opponents:opponents.length,demandRatio};
  }

  function opportunity34(p){
    const m=marketStats34(p);
    const lowDemand=1-m.demandRatio;
    const alternatives=clamp((m.remainingSimilar-1)/5,0,1);
    return Math.round(clamp(100*(.64*lowDemand+.36*alternatives),0,100));
  }
  window.v34Opportunity=opportunity34;

  function ownCapacity34(p){
    let info=null;try{info=typeof auctionMyTeamDashboardData==='function'?auctionMyTeamDashboardData():null}catch{}
    if(!info)return Infinity;
    const remaining=num(info.remaining);if(remaining==null)return Infinity;
    const assignments=info.assignments||[];
    const cfg=session34()?.setup_snapshot?.roster_config||state.auction?.settings?.roster_config||{};
    let reserve=0;
    if(mode34()!=='mantra'){
      const c=cfg.classic||{};const limit=['P','D','C','A'].reduce((s,k)=>s+Math.max(0,Number(c[k]||0)),0)||Number(info.rosterLimit||0);
      reserve=Math.max(0,limit-(assignments.length+1));
    }else{
      const c=cfg.mantra||{},isGk=roles34(p).some(r=>['p','por'].includes(String(r).toLowerCase()));
      const gk=assignments.filter(a=>roles34(a.player||a).some(r=>['p','por'].includes(String(r).toLowerCase()))).length;
      const newGk=gk+(isGk?1:0),newOut=assignments.length-gk+(isGk?0:1),newTotal=assignments.length+1;
      const mg=Math.max(0,Number(c.goalkeepers?.min||0)-newGk),mo=Math.max(0,Number(c.outfield?.min||0)-newOut),mt=Math.max(0,Number(c.total?.min||0)-newTotal);
      reserve=Math.max(mt,mg+mo);
    }
    return Math.max(0,Math.floor(remaining-reserve));
  }

  function max34(p){
    const idx=idx34(p),market=market34(p),m=marketStats34(p);
    if(idx<=0&&market<=0)return 1;
    const base=.64*idx+.36*market;
    const scarcity=1-clamp((m.remainingSimilar-1)/5,0,1);
    let premium=.20*scarcity+.10*m.demandRatio;
    if(m.remainingSimilar<=1)premium+=.06;
    const model=Math.max(1,Math.round(base*(1+premium)));
    const cap=ownCapacity34(p);
    return Number.isFinite(cap)?Math.max(1,Math.min(model,cap)):model;
  }
  window.v34MaxPrice=max34;

  function paintDeal34(root,players){
    if(!root)return;const by=new Map((players||[]).map(p=>[String(p.id),p]));
    root.querySelectorAll('tr[data-player-id]').forEach(row=>{
      const p=by.get(String(row.dataset.playerId));if(!p)return;
      const idx=idx34(p),ud=ud34(p),strength=clamp(Math.abs(ud)/Math.max(1,idx*.35),0,1),hue=ud>=0?48+84*strength:48*(1-strength),alpha=.045+.125*strength;
      row.classList.add('v30-index-market-row');row.style.setProperty('--v30-market-hue',hue.toFixed(1));row.style.setProperty('--v30-market-alpha',alpha.toFixed(3));
      row.title=`IDX ${Math.round(idx)} · PMA/PFC ${market34(p).toFixed(1)} · UD ${ud>=0?'+':''}${ud.toFixed(1)}`;
    });
  }

  function addUdColumn34(table,players,kind){
    if(!table||table.dataset.v34UdReady==='1')return;
    const headerRows=[...(table.tHead?.rows||[])],main=headerRows.find(r=>[...r.cells].some(c=>String(c.textContent||'').trim().toUpperCase()==='INDICE'));
    if(!main)return;
    const idx=[...main.cells].findIndex(c=>String(c.textContent||'').trim().toUpperCase()==='INDICE');if(idx<0)return;
    const th=document.createElement('th');th.className='v34-ud-col';th.innerHTML=`<button type="button" data-v34-ud-sort="${kind}" title="Unknown Deal = IDX − riferimento mercato (75% PMA, 25% PFC)">UD ↕</button>`;main.insertBefore(th,main.cells[idx+1]||null);
    headerRows.filter(r=>r!==main).forEach(r=>{if(r.cells.length>idx){const x=document.createElement('th');x.className='v34-ud-col';r.insertBefore(x,r.cells[idx+1]||null)}});
    const by=new Map((players||[]).map(p=>[String(p.id),p]));
    [...(table.tBodies?.[0]?.rows||[])].forEach(row=>{const p=by.get(String(row.dataset.playerId||''));if(!p||row.querySelector('.v34-ud-col'))return;const v=ud34(p),td=document.createElement('td');td.className=`v34-ud-col ${v>.5?'v34-ud-positive':v<-.5?'v34-ud-negative':'v34-ud-neutral'}`;td.dataset.v34Ud=String(v);td.textContent=`${v>0?'+':''}${v.toFixed(1).replace('.',',')}`;row.insertBefore(td,row.cells[idx+1]||null)});
    table.dataset.v34UdReady='1';
  }

  function sortUd34(kind){
    const table=kind==='list'?qs('#view-list table'):qs('#view-auction .auction-free-table');if(!table)return;
    const body=table.tBodies?.[0];if(!body)return;const dir=state.v34UdSort[kind]||0;
    if(!dir)return;
    [...body.rows].filter(r=>r.dataset.playerId).sort((a,b)=>(Number(a.querySelector('.v34-ud-col')?.dataset.v34Ud||0)-Number(b.querySelector('.v34-ud-col')?.dataset.v34Ud||0))*dir).forEach(r=>body.appendChild(r));
    const b=table.querySelector(`[data-v34-ud-sort="${kind}"]`);if(b)b.textContent=`UD ${dir>0?'↑':'↓'}`;
  }

  function queueCanCall34(){const s=session34();if(!s||s.current_player_id)return false;try{return Boolean(typeof auctionOwnCallTurn==='function'&&auctionOwnCallTurn())}catch{return false}}
  function injectQueueCalls34(){
    const rows=typeof auctionQueueRows==='function'?auctionQueueRows():state.auction?.myCallQueue||[];const byPlayer=new Map(rows.map(x=>[String(x.player_id),x]));
    qsa('.v30-mobile-queue-row[data-v30-queue-player]').forEach(row=>{if(row.querySelector('.v34-queue-call'))return;const q=byPlayer.get(String(row.dataset.v30QueuePlayer));const del=row.querySelector('[data-v30-queue-remove]');if(!q||!del)return;const b=document.createElement('button');b.type='button';b.className='v34-queue-call';b.dataset.v34QueueCall=q.id;b.textContent='✓';b.title='Chiama ora dalla coda';b.disabled=!queueCanCall34();del.insertAdjacentElement('beforebegin',b)});
    qsa('#view-auction [data-queue-player-id],#view-auction [data-queue-player]').forEach(row=>{if(row.classList.contains('v30-mobile-queue-row')||row.querySelector('.v34-queue-call'))return;const pid=row.dataset.queuePlayerId||row.dataset.queuePlayer;const q=byPlayer.get(String(pid));const del=row.querySelector('[data-queue-remove],[data-call-queue-remove],.auction-queue-remove');if(!q||!del)return;const b=document.createElement('button');b.type='button';b.className='v34-queue-call';b.dataset.v34QueueCall=q.id;b.textContent='✓';b.title='Chiama ora dalla coda';b.disabled=!queueCanCall34();del.insertAdjacentElement('beforebegin',b)});
  }

  async function callQueue34(id,button){if(!id||!queueCanCall34())return;button.disabled=true;try{await api(ENDPOINTS.auction,{action:'callQueuedPlayer',sessionId:session34().id,queueId:id});if(typeof msg==='function')msg('Giocatore chiamato dalla coda.','success');if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(50)}catch(e){if(typeof msg==='function')msg(e.message||'Chiamata non riuscita.','error');button.disabled=false}}

  function console34(){
    const d=qs('#auctioneer-console-drawer');if(!d)return;
    const pre=session34()?.prestart_hold===true;if(pre){d.open=true;return}
    const desired=state.v34AuctioneerOpen===true;if(d.open!==desired)d.open=desired;state.auctionAdminConsoleOpen=desired;
  }

  function patchSuggested34(){
    qsa('.auction-suggested-row').forEach((row,i)=>{row.querySelector('.v8n em')?.remove();row.querySelector('.auction-v7-prices')?.remove()});
  }

  /* Replace the old visible score/conv/SUGG model. Old scorer may still supply candidates, but is no longer exposed. */
  if(typeof renderAuctionSuggestedCalls==='function'&&typeof auctionSuggestedCalls==='function'){
    window.v34OldSuggestedRenderer=renderAuctionSuggestedCalls;
    renderAuctionSuggestedCalls=function(){
      const limit=document.fullscreenElement?8:4;
      let source=[];try{source=auctionSuggestedCalls(Math.max(limit*3,12))||[]}catch{}
      const hidden=state.v8Hidden||new Set();
      const items=source.map(x=>x?.player?x:{player:x}).filter(x=>x.player&&!hidden.has?.(String(x.player.id))).map(x=>{const p=x.player,ud=ud34(p),o=opportunity34(p),mx=max34(p),idx=idx34(p),mk=market34(p);const rank=(ud/Math.max(1,idx))*55+o*.34+(1-clamp((marketStats34(p).remainingSimilar-1)/5,0,1))*12;return{p,ud,o,mx,idx,mk,rank}}).sort((a,b)=>b.rank-a.rank).slice(0,limit);
      if(!items.length)return'';
      let can=false;try{can=typeof auctionHasPresidentRole==='function'&&auctionHasPresidentRole()}catch{}
      let label='CODA';try{label=auctionOwnCallTurn()&&auctionQueueRows().length===0?'CHIAMA':'CODA'}catch{}
      return `<section class="auction-suggested-calls" aria-label="Consulente Strategico"><div class="auction-suggested-head"><div><strong>Consulente Strategico</strong><small>IDX matematico · PMA mercato · scarsità · concorrenza</small></div><span>LIVE</span></div><div class="auction-suggested-list">${items.map((x,i)=>`<div class="auction-suggested-row ${i===0?'is-must-have':''}"><span class="auction-suggested-roles">${roles34(x.p).map(r=>`<span class="rolebadge" data-role="${esc34(r)}">${esc34(r)}</span>`).join('')}</span><div class="auction-suggested-copy"><div class="v8n"><strong>${esc34(x.p.name||'Giocatore')}</strong></div><small>${esc34(x.p.serie_a_team||'—')} · IDX ${Math.round(x.idx)} · PMA ${num(x.p.pma)!=null?Math.round(Number(x.p.pma)):'—'}</small></div><span class="v34-suggest-metrics"><span class="v34-suggest-metric ud ${x.ud>.5?'pos':x.ud<-.5?'neg':'zero'}"><small>UD</small><b>${x.ud>0?'+':''}${x.ud.toFixed(1).replace('.',',')}</b></span><span class="v34-suggest-metric"><small>O</small><b>${x.o}</b></span><span class="v34-suggest-metric"><small>MAX</small><b>${x.mx}</b></span></span><span class="auction-v7-suggest-actions"><button type="button" class="auction-v7-dismiss" data-v8-hide="${esc34(x.p.id)}" title="Nascondi per ora">×</button>${can?`<button type="button" class="auction-suggested-action" data-suggest-call="${esc34(x.p.id)}">${label}</button>`:'<span class="auction-suggested-action-placeholder">VICE</span>'}</span></div>`).join('')}</div></section>`;
    };
  }

  function patchAll34(){
    document.body.classList.toggle('v34-manual-flow',manual34());
    console34();injectQueueCalls34();patchSuggested34();
    const lp=state.list?.players||[],ap=state.auction?.callCandidates||[];
    paintDeal34(qs('#list-body'),lp);paintDeal34(qs('#auction-player-body'),ap);
    const lt=qs('#view-list table');if(lt){if(lt.dataset.v34UdReady!=='1')addUdColumn34(lt,lp,'list');sortUd34('list')}
    const at=qs('#view-auction .auction-free-table');if(at){if(at.dataset.v34UdReady!=='1')addUdColumn34(at,ap,'auction');sortUd34('auction')}
  }

  document.addEventListener('click',e=>{
    const sort=e.target.closest?.('[data-v34-ud-sort]');if(sort){e.preventDefault();const k=sort.dataset.v34UdSort;state.v34UdSort[k]=state.v34UdSort[k]===-1?1:-1;sortUd34(k);return}
    const q=e.target.closest?.('[data-v34-queue-call]');if(q){e.preventDefault();e.stopImmediatePropagation();void callQueue34(q.dataset.v34QueueCall,q);return}
    const summary=e.target.closest?.('#auctioneer-console-drawer>summary');if(summary){const d=summary.parentElement;if(session34()?.prestart_hold===true)return;e.preventDefault();e.stopImmediatePropagation();state.v34AuctioneerOpen=!d.open;state.auctionAdminConsoleOpen=state.v34AuctioneerOpen;d.open=state.v34AuctioneerOpen;return}
  },true);

  const obs=new MutationObserver(()=>requestAnimationFrame(patchAll34));
  obs.observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('resize',patchAll34,{passive:true});
  window.addEventListener('hashchange',()=>{setTimeout(()=>{patchAll34();void loadMarket34()},0)});
  document.addEventListener('DOMContentLoaded',()=>{patchAll34();void loadMarket34(true)},{once:true});
  setInterval(()=>{if(state.view==='auction'&&session34()?.status==='live')void loadMarket34();},5000);
  setTimeout(()=>{patchAll34();void loadMarket34(true)},0);
})();
</script>
'''

text=text.replace('</head>',style+'\n</head>',1)
text=text.replace('</body>',runtime+'\n</body>',1)

assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text
assert 'v34-market-strategy-runtime' in text
p.write_text(text,encoding='utf-8')
print('V34 market strategy UI applied')
