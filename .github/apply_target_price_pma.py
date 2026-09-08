from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V48 · canonical strategic target + economic colour signal
# - team FP TARGET is fixed at 72
# - Index remains independent from PFC/PMA/prices
# - Index/Rapporto colouring compares market reference with Index
# - green = market below Index, yellow = threshold, red = market above Index
# ==========================================================

# 1) Keep expected price as a market estimate, never as the strategic target.
pma_only = """    function strategicExpectedPrice(player) {
      const pma = strategicFinite(player?.pma);
      return Math.max(1, pma ?? 1);
    }"""
market_estimate = """    function strategicExpectedPrice(player) {
      const pfc = strategicFinite(player?.pfc);
      const pma = strategicFinite(player?.pma);
      if (pfc !== null && pma !== null) return Math.max(1, pfc * .65 + pma * .35);
      return Math.max(1, pfc ?? pma ?? 1);
    }"""
if pma_only in text:
    text = text.replace(pma_only, market_estimate, 1)
require(market_estimate in text, 'strategicExpectedPrice market estimate missing')

text = text.replace('Prezzo target', 'Prezzo atteso')
text = text.replace('prezzo target ${Math.round(strategicExpectedPrice(player))} cr',
                    'prezzo atteso ${Math.round(strategicExpectedPrice(player))} cr')

# 2) TARGET: fixed 72 in Strategia > Statistiche vittoria.
# Accept both the old dynamic block and a previously exported version.
target_re = re.compile(
    r"  function targetAverage\(\)\{\n"
    r"(?:.*?\n)*?"
    r"  \}\n"
    r"(?:  window\.v9StrategyTargetAverage=targetAverage;\n)?",
    re.S,
)
fixed_target = """  function targetAverage(){
    return 72;
  }
  window.v9StrategyTargetAverage=targetAverage;
"""
text, target_count = target_re.subn(fixed_target, text, count=1)
require(target_count == 1, 'Strategia targetAverage() block not found')

# 3) Strategic engine consumes exactly the same fixed target.
win_target_re = re.compile(
    r"    function strategicWinningTargetAverage\(\) \{.*?\n    \}",
    re.S,
)
fixed_win_target = """    function strategicWinningTargetAverage() {
      const shared = typeof window.v9StrategyTargetAverage === 'function'
        ? strategicFinite(window.v9StrategyTargetAverage())
        : null;
      return shared !== null ? shared : 72;
    }"""
text, win_count = win_target_re.subn(fixed_win_target, text, count=1)
require(win_count == 1, 'strategicWinningTargetAverage() block not found')

# 4) Index tooltip must not describe the obsolete dynamic 71–73 benchmark.
# V30 installs this override; make its source text explicitly fixed at 72.
text = re.sub(
    r"      const mantra=\(state\.auction\?\.settings\?\.fantasy_mode\|\|state\.setup\?\.fantasy_mode\|\|state\.list\?\.settings\?\.fantasyMode\)==='mantra';\n"
    r"      const rules=state\.v9Rules\|\|\{\};\n"
    r"      const classicBase=rules\.defense_rule_enabled\?\(rules\.clean_sheet_bonus_enabled\?73\.2:73\.0\):\(rules\.clean_sheet_bonus_enabled\?72\.0:71\.1\);\n"
    r"      const adjustment=mantra\?-\.5:0;\n"
    r"      const source=`benchmark \$\{classicBase\.toFixed\(2\)\}\$\{mantra\?' - 0\.50 Mantra':''\}`;",
    "      const source='target fisso 72.00';",
    text,
    count=1,
)

# 5) Restore dedicated Index / Rapporto colouring without changing layout.
STYLE_ID = 'v48-index-ratio-colors-style'
RUNTIME_ID = 'v48-index-ratio-colors-runtime'
text = re.sub(r'\s*<style id=["\']' + STYLE_ID + r'["\']>.*?</style>\s*', '\n', text, flags=re.S)
text = re.sub(r'\s*<script id=["\']' + RUNTIME_ID + r'["\']>.*?</script>\s*', '\n', text, flags=re.S)

style = r'''
<style id="v48-index-ratio-colors-style">
/* V48 · visible colour signal on Index and Rapporto cells only. */
.v48-index-ratio-tone{
  background:linear-gradient(90deg,
    hsl(var(--v48-hue) 74% 46% / var(--v48-alpha)),
    hsl(var(--v48-hue) 74% 46% / calc(var(--v48-alpha) * .38)))!important;
  box-shadow:inset 3px 0 0 hsl(var(--v48-hue) 80% 50% / .82)!important;
  font-weight:950!important;
  transition:background .16s ease,box-shadow .16s ease!important;
}
.v48-index-ratio-tone.v48-good{color:#83eab0!important}
.v48-index-ratio-tone.v48-warn{color:#f2d16b!important}
.v48-index-ratio-tone.v48-bad{color:#ff918d!important}
</style>
'''

runtime = r'''
<script id="v48-index-ratio-colors-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V48_INDEX_RATIO_COLORS__)return;
  window.__FANTA_V48_INDEX_RATIO_COLORS__=1;

  const clamp48=(v,a,b)=>Math.max(a,Math.min(b,v));
  const norm48=v=>String(v??'').trim().toUpperCase().replace(/[^A-ZÀ-Ú0-9%]+/g,' ');
  const number48=v=>{
    const s=String(v??'').replace(/\s/g,'').replace(/\./g,'').replace(',','.').replace(/[^0-9+\-.]/g,'');
    const n=Number(s);return Number.isFinite(n)?n:null;
  };
  const cellNumber48=cell=>number48(cell?.textContent);

  function tone48(cell,ratio){
    if(!cell||!Number.isFinite(ratio)||ratio<=0)return;
    const delta=1-ratio; // positive = market below Index = good
    const strength=clamp48(Math.abs(delta)/.35,0,1);
    const hue=delta>0 ? 48+84*strength : delta<0 ? 48*(1-strength) : 48;
    const alpha=.075+.16*strength;
    cell.classList.remove('v48-good','v48-warn','v48-bad');
    cell.classList.add('v48-index-ratio-tone',delta>.03?'v48-good':delta<-.03?'v48-bad':'v48-warn');
    cell.style.setProperty('--v48-hue',hue.toFixed(1));
    cell.style.setProperty('--v48-alpha',alpha.toFixed(3));
  }

  function headerMap48(table){
    const rows=[...(table?.tHead?.rows||[])];
    if(!rows.length)return null;
    const row=[...rows].reverse().find(r=>[...r.cells].some(c=>/INDICE|INDEX|RAPPORTO|PFC|PMA/.test(norm48(c.textContent))));
    if(!row)return null;
    const labels=[...row.cells].map(c=>norm48(c.textContent));
    const find=(rx)=>labels.findIndex(x=>rx.test(x));
    return{
      index:find(/^(INDICE|INDEX)( |$)/),
      ratio:find(/^RAPPORTO( |$)/),
      pfc:find(/^PFC( |$)/),
      pma:find(/^PMA( |$)/)
    };
  }

  function paintTable48(table){
    const map=headerMap48(table);if(!map||map.index<0)return;
    [...(table.tBodies||[])].flatMap(tb=>[...tb.rows]).forEach(row=>{
      const idx=cellNumber48(row.cells?.[map.index]);
      if(!(idx>0))return;
      const pfc=map.pfc>=0?cellNumber48(row.cells?.[map.pfc]):null;
      const pma=map.pma>=0?cellNumber48(row.cells?.[map.pma]):null;
      let market=null;
      if(pma!=null&&pfc!=null)market=.75*pma+.25*pfc;
      else market=pma??pfc;
      let ratio=market!=null&&market>0?market/idx:null;
      const ratioCell=map.ratio>=0?row.cells?.[map.ratio]:null;
      if(ratio==null&&ratioCell){
        const own=cellNumber48(ratioCell);
        if(own!=null)ratio=own>3?own/100:own;
      }
      if(ratio==null)return;
      tone48(row.cells?.[map.index],ratio);
      if(ratioCell)tone48(ratioCell,ratio);
    });
  }

  function paintCards48(){
    document.querySelectorAll('#view-strategy small,#view-strategy .label,#view-strategy [class*="label"]').forEach(label=>{
      const key=norm48(label.textContent);
      if(!/^RAPPORTO( |$)/.test(key))return;
      const host=label.parentElement;if(!host)return;
      const value=host.querySelector('b,strong,[data-value]');
      const raw=cellNumber48(value);if(raw==null)return;
      tone48(value,raw>3?raw/100:raw);
    });
  }

  let raf48=0;
  function paintAll48(){
    cancelAnimationFrame(raf48);
    raf48=requestAnimationFrame(()=>{
      document.querySelectorAll('#view-list table,#view-strategy table,#view-auction table').forEach(paintTable48);
      paintCards48();
    });
  }

  ['renderListTable','renderAuctionPlayers','renderAuctionLive','renderStats','renderStrategy'].forEach(name=>{
    const fn=window[name];if(typeof fn!=='function'||fn.__v48wrapped)return;
    const wrapped=function(...args){const out=fn.apply(this,args);queueMicrotask(paintAll48);return out;};
    wrapped.__v48wrapped=true;window[name]=wrapped;
  });

  const mount48=()=>{
    ['view-list','view-strategy','view-auction'].forEach(id=>{
      const root=document.getElementById(id);if(!root||root.dataset.v48Observer==='1')return;
      root.dataset.v48Observer='1';
      new MutationObserver(paintAll48).observe(root,{childList:true,subtree:true});
    });
    paintAll48();
  };
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',mount48,{once:true});else mount48();
  window.addEventListener('hashchange',()=>queueMicrotask(mount48));
})();
</script>
'''

require('</body>' in text, 'closing body tag not found')
text = text.replace('</body>', style + '\n' + runtime + '\n</body>', 1)

# Regression checks.
for needle in [
    'function targetAverage(){\n    return 72;',
    'window.v9StrategyTargetAverage=targetAverage;',
    'return shared !== null ? shared : 72;',
    'Punti squadra target',
    'v48-index-ratio-colors-style',
    'v48-index-ratio-colors-runtime',
    "if(pma!=null&&pfc!=null)market=.75*pma+.25*pfc;",
    "delta>.03?'v48-good':delta<-.03?'v48-bad':'v48-warn'",
]:
    require(needle in text, 'V48 assertion failed: '+needle)

require('Prezzo target' not in text, 'PMA/price is still mislabeled as target')
require("const target=typeof strategicWinningTargetAverage==='function'?Number(strategicWinningTargetAverage()||72):72;" in text,
        'index credit-per-point no longer uses the strategic FP target')

if text == original:
    print('V48 already applied: fixed target 72 and Index/Rapporto colours present')
else:
    path.write_text(text, encoding='utf-8')
    print('V48 applied: target 72 fixed; Index/Rapporto colours restored')
