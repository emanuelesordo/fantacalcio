from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def replace_once(old, new, label):
    global text
    if new in text:
        print(f'{label}: already applied')
        return
    if old not in text:
        raise SystemExit(f'{label}: target not found')
    text = text.replace(old, new, 1)
    print(f'{label}: patched')


# 1) V34 cockpit: keep the live workspace inside the viewport.
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
if not style_match:
    raise SystemExit('V34 style block not found')
style = style_match.group(2)

old_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:minmax(0,1fr) auto!important}'
new_rows = 'body.auction-live #view-auction .auction-cockpit{grid-template-rows:auto minmax(0,1fr)!important}'
if old_rows in style:
    style = style.replace(old_rows, new_rows, 1)
elif new_rows not in style:
    raise SystemExit('V34 cockpit rows target not found')

style, n_header = re.subn(
    r'(\.auction-rosters-accordion-header\s*\{\s*)grid-row:2!important;',
    r'\1grid-row:1!important;',
    style,
    count=1,
    flags=re.S,
)
if not n_header and 'grid-row:1!important' not in style:
    raise SystemExit('V34 accordion row target not found')

stage_pattern = r'(\.auction-cockpit-stage[^\{]*\{[^\}]*?)grid-row:3!important;'
style, n_stage = re.subn(stage_pattern, r'\1grid-row:2!important;', style, count=1, flags=re.S)
if not n_stage:
    # Current selector is grouped with the overlay; accept an already-patched block.
    if not re.search(r'\.auction-cockpit-stage[^\{]*\{[^\}]*grid-row:2!important;', style, re.S):
        raise SystemExit('V34 cockpit stage row target not found')

exit_css = '''
/* V38 · desktop exit from live auction. Mobile keeps its existing back control. */
#auction-live-exit-btn{display:none}
body.auction-live #auction-live-exit-btn{display:inline-flex}
@media(max-width:850px){body.auction-live #auction-live-exit-btn{display:none!important}}
'''
if '#auction-live-exit-btn' not in style:
    style += exit_css

text = text[:style_match.start(2)] + style + text[style_match.end(2):]

# 2) The auctioneer drawer must remain user-collapsible, also during prestart hold.
console_pattern = re.compile(
    r'\$\{prestartHold\s*\|\|\s*state\.auctionAdminConsoleOpen\s*\?\s*(["\'])open\1\s*:\s*(["\'])\2\s*\}'
)
text, n_console = console_pattern.subn('${state.auctionAdminConsoleOpen ? "open" : ""}', text, count=1)
if not n_console and '${state.auctionAdminConsoleOpen ? "open" : ""}' not in text:
    raise SystemExit('Auctioneer drawer open-condition target not found')

# 3) Restore a desktop control to leave live auction and return to the tabs.
league_button = '<button id="league-switch-btn" class="secondary" type="button">Leghe</button>'
exit_button = '<button id="auction-live-exit-btn" class="secondary" type="button" title="Torna alle tab">← TAB</button>'
if exit_button not in text:
    if league_button not in text:
        raise SystemExit('Header league button target not found')
    text = text.replace(league_button, exit_button + '\n        ' + league_button, 1)

league_listener = """    $('league-switch-btn')
      .addEventListener(
        'click',
        () =>
          switchView('leagues')
      );"""
exit_listener = """    $('auction-live-exit-btn')
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
    if league_listener not in text:
        raise SystemExit('League switch listener target not found')
    text = text.replace(league_listener, exit_listener + league_listener, 1)

# 4) V34 market context: never perform a timed full render of all auction cards.
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

interval = "  setInterval(()=>{if(state.view==='auction'&&session34()?.status==='live')void loadMarket34();},5000);\n"
if interval in runtime:
    runtime = runtime.replace(interval, "  /* V38: no periodic full live-card refresh. */\n", 1)
elif 'V38: no periodic full live-card refresh' not in runtime:
    raise SystemExit('V34 periodic market refresh target not found')

if 'window.loadMarket34=loadMarket34;' not in runtime:
    anchor = '\n  function marketStats34(p){'
    if anchor not in runtime:
        raise SystemExit('marketStats34 anchor not found')
    runtime = runtime.replace(anchor, '\n  window.loadMarket34=loadMarket34;\n' + anchor, 1)

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]

# 5) When a confirmed structural auction event arrives, refresh market context
#    before the normal canonical full render. Hot bid/timer events remain DOM-only.
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
