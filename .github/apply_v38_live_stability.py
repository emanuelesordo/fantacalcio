from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V40 · GOLDEN RULE
# The live auction must never grow beyond its viewport.
# Large contents scroll inside their own cards; fixed operational
# regions (roster, current call, queue, last bids, free agents,
# suggester, auctioneer) must remain simultaneously reachable.
# ==========================================================
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

# Remove the V39 patch that reintroduced an implicit third cockpit row
# and added a separate 38px strip for the back button.
style = re.sub(
    r'\n/\* V39 · restore original live flow and harden responsive cards\. \*/.*?(?=\n</style>|\Z)',
    '\n',
    style,
    count=1,
    flags=re.S,
)

# V34 hides the old statusbar. Therefore the cockpit has TWO real rows:
# 1) teams/rosters accordion strip; 2) the live stage.
style = re.sub(
    r'body\.auction-live #view-auction \.auction-cockpit\{grid-template-rows:[^}]+\}',
    'body.auction-live #view-auction .auction-cockpit{grid-template-rows:42px minmax(0,1fr)!important}',
    style,
    count=1,
)

v40_css = r'''
/* V40 · compact live viewport baseline. */

/* The back control belongs to the app header, never to a separate live row. */
#auction-back-live{display:none}
body.auction-live #auction-back-live{
  display:inline-flex!important;
  position:static!important;
  inset:auto!important;
  z-index:auto!important;
  min-height:30px!important;
  height:30px!important;
  padding:4px 9px!important;
  margin:0 7px 0 0!important;
  flex:0 0 auto!important;
  box-shadow:none!important;
}
body.auction-live #view-auction .auction-root{padding-top:0!important}

/* V34 removes the old statusbar: strip + stage are the only cockpit rows. */
body.auction-live #view-auction .auction-cockpit{
  grid-template-columns:minmax(0,1fr)!important;
  grid-template-rows:42px minmax(0,1fr)!important;
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  padding:0!important;
  gap:3px!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-rosters-accordion-header{
  grid-column:1!important;
  grid-row:1!important;
  min-height:0!important;
  height:42px!important;
  max-height:42px!important;
}
body.auction-live #view-auction .auction-cockpit-stage,
body.auction-live #view-auction .auction-rosters-overlay{
  grid-column:1!important;
  grid-row:2!important;
  min-height:0!important;
  max-height:100%!important;
}

/* Hard viewport containment: no live region may increase page height. */
body.auction-live #view-auction,
body.auction-live #view-auction .auction-root,
body.auction-live #view-auction .auction-live-shell,
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

/* ROSA: card fixed to its column; only the player list scrolls. */
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

/* CENTRO: preserve the last-bids card at the bottom; queue absorbs free height. */
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

/* SVINCOLATI + CONSULENTE: table owns the flexible row, suggester stays visible. */
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
  max-height:170px!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-free-suggestions .auction-suggested-calls{
  height:auto!important;
  min-height:0!important;
  max-height:170px!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-free-suggestions .auction-suggested-list{
  min-height:0!important;
  max-height:138px!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
}

/* Text can shrink; names never make a column wider than the viewport budget. */
body.auction-live #view-auction :is(
  .auction-team-column,
  .auction-middle-column,
  .auction-free-fixed,
  .auction-call-queue,
  .auction-bid-history,
  .auction-suggested-calls,
  .auction-suggested-list,
  .auction-suggested-row,
  .auction-player-name-live,
  .auction-queue-player,
  .auction-suggested-copy
){min-width:0!important;max-width:100%!important}
body.auction-live #view-auction :is(
  .auction-queue-player strong,
  .auction-suggested-copy strong,
  .auction-free-fixed .player-name
){overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}

/* Short desktop viewport: compact non-essential vertical whitespace, keep cards present. */
@media(min-width:701px) and (max-height:760px){
  body.auction-live #view-auction .auction-cockpit{
    grid-template-rows:38px minmax(0,1fr)!important;
  }
  body.auction-live #view-auction .auction-rosters-accordion-header{
    height:38px!important;
    max-height:38px!important;
  }
  body.auction-live #view-auction .auction-middle-column .auction-bid-history{
    flex-basis:68px!important;
    min-height:68px!important;
    max-height:86px!important;
  }
  body.auction-live #view-auction .auction-free-suggestions,
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-calls{
    max-height:142px!important;
  }
  body.auction-live #view-auction .auction-free-suggestions .auction-suggested-list{
    max-height:112px!important;
  }
}

/* Phone/tablet rules below 700px remain owned by the dedicated mobile layout. */
'''
style += v40_css
text = text[:style_match.start(2)] + style + text[style_match.end(2):]


# ==========================================================
# Header navigation: move the original button into the header.
# Keep the original ID/listener and use the compact label from
# the known-good layout screenshot.
# ==========================================================
view_button_re = re.compile(
    r'\n\s*<button id="auction-back-live" class="auction-back-live secondary" type="button">[^<]*</button>'
)
text, removed = view_button_re.subn('', text, count=1)
require(removed == 1 or 'id="auction-back-live"' in text,
        'live back button markup not found')

# If a previous attempt already moved it, avoid duplicating it.
if 'id="auction-back-live"' not in text:
    header_anchor = '        <div class="modern-title-line">\n          <h1 id="modern-page-title">Le mie leghe</h1>'
    header_replacement = (
        '        <div class="modern-title-line">\n'
        '          <button id="auction-back-live" class="auction-back-live secondary" type="button">← Lega</button>\n'
        '          <h1 id="modern-page-title">Le mie leghe</h1>'
    )
    require(header_anchor in text, 'modern header title anchor not found')
    text = text.replace(header_anchor, header_replacement, 1)
else:
    # Existing button must be in the header, not in #view-auction.
    before_auction = text.split('<!-- ASTA -->', 1)[0]
    if 'id="auction-back-live"' not in before_auction:
        # Remove any remaining copy and insert one canonical header copy.
        text = re.sub(r'\s*<button id="auction-back-live"[^>]*>[^<]*</button>', '', text, count=1)
        header_anchor = '        <div class="modern-title-line">\n          <h1 id="modern-page-title">Le mie leghe</h1>'
        header_replacement = (
            '        <div class="modern-title-line">\n'
            '          <button id="auction-back-live" class="auction-back-live secondary" type="button">← Lega</button>\n'
            '          <h1 id="modern-page-title">Le mie leghe</h1>'
        )
        require(header_anchor in text, 'modern header title anchor not found')
        text = text.replace(header_anchor, header_replacement, 1)

# Normalize label if the header already contained a prior version.
text = re.sub(
    r'(<button id="auction-back-live" class="auction-back-live secondary" type="button">)[^<]*(</button>)',
    r'\1← Lega\2',
    text,
    count=1,
)


# ==========================================================
# Keep server-status chrome removed and the prestart drawer fix.
# ==========================================================
text = text.replace('        <span class="modern-status-pill"><i></i> Server autorevole</span>\n', '', 1)
text = text.replace(
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo collegato allo stato autorevole del server.' },",
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo dell’asta in corso.' },",
    1,
)

runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

# Remove any remaining prestart force-open logic, including older spellings.
runtime = re.sub(
    r"\n\s*const pre=session34\(\)\?\.prestart_hold===true;\n\s*if\(pre\)\{.*?\n\s*\}\n",
    '\n',
    runtime,
    count=1,
    flags=re.S,
)
require('prestart_hold===true' not in runtime or 'd.open=true' not in runtime,
        'prestart console force-open still present')

# Preserve the successful refresh policy: only hot call/bid state updates continuously.
require('async function loadMarket34(force=false,renderAfter=true)' in runtime,
        'loadMarket34 renderAfter protection missing')
require('/* V38: no periodic full live-card refresh. */' in runtime,
        'periodic full live refresh protection missing')
require('window.loadMarket34=loadMarket34;' in runtime,
        'loadMarket34 export missing')

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# ==========================================================
# Regression assertions: fail instead of committing partial UI.
# ==========================================================
style_check = re.search(r'<style id="v34-market-strategy-style">(.*?)</style>', text, re.S)
require(style_check, 'post-patch V34 style block missing')
style_final = style_check.group(1)

header_pos = text.find('<header class="app-head modern-topbar">')
back_pos = text.find('id="auction-back-live"')
title_pos = text.find('id="modern-page-title"')
view_pos = text.find('<section id="view-auction"')
require(0 <= header_pos < back_pos < title_pos < view_pos,
        'back button is not in the left header title line')
require(text.count('id="auction-back-live"') == 1,
        'back button must exist exactly once')
require("$('auction-back-live')" in text and "switchView('home')" in text,
        'back button listener missing')

checks = {
    'V39 override removed': '/* V39 · restore original live flow and harden responsive cards. */' not in style_final,
    'V40 baseline present': '/* V40 · compact live viewport baseline. */' in style_final,
    'two-row cockpit': 'grid-template-rows:42px minmax(0,1fr)!important' in style_final,
    'roster strip row 1': '.auction-rosters-accordion-header' in style_final and 'grid-row:1!important' in style_final,
    'live stage row 2': '.auction-cockpit-stage' in style_final and 'grid-row:2!important' in style_final,
    'no separate back-button padding': 'body.auction-live #view-auction .auction-root{padding-top:0!important}' in style_final,
    'roster scroll containment': '.auction-team-roster-list' in style_final and 'overflow-y:auto!important' in style_final,
    'last bids reserved': '.auction-bid-history' in style_final and 'min-height:72px!important' in style_final,
    'suggester reserved': '.auction-free-suggestions' in style_final and 'max-height:170px!important' in style_final,
    'server status removed': 'Server autorevole' not in text and 'stato autorevole del server' not in text,
    'periodic full refresh removed': '/* V38: no periodic full live-card refresh. */' in text,
}
failed = [name for name, ok in checks.items() if not ok]
require(not failed, 'Regression assertions failed: ' + ', '.join(failed))
print('Regression assertions passed:', ', '.join(checks))

if text == original:
    print('V40: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V40 compact live viewport patch applied')
