from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v18-auction-controls-runtime' in s:
    raise SystemExit('V18 already applied')

# 1) Listone NOME: usa lo stesso fuzzy matcher dell'asta.
old="""    if(f.name&&!String(p?.name||'').toLowerCase().includes(String(f.name).trim().toLowerCase()))return false;"""
new="""    if(f.name){
      const q=String(f.name).trim();
      const similar=typeof playerSearchRank==='function'
        ? playerSearchRank(p,q,mode15())!==null
        : String(p?.name||'').toLowerCase().includes(q.toLowerCase());
      if(q&&!similar)return false;
    }"""
if old not in s:
    raise SystemExit('V15 fuzzy target not found')
s=s.replace(old,new,1)

# 2) Pausa: può essere richiesta soltanto con lotto attivo; dopo acquisto resta attiva.
old="""            <button
              id=\"auction-pause-cycle\"
              class=\"secondary\"
              type=\"button\"
            >
              ${
                s.pause_after_award
                  ? 'RIPRENDI ASTA'
                  : hasPlayer
                    ? 'PAUSA DOPO AGGIUD.'
                    : 'PAUSA ASTA'
              }
            </button>"""
new="""            <button
              id=\"auction-pause-cycle\"
              class=\"secondary\"
              type=\"button\"
              ${!s.pause_after_award && !hasPlayer ? 'disabled' : ''}
              title=\"${s.pause_after_award ? (hasPlayer ? 'Annulla la pausa programmata' : 'Riprende le chiamate') : 'La pausa scatterà solo dopo la conferma dell’acquisto corrente'}\"
            >
              ${
                s.pause_after_award
                  ? (hasPlayer ? 'ANNULLA PAUSA' : 'RIPRENDI ASTA')
                  : 'PAUSA DOPO ACQUISTO'
              }
            </button>"""
if old not in s:
    raise SystemExit('pause button target not found')
s=s.replace(old,new,1)

# Non disarmare la pausa prima dell'aggiudicazione: deve essere l'award a renderla effettiva.
old=re.compile(r"\s*/\* La conferma esplicita deve far partire il prossimo timer\. \*/\s*if \(session\.pause_after_award\) \{\s*await api\(\s*ENDPOINTS\.auction,\s*\{\s*action: 'setAuctionPause',\s*sessionId: session\.id,\s*paused: false\s*\}\s*\);\s*\}\s*",re.S)
s,n=old.subn("\n            /* Se PAUSA è programmata, awardPlayer la lascia attiva e blocca la chiamata successiva. */\n",s,count=1)
if n!=1:
    raise SystemExit(f'award pause target count={n}')

# 3) Sostituisci i dialoghi browser con helper in-app asincroni.
# Tutti i call-site correnti vivono in handler async; node --check del workflow verifica il vincolo.
s=re.sub(r'(?<![A-Za-z0-9_])confirm\(', 'await appConfirm(', s)
s=re.sub(r'(?<![A-Za-z0-9_])prompt\(', 'await appPrompt(', s)

runtime=r'''
<script id="v18-auction-controls-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V18_AUCTION__)return;
  window.__FANTA_V18_AUCTION__=1;

  /* =========================================================
     MODALI APPLICATIVE: niente confirm/prompt del browser
     ========================================================= */
  function ensureAppModal(){
    let d=document.getElementById('app-modal-dialog');
    if(d)return d;
    d=document.createElement('dialog');
    d.id='app-modal-dialog';
    d.className='app-modal-dialog';
    d.innerHTML=`<form method="dialog" class="app-modal-card">
      <header><strong id="app-modal-title">Conferma</strong><button type="button" id="app-modal-x" class="secondary" aria-label="Chiudi">×</button></header>
      <div id="app-modal-message" class="app-modal-message"></div>
      <input id="app-modal-input" class="app-modal-input" hidden>
      <footer><button type="button" id="app-modal-cancel" class="secondary">Annulla</button><button type="button" id="app-modal-ok">Conferma</button></footer>
    </form>`;
    document.body.appendChild(d);
    return d;
  }

  window.appConfirm=window.appConfirm||function(message,{title='Conferma',confirmText='Conferma',cancelText='Annulla',danger=false}={}){
    return new Promise(resolve=>{
      const d=ensureAppModal(),t=d.querySelector('#app-modal-title'),m=d.querySelector('#app-modal-message'),i=d.querySelector('#app-modal-input'),ok=d.querySelector('#app-modal-ok'),cancel=d.querySelector('#app-modal-cancel'),x=d.querySelector('#app-modal-x');
      t.textContent=title;m.textContent=String(message||'');i.hidden=true;ok.textContent=confirmText;cancel.textContent=cancelText;ok.className=danger?'danger':'';
      let done=false;const finish=v=>{if(done)return;done=true;try{d.close()}catch{}resolve(v)};
      ok.onclick=()=>finish(true);cancel.onclick=x.onclick=()=>finish(false);d.oncancel=e=>{e.preventDefault();finish(false)};
      d.showModal();requestAnimationFrame(()=>ok.focus({preventScroll:true}));
    });
  };

  window.appPrompt=window.appPrompt||function(message,value='',{title='Inserisci valore',confirmText='Conferma',cancelText='Annulla',placeholder=''}={}){
    return new Promise(resolve=>{
      const d=ensureAppModal(),t=d.querySelector('#app-modal-title'),m=d.querySelector('#app-modal-message'),i=d.querySelector('#app-modal-input'),ok=d.querySelector('#app-modal-ok'),cancel=d.querySelector('#app-modal-cancel'),x=d.querySelector('#app-modal-x');
      t.textContent=title;m.textContent=String(message||'');i.hidden=false;i.value=String(value??'');i.placeholder=placeholder;ok.textContent=confirmText;cancel.textContent=cancelText;ok.className='';
      let done=false;const finish=v=>{if(done)return;done=true;try{d.close()}catch{}resolve(v)};
      ok.onclick=()=>finish(i.value);cancel.onclick=x.onclick=()=>finish(null);d.oncancel=e=>{e.preventDefault();finish(null)};
      i.onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();finish(i.value)}};
      d.showModal();requestAnimationFrame(()=>{i.focus({preventScroll:true});i.select()});
    });
  };

  /* =========================================================
     DATI GIOCATORE: label + valore orizzontali
     ========================================================= */
  function patchCalledDetails(){
    const card=document.querySelector('.v14-called-details');
    if(!card)return;
    card.classList.add('v18-called-horizontal');
  }

  /* =========================================================
     HOLD: feedback locale immediato, poi persistenza server
     ========================================================= */
  document.addEventListener('click',async e=>{
    const btn=e.target.closest?.('#auction-hold');
    if(!btn)return;
    e.preventDefault();e.stopImmediatePropagation();
    const s=typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession;
    if(!s?.id)return;
    const previous={hold_active:s.hold_active,hold_remaining_seconds:s.hold_remaining_seconds,timer_deadline:s.timer_deadline,timer_expired_at:s.timer_expired_at};
    const next=!s.hold_active;
    if(next){
      const deadline=Date.parse(s.timer_deadline||'');
      const remaining=Number.isFinite(deadline)?Math.max(0,Math.ceil((deadline-Date.now()-Number(state.serverOffsetMs||0))/1000)):Math.max(0,Number(s.current_timer_seconds||0));
      s.hold_active=true;s.hold_remaining_seconds=remaining;s.timer_deadline=null;s.timer_expired_at=null;
      if(typeof renderAuctionTimer==='function')renderAuctionTimer();
      if(typeof patchAuctionLiveDynamic==='function')patchAuctionLiveDynamic();
    }
    btn.disabled=true;
    try{
      const response=await api(ENDPOINTS.auction,{action:'setHold',sessionId:s.id,hold:next});
      if(response?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(response.state,{fromMutation:true});
      else if(!next&&typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(20);
    }catch(error){
      Object.assign(s,previous);
      if(typeof renderAuctionLive==='function')renderAuctionLive();
      if(typeof msg==='function')msg(error.message,'error');
    }
  },true);

  /* =========================================================
     ASSEGNA TURNO: squadra operativa selezionata dal Banditore
     ========================================================= */
  const TURN_API=`${SUPABASE_URL}/functions/v1/auction-turn-api`;
  function mountAssignTurn(){
    const pass=document.getElementById('auction-pass-nomination');
    if(!pass||document.getElementById('auction-assign-nomination'))return;
    const s=typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession;
    const team=(state.auction?.teams||[]).find(t=>t.id===state.auctionAdminTeamId)||null;
    const b=document.createElement('button');
    b.id='auction-assign-nomination';b.type='button';b.className='secondary';
    b.disabled=Boolean(s?.current_player_id)||!state.auctionAdminTeamId||!(typeof auctionCallMode==='function'&&auctionCallMode());
    b.textContent='ASSEGNA TURNO';
    b.title=team?`Assegna il turno di chiamata a ${typeof auctionTeamReference==='function'?auctionTeamReference(team,team.name):team.name}`:'Seleziona prima una Squadra operativa';
    pass.insertAdjacentElement('afterend',b);
  }

  document.addEventListener('click',async e=>{
    const b=e.target.closest?.('#auction-assign-nomination');if(!b)return;
    e.preventDefault();e.stopImmediatePropagation();
    const s=typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession,teamId=state.auctionAdminTeamId;
    const team=(state.auction?.teams||[]).find(t=>t.id===teamId)||null;
    if(!s?.id||!teamId||s.current_player_id)return;
    const name=typeof auctionTeamReference==='function'?auctionTeamReference(team,team?.name||'squadra'):team?.name||'squadra';
    if(!await appConfirm(`Assegnare il turno di chiamata a ${name}?`,{title:'Assegna turno',confirmText:'Assegna'}))return;
    b.disabled=true;
    try{
      const r=await api(TURN_API,{sessionId:s.id,teamId},{quiet:true});
      if(r?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(r.state,{fromMutation:true});
      else {s.current_nomination_team_id=teamId;if(typeof renderAuctionLive==='function')renderAuctionLive();}
      if(typeof msg==='function')msg(`Turno assegnato a ${name}.`,'success');
    }catch(error){if(typeof msg==='function')msg(error.message,'error')}
  },true);

  /* =========================================================
     CHIAMA accanto a NOME | PREZZO nel blocco superiore
     ========================================================= */
  function moveCallButtonTop(){
    const button=document.getElementById('auction-call-confirm');
    const top=document.querySelector('#view-auction .auction-caller-controls');
    if(button&&top&&button.parentElement!==top){button.classList.add('v18-top-call');top.appendChild(button);}
  }

  /* =========================================================
     FILTRI PER COLONNA NELLA LISTA SVINCOLATI
     ========================================================= */
  const NUM={
    pfc:{label:'PFC',step:1,get:p=>Number(p?.pfc)},
    fm:{label:'FM',step:.01,get:p=>Number(typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):p?.expected_fantasy_avg)},
    pma:{label:'PMA',step:1,get:p=>Number(p?.pma)},
    index:{label:'Indice',step:1,get:p=>Number(typeof strategicValueIndex==='function'?strategicValueIndex(p):0)}
  };
  state.v18AuctionFilters=state.v18AuctionFilters||{name:'',badge:'all',ranges:{},key:''};
  const finite=v=>Number.isFinite(Number(v))?Number(v):null;
  const fmt=(v,step=1)=>step<1?Number(v).toFixed(step<=.01?2:1).replace('.',','):String(Math.round(Number(v)));
  function bounds(key,players){const d=NUM[key],vals=players.map(d.get).filter(Number.isFinite);let min=vals.length?Math.min(...vals):0,max=vals.length?Math.max(...vals):d.step;if(d.step>=1){min=Math.floor(min);max=Math.ceil(max)}else{min=Math.floor(min/d.step)*d.step;max=Math.ceil(max/d.step)*d.step}if(min===max)max=min+d.step;return{min,max,lo:min,hi:max,step:d.step}}
  function ensureRanges(){
    const ps=state.auction?.callCandidates||[],k=`${state.auction?.auctionSession?.id||''}|${ps.length}|${ps.slice(0,5).map(p=>p.id).join(',')}`;
    if(state.v18AuctionFilters.key===k&&Object.keys(state.v18AuctionFilters.ranges||{}).length)return;
    const old=state.v18AuctionFilters.ranges||{},next={};
    Object.keys(NUM).forEach(x=>{const b=bounds(x,ps),o=old[x];next[x]={...b,lo:o?Math.max(b.min,Math.min(b.max,o.lo)):b.min,hi:o?Math.max(b.min,Math.min(b.max,o.hi)):b.max};if(next[x].lo>next[x].hi){next[x].lo=b.min;next[x].hi=b.max}});
    state.v18AuctionFilters.ranges=next;state.v18AuctionFilters.key=k;
  }
  function rangeHtml(key){const r=state.v18AuctionFilters.ranges[key],d=NUM[key];if(!r)return'';const full=r.lo===r.min&&r.hi===r.max,label=full?'tutto':`${fmt(r.lo,d.step)}–${fmt(r.hi,d.step)}`;return `<div class="v18-range" data-v18-box="${key}"><button type="button" class="v18-range-toggle" data-v18-toggle="${key}">${label}<i>⌄</i></button><div class="v18-range-pop" data-v18-pop="${key}" hidden><div class="v18-range-values"><b data-v18-lo="${key}">${fmt(r.lo,d.step)}</b><span>${d.label}</span><b data-v18-hi="${key}">${fmt(r.hi,d.step)}</b></div><div class="v18-dual"><div class="base"></div><div class="fill" data-v18-fill="${key}"></div><input type="range" data-v18-range="${key}" data-bound="lo" min="${r.min}" max="${r.max}" step="${r.step}" value="${r.lo}"><input type="range" data-v18-range="${key}" data-bound="hi" min="${r.min}" max="${r.max}" step="${r.step}" value="${r.hi}"></div><div class="ends"><small>${fmt(r.min,d.step)}</small><button type="button" data-v18-reset="${key}">azzera</button><small>${fmt(r.max,d.step)}</small></div></div></div>`}
  function updateRangeVisual(key){const r=state.v18AuctionFilters.ranges[key],d=NUM[key];if(!r)return;const span=Math.max(r.step,r.max-r.min),a=(r.lo-r.min)/span*100,b=(r.hi-r.min)/span*100;document.querySelectorAll(`[data-v18-fill="${key}"]`).forEach(x=>{x.style.left=`${a}%`;x.style.width=`${Math.max(0,b-a)}%`});document.querySelectorAll(`[data-v18-lo="${key}"]`).forEach(x=>x.textContent=fmt(r.lo,d.step));document.querySelectorAll(`[data-v18-hi="${key}"]`).forEach(x=>x.textContent=fmt(r.hi,d.step));const full=r.lo===r.min&&r.hi===r.max,label=full?'tutto':`${fmt(r.lo,d.step)}–${fmt(r.hi,d.step)}`;document.querySelectorAll(`[data-v18-toggle="${key}"]`).forEach(x=>{x.childNodes[0].nodeValue=label})}
  function closeRange(except=''){document.querySelectorAll('[data-v18-pop]').forEach(x=>{if(x.dataset.v18Pop!==except)x.hidden=true})}
  function matchPlayer(p){
    const f=state.v18AuctionFilters,q=String(f.name||'').trim();
    if(q){const ok=typeof playerSearchRank==='function'?playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null:String(p?.name||'').toLowerCase().includes(q.toLowerCase());if(!ok)return false}
    if(f.badge&&f.badge!=='all'&&typeof matchesFlag==='function'&&!matchesFlag(p,f.badge))return false;
    for(const key of Object.keys(NUM)){const r=f.ranges[key],v=NUM[key].get(p);if(!r||!Number.isFinite(v)||v<r.lo-1e-9||v>r.hi+1e-9)return false}
    return true;
  }
  function applyAuctionColumnFilters(){
    const body=document.getElementById('auction-player-body');if(!body)return;
    const by=new Map((state.auction?.callCandidates||[]).map(p=>[String(p.id),p]));
    body.querySelectorAll('tr[data-player-id]').forEach(row=>{const p=by.get(String(row.dataset.playerId));row.hidden=Boolean(p&&!matchPlayer(p))});
  }
  function mountAuctionColumnFilters(){
    const box=document.querySelector('#view-auction .auction-free-fixed');if(!box)return;
    box.querySelector('.drawer-filters')?.setAttribute('hidden','');ensureRanges();
    const thead=box.querySelector('.player-table thead');if(!thead)return;
    thead.querySelector('.v18-auction-filter-row')?.remove();
    const row=document.createElement('tr');row.className='v18-auction-filter-row';row.innerHTML=`<th><span class="v18-role-filter-note">ruoli sopra</span></th><th><input type="search" class="v18-name-filter" value="${String(state.v18AuctionFilters.name||'').replace(/"/g,'&quot;')}" placeholder="nome simile…" autocomplete="off"></th><th><select class="v18-badge-filter"><option value="all">tutti</option><option value="market">mercato</option><option value="injury">indisp.</option><option value="new">nuovo</option><option value="penalties">rigori</option><option value="free_kicks">piazzati</option></select></th><th>${rangeHtml('pfc')}</th><th>${rangeHtml('fm')}</th><th>${rangeHtml('pma')}</th><th>${rangeHtml('index')}</th><th></th>`;
    thead.appendChild(row);row.querySelector('.v18-badge-filter').value=state.v18AuctionFilters.badge||'all';Object.keys(NUM).forEach(updateRangeVisual);applyAuctionColumnFilters();
  }

  document.addEventListener('input',e=>{
    const name=e.target.closest?.('.v18-name-filter');if(name){e.stopImmediatePropagation();state.v18AuctionFilters.name=name.value;applyAuctionColumnFilters();return}
    const range=e.target.closest?.('[data-v18-range]');if(range){e.stopImmediatePropagation();const key=range.dataset.v18Range,bound=range.dataset.bound,r=state.v18AuctionFilters.ranges[key];let v=Number(range.value);if(bound==='lo'){r.lo=Math.min(v,r.hi);range.value=r.lo}else{r.hi=Math.max(v,r.lo);range.value=r.hi}updateRangeVisual(key);applyAuctionColumnFilters()}
  },true);
  document.addEventListener('change',e=>{const badge=e.target.closest?.('.v18-badge-filter');if(badge){e.stopImmediatePropagation();state.v18AuctionFilters.badge=badge.value;applyAuctionColumnFilters()}},true);
  document.addEventListener('click',e=>{
    const toggle=e.target.closest?.('[data-v18-toggle]');if(toggle){e.preventDefault();e.stopPropagation();const key=toggle.dataset.v18Toggle,pop=document.querySelector(`[data-v18-pop="${key}"]`),open=pop?.hidden!==false;closeRange(open?key:'');if(pop)pop.hidden=!open;updateRangeVisual(key);return}
    const reset=e.target.closest?.('[data-v18-reset]');if(reset){e.preventDefault();e.stopPropagation();const key=reset.dataset.v18Reset,r=state.v18AuctionFilters.ranges[key];r.lo=r.min;r.hi=r.max;document.querySelectorAll(`[data-v18-range="${key}"][data-bound="lo"]`).forEach(x=>x.value=r.lo);document.querySelectorAll(`[data-v18-range="${key}"][data-bound="hi"]`).forEach(x=>x.value=r.hi);updateRangeVisual(key);applyAuctionColumnFilters();return}
    if(!e.target.closest?.('.v18-range'))closeRange('');
  });

  if(typeof renderAuctionPlayers==='function'){
    const old=renderAuctionPlayers;renderAuctionPlayers=function(...a){const r=old(...a);mountAuctionColumnFilters();return r};
  }
  if(typeof renderAuctionLive==='function'){
    const old=renderAuctionLive;renderAuctionLive=function(...a){const r=old(...a);queueMicrotask(()=>{patchCalledDetails();mountAssignTurn();moveCallButtonTop();mountAuctionColumnFilters()});return r};
  }

  /* Squadra operativa cambiata: aggiorna subito abilitazione/tooltip ASSEGNA TURNO. */
  document.addEventListener('click',e=>{if(e.target.closest?.('[data-admin-team]'))queueMicrotask(mountAssignTurn)},true);

  const style=document.createElement('style');style.id='v18-auction-controls-style';style.textContent=`
    .app-modal-dialog{width:min(480px,calc(100vw - 24px));padding:0;border:1px solid rgba(96,158,222,.46);border-radius:12px;background:#081d32;color:var(--text);box-shadow:0 22px 70px rgba(0,0,0,.58)}
    .app-modal-dialog::backdrop{background:rgba(2,8,16,.7);backdrop-filter:blur(5px)}
    .app-modal-card{display:grid;gap:10px;padding:12px}.app-modal-card header,.app-modal-card footer{display:flex;align-items:center;gap:6px}.app-modal-card header{justify-content:space-between}.app-modal-card header strong{font-size:15px}.app-modal-card header button{width:28px;min-width:28px;height:28px;min-height:28px;padding:0}.app-modal-card footer{justify-content:flex-end}.app-modal-message{font-size:11px;line-height:1.45;color:#d7e5f5;white-space:pre-wrap}.app-modal-input{font-size:12px!important}

    body.v10-index-owner #view-auction .v14-called-details.v18-called-horizontal .v14-called-grid>span{min-height:34px!important;padding:4px 6px!important;display:flex!important;flex-direction:row!important;align-items:center!important;justify-content:space-between!important;gap:6px!important}
    body.v10-index-owner #view-auction .v14-called-details.v18-called-horizontal .v14-called-grid small{display:inline!important;font-size:7.2px!important;font-weight:400!important;color:var(--soft)!important;overflow:visible!important;text-overflow:clip!important}
    body.v10-index-owner #view-auction .v14-called-details.v18-called-horizontal .v14-called-grid b{display:inline!important;font-size:9.4px!important;font-weight:900!important;margin:0!important;text-align:right!important}
    body.v10-index-owner #view-auction .v14-called-details.v18-called-horizontal .v14-called-title{font-size:7.5px!important}

    #view-auction .auction-caller-controls{grid-template-columns:minmax(110px,1fr) minmax(50px,72px) minmax(58px,78px)!important;align-items:end!important}
    #view-auction .auction-caller-controls .v18-top-call{width:100%!important;height:32px!important;min-height:32px!important;margin:0!important;font-size:8.5px!important;background:var(--good)!important}
    #view-auction .auction-free-fixed .drawer-filters{display:none!important}
    #view-auction .auction-free-fixed{grid-template-rows:auto auto minmax(0,1fr)!important}
    #view-auction .auction-free-fixed .drawer-table{position:relative!important;overflow:auto!important}
    #view-auction .auction-free-fixed .player-table thead tr:first-child th{position:sticky!important;top:0!important;z-index:32!important;background:#0d2b46!important}
    #view-auction .v18-auction-filter-row th{position:sticky!important;top:27px!important;z-index:31!important;height:27px!important;padding:2px 2px!important;background:#09243d!important;overflow:visible!important;border-bottom:1px solid rgba(91,151,216,.35)!important}
    #view-auction .v18-name-filter,#view-auction .v18-badge-filter,#view-auction .v18-range-toggle{width:100%!important;height:22px!important;min-height:22px!important;padding:1px 3px!important;margin:0!important;border-radius:4px!important;border:1px solid rgba(91,151,216,.28)!important;background:#061b2f!important;color:var(--text)!important;font-size:6.5px!important}
    #view-auction .v18-role-filter-note{display:block;text-align:center;color:var(--muted);font-size:5px;white-space:nowrap}
    #view-auction .v18-range{position:relative;min-width:46px}#view-auction .v18-range-toggle{display:flex!important;justify-content:space-between!important;align-items:center!important;gap:2px!important;white-space:nowrap!important}#view-auction .v18-range-toggle i{font-style:normal;color:var(--muted)}
    #view-auction .v18-range-pop{position:absolute;top:24px;left:50%;transform:translateX(-50%);width:180px;padding:7px;border:1px solid rgba(104,164,225,.48);border-radius:8px;background:#071e34;box-shadow:0 12px 32px rgba(0,0,0,.5);z-index:90}
    #view-auction .v18-auction-filter-row th:nth-child(n+6) .v18-range-pop{left:auto;right:0;transform:none}
    #view-auction .v18-range-values{display:grid;grid-template-columns:44px 1fr 44px;align-items:center;gap:3px;font-size:8px;margin-bottom:6px}#view-auction .v18-range-values span{text-align:center;color:var(--soft);font-size:6px}#view-auction .v18-range-values b:last-child{text-align:right}
    #view-auction .v18-dual{height:22px;position:relative;margin:0 6px}#view-auction .v18-dual .base,#view-auction .v18-dual .fill{position:absolute;top:10px;left:0;right:0;height:3px;border-radius:99px;background:rgba(255,255,255,.14)}#view-auction .v18-dual .fill{right:auto;background:#4f9bea}
    #view-auction .v18-dual input[type=range]{position:absolute;left:0;top:2px;width:100%!important;height:18px!important;margin:0!important;padding:0!important;background:transparent!important;pointer-events:none;-webkit-appearance:none;appearance:none}#view-auction .v18-dual input[type=range]::-webkit-slider-runnable-track{height:3px;background:transparent}#view-auction .v18-dual input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:13px;height:13px;margin-top:-5px;border-radius:50%;border:2px solid #9ed0ff;background:#1765ad;pointer-events:auto;cursor:ew-resize}
    #view-auction .v18-range-pop .ends{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:4px;font-size:6px;color:var(--soft)}#view-auction .v18-range-pop .ends small:last-child{text-align:right}#view-auction .v18-range-pop .ends button{height:18px!important;min-height:18px!important;padding:1px 4px!important;font-size:6px!important}
    #view-auction .auctioneer-functions-section>.auctioneer-head-actions{grid-template-columns:repeat(5,minmax(0,1fr))!important;grid-template-rows:repeat(2,minmax(0,1fr))!important}
    @media(max-width:1250px){#view-auction .auctioneer-functions-section>.auctioneer-head-actions{grid-template-columns:repeat(4,minmax(0,1fr))!important;grid-template-rows:repeat(3,minmax(0,1fr))!important}}
  `;document.head.appendChild(style);

  queueMicrotask(()=>{patchCalledDetails();mountAssignTurn();moveCallButtonTop();mountAuctionColumnFilters()});
})();
</script>
'''

s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
