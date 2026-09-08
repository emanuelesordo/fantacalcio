from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

start=text.find('<script id="v23-mobile-auction-mode-runtime">')
end=text.find('</script>', start)
if start<0 or end<0:
    raise SystemExit('V23 mobile runtime not found')
block=text[start:end]

# 1) Compact, self-contained mobile header.
block=block.replace(
'''      <header class="v23-mobile-head">\n        <div class="v23-mobile-credit"><small>CREDITI</small><strong data-v23-credits>—</strong><span>MAX <b data-v23-max>—</b></span></div>\n      </header>''',
'''      <header class="v23-mobile-head">\n        <div class="v23-mobile-turn"><small>TURNO DI CHIAMATA</small><strong data-v23-turn>—</strong></div>\n        <div class="v23-mobile-credit"><small>CREDITI</small><strong data-v23-credits>—</strong><span>MAX <b data-v23-max>—</b></span></div>\n      </header>''')

# 2) Keep LIBERO, OK and LASCIA on the same row.
block=block.replace(
'''        <div class="v23-free-bid"><label>LIBERO <input type="number" min="1" step="1" value="1" data-v23-free></label><button type="button" data-v23-free-ok>OK</button></div>\n        <div class="v23-main-actions"><button type="button" class="secondary" data-v23-proxy="hold">HOLD</button><button type="button" class="warn" data-v23-proxy="done">A POSTO</button><button type="button" class="danger" data-v23-proxy="leave">LASCIA</button></div>''',
'''        <div class="v23-free-bid"><label>LIBERO <input type="number" min="1" step="1" value="1" data-v23-free></label><button type="button" data-v23-free-ok>OK</button><button type="button" class="danger" data-v23-proxy="leave">LASCIA</button></div>\n        <div class="v23-main-actions"><button type="button" class="secondary" data-v23-proxy="hold">HOLD</button><button type="button" class="warn" data-v23-proxy="done">A POSTO</button></div>''')

# 3) Replace DOM-proxy drawers with real mobile drawers populated from auction state.
block=re.sub(r'''  function rosterTarget\(\)\{.*?  function ensureHeaderMode\(\)\{''', r'''  function mobileEsc(v){try{return typeof esc==='function'?esc(v):String(v??'')}catch{return String(v??'')}}
  function mobileAssignmentPlayer(a){
    if(a?.player)return a.player;if(a?.league_player)return a.league_player;
    const id=String(a?.player_id||a?.league_player_id||'');
    return [...(state.list?.players||[]),...(state.auction?.callCandidates||[])].find(p=>String(p.id)===id)||a||{};
  }
  function mobileCanCall(){
    const s=session();if(!s||s.current_player_id)return false;
    try{return typeof auctionOwnCallTurn==='function'?Boolean(auctionOwnCallTurn()):false}catch{return false}
  }
  function mobileFreeCandidates(query=''){
    const q=String(query||'').trim();
    return (state.auction?.callCandidates||[])
      .filter(p=>(!p.status||p.status==='available')&&String(p.id)!==String(session()?.current_player_id||''))
      .filter(p=>{if(!q)return true;try{return typeof playerSearchRank==='function'?playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null:String(p?.name||'').toLowerCase().includes(q.toLowerCase())}catch{return true}})
      .sort((a,b)=>String(a?.name||'').localeCompare(String(b?.name||''),'it'))
      .slice(0,120);
  }
  function renderMobileRosterDrawer(){
    const host=qs('[data-v23-roster-list]');if(!host)return;
    const rows=myInfo()?.assignments||[];
    host.innerHTML=rows.map(a=>{const p=mobileAssignmentPlayer(a),rr=roles(p),price=a?.purchase_price??a?.price??a?.amount??'—';return `<div class="v23-mobile-drawer-row"><div class="v23-mobile-drawer-player"><span>${rr.map(r=>`<i class="rolebadge">${mobileEsc(r)}</i>`).join('')}</span><strong>${mobileEsc(p?.name||a?.player_name||'Giocatore')}</strong><small>${mobileEsc(p?.serie_a_team||'')} · ${mobileEsc(price)} cr</small></div></div>`}).join('')||'<div class="v23-mobile-empty">Rosa vuota.</div>';
  }
  function renderMobileFreeDrawer(){
    const host=qs('[data-v23-free-list]');if(!host)return;
    const q=qs('[data-v23-free-search]')?.value||'';const can=mobileCanCall();
    host.innerHTML=mobileFreeCandidates(q).map(p=>`<div class="v23-mobile-drawer-row"><div class="v23-mobile-drawer-player"><span>${roles(p).map(r=>`<i class="rolebadge">${mobileEsc(r)}</i>`).join('')}</span><strong>${mobileEsc(p?.name||'—')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div><button type="button" data-v23-mobile-call="${mobileEsc(p.id)}" ${can?'':'disabled'}>CHIAMA</button></div>`).join('')||'<div class="v23-mobile-empty">Nessun giocatore disponibile.</div>';
  }
  function renderMobileDrawer(which){if(which==='roster')renderMobileRosterDrawer();if(which==='free')renderMobileFreeDrawer();}
  function closeDrawer(){document.body.classList.remove('v23-roster-open','v23-free-open');const ui=qs('.v23-mobile-drawer-ui');if(ui)ui.hidden=true;}
  function openDrawer(which){
    if(getMode()!=='full')return;
    document.body.classList.toggle('v23-roster-open',which==='roster');
    document.body.classList.toggle('v23-free-open',which==='free');
    const ui=ensureDrawerUi();ui.hidden=false;renderMobileDrawer(which);
  }
  function syncDrawerTargets(){
    const ui=qs('.v23-mobile-drawer-ui');if(!ui)return;
    const rosterOpen=document.body.classList.contains('v23-roster-open'),freeOpen=document.body.classList.contains('v23-free-open');
    ui.hidden=!(rosterOpen||freeOpen);
    if(rosterOpen)renderMobileRosterDrawer();if(freeOpen)renderMobileFreeDrawer();
  }

  function ensureHeaderMode(){''', block, flags=re.S)

# 4) Real drawer UI and call action.
block=re.sub(r'''  function ensureDrawerUi\(\)\{.*?  function timerText\(\)\{''', r'''  function ensureDrawerUi(){
    let ui=qs('.v23-mobile-drawer-ui');if(ui)return ui;
    ui=document.createElement('div');ui.className='v23-mobile-drawer-ui';ui.hidden=true;ui.innerHTML=`
      <div class="v23-drawer-backdrop"></div>
      <section class="v23-mobile-drawer-panel v23-mobile-drawer-roster-panel"><header><strong>LA MIA ROSA</strong><button type="button" class="v23-drawer-close" aria-label="Chiudi">×</button></header><div class="v23-mobile-drawer-list" data-v23-roster-list></div></section>
      <section class="v23-mobile-drawer-panel v23-mobile-drawer-free-panel"><header><strong>SVINCOLATI</strong><button type="button" class="v23-drawer-close" aria-label="Chiudi">×</button></header><div class="v23-mobile-drawer-search"><input type="search" data-v23-free-search placeholder="Cerca giocatore…" autocomplete="off"></div><div class="v23-mobile-drawer-list" data-v23-free-list></div></section>`;
    document.body.appendChild(ui);
    ui.addEventListener('click',async e=>{
      if(e.target.closest('.v23-drawer-close')||e.target.classList.contains('v23-drawer-backdrop')){closeDrawer();return;}
      const call=e.target.closest('[data-v23-mobile-call]');if(!call)return;
      const p=(state.auction?.callCandidates||[]).find(x=>String(x.id)===String(call.dataset.v23MobileCall));
      if(!p||!mobileCanCall())return;
      if(typeof appConfirm==='function'&&!await appConfirm(`Chiamare ${p.name} a base 1?`,{title:'Conferma chiamata',confirmText:'CHIAMA'}))return;
      call.disabled=true;
      try{
        const s=session(),response=await api(ENDPOINTS.auction,{action:'callPlayer',sessionId:s.id,playerId:p.id,openingBid:1});
        state.auction.currentPlayer=p;
        if(response?.state&&typeof applyAuctionHotState==='function')applyAuctionHotState(response.state,{fromMutation:true});
        closeDrawer();
        if(typeof window.v11ScheduleAuctionRefresh==='function')window.v11ScheduleAuctionRefresh('mobile-call',45);else if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(80);
      }catch(err){msg(err.message||'Chiamata non riuscita.','error')}finally{call.disabled=false;}
    });
    ui.addEventListener('input',e=>{if(e.target.matches('[data-v23-free-search]'))renderMobileFreeDrawer();});
    return ui;
  }

  function timerText(){''', block, flags=re.S)

# 5) Sync header contents and move mode switch into the mobile header.
block=block.replace(
'''    const shell=ensureShell();ensureDrawerUi();const headerMode=ensureHeaderMode();\n    const active=isPhone()&&isLive();shell.hidden=!active;if(headerMode)headerMode.hidden=!active;''',
'''    const shell=ensureShell();ensureDrawerUi();const headerMode=ensureHeaderMode();\n    const active=isPhone()&&isLive();shell.hidden=!active;if(headerMode)headerMode.hidden=!active;\n    const mobileHead=qs('.v23-mobile-head',shell);if(active&&headerMode&&mobileHead&&headerMode.parentElement!==mobileHead){mobileHead.insertBefore(headerMode,mobileHead.querySelector('.v23-mobile-credit'));}''')
block=block.replace(
'''    qs('[data-v23-credits]',shell).textContent=info?.remaining??'—';qs('[data-v23-max]',shell).textContent=info?.maxBid??'—';''',
'''    qs('[data-v23-turn]',shell).textContent=teamName(s?.current_nomination_team_id||state.auction?.currentNominationTeam?.id);\n    qs('[data-v23-credits]',shell).textContent=info?.remaining??'—';qs('[data-v23-max]',shell).textContent=info?.maxBid??'—';''')
block=block.replace(
'''    const drawers=qs('.v23-mobile-drawers',shell);if(drawers)drawers.hidden=mode!=='full';syncButtons(shell);syncDrawerTargets();''',
'''    const drawers=qs('.v23-mobile-drawers',shell);if(drawers)drawers.hidden=mode!=='full';syncButtons(shell);syncDrawerTargets();''')

# 6) CSS: mobile shell covers the whole viewport; no clipped legacy header.
block=block.replace(
'''      body.v23-mobile-auction .app-head{position:fixed!important;top:4px!important;left:4px!important;right:4px!important;z-index:2050!important;height:var(--header-h)!important;min-height:var(--header-h)!important}''',
'''      body.v23-mobile-auction .app-head{display:none!important}\n      body.v23-mobile-auction #view-auction .auction-root{visibility:hidden!important;pointer-events:none!important}''')
block=block.replace(
'''      body.v23-mobile-auction .v23-mobile-shell{display:grid!important;position:fixed!important;inset:calc(var(--header-h) + 8px) 0 0 0!important;z-index:1900!important;background:#061426!important;padding:max(7px,env(safe-area-inset-top)) 7px max(8px,env(safe-area-inset-bottom))!important;grid-template-rows:auto auto auto minmax(0,1fr)!important;gap:7px!important;color:var(--text)!important}''',
'''      body.v23-mobile-auction .v23-mobile-shell{display:grid!important;position:fixed!important;inset:0!important;z-index:1900!important;background:#061426!important;padding:max(8px,env(safe-area-inset-top)) 7px max(8px,env(safe-area-inset-bottom))!important;grid-template-rows:auto auto auto minmax(0,1fr)!important;gap:7px!important;color:var(--text)!important}''')
block=block.replace(
'''      .v23-mobile-head{display:grid!important;grid-template-columns:1fr!important;gap:7px!important;align-items:center!important}''',
'''      .v23-mobile-head{display:grid!important;grid-template-columns:minmax(0,1fr) 108px 116px!important;gap:5px!important;align-items:stretch!important}\n      .v23-mobile-turn{min-width:0!important;display:flex!important;flex-direction:column!important;justify-content:center!important;padding:5px 8px!important;border:1px solid var(--line)!important;border-radius:10px!important;background:var(--panel)!important}.v23-mobile-turn small{font-size:6px!important;color:var(--muted)!important}.v23-mobile-turn strong{font-size:15px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}\n      body.v23-mobile-auction .v23-mobile-head .v23-header-mode{display:grid!important;grid-template-columns:1fr 1fr!important;align-self:stretch!important;min-width:0!important;padding:2px!important}.v23-mobile-head .v23-header-mode button{min-width:0!important;padding:2px!important;font-size:6.5px!important}\n      .v23-mobile-credit{min-width:0!important}''')
block=block.replace(
'''      .v23-mobile-free{display:grid!important;grid-template-columns:46px minmax(0,1fr) 46px;gap:6px}''',
'''      .v23-mobile-free{display:grid!important;grid-template-columns:46px minmax(0,1fr) 46px;gap:6px}''')
block=block.replace(
'''      .v23-mobile-console{align-self:end!important;display:grid!important;grid-template-rows:auto auto auto!important;gap:6px!important;padding:8px!important;border:1px solid var(--line2)!important;border-radius:12px!important;background:linear-gradient(180deg,rgba(18,52,93,.98),rgba(8,31,54,.99))!important;box-shadow:0 -10px 35px rgba(0,0,0,.28)!important}.v23-quick-bids{display:grid!important;grid-template-columns:repeat(5,1fr)!important;gap:5px!important}.v23-quick-bids button{min-height:48px!important;font-size:15px!important;border-radius:10px!important}.v23-free-bid{display:grid!important;grid-template-columns:minmax(0,1fr) 86px!important;gap:5px!important}.v23-free-bid label{display:grid!important;grid-template-columns:auto minmax(0,1fr)!important;align-items:center!important;gap:6px!important;padding:4px 6px!important;border:1px solid var(--line)!important;border-radius:10px!important;background:#0b2a4d!important;font-size:8px!important}.v23-free-bid input{height:40px!important;min-height:40px!important;font-size:18px!important;text-align:center!important}.v23-free-bid button{min-height:48px!important;background:var(--good)!important;font-size:14px!important}.v23-main-actions{display:grid!important;grid-template-columns:repeat(3,1fr)!important;gap:5px!important}.v23-main-actions button{min-height:44px!important;font-size:11px!important}''',
'''      .v23-mobile-console{align-self:end!important;display:grid!important;grid-template-rows:auto auto auto!important;gap:6px!important;padding:8px!important;border:1px solid var(--line2)!important;border-radius:12px!important;background:linear-gradient(180deg,rgba(18,52,93,.98),rgba(8,31,54,.99))!important;box-shadow:0 -10px 35px rgba(0,0,0,.28)!important}.v23-quick-bids{display:grid!important;grid-template-columns:repeat(5,1fr)!important;gap:5px!important}.v23-quick-bids button{min-height:48px!important;font-size:15px!important;border-radius:10px!important}.v23-free-bid{display:grid!important;grid-template-columns:minmax(0,1fr) 72px 78px!important;gap:5px!important}.v23-free-bid label{min-width:0!important;display:grid!important;grid-template-columns:auto minmax(0,1fr)!important;align-items:center!important;gap:5px!important;padding:3px 5px!important;border:1px solid var(--line)!important;border-radius:10px!important;background:#0b2a4d!important;font-size:7px!important}.v23-free-bid input{min-width:0!important;width:100%!important;height:40px!important;min-height:40px!important;font-size:18px!important;text-align:center!important}.v23-free-bid button{min-width:0!important;min-height:48px!important;font-size:11px!important;padding:4px!important}.v23-free-bid [data-v23-free-ok]{background:var(--good)!important}.v23-main-actions{display:grid!important;grid-template-columns:repeat(2,1fr)!important;gap:5px!important}.v23-main-actions button{min-height:40px!important;font-size:10px!important}''')

# Replace old proxy-drawer CSS with dedicated drawer panels.
block=block.replace(
'''      body.v23-mobile-auction .v23-drawer-target{display:none!important}\n      body.v23-roster-open .v23-drawer-roster,body.v23-free-open .v23-drawer-free{display:block!important;position:fixed!important;z-index:2000!important;left:8px!important;right:8px!important;top:max(54px,calc(env(safe-area-inset-top) + 48px))!important;bottom:max(8px,env(safe-area-inset-bottom))!important;width:auto!important;max-width:none!important;height:auto!important;max-height:none!important;overflow:auto!important;transform:none!important;border:1px solid var(--line2)!important;border-radius:12px!important;background:var(--panel)!important;box-shadow:0 20px 70px rgba(0,0,0,.55)!important}''',
'''      .v23-mobile-drawer-panel{display:none!important;position:fixed!important;z-index:2000!important;left:8px!important;right:8px!important;top:max(58px,calc(env(safe-area-inset-top) + 52px))!important;bottom:max(8px,env(safe-area-inset-bottom))!important;min-height:0!important;overflow:hidden!important;border:1px solid var(--line2)!important;border-radius:12px!important;background:var(--panel)!important;box-shadow:0 20px 70px rgba(0,0,0,.55)!important;grid-template-rows:auto auto minmax(0,1fr)!important}\n      body.v23-roster-open .v23-mobile-drawer-roster-panel{display:grid!important;grid-template-rows:auto minmax(0,1fr)!important}\n      body.v23-free-open .v23-mobile-drawer-free-panel{display:grid!important}\n      .v23-mobile-drawer-panel>header{display:flex!important;align-items:center!important;justify-content:space-between!important;gap:8px!important;padding:8px 10px!important;border-bottom:1px solid var(--line)!important}.v23-mobile-drawer-panel>header strong{font-size:14px!important}.v23-mobile-drawer-panel .v23-drawer-close{position:static!important;width:34px!important;height:34px!important;min-height:34px!important;font-size:20px!important;pointer-events:auto!important}\n      .v23-mobile-drawer-search{padding:7px!important;border-bottom:1px solid var(--line)!important}.v23-mobile-drawer-search input{height:38px!important;font-size:12px!important}\n      .v23-mobile-drawer-list{min-height:0!important;overflow:auto!important;padding:6px!important;display:grid!important;align-content:start!important;gap:4px!important}\n      .v23-mobile-drawer-row{min-height:48px!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:7px!important;align-items:center!important;padding:5px 7px!important;border:1px solid var(--line)!important;border-radius:8px!important;background:var(--panel2)!important}.v23-mobile-drawer-player{min-width:0!important}.v23-mobile-drawer-player strong{display:block!important;font-size:11px!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}.v23-mobile-drawer-player small{display:block!important;margin-top:2px!important;color:var(--soft)!important;font-size:8px!important}.v23-mobile-drawer-player .rolebadge{font-style:normal!important;margin-right:2px!important}.v23-mobile-drawer-row>button{min-width:72px!important;height:36px!important;font-size:9px!important}.v23-mobile-empty{padding:16px!important;text-align:center!important;color:var(--soft)!important}''')

text=text[:start]+block+text[end:]
p.write_text(text,encoding='utf-8')
