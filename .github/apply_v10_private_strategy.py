from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')

# Fix the two existing live credit/max displays: a live offer is not spent until award.
old_live="""      const ownLiveBid =
        liveSession.current_bidder_team_id === info.teamId
          ? Math.max(0, Number(liveSession.current_bid || 0))
          : 0;

      const liveRemainingCredits =
        Math.max(0, Number(info.remaining || 0) - ownLiveBid);

      const numericMaxBid =
        info.maxBid === null
        || info.maxBid === undefined
          ? null
          : Number(info.maxBid);

      const liveMaxBid =
        numericMaxBid === null
        || !Number.isFinite(numericMaxBid)
          ? null
          : Math.max(0, numericMaxBid - ownLiveBid);
"""
new_live="""      const ownLiveBid =
        liveSession.current_bidder_team_id === info.teamId
          ? Math.max(0, Number(liveSession.current_bid || 0))
          : 0;

      /* Un'offerta live non viene scalata dai crediti finché non è aggiudicata. */
      const liveRemainingCredits =
        Math.max(0, Number(info.remaining || 0));

      const genericMaxBid =
        Math.max(
          0,
          Number(info.remaining || 0)
          - Math.max(
              0,
              Number(info.rosterMin || 0)
              - Number(info.rosterCount ?? info.assignments?.length ?? 0)
              - 1
            )
        );

      const numericMaxBid =
        info.maxBid === null
        || info.maxBid === undefined
        || info.maxBid === ''
        || !Number.isFinite(Number(info.maxBid))
          ? genericMaxBid
          : Number(info.maxBid);

      /* MAX è l'offerta totale consentita, non il margine ancora rilanciabile. */
      const liveMaxBid =
        Math.max(0, numericMaxBid);
"""
if old_live not in s:
    raise SystemExit('live credit/max block not found')
s=s.replace(old_live,new_live)

old_dynamic="""      const ownBid =
        s.current_bidder_team_id === info.teamId
          ? Math.max(0, Number(s.current_bid || 0))
          : 0;

      const credits =
        Math.max(0, Number(info.remaining || 0) - ownBid);

      const baseMax =
        info.maxBid === null
        || info.maxBid === undefined
          ? null
          : Number(info.maxBid);

      const max =
        baseMax === null
        || !Number.isFinite(baseMax)
          ? null
          : Math.max(0, baseMax - ownBid);
"""
new_dynamic="""      const ownBid =
        s.current_bidder_team_id === info.teamId
          ? Math.max(0, Number(s.current_bid || 0))
          : 0;

      const credits =
        Math.max(0, Number(info.remaining || 0));

      const genericMax =
        Math.max(
          0,
          Number(info.remaining || 0)
          - Math.max(
              0,
              Number(info.rosterMin || 0)
              - Number(info.rosterCount ?? info.assignments?.length ?? 0)
              - 1
            )
        );

      const baseMax =
        info.maxBid === null
        || info.maxBid === undefined
        || info.maxBid === ''
        || !Number.isFinite(Number(info.maxBid))
          ? genericMax
          : Number(info.maxBid);

      const max =
        Math.max(0, baseMax);
"""
if old_dynamic not in s:
    raise SystemExit('dynamic credit/max block not found')
s=s.replace(old_dynamic,new_dynamic)

# Final runtime layer: access policy, private index, index-price border and PFC-PMA row heatmap.
marker='id="v10-private-strategy-runtime"'
if marker in s:
    raise SystemExit('v10 runtime already present')

runtime=r'''
<script id="v10-private-strategy-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V10_PRIVATE_STRATEGY__) return;
  window.__FANTA_V10_PRIVATE_STRATEGY__=1;

  state.v10StrategicAccess = state.v10StrategicAccess || null;
  state.v10StrategicAccessLeague = state.v10StrategicAccessLeague || '';
  state.v10StrategicAccessBusy = false;

  const v10Clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const v10Username=()=>String(
    state.dashboard?.currentUser?.username
    || state.session?.user?.username
    || ''
  ).trim().toLowerCase();
  const v10IsIndexOwner=()=>v10Username()==='emanuelesordo';
  const v10StrategicAllowed=()=>state.v10StrategicAccess?.allowed===true;

  function v10GenericMaxBid(info){
    if(!info) return null;
    const remaining=Math.max(0,Number(info.remaining||0));
    const rosterMin=Math.max(0,Number(info.rosterMin||0));
    const rosterCount=Math.max(0,Number(info.rosterCount??info.assignments?.length??0));
    return Math.max(0,remaining-Math.max(0,rosterMin-rosterCount-1));
  }

  /* Unifica la sorgente MAX della squadra propria con quella delle altre card. */
  if(typeof auctionMyTeamDashboardData==='function'){
    const oldInfo=auctionMyTeamDashboardData;
    auctionMyTeamDashboardData=function(...args){
      const info=oldInfo(...args);
      if(!info) return info;
      const raw=info.maxBid;
      if(raw===null||raw===undefined||raw===''||!Number.isFinite(Number(raw))){
        info.maxBid=v10GenericMaxBid(info);
      }
      return info;
    };
  }

  async function v10LoadStrategicAccess(force=false){
    const leagueId=state.selectedLeague?.id||'';
    if(!leagueId){state.v10StrategicAccess=null;state.v10StrategicAccessLeague='';v10ApplyAccessUi();return null;}
    if(!force&&state.v10StrategicAccessLeague===leagueId&&state.v10StrategicAccess) return state.v10StrategicAccess;
    if(state.v10StrategicAccessBusy) return state.v10StrategicAccess;
    state.v10StrategicAccessBusy=true;
    try{
      const res=await api(ENDPOINTS.strategy,{action:'getAccess'},{quiet:true});
      if(res?.access){
        state.v10StrategicAccess=res.access;
        state.v10StrategicAccessLeague=leagueId;
      }else{
        state.v10StrategicAccess={mode:'league_admin_only',allowed:false,canConfigure:false};
        state.v10StrategicAccessLeague=leagueId;
      }
    }catch(e){
      console.warn('Strategic access',e);
      state.v10StrategicAccess={mode:'league_admin_only',allowed:false,canConfigure:false};
      state.v10StrategicAccessLeague=leagueId;
    }finally{
      state.v10StrategicAccessBusy=false;
      v10ApplyAccessUi();
    }
    return state.v10StrategicAccess;
  }

  function v10ApplyAccessUi(){
    const allowed=v10StrategicAllowed();
    const owner=v10IsIndexOwner();
    document.body.classList.toggle('v10-strategy-allowed',allowed);
    document.body.classList.toggle('v10-strategy-disabled',!allowed);
    document.body.classList.toggle('v10-index-owner',owner);
    const nav=document.querySelector('.nav-btn[data-route="strategy"]');
    if(nav) nav.hidden=!allowed;
    if(state.view==='strategy'&&!allowed&&state.v10StrategicAccess){
      if(location.hash!=='#/setup') location.hash='#/home';
    }
    v10MountStrategyAccessSetup();
    v10PatchPrivateVisuals();
  }

  function v10MountStrategyAccessSetup(){
    const form=document.getElementById('setup-form');
    if(!form||!state.v10StrategicAccess) return;
    let box=document.getElementById('v10-strategy-access-setup');
    if(!box){
      box=document.createElement('section');
      box.id='v10-strategy-access-setup';
      box.className='panel full';
      form.appendChild(box);
    }
    const access=state.v10StrategicAccess;
    const can=access.canConfigure===true;
    const mode=access.mode||'league_admin_only';
    box.innerHTML=`
      <div class="panel-title"><div><h2>Visibilità Consulente Strategico</h2><p>Controlla insieme Suggeritore live, Centro Strategico e Statistiche.</p></div></div>
      <div class="form-grid">
        <label>Accesso
          <select id="v10-strategy-access-mode" ${can?'':'disabled'}>
            <option value="all_presidents">Tutti i presidenti</option>
            <option value="league_admin_only">Solo Presidente/Admin lega</option>
            <option value="none">Nessuno</option>
          </select>
        </label>
        <div style="display:flex;align-items:end"><button id="v10-strategy-access-save" type="button" ${can?'':'disabled'}>APPLICA</button></div>
      </div>
      <small class="soft">Preferiti, strategia e suggerimenti restano privati per ciascun account. L'Indice personale di emanuelesordo è indipendente da questa impostazione.</small>`;
    const select=box.querySelector('#v10-strategy-access-mode');
    if(select) select.value=mode;
    box.querySelector('#v10-strategy-access-save')?.addEventListener('click',async e=>{
      const button=e.currentTarget;
      button.disabled=true;
      try{
        const res=await api(ENDPOINTS.strategy,{action:'saveAccess',mode:select?.value||'league_admin_only'},{quiet:true});
        if(res?.access){
          state.v10StrategicAccess=res.access;
          msg('Visibilità strategica aggiornata.','success');
          v10ApplyAccessUi();
          if(state.view==='auction'&&state.auction?.auctionSession?.status==='live') renderAuctionLive();
        }
      }catch(err){msg(err.message||'Errore salvataggio visibilità strategica.','error')}
      finally{button.disabled=false;}
    });
  }

  /* Fail-closed: il suggeritore non viene renderizzato finché getAccess non lo abilita. */
  if(typeof renderAuctionSuggestedCalls==='function'){
    const oldSuggested=renderAuctionSuggestedCalls;
    renderAuctionSuggestedCalls=function(...args){
      return v10StrategicAllowed()?oldSuggested(...args):'';
    };
  }

  function v10PriceHue(price,threshold){
    const ratio=threshold>0?price/threshold:1;
    if(ratio<=1){
      const t=v10Clamp((1-ratio)/.35,0,1);
      return 48+82*t; // soglia gialla -> verde
    }
    const t=v10Clamp((ratio-1)/.35,0,1);
    return 48*(1-t); // soglia gialla -> rosso
  }

  function v10PatchCalledPlayer(){
    const nodes=document.querySelectorAll('.auction-command-player');
    nodes.forEach(n=>{n.classList.remove('v10-index-price-card');n.style.removeProperty('--v10-index-hue');n.style.removeProperty('--v10-index-glow')});
    if(!v10IsIndexOwner()||state.view!=='auction') return;
    const player=state.auction?.currentPlayer;
    const session=state.auction?.auctionSession;
    if(!player||!session?.current_player_id||typeof strategicThresholdPrice!=='function') return;
    const threshold=Number(strategicThresholdPrice(player));
    if(!Number.isFinite(threshold)||threshold<=0) return;
    const current=Math.max(1,Number(session.current_bid||1));
    const hue=v10PriceHue(current,threshold);
    const glow=.18+.20*v10Clamp(Math.abs(current-threshold)/Math.max(1,threshold),0,1);
    nodes.forEach(n=>{
      n.classList.add('v10-index-price-card');
      n.style.setProperty('--v10-index-hue',String(hue.toFixed(1)));
      n.style.setProperty('--v10-index-glow',String(glow.toFixed(2)));
      n.dataset.indexThreshold=String(threshold);
      n.dataset.indexPrice=String(current);
    });
  }

  function v10DeltaHue(player){
    const pfc=Number(player?.pfc||0),pma=Number(player?.pma||0);
    const delta=Number.isFinite(Number(player?.pfc_pma_delta))?Number(player.pfc_pma_delta):(pfc-pma);
    const scale=Math.max(4,(Math.abs(pfc)+Math.abs(pma))*.18);
    const x=v10Clamp(delta/scale,-1,1);
    const hue=x>=0?48+(132-48)*x:48*(1+x);
    const alpha=.075+.115*Math.abs(x);
    return{delta,hue,alpha};
  }

  function v10PatchFreeRows(){
    const rows=document.querySelectorAll('.auction-free-fixed tr[data-player-id]');
    rows.forEach(r=>{r.classList.remove('v10-private-delta-row');r.style.removeProperty('--v10-delta-hue');r.style.removeProperty('--v10-delta-alpha');delete r.dataset.pfcPmaDelta;});
    if(!v10IsIndexOwner()||state.view!=='auction') return;
    const by=new Map((state.auction?.callCandidates||[]).map(p=>[String(p.id),p]));
    rows.forEach(row=>{
      const player=by.get(String(row.dataset.playerId||''));
      if(!player) return;
      const c=v10DeltaHue(player);
      row.classList.add('v10-private-delta-row');
      row.style.setProperty('--v10-delta-hue',String(c.hue.toFixed(1)));
      row.style.setProperty('--v10-delta-alpha',String(c.alpha.toFixed(3)));
      row.dataset.pfcPmaDelta=String(c.delta);
    });
  }

  function v10PatchPrivateVisuals(){
    document.body.classList.toggle('v10-index-owner',v10IsIndexOwner());
    v10PatchCalledPlayer();
    v10PatchFreeRows();
  }

  /* Caricamento accesso agganciato alle viste che lo usano. */
  if(typeof loadSetup==='function'){
    const oldLoadSetup=loadSetup;
    loadSetup=async function(...args){const r=await oldLoadSetup(...args);await v10LoadStrategicAccess();v10MountStrategyAccessSetup();return r;};
  }
  if(typeof loadAuction==='function'){
    const oldLoadAuction=loadAuction;
    loadAuction=async function(...args){
      const r=await oldLoadAuction(...args);
      await v10LoadStrategicAccess();
      if(state.auction?.auctionSession?.status==='live') renderAuctionLive();
      v10PatchPrivateVisuals();
      return r;
    };
  }
  if(typeof renderAuctionLive==='function'){
    const oldRenderAuctionLive=renderAuctionLive;
    renderAuctionLive=function(...args){const r=oldRenderAuctionLive(...args);queueMicrotask(v10PatchPrivateVisuals);return r;};
  }

  window.addEventListener('hashchange',()=>{void v10LoadStrategicAccess().then(v10ApplyAccessUi)});
  const root=document.getElementById('auction-root');
  if(root){
    let scheduled=false;
    new MutationObserver(()=>{
      if(scheduled)return;
      scheduled=true;
      requestAnimationFrame(()=>{scheduled=false;v10PatchPrivateVisuals()});
    }).observe(root,{childList:true,subtree:true});
  }

  const style=document.createElement('style');
  style.id='v10-private-strategy-style';
  style.textContent=`
    body:not(.v10-index-owner) #view-list .auction-player-col-supreme,
    body:not(.v10-index-owner) #view-auction .auction-player-col-supreme,
    body:not(.v10-index-owner) #view-auction [data-auction-column="supreme"]{display:none!important}
    body.v10-strategy-disabled #view-auction .auction-free-suggestions,
    body.v10-strategy-disabled #view-auction .v8rm,
    body.v10-strategy-disabled #view-auction .v8lp,
    body.v10-strategy-disabled #view-auction .auction-v7-live-price{display:none!important}
    body.v10-index-owner #view-auction .auction-command-player.v10-index-price-card{
      border:2px solid hsl(var(--v10-index-hue) 86% 53%)!important;
      box-shadow:0 0 0 1px hsl(var(--v10-index-hue) 86% 53% / .30),0 0 14px hsl(var(--v10-index-hue) 86% 53% / var(--v10-index-glow))!important;
      transition:border-color .22s ease,box-shadow .22s ease!important
    }
    body.v10-index-owner #view-auction .auction-free-fixed tr.v10-private-delta-row{
      background:linear-gradient(90deg,hsl(var(--v10-delta-hue) 76% 48% / var(--v10-delta-alpha)),transparent 78%)!important;
      box-shadow:inset 3px 0 0 hsl(var(--v10-delta-hue) 78% 50% / .78)!important;
      transition:background .18s ease,box-shadow .18s ease!important
    }
    body.v10-index-owner #view-auction .auction-free-fixed tr.v10-private-delta-row:hover{
      background:linear-gradient(90deg,hsl(var(--v10-delta-hue) 80% 52% / calc(var(--v10-delta-alpha) + .06)),rgba(16,54,99,.36) 85%)!important
    }
  `;
  document.head.appendChild(style);

  void v10LoadStrategicAccess(true).then(v10ApplyAccessUi);
})();
</script>
'''

if '</body>' not in s:
    raise SystemExit('body close not found')
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
