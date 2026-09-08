from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(cond, msg):
    if not cond:
        raise SystemExit(msg)

# ----------------------------------------------------------
# 1) Live cockpit must stay inside the viewport.
# V34 hides the old status bar: explicitly realign the two
# remaining rows instead of allowing an implicit auto row.
# ----------------------------------------------------------
style_match = re.search(r'(<style id=["\']v34-market-strategy-style["\']>)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

v44_css = r'''
/* V44 · auction live emergency stability. */
body.auction-live #view-auction .auction-cockpit{
  grid-template-rows:auto minmax(0,1fr)!important;
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
body.auction-live #view-auction .auction-rosters-accordion-header{
  grid-row:1!important;
}
body.auction-live #view-auction .auction-cockpit-stage,
body.auction-live #view-auction .auction-rosters-overlay{
  grid-row:2!important;
  min-height:0!important;
  max-height:100%!important;
}
body.auction-live #view-auction .auction-lower-main{
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
#auction-live-exit-btn{display:none}
body.auction-live #auction-live-exit-btn{display:inline-flex!important;align-items:center;justify-content:center}
@media(max-width:850px){
  body.auction-live #auction-live-exit-btn{display:none!important}
}
'''

# Replace a previous V44 block if re-run, otherwise append.
style = re.sub(
    r'\n/\* V44 · auction live emergency stability\. \*/.*?(?=\n/\* V\d+|\Z)',
    '\n',
    style,
    count=1,
    flags=re.S,
)
style += v44_css
text = text[:style_match.start(2)] + style + text[style_match.end(2):]

# ----------------------------------------------------------
# 2) BANDITORE drawer: its open state belongs to the user.
# Never force it open just because the auction is in prestart.
# ----------------------------------------------------------
patterns = [
    (r'\$\{\s*prestartHold\s*\|\|\s*state\.auctionAdminConsoleOpen\s*\?\s*(["\'])open\1\s*:\s*(["\'])\2\s*\}',
     '${state.auctionAdminConsoleOpen ? "open" : ""}'),
]
for pat, repl in patterns:
    text = re.sub(pat, repl, text, count=1)

# Remove the known prestart re-open guard if present.
text = re.sub(
    r'\s*if\s*\(\s*prestartHold\s*&&\s*!console34\.open\s*\)\s*\{\s*console34\.open\s*=\s*true\s*;\s*state\.auctionAdminConsoleOpen\s*=\s*true\s*;\s*return\s*;?\s*\}',
    '\n',
    text,
    count=1,
    flags=re.S,
)

# Also neutralize a compact prestart-only force-open block, if present.
text = re.sub(
    r'if\s*\(\s*prestartHold\s*\)\s*\{\s*console34\.open\s*=\s*true\s*;\s*state\.auctionAdminConsoleOpen\s*=\s*true\s*;?\s*\}',
    '/* V44: drawer remains user-collapsible during prestart. */',
    text,
    count=1,
    flags=re.S,
)

# ----------------------------------------------------------
# 3) Restore a clear desktop control to leave live auction.
# ----------------------------------------------------------
if 'id="auction-live-exit-btn"' not in text:
    exit_btn = '<button id="auction-live-exit-btn" class="secondary" type="button" title="Torna alle tab">← TAB</button>'
    # Prefer placing it immediately before the league switch.
    m = re.search(r'<button\s+id=["\']league-switch-btn["\'][^>]*>.*?</button>', text, re.S)
    require(m, 'league-switch button not found')
    text = text[:m.start()] + exit_btn + '\n        ' + text[m.start():]

# ----------------------------------------------------------
# 4) Stop the V34 market strategist from rebuilding every card
# every 5 seconds. Hot bid/timer changes are already DOM-patched
# by the canonical auction reconcile path.
# ----------------------------------------------------------
runtime_match = re.search(r'(<script id=["\']v34-market-strategy-runtime["\']>)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

# Exact known timer plus whitespace-tolerant variants.
runtime, removed_intervals = re.subn(
    r'^\s*setInterval\s*\(\s*\(\)\s*=>\s*\{\s*if\s*\(\s*state\.view\s*===\s*["\']auction["\']\s*&&\s*session34\(\)\?\.status\s*===\s*["\']live["\']\s*\)\s*void\s+loadMarket34\(\)\s*;?\s*\}\s*,\s*5000\s*\)\s*;?\s*$',
    '  /* V44: periodic full live-card refresh disabled. */',
    runtime,
    count=1,
    flags=re.M,
)

# Fallback for the exact compact line used by V34.
compact = "  setInterval(()=>{if(state.view==='auction'&&session34()?.status==='live')void loadMarket34();},5000);"
if compact in runtime:
    runtime = runtime.replace(compact, '  /* V44: periodic full live-card refresh disabled. */', 1)
    removed_intervals += 1

# Protect against equivalent V34 5-second timers that still invoke loadMarket34.
# Only remove setInterval statements inside this runtime block and only when
# both loadMarket34 and 5000 are present.
def strip_market_interval(match):
    s = match.group(0)
    if 'loadMarket34' in s and re.search(r'[,\s]5000\s*\)', s):
        return '/* V44: periodic market interval removed. */'
    return s
runtime = re.sub(r'setInterval\s*\(.*?\)\s*;', strip_market_interval, runtime, flags=re.S)

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]

# ----------------------------------------------------------
# 5) Delegated exit handler, independent of render cycles.
# ----------------------------------------------------------
script_id = 'v44-live-emergency-runtime'
text = re.sub(
    rf'\s*<script id=["\']{script_id}["\']>.*?</script>\s*',
    '\n',
    text,
    count=1,
    flags=re.S,
)
exit_runtime = r'''
<script id="v44-live-emergency-runtime">
(() => {
  document.addEventListener('click', (event) => {
    const button = event.target.closest?.('#auction-live-exit-btn');
    if (!button) return;
    event.preventDefault();
    event.stopPropagation();
    try { state.auctionMobileDrawerOpen = false; } catch {}
    try { if (typeof clearAuctionTransient === 'function') clearAuctionTransient(); } catch {}
    if (typeof switchView === 'function') {
      switchView('home');
    } else {
      location.hash = '#/home';
    }
  }, true);
})();
</script>
'''
require('</body>' in text, 'closing body tag not found')
text = text.replace('</body>', exit_runtime + '\n</body>', 1)

# ----------------------------------------------------------
# Regression checks for the emergency requirements.
# ----------------------------------------------------------
require('id="auction-live-exit-btn"' in text, 'live exit button missing')
require('V44 · auction live emergency stability.' in text, 'V44 CSS missing')
require('v44-live-emergency-runtime' in text, 'V44 exit runtime missing')

# The specific known bad open condition must be gone.
require('prestartHold || state.auctionAdminConsoleOpen' not in text,
        'auctioneer drawer is still forced open by prestartHold')

# No V34 periodic 5-second market refresh should remain.
post_runtime = re.search(r'<script id=["\']v34-market-strategy-runtime["\']>(.*?)</script>', text, re.S)
require(post_runtime, 'post-patch V34 runtime missing')
for interval in re.findall(r'setInterval\s*\(.*?\)\s*;', post_runtime.group(1), re.S):
    require(not ('loadMarket34' in interval and '5000' in interval),
            'periodic loadMarket34 5-second refresh still present')

if text == original:
    print('V44: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print(f'V44 applied; removed market intervals: {removed_intervals}')
