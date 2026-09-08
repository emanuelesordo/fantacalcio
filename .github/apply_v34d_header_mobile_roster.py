from pathlib import Path
import re

p = Path('home.html')
t = p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in t
assert 'Fantacalcio Live - tool per asta online' in t

# Idempotency.
t = re.sub(r'\n<style id="v34d-header-mobile-roster-style">.*?</style>\n', '\n', t, flags=re.S)
t = re.sub(r'\n<script id="v34d-header-mobile-roster-runtime">.*?</script>\n', '\n', t, flags=re.S)

# Do not force the auctioneer drawer state on every mutation/render. The canonical
# <details> toggle handler already persists state.auctionAdminConsoleOpen.
console_pattern = re.compile(
    r"  function console34\(\)\{\n"
    r"    const d=qs\('#auctioneer-console-drawer'\);if\(!d\)return;\n"
    r"    const pre=session34\(\)\?\.prestart_hold===true;if\(pre\)\{d\.open=true;return\}\n"
    r"    const desired=state\.v34AuctioneerOpen===true;if\(d\.open!==desired\)d\.open=desired;state\.auctionAdminConsoleOpen=desired;\n"
    r"  \}"
)
console_replacement = """  function console34(){
    const d=qs('#auctioneer-console-drawer');if(!d)return;
    const pre=session34()?.prestart_hold===true;
    if(pre){
      if(!d.open)d.open=true;
      state.auctionAdminConsoleOpen=true;
      state.v34AuctioneerOpen=true;
      return;
    }
    /* Native <details> + the existing toggle listener own the state. */
    state.v34AuctioneerOpen=d.open===true;
  }"""
t, console_count = console_pattern.subn(console_replacement, t)
if console_count < 1:
    raise SystemExit('console34 source not found')

# Remove the capture-phase summary interception introduced in V34. It prevented
# the native <details> element from closing reliably.
summary_pattern = re.compile(
    r"\n    const summary=e\.target\.closest\?\.\('#auctioneer-console-drawer>summary'\);"
    r"if\(summary\)\{const d=summary\.parentElement;if\(session34\(\)\?\.prestart_hold===true\)return;"
    r"e\.preventDefault\(\);e\.stopImmediatePropagation\(\);state\.v34AuctioneerOpen=!d\.open;"
    r"state\.auctionAdminConsoleOpen=state\.v34AuctioneerOpen;d\.open=state\.v34AuctioneerOpen;return\}"
)
t, summary_count = summary_pattern.subn('', t)
if summary_count < 1:
    raise SystemExit('V34 summary interception not found')

# Latest mobile roster drawer: reproduce the desktop Classic slot model (P/D/C/A)
# including empty slots instead of showing only purchased players.
mobile_roster_pattern = re.compile(
    r"  function renderMobileRosterDrawer\(\)\{.*?\n  \}\n  function mobileFreeMetrics",
    re.S,
)
mobile_roster_replacement = r'''  function renderMobileRosterDrawer(){
    const host=qs('[data-v23-roster-list]');if(!host)return;
    const info=myInfo();
    const rows=info?.assignments||[];
    const fantasyMode=state.auction?.settings?.fantasy_mode||'classic';

    if(fantasyMode!=='classic'){
      host.innerHTML=rows.map(a=>{
        const p=mobileAssignmentPlayer(a),rr=roles(p),price=a?.purchase_price??a?.price??a?.amount??'—';
        return `<div class="v23-mobile-drawer-row v23-mobile-roster-row"><div class="v23-mobile-drawer-roles">${mobileRoleBadges(rr)}</div><div class="v23-mobile-drawer-player"><strong>${mobileEsc(p?.name||a?.player_name||'Giocatore')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div><div class="v23-mobile-drawer-price">${mobileEsc(price)} cr</div></div>`;
      }).join('')||'<div class="v23-mobile-empty">Rosa vuota.</div>';
      return;
    }

    let cfg={P:3,D:8,C:8,A:6};
    try{
      const raw=state.auction?.settings?.roster_config||state.setup?.roster_config;
      const parsed=typeof parseRosterConfig==='function'?parseRosterConfig(raw):raw;
      cfg={...cfg,...(parsed?.classic||{})};
    }catch{}

    const labels={P:'PORTIERI',D:'DIFENSORI',C:'CENTROCAMPISTI',A:'ATTACCANTI'};
    const grouped={P:[],D:[],C:[],A:[]};
    rows.forEach(a=>{
      const p=mobileAssignmentPlayer(a),rr=roles(p);
      const macro=String(p?.classic_role||rr?.[0]||'').toUpperCase();
      if(grouped[macro])grouped[macro].push(a);
    });

    host.innerHTML=['P','D','C','A'].map(role=>{
      const group=grouped[role]||[];
      const required=Math.max(0,Number(cfg?.[role]||0));
      const total=Math.max(required,group.length);
      const filled=group.map(a=>{
        const p=mobileAssignmentPlayer(a),rr=roles(p),price=a?.purchase_price??a?.price??a?.amount??'—';
        return `<div class="v23-mobile-drawer-row v23-mobile-roster-row"><div class="v23-mobile-drawer-roles">${mobileRoleBadges(rr.length?rr:[role])}</div><div class="v23-mobile-drawer-player"><strong>${mobileEsc(p?.name||a?.player_name||'Giocatore')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div><div class="v23-mobile-drawer-price">${mobileEsc(price)} cr</div></div>`;
      });
      for(let i=group.length;i<total;i++){
        filled.push(`<div class="v23-mobile-drawer-row v23-mobile-roster-row is-empty" aria-label="Slot ${role} libero"><div class="v23-mobile-drawer-roles"><span class="rolebadge" data-role="${role}">${role}</span></div><div class="v23-mobile-drawer-player"><strong>Slot libero</strong><small>${labels[role]}</small></div><div class="v23-mobile-drawer-price">—</div></div>`);
      }
      return `<section class="v34-mobile-roster-group" data-v34-role="${role}"><header class="v34-mobile-roster-group-head"><span class="rolebadge" data-role="${role}">${role}</span><strong>${labels[role]}</strong><small>${group.length}/${required}</small></header>${filled.join('')}</section>`;
    }).join('');
  }
  function mobileFreeMetrics'''
t, mobile_count = mobile_roster_pattern.subn(mobile_roster_replacement, t)
if mobile_count < 1:
    raise SystemExit('renderMobileRosterDrawer source not found')

# Legacy V23 phone roster renderer: keep the same Classic slot grouping in case
# this shell is selected by an older/mobile path.
legacy_roster_pattern = re.compile(
    r"  function renderRoster23\(\)\{.*?\n  \}\n  function fuzzy23",
    re.S,
)
legacy_roster_replacement = r'''  function renderRoster23(){
    const host=document.getElementById('v23-mobile-roster-list'),info=info23();if(!host)return;
    const rows=info?.assignments||[];
    const fantasyMode=state.auction?.settings?.fantasy_mode||'classic';
    if(fantasyMode!=='classic'){
      host.innerHTML=rows.map(a=>{const p=playerForAssignment23(a),rr=typeof playerRoles==='function'?playerRoles(p,fantasyMode):[];const price=a?.price??a?.purchase_price??a?.amount??'—';return `<div class="v23-mobile-row"><div><span>${rr.map(r=>`<i class="rolebadge">${esc23(r)}</i>`).join('')}</span><strong>${esc23(p?.name||a?.player_name||'Giocatore')}</strong><small>${esc23(p?.serie_a_team||'')} · ${esc23(price)} cr</small></div></div>`}).join('')||'<div class="soft">Rosa vuota.</div>';
      return;
    }
    let cfg={P:3,D:8,C:8,A:6};
    try{const raw=state.auction?.settings?.roster_config||state.setup?.roster_config;const parsed=typeof parseRosterConfig==='function'?parseRosterConfig(raw):raw;cfg={...cfg,...(parsed?.classic||{})}}catch{}
    const labels={P:'PORTIERI',D:'DIFENSORI',C:'CENTROCAMPISTI',A:'ATTACCANTI'},grouped={P:[],D:[],C:[],A:[]};
    rows.forEach(a=>{const p=playerForAssignment23(a),rr=typeof playerRoles==='function'?playerRoles(p,fantasyMode):[];const macro=String(p?.classic_role||rr?.[0]||'').toUpperCase();if(grouped[macro])grouped[macro].push(a)});
    host.innerHTML=['P','D','C','A'].map(role=>{const group=grouped[role]||[],required=Math.max(0,Number(cfg?.[role]||0)),total=Math.max(required,group.length);const out=group.map(a=>{const p=playerForAssignment23(a),rr=typeof playerRoles==='function'?playerRoles(p,fantasyMode):[];const price=a?.price??a?.purchase_price??a?.amount??'—';return `<div class="v23-mobile-row"><div><span>${(rr.length?rr:[role]).map(r=>`<i class="rolebadge">${esc23(r)}</i>`).join('')}</span><strong>${esc23(p?.name||a?.player_name||'Giocatore')}</strong><small>${esc23(p?.serie_a_team||'')} · ${esc23(price)} cr</small></div></div>`});for(let i=group.length;i<total;i++)out.push(`<div class="v23-mobile-row is-empty"><div><span><i class="rolebadge">${role}</i></span><strong>Slot libero</strong><small>${labels[role]}</small></div></div>`);return `<section class="v34-mobile-roster-group"><header class="v34-mobile-roster-group-head"><span class="rolebadge" data-role="${role}">${role}</span><strong>${labels[role]}</strong><small>${group.length}/${required}</small></header>${out.join('')}</section>`}).join('');
  }
  function fuzzy23'''
t, legacy_count = legacy_roster_pattern.subn(legacy_roster_replacement, t)
if legacy_count < 1:
    raise SystemExit('renderRoster23 source not found')

style = r'''
<style id="v34d-header-mobile-roster-style">
/* Desktop live auction: keep the global top header. Only the old fixed live
   status banner remains removed by V34. The sidebar stays hidden in live mode. */
@media(min-width:851px){
  body.auction-live.modern-glass #app-shell.app{
    grid-template-columns:minmax(0,1fr)!important;
    grid-template-rows:var(--topbar) minmax(0,1fr)!important;
  }
  body.auction-live.modern-glass .app-head.modern-topbar,
  body.auction-live .app-head{
    display:flex!important;
    grid-column:1!important;
    grid-row:1!important;
  }
  body.auction-live.modern-glass .workspace{
    grid-column:1!important;
    grid-row:2!important;
    min-height:0!important;
    height:auto!important;
    padding:0!important;
    overflow:hidden!important;
  }
}

/* Phone navigation: hard final authority. Admin, President and every other role
   get exactly the same three visible app tabs. */
@media(max-width:850px){
  #main-nav .nav-btn,
  body.modern-glass #main-nav .nav-btn{display:none!important}
  #main-nav .nav-btn[data-view="list"],
  #main-nav .nav-btn[data-view="rosters"],
  #main-nav .nav-btn[data-view="auction"],
  body.modern-glass #main-nav .nav-btn[data-view="list"],
  body.modern-glass #main-nav .nav-btn[data-view="rosters"],
  body.modern-glass #main-nav .nav-btn[data-view="auction"]{display:grid!important}
  .modern-command-item[data-modern-route]:not([data-modern-route="list"]):not([data-modern-route="rosters"]):not([data-modern-route="auction"]){display:none!important}

  .v34-mobile-roster-group{display:grid!important;gap:3px!important;margin:0 0 7px!important;min-width:0!important}
  .v34-mobile-roster-group:last-child{margin-bottom:0!important}
  .v34-mobile-roster-group-head{
    position:sticky!important;top:0!important;z-index:2!important;
    display:grid!important;grid-template-columns:26px minmax(0,1fr) auto!important;align-items:center!important;gap:5px!important;
    min-height:27px!important;padding:3px 6px!important;border:1px solid var(--line2)!important;border-radius:7px!important;
    background:#0b2b50!important;color:var(--text)!important;
  }
  .v34-mobile-roster-group-head strong{font-size:8px!important;letter-spacing:.07em!important}
  .v34-mobile-roster-group-head small{font-size:8px!important;color:var(--soft)!important;font-variant-numeric:tabular-nums!important}
  .v23-mobile-roster-row.is-empty,.v23-mobile-row.is-empty{opacity:.43!important;border-style:dashed!important;background:rgba(8,29,50,.38)!important}
  .v23-mobile-roster-row.is-empty strong,.v23-mobile-row.is-empty strong{font-weight:700!important;color:var(--soft)!important}
}
</style>
'''

runtime = r'''
<script id="v34d-header-mobile-roster-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V34D_HEADER_MOBILE_ROSTER__)return;
  window.__FANTA_V34D_HEADER_MOBILE_ROSTER__=1;
  const mq=window.matchMedia('(max-width:850px)');
  function enforcePhoneNav34d(){
    const buttons=[...document.querySelectorAll('#main-nav .nav-btn[data-view]')];
    buttons.forEach(button=>{
      if(!mq.matches){button.style.removeProperty('display');return}
      const allowed=['list','rosters','auction'].includes(String(button.dataset.view||''));
      button.style.setProperty('display',allowed?'grid':'none','important');
      button.setAttribute('aria-hidden',allowed?'false':'true');
    });
  }
  mq.addEventListener?.('change',enforcePhoneNav34d);
  window.addEventListener('hashchange',enforcePhoneNav34d);
  document.addEventListener('DOMContentLoaded',enforcePhoneNav34d,{once:true});
  const obs=new MutationObserver(()=>requestAnimationFrame(enforcePhoneNav34d));
  obs.observe(document.documentElement,{subtree:true,childList:true});
  enforcePhoneNav34d();
})();
</script>
'''

if '</head>' not in t or '</body>' not in t:
    raise SystemExit('HTML closing tags not found')
t = t.replace('</head>', style + '\n</head>', 1)
t = t.replace('</body>', runtime + '\n</body>', 1)

p.write_text(t, encoding='utf-8')
print('patched', {'console':console_count,'summary':summary_count,'mobile_roster':mobile_count,'legacy_roster':legacy_count})
