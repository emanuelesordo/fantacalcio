from pathlib import Path
import re

p = Path('home.html')
s = p.read_text(encoding='utf-8')

if 'v11-flow-score-listone-runtime' in s:
    raise SystemExit('V11 already applied')

# -----------------------------------------------------------------------------
# 1) Auction flow: structural mutations must cause a full, authoritative reload.
#    Hot-state only is fine for bids/timer ticks, but not for lifecycle changes.
# -----------------------------------------------------------------------------
old_rx = "/AWARD|ASSIGN|ROSTER|QUEUE|ROLE_PHASE|NOMINATION|CALL|UNDO|CREDIT|PASS|VICE/i"
new_rx = "/AWARD|ASSIGN|ROSTER|QUEUE|ROLE_PHASE|NOMINATION|CALL|UNDO|CREDIT|PASS|VICE|RESET|START|PREPARE|FINISH|CANCEL|PAUSE|READY|DONE|TEAM_ORDER|ABANDON/i"
if old_rx not in s:
    raise SystemExit('Realtime structural regex not found')
s = s.replace(old_rx, new_rx, 1)

old_structural = """      if (structural) {
        await originalLoadAuction({ quiet: true, onlyIfChanged: true });
        await v7SyncCatalog();
        return;
      }"""
new_structural = """      if (structural) {
        /* Structural events change the shape of the whole auction view.
           Always reload the canonical auction payload; a hot patch is not enough. */
        await loadAuction({ quiet: true, onlyIfChanged: false });
        await v7SyncCatalog();
        return;
      }"""
if old_structural not in s:
    raise SystemExit('Realtime structural branch not found')
s = s.replace(old_structural, new_structural, 1)

old_actions_tail = """          'resetAuction',
          'cancelCall',
          'passNominationTurn',
          'advanceRolePhase',
          'finishAuction'
        ]);"""
new_actions_tail = """          'resetAuction',
          'cancelCall',
          'passNominationTurn',
          'advanceRolePhase',
          'finishAuction',
          'confirmRoleReady',
          'undoLastBid'
        ]);"""
if old_actions_tail not in s:
    raise SystemExit('auctionAction structuralActions tail not found')
s = s.replace(old_actions_tail, new_actions_tail, 1)

old_action_refresh = """        if (structuralActions.has(payload?.action)) {
          state.auctionPersonalRosterFetchedAt = 0;
          scheduleAuctionReconcile(80);
        } else if (!auctionRealtimeSubscribed) {
          scheduleAuctionReconcile(2500);
        }"""
new_action_refresh = """        if (structuralActions.has(payload?.action)) {
          state.auctionPersonalRosterFetchedAt = 0;
          if (typeof window.v11ScheduleAuctionRefresh === 'function') {
            window.v11ScheduleAuctionRefresh(payload?.action || 'auctionAction', 45);
          } else {
            scheduleAuctionReconcile(80);
          }
        } else if (!auctionRealtimeSubscribed) {
          scheduleAuctionReconcile(2500);
        }"""
if old_action_refresh not in s:
    raise SystemExit('auctionAction refresh block not found')
s = s.replace(old_action_refresh, new_action_refresh, 1)

# -----------------------------------------------------------------------------
# 2) Theoretical roster: fantasy forecast must not fall back to prices.
# -----------------------------------------------------------------------------
old_forecast = "const forecast=p=>n(feature(p).forecast_fantasy_avg)??n(p?.expected_fantasy_avg)??n(p?.pfc)??n(p?.pma)??n(p?.quotation)??0;"
new_forecast = """const forecast=p=>{
    const direct=n(feature(p).forecast_fantasy_avg)??n(p?.expected_fantasy_avg);
    if(direct!=null&&direct>0&&direct<20)return direct;
    /* PMA/PFC are prices, never fantasy points. If the imported FV is absent,
       use a conservative football estimate driven only by slot/quotation. */
    const sl=clamp(n(p?.slot)??4,1,8),q=Math.max(0,n(p?.quotation)??0);
    return clamp(5.35+(5-sl)*.11+Math.min(.30,Math.log1p(q)*.035),5.15,6.45);
  };"""
if old_forecast not in s:
    raise SystemExit('forecast definition not found')
s = s.replace(old_forecast, new_forecast, 1)

# -----------------------------------------------------------------------------
# 3) Replace the greedy Mantra module picker with an expected-points optimiser.
#    Budget is a constraint, not a value divisor: cheap mediocre players should
#    not beat a better XI just because they are cheap.
# -----------------------------------------------------------------------------
new_choose = r'''  function v11StarterQuality(p,includeFav){
    const fv=Math.max(0,Number(forecast(p)||0));
    const pr=clamp(Number(presence(p)||0),0,100);
    const rk=clamp(Number(risk(p)||0),0,1);
    const tr=clamp(Number(trend(p)||0),-1,1);
    const pf=pref(p);
    const favBoost=includeFav&&(pf?.is_favorite||pf?.strategy==='top')?.035:0;
    /* FV dominates. Presence, risk and trend are tie-breakers, not substitutes. */
    return fv+(pr-65)*.0025-rk*.07+tr*.045+favBoost;
  }

  function v11SlotCandidates(players,slot,includeFav){
    const raw=players.filter(p=>compatible(p,slot)).map(p=>{
      const pr=Math.max(1,Math.round(basePrice(p)));
      const quality=v11StarterQuality(p,includeFav);
      return {p,pr,quality,raw:Math.max(0,Number(forecast(p)||0))};
    });
    const premium=[...raw].sort((a,b)=>b.quality-a.quality||a.pr-b.pr).slice(0,14);
    const value=[...raw].sort((a,b)=>(b.quality/Math.pow(b.pr,.16))-(a.quality/Math.pow(a.pr,.16))).slice(0,8);
    const cheap=[...raw].sort((a,b)=>a.pr-b.pr||b.quality-a.quality).slice(0,6);
    const uniq=new Map();
    [...premium,...value,...cheap].forEach(x=>uniq.set(String(x.p.id),x));
    return [...uniq.values()];
  }

  function v11OptimiseSlots(players,slots,budget,includeFav){
    const hard=Math.max(slots.length,Math.floor(Number(budget)||0));
    const lists=slots.map(slot=>v11SlotCandidates(players,slot,includeFav));
    if(lists.some(x=>!x.length))return null;
    const order=[...slots.keys()].sort((a,b)=>lists[a].length-lists[b].length);
    let beam=[{score:0,raw:0,spent:0,used:new Set(),line:Array(slots.length).fill(null)}];
    const width=150;
    for(let step=0;step<order.length;step++){
      const idx=order[step],next=[],remaining=order.length-step-1;
      for(const st of beam){
        for(const c of lists[idx]){
          const id=String(c.p.id);
          if(st.used.has(id))continue;
          if(st.spent+c.pr+remaining>hard)continue;
          const used=new Set(st.used);used.add(id);
          const line=st.line.slice();line[idx]=c;
          next.push({score:st.score+c.quality,raw:st.raw+c.raw,spent:st.spent+c.pr,used,line});
        }
      }
      if(!next.length)return null;
      next.sort((a,b)=>b.score-a.score||b.raw-a.raw||a.spent-b.spent);
      const seen=new Set(),trim=[];
      for(const st of next){
        const sig=st.line.map(x=>x?String(x.p.id):'').join('|');
        if(seen.has(sig))continue;
        seen.add(sig);trim.push(st);
        if(trim.length>=width)break;
      }
      beam=trim;
    }
    return beam[0]||null;
  }

  function chooseModule(players,budget,includeFav){
    let best=null;
    for(const id of moduleSlots()){
      const slots=MODS[id];
      const opt=v11OptimiseSlots(players,slots,budget,includeFav);
      if(!opt)continue;
      const line=opt.line.map((x,i)=>({p:x.p,pr:x.pr,slot:slots[i].join('/')}));
      const rank=opt.raw*100+opt.score;
      if(!best||rank>best.rank){
        best={id,line,spent:opt.spent,value:opt.raw,rank,used:new Set(line.map(x=>x.p.id))};
      }
    }
    return best;
  }
'''
pat_choose = re.compile(r"  function chooseModule\(players,budget,includeFav\)\{.*?\n  \}\n\n  function v9BestRosterCacheKey\(\)\{", re.S)
m = pat_choose.search(s)
if not m:
    raise SystemExit('chooseModule block not found')
s = s[:m.start()] + new_choose + "\n  function v9BestRosterCacheKey(){" + s[m.end():]

# -----------------------------------------------------------------------------
# 4) Rebuild best roster reasoning for both Classic and Mantra.
#    - maximise expected XI points first;
#    - keep enough budget for a complete bench;
#    - 60% starter budget is no longer a hard ceiling;
#    - retry up to 90% if the benchmark is not reached.
# -----------------------------------------------------------------------------
new_build = r'''  function v11ClassicFormationSlots(name){
    const [d,c,a]=name.split('-').map(Number);
    return [['Por'],...Array.from({length:d},()=>['D']),...Array.from({length:c},()=>['C']),...Array.from({length:a},()=>['A'])];
  }

  function v11StarterBudgetCaps(credits,totalCount){
    const benchCount=Math.max(0,totalCount-11);
    const absolute=Math.max(11,Math.min(credits-benchCount,Math.round(credits*.90)));
    const configured=clamp(Number(state.v8Profile?.starter_budget_percent||60),40,90);
    const first=Math.min(absolute,Math.max(Math.round(credits*.82),Math.round(credits*configured/100)));
    return [...new Set([first,absolute])].filter(x=>x>=11).sort((a,b)=>a-b);
  }

  function v11FillClassicBench(all,starters,cfg,credits){
    const used=new Set(starters.map(x=>String(x.p.id)));
    const picked=[],starterCounts={P:0,D:0,C:0,A:0};
    starters.forEach(x=>{const r=x.p.classic_role;if(starterCounts[r]!=null)starterCounts[r]++});
    let spent=starters.reduce((sum,x)=>sum+x.pr,0);
    let remainingSlots=['P','D','C','A'].reduce((sum,r)=>sum+Math.max(0,Number(cfg[r]||0)-starterCounts[r]),0);
    for(const role of ['P','D','C','A']){
      const need=Math.max(0,Number(cfg[role]||0)-starterCounts[role]);
      for(let i=0;i<need;i++){
        const pool=all.filter(p=>p.classic_role===role&&!used.has(String(p.id))).map(p=>{
          const pr=Math.max(1,Math.round(basePrice(p))),flex=1;
          const val=(scoreValue(p)+forecast(p)*.45+presence(p)/180+flex*.05)/Math.pow(pr,.20);
          return {p,pr,val};
        }).sort((a,b)=>b.val-a.val||a.pr-b.pr);
        const reserve=Math.max(0,remainingSlots-1);
        let pick=pool.find(x=>spent+x.pr+reserve<=credits);
        if(!pick)pick=[...pool].sort((a,b)=>a.pr-b.pr||b.val-a.val)[0];
        if(!pick)break;
        used.add(String(pick.p.id));picked.push({...pick,starter:false,group:role});spent+=pick.pr;remainingSlots--;
      }
    }
    return {picked,spent};
  }

  function v11FillMantraBench(all,starters,targetCount,credits){
    const used=new Set(starters.map(x=>String(x.p.id)));
    const picked=[];let spent=starters.reduce((sum,x)=>sum+x.pr,0);
    let remainingSlots=Math.max(0,targetCount-starters.length);
    while(remainingSlots>0){
      const pool=all.filter(p=>!used.has(String(p.id))).map(p=>{
        const pr=Math.max(1,Math.round(basePrice(p))),flex=Math.min(3,new Set(roles(p)).size);
        const val=(scoreValue(p)+forecast(p)*.45+flex*.30+presence(p)/220)/Math.pow(pr,.20);
        return {p,pr,val,flex};
      }).sort((a,b)=>b.val-a.val||a.pr-b.pr);
      const reserve=Math.max(0,remainingSlots-1);
      let pick=pool.find(x=>spent+x.pr+reserve<=credits);
      if(!pick)pick=[...pool].sort((a,b)=>a.pr-b.pr||b.val-a.val)[0];
      if(!pick)break;
      used.add(String(pick.p.id));picked.push({...pick,starter:false,group:roles(pick.p).join('/')});spent+=pick.pr;remainingSlots--;
    }
    return {picked,spent};
  }

  function buildBestRoster(){
    const cacheKey=v9BestRosterCacheKey();
    if(state.v9BestRosterCacheKey===cacheKey&&state.v9BestRosterCache)return state.v9BestRosterCache;
    const all=(state.v9Center?.players||state.list?.players||[]).filter(p=>p.status==='available'||!p.status);
    const credits=Math.max(1,Number(state.auction?.settings?.initial_credits||state.setup?.initial_credits||500));
    const includeFav=state.v9BestIncludeFav;
    const targetPoints=Math.max(66,Number(targetAverage()||66));

    if(mode()==='classic'){
      let cfg={P:3,D:8,C:8,A:6};
      try{const c=parseRosterConfig(state.auction?.settings?.roster_config||state.setup?.roster_config);cfg={...cfg,...(c?.classic||{})}}catch{}
      const totalCount=['P','D','C','A'].reduce((sum,r)=>sum+Math.max(0,Number(cfg[r]||0)),0);
      const formations=['3-4-3','3-5-2','4-3-3','4-4-2','4-5-1','5-3-2'].filter(id=>{
        const [d,c,a]=id.split('-').map(Number);return d<=Number(cfg.D||0)&&c<=Number(cfg.C||0)&&a<=Number(cfg.A||0);
      });
      let bestStart=null;
      for(const cap of v11StarterBudgetCaps(credits,totalCount)){
        let capBest=null;
        for(const id of formations){
          const slots=v11ClassicFormationSlots(id),opt=v11OptimiseSlots(all,slots,cap,includeFav);
          if(!opt)continue;
          const d=Number(id.split('-')[0]),modBonus=state.v9Rules?.defense_rule_enabled&&d>=4?.16:0;
          const rank=opt.raw+modBonus;
          if(!capBest||rank>capBest.rank)capBest={id,opt,rank};
        }
        if(capBest&&(!bestStart||capBest.opt.raw>bestStart.opt.raw))bestStart=capBest;
        if(capBest?.opt?.raw>=targetPoints-.25)break;
      }
      const starter=(bestStart?.opt?.line||[]).filter(Boolean).map((x,i)=>({p:x.p,pr:x.pr,starter:true,group:bestStart?.id?['POR',...v11ClassicFormationSlots(bestStart.id).slice(1).map(z=>z[0])][i]:'',val:x.quality}));
      const bench=v11FillClassicBench(all,starter,cfg,credits);
      const starterSpent=starter.reduce((sum,x)=>sum+x.pr,0);
      const result={mode:'classic',module:bestStart?.id||'—',players:[...starter,...bench.picked],spent:bench.spent,budget:credits,starterBudget:starterSpent,expectedPoints:starter.reduce((sum,x)=>sum+forecast(x.p),0),targetPoints};
      state.v9BestRosterCacheKey=cacheKey;state.v9BestRosterCache=result;return result;
    }

    let targetCount=25;
    try{
      const raw=state.auction?.settings?.roster_config||state.setup?.roster_config;
      const cfg=typeof parseRosterConfig==='function'?parseRosterConfig(raw):raw;
      targetCount=Math.max(11,Number(cfg?.mantra?.total?.max||cfg?.mantra?.total?.min||cfg?.mantra?.max||targetCount));
    }catch{}
    let first=null;
    for(const cap of v11StarterBudgetCaps(credits,targetCount)){
      const candidate=chooseModule(all,cap,includeFav);
      if(candidate&&(!first||candidate.value>first.value))first=candidate;
      if(candidate?.value>=targetPoints-.25)break;
    }
    const starters=(first?.line||[]).map(x=>({...x,starter:true,group:x.slot}));
    const bench=v11FillMantraBench(all,starters,targetCount,credits);
    const starterSpent=starters.reduce((sum,x)=>sum+x.pr,0);
    const result={mode:'mantra',module:first?.id||'—',players:[...starters,...bench.picked],spent:bench.spent,budget:credits,starterBudget:starterSpent,expectedPoints:starters.reduce((sum,x)=>sum+forecast(x.p),0),targetPoints};
    state.v9BestRosterCacheKey=cacheKey;state.v9BestRosterCache=result;return result;
  }
'''
pat_build = re.compile(r"  function buildBestRoster\(\)\{.*?\n  \}\n\n  function barRows\(dist,credits\)\{", re.S)
m = pat_build.search(s)
if not m:
    raise SystemExit('buildBestRoster block not found')
s = s[:m.start()] + new_build + "\n  function barRows(dist,credits){" + s[m.end():]

# -----------------------------------------------------------------------------
# 5) Re-render statistics with explicit expected XI points, not a misleading
#    'fantamedia target' label, and make calculated-roster rows readable.
# -----------------------------------------------------------------------------
new_render_stats = r'''  function renderStats(){
    const host=document.querySelector('.v9-pane-stats');if(!host)return;
    const credits=Number(state.auction?.settings?.initial_credits||state.setup?.initial_credits||500),mantra=mode()==='mantra',dist=classicBudget(),best=buildBestRoster();
    const starter=best.players.filter(x=>x.starter),bench=best.players.filter(x=>!x.starter);
    const expectedPoints=Number(best.expectedPoints??starter.reduce((sum,x)=>sum+forecast(x.p),0));
    const targetPoints=Number(best.targetPoints??targetAverage());
    const pointBand=expectedPoints>=targetPoints?'good':expectedPoints>=66?'warn':'danger';
    host.innerHTML=`<div class="v9scroll">
      <section class="v9card"><div class="between"><div><strong>Statistiche vittoria</strong><small class="soft">benchmark forniti · lega a 10</small></div><span class="badge">${mantra?'MANTRA ADATTATO':'CLASSIC'}</span></div><div class="v9kpi"><span><small>Punti squadra target</small><b>${targetPoints.toFixed(1)}</b></span><span><small>Gare ≥72</small><b>${BENCH.rule72.winner}/38</b></span><span><small>Gol target</small><b>${BENCH.bonus.goals}</b></span><span><small>Assist target</small><b>${BENCH.bonus.assists}</b></span></div>${mantra?'<small class="soft">Il benchmark Mantra è adattato dal campione Classic; il totale XI è la somma delle FV previste dei titolari.</small>':''}</section>
      <section class="v9card"><strong>${mantra?'Distribuzione strategica':'Budget dei vincitori'}</strong>${mantra?`<div class="v9bar"><b>TIT</b><span><i style="width:${Number(state.v8Profile?.starter_budget_percent||60)}%"></i></span><em>target morbido ${Number(state.v8Profile?.starter_budget_percent||60)}%</em></div><small class="soft">Il target titolari orienta la strategia ma non blocca la rosa teorica: se l’XI non è competitivo l’ottimizzatore può salire fino al 90%, mantenendo budget per completare la panchina.</small>`:barRows(dist,credits)}</section>
      ${!mantra?`<section class="v9card"><strong>Prezzo medio slot per slot</strong><div class="v9card-scroll">${Object.entries(BENCH.slotModClean).map(([r,a])=>`<div class="v9slotgroup"><b>${r}</b>${a.map((v,i)=>`<span>Slot ${i+1}<em>${pct(v)} · ${Math.round(credits*v/100)} cr</em></span>`).join('')}</div>`).join('')}</div></section>`:''}
      <section class="v9card"><strong>Indicatori di squadra</strong><div class="v9statsgrid"><span>Gol reparto A / offensivi<b>${BENCH.goals.A}</b></span><span>Gol C / centrali<b>${BENCH.goals.C}</b></span><span>Gol D / difensivi<b>${BENCH.goals.D}</b></span><span>Imbattibilità portiere<b>${BENCH.bonus.cleanSheets}</b></span><span>Cartellini G/R<b>${BENCH.bonus.yellow}/${BENCH.bonus.red}</b></span><span>Gol lasciati in panchina<b>${BENCH.bonus.benchGoals}</b></span></div></section>
      <section class="v9card"><div class="between"><div><strong>Miglior rosa teorica</strong><small class="soft">XI ottimizzato sui punti attesi; presenza/rischio come correttivi, prezzo come vincolo, poi profondità panchina</small></div><label class="v9switch"><input id="v9-best-fav" type="checkbox" ${state.v9BestIncludeFav?'checked':''}> integra preferiti</label></div><div class="v9besthead"><span>${best.module}</span><b>${Math.round(best.spent)}/${best.budget} cr</b><em>titolari ${Math.round(best.starterBudget||0)} cr</em><strong class="v11-xi-points ${pointBand}">XI ${expectedPoints.toFixed(1)} pt</strong><em>target ${targetPoints.toFixed(1)}</em></div><div class="v9bestcols"><div><strong>Titolari</strong><div class="v9card-scroll">${starter.map(x=>`<span><b>${esc(x.p.name)}</b><small>${esc(x.group||'')} · ${x.pr} cr · FV ${forecast(x.p).toFixed(2)}</small></span>`).join('')}</div></div><div><strong>Ricambi</strong><div class="v9card-scroll">${bench.map(x=>`<span><b>${esc(x.p.name)}</b><small>${esc(x.group||'')} · ${x.pr} cr · FV ${forecast(x.p).toFixed(2)}</small></span>`).join('')}</div></div></div></section>
    </div>`;
    host.querySelector('#v9-best-fav')?.addEventListener('change',async e=>{state.v9BestIncludeFav=e.target.checked;state.v9BestRosterCacheKey='';state.v9BestRosterCache=null;const res=await api(ENDPOINTS.strategy,{action:'saveProfile',preferredModules:state.v8Profile?.preferred_modules||[],profile:state.v8Profile?.profile||'balanced',roleBudgets:state.v8Profile?.role_budgets||{},notes:state.v8Profile?.notes||'',starterBudgetPercent:Number(state.v8Profile?.starter_budget_percent||60),includeFavoritesInBestRosters:state.v9BestIncludeFav},{quiet:true});if(res?.profile){state.v8Profile=res.profile;state.v9Center.profile=res.profile}renderStats();});
  }
'''
pat_stats = re.compile(r"  function renderStats\(\)\{.*?\n  \}\n\n  function activateTab\(name\)\{", re.S)
m = pat_stats.search(s)
if not m:
    raise SystemExit('renderStats block not found')
s = s[:m.start()] + new_render_stats + "\n  function activateTab(name){" + s[m.end():]

# -----------------------------------------------------------------------------
# 6) Runtime: catch direct auction API mutations that bypass auctionAction and
#    debounce a full view refresh. Also alias Listone visuals to the auction card.
# -----------------------------------------------------------------------------
runtime = r'''
<script id="v11-flow-score-listone-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V11_FLOW_SCORE_LISTONE__)return;
  window.__FANTA_V11_FLOW_SCORE_LISTONE__=1;

  let refreshTimer=null,refreshBusy=false,refreshAgain=false;
  window.v11ScheduleAuctionRefresh=function(reason='mutation',delay=55){
    if(refreshTimer)clearTimeout(refreshTimer);
    refreshTimer=setTimeout(async()=>{
      refreshTimer=null;
      if(!state.session?.token||!state.selectedLeague?.id||state.view!=='auction')return;
      if(refreshBusy){refreshAgain=true;return;}
      refreshBusy=true;
      try{
        await loadAuction({quiet:true,onlyIfChanged:false});
      }catch(error){
        console.warn('Auction full refresh',reason,error);
      }finally{
        refreshBusy=false;
        if(refreshAgain){refreshAgain=false;window.v11ScheduleAuctionRefresh('coalesced',70);}
      }
    },Math.max(0,Number(delay)||0));
  };

  const oldApiV11=api;
  const lifecycle=new Set([
    'createAuction','prepareAuction','cancelPreparedAuction','saveTeamOrder','startAuction',
    'callPlayer','awardPlayer','manualAward','editRosterPrice','removeRosterPlayer',
    'transferRosterPlayer','undoLastAssignment','undoOperation','undoLastBid','resetAuction',
    'cancelCall','passNominationTurn','advanceRolePhase','finishAuction','confirmRoleReady',
    'setTeamCredits','abandonTurn'
  ]);
  const structuralAction=action=>lifecycle.has(action)||/(Queue|Roster|TeamOrder|TeamCredits|RoleReady)/i.test(action);
  api=async function(endpoint,payload={},options={}){
    const response=await oldApiV11(endpoint,payload,options);
    const action=String(payload?.action||'');
    if(endpoint===ENDPOINTS.auction&&structuralAction(action)){
      window.v11ScheduleAuctionRefresh(action,55);
    }
    return response;
  };

  const style=document.createElement('style');
  style.id='v11-flow-score-listone-style';
  style.textContent=`
    /* Calculated roster: stop rendering 5–6px rows. */
    #view-strategy .v9bestcols .v9card-scroll>span,
    #view-auction .v9-pane-stats .v9bestcols .v9card-scroll>span{
      min-height:36px!important;
      padding:6px 7px!important;
      display:flex!important;
      flex-direction:column!important;
      justify-content:center!important;
      gap:2px!important;
    }
    #view-strategy .v9bestcols b,
    #view-auction .v9-pane-stats .v9bestcols b{font-size:9px!important;line-height:1.12!important}
    #view-strategy .v9bestcols small,
    #view-auction .v9-pane-stats .v9bestcols small{font-size:7px!important;line-height:1.15!important}
    .v11-xi-points{font-size:9px!important;font-weight:1000!important;padding:2px 6px;border-radius:99px;border:1px solid currentColor}
    .v11-xi-points.good{color:#74e3b7}.v11-xi-points.warn{color:#f1c861}.v11-xi-points.danger{color:#ff8fa6}

    /* LISTONE page = same visual language and columns as the auction free-agents card.
       Only the last action cell differs: it contains the private heart. */
    body.modern-glass #view-list .panel,
    body.modern-glass #view-list .table-wrap{
      border-color:var(--line)!important;
      background:linear-gradient(145deg,rgba(255,255,255,.055),rgba(255,255,255,.018))!important;
      box-shadow:inset 0 1px rgba(255,255,255,.045),0 18px 50px rgba(0,0,0,.18)!important;
    }
    body.modern-glass #view-list .table-wrap{border-radius:9px!important;overflow:auto!important}
    body.modern-glass #view-list .player-table{
      width:100%!important;min-width:0!important;max-width:100%!important;
      table-layout:fixed!important;border-spacing:0!important;
    }
    body.modern-glass #view-list .player-table thead tr{height:28px!important}
    body.modern-glass #view-list .player-table thead th{
      height:28px!important;min-height:28px!important;padding:0 2px!important;vertical-align:middle!important;
      background:rgba(13,43,70,.98)!important;border-bottom:1px solid rgba(69,117,163,.54)!important;
      font-size:5.8px!important;letter-spacing:.025em!important;line-height:1!important;
    }
    body.modern-glass #view-list .player-table thead th>button{
      width:100%!important;height:100%!important;min-height:0!important;margin:0!important;padding:0!important;
      border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;
      color:var(--soft)!important;font-size:5.8px!important;line-height:1!important;
    }
    body.modern-glass #view-list .player-table tbody tr{
      background:linear-gradient(145deg,rgba(34,64,96,.20),rgba(13,32,54,.14))!important;
    }
    body.modern-glass #view-list .player-table tbody tr:hover{
      background:linear-gradient(145deg,rgba(48,88,128,.40),rgba(18,43,70,.34))!important;
    }
    body.modern-glass #view-list .player-table td{
      height:30px!important;min-width:0!important;padding:3px 2px!important;overflow:hidden!important;text-overflow:ellipsis!important;
      border-bottom:1px solid rgba(69,117,163,.26)!important;
    }
    body.modern-glass #view-list .auction-player-col-role{width:54px!important;min-width:54px!important;max-width:54px!important;padding-inline:1px!important}
    body.modern-glass #view-list .auction-player-col-role .rolebadge{min-width:16px!important;width:auto!important;height:16px!important;padding-inline:2px!important;margin-right:1px!important;font-size:5.4px!important}
    body.modern-glass #view-list .auction-player-col-name{width:auto!important;min-width:0!important;max-width:none!important;padding-inline:3px!important}
    body.modern-glass #view-list .auction-player-col-name .player-name{font-size:7.6px!important;line-height:1.05!important;font-weight:900!important;letter-spacing:.01em!important}
    body.modern-glass #view-list .auction-player-team-small{margin-top:1px!important;font-size:5.1px!important;line-height:1!important}
    body.modern-glass #view-list .auction-player-col-signals{width:32px!important;min-width:32px!important;max-width:32px!important;padding-inline:1px!important;text-align:center!important}
    body.modern-glass #view-list .auction-player-col-pfc,
    body.modern-glass #view-list .auction-player-col-pma{width:34px!important;min-width:34px!important;max-width:34px!important;padding-inline:1px!important;text-align:right!important;font-variant-numeric:tabular-nums!important}
    body.modern-glass #view-list .auction-player-col-fm{width:36px!important;min-width:36px!important;max-width:36px!important;padding-inline:1px!important;text-align:right!important;color:#b9d7f2!important}
    body.modern-glass #view-list .auction-player-col-supreme{width:35px!important;min-width:35px!important;max-width:35px!important;padding-inline:1px!important;text-align:center!important}
    body.modern-glass #view-list .auction-player-col-action{width:42px!important;min-width:42px!important;max-width:42px!important;padding-inline:1px!important;text-align:center!important}
    body.modern-glass #view-list .auction-signal-list{gap:1px!important}
    body.modern-glass #view-list .auction-signal-badge{width:13px!important;height:13px!important;font-size:7px!important}
    body.modern-glass #view-list .list-fav-slot{width:100%;height:100%;display:flex!important;align-items:center!important;justify-content:center!important}
    body.modern-glass #view-list .v8heart{width:26px!important;min-width:26px!important;height:26px!important;min-height:26px!important;font-size:17px!important;margin:0!important}
    body.modern-glass #view-list .rolebar .rolebtn{
      border-color:rgba(91,151,216,.24)!important;background:rgba(21,55,88,.72)!important;
    }
    body.modern-glass #view-list .rolebar .rolebtn.active{background:var(--primary)!important;border-color:var(--primary)!important}
  `;
  document.head.appendChild(style);
})();
</script>
'''
if '</body>' not in s:
    raise SystemExit('body close not found')
s = s.replace('</body>', runtime + '\n</body>', 1)

p.write_text(s, encoding='utf-8')
print('V11 patch applied')
