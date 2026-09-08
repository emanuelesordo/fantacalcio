from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V45 · SINGLE PLAYER AUCTION
# - Setup toggle persisted through single-player-api
# - no nomination advancement / no bids (server-enforced)
# - select player + operational team + price -> direct assignment
# - canonical reload updates rosters, credits and free agents
# ==========================================================

require('id="view-setup"' in text and 'id="setup-form"' in text,
        'Setup view/form not found')
require('id="v34-market-strategy-runtime"' in text,
        'V34 auction runtime not found')

# Remove a previous V45 standalone style/runtime when re-running.
text = re.sub(
    r'\s*<style id="v45-single-player-style">.*?</style>\s*',
    '\n',
    text,
    count=1,
    flags=re.S,
)
text = re.sub(
    r'\s*<script id="v45-single-player-runtime">.*?</script>\s*',
    '\n',
    text,
    count=1,
    flags=re.S,
)

# ----------------------------------------------------------
# 1) Reuse the established player/team/price controls from V43,
#    but route SINGLE PLAYER through the direct backend endpoint.
# ----------------------------------------------------------
runtime_match = re.search(
    r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)',
    text,
    re.S,
)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

# canDirectAward43: Single Player is a first-class direct-award condition,
# independent from timer/manual legacy mode.
runtime, n = re.subn(
    r'(return Boolean\(\s*)timerInactive43\(\)(\s*&&\s*s\?\.id)',
    r'\1(window.v45SinglePlayerActive?.()===true||timerInactive43())\2',
    runtime,
    count=1,
    flags=re.S,
)
require(n == 1 or 'window.v45SinglePlayerActive?.()===true||timerInactive43()' in runtime,
        'V43 canDirectAward hook not patched')

# mountDirectAward43: show ASSEGNA in Single Player even with normal timers.
old_mount = (
    "    const inactive=timerInactive43(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43(),price=directAwardPrice43();\n"
    "    b.hidden=!inactive;\n"
    "    b.disabled=!canDirectAward43();"
)
new_mount = (
    "    const single=window.v45SinglePlayerActive?.()===true,inactive=single||timerInactive43(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43(),price=directAwardPrice43();\n"
    "    b.textContent=single?'ASSEGNA':'ASSEGNA DIRETTO';\n"
    "    b.hidden=!inactive;\n"
    "    b.disabled=!canDirectAward43();"
)
if old_mount in runtime:
    runtime = runtime.replace(old_mount, new_mount, 1)
require("b.textContent=single?'ASSEGNA':'ASSEGNA DIRETTO';" in runtime,
        'V43 direct button Single Player label missing')

# directAward43: before the legacy call->bid->award sequence, delegate to
# single-player-api. This path never creates an auction bid.
sp_branch = r'''
    if(window.v45SinglePlayerActive?.()===true){
      if(typeof window.v45SinglePlayerAssign!=='function'){
        if(typeof msg==='function')msg('Modulo Single Player non disponibile.','error');
        return;
      }
      await window.v45SinglePlayerAssign(button,{session:s,player:p,team,price});
      return;
    }
'''
if 'window.v45SinglePlayerAssign(button,{session:s,player:p,team,price})' not in runtime:
    anchor = (
        "    const s=session34(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43(),price=directAwardPrice43();\n"
        "    if(!s?.id||!p||!team)return;\n"
    )
    require(anchor in runtime, 'V43 directAward43 anchor missing')
    runtime = runtime.replace(anchor, anchor + sp_branch, 1)

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]

# ----------------------------------------------------------
# 2) Style: Setup card + auction mode visual state.
# ----------------------------------------------------------
v45_style = r'''
<style id="v45-single-player-style">
  #single-player-setup-v45{
    grid-column:1/-1;
  }
  #single-player-setup-v45 .v45-single-line{
    display:grid;
    grid-template-columns:minmax(0,1fr) auto;
    align-items:center;
    gap:12px;
  }
  #single-player-setup-v45 .v45-single-copy strong{
    display:block;
    font-size:12px;
    color:var(--text);
    margin-bottom:3px;
  }
  #single-player-setup-v45 .v45-single-copy small{
    display:block;
    color:var(--soft);
    font-size:9px;
    line-height:1.35;
  }
  #single-player-setup-v45 .v45-single-toggle{
    display:flex;
    align-items:center;
    gap:7px;
    min-width:max-content;
    color:var(--text);
    font-weight:850;
  }
  #single-player-setup-v45 .v45-single-state{
    margin-top:7px;
    padding-top:7px;
    border-top:1px solid var(--line);
    color:var(--soft);
    font-size:9px;
  }
  #single-player-setup-v45[data-enabled="true"]{
    border-color:rgba(70,210,150,.55);
    box-shadow:inset 0 0 0 1px rgba(70,210,150,.08);
  }
  body.v45-single-player #view-auction #auction-call-confirm{
    display:none!important;
  }
  body.v45-single-player #view-auction #auction-direct-award-v43{
    display:inline-flex!important;
    align-items:center!important;
    justify-content:center!important;
    background:var(--good,#1f6c58)!important;
    border-color:rgba(80,230,160,.7)!important;
    color:#fff!important;
    font-size:9px!important;
    min-width:76px!important;
  }
  body.v45-single-player #view-auction :is(
    #auction-hold,
    #live-hold-button,
    #live-president-controls,
    #auctioneer-team-buttons,
    [data-auction-bid-controls],
    .auction-bid-controls,
    .auction-quick-bids,
    .auction-bid-quick-actions
  ){
    display:none!important;
  }
  #v45-single-player-badge{
    display:none;
  }
  body.v45-single-player #v45-single-player-badge{
    display:inline-flex;
    align-items:center;
    gap:5px;
    min-height:23px;
    padding:3px 8px;
    border:1px solid rgba(80,230,160,.55);
    border-radius:8px;
    background:rgba(31,108,88,.28);
    color:#caffeb;
    font-size:8px;
    font-weight:950;
    letter-spacing:.04em;
    white-space:nowrap;
  }
  @media(max-width:700px){
    #single-player-setup-v45 .v45-single-line{grid-template-columns:1fr}
    #single-player-setup-v45 .v45-single-toggle{justify-content:flex-start}
  }
</style>
'''
require('</head>' in text, 'closing head missing')
text = text.replace('</head>', v45_style + '\n</head>', 1)

# ----------------------------------------------------------
# 3) Runtime: Setup persistence + direct assignment + refresh.
# ----------------------------------------------------------
v45_runtime = r'''
<script id="v45-single-player-runtime">
(() => {
  'use strict';
  if(window.__FANTA_V45_SINGLE_PLAYER__)return;
  window.__FANTA_V45_SINGLE_PLAYER__=1;

  const API=`${SUPABASE_URL}/functions/v1/single-player-api`;
  const local={mode:null,loading:false,lastFetch:0,saving:false};

  function auctionSession45(){
    try{
      if(typeof auctionSession==='function')return auctionSession();
    }catch{}
    return state.auction?.auctionSession||null;
  }

  window.v45SinglePlayerActive=function(){
    const s=auctionSession45();
    if(s?.setup_snapshot?.single_player_mode===true)return true;
    if(s)return false;
    return local.mode?.enabled===true;
  };

  function applyAuctionModeClass45(){
    const active=window.v45SinglePlayerActive()===true;
    document.body.classList.toggle('v45-single-player',active&&state.view==='auction');
    if(active&&state.view==='auction')mountAuctionBadge45();
  }

  async function fetchMode45(force=false){
    if(local.loading)return local.mode;
    if(!force&&local.mode&&Date.now()-local.lastFetch<15000)return local.mode;
    if(!state.session?.token||!state.selectedLeague?.id)return null;
    local.loading=true;
    try{
      const result=await api(API,{action:'getMode'},{quiet:true});
      if(result?.ok===false)throw new Error(result.error||'Impossibile leggere la modalità Single Player.');
      local.mode=result||null;
      local.lastFetch=Date.now();
      return local.mode;
    }catch(error){
      console.warn('V45 get mode',error);
      return local.mode;
    }finally{
      local.loading=false;
      renderSetup45();
      applyAuctionModeClass45();
    }
  }

  function setupCard45(){
    let card=document.getElementById('single-player-setup-v45');
    if(card)return card;
    const form=document.getElementById('setup-form');
    if(!form)return null;
    card=document.createElement('section');
    card.id='single-player-setup-v45';
    card.className='panel full';
    card.innerHTML=`
      <div class="panel-title">
        <div>
          <h2>Modalità Single Player</h2>
          <p>Assegnazioni dirette senza rilanci.</p>
        </div>
      </div>
      <div class="v45-single-line">
        <div class="v45-single-copy">
          <strong>Gestione manuale dell’asta</strong>
          <small>Selezioni uno svincolato, la squadra e il prezzo. ASSEGNA aggiorna subito rosa, crediti e lista degli svincolati. In questa modalità i rilanci sono disabilitati anche lato server.</small>
        </div>
        <label class="v45-single-toggle">
          <input id="single-player-mode-v45" type="checkbox">
          <span>Attiva</span>
        </label>
      </div>
      <div class="v45-single-state" id="single-player-state-v45">Caricamento…</div>
    `;
    const firstFull=form.querySelector(':scope > .full');
    if(firstFull)form.insertBefore(card,firstFull);
    else form.appendChild(card);
    return card;
  }

  function renderSetup45(){
    if(state.view!=='setup'&&!location.hash.includes('/setup'))return;
    const card=setupCard45();
    if(!card)return;
    const input=card.querySelector('#single-player-mode-v45');
    const info=card.querySelector('#single-player-state-v45');
    const mode=local.mode;
    if(!mode){
      input.disabled=true;
      info.textContent='Caricamento modalità…';
      return;
    }
    input.checked=mode.enabled===true;
    input.disabled=local.saving||mode.canEdit!==true||mode.locked===true;
    card.dataset.enabled=String(mode.enabled===true);
    if(mode.locked){
      const active=mode.activeEnabled===true?'attiva':'non attiva';
      info.textContent=`Sessione d’asta aperta: la modalità della sessione è ${active}. Per cambiarla, chiudi o annulla prima la sessione.`;
    }else if(mode.canEdit!==true){
      info.textContent='Solo un Admin Lega può modificare questa impostazione.';
    }else{
      info.textContent=mode.enabled===true
        ? 'Single Player attivo per la prossima asta: nessun rilancio, solo assegnazioni dirette.'
        : 'Asta standard: chiamate e rilanci restano attivi.';
    }
  }

  async function saveSetupMode45(input){
    if(local.saving)return;
    const previous=local.mode?.enabled===true;
    const enabled=input.checked===true;
    local.saving=true;
    renderSetup45();
    try{
      const result=await api(API,{action:'setMode',enabled},{quiet:true});
      if(result?.ok===false)throw new Error(result.error||'Impossibile salvare la modalità Single Player.');
      local.mode={...(local.mode||{}),enabled:result.enabled===true,locked:false};
      local.lastFetch=Date.now();
      if(typeof msg==='function')msg(result.enabled?'Modalità Single Player attivata.':'Modalità Single Player disattivata.','success');
    }catch(error){
      if(local.mode)local.mode.enabled=previous;
      input.checked=previous;
      if(typeof msg==='function')msg(error.message||'Impossibile salvare la modalità Single Player.','error');
    }finally{
      local.saving=false;
      renderSetup45();
    }
  }

  function mountAuctionBadge45(){
    if(state.view!=='auction')return;
    let badge=document.getElementById('v45-single-player-badge');
    if(badge)return;
    const host=document.querySelector('#view-auction .auction-caller-controls')
      ||document.querySelector('#view-auction .auction-live-shell')
      ||document.querySelector('#view-auction .auction-root');
    if(!host)return;
    badge=document.createElement('span');
    badge.id='v45-single-player-badge';
    badge.textContent='SINGLE PLAYER · ASSEGNAZIONE DIRETTA';
    host.prepend(badge);
  }

  window.v45SinglePlayerAssign=async function(button,{session,player,team,price}){
    if(!session?.id||!player?.id||!team?.id)return;
    const teamLabel=typeof auctionTeamReference==='function'
      ? auctionTeamReference(team,team.name||'squadra')
      : (team.name||'squadra');
    const confirmed=typeof appConfirm==='function'
      ? await appConfirm(
          `${player.name||'Giocatore'} → ${teamLabel} per ${price} crediti?`,
          {title:'Assegnazione Single Player',confirmText:'ASSEGNA'}
        )
      : true;
    if(!confirmed)return;

    button.disabled=true;
    try{
      const result=await api(API,{
        action:'assignPlayer',
        sessionId:session.id,
        playerId:player.id,
        teamId:team.id,
        price
      });
      if(result?.ok===false)throw new Error(result.error||'Assegnazione non riuscita.');
      if(result?.state&&typeof applyAuctionHotState==='function'){
        applyAuctionHotState(result.state,{fromMutation:true});
      }
      state.auctionAdminPlayerId=null;
      state.auctionPersonalRosterFetchedAt=0;
      if(typeof msg==='function')msg(`${player.name||'Giocatore'} assegnato a ${teamLabel} per ${price}.`,'success');
      if(typeof loadAuction==='function'){
        await loadAuction({quiet:true,onlyIfChanged:false});
      }
      if(typeof window.loadMarket34==='function'){
        await window.loadMarket34(true,false);
      }
      if(typeof window.v11ScheduleAuctionRefresh==='function'){
        window.v11ScheduleAuctionRefresh('single-player-award',30);
      }
    }catch(error){
      if(typeof msg==='function')msg(error.message||'Assegnazione Single Player non riuscita.','error');
      if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(80);
    }finally{
      button.disabled=false;
      applyAuctionModeClass45();
      try{if(typeof patchAuctionTopSelection==='function')patchAuctionTopSelection()}catch{}
    }
  };

  document.addEventListener('change',event=>{
    const input=event.target.closest?.('#single-player-mode-v45');
    if(!input)return;
    void saveSetupMode45(input);
  });

  function tick45(){
    if(state.view==='setup'||location.hash.includes('/setup')){
      setupCard45();
      renderSetup45();
      void fetchMode45(false);
    }
    applyAuctionModeClass45();
  }

  window.addEventListener('hashchange',()=>{
    if(location.hash.includes('/setup'))void fetchMode45(true);
    queueMicrotask(tick45);
  });
  document.addEventListener('visibilitychange',()=>{
    if(!document.hidden)queueMicrotask(tick45);
  });

  setInterval(tick45,900);
  queueMicrotask(()=>{
    tick45();
    if(location.hash.includes('/setup'))void fetchMode45(true);
  });
})();
</script>
'''
require('</body>' in text, 'closing body missing')
text = text.replace('</body>', v45_runtime + '\n</body>', 1)

# ----------------------------------------------------------
# Regression checks.
# ----------------------------------------------------------
checks = {
    'setup toggle runtime': 'single-player-mode-v45' in text,
    'single player api': 'functions/v1/single-player-api' in text,
    'direct backend assignment': "action:'assignPlayer'" in text,
    'V43 delegates before bids': 'window.v45SinglePlayerAssign(button,{session:s,player:p,team,price})' in text,
    'button becomes ASSEGNA': "b.textContent=single?'ASSEGNA':'ASSEGNA DIRETTO';" in text,
    'standard call hidden in single mode': 'body.v45-single-player #view-auction #auction-call-confirm' in text,
    'canonical roster refresh': 'state.auctionPersonalRosterFetchedAt=0' in text and 'onlyIfChanged:false' in text,
}
for name, ok in checks.items():
    require(ok, 'V45 regression failed: ' + name)

require(text != original, 'V45 produced no changes')
path.write_text(text, encoding='utf-8')
print('V45 single player patch applied')
