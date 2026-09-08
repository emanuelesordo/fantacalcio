from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# 1) Restore the original live cockpit flow and make cards
#    shrink with the viewport instead of imposing old minima.
# ==========================================================
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

bad_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:auto minmax(0,1fr)!important}'
good_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:minmax(0,1fr) auto!important}'
if bad_rows in style:
    style = style.replace(bad_rows, good_rows, 1)
elif good_rows not in style:
    raise SystemExit('V34 cockpit row declaration not found')

# Remove the V38 layout override that reordered stage/accordion and added TAB.
style = re.sub(
    r'\n/\* V38 · live viewport \+ desktop exit control\. \*/.*?@media\(max-width:850px\)\{body\.auction-live #auction-live-exit-btn\{display:none!important\}\}\n?',
    '\n',
    style,
    count=1,
    flags=re.S,
)

v39_css = r'''
/* V39 · restore original live flow and harden responsive cards. */
body.auction-live #view-auction .auction-back-live{
  display:inline-flex!important;
  position:absolute!important;
  top:5px!important;
  left:5px!important;
  z-index:120!important;
}
body.auction-live #view-auction .auction-root{
  padding-top:38px!important;
}
body.auction-live #view-auction :is(
  .auction-cockpit,
  .auction-cockpit-stage,
  .auction-cockpit-stage-grid,
  .auction-lower-stage,
  .auction-lower-main,
  .auction-team-column,
  .auction-middle-column,
  .auction-free-fixed,
  .auction-team-roster,
  .auction-call-queue,
  .auction-bid-history,
  .auction-suggested-calls,
  .auction-suggested-list,
  .auction-suggested-row
){
  min-width:0!important;
  max-width:100%!important;
}
body.auction-live #view-auction .auction-lower-main{
  width:100%!important;
  min-width:0!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-lower-main>*{
  min-width:0!important;
  max-width:100%!important;
}
body.auction-live #view-auction .auction-free-fixed .player-table{
  width:100%!important;
  min-width:0!important;
  max-width:100%!important;
  table-layout:fixed!important;
}
body.auction-live #view-auction .auction-free-fixed .player-main,
body.auction-live #view-auction .auction-free-fixed .player-name,
body.auction-live #view-auction .auction-queue-player,
body.auction-live #view-auction .auction-suggested-copy{
  min-width:0!important;
  max-width:100%!important;
}
body.auction-live #view-auction .auction-free-fixed .player-name,
body.auction-live #view-auction .auction-queue-player strong,
body.auction-live #view-auction .auction-suggested-copy strong{
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  white-space:nowrap!important;
}
@media(min-width:1101px){
  html:not(:fullscreen) body.auction-live #view-auction .auction-lower-main{
    grid-template-columns:
      minmax(0,.75fr)
      minmax(0,.80fr)
      minmax(0,1.60fr)
      auto!important;
  }
}
@media(min-width:851px) and (max-width:1100px){
  html:not(:fullscreen) body.auction-live #view-auction .auction-lower-main{
    grid-template-columns:
      minmax(0,.70fr)
      minmax(0,.75fr)
      minmax(0,1.55fr)
      auto!important;
  }
  html:not(:fullscreen) body.auction-live #view-auction
    .auction-lower-main>.auctioneer-console-drawer[open]{
    width:clamp(240px,26vw,300px)!important;
    min-width:0!important;
    max-width:300px!important;
  }
}
@media(min-width:701px) and (max-width:850px){
  html:not(:fullscreen) body.auction-live #view-auction .auction-lower-main{
    grid-template-columns:
      minmax(0,.75fr)
      minmax(0,1.25fr)
      auto!important;
  }
  html:not(:fullscreen) body.auction-live #view-auction
    .auction-lower-main>.auctioneer-console-drawer[open]{
    width:clamp(220px,30vw,255px)!important;
    min-width:0!important;
    max-width:255px!important;
  }
}
'''
if '/* V39 · restore original live flow and harden responsive cards. */' not in style:
    style += v39_css

text = text[:style_match.start(2)] + style + text[style_match.end(2):]


# ==========================================================
# 2) Use the original left-side back button. Remove the V38
#    header TAB control and its listener entirely.
# ==========================================================
text = re.sub(
    r'\n\s*<button id="auction-live-exit-btn"[^>]*>← TAB</button>',
    '',
    text,
    count=1,
)
text = re.sub(
    r"\n\s*\$\('auction-live-exit-btn'\)\s*\.addEventListener\(\s*'click',\s*\(\)\s*=>\s*\{.*?switchView\('home'\);\s*\}\s*\);\s*",
    '\n',
    text,
    count=1,
    flags=re.S,
)

# ==========================================================
# 3) Remove player-facing server-status chrome/copy.
# ==========================================================
text = text.replace(
    '        <span class="modern-status-pill"><i></i> Server autorevole</span>\n',
    '',
    1,
)
text = text.replace(
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo collegato allo stato autorevole del server.' },",
    "auction: { title: 'Asta live', subtitle: 'Cockpit operativo dell’asta in corso.' },",
    1,
)


# ==========================================================
# 4) Banditore: prestart must NOT force-open the <details>.
#    The existing native toggle listener owns open/closed state.
# ==========================================================
runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

forced_console = re.compile(
    r"  function console34\(\)\{\n"
    r"    const d=qs\('#auctioneer-console-drawer'\);if\(!d\)return;\n"
    r"    const pre=session34\(\)\?\.prestart_hold===true;\n"
    r"    if\(pre\)\{\n"
    r"      if\(!d\.open\)d\.open=true;\n"
    r"      state\.auctionAdminConsoleOpen=true;\n"
    r"      state\.v34AuctioneerOpen=true;\n"
    r"      return;\n"
    r"    \}\n"
    r"    /\* Native <details> \+ the existing toggle listener own the state\. \*/\n"
    r"    state\.v34AuctioneerOpen=d\.open===true;\n"
    r"  \}"
)
replacement_console = """  function console34(){
    const d=qs('#auctioneer-console-drawer');if(!d)return;
    /* Native <details> + the existing toggle listener own the state, also prestart. */
    state.v34AuctioneerOpen=d.open===true;
  }"""
runtime, n_console = forced_console.subn(replacement_console, runtime, count=1)
if not n_console and 'const pre=session34()?.prestart_hold===true;' in runtime:
    raise SystemExit('V34 forced prestart console block not patched')

# Keep the previous live-refresh stability changes.
require('async function loadMarket34(force=false,renderAfter=true)' in runtime,
        'loadMarket34 renderAfter protection missing')
require('/* V38: no periodic full live-card refresh. */' in runtime,
        'periodic full live refresh protection missing')
require('window.loadMarket34=loadMarket34;' in runtime,
        'loadMarket34 export missing')

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# ==========================================================
# 5) Regression assertions. Fail the workflow instead of
#    committing a partial patch.
# ==========================================================
style_check = re.search(r'<style id="v34-market-strategy-style">(.*?)</style>', text, re.S)
runtime_check = re.search(r'<script id="v34-market-strategy-runtime">(.*?)</script>', text, re.S)
require(style_check and runtime_check, 'post-patch V34 blocks missing')
style_final = style_check.group(1)
runtime_final = runtime_check.group(1)

checks = {
    'original left back button markup': 'id="auction-back-live"' in text,
    'original left back button listener': "$('auction-back-live')" in text and "switchView('home')" in text,
    'header TAB button removed': 'auction-live-exit-btn' not in text,
    'server status pill removed': 'Server autorevole' not in text,
    'server status subtitle removed': 'stato autorevole del server' not in text,
    'original V34 cockpit row order': good_rows in style_final,
    'V38 row override removed': '/* V38 · live viewport + desktop exit control. */' not in style_final,
    'V39 responsive hardening': '/* V39 · restore original live flow and harden responsive cards. */' in style_final,
    'left back button forced visible': 'body.auction-live #view-auction .auction-back-live{' in style_final,
    'prestart force-open removed': 'const pre=session34()?.prestart_hold===true;' not in runtime_final,
    'market full refresh timer still removed': '/* V38: no periodic full live-card refresh. */' in runtime_final,
}
failed = [name for name, ok in checks.items() if not ok]
require(not failed, 'Regression assertions failed: ' + ', '.join(failed))
print('Regression assertions passed:', ', '.join(checks))

if text == original:
    print('V39: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V39 live navigation/responsive patch applied')
