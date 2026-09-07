from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v23-device-profiles-runtime' in s:
    raise SystemExit('V23 already applied')

runtime=r'''
<script id="v23-device-profiles-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V23_DEVICE_PROFILES__)return;
  window.__FANTA_V23_DEVICE_PROFILES__=1;

  const DEVICE_API='https://yyklmhzjxzkvycmxkegx.supabase.co/functions/v1/device-api';
  state.v23DeviceProfiles=state.v23DeviceProfiles||new Map();
  state.v23DeviceProfile=state.v23DeviceProfile||'pc_plus_phone';
  state.v23DeviceLeague=state.v23DeviceLeague||'';
  state.v23DeviceMineBusy=false;
  state.v23DeviceManageBusy=false;
  state.v23MobileBidAmount=state.v23MobileBidAmount||1;
  state.v23MobileBidPlayer='';
  state.v23MobileFreeSearch=state.v23MobileFreeSearch||'';

  const esc23=v=>typeof esc==='function'?esc(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const mobile23=()=>window.matchMedia('(max-width:850px)').matches;
  const president23=()=>typeof auctionHasPresidentRole==='function'&&auctionHasPresidentRole();
  const session23=()=>typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession;
  const myTeam23=()=>typeof auctionMyTeamId==='function'?auctionMyTeamId():state.dashboard?.myTeam?.team?.id||null;
  const info23=()=>typeof auctionMyTeamDashboardData==='function'?auctionMyTeamDashboardData():null;

  async function loadMine23(force=false){
    const leagueId=state.selectedLeague?.id||'';
    if(!leagueId)return null;
    if(!force&&state.v23DeviceLeague===leagueId&&state.v23DeviceProfile)return state.v23DeviceProfile;
    if(state.v23DeviceMineBusy)return state.v23DeviceProfile;
    state.v23DeviceMineBusy=true;
    try{
      const r=await api(DEVICE_API,{action:'getMine'},{quiet:true});
      state.v23DeviceProfile=r?.deviceProfile||'pc_plus_phone';
      state.v23DeviceLeague=leagueId;
    }catch(e){
      console.warn('Device profile',e);
      state.v23DeviceProfile='pc_plus_phone';
      state.v23DeviceLeague=leagueId;
    }finally{state.v23DeviceMineBusy=false;applyMobileMode23();}
    return state.v23DeviceProfile;
  }

  async function loadManageProfiles23(force=false){
    const leagueId=state.selectedLeague?.id||'';
    if(!leagueId||!state.management?.permissions?.isLeagueAdmin)return;
    if(state.v23DeviceManageBusy)return;
    if(!force&&state.v23DeviceProfilesLeague===leagueId&&state.v23DeviceProfiles?.size){decorateManage23();return;}
    state.v23DeviceManageBusy=true;
    try{
      const r=await api(DEVICE_API,{action:'getLeagueProfiles'},{quiet:true});
      state.v23DeviceProfiles=new Map((r?.profiles||[]).map(x=>[String(x.user_id),x.device_profile||'pc_plus_phone']));
      state.v23DeviceProfilesLeague=leagueId;
      decorateManage23();
    }catch(e){console.warn('League device profiles',e)}
    finally{state.v23DeviceManageBusy=false;}
  }

  function decorateManage23(){
    const host=document.getElementById('manage-members'),data=state.management;
    if(!host||!data)return;
    const rows=[...host.children].filter(x=>x.classList?.contains('compact-row'));
    (data.members||[]).forEach((member,i)=>{
      const row=rows[i];if(!row)return;
      let holder=row.querySelector('.v23-member-device');
      if(!holder){holder=document.createElement('div');holder.className='v23-member-device';row.appendChild(holder);}
      const value=state.v23DeviceProfiles.get(String(member.userId))||'pc_plus_phone';
      if(data.permissions?.isLeagueAdmin){
        holder.innerHTML=`<label><span>Uso smartphone asta</span><select data-v23-device-user="${esc23(member.userId)}"><option value="smartphone_only" ${value==='smartphone_only'?'selected':''}>Solo smartphone</option><option value="pc_plus_phone" ${value==='pc_plus_phone'?'selected':''}>PC + smartphone</option></select></label><small>${value==='smartphone_only'?'Console completa mobile · Rosa + Svincolati':'Smartphone = solo console rilanci'}</small>`;
      }else{
        holder.innerHTML=`<span class="badge">${value==='smartphone_only'?'Solo smartphone':'PC + smartphone'}</span>`;
      }
    });
  }

  document.addEventListener('change',async e=>{
    const select=e.target.closest?.('[data-v23-device-user]');if(!select)return;
    const old=state.v23DeviceProfiles.get(String(select.dataset.v23DeviceUser))||'pc_plus_phone';
    select.disabled=true;
    try{
      const r=await api(DEVICE_API,{action:'setProfile',targetUserId:select.dataset.v23DeviceUser,deviceProfile:select.value},{quiet:true});
      state.v23DeviceProfiles.set(String(select.dataset.v23DeviceUser),r?.deviceProfile||select.value);
      if(String(select.dataset.v23DeviceUser)===String(state.dashboard?.currentUser?.id||'')){state.v23DeviceProfile=r?.deviceProfile||select.value;applyMobileMode23();}
      msg('Utilizzo dispositivi aggiornato.','success');decorateManage23();
    }catch(err){select.value=old;msg(err.message||'Errore aggiornamento dispositivi.','error')}
    finally{select.disabled=false;}
  },true);

  if(typeof renderManagement==='function'){
    const oldManage23=renderManagement;
    renderManagement=function(...a){const r=oldManage23(...a);decorateManage23();void loadManageProfiles23();return r;};
  }

  function canBid23(){
    const s=session23(),d=state.auction||{};
    if(!s?.current_player_id||!president23())return false;
    if(typeof auctionBidTimerIsActive==='function'&&!auctionBidTimerIsActive(s))return false;
    if(typeof auctionMyTeamLeftCurrentPlayer==='function'&&auctionMyTeamLeftCurrentPlayer())return false;
    return d.settings?.bid_mode!=='turn'||!d.currentTurnTeam||String(d.currentTurnTeam.id)===String(myTeam23());
  }
  function canCall23(){
    const s=session23();if(!s||s.status!=='live'||s.current_player_id||!president23())return false;
    if(typeof auctionOwnCallTurn==='function')return auctionOwnCallTurn();
    return !s.current_nomination_team_id||String(s.current_nomination_team_id)===String(myTeam23());
  }
  function timer23(){
    const s=session23();if(!s?.current_player_id)return '—';if(s.hold_active)return 'HOLD';
    const now=Date.now()+Number(state.serverOffsetMs||0),start=Date.parse(s.timer_starts_at||''),end=Date.parse(s.timer_deadline||'');
    if(Number.isFinite(start)&&now<start)return `${Math.max(0,Math.ceil((start-now)/1000))}s`;
    return Number.isFinite(end)?`${Math.max(0,Math.ceil((end-now)/1000))}s`:'—';
  }
  function currentBid23(){const s=session23();return s?.current_player_id?Math.max(0,Number(s.current_bid||0)):0;}
  function syncBid23(force=false){
    const s=session23(),pid=String(s?.current_player_id||''),min=Math.max(1,currentBid23()+1);
    if(force||state.v23MobileBidPlayer!==pid||Number(state.v23MobileBidAmount)<min){state.v23MobileBidPlayer=pid;state.v23MobileBidAmount=min;}
  }

  function ensureShell23(){
    let root=document.getElementById('v23-mobile-auction');if(root)return root;
    root=document.createElement('section');root.id='v23-mobile-auction';root.innerHTML=`
      <div class="v23-mobile-head">
        <div class="v23-mobile-player"><small>CALCIATORE</small><strong id="v23-mobile-player">—</strong><span id="v23-mobile-team">—</span></div>
        <div class="v23-mobile-kpi"><small>TIMER</small><strong id="v23-mobile-timer">—</strong></div>
      </div>
      <div class="v23-mobile-strip"><span>OFFERTA <b id="v23-mobile-current">—</b></span><span>CREDITI <b id="v23-mobile-credits">—</b></span></div>
      <div id="v23-mobile-drawer-buttons" class="v23-mobile-drawer-buttons"><button type="button" data-v23-open="roster" class="secondary">ROSA</button><button type="button" data-v23-open="free" class="secondary">SVINCOLATI</button></div>
      <div class="v23-mobile-bidbox">
        <div class="v23-mobile-quick">${[1,2,3,5,10].map(x=>`<button type="button" data-v23-offset="${x}">+${x}</button>`).join('')}</div>
        <div class="v23-mobile-free"><button type="button" data-v23-step="-1" class="secondary">−</button><input id="v23-mobile-bid" type="number" min="1" step="1"><button type="button" data-v23-step="1" class="secondary">+</button></div>
        <div class="v23-mobile-actions"><button id="v23-mobile-confirm" type="button" class="good">RILANCIA</button><button id="v23-mobile-leave" type="button" class="danger">LASCIA</button></div>
      </div>
      <aside id="v23-drawer-roster" class="v23-mobile-drawer"><header><strong>LA MIA ROSA</strong><button type="button" data-v23-close class="secondary">×</button></header><div id="v23-mobile-roster-list" class="v23-mobile-list"></div></aside>
      <aside id="v23-drawer-free" class="v23-mobile-drawer"><header><strong>SVINCOLATI</strong><button type="button" data-v23-close class="secondary">×</button></header><div class="v23-mobile-search"><input id="v23-mobile-free-search" type="search" placeholder="Cerca giocatore…" autocomplete="off"></div><div id="v23-mobile-free-list" class="v23-mobile-list"></div></aside>`;
    document.body.appendChild(root);
    return root;
  }

  function playerForAssignment23(a){
    if(a?.player)return a.player;if(a?.league_player)return a.league_player;
    const id=String(a?.player_id||a?.league_player_id||'');
    return [...(state.list?.players||[]),...(state.auction?.callCandidates||[])].find(p=>String(p.id)===id)||a||{};
  }
  function renderRoster23(){
    const host=document.getElementById('v23-mobile-roster-list'),info=info23();if(!host)return;
    const rows=info?.assignments||[];
    host.innerHTML=rows.map(a=>{const p=playerForAssignment23(a),roles=typeof playerRoles==='function'?playerRoles(p,state.auction?.settings?.fantasy_mode||'classic'):[];const price=a?.price??a?.purchase_price??a?.amount??'—';return `<div class="v23-mobile-row"><div><span>${roles.map(r=>`<i class="rolebadge">${esc23(r)}</i>`).join('')}</span><strong>${esc23(p?.name||a?.player_name||'Giocatore')}</strong><small>${esc23(p?.serie_a_team||'')} · ${esc23(price)} cr</small></div></div>`}).join('')||'<div class="soft">Rosa vuota.</div>';
  }
  function fuzzy23(p,q){if(!q)return true;if(typeof playerSearchRank==='function')return playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null;return String(p?.name||'').toLowerCase().includes(q.toLowerCase());}
  function freePlayers23(){return (state.auction?.callCandidates||[]).filter(p=>(p.status==='available'||!p.status)&&(!state.auction?.auctionSession?.current_player_id||String(p.id)!==String(state.auction.auctionSession.current_player_id))).filter(p=>fuzzy23(p,String(state.v23MobileFreeSearch||'').trim())).sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'it')).slice(0,100);}
  function renderFree23(){
    const host=document.getElementById('v23-mobile-free-list');if(!host)return;const can=canCall23();
    host.innerHTML=freePlayers23().map(p=>{const roles=typeof playerRoles==='function'?playerRoles(p,state.auction?.settings?.fantasy_mode||'classic'):[];return `<div class="v23-mobile-row"><div><span>${roles.map(r=>`<i class="rolebadge">${esc23(r)}</i>`).join('')}</span><strong>${esc23(p.name||'—')}</strong><small>${esc23(p.serie_a_team||'—')}</small></div><button type="button" data-v23-call="${esc23(p.id)}" ${can?'':'disabled'}>CHIAMA</button></div>`}).join('')||'<div class="soft">Nessun giocatore.</div>';
  }

  function updateShell23(){
    const root=document.getElementById('v23-mobile-auction');if(!root)return;
    const p=state.auction?.currentPlayer,s=session23(),info=info23();syncBid23();
    root.querySelector('#v23-mobile-player').textContent=p?.name||'Nessuna chiamata';
    root.querySelector('#v23-mobile-team').textContent=p?.serie_a_team||'';
    root.querySelector('#v23-mobile-timer').textContent=timer23();
    root.querySelector('#v23-mobile-current').textContent=s?.current_player_id?String(currentBid23()):'—';
    root.querySelector('#v23-mobile-credits').textContent=info?.remaining==null?'—':String(Math.max(0,Number(info.remaining)));
    const input=root.querySelector('#v23-mobile-bid');if(input&&document.activeElement!==input)input.value=String(state.v23MobileBidAmount||1);
    const bid=canBid23();root.querySelectorAll('[data-v23-offset],[data-v23-step]').forEach(b=>b.disabled=!bid);root.querySelector('#v23-mobile-confirm').disabled=!bid;
    root.querySelector('#v23-mobile-leave').disabled=!Boolean(s?.current_player_id&&president23());
    root.querySelector('#v23-mobile-drawer-buttons').hidden=state.v23DeviceProfile!=='smartphone_only';
    if(state.v23DeviceProfile==='smartphone_only'){renderRoster23();renderFree23();}
  }

  function applyMobileMode23(){
    const active=mobile23()&&state.view==='auction'&&session23()?.status==='live'&&president23();
    document.body.classList.toggle('v23-mobile-auction-active',active);
    document.body.classList.toggle('v23-mobile-smartphone-only',active&&state.v23DeviceProfile==='smartphone_only');
    document.body.classList.toggle('v23-mobile-pc-phone',active&&state.v23DeviceProfile==='pc_plus_phone');
    const root=ensureShell23();root.hidden=!active;
    if(active)updateShell23();else root.querySelectorAll('.v23-mobile-drawer.open').forEach(x=>x.classList.remove('open'));
  }

  document.addEventListener('click',async e=>{
    const open=e.target.closest?.('[data-v23-open]');if(open){document.getElementById(`v23-drawer-${open.dataset.v23Open}`)?.classList.add('open');if(open.dataset.v23Open==='roster')renderRoster23();else renderFree23();return;}
    if(e.target.closest?.('[data-v23-close]')){e.target.closest('.v23-mobile-drawer')?.classList.remove('open');return;}
    const off=e.target.closest?.('[data-v23-offset]');if(off){state.v23MobileBidAmount=Math.max(1,currentBid23()+Number(off.dataset.v23Offset||1));updateShell23();return;}
    const step=e.target.closest?.('[data-v23-step]');if(step){state.v23MobileBidAmount=Math.max(currentBid23()+1,Number(state.v23MobileBidAmount||1)+Number(step.dataset.v23Step||0));updateShell23();return;}
    if(e.target.closest?.('#v23-mobile-confirm')){if(!canBid23())return;try{await placeBid(myTeam23(),Number(state.v23MobileBidAmount||currentBid23()+1),'APP');}catch(err){msg(err.message||'Rilancio non riuscito.','error')}return;}
    if(e.target.closest?.('#v23-mobile-leave')){if(typeof leaveCurrentAuctionPlayer==='function')leaveCurrentAuctionPlayer();return;}
    const call=e.target.closest?.('[data-v23-call]');if(call){
      const p=(state.auction?.callCandidates||[]).find(x=>String(x.id)===String(call.dataset.v23Call));if(!p||!canCall23())return;
      if(!await appConfirm(`Chiamare ${p.name} a base 1?`,{title:'Conferma chiamata',confirmText:'CHIAMA'}))return;
      call.disabled=true;
      try{
        const ss=session23(),response=await api(ENDPOINTS.auction,{action:'callPlayer',sessionId:ss.id,playerId:p.id,openingBid:1});
        state.auction.currentPlayer=p;if(response?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(response.state,{fromMutation:true});
        document.getElementById('v23-drawer-free')?.classList.remove('open');if(typeof window.v11ScheduleAuctionRefresh==='function')window.v11ScheduleAuctionRefresh('mobile-call',45);else if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(80);
      }catch(err){msg(err.message||'Chiamata non riuscita.','error')}finally{call.disabled=false;}return;
    }
  },true);
  document.addEventListener('input',e=>{
    if(e.target?.id==='v23-mobile-bid'){state.v23MobileBidAmount=Math.max(1,Number(e.target.value||1));return;}
    if(e.target?.id==='v23-mobile-free-search'){state.v23MobileFreeSearch=e.target.value;renderFree23();}
  },true);

  if(typeof renderAuctionLive==='function'){
    const oldLive23=renderAuctionLive;
    renderAuctionLive=function(...a){const r=oldLive23(...a);queueMicrotask(()=>{void loadMine23();applyMobileMode23();});return r;};
  }
  if(typeof loadAuction==='function'){
    const oldLoad23=loadAuction;
    loadAuction=async function(...a){const r=await oldLoad23(...a);await loadMine23();applyMobileMode23();return r;};
  }
  window.addEventListener('hashchange',()=>{if(state.view==='manage')void loadManageProfiles23();if(state.view==='auction')void loadMine23(true);queueMicrotask(applyMobileMode23);});
  window.matchMedia('(max-width:850px)').addEventListener?.('change',applyMobileMode23);
  setInterval(()=>{if(document.body.classList.contains('v23-mobile-auction-active'))updateShell23();},250);

  const css=document.createElement('style');css.id='v23-device-profiles-style';css.textContent=`
    #manage-members .compact-row{grid-template-columns:minmax(0,1fr) auto auto!important}
    .v23-member-device{min-width:170px;display:grid;gap:2px}.v23-member-device label{display:grid;grid-template-columns:auto 140px;gap:5px;align-items:center;font-size:8px}.v23-member-device select{height:28px!important;min-height:28px!important;font-size:8px!important}.v23-member-device small{font-size:6.5px;color:var(--soft);text-align:right}
    #v23-mobile-auction{display:none}
    @media(max-width:850px){
      body.v23-mobile-auction-active{overflow:hidden!important;background:#061426!important}
      body.v23-mobile-auction-active #view-auction .auction-root{display:none!important}
      body.v23-mobile-auction-active #v23-mobile-auction{display:grid!important;position:fixed;inset:0;z-index:5000;background:#061426;color:var(--text);padding:max(8px,env(safe-area-inset-top)) 8px max(8px,env(safe-area-inset-bottom));grid-template-rows:auto auto auto minmax(0,1fr);gap:8px;overflow:hidden}
      .v23-mobile-head{display:grid;grid-template-columns:minmax(0,1fr) 86px;gap:7px}.v23-mobile-player,.v23-mobile-kpi{border:1px solid var(--line);border-radius:12px;background:var(--panel);padding:9px}.v23-mobile-player{display:grid;grid-template-columns:1fr auto;align-items:center}.v23-mobile-player small{grid-column:1/-1;color:var(--muted);font-size:7px}.v23-mobile-player strong{font-size:22px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v23-mobile-player span{color:var(--soft);font-size:9px}.v23-mobile-kpi{text-align:center}.v23-mobile-kpi small{display:block;color:var(--muted);font-size:7px}.v23-mobile-kpi strong{font-size:28px}
      .v23-mobile-strip{display:grid;grid-template-columns:1fr 1fr;gap:7px}.v23-mobile-strip span{border:1px solid var(--line);border-radius:9px;background:var(--panel2);padding:8px 10px;color:var(--soft);font-size:8px;display:flex;justify-content:space-between;align-items:center}.v23-mobile-strip b{color:var(--text);font-size:18px}
      .v23-mobile-drawer-buttons{display:grid;grid-template-columns:1fr 1fr;gap:7px}.v23-mobile-drawer-buttons button{height:42px!important;font-size:11px!important}
      body.v23-mobile-pc-phone .v23-mobile-drawer-buttons{display:none!important}
      .v23-mobile-bidbox{align-self:end;display:grid;gap:8px;border:1px solid var(--line2);border-radius:14px;background:var(--panel);padding:10px;box-shadow:0 -10px 30px rgba(0,0,0,.22)}
      .v23-mobile-quick{display:grid;grid-template-columns:repeat(5,1fr);gap:6px}.v23-mobile-quick button{height:54px!important;font-size:15px!important;border-radius:10px!important;background:var(--panel3)!important}.v23-mobile-free{display:grid;grid-template-columns:46px minmax(0,1fr) 46px;gap:6px}.v23-mobile-free button{height:48px!important;font-size:20px!important}.v23-mobile-free input{height:48px!important;text-align:center!important;font-size:20px!important;font-weight:900!important}
      .v23-mobile-actions{display:grid;grid-template-columns:2fr 1fr;gap:7px}.v23-mobile-actions button{height:58px!important;font-size:14px!important;border-radius:11px!important}
      .v23-mobile-drawer{position:fixed;z-index:5100;inset:0;background:#061426;transform:translateX(105%);transition:transform .16s ease;padding:max(8px,env(safe-area-inset-top)) 8px max(8px,env(safe-area-inset-bottom));display:grid;grid-template-rows:auto auto minmax(0,1fr);gap:7px}.v23-mobile-drawer.open{transform:none}.v23-mobile-drawer header{display:flex;justify-content:space-between;align-items:center;border:1px solid var(--line);background:var(--panel);border-radius:10px;padding:6px 8px}.v23-mobile-drawer header strong{font-size:15px}.v23-mobile-drawer header button{width:36px!important;height:36px!important;font-size:20px!important;padding:0!important}.v23-mobile-search input{height:40px!important;font-size:12px!important}
      .v23-mobile-list{overflow:auto;display:grid;align-content:start;gap:4px}.v23-mobile-row{min-height:48px;border:1px solid var(--line);border-radius:8px;background:var(--panel2);padding:5px 7px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:7px;align-items:center}.v23-mobile-row>div{min-width:0}.v23-mobile-row strong{display:block;font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.v23-mobile-row small{display:block;color:var(--soft);font-size:8px;margin-top:2px}.v23-mobile-row .rolebadge{font-style:normal;margin-right:2px}.v23-mobile-row>button{height:36px!important;min-width:68px!important;font-size:9px!important}
    }
  `;document.head.appendChild(css);

  queueMicrotask(()=>{if(state.view==='manage')void loadManageProfiles23();if(state.view==='auction')void loadMine23();applyMobileMode23();});
})();
</script>
'''

pos=s.rfind('</body>')
if pos<0: raise SystemExit('body close not found')
s=s[:pos]+runtime+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
