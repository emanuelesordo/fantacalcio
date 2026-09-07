from pathlib import Path
import re

p = Path('home.html')
s = p.read_text(encoding='utf-8')
if 'v17-live-performance-runtime' in s:
    raise SystemExit('V17 already applied')

# 1) Rosa: elimina la ripetizione del nome squadra nell'header; resta ROSA + toggle CODA.
old = '''            <div class="auction-team-roster-head">
              <strong>${esc(info.teamName)}</strong>

              <div class="auction-roster-head-actions">'''
new = '''            <div class="auction-team-roster-head">
              <strong>ROSA</strong>

              <div class="auction-roster-head-actions">'''
if old not in s:
    raise SystemExit('roster header target not found')
s = s.replace(old, new, 1)

# 2) Il refresh roster non deve bloccare il paint del cockpit durante il live.
old = '''      if (rosterChanged) {
        await loadAuctionPersonalRoster(
          true
        );
      } else {
        await loadAuctionPersonalRoster(
          false
        );
      }


      state.auctionRenderSignature ='''
new = '''      const rosterRefreshPromise =
        loadAuctionPersonalRoster(
          firstLoad ? true : Boolean(rosterChanged)
        );

      /*
       * V17 · percorso critico live.
       * Al primo ingresso aspettiamo la rosa. Durante l'asta utilizziamo
       * subito la copia già in memoria e aggiorniamo soltanto il pannello
       * Rosa quando il fetch termina, senza tenere ferma la console.
       */
      if (firstLoad) {
        await rosterRefreshPromise;
      } else {
        Promise.resolve(rosterRefreshPromise)
          .then(() => {
            if (typeof window.v17RefreshRosterFragments === 'function') {
              window.v17RefreshRosterFragments();
            }
          })
          .catch(() => {});
      }


      state.auctionRenderSignature ='''
if old not in s:
    raise SystemExit('blocking roster refresh target not found')
s = s.replace(old, new, 1)

# 3) V8 non deve ricostruire tutto il cockpit una seconda volta dopo loadAuction.
needle = "auctionSession()?.status==='live'?renderAuctionLive():patchCenter();return r};"
if needle not in s:
    raise SystemExit('V8 loadAuction rerender target not found')
s = s.replace(needle, "auctionSession()?.status==='live'?patchLive():patchCenter();return r};", 1)

# 4) V8: rimuove i KPI strategici ridondanti dall'header Rosa (erano anche costosi da calcolare).
pattern = re.compile(
    r"function patchLive\(\)\{const info=auctionMyTeamDashboardData\(\);.*?const p=state\.auction\?\.currentPlayer;",
    re.S,
)
replacement = "function patchLive(){const h=document.querySelector('.auction-team-column-roster-only .auction-team-roster-head');if(h){h.querySelector('.auction-v7-roster-metrics')?.remove();h.querySelector('.v8rm')?.remove();}const p=state.auction?.currentPlayer;"
s, n = pattern.subn(replacement, s, count=1)
if n != 1:
    raise SystemExit(f'V8 patchLive target count={n}')

# 5) V16 non deve fare un altro renderAuctionLive completo al termine di ogni loadAuction.
old = '''  if(typeof loadAuction==='function'){
    const oldLoad=loadAuction;
    loadAuction=async function(...args){
      const r=await oldLoad(...args);
      v16PreselectQueue();
      if(state.view==='auction'&&state.auction?.auctionSession?.status==='live')renderAuctionLive();
      return r;
    };
  }
'''
new = '''  if(typeof loadAuction==='function'){
    const oldLoad=loadAuction;
    loadAuction=async function(...args){
      const r=await oldLoad(...args);
      v16PreselectQueue();
      queueMicrotask(()=>{
        if(typeof patchAuctionTopSelection==='function')patchAuctionTopSelection();
        v16AfterRender();
      });
      return r;
    };
  }
'''
if old not in s:
    raise SystemExit('V16 extra render target not found')
s = s.replace(old, new, 1)

runtime = r'''
<script id="v17-live-performance-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V17_LIVE_PERF__)return;
  window.__FANTA_V17_LIVE_PERF__=1;

  const v17Now=()=>Date.now()+Number(state.serverOffsetMs||0);
  const v17Session=()=>typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession;
  const v17IsLive=()=>state.view==='auction'&&v17Session()?.status==='live';

  /* =========================================================
     1. SUGGERITORE FUORI DAL PERCORSO CRITICO
     ========================================================= */
  const v17HeavySuggestions=typeof renderAuctionSuggestedCalls==='function'?renderAuctionSuggestedCalls:null;
  let v17SuggestionHtml='';
  let v17SuggestionKey='';
  let v17SuggestionPendingKey='';
  let v17SuggestionTimer=null;

  function v17SuggestionContextKey(){
    const s=v17Session()||{},info=typeof auctionMyTeamDashboardData==='function'?auctionMyTeamDashboardData():null;
    return [
      s.id||'',s.current_player_id||'',s.role_phase_index||0,
      info?.assignments?.length||0,info?.remaining||0,info?.maxBid??'',
      state.auction?.callCandidates?.length||0,
      document.fullscreenElement?'FULL':'NORMAL',
      (state.v7SuggestedDismissed||[]).join(','),
      state.v8Moment||''
    ].join('|');
  }

  function v17BindSuggestionHost(){
    try{if(typeof attachAuctionCallQueueEvents==='function')attachAuctionCallQueueEvents();}catch(e){console.warn('V17 suggestion bind',e);}
  }

  function v17ScheduleSuggestions(key=v17SuggestionContextKey()){
    if(!v17HeavySuggestions||v17SuggestionPendingKey===key)return;
    v17SuggestionPendingKey=key;
    if(v17SuggestionTimer){clearTimeout(v17SuggestionTimer);v17SuggestionTimer=null;}
    const run=()=>{
      v17SuggestionTimer=null;
      if(v17SuggestionContextKey()!==key){v17SuggestionPendingKey='';v17ScheduleSuggestions();return;}
      try{
        const html=v17HeavySuggestions();
        v17SuggestionHtml=html||'';
        v17SuggestionKey=key;
        v17SuggestionPendingKey='';
        const host=document.querySelector('#view-auction .auction-free-suggestions');
        if(host&&v17IsLive()){
          host.innerHTML=v17SuggestionHtml;
          v17BindSuggestionHost();
        }
      }catch(error){
        v17SuggestionPendingKey='';
        console.warn('V17 strategic suggestions',error);
      }
    };
    if('requestIdleCallback' in window){
      requestIdleCallback(run,{timeout:220});
    }else{
      v17SuggestionTimer=setTimeout(run,0);
    }
  }

  if(v17HeavySuggestions){
    renderAuctionSuggestedCalls=function(){
      const key=v17SuggestionContextKey();
      if(v17SuggestionKey===key&&v17SuggestionHtml)return v17SuggestionHtml;
      v17ScheduleSuggestions(key);
      return v17SuggestionHtml||`<section class="auction-suggested-calls v17-suggestions-loading" aria-label="Consulente Strategico"><div class="auction-suggested-head"><div><strong>Consulente Strategico</strong><small>aggiornamento in background</small></div><span>LIVE</span></div></section>`;
    };
  }

  function v17InvalidateSuggestions(){
    v17SuggestionKey='';
    v17SuggestionPendingKey='';
    v17ScheduleSuggestions();
  }

  /* =========================================================
     2. PATCH DELLA SOLA ROSA DOPO FETCH ASINCRONO
     ========================================================= */
  window.v17RefreshRosterFragments=function(){
    if(!v17IsLive()||typeof renderAuctionCockpitTeamPanel!=='function')return;
    const current=document.querySelector('.auction-team-column-roster-only');
    if(current){
      const box=document.createElement('div');
      box.innerHTML=renderAuctionCockpitTeamPanel('roster').trim();
      const next=box.firstElementChild;
      if(next){current.replaceWith(next);if(typeof attachAuctionRosterQueueToggle==='function')attachAuctionRosterQueueToggle();}
    }
    document.querySelectorAll('.auction-v7-roster-metrics,.v8rm,.auction-roster-projected-summary').forEach(x=>x.remove());
    if(typeof patchAuctionMyTeamLiveKpis==='function')patchAuctionMyTeamLiveKpis();
    v17InvalidateSuggestions();
  };

  /* =========================================================
     3. REALTIME: RENDER STRUTTURALE IMMEDIATO DA HOT STATE
     ========================================================= */
  const v17OldApply=typeof applyAuctionHotState==='function'?applyAuctionHotState:null;
  if(v17OldApply){
    applyAuctionHotState=function(nextState,opts={}){
      const before=v17Session()?{...v17Session()}:null;
      const incomingPlayerId=nextState?.current_player_id;
      if(state.auction&&incomingPlayerId!==undefined){
        if(incomingPlayerId){
          const cached=(state.auction.callCandidates||[]).find(p=>String(p.id)===String(incomingPlayerId));
          if(cached)state.auction.currentPlayer=cached;
        }else{
          state.auction.currentPlayer=null;
        }
      }
      state.v17ApplyingHot=true;
      let result;
      try{result=v17OldApply(nextState,opts);}finally{state.v17ApplyingHot=false;}
      const after=v17Session();
      const structural=Boolean(before&&after&&(
        before.current_player_id!==after.current_player_id||
        before.current_nomination_team_id!==after.current_nomination_team_id||
        before.role_phase_index!==after.role_phase_index||
        before.role_phase_status!==after.role_phase_status||
        before.status!==after.status||
        before.pause_after_award!==after.pause_after_award
      ));
      if(structural&&state.view==='auction'&&after?.status==='live'){
        state.v17CriticalPaint=true;
        try{renderAuctionLive();}finally{state.v17CriticalPaint=false;}
        if(typeof renderAuctionTimer==='function')renderAuctionTimer();
        v17ScheduleSuggestions();
        if(typeof window.v11ScheduleAuctionRefresh==='function')window.v11ScheduleAuctionRefresh('hot-structural',180);
      }
      return result;
    };
  }

  /* =========================================================
     4. RECONCILE LEGGERO: V6Y HOT PRIMA, PAYLOAD COMPLETO DOPO
     ========================================================= */
  const v17OldSchedule=typeof scheduleAuctionReconcile==='function'?scheduleAuctionReconcile:null;
  let v17HotTimer=null,v17HotBusy=false,v17HotAgain=false;

  async function v17FastHotReconcile(){
    if(v17HotBusy){v17HotAgain=true;return;}
    const s=v17Session();
    if(!s?.id||s.status!=='live'||!state.session?.token)return;
    v17HotBusy=true;
    const started=performance.now();
    try{
      const hot=await api(ENDPOINTS.v6y,{action:'getHotState',sessionId:s.id},{quiet:true});
      if(hot?.serverNow){
        const measured=Date.parse(hot.serverNow)-Date.now();
        if(Number.isFinite(measured))state.serverOffsetMs=state.serverOffsetReady?(state.serverOffsetMs*.8+measured*.2):measured;
        state.serverOffsetReady=true;
      }
      if(hot?.currentPlayer)state.auction.currentPlayer=hot.currentPlayer;
      else if(hot?.state?.current_player_id==null)state.auction.currentPlayer=null;
      if(hot?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(hot.state,{fromMutation:false});
      if(Array.isArray(hot?.recentBids)){
        const teams=state.auction?.teams||[];
        state.auction.recentBids=hot.recentBids.map(b=>({...b,team:teams.find(t=>t.id===b.team_id)||null}));
        if(typeof renderRecentBidChips==='function')renderRecentBidChips();
      }
      state.v17LastHotMs=Math.round(performance.now()-started);
    }catch(error){
      console.warn('V17 hot reconcile',error);
    }finally{
      v17HotBusy=false;
      if(v17HotAgain){v17HotAgain=false;setTimeout(()=>void v17FastHotReconcile(),40);}
    }
  }

  if(v17OldSchedule){
    scheduleAuctionReconcile=function(delay=60){
      if(state.v17ApplyingHot)return;
      const s=v17Session();
      if(!s?.id||s.status!=='live')return v17OldSchedule(delay);
      if(v17HotTimer)clearTimeout(v17HotTimer);
      v17HotTimer=setTimeout(()=>{v17HotTimer=null;void v17FastHotReconcile();},Math.max(0,Math.min(180,Number(delay)||0)));
    };
  }

  /* =========================================================
     5. REFRESH CANONICO: MAI DURANTE UN COUNTDOWN DI RILANCIO
     ========================================================= */
  let v17FullTimer=null,v17FullBusy=false,v17FullAgain=false;
  window.v11ScheduleAuctionRefresh=function(reason='mutation',delay=180){
    if(v17FullTimer)clearTimeout(v17FullTimer);
    const run=async()=>{
      v17FullTimer=null;
      if(!state.session?.token||!state.selectedLeague?.id||state.view!=='auction')return;
      const s=v17Session();
      if(s?.current_player_id&&typeof auctionBidTimerIsActive==='function'&&auctionBidTimerIsActive(s)){
        const deadline=Date.parse(s.timer_deadline||'');
        const wait=Number.isFinite(deadline)?Math.max(140,deadline-v17Now()+140):500;
        v17FullTimer=setTimeout(run,Math.min(5000,wait));
        return;
      }
      if(v17FullBusy){v17FullAgain=true;return;}
      v17FullBusy=true;
      try{
        await loadAuction({quiet:true,onlyIfChanged:true});
      }catch(error){
        console.warn('V17 canonical refresh',reason,error);
      }finally{
        v17FullBusy=false;
        if(v17FullAgain){v17FullAgain=false;window.v11ScheduleAuctionRefresh('coalesced',180);}
      }
    };
    v17FullTimer=setTimeout(run,Math.max(120,Number(delay)||0));
  };

  const style=document.createElement('style');
  style.id='v17-live-performance-style';
  style.textContent=`
    /* Header Rosa: niente KPI duplicati, toggle Coda sempre visibile. */
    #view-auction .auction-team-roster-head .auction-v7-roster-metrics,
    #view-auction .auction-team-roster-head .v8rm,
    #view-auction .auction-team-roster-head .auction-roster-projected-summary{display:none!important}
    #view-auction .auction-team-roster-head{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:5px!important}
    #view-auction .auction-roster-head-actions{margin-left:auto!important;display:flex!important;align-items:center!important;justify-content:flex-end!important;gap:4px!important;min-width:max-content!important}
    #view-auction .auction-roster-queue-toggle{display:flex!important;visibility:visible!important;opacity:1!important;flex:0 0 auto!important}
    #view-auction .v17-suggestions-loading{min-height:32px!important;opacity:.72}
  `;
  document.head.appendChild(style);

  queueMicrotask(()=>{
    document.querySelectorAll('.auction-v7-roster-metrics,.v8rm,.auction-roster-projected-summary').forEach(x=>x.remove());
    if(v17IsLive())v17ScheduleSuggestions();
  });
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('</body> not found')
s = s.replace('</body>', runtime + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
