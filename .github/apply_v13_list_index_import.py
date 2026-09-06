from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v13-list-index-import-runtime' in s:
    raise SystemExit('V13 already present')

runtime=r'''
<script id="v13-list-index-import-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V13_LIST_INDEX_IMPORT__)return;
  window.__FANTA_V13_LIST_INDEX_IMPORT__=1;

  ENDPOINTS.leagueMeta=`${SUPABASE_URL}/functions/v1/league-meta-api`;
  state.v13NextRound=Number(state.v13NextRound||1);
  state.v13MetaLeague=state.v13MetaLeague||'';
  state.v13Filters=state.v13Filters||{};

  const V13_FILTER_KEYS=['role','name','team','badge','slot','presence','pfc','pma','delta','index','threshold','expected','fmv','favorite'];
  const v13Num=v=>{const n=Number(v);return Number.isFinite(n)?n:null};
  const v13Esc=v=>typeof esc==='function'?esc(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const v13Mode=()=>typeof fantasyMode==='function'?fantasyMode():'classic';
  const v13Roles=p=>typeof playerRoles==='function'?playerRoles(p,v13Mode()):[];
  const v13Presence=p=>typeof strategicPresencePercent==='function'?Number(strategicPresencePercent(p)||0):Number(p?.expected_titolarity||0);
  const v13Fmv=p=>typeof strategicExpectedFantasyAverage==='function'?Number(strategicExpectedFantasyAverage(p)||0):Number(p?.expected_fantasy_avg||0);
  const v13Threshold=p=>typeof strategicThresholdPrice==='function'?Number(strategicThresholdPrice(p)||0):0;
  const v13Expected=p=>typeof strategicExpectedPrice==='function'?Number(strategicExpectedPrice(p)||0):0;
  const v13Delta=p=>{const x=v13Num(p?.pfc_pma_delta);if(x!==null)return x;const a=v13Num(p?.pfc),b=v13Num(p?.pma);return a!==null&&b!==null?a-b:null};
  const v13Pref=p=>state.v7Preferences?.get(String(p?.source_player_id||p?.id||''))||null;
  const v13Favorite=p=>{const x=v13Pref(p);return Boolean(x?.is_favorite||x?.strategy==='top')};

  async function v13LoadMeta(force=false){
    const leagueId=state.selectedLeague?.id||'';
    if(!leagueId)return null;
    if(!force&&state.v13MetaLeague===leagueId)return state.v13NextRound;
    try{
      const res=await api(ENDPOINTS.leagueMeta,{action:'getMeta'},{quiet:true});
      if(res?.nextRound){state.v13NextRound=Number(res.nextRound);state.v13MetaLeague=leagueId;}
      v13MountNextRoundSetup(res?.canEdit===true);
      return state.v13NextRound;
    }catch(e){console.warn('Next round meta',e);return state.v13NextRound;}
  }

  function v13RoundsRemaining(){return Math.max(0,39-Math.max(1,Math.min(38,Number(state.v13NextRound||1))))}
  function v13ExpectedGames(player){
    const next=Math.max(1,Math.min(38,Number(state.v13NextRound||1)));
    const remaining=v13RoundsRemaining();
    const until=Math.max(0,Number(player?.unavailable_until_round||0));
    const forcedMiss=until>=next?Math.min(remaining,until-next+1):0;
    const available=Math.max(0,remaining-forcedMiss);
    return available*Math.max(0,Math.min(100,v13Presence(player)))/100;
  }
  function v13SeasonContribution(player){return Math.max(0,v13Fmv(player))*v13ExpectedGames(player)}
  function v13CreditPerPoint(){
    const remaining=v13RoundsRemaining();if(!remaining)return 0;
    const target=typeof strategicWinningTargetAverage==='function'?Number(strategicWinningTargetAverage()||72):72;
    const credits=Number(state.auction?.settings?.initial_credits||state.setup?.initial_credits||500);
    return credits/Math.max(1,target*remaining);
  }

  /* INDICE = valore in crediti della produzione stagionale prevista:
     FMV prevista × presenze/giornate attese × valore-crediti di un punto. */
  strategicValueIndex=function(player){return Math.max(0,Math.round(v13SeasonContribution(player)*v13CreditPerPoint()))};
  strategicIndexTitle=function(player){
    const games=v13ExpectedGames(player),points=v13SeasonContribution(player),value=strategicValueIndex(player);
    return `Indice ${value} cr · FMV ${v13Fmv(player).toFixed(2)} × ${games.toFixed(1)} gare attese = ${points.toFixed(1)} punti stagionali previsti · prossima G${state.v13NextRound}`;
  };

  function v13SignalKeys(p){
    const out=[];
    if(p?.market_flag===true)out.push('market');
    if(p?.new_arrival===true)out.push('new');
    if(Number(p?.unavailable_until_round||0)>=Number(state.v13NextRound||1)||p?.uncertain_return===true)out.push('injury');
    if(typeof importedProbabilityPercent==='function'&&importedProbabilityPercent(p?.penalty_probability)>0)out.push('penalties');
    if(typeof importedProbabilityPercent==='function'&&importedProbabilityPercent(p?.free_kick_probability)>0)out.push('free_kicks');
    return out;
  }

  function v13NumericMatch(value,expr){
    const x=v13Num(value),q=String(expr||'').trim().replace(',','.');if(!q)return true;if(x===null)return false;
    let m=q.match(/^(>=|<=|>|<|=)?\s*(-?\d+(?:\.\d+)?)$/);if(m){const op=m[1]||'=',n=Number(m[2]);return op==='>'?x>n:op==='<'?x<n:op==='>='?x>=n:op==='<='?x<=n:Math.abs(x-n)<1e-9;}
    m=q.match(/^(-?\d+(?:\.\d+)?)\s*[-:]\s*(-?\d+(?:\.\d+)?)$/);if(m){const a=Number(m[1]),b=Number(m[2]);return x>=Math.min(a,b)&&x<=Math.max(a,b)}
    return String(x).includes(q);
  }
  function v13FilterMatch(p){
    const f=state.v13Filters||{},roles=v13Roles(p).join('/').toLowerCase(),signals=v13SignalKeys(p);
    if(f.role&&f.role!=='all'&&!roles.split('/').includes(String(f.role).toLowerCase()))return false;
    if(f.name&&!String(p?.name||'').toLowerCase().includes(String(f.name).toLowerCase()))return false;
    if(f.team&&f.team!=='all'&&String(p?.serie_a_team||'')!==f.team)return false;
    if(f.badge&&f.badge!=='all'&&!signals.includes(f.badge))return false;
    if(f.slot&&f.slot!=='all'&&String(p?.slot??'')!==String(f.slot))return false;
    if(!v13NumericMatch(v13Presence(p),f.presence))return false;
    if(!v13NumericMatch(p?.pfc,f.pfc))return false;
    if(!v13NumericMatch(p?.pma,f.pma))return false;
    if(!v13NumericMatch(v13Delta(p),f.delta))return false;
    if(!v13NumericMatch(strategicValueIndex(p),f.index))return false;
    if(!v13NumericMatch(v13Threshold(p),f.threshold))return false;
    if(!v13NumericMatch(v13Expected(p),f.expected))return false;
    if(!v13NumericMatch(v13Fmv(p),f.fmv))return false;
    if(f.favorite==='yes'&&!v13Favorite(p))return false;
    if(f.favorite==='no'&&v13Favorite(p))return false;
    return true;
  }
  function v13SortValue(p,key){
    const values={
      role:v13Roles(p).join('/'),name:p?.name||'',team:p?.serie_a_team||'',badge:v13SignalKeys(p).join(','),slot:Number(p?.slot??999),presence:v13Presence(p),pfc:Number(p?.pfc??-1),pma:Number(p?.pma??-1),delta:v13Delta(p)??-999,index:strategicValueIndex(p),threshold:v13Threshold(p),expected:v13Expected(p),fmv:v13Fmv(p),favorite:v13Favorite(p)?1:0
    };return values[key]??'';
  }
  function v13SortPlayers(rows){
    const key=state.listSort?.key||'name',dir=state.listSort?.direction==='desc'?-1:1;
    return [...rows].sort((a,b)=>{const av=v13SortValue(a,key),bv=v13SortValue(b,key);let c;if(typeof av==='number'&&typeof bv==='number')c=av-bv;else c=String(av).localeCompare(String(bv),'it',{sensitivity:'base'});return c===0?String(a.name||'').localeCompare(String(b.name||''),'it'):c*dir});
  }

  const sortHead=(key,label)=>`<button type="button" data-list-sort="${key}">${label} <span>${state.listSort?.key===key?(state.listSort.direction==='desc'?'↓':'↑'):'↕'}</span></button>`;
  const filterInput=(key,placeholder='filtra')=>`<input class="v13-col-filter" data-v13-filter="${key}" value="${v13Esc(state.v13Filters?.[key]||'')}" placeholder="${placeholder}">`;
  const filterSelect=(key,options)=>`<select class="v13-col-filter" data-v13-filter="${key}"><option value="">tutti</option>${options.map(([v,l])=>`<option value="${v13Esc(v)}" ${String(state.v13Filters?.[key]||'')===String(v)?'selected':''}>${v13Esc(l)}</option>`).join('')}</select>`;

  function v13Header(players){
    const roles=[...new Set(players.flatMap(p=>v13Roles(p)))].sort();
    const teams=[...new Set(players.map(p=>p.serie_a_team).filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b),'it'));
    const slots=[...new Set(players.map(p=>p.slot).filter(v=>v!==null&&v!==undefined&&v!==''))].sort((a,b)=>Number(a)-Number(b));
    return `<tr class="v13-sort-row">
      <th>${sortHead('role','Ruoli')}</th><th>${sortHead('name','Nome')}</th><th>${sortHead('team','Squadra')}</th><th>${sortHead('badge','Badge')}</th><th>${sortHead('slot','Slot')}</th><th>${sortHead('presence','%Tit')}</th><th>${sortHead('pfc','PFC')}</th><th>${sortHead('pma','PMA')}</th><th>${sortHead('delta','Delta')}</th><th>${sortHead('index','Indice cr')}</th><th>${sortHead('threshold','Soglia')}</th><th>${sortHead('expected','Prezzo atteso')}</th><th>${sortHead('fmv','FMV')}</th><th>${sortHead('favorite','Preferito')}</th>
    </tr><tr class="v13-filter-row">
      <th>${filterSelect('role',roles.map(x=>[String(x).toLowerCase(),x]))}</th>
      <th>${filterInput('name','nome')}</th>
      <th>${filterSelect('team',teams.map(x=>[x,x]))}</th>
      <th>${filterSelect('badge',[['market','mercato'],['injury','indisp.'],['new','nuovo'],['penalties','rigori'],['free_kicks','piazzati']])}</th>
      <th>${filterSelect('slot',slots.map(x=>[String(x),String(x)]))}</th>
      <th>${filterInput('presence','>=70')}</th><th>${filterInput('pfc','10-30')}</th><th>${filterInput('pma','10-30')}</th><th>${filterInput('delta','>0')}</th><th>${filterInput('index','>=20')}</th><th>${filterInput('threshold','>=20')}</th><th>${filterInput('expected','>=20')}</th><th>${filterInput('fmv','>=6.5')}</th>
      <th>${filterSelect('favorite',[['yes','sì'],['no','no']])}</th>
    </tr>`;
  }

  function v13Heart(p){const yes=v13Favorite(p);return `<button type="button" class="v13-heart ${yes?'active':''}" data-v13-fav="${v13Esc(p?.source_player_id||p?.id||'')}" data-v13-player="${v13Esc(p?.id||'')}" aria-pressed="${yes?'true':'false'}" title="${yes?'Rimuovi dai preferiti':'Aggiungi ai preferiti'}">${yes?'♥':'♡'}</button>`}
  function v13Row(p){
    const roles=v13Roles(p),delta=v13Delta(p),signals=typeof auctionPlayerSignalBadges==='function'?auctionPlayerSignalBadges(p):'—';
    return `<tr data-player-id="${v13Esc(p.id)}">
      <td>${roles.map(r=>`<span class="rolebadge" data-role="${v13Esc(r)}">${v13Esc(r)}</span>`).join('')}</td>
      <td class="v13-name"><strong>${v13Esc(p.name||'—')}</strong></td>
      <td>${v13Esc(p.serie_a_team||'—')}</td><td class="v13-badges">${signals}</td><td class="num">${v13Esc(p.slot??'—')}</td><td class="num">${Math.round(v13Presence(p))}%</td><td class="num"><strong>${Math.round(Number(p.pfc||0))}</strong></td><td class="num">${Math.round(Number(p.pma||0))}</td><td class="num ${delta>0?'positive':delta<0?'negative':''}">${delta==null?'—':`${delta>0?'+':''}${Math.round(delta)}`}</td><td class="num strategic-index-value" title="${v13Esc(strategicIndexTitle(p))}">${strategicValueIndex(p)}</td><td class="num">${Math.round(v13Threshold(p)||0)}</td><td class="num">${Math.round(v13Expected(p)||0)}</td><td class="num">${v13Fmv(p).toFixed(2)}</td><td class="v13-fav-cell">${v13Heart(p)}</td>
    </tr>`;
  }

  renderListTable=function(){
    if(!state.list)return;
    const all=state.list.players||[],controls={search:$('list-search'),team:$('list-team'),slot:$('list-slot'),flag:$('list-flag')};
    let rows=typeof filterPlayers==='function'?filterPlayers(all,controls,state.listRoles,v13Mode()):all;
    rows=rows.filter(v13FilterMatch);rows=v13SortPlayers(rows);
    const thead=document.querySelector('#view-list .player-table thead');if(thead)thead.innerHTML=v13Header(all);
    const body=document.getElementById('list-body');if(body)body.innerHTML=rows.map(v13Row).join('')||'<tr><td colspan="14" class="soft" style="text-align:center;height:60px">Nessun giocatore.</td></tr>';
  };

  document.querySelector('#view-list')?.addEventListener('input',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;renderListTable();});
  document.querySelector('#view-list')?.addEventListener('change',e=>{const el=e.target.closest?.('[data-v13-filter]');if(!el)return;state.v13Filters[el.dataset.v13Filter]=el.value;renderListTable();});
  document.querySelector('#view-list')?.addEventListener('click',async e=>{
    const heart=e.target.closest?.('[data-v13-fav]');if(!heart)return;
    e.preventDefault();e.stopPropagation();
    const source=String(heart.dataset.v13Fav||''),current=state.v7Preferences?.get(source)||null,next=!Boolean(current?.is_favorite||current?.strategy==='top');
    heart.disabled=true;
    try{
      const res=await api(ENDPOINTS.v6y,{action:'savePreference',sourcePlayerId:source,isFavorite:next,strategy:next?(current?.strategy==='top'?'top':'favorite'):'none',priority:Number(current?.priority||0),maxPrice:current?.max_price??'',expectedSpend:current?.expected_spend??'',note:current?.note||''},{quiet:true});
      if(res?.preference){state.v7Preferences=state.v7Preferences||new Map();state.v7Preferences.set(source,res.preference);renderListTable();}
    }catch(err){msg(err.message||'Errore preferito.','error')}finally{heart.disabled=false;}
  });

  /* Nuova giornata nel Setup. */
  function v13MountNextRoundSetup(canEdit=true){
    const grid=document.querySelector('#setup-form .panel .form-grid');if(!grid)return;
    let label=document.getElementById('v13-next-round-label');
    if(!label){label=document.createElement('label');label.id='v13-next-round-label';label.innerHTML='Prossima giornata<input id="v13-next-round" type="number" min="1" max="38">';grid.appendChild(label);}
    const input=document.getElementById('v13-next-round');if(input){input.value=String(state.v13NextRound||1);input.disabled=!canEdit;}
  }
  if(typeof loadSetup==='function'){
    const oldLoadSetupV13=loadSetup;
    loadSetup=async function(...args){const r=await oldLoadSetupV13(...args);await v13LoadMeta(true);v13MountNextRoundSetup(true);return r;};
  }
  document.getElementById('setup-form')?.addEventListener('submit',async()=>{
    const input=document.getElementById('v13-next-round');if(!input)return;
    const next=Number(input.value);if(!Number.isInteger(next)||next<1||next>38){msg('Prossima giornata non valida.','error');return;}
    try{const res=await api(ENDPOINTS.leagueMeta,{action:'saveNextRound',nextRound:next},{quiet:true});if(res?.nextRound){state.v13NextRound=Number(res.nextRound);state.v13MetaLeague=state.selectedLeague?.id||'';}}
    catch(e){msg(e.message||'Errore salvataggio giornata.','error')}
  },false);

  /* Import CSV/XLS/XLSX: il file resta nel browser; al termine staging e batch incompleti
     vengono ripuliti dal trigger DB e l'input file viene azzerato. */
  function v13LoadXlsx(){return new Promise((resolve,reject)=>{if(window.XLSX)return resolve(window.XLSX);const sc=document.createElement('script');sc.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';sc.onload=()=>resolve(window.XLSX);sc.onerror=()=>reject(new Error('Impossibile caricare il parser Excel.'));document.head.appendChild(sc);});}
  const v13Pick=(row,names)=>{for(const n of names){if(Object.prototype.hasOwnProperty.call(row,n)&&row[n]!==''&&row[n]!==null&&row[n]!==undefined)return row[n];const k=Object.keys(row).find(k=>String(k).toLowerCase()===String(n).toLowerCase());if(k&&row[k]!==''&&row[k]!==null&&row[k]!==undefined)return row[k];}return null};
  const v13Bool=v=>{if(typeof v==='boolean')return v;const x=String(v??'').trim().toLowerCase();return ['1','true','si','sì','yes','y','x'].includes(x)||(x!==''&&!['0','false','no','n'].includes(x))};
  const v13Number=v=>{if(v===null||v===undefined||v==='')return null;const n=Number(String(v).replace(',','.'));return Number.isFinite(n)?n:null};
  function v13NormalizeRow(row,index){
    const name=String(v13Pick(row,['name','nome','player','calciatore'])||'').trim(),team=String(v13Pick(row,['team','squadra'])||'').trim();
    const pfc=v13Number(v13Pick(row,['pfc'])),pma=v13Number(v13Pick(row,['pma']));
    const mantraRaw=v13Pick(row,['roleMantra','mantra_roles','ruoloMantra','ruoliMantra']);
    const mantra=Array.isArray(mantraRaw)?mantraRaw:String(mantraRaw||'').split(/[\s,;/]+/).map(x=>x.trim()).filter(Boolean);
    const normalized={
      name,team,classic_role:String(v13Pick(row,['role','classic_role','ruolo'])||'').trim(),mantra_roles:mantra,
      pma,pfc,pfc_pma_delta:v13Number(v13Pick(row,['dpfcpma','pfc_pma_delta','delta']))??(pfc!==null&&pma!==null?pfc-pma:null),
      pma_range:v13Pick(row,['pmaRange','pma_range']),pfc_range:v13Pick(row,['pfcRange','pfc_range']),slot:v13Number(v13Pick(row,['slot'])),
      expected_titolarity:v13Number(v13Pick(row,['expectedTitolarita','expectedTitolarity','expected_titolarity'])),expected_fantasy_avg:v13Number(v13Pick(row,['expectedFantamedia','expected_fantasy_avg'])),
      penalty_probability:v13Number(v13Pick(row,['penaltyProbability','penalty_probability'])),free_kick_probability:v13Number(v13Pick(row,['freeKickProbability','free_kick_probability'])),
      unavailable_until_round:v13Number(v13Pick(row,['unavailableUntilRound','unavailable_until_round'])),tier_classic:v13Pick(row,['fasciaFc','tier_classic']),tier_mantra:v13Pick(row,['fasciaFr','tier_mantra']),
      uncertain_return:v13Bool(v13Pick(row,['rientroIncerto','uncertain_return'])),new_arrival:v13Bool(v13Pick(row,['newArrival','new_arrival'])),market_flag:v13Bool(v13Pick(row,['calciomercato','market_flag'])),
      source_updated_at:v13Pick(row,['updatedAt','source_updated_at']),last_three_year_titolarity:v13Number(v13Pick(row,['lastThreeYearTitolarity','last_three_year_titolarity'])),
      last_five_year_base_rating:v13Number(v13Pick(row,['lastFiveYearVotoBase','last_five_year_base_rating'])),last_five_year_fantasy_avg:v13Number(v13Pick(row,['lastFiveYearFantamedia','last_five_year_fantasy_avg'])),last_five_year_titolarity:v13Number(v13Pick(row,['lastFiveYearTitolarity','last_five_year_titolarity'])),
      last_year_base_rating:v13Number(v13Pick(row,['lastYearVotoBase','last_year_base_rating'])),last_year_fantasy_avg:v13Number(v13Pick(row,['lastYearFantamedia','last_year_fantasy_avg'])),last_year_titolarity:v13Number(v13Pick(row,['lastYearTitolarity','last_year_titolarity'])),
      last_five_matches_base_rating:v13Number(v13Pick(row,['lastFiveMatchesVotoBase','last_five_matches_base_rating'])),last_five_matches_fantasy_avg:v13Number(v13Pick(row,['lastFiveMatchesFantamedia','last_five_matches_fantasy_avg'])),last_five_matches_titolarity:v13Number(v13Pick(row,['lastFiveMatchesTitolarita','lastFiveMatchesTitolarity','last_five_matches_titolarity'])),
      current_season_base_rating:v13Number(v13Pick(row,['currentSeasonVotoBase','current_season_base_rating'])),current_season_fantasy_avg:v13Number(v13Pick(row,['currentSeasonFantamedia','current_season_fantasy_avg'])),current_season_titolarity:v13Number(v13Pick(row,['currentSeasonTitolarity','current_season_titolarity']))
    };
    const source=String(v13Pick(row,['id','playerId','sourcePlayerId','source_player_id'])||`${name}|${team}`).trim();
    return {rowIndex:index+1,sourcePlayerId:source,normalized,raw:row};
  }
  async function v13ImportFile(file){
    if(!file) return;const XLSX=await v13LoadXlsx(),buffer=await file.arrayBuffer(),wb=XLSX.read(buffer,{type:'array',cellDates:true});
    const sheet=wb.Sheets[wb.SheetNames[0]],rawRows=XLSX.utils.sheet_to_json(sheet,{defval:'',raw:false});
    if(!rawRows.length)throw new Error('Il file non contiene righe.');
    const rows=rawRows.map(v13NormalizeRow).filter(x=>x.normalized.name);
    if(!rows.length)throw new Error('Nessun giocatore riconosciuto.');
    const ext=(file.name.split('.').pop()||'').toLowerCase();
    const begin=await api(ENDPOINTS.list,{action:'beginListImport',sourceFilename:file.name,sourceFormat:ext,sourceColumns:Object.keys(rawRows[0]||{}),referenceDate:new Date().toISOString().slice(0,10)});
    const batchId=begin?.batchId;if(!batchId)throw new Error('Impossibile iniziare l’import.');
    for(let i=0;i<rows.length;i+=80)await api(ENDPOINTS.list,{action:'appendListImport',batchId,rows:rows.slice(i,i+80)});
    const fin=await api(ENDPOINTS.list,{action:'finishListImport',batchId});
    if(!fin?.ok&&fin?.rowCount==null)throw new Error('Import non finalizzato.');
    state.v13Filters={};
    await loadList();
    msg(`Listone aggiornato: ${fin.rowCount??rows.length} giocatori. Area temporanea import pulita.`,'success');
  }
  function v13MountImport(){
    if(!state.list?.permissions?.canManageList)return;
    const row=document.querySelector('#view-list .v12-toolbar-row')||document.querySelector('#view-list .v12-toolbar');if(!row||row.querySelector('#v13-import-button'))return;
    const input=document.createElement('input');input.type='file';input.id='v13-import-file';input.accept='.csv,.xls,.xlsx';input.hidden=true;
    const button=document.createElement('button');button.type='button';button.id='v13-import-button';button.className='secondary';button.textContent='IMPORTA CSV/XLSX';
    button.addEventListener('click',()=>input.click());
    input.addEventListener('change',async()=>{const file=input.files?.[0];if(!file)return;button.disabled=true;button.textContent='IMPORT…';try{await v13ImportFile(file)}catch(e){msg(e.message||'Errore import.','error')}finally{input.value='';button.disabled=false;button.textContent='IMPORTA CSV/XLSX';}});
    row.append(input,button);
  }

  if(typeof loadList==='function'){
    const oldLoadListV13=loadList;
    loadList=async function(...args){const r=await oldLoadListV13(...args);await v13LoadMeta();v13MountImport();renderListTable();return r;};
  }

  /* Evidenziazione chiamata: ora la soglia colore è l'Indice stesso, espresso in crediti. */
  function v13PatchCalled(){
    if(String(state.dashboard?.currentUser?.username||'').toLowerCase()!=='emanuelesordo')return;
    const p=state.auction?.currentPlayer,s=state.auction?.auctionSession;if(!p||!s)return;const value=Math.max(1,Number(strategicValueIndex(p)||1)),bid=Math.max(1,Number(s.current_bid||1)),ratio=bid/value;
    let hue=48;if(ratio<1)hue=48+84*Math.min(1,(1-ratio)/.35);else hue=48*Math.max(0,1-Math.min(1,(ratio-1)/.35));
    document.querySelectorAll('.auction-command-player').forEach(el=>{el.classList.add('v13-index-border');el.style.setProperty('--v13-hue',String(hue));});
  }
  if(typeof renderAuctionLive==='function'){const oldRAL13=renderAuctionLive;renderAuctionLive=function(...a){const r=oldRAL13(...a);queueMicrotask(v13PatchCalled);return r;};}

  const style=document.createElement('style');style.id='v13-list-index-import-style';style.textContent=`
    #view-list .player-table{width:100%!important;min-width:0!important;max-width:100%!important;table-layout:auto!important}
    #view-list .player-table th,#view-list .player-table td{width:auto!important;min-width:0!important;max-width:none!important;white-space:nowrap!important}
    #view-list .player-table th:nth-child(2),#view-list .player-table td:nth-child(2){width:18%!important}
    #view-list .player-table th:nth-child(3),#view-list .player-table td:nth-child(3){width:9%!important}
    #view-list .v13-sort-row th{height:27px!important;padding:2px 3px!important;font-size:7px!important}
    #view-list .v13-sort-row button{min-height:0!important;height:22px!important;padding:1px 2px!important;background:transparent!important;border:0!important;font-size:7px!important;box-shadow:none!important;color:var(--soft)!important}
    #view-list .v13-filter-row th{height:24px!important;padding:1px 2px!important;background:rgba(10,37,62,.96)!important}
    #view-list .v13-col-filter{width:100%!important;min-width:0!important;height:20px!important;min-height:20px!important;padding:1px 3px!important;border-radius:4px!important;font-size:6.5px!important;background:rgba(7,25,44,.92)!important}
    #view-list .player-table tbody td{height:34px!important;padding:4px 4px!important;font-size:9.5px!important;line-height:1.05!important}
    #view-list .player-table tbody td.num{font-size:10.5px!important;font-weight:750!important;font-variant-numeric:tabular-nums!important}
    #view-list .v13-name strong{font-size:9.5px!important}
    #view-list .v13-badges{max-width:84px!important}
    #view-list .v13-fav-cell{text-align:center!important}
    #view-list .v13-heart{width:27px!important;min-width:27px!important;height:27px!important;min-height:27px!important;padding:0!important;border-radius:50%!important;font-size:18px!important;line-height:1!important;background:rgba(10,38,65,.92)!important;border:1px solid rgba(111,171,224,.35)!important;color:#8aa9c7!important}
    #view-list .v13-heart.active{color:#ff688c!important;border-color:#ff688c!important;background:rgba(100,24,50,.28)!important}
    #view-list #v13-import-button{height:28px!important;min-height:28px!important;padding:2px 7px!important;font-size:7px!important;white-space:nowrap!important}
    body.v10-index-owner #view-auction .auction-command-player.v13-index-border{border:2px solid hsl(var(--v13-hue) 86% 53%)!important;box-shadow:0 0 0 1px hsl(var(--v13-hue) 86% 53%/.28),0 0 14px hsl(var(--v13-hue) 86% 53%/.22)!important}
    @media(max-width:1100px){#view-list .player-table tbody td{font-size:8.5px!important}#view-list .player-table tbody td.num{font-size:9.5px!important}.v13-col-filter{font-size:6px!important}}
  `;document.head.appendChild(style);

  void v13LoadMeta(true).then(()=>{if(state.view==='list'){v13MountImport();renderListTable();}});
})();
</script>
'''

if '</body>' not in s: raise SystemExit('body close missing')
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
