from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


# 1) Live cockpit: reclaim the viewport without depending on older CSS row declarations.
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
if not style_match:
    raise SystemExit('V34 style block not found')
style = style_match.group(2)

old_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:minmax(0,1fr) auto!important}'
new_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:auto minmax(0,1fr)!important}'
if old_rows in style:
    style = style.replace(old_rows, new_rows, 1)

v38_css = '''
/* V38 · live viewport + desktop exit control. */
body.auction-live #view-auction .auction-cockpit{
  grid-template-rows:auto minmax(0,1fr)!important;
  min-height:0!important;
}
body.auction-live #view-auction .auction-rosters-accordion-header{
  grid-row:1!important;
}
body.auction-live #view-auction .auction-cockpit-stage{
  grid-row:2!important;
  min-height:0!important;
  overflow:hidden!important;
}
#auction-live-exit-btn{display:none}
body.auction-live #auction-live-exit-btn{display:inline-flex}
@media(max-width:850px){body.auction-live #auction-live-exit-btn{display:none!important}}
'''
if '/* V38 · live viewport + desktop exit control. */' not in style:
    style += v38_css

text = text[:style_match.start(2)] + style + text[style_match.end(2):]


# 2) The auctioneer drawer must be controlled only by the user's open/closed state.
console_pattern = re.compile(
    r'\$\{\s*(?:\(\s*)?prestartHold\s*\|\|\s*state\.auctionAdminConsoleOpen(?:\s*\))?\s*\?\s*(["\'])open\1\s*:\s*(["\'])\2\s*\}'
)
text, n_console = console_pattern.subn('${state.auctionAdminConsoleOpen ? "open" : ""}', text, count=1)
if n_console:
    print('auctioneer drawer: patched')
elif '${state.auctionAdminConsoleOpen ? "open" : ""}' in text:
    print('auctioneer drawer: already patched')
else:
    # Do not block the other live fixes if an older template uses a different spelling.
    print('auctioneer drawer: target spelling not found')


# 3) Desktop control to leave the live auction and return to the league tabs.
league_button = '<button id="league-switch-btn" class="secondary" type="button">Leghe</button>'
exit_button = '<button id="auction-live-exit-btn" class="secondary" type="button" title="Torna alle tab">← TAB</button>'
if exit_button not in text:
    if league_button not in text:
        raise SystemExit('Header league button target not found')
    text = text.replace(league_button, exit_button + '\n        ' + league_button, 1)

league_listener_pattern = re.compile(
    r"(\s*\$\('league-switch-btn'\)\s*\.addEventListener\(\s*'click',\s*\(\)\s*=>\s*switchView\('leagues'\)\s*\);)",
    re.S,
)
exit_listener = """
    $('auction-live-exit-btn')
      .addEventListener(
        'click',
        () => {
          state.auctionMobileDrawerOpen = false;
          clearAuctionTransient();
          switchView('home');
        }
      );
"""
if "$('auction-live-exit-btn')" not in text:
    m = league_listener_pattern.search(text)
    if not m:
        raise SystemExit('League switch listener target not found')
    text = text[:m.start()] + exit_listener + m.group(1) + text[m.end():]


# 4) V34 market context: remove the timer that was rebuilding every live card every 5 s.
runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
if not runtime_match:
    raise SystemExit('V34 runtime block not found')
runtime = runtime_match.group(2)

if 'async function loadMarket34(force=false,renderAfter=true)' not in runtime:
    if 'async function loadMarket34(force=false)' not in runtime:
        raise SystemExit('loadMarket34 signature target not found')
    runtime = runtime.replace(
        'async function loadMarket34(force=false)',
        'async function loadMarket34(force=false,renderAfter=true)',
        1,
    )

old_render = "if(typeof renderAuctionLive==='function'&&state.view==='auction')renderAuctionLive();"
new_render = "if(renderAfter&&typeof renderAuctionLive==='function'&&state.view==='auction')renderAuctionLive();"
if new_render not in runtime:
    if old_render not in runtime:
        raise SystemExit('loadMarket34 render target not found')
    runtime = runtime.replace(old_render, new_render, 1)

runtime, n_interval = re.subn(
    r"\s*setInterval\(\(\)=>\{if\(state\.view==='auction'&&session34\(\)\?\.status==='live'\)void loadMarket34\(\);\},5000\);",
    "\n  /* V38: no periodic full live-card refresh. */",
    runtime,
    count=1,
)
if not n_interval and 'V38: no periodic full live-card refresh' not in runtime:
    raise SystemExit('V34 periodic market refresh target not found')

if 'window.loadMarket34=loadMarket34;' not in runtime:
    anchor = '\n  function marketStats34(p){'
    if anchor not in runtime:
        raise SystemExit('marketStats34 anchor not found')
    runtime = runtime.replace(anchor, '\n  window.loadMarket34=loadMarket34;\n' + anchor, 1)

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# 5) Confirmed structural events refresh all dependent cards once.
#    Hot bid/timer events remain handled by patchAuctionLiveDynamic().
structural_anchor = """      if (structural) {
        /* Structural events change the shape of the whole auction view.
           Always reload the canonical auction payload; a hot patch is not enough. */
        await loadAuction({ quiet: true, onlyIfChanged: false });"""
structural_new = """      if (structural) {
        /* Structural events change the shape of the whole auction view.
           Always reload the canonical auction payload; a hot patch is not enough. */
        if (typeof window.loadMarket34 === 'function') {
          await window.loadMarket34(true, false);
        }
        await loadAuction({ quiet: true, onlyIfChanged: false });"""
if structural_new not in text:
    if structural_anchor not in text:
        raise SystemExit('Structural reconcile target not found')
    text = text.replace(structural_anchor, structural_new, 1)


if text == original:
    print('V38: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V38 live stability patch applied')
