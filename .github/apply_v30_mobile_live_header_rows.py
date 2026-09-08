from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

start=text.find('<script id="v23-mobile-auction-mode-runtime">')
end=text.find('</script>', start)
if start < 0 or end < 0:
    raise SystemExit('mobile auction runtime not found')
block=text[start:end]

# Metrics used by the mobile free-agent row.
if 'function mobileFreeMetrics(' not in block:
    anchor='  function renderMobileFreeDrawer(){'
    helper="""  function mobileFreeMetrics(p){
    const pfc=Number(p?.pfc);
    let fmv=Number(p?.expected_fantasy_avg);
    let tit=Number(p?.expected_titolarity);
    try{if(typeof strategicExpectedFantasyAverage==='function')fmv=Number(strategicExpectedFantasyAverage(p));}catch{}
    try{if(typeof strategicPresencePercent==='function')tit=Number(strategicPresencePercent(p));}catch{}
    const fmt=v=>Number.isFinite(Number(v))?Number(v).toFixed(2).replace('.',','):'—';
    return {
      pfc:Number.isFinite(pfc)?Math.round(pfc):'—',
      fmv:Number.isFinite(fmv)?fmt(fmv):'—',
      tit:Number.isFinite(tit)?`${Math.round(tit)}%`:'—'
    };
  }

"""
    if anchor not in block: raise SystemExit('renderMobileFreeDrawer anchor missing')
    block=block.replace(anchor,helper+anchor,1)

# One canonical mobile free-agent row: roles | identity | stats | action.
pat=re.compile(r"  function renderMobileFreeDrawer\(\)\{.*?\n  \}\n  function renderMobileDrawer",re.S)
rep="""  function renderMobileFreeDrawer(){
    const host=qs('[data-v23-free-list]');if(!host)return;
    const q=qs('[data-v23-free-search]')?.value||'';const can=mobileCanCall();
    host.innerHTML=mobileFreeCandidates(q).map(p=>{
      const m=mobileFreeMetrics(p);
      return `<div class=\"v23-mobile-drawer-row v23-mobile-free-row\">
        <div class=\"v23-mobile-drawer-roles\">${mobileRoleBadges(roles(p))}</div>
        <div class=\"v23-mobile-drawer-player\"><strong>${mobileEsc(p?.name||'—')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div>
        <div class=\"v23-mobile-drawer-stats\"><span><i>PFC</i><b>${mobileEsc(m.pfc)}</b></span><span><i>FMV</i><b>${mobileEsc(m.fmv)}</b></span><span><i>TIT</i><b>${mobileEsc(m.tit)}</b></span></div>
        <button type=\"button\" data-v23-mobile-call=\"${mobileEsc(p.id)}\" ${can?'':'disabled'}>CHIAMA</button>
      </div>`;
    }).join('')||'<div class=\"v23-mobile-empty\">Nessun giocatore disponibile.</div>';
  }
  function renderMobileDrawer"""
block,n=pat.subn(rep,block,count=1)
if n!=1: raise SystemExit(f'free drawer renderer replacement count={n}')

# Header controls: remove the old complete/compact switch, add BACK and PAUSE/RESUME.
if 'function ensureV30MobileHeader(' not in block:
    anchor='  function syncButtons(shell){'
    helper="""  function ensureV30MobileHeader(shell){
    qsa('.v23-header-mode').forEach(n=>n.remove());
    const head=qs('.v23-mobile-head',shell);if(!head)return;
    let back=qs('[data-v30-back]',head);
    if(!back){back=document.createElement('button');back.type='button';back.className='secondary v30-mobile-back';back.dataset.v30Back='1';back.setAttribute('aria-label','Torna al menu principale');back.textContent='←';head.prepend(back);}
    let pause=qs('[data-v30-pause]',head);
    if(!pause){pause=document.createElement('button');pause.type='button';pause.className='secondary v30-mobile-pause';pause.dataset.v30Pause='1';pause.textContent='PAUSA';head.appendChild(pause);}
  }
  function syncV30MobilePause(shell){
    const local=qs('[data-v30-pause]',shell);if(!local)return;
    const orig=document.getElementById('auction-pause-cycle');
    if(!orig){local.disabled=true;local.textContent='PAUSA';return;}
    local.disabled=orig.disabled;
    const t=String(orig.textContent||'').trim().toUpperCase();
    const resume=t.includes('RIPRENDI');
    local.textContent=resume?'RIPRENDI':'PAUSA';
    local.classList.toggle('good',resume);
    local.classList.toggle('warn',!resume);
    local.title=orig.title||t;
  }

"""
    if anchor not in block: raise SystemExit('syncButtons anchor missing')
    block=block.replace(anchor,helper+anchor,1)

# Ensure controls on every live sync.
needle="    const active=isPhone()&&isLive();shell.hidden=!active;"
if needle in block:
    block=block.replace(needle,needle+"ensureV30MobileHeader(shell);",1)
else:
    raise SystemExit('mobile active sync anchor missing')

# Sync pause state after normal button sync.
needle2='normalizeMobileActionRow(shell);syncButtons(shell);syncDrawerTargets();'
if needle2 in block:
    block=block.replace(needle2,'normalizeMobileActionRow(shell);syncButtons(shell);syncV30MobilePause(shell);syncDrawerTargets();',1)
else:
    raise SystemExit('mobile syncButtons sequence missing')

# Remove old switch creation from layout even if an older runtime tries to recreate it.
block=block.replace("const shell=ensureShell();ensureDrawerUi();const headerMode=ensureHeaderMode();","const shell=ensureShell();ensureDrawerUi();const headerMode=null;qsa('.v23-header-mode').forEach(n=>n.remove());")

# Add click handlers once for BACK and PAUSE.
if 'data-v30-back' in block and 'V30 mobile header controls' not in block:
    marker="  if(typeof renderAuctionLive==='function'){"
    handler="""  /* V30 mobile header controls */
  document.addEventListener('click',e=>{
    const back=e.target.closest?.('[data-v30-back]');
    if(back){e.preventDefault();e.stopPropagation();closeDrawer();window.location.hash='#/home';return;}
    const pause=e.target.closest?.('[data-v30-pause]');
    if(pause){e.preventDefault();e.stopPropagation();const orig=document.getElementById('auction-pause-cycle');if(orig&&!orig.disabled)orig.click();setTimeout(()=>syncV30MobilePause(qs('.v23-mobile-shell')),80);}
  },true);

"""
    if marker not in block: raise SystemExit('renderAuctionLive marker missing')
    block=block.replace(marker,handler+marker,1)

# Final CSS authority inside the mobile runtime.
css_extra="""
      /* V30: opaque, ordered free-agent drawer. */
      .v23-mobile-drawer-ui{position:fixed!important;inset:0!important;z-index:2090!important;pointer-events:none!important}
      .v23-drawer-backdrop{display:block!important;position:fixed!important;left:0!important;right:0!important;top:max(58px,calc(env(safe-area-inset-top) + 52px))!important;bottom:0!important;background:#061426!important;opacity:1!important;z-index:2090!important;pointer-events:none!important}
      .v23-mobile-drawer-panel{z-index:2101!important;background:#0c2442!important;opacity:1!important;pointer-events:auto!important}
      .v23-mobile-drawer-list{overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;touch-action:pan-y!important;overscroll-behavior:contain!important}
      .v23-mobile-free-row{grid-template-columns:72px minmax(0,1fr) 62px 72px!important;gap:6px!important;min-height:64px!important;align-items:center!important;background:#12345d!important;overflow:hidden!important}
      .v23-mobile-free-row .v23-mobile-drawer-roles{width:72px!important;max-width:72px!important;gap:2px!important;justify-content:flex-start!important}
      .v23-mobile-free-row .v23-mobile-drawer-roles .rolebadge{min-width:22px!important;width:auto!important;height:26px!important;padding:1px 4px!important;font-size:9px!important;border-radius:6px!important}
      .v23-mobile-free-row .v23-mobile-drawer-player{min-width:0!important;overflow:hidden!important}
      .v23-mobile-free-row .v23-mobile-drawer-player strong{font-size:11px!important;line-height:1.05!important}
      .v23-mobile-free-row .v23-mobile-drawer-player small{font-size:8px!important;margin-top:3px!important}
      .v23-mobile-drawer-stats{min-width:0!important;display:grid!important;gap:2px!important;align-content:center!important}
      .v23-mobile-drawer-stats span{display:grid!important;grid-template-columns:24px minmax(0,1fr)!important;gap:3px!important;align-items:center!important;line-height:1!important}
      .v23-mobile-drawer-stats i{font-style:normal!important;color:var(--soft)!important;font-size:7px!important;text-align:left!important}
      .v23-mobile-drawer-stats b{font-size:8px!important;text-align:right!important;font-variant-numeric:tabular-nums!important;white-space:nowrap!important}
      .v23-mobile-free-row>button{position:static!important;inset:auto!important;transform:none!important;align-self:center!important;justify-self:stretch!important;width:72px!important;min-width:72px!important;max-width:72px!important;height:40px!important;min-height:40px!important;max-height:40px!important;margin:0!important;padding:3px 4px!important;font-size:8px!important;border-radius:9px!important}

      /* V30: mobile live header = BACK | TURN | CREDITS | PAUSE. */
      body.v23-mobile-auction .v23-header-mode{display:none!important}
      .v23-mobile-head{grid-template-columns:40px minmax(0,1fr) 92px 76px!important;gap:5px!important;align-items:stretch!important}
      .v30-mobile-back,.v30-mobile-pause{display:flex!important;align-items:center!important;justify-content:center!important;min-width:0!important;width:100%!important;min-height:48px!important;height:auto!important;margin:0!important;padding:3px 5px!important;border-radius:10px!important;font-weight:900!important}
      .v30-mobile-back{font-size:22px!important}
      .v30-mobile-pause{font-size:7px!important;line-height:1.05!important;white-space:normal!important}
      .v23-mobile-turn{min-width:0!important}
      .v23-mobile-credit{min-width:0!important;padding-left:6px!important;padding-right:6px!important}
      @media(max-width:390px){
        .v23-mobile-head{grid-template-columns:38px minmax(0,1fr) 86px 70px!important;gap:4px!important}
        .v23-mobile-free-row{grid-template-columns:66px minmax(0,1fr) 56px 66px!important;gap:5px!important;padding-left:5px!important;padding-right:5px!important}
        .v23-mobile-free-row .v23-mobile-drawer-roles{width:66px!important;max-width:66px!important}
        .v23-mobile-free-row>button{width:66px!important;min-width:66px!important;max-width:66px!important;font-size:7.5px!important}
        .v23-mobile-drawer-stats span{grid-template-columns:22px minmax(0,1fr)!important;gap:2px!important}
      }
"""
needle_css="    }\n  `;document.head.appendChild(css);"
if 'V30: opaque, ordered free-agent drawer.' not in block:
    if needle_css not in block: raise SystemExit('mobile CSS closing marker missing')
    block=block.replace(needle_css,css_extra+"    }\n  `;document.head.appendChild(css);",1)

text=text[:start]+block+text[end:]
p.write_text(text,encoding='utf-8')
