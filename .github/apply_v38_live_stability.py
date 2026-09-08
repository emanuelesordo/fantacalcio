from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V41 · operational live cockpit baseline
# - old compact KPI header restored
# - no global app chrome beside/above the live cockpit
# - viewport remains a hard boundary
# - strategist uses dense 2-column rows
# - auction Index signal uses the exact same formula/colors as Listone
# ==========================================================
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

# Remove the previous V40 override wholesale; V41 replaces it with the
# screenshot-proven three-row geometry: KPI header | teams strip | stage.
style = re.sub(
    r'\n/\* V40 · compact live viewport baseline\. \*/.*?(?=\n</style>|\Z)',
    '\n',
    style,
    count=1,
    flags=re.S,
)

# Keep V34's base declaration harmless; desktop V41 owns the real rows.
style = re.sub(
    r'body\.auction-live #view-auction \.auction-cockpit\{grid-template-rows:[^}]+\}',
    'body.auction-live #view-auction .auction-cockpit{grid-template-rows:minmax(0,1fr) auto!important}',
    style,
    count=1,
)

v41_css = r'''
/* V41 · compact KPI header + hard viewport cockpit. */

/* The legacy standalone button remains only as an event-binding fallback.
   The visible live back control is #auction-cockpit-back inside the KPI bar. */
#auction-back-live{display:none!important}
body.auction-live #view-auction .auction-root{padding-top:0!important}

/* Robust full-width live shell. :has() closes the race where auction-live can
   arrive one render later than the cockpit DOM. This also fixes fullscreen. */
body.auction-live.modern-glass #app-shell.app,
body.modern-glass:has(#view-auction.active .auction-cockpit) #app-shell.app{
  grid-template-columns:minmax(0,1fr)!important;
  grid-template-rows:minmax(0,1fr)!important;
  height:100dvh!important;
  min-height:100dvh!important;
}
body.auction-live.modern-glass .app-head.modern-topbar,
body.auction-live.modern-glass #main-nav.modern-sidebar,
body.modern-glass:has(#view-auction.active .auction-cockpit) .app-head.modern-topbar,
body.modern-glass:has(#view-auction.active .auction-cockpit) #main-nav.modern-sidebar{
  display:none!important;
}
body.auction-live.modern-glass .workspace,
body.modern-glass:has(#view-auction.active .auction-cockpit) .workspace{
  grid-column:1!important;
  grid-row:1!important;
  width:100%!important;
  height:100dvh!important;
  min-width:0!important;
  min-height:0!important;
  padding:0!important;
  overflow:hidden!important;
}

/* Desktop live cockpit: KPI header, teams strip, remaining viewport. */
@media(min-width:701px){
  body.auction-live #view-auction .auction-statusbar{
    display:grid!important;
    grid-column:1!important;
    grid-row:1!important;
    height:38px!important;
    min-height:38px!important;
    max-height:38px!important;
    padding:3px 5px!important;
    gap:4px!important;
    overflow:hidden!important;
    grid-template-columns:auto minmax(118px,.58fr) minmax(0,2.2fr) minmax(170px,auto)!important;
  }
  body.auction-live #view-auction .auction-statusbar .back-live,
  body.auction-live #view-auction .auction-statusbar .auction-immersion-live{
    height:30px!important;
    min-height:30px!important;
    padding-block:2px!important;
  }
  body.auction-live #view-auction .auction-status-team-kpis{
    min-width:0!important;
    grid-template-columns:minmax(74px,1.08fr) repeat(7,minmax(44px,.68fr))!important;
    gap:3px!important;
  }
  body.auction-live #view-auction .auction-status-team-kpis>span{
    height:28px!important;
    min-height:28px!important;
    padding:2px 5px!important;
  }
  body.auction-live #view-auction .auction-status-team-kpis small{
    font-size:5.5px!important;
    line-height:1!important;
  }
  body.auction-live #view-auction .auction-status-team-kpis b{
    font-size:9px!important;
    line-height:1!important;
  }
  body.auction-live #view-auction .auction-cockpit{
    grid-template-columns:minmax(0,1fr)!important;
    grid-template-rows:38px 38px minmax(0,1fr)!important;
    height:100%!important;
    min-height:0!important;
    max-height:100%!important;
    padding:0!important;
    gap:3px!important;
    overflow:hidden!important;
  }
  body.auction-live #view-auction .auction-rosters-accordion-header{
    grid-column:1!important;
    grid-row:2!important;
    height:38px!important;
    min-height:38px!important;
    max-height:38px!important;
  }
  body.auction-live #view-auction .auction-cockpit-stage,
  body.auction-live #view-auction .auction-rosters-overlay{
    grid-column:1!important;
    grid-row:3!important;
    min-height:0!important;
    max-height:100%!important;
  }
}

/* Mobile keeps the dedicated mobile auction layout and the statusbar hidden. */
@media(max-width:700px){
  body.auction-live #view-auction .auction-statusbar{display:none!important}
  body.auction-live #view-auction .auction-cockpit{
    grid-template-rows:38px minmax(0,1fr)!important;
    min-height:0!important;
    overflow:hidden!important;
  }
  body.auction-live #view-auction .auction-rosters-accordion-header{
    grid-row:1!important;
    height:38px!important;
    min-height:38px!important;
    max-height:38px!important;
  }
  body.auction-live #view-auction .auction-cockpit-stage,
  body.auction-live #view-auction .auction-rosters-overlay{grid-row:2!important;min-height:0!important}
}

/* Hard viewport containment: content may scroll inside its own card only. */
body.auction-live #view-auction,
body.auction-live #view-auction .auction-root,
body.auction-live #view-auction .auction-live-shell,
body.auction-live #view-auction .auction-cockpit,
body.auction-live #view-auction .auction-cockpit-stage,
body.auction-live #view-auction .auction-cockpit-stage-grid,
body.auction-live #view-auction .auction-lower-stage,
body.auction-live #view-auction .auction-lower-main{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-lower-main{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  align-items:stretch!important;
}
body.auction-live #view-auction .auction-lower-main>*{
  min-width:0!important;
  min-height:0!important;
  max-width:100%!important;
  max-height:100%!important;
}

/* ROSA: fixed card, internal list scroll. */
body.auction-live #view-auction .auction-team-column-roster-only,
body.auction-live #view-auction .auction-team-column-roster-only>.auction-team-roster{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-team-column-roster-only>.auction-team-roster{
  display:grid!important;
  grid-template-rows:auto minmax(0,1fr)!important;
}
body.auction-live #view-auction .auction-team-column-roster-only .auction-team-roster-list{
  height:auto!important;
  min-height:0!important;
  max-height:100%!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  overscroll-behavior:contain!important;
}

/* CENTRE: queue flexes, last bids never disappear. */
body.auction-live #view-auction .auction-middle-column{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-middle-column .auction-central-queue{
  min-height:0!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-middle-column .auction-bid-history{
  flex:0 0 clamp(72px,10vh,108px)!important;
  min-height:72px!important;
  max-height:108px!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-middle-column .auction-bid-history-list{
  min-height:0!important;
  max-height:100%!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
}

/* FREE AGENTS + STRATEGIST: table flexes, 4 normal suggestions = 2x2 dense rows. */
body.auction-live #view-auction .auction-free-fixed{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
  grid-template-rows:auto auto minmax(0,1fr) auto!important;
}
body.auction-live #view-auction .auction-free-fixed .drawer-table,
body.auction-live #view-auction .auction-free-fixed .table-wrap{
  min-height:0!important;
  max-height:100%!important;
  overflow:auto!important;
}
body.auction-live #view-auction .auction-free-suggestions{
  min-height:0!important;
  max-height:126px!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-free-suggestions .auction-suggested-calls{
  height:auto!important;
  min-height:0!important;
  max-height:126px!important;
  overflow:hidden!important;
}
@media(min-width:701px){
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-list{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-auto-flow:row!important;
    grid-auto-rows:44px!important;
    align-content:start!important;
    gap:4px!important;
    min-height:0!important;
    max-height:92px!important;
    overflow:hidden!important;
  }
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-row{
    height:44px!important;
    min-height:44px!important;
    max-height:44px!important;
    padding:4px 5px!important;
    overflow:hidden!important;
  }
  :fullscreen body.auction-live #view-auction .auction-free-suggestions,
  :fullscreen body.auction-live #view-auction .auction-free-suggestions .auction-suggested-calls{
    max-height:180px!important;
  }
  :fullscreen body.auction-live #view-auction .auction-free-suggestions .auction-suggested-list{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-auto-rows:36px!important;
    max-height:156px!important;
  }
  :fullscreen body.auction-live #view-auction .auction-free-suggestions .auction-suggested-row{
    height:36px!important;
    min-height:36px!important;
    max-height:36px!important;
  }
}

/* Text can shrink; identities never widen their grid columns. */
body.auction-live #view-auction :is(
  .auction-team-column,.auction-middle-column,.auction-free-fixed,
  .auction-call-queue,.auction-bid-history,.auction-suggested-calls,
  .auction-suggested-list,.auction-suggested-row,.auction-player-name-live,
  .auction-queue-player,.auction-suggested-copy
){min-width:0!important;max-width:100%!important}
body.auction-live #view-auction :is(
  .auction-queue-player strong,.auction-suggested-copy strong,.auction-free-fixed .player-name
){overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}

/* Short desktop: preserve every operational card before reducing row density. */
@media(min-width:701px) and (max-height:760px){
  body.auction-live #view-auction .auction-statusbar,
  body.auction-live #view-auction .auction-rosters-accordion-header{
    height:34px!important;min-height:34px!important;max-height:34px!important;
  }
  body.auction-live #view-auction .auction-cockpit{
    grid-template-rows:34px 34px minmax(0,1fr)!important;
  }
  body.auction-live #view-auction .auction-middle-column .auction-bid-history{
    flex-basis:68px!important;min-height:68px!important;max-height:86px!important;
  }
  body.auction-live #view-auction .auction-free-suggestions,
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-calls{
    max-height:112px!important;
  }
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-list{
    grid-auto-rows:38px!important;max-height:80px!important;
  }
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-row{
    height:38px!important;min-height:38px!important;max-height:38px!important;
  }
}
'''
style += v41_css
text = text[:style_match.start(2)] + style + text[style_match.end(2):]


# ==========================================================
# Restore the fallback button to #view-auction. The visible live button is
# already inside .auction-statusbar (#auction-cockpit-back) with its own listener.
# ==========================================================
text = re.sub(r'\s*<button id="auction-back-live"[^>]*>[^<]*</button>', '', text, count=1)
auction_anchor = '      <section id="view-auction" class="view no-page-scroll">\n        <div id="auction-root" class="auction-root"></div>'
auction_replacement = (
    '      <section id="view-auction" class="view no-page-scroll">\n'
    '        <button id="auction-back-live" class="auction-back-live secondary" type="button">← Torna alla lega</button>\n'
    '        <div id="auction-root" class="auction-root"></div>'
)
require(auction_anchor in text, 'auction view anchor not found')
text = text.replace(auction_anchor, auction_replacement, 1)


# ==========================================================
# Remove all player-facing infrastructure/server status chrome and the ugly
# auction route subtitle. No server implementation details belong in the UI.
# ==========================================================
text = re.sub(
    r'\n\s*<div class="modern-sidebar-footer">\s*<span class="modern-sidebar-eyebrow">Stato</span>\s*<strong>Frontend statico</strong>\s*<small>Edge Functions \+ PostgreSQL</small>\s*<i></i>\s*</div>',
    '',
    text,
    count=1,
    flags=re.S,
)
text = text.replace('        <span class="modern-status-pill"><i></i> Server autorevole</span>\n', '', 1)
text = text.replace(
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo dell’asta in corso.' },",
    "auction: { title: 'Asta live', subtitle: '' },",
    1,
)
text = text.replace(
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo collegato allo stato autorevole del server.' },",
    "auction: { title: 'Asta live', subtitle: '' },",
    1,
)


# ==========================================================
# V34 runtime: live auction rows must use the exact V33/Listone Index signal.
# V34 previously repainted auction rows with a slightly different strength scale.
# ==========================================================
runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

paint_re = re.compile(r'  function paintDeal34\(root,players\)\{.*?\n  \}\n\n  function addUdColumn34', re.S)
paint_new = r'''  function paintDeal34(root,players){
    if(!root)return;
    const by=new Map((players||[]).map(p=>[String(p.id),p]));
    root.querySelectorAll('tr[data-player-id]').forEach(row=>{
      const p=by.get(String(row.dataset.playerId));if(!p)return;
      const idx=idx34(p),pma=num(p?.pma),pfc=num(p?.pfc);
      if(idx==null||(pma==null&&pfc==null))return;
      const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);
      const delta=idx-market;
      const scale=Math.max(8,Math.abs(idx),Math.abs(market));
      const relative=delta/scale;
      const strength=clamp(Math.abs(relative)/.35,0,1);
      const hue=relative>=0?52+(128-52)*strength:52*(1-strength);
      const alpha=.060+.115*strength;
      row.classList.remove('v30-index-market-row');
      row.classList.add('v33-index-market-row');
      row.style.removeProperty('--v30-market-hue');
      row.style.removeProperty('--v30-market-alpha');
      row.style.setProperty('--v33-market-hue',hue.toFixed(1));
      row.style.setProperty('--v33-market-alpha',alpha.toFixed(3));
      row.title=`Indice ${Math.round(idx)} cr · PFC/PMA medio ${market.toFixed(1)} · delta ${delta>=0?'+':''}${delta.toFixed(1)} cr`;
    });
  }

  function addUdColumn34'''
runtime, n_paint = paint_re.subn(paint_new, runtime, count=1)
require(n_paint == 1 or 'const scale=Math.max(8,Math.abs(idx),Math.abs(market));' in runtime,
        'V34 Index painter not patched')

# Keep the prestart drawer fix and refresh policy already validated.
runtime = re.sub(
    r"\n\s*const pre=session34\(\)\?\.prestart_hold===true;\n\s*if\(pre\)\{.*?\n\s*\}\n",
    '\n',
    runtime,
    count=1,
    flags=re.S,
)
require('async function loadMarket34(force=false,renderAfter=true)' in runtime,
        'loadMarket34 renderAfter protection missing')
require('/* V38: no periodic full live-card refresh. */' in runtime,
        'periodic full live refresh protection missing')
require('window.loadMarket34=loadMarket34;' in runtime,
        'loadMarket34 export missing')
text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# ==========================================================
# Regression assertions: a partial patch must fail the workflow.
# ==========================================================
style_check = re.search(r'<style id="v34-market-strategy-style">(.*?)</style>', text, re.S)
runtime_check = re.search(r'<script id="v34-market-strategy-runtime">(.*?)</script>', text, re.S)
require(style_check and runtime_check, 'post-patch V34 blocks missing')
style_final = style_check.group(1)
runtime_final = runtime_check.group(1)

checks = {
    'V40 override removed': '/* V40 · compact live viewport baseline. */' not in style_final,
    'V41 baseline present': '/* V41 · compact KPI header + hard viewport cockpit. */' in style_final,
    'desktop KPI statusbar visible': 'body.auction-live #view-auction .auction-statusbar{' in style_final and 'display:grid!important' in style_final,
    'three-row desktop cockpit': 'grid-template-rows:38px 38px minmax(0,1fr)!important' in style_final,
    'teams strip row 2': '.auction-rosters-accordion-header' in style_final and 'grid-row:2!important' in style_final,
    'stage row 3': '.auction-cockpit-stage' in style_final and 'grid-row:3!important' in style_final,
    'KPI markup still exists': 'auction-status-team-kpis' in text,
    'cockpit back markup/listener exists': 'id="auction-cockpit-back"' in text and "$('auction-cockpit-back')" in text,
    'fallback back remains bound': text.count('id="auction-back-live"') == 1 and "$('auction-back-live')" in text,
    'global live chrome race hardened': ':has(#view-auction.active .auction-cockpit)' in style_final,
    'strategist two columns': 'grid-template-columns:repeat(2,minmax(0,1fr))!important' in style_final,
    'strategist queue-like row height': 'grid-auto-rows:44px!important' in style_final and 'height:44px!important' in style_final,
    'roster internal scroll': '.auction-team-roster-list' in style_final and 'overflow-y:auto!important' in style_final,
    'last bids reserved': '.auction-bid-history' in style_final and 'min-height:72px!important' in style_final,
    'Listone/live Index formula aligned': 'const scale=Math.max(8,Math.abs(idx),Math.abs(market));' in runtime_final and "row.classList.add('v33-index-market-row')" in runtime_final,
    'route subtitle removed': "auction: { title: 'Asta live', subtitle: '' }," in text,
    'server chrome removed': all(s not in text for s in ['Server autorevole','stato autorevole del server','Frontend statico','Edge Functions + PostgreSQL']),
    'periodic full refresh removed': '/* V38: no periodic full live-card refresh. */' in runtime_final,
}
failed=[name for name,ok in checks.items() if not ok]
require(not failed, 'Regression assertions failed: '+', '.join(failed))
print('Regression assertions passed: '+', '.join(checks))

if text == original:
    print('V41: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V41 live KPI/header/strategist/index patch applied')
