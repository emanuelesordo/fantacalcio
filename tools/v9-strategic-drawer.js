/* FANTACALCIO LIVE · V9 strategic drawer + benchmarks */
'use strict';
(()=>{
  if(window.__FANTA_V9_DRAWER__) return;
  window.__FANTA_V9_DRAWER__=1;

  ENDPOINTS.strategy=ENDPOINTS.strategy||`${SUPABASE_URL}/functions/v1/strategy-api`;
  ENDPOINTS.scoring=`${SUPABASE_URL}/functions/v1/scoring-api`;

  const MODS=state.v8Modules||{
    '3-4-3':[['Por'],['Dc'],['Dc'],['Dc','B'],['E'],['M','C'],['C'],['E'],['W','A'],['W','A'],['A','Pc']],
    '3-4-1-2':[['Por'],['Dc'],['Dc'],['Dc','B'],['E'],['M','C'],['C'],['E'],['T'],['A','Pc'],['A','Pc']],
    '3-4-2-1':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['E'],['M','C'],['E','W'],['T'],['T','A'],['A','Pc']],
    '3-5-2':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['E'],['M','C'],['C'],['E','W'],['A','Pc'],['A','Pc']],
    '3-5-1-1':[['Por'],['Dc'],['Dc'],['Dc','B'],['M'],['M'],['C'],['E','W'],['E','W'],['T','A'],['A','Pc']],
    '4-3-3':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['M'],['C'],['W','A'],['W','A'],['A','Pc']],
    '4-3-1-2':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['M'],['C'],['T'],['T','A','Pc'],['A','Pc']],
    '4-4-2':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M','C'],['C'],['E','W'],['E'],['A','Pc'],['A','Pc']],
    '4-1-4-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['C','T'],['T'],['E','W'],['W'],['A','Pc']],
    '4-4-1-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['C'],['E','W'],['E','W'],['T','A'],['A','Pc']],
    '4-2-3-1':[['Por'],['Dd'],['Dc'],['Dc'],['Ds'],['M'],['M','C'],['W','T'],['T'],['W','A'],['A','Pc']]
  };

  const BENCH={
    budgetNoModClean:{P:9,D:14,C:29,A:48},
    budgetModClean:{P:9.3,D:16.5,C:28.3,A:46},
    slotModClean:{
      P:[7.0,1.0,.4],D:[5.8,3.6,2.2,1.4,1.0,.6,.4,.2],
      C:[12.2,6.2,3.4,2.0,1.2,.8,.4,.2],A:[24.6,11.4,5.8,3.0,1.4,.6]
    },
    avg:{none:71.1,clean:72.0,def:73.0,both:73.2,other:73.5},
    rule72:{winner:21,league:15,last:10},
    goals:{A:30,C:20,D:11},
    bonus:{goals:61,assists:38,cleanSheets:16,yellow:45,red:2,benchGoals:77}
  };

  Object.assign(state,{
    v9Rules:state.v9Rules||{defense_rule_enabled:false,defense_include_goalkeeper:true,clean_sheet_bonus_enabled:false,clean_sheet_bonus_value:1},
    v9Center:state.v9Center||null,
    v9LoadedLeague:state.v9LoadedLeague||'',
    v9BestIncludeFav:state.v9BestIncludeFav||false,
    v9ActiveDrawerTab:state.v9ActiveDrawerTab||'free'
  });

  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const n=v=>Number.isFinite(Number(v))?Number(v):null;
  const pct=v=>`${Number(v||0).toFixed(1).replace('.0','')}%`;
  const mode=()=>state.auction?.settings?.fantasy_mode||state.setup?.fantasy_mode||state.list?.settings?.fantasyMode||'classic';
  const roles=p=>playerRoles(p||{},mode()).map(r=>r==='P'?'Por':r);
  const feature=p=>p?.strategic_features||{};
  const favMap=()=>state.v7Preferences||new Map();
  const playerMap=()=>new Map((state.v9Center?.players||state.list?.players||state.auction?.callCandidates||[]).map(p=>[String(p.source_player_id||p.id),p]));
  const pref=p=>favMap().get(String(p?.source_player_id||p?.id||''))||null;
  const forecast=p=>n(feature(p).forecast_fantasy_avg)??n(p?.expected_fantasy_avg)??n(p?.pfc)??n(p?.pma)??n(p?.quotation)??0;
  const presence=p=>{let v=n(feature(p).forecast_presence)??n(p?.expected_titolarity)??60;if(v<=1)v*=100;return clamp(v,0,100)};
  const trend=p=>clamp(n(feature(p).trend_age_adjusted)??0,-1,1);
  const risk=p=>clamp(n(feature(p).volatility)??.25,0,1);
  const basePrice=p=>{
    const pfc=n(p?.pfc),pma=n(p?.pma),q=n(p?.quotation);
    const raw=(pfc!=null?pfc*.55:0)+(pma!=null?pma*.30:0)+(q!=null?q*.15:0);
    const denom=(pfc!=null?.55:0)+(pma!=null?.30:0)+(q!=null?.15:0);
    const ref=denom?raw/denom:(pfc??pma??q??1);
    return Math.max(1,Math.round(ref*(1+trend(p)*.12+(presence(p)-65)/700)));
  };
  const scoreValue=p=>forecast(p)*(.80+.20*presence(p)/100)*(1-risk(p)*.08)+(4-Math.min(4,Number(p?.slot||4)))*.15+trend(p)*.5;

  async function loadV9(force=false){
    const lid=state.selectedLeague?.id||'';
    if(!lid||(!force&&state.v9LoadedLeague===lid&&state.v9Center)) return;
    try{
      const [center,rules]=await Promise.all([
        api(ENDPOINTS.strategy,{action:'getStrategyCenter'},{quiet:true}),
        api(ENDPOINTS.scoring,{action:'getRules'},{quiet:true})
      ]);
      if(center){
        state.v9Center=center;
        state.v8Profile=center.profile||state.v8Profile||{};
        state.v9BestIncludeFav=state.v8Profile?.include_favorites_in_best_rosters===true;
        state.v7Preferences=new Map((center.preferences||[]).map(x=>[String(x.source_player_id),x]));
      }
      if(rules?.rules) state.v9Rules=rules.rules;
      state.v9LoadedLeague=lid;
    }catch(e){console.warn('V9 load',e)}
  }

  function softModuleBoost(p){
    if(mode()!=='mantra') return 0;
    const selected=(state.v8Profile?.preferred_modules||[]).filter(x=>MODS[x]);
    if(!selected.length) return 0;
    const rr=new Set(roles(p));
    let fit=0;
    selected.forEach(id=>{
      const slots=MODS[id]||[];
      const matches=slots.filter(slot=>slot.some(r=>rr.has(r))).length;
      fit=Math.max(fit,matches/Math.max(1,slots.length));
    });
    return fit>=.27?4:fit>=.18?2:fit>0?1:0;
  }

  const prevScore=auctionSuggestedCallScore;
  auctionSuggestedCallScore=function(p){
    const keep=state.v8Profile?.preferred_modules;
    if(state.v8Profile) state.v8Profile.preferred_modules=[];
    let x;
    try{x=prevScore(p)}finally{if(state.v8Profile) state.v8Profile.preferred_modules=keep||[];}
    if(!x) return x;
    const pf=pref(p), predicted=x.prices?.suggested??basePrice(p), cap=n(pf?.max_price);
    let favoriteBoost=0;
    if(pf?.is_favorite||pf?.strategy==='top'){
      if(cap==null) favoriteBoost=pf?.strategy==='top'?7:4;
      else if(predicted<=cap) favoriteBoost=pf?.strategy==='top'?9:6;
      else if(predicted<=cap*1.10) favoriteBoost=2;
      else favoriteBoost=-3;
    }
    x.score=clamp(Number(x.score||0)+softModuleBoost(p)+favoriteBoost,0,100);
    x.favoritePriceFit=cap==null?null:predicted/cap;
    return x;
  };

  function classicBudget(){
    const r=state.v9Rules||{};
    if(r.defense_rule_enabled&&r.clean_sheet_bonus_enabled) return BENCH.budgetModClean;
    if(!r.defense_rule_enabled&&r.clean_sheet_bonus_enabled) return BENCH.budgetNoModClean;
    if(r.defense_rule_enabled) return {P:8.7,D:16,C:28.6,A:46.7};
    return {P:8.5,D:14,C:29.5,A:48};
  }
  function targetAverage(){
    const r=state.v9Rules||{};
    let v=r.defense_rule_enabled?(r.clean_sheet_bonus_enabled?BENCH.avg.both:BENCH.avg.def):(r.clean_sheet_bonus_enabled?BENCH.avg.clean:BENCH.avg.none);
    if(mode()==='mantra') v-=.5;
    return v;
  }

  function moduleSlots(){
    const preferred=(state.v8Profile?.preferred_modules||[]).filter(x=>MODS[x]);
    return preferred.length?preferred:Object.keys(MODS);
  }
  function compatible(p,slot){const rr=new Set(roles(p));return slot.some(r=>rr.has(r));}

  function chooseModule(players,budget,includeFav){
    let best=null;
    for(const id of moduleSlots()){
      const slots=MODS[id],used=new Set(),line=[];let spent=0,total=0;
      for(const slot of slots){
        const cand=players.filter(p=>!used.has(p.id)&&compatible(p,slot)).map(p=>{
          const pr=basePrice(p),pf=pref(p),fb=includeFav&&(pf?.is_favorite||pf?.strategy==='top')?1.06:1;
          return {p,pr,val:scoreValue(p)*fb/Math.pow(Math.max(1,pr),.22)};
        }).sort((a,b)=>b.val-a.val);
        const pick=cand.find(c=>spent+c.pr<=budget)||cand[0];
        if(!pick) continue;
        used.add(pick.p.id);line.push({...pick,slot:slot.join('/')});spent+=pick.pr;total+=scoreValue(pick.p);
      }
      const value=line.length?total/line.length:0;
      const rank=line.length*100+value*10-spent/100;
      if(!best||rank>best.rank) best={id,line,spent,value,rank,used};
    }
    return best;
  }

  function buildBestRoster(){
    const all=(state.v9Center?.players||state.list?.players||[]).filter(p=>p.status==='available'||!p.status);
    const credits=Number(state.auction?.settings?.initial_credits||state.setup?.initial_credits||500);
    const includeFav=state.v9BestIncludeFav;
    if(mode()==='classic'){
      let cfg={P:3,D:8,C:8,A:6};
      try{const c=parseRosterConfig(state.auction?.settings?.roster_config||state.setup?.roster_config);cfg={...cfg,...(c?.classic||{})}}catch{}
      const dist=classicBudget(); const picked=[]; let spent=0;
      ['P','D','C','A'].forEach(role=>{
        const count=Math.max(0,Number(cfg[role]||0)),roleBudget=credits*(dist[role]||0)/100;
        const candidates=all.filter(p=>p.classic_role===role).map(p=>{
          const pr=basePrice(p),pf=pref(p),fb=includeFav&&(pf?.is_favorite||pf?.strategy==='top')?1.06:1;
          return {p,pr,val:scoreValue(p)*fb/Math.pow(Math.max(1,pr),.20)};
        }).sort((a,b)=>b.val-a.val);
        const selected=[];let rs=0;
        for(let i=0;i<count;i++){
          const starterCut=role==='P'?1:role==='D'?(state.v9Rules?.defense_rule_enabled?4:3):role==='C'?4:3;
          const starter=i<starterCut;
          const allowance=roleBudget*(starter?.76:.24);
          const pool=candidates.filter(c=>!selected.includes(c)&&(!starter||rs+c.pr<=roleBudget*.82));
          const pick=pool[0]||candidates.find(c=>!selected.includes(c));
          if(!pick) break;selected.push(pick);rs+=pick.pr;picked.push({...pick,group:role,starter});
        }
        spent+=rs;
      });
      return {mode:'classic',module:state.v9Rules?.defense_rule_enabled?'4-3-3/4-4-2':'3-4-3',players:picked,spent,budget:credits,starterBudget:null};
    }
    const starterPct=clamp(Number(state.v8Profile?.starter_budget_percent||60),40,80);
    const starterBudget=credits*starterPct/100;
    const first=chooseModule(all,starterBudget,includeFav);
    const used=first?.used||new Set(),remaining=all.filter(p=>!used.has(p.id));
    const targetCount=Math.max(23,Number(state.auction?.settings?.roster_config?.mantra?.total?.max||25));
    const benchBudget=Math.max(0,credits-(first?.spent||0));
    const bench=remaining.map(p=>{
      const pr=basePrice(p),flex=Math.min(3,new Set(roles(p)).size),pf=pref(p),fb=includeFav&&(pf?.is_favorite||pf?.strategy==='top')?1.05:1;
      return {p,pr,val:(scoreValue(p)+flex*.35)*fb/Math.pow(Math.max(1,pr),.24)};
    }).sort((a,b)=>b.val-a.val);
    const chosen=[];let bs=0;
    for(const c of bench){if((first?.line.length||0)+chosen.length>=targetCount)break;if(bs+c.pr>benchBudget&&chosen.length>=10)continue;chosen.push({...c,starter:false,group:roles(c.p).join('/')});bs+=c.pr;}
    const starters=(first?.line||[]).map(x=>({...x,starter:true,group:x.slot}));
    return {mode:'mantra',module:first?.id||'—',players:[...starters,...chosen],spent:(first?.spent||0)+bs,budget:credits,starterBudget};
  }

  function barRows(dist,credits){return Object.entries(dist).map(([k,v])=>`<div class="v9bar"><b>${k}</b><span><i style="width:${Math.min(100,Number(v))}%"></i></span><em>${pct(v)} · ${Math.round(credits*Number(v)/100)} cr</em></div>`).join('')}

  function renderFavorites(){
    const pmap=playerMap();
    const rows=[...favMap().values()].filter(x=>x.is_favorite||x.strategy==='top').map(x=>({x,p:pmap.get(String(x.source_player_id))})).filter(z=>z.p).sort((a,b)=>String(a.p.name).localeCompare(String(b.p.name),'it'));
    if(!rows.length) return '<div class="v9empty">Nessun preferito. Aggiungili dal Listone con il cuore.</div>';
    return rows.map(({x,p})=>{
      const predicted=auctionSuggestedCallScore(p)?.prices?.suggested??basePrice(p);
      return `<div class="v9fav" data-v9-source="${esc(x.source_player_id)}"><div><strong>${esc(p.name)}</strong><small>${esc(p.serie_a_team||'—')} · ${esc(playerRoles(p,mode()).join('/'))} · previsto ${predicted}</small></div><label>MAX<input type="number" min="1" data-v9-max value="${x.max_price??''}" placeholder="—"></label><button type="button" class="secondary" data-v9-remove title="Rimuovi dai preferiti">×</button></div>`;
    }).join('');
  }

  function renderStrategy(){
    const host=document.querySelector('.v9-pane-strategy');if(!host)return;
    const pr=state.v8Profile||{},mantra=mode()==='mantra',selected=new Set(pr.preferred_modules||[]);
    const top=(state.auction?.callCandidates||state.v9Center?.players||[]).filter(p=>p.status==='available'||!p.status).map(p=>auctionSuggestedCallScore(p)).filter(Boolean).sort((a,b)=>b.score-a.score).slice(0,5);
    host.innerHTML=`<div class="v9scroll"><section class="v9card"><div class="between"><div><strong>Centro Strategico</strong><small class="soft">configurazione privata pre-asta</small></div><span class="badge primary">PRIVATO</span></div><label>Profilo<select id="v9-profile"><option value="conservative">Conservativo</option><option value="balanced">Bilanciato</option><option value="aggressive">Aggressivo</option></select></label>${mantra?`<div class="v9block"><b>Moduli ideali</b><small>Nessuno = nessuna preferenza. Sono un boost morbido: non escludono alternative migliori.</small><div class="v9mods">${Object.keys(MODS).map(id=>`<label><input type="checkbox" data-v9-module="${id}" ${selected.has(id)?'checked':''}>${id}</label>`).join('')}</div></div><label>Budget indicativo titolari <b id="v9-starter-label">${Number(pr.starter_budget_percent||60)}%</b><input id="v9-starter" type="range" min="40" max="80" step="1" value="${Number(pr.starter_budget_percent||60)}"></label>`:`<div class="v9block"><b>Budget per ruolo</b><small>Classic: ripartizione esplicita P/D/C/A.</small><div class="v9budgets">${['P','D','C','A'].map(k=>`<label>${k}<input type="number" min="0" data-v9-budget="${k}" value="${pr.role_budgets?.[k]??''}" placeholder="cr"></label>`).join('')}</div></div>`}<label>Note<textarea id="v9-notes" rows="2">${esc(pr.notes||'')}</textarea></label><button type="button" id="v9-save">SALVA STRATEGIA</button></section><section class="v9card"><div class="between"><strong>Preferiti</strong><span class="badge">${[...favMap().values()].filter(x=>x.is_favorite||x.strategy==='top').length}</span></div><div class="v9card-scroll v9-favorites">${renderFavorites()}</div></section><section class="v9card"><div class="between"><strong>Top 5 suggerita</strong><small class="soft">preferiti residui e prezzo previsto inclusi nello score</small></div><div class="v9card-scroll">${top.length?top.map((x,i)=>`<div class="v9top ${i===0?'mom':''}"><b>${i+1}. ${esc(x.player?.name||'')}</b><span>S ${Math.round(x.score)}</span><span>${x.prices?.suggested??basePrice(x.player)}</span><span>${x.prices?.ceiling??'—'}</span></div>`).join(''):'<div class="v9empty">Catalogo non ancora disponibile.</div>'}</div></section></div>`;
    const prof=host.querySelector('#v9-profile');if(prof)prof.value=pr.profile||'balanced';
    const slider=host.querySelector('#v9-starter'),lab=host.querySelector('#v9-starter-label');slider?.addEventListener('input',()=>{if(lab)lab.textContent=`${slider.value}%`});
    host.querySelector('#v9-save')?.addEventListener('click',async()=>{
      const roleBudgets={};host.querySelectorAll('[data-v9-budget]').forEach(i=>{const v=n(i.value);if(v!=null&&v>=0)roleBudgets[i.dataset.v9Budget]=Math.round(v)});
      const res=await api(ENDPOINTS.strategy,{action:'saveProfile',preferredModules:[...host.querySelectorAll('[data-v9-module]:checked')].map(i=>i.dataset.v9Module),profile:prof?.value||'balanced',roleBudgets,notes:host.querySelector('#v9-notes')?.value||'',starterBudgetPercent:Number(slider?.value||60),includeFavoritesInBestRosters:state.v9BestIncludeFav},{quiet:true});
      if(res?.profile){state.v8Profile=res.profile;state.v9Center.profile=res.profile;msg('Strategia salvata.','success');renderStrategy();renderStats();}
    });
    host.querySelectorAll('.v9fav').forEach(row=>{
      const source=row.dataset.v9Source,inp=row.querySelector('[data-v9-max]');
      inp?.addEventListener('change',async()=>{const current=favMap().get(String(source));const res=await api(ENDPOINTS.v6y,{action:'savePreference',sourcePlayerId:source,isFavorite:true,strategy:current?.strategy||'favorite',priority:Number(current?.priority||0),maxPrice:inp.value,expectedSpend:current?.expected_spend??'',note:current?.note||''},{quiet:true});if(res?.preference)state.v7Preferences.set(String(source),res.preference);renderStrategy();});
      row.querySelector('[data-v9-remove]')?.addEventListener('click',async()=>{const current=favMap().get(String(source));const res=await api(ENDPOINTS.v6y,{action:'savePreference',sourcePlayerId:source,isFavorite:false,strategy:'none',priority:0,maxPrice:current?.max_price??'',expectedSpend:current?.expected_spend??'',note:current?.note||''},{quiet:true});if(res?.preference)state.v7Preferences.set(String(source),res.preference);renderStrategy();renderStats();});
    });
  }

  function renderStats(){
    const host=document.querySelector('.v9-pane-stats');if(!host)return;
    const credits=Number(state.auction?.settings?.initial_credits||state.setup?.initial_credits||500),mantra=mode()==='mantra',dist=classicBudget(),best=buildBestRoster();
    const starter=best.players.filter(x=>x.starter),bench=best.players.filter(x=>!x.starter);
    host.innerHTML=`<div class="v9scroll"><section class="v9card"><div class="between"><div><strong>Statistiche vittoria</strong><small class="soft">benchmark forniti · lega a 10</small></div><span class="badge">${mantra?'MANTRA ADATTATO':'CLASSIC'}</span></div><div class="v9kpi"><span><small>Fantamedia target</small><b>${targetAverage().toFixed(1)}</b></span><span><small>Gare ≥72</small><b>${BENCH.rule72.winner}/38</b></span><span><small>Gol target</small><b>${BENCH.bonus.goals}</b></span><span><small>Assist target</small><b>${BENCH.bonus.assists}</b></span></div>${mantra?'<small class="soft">Per Mantra il riferimento di fantamedia è ridotto di ~0,5 rispetto al benchmark Classic allegato; budget non suddiviso rigidamente per ruolo.</small>':''}</section><section class="v9card"><strong>${mantra?'Distribuzione strategica':'Budget dei vincitori'}</strong>${mantra?`<div class="v9bar"><b>TIT</b><span><i style="width:${Number(state.v8Profile?.starter_budget_percent||60)}%"></i></span><em>${Number(state.v8Profile?.starter_budget_percent||60)}% · ${Math.round(credits*Number(state.v8Profile?.starter_budget_percent||60)/100)} cr</em></div><div class="v9bar"><b>PAN</b><span><i style="width:${100-Number(state.v8Profile?.starter_budget_percent||60)}%"></i></span><em>${100-Number(state.v8Profile?.starter_budget_percent||60)}% · ${Math.round(credits*(100-Number(state.v8Profile?.starter_budget_percent||60))/100)} cr</em></div><small class="soft">Il 60/40 è una base: i doppi ruoli rendono poco utile forzare budget rigidi per ruolo.</small>`:barRows(dist,credits)}</section>${!mantra?`<section class="v9card"><strong>Prezzo medio slot per slot</strong><div class="v9card-scroll">${Object.entries(BENCH.slotModClean).map(([r,a])=>`<div class="v9slotgroup"><b>${r}</b>${a.map((v,i)=>`<span>Slot ${i+1}<em>${pct(v)} · ${Math.round(credits*v/100)} cr</em></span>`).join('')}</div>`).join('')}</div></section>`:''}<section class="v9card"><strong>Indicatori di squadra</strong><div class="v9statsgrid"><span>Gol reparto A / offensivi<b>${BENCH.goals.A}</b></span><span>Gol C / centrali<b>${BENCH.goals.C}</b></span><span>Gol D / difensivi<b>${BENCH.goals.D}</b></span><span>Imbattibilità portiere<b>${BENCH.bonus.cleanSheets}</b></span><span>Cartellini G/R<b>${BENCH.bonus.yellow}/${BENCH.bonus.red}</b></span><span>Gol lasciati in panchina<b>${BENCH.bonus.benchGoals}</b></span></div></section><section class="v9card"><div class="between"><div><strong>Miglior rosa teorica</strong><small class="soft">PMA + PFC + FV prevista + presenza + panchina</small></div><label class="v9switch"><input id="v9-best-fav" type="checkbox" ${state.v9BestIncludeFav?'checked':''}> integra preferiti</label></div><div class="v9besthead"><span>${best.module}</span><b>${Math.round(best.spent)}/${best.budget} cr</b>${best.starterBudget?`<em>titolari ~${Math.round(best.starterBudget)} cr</em>`:''}</div><div class="v9bestcols"><div><strong>Titolari</strong><div class="v9card-scroll">${starter.map(x=>`<span><b>${esc(x.p.name)}</b><small>${esc(x.group||'')} · ${x.pr} cr · FV ${forecast(x.p).toFixed(2)}</small></span>`).join('')}</div></div><div><strong>Ricambi</strong><div class="v9card-scroll">${bench.map(x=>`<span><b>${esc(x.p.name)}</b><small>${esc(x.group||'')} · ${x.pr} cr · FV ${forecast(x.p).toFixed(2)}</small></span>`).join('')}</div></div></div></section></div>`;
    host.querySelector('#v9-best-fav')?.addEventListener('change',async e=>{state.v9BestIncludeFav=e.target.checked;const res=await api(ENDPOINTS.strategy,{action:'saveProfile',preferredModules:state.v8Profile?.preferred_modules||[],profile:state.v8Profile?.profile||'balanced',roleBudgets:state.v8Profile?.role_budgets||{},notes:state.v8Profile?.notes||'',starterBudgetPercent:Number(state.v8Profile?.starter_budget_percent||60),includeFavoritesInBestRosters:state.v9BestIncludeFav},{quiet:true});if(res?.profile){state.v8Profile=res.profile;state.v9Center.profile=res.profile}renderStats();});
  }

  function activateTab(name){state.v9ActiveDrawerTab=name;document.querySelectorAll('.v9-drawer-tab').forEach(b=>b.classList.toggle('active',b.dataset.v9Tab===name));document.querySelectorAll('.v9-pane').forEach(p=>p.hidden=p.dataset.v9Pane!==name);}
  function patchDrawer(){
    const card=document.querySelector('.auction-free-fixed');if(!card||card.dataset.v9Ready)return;
    card.dataset.v9Ready='1';card.classList.add('v9-tabbed');
    const existing=[...card.children],free=document.createElement('div');free.className='v9-pane v9-pane-free';free.dataset.v9Pane='free';existing.forEach(x=>free.appendChild(x));
    const tabs=document.createElement('div');tabs.className='v9-drawer-tabs';tabs.innerHTML=`<button type="button" class="v9-drawer-tab" data-v9-tab="free">SVINCOLATI</button><button type="button" class="v9-drawer-tab" data-v9-tab="strategy">CENTRO STRATEGICO</button><button type="button" class="v9-drawer-tab" data-v9-tab="stats">STATISTICHE</button>`;
    const strategy=document.createElement('div');strategy.className='v9-pane v9-pane-strategy';strategy.dataset.v9Pane='strategy';
    const stats=document.createElement('div');stats.className='v9-pane v9-pane-stats';stats.dataset.v9Pane='stats';
    card.append(tabs,free,strategy,stats);tabs.querySelectorAll('[data-v9-tab]').forEach(b=>b.addEventListener('click',()=>activateTab(b.dataset.v9Tab)));
    renderStrategy();renderStats();activateTab(state.v9ActiveDrawerTab||'free');
  }

  async function loadRulesIntoSetup(){
    if(!document.getElementById('setup-form'))return;
    try{const res=await api(ENDPOINTS.scoring,{action:'getRules'},{quiet:true});if(res?.rules)state.v9Rules=res.rules;}catch{}
    patchSetup();
  }
  function patchSetup(){
    const form=document.getElementById('setup-form');if(!form)return;
    let box=document.getElementById('v9-scoring-setup');
    if(!box){box=document.createElement('section');box.id='v9-scoring-setup';box.className='panel full';const first=form.querySelector('.panel');first?.insertAdjacentElement('afterend',box);}
    const mantra=document.getElementById('setup-fantasy-mode')?.value==='mantra',r=state.v9Rules||{};
    box.innerHTML=`<div class="panel-title"><div><h2>${mantra?'D-Factor':'Modificatore difesa'} e portiere</h2><p>Impostazioni coerenti con le opzioni Leghe Fantacalcio.it.</p></div></div><div class="form-grid"><label class="check-line"><input id="v9-defense" type="checkbox" ${r.defense_rule_enabled?'checked':''}> ${mantra?'Attiva D-Factor':'Attiva Modificatore difesa'}</label><label class="check-line"><input id="v9-defense-gk" type="checkbox" ${r.defense_include_goalkeeper!==false?'checked':''}> ${mantra?'D-Factor 5+1 con portiere':'Includi portiere nel modificatore'}</label><label class="check-line"><input id="v9-clean" type="checkbox" ${r.clean_sheet_bonus_enabled?'checked':''}> Bonus portiere imbattuto</label><label>Valore bonus<input id="v9-clean-value" type="number" min="0" max="10" step="0.5" value="${r.clean_sheet_bonus_value??1}"></label></div><small class="soft">${mantra?'Mantra: D-Factor su 5 uomini difensivi; opzionalmente 5+1 includendo il portiere. Non è previsto portiere + 4 uomini di movimento.':'Classic: con portiere incluso il modificatore usa portiere + migliori 3 difensori; senza portiere usa i migliori 4 difensori.'}</small>`;
    const sync=()=>{box.querySelector('#v9-defense-gk').disabled=!box.querySelector('#v9-defense').checked;box.querySelector('#v9-clean-value').disabled=!box.querySelector('#v9-clean').checked};box.querySelector('#v9-defense')?.addEventListener('change',sync);box.querySelector('#v9-clean')?.addEventListener('change',sync);sync();
  }

  const oldUpdateVisibility=updateSetupVisibility;updateSetupVisibility=function(...a){const r=oldUpdateVisibility(...a);patchSetup();return r};
  const oldLoadSetup=loadSetup;loadSetup=async function(...a){const r=await oldLoadSetup(...a);await loadRulesIntoSetup();return r};
  document.getElementById('setup-form')?.addEventListener('submit',async()=>{const box=document.getElementById('v9-scoring-setup');if(!box)return;try{const res=await api(ENDPOINTS.scoring,{action:'saveRules',defenseRuleEnabled:box.querySelector('#v9-defense')?.checked===true,defenseIncludeGoalkeeper:box.querySelector('#v9-defense-gk')?.checked!==false,cleanSheetBonusEnabled:box.querySelector('#v9-clean')?.checked===true,cleanSheetBonusValue:Number(box.querySelector('#v9-clean-value')?.value||1)},{quiet:true});if(res?.rules)state.v9Rules=res.rules;}catch(e){msg(e.message||'Errore salvataggio regole punteggio.','error')}},false);

  const oldLive=renderAuctionLive;renderAuctionLive=function(...a){const r=oldLive(...a);queueMicrotask(()=>{document.querySelector('.v8center')?.remove();patchDrawer()});return r};
  const oldLobby=renderAuctionLobby;renderAuctionLobby=function(...a){const r=oldLobby(...a);queueMicrotask(()=>{document.querySelector('.v8center')?.remove();patchDrawer()});return r};
  const oldPrepared=renderAuctionPrepared;renderAuctionPrepared=function(...a){const r=oldPrepared(...a);queueMicrotask(()=>{document.querySelector('.v8center')?.remove();patchDrawer()});return r};
  const oldLoadAuction=loadAuction;loadAuction=async function(...a){const r=await oldLoadAuction(...a);await loadV9();document.querySelector('.v8center')?.remove();patchDrawer();return r};

  const obs=new MutationObserver(()=>{if(state.view==='auction'){document.querySelector('.v8center')?.remove();patchDrawer()}});const ar=document.getElementById('auction-root');if(ar)obs.observe(ar,{childList:true,subtree:true});

  const st=document.createElement('style');st.textContent=`
    .auction-free-fixed.v9-tabbed{grid-template-rows:25px minmax(0,1fr)!important;overflow:hidden!important}.v9-drawer-tabs{display:grid;grid-template-columns:1fr 1.25fr 1fr;gap:2px;padding:2px;background:rgba(7,25,44,.96);border-bottom:1px solid rgba(91,151,216,.25)}.v9-drawer-tab{min-height:20px!important;height:20px!important;padding:1px 4px!important;background:rgba(34,64,96,.45)!important;border:1px solid rgba(91,151,216,.18)!important;font-size:6.5px!important}.v9-drawer-tab.active{background:var(--primary)!important}.v9-pane{min-height:0;overflow:hidden}.v9-pane-free{display:grid;grid-template-rows:auto auto minmax(0,1fr);height:100%;min-height:0}.v9-tabbed.has-status-card.has-caller-controls .v9-pane-free{grid-template-rows:auto auto auto minmax(0,1fr) auto}.v9-tabbed.has-status-card.no-caller-controls .v9-pane-free{grid-template-rows:auto auto minmax(0,1fr) auto}.v9-pane-strategy,.v9-pane-stats{height:100%;overflow:auto;overscroll-behavior:contain;padding:4px}.v9scroll{display:grid;gap:5px;align-content:start}.v9card{min-height:0;padding:6px;border:1px solid rgba(91,151,216,.24);border-radius:7px;background:linear-gradient(145deg,rgba(27,56,86,.58),rgba(8,28,48,.64));display:grid;gap:5px}.v9card-scroll{min-height:0;max-height:190px;overflow:auto;overscroll-behavior:contain;scrollbar-gutter:stable}.v9block{display:grid;gap:3px}.v9block>b,.v9card>strong{font-size:8px}.v9block>small{color:var(--soft);font-size:6px}.v9mods{display:flex;flex-wrap:wrap;gap:2px}.v9mods label{display:flex;align-items:center;gap:2px;padding:2px 4px;border:1px solid var(--line);border-radius:5px;font-size:6px}.v9mods input{width:11px;min-width:11px;height:11px;min-height:11px}.v9budgets{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px}.v9fav{display:grid;grid-template-columns:minmax(0,1fr) 58px 20px;gap:3px;align-items:center;padding:4px;border-bottom:1px solid rgba(91,151,216,.14)}.v9fav strong,.v9fav small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v9fav strong{font-size:7px}.v9fav small{font-size:5.5px;color:var(--soft)}.v9fav label{font-size:5px}.v9fav input{min-height:23px;height:23px;padding:2px 4px}.v9fav button{width:20px!important;min-width:20px!important;height:20px!important;min-height:20px!important;padding:0!important}.v9top{display:grid;grid-template-columns:minmax(0,1fr) 38px 32px 32px;gap:3px;align-items:center;min-height:24px;border-bottom:1px solid rgba(91,151,216,.14);font-size:6px}.v9top.mom{border:1px solid rgba(220,180,70,.45);border-radius:5px;padding:0 3px}.v9top span{text-align:right}.v9empty{padding:8px;color:var(--soft);font-size:6px}.v9kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:3px}.v9kpi span{padding:5px;border:1px solid rgba(91,151,216,.18);border-radius:5px;background:rgba(11,42,77,.55)}.v9kpi small,.v9kpi b{display:block}.v9kpi small{font-size:5px;color:var(--soft)}.v9kpi b{font-size:11px}.v9bar{display:grid;grid-template-columns:24px minmax(0,1fr) 84px;gap:4px;align-items:center;font-size:6px}.v9bar span{height:8px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden}.v9bar i{display:block;height:100%;background:linear-gradient(90deg,#3478f6,#43d6b5);border-radius:99px}.v9bar em{font-style:normal;text-align:right;color:var(--soft)}.v9slotgroup{display:grid;grid-template-columns:24px repeat(auto-fit,minmax(62px,1fr));gap:3px;padding:3px 0;border-bottom:1px solid rgba(91,151,216,.14)}.v9slotgroup span{display:grid;font-size:5.5px}.v9slotgroup em{font-style:normal;color:var(--soft)}.v9statsgrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:3px}.v9statsgrid span{padding:4px;border:1px solid rgba(91,151,216,.16);border-radius:5px;font-size:5.5px}.v9statsgrid b{display:block;font-size:10px;margin-top:2px}.v9switch{display:flex!important;align-items:center;gap:3px!important;font-size:6px!important}.v9switch input{width:14px;min-width:14px;height:14px;min-height:14px}.v9besthead{display:flex;align-items:center;gap:6px;font-size:6px}.v9besthead b{font-size:8px}.v9besthead em{font-style:normal;color:var(--soft)}.v9bestcols{display:grid;grid-template-columns:1fr 1fr;gap:4px;min-height:0}.v9bestcols>div{min-height:0;border:1px solid rgba(91,151,216,.15);border-radius:5px;padding:4px}.v9bestcols>div>strong{font-size:7px}.v9bestcols .v9card-scroll{max-height:220px}.v9bestcols .v9card-scroll>span{display:block;padding:3px;border-bottom:1px solid rgba(91,151,216,.12)}.v9bestcols b,.v9bestcols small{display:block}.v9bestcols b{font-size:6px}.v9bestcols small{font-size:5px;color:var(--soft)}@media(max-width:700px){.v9-drawer-tabs{grid-template-columns:1fr}.v9-drawer-tab{height:18px!important;min-height:18px!important}.auction-free-fixed.v9-tabbed{grid-template-rows:58px minmax(0,1fr)!important}.v9kpi,.v9statsgrid{grid-template-columns:repeat(2,minmax(0,1fr))}.v9bestcols{grid-template-columns:1fr}.v9budgets{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;document.head.appendChild(st);

  void loadV9(true).then(()=>{if(state.view==='auction')patchDrawer();if(state.view==='setup')loadRulesIntoSetup()});
})();
