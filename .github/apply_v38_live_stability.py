from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V42 · focused live-auction correction
# - 4 strategist cards in the normal footprint: 2 x 2
# - compact unboxed UD / O / MAX values
# - live row economic signal is literally the Listone V33 formula
# ==========================================================
style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

# Idempotency when the workflow is manually re-run.
style = re.sub(
    r'\n/\* V42 · strategist 2x2 \+ exact Listone signal\. \*/.*?(?=\Z)',
    '\n',
    style,
    count=1,
    flags=re.S,
)

v42_css = r'''
/* V42 · strategist 2x2 + exact Listone signal. */

/* Normal live strategist: exactly the four returned suggestions occupy a 2x2 grid.
   This selector intentionally beats the old v10 auto-fit rule. */
@media(min-width:701px){
  html body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-list{
    display:grid!important;
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-auto-flow:row!important;
    grid-auto-rows:44px!important;
    align-content:start!important;
    gap:4px!important;
    width:100%!important;
    min-width:0!important;
    max-height:92px!important;
    overflow:hidden!important;
  }

  html body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-row{
    display:grid!important;
    grid-template-columns:auto minmax(0,1fr) auto auto!important;
    width:100%!important;
    min-width:0!important;
    max-width:100%!important;
    height:44px!important;
    min-height:44px!important;
    max-height:44px!important;
    padding:4px 6px!important;
    gap:5px!important;
    align-items:center!important;
    overflow:hidden!important;
  }

  /* UD / O / MAX are data, not three nested cards. */
  html body.auction-live.modern-glass #view-auction
  .auction-suggested-row .v34-suggest-metrics{
    display:flex!important;
    grid-template-columns:none!important;
    align-items:center!important;
    justify-content:flex-end!important;
    gap:7px!important;
    min-width:0!important;
    width:auto!important;
  }
  html body.auction-live.modern-glass #view-auction
  .auction-suggested-row .v34-suggest-metric{
    display:inline-flex!important;
    align-items:baseline!important;
    justify-content:center!important;
    gap:2px!important;
    min-width:0!important;
    min-height:0!important;
    height:auto!important;
    padding:0!important;
    border:0!important;
    border-radius:0!important;
    background:transparent!important;
    box-shadow:none!important;
  }
  html body.auction-live.modern-glass #view-auction
  .auction-suggested-row .v34-suggest-metric small{
    font-size:5.5px!important;
    line-height:1!important;
    color:var(--muted)!important;
    font-weight:900!important;
  }
  html body.auction-live.modern-glass #view-auction
  .auction-suggested-row .v34-suggest-metric b{
    font-size:9.5px!important;
    line-height:1!important;
    font-weight:950!important;
    font-variant-numeric:tabular-nums!important;
  }

  html body.auction-live.modern-glass #view-auction
  .auction-suggested-row .auction-suggested-copy>small{
    font-size:6px!important;
    line-height:1.05!important;
  }

  /* Full immersion still returns eight suggestions: 2 columns x 4 compact rows. */
  :fullscreen html body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-list,
  html:fullscreen body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-list{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    grid-auto-rows:36px!important;
    max-height:156px!important;
  }
  :fullscreen html body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-row,
  html:fullscreen body.auction-live.modern-glass #view-auction
  .auction-free-suggestions .auction-suggested-calls .auction-suggested-row{
    height:36px!important;
    min-height:36px!important;
    max-height:36px!important;
  }
}

/* Live auction uses the same V33 red -> yellow -> green variables as Listone.
   Do not depend on a body helper class that can arrive one render late. */
html body.auction-live #view-auction tr.v33-index-market-row{
  background:linear-gradient(90deg,
    hsl(var(--v33-market-hue) 76% 46% / var(--v33-market-alpha)),
    transparent 86%)!important;
  box-shadow:inset 3px 0 0 hsl(var(--v33-market-hue) 84% 51% / .78)!important;
  transition:background .16s ease,box-shadow .16s ease!important;
}
'''
style += v42_css
text = text[:style_match.start(2)] + style + text[style_match.end(2):]


# ==========================================================
# V34 runtime painter: copy the Listone V33 calculation verbatim.
# Important: do NOT use idx34/ud34 for row colour. The value shown in
# the Index column and the row signal must both originate from
# strategicValueIndex() and the same 75% PMA / 25% PFC market reference.
# ==========================================================
runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

paint_re = re.compile(
    r'  function paintDeal34\(root,players\)\{.*?\n  \}\n\n  function addUdColumn34',
    re.S,
)
paint_new = r'''  function paintDeal34(root,players){
    if(!root)return;
    const by=new Map((players||[]).map(p=>[String(p.id),p]));
    root.querySelectorAll('tr[data-player-id]').forEach(row=>{
      const p=by.get(String(row.dataset.playerId));if(!p)return;

      /* Same cleanup + same calculation used by Listone V33. */
      row.classList.remove('v22-market-value-row','auction-market-value-row','v10-private-delta-row','v30-index-market-row','v33-index-market-row');
      ['--v22-hue','--v22-alpha','--auction-market-hue','--auction-market-alpha','--v10-delta-hue','--v10-delta-alpha','--v30-market-hue','--v30-market-alpha','--v33-market-hue','--v33-market-alpha'].forEach(k=>row.style.removeProperty(k));

      let idx=null;try{idx=num(typeof strategicValueIndex==='function'?strategicValueIndex(p):null)}catch{}
      const pma=num(p?.pma),pfc=num(p?.pfc);
      if(idx==null||(pma==null&&pfc==null))return;
      const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);
      const delta=idx-market;
      const scale=Math.max(8,Math.abs(idx),Math.abs(market));
      const relative=delta/scale;
      const strength=clamp(Math.abs(relative)/.35,0,1);
      /* 52 = yellow at exactly zero; smoothly approach green 128 or red 0. */
      const hue=relative>=0?52+(128-52)*strength:52*(1-strength);
      const alpha=.060+.115*strength;
      row.classList.add('v33-index-market-row');
      row.style.setProperty('--v33-market-hue',hue.toFixed(1));
      row.style.setProperty('--v33-market-alpha',alpha.toFixed(3));
      row.title=`Indice ${Math.round(idx)} cr · PFC/PMA medio ${market.toFixed(1)} · delta ${delta>=0?'+':''}${delta.toFixed(1)} cr`;
    });
  }

  function addUdColumn34'''
runtime, n_paint = paint_re.subn(paint_new, runtime, count=1)
require(n_paint == 1, 'paintDeal34 target not found')
text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# ==========================================================
# Regression tests. These are deliberately concrete instead of checking only
# for generic words/selectors, because that allowed the previous bug through.
# ==========================================================
style_check = re.search(r'<style id="v34-market-strategy-style">(.*?)</style>', text, re.S)
runtime_check = re.search(r'<script id="v34-market-strategy-runtime">(.*?)</script>', text, re.S)
require(style_check and runtime_check, 'post-patch blocks missing')
style_final = style_check.group(1)
runtime_final = runtime_check.group(1)

paint_match = re.search(
    r'function paintDeal34\(root,players\)\{(.*?)\n  \}\n\n  function addUdColumn34',
    runtime_final,
    re.S,
)
require(paint_match, 'post-patch paintDeal34 missing')
paint_body = paint_match.group(1)

# Literal Listone formula requirements.
exact_formula = [
    "strategicValueIndex(p)",
    "const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);",
    "const delta=idx-market;",
    "const scale=Math.max(8,Math.abs(idx),Math.abs(market));",
    "const relative=delta/scale;",
    "const strength=clamp(Math.abs(relative)/.35,0,1);",
    "const hue=relative>=0?52+(128-52)*strength:52*(1-strength);",
    "const alpha=.060+.115*strength;",
    "row.classList.add('v33-index-market-row');",
]
for token in exact_formula:
    require(token in paint_body, 'Listone formula token missing from live painter: '+token)
require('idx34(p)' not in paint_body and 'ud34(p)' not in paint_body,
        'live row painter still uses V34 alternative Index/UD calculation')

# Concrete examples from the reported screen.
def signal(idx, pfc, pma):
    market = .75*pma + .25*pfc
    delta = idx - market
    scale = max(8, abs(idx), abs(market))
    relative = delta / scale
    strength = min(1, max(0, abs(relative)/.35))
    hue = 52 + (128-52)*strength if relative >= 0 else 52*(1-strength)
    return market, delta, hue

bijlow_market, bijlow_delta, bijlow_hue = signal(5, 12, 4)
degea_market, degea_delta, degea_hue = signal(33, 24, 13)
require(abs(bijlow_market-6.0) < 1e-9 and bijlow_delta < 0 and bijlow_hue < 52,
        'BIJLOW regression failed: IDX 5 vs PFC 12/PMA 4 must be on the red side')
require(abs(degea_market-15.75) < 1e-9 and degea_delta > 0 and degea_hue > 52,
        'DE GEA regression failed: IDX 33 vs PFC 24/PMA 13 must be on the green side')

# Strategist must beat the old auto-fit selector and must not box each metric.
requirements = [
    'html body.auction-live.modern-glass #view-auction',
    '.auction-free-suggestions .auction-suggested-calls .auction-suggested-list',
    'grid-template-columns:repeat(2,minmax(0,1fr))!important',
    'grid-auto-rows:44px!important',
    '.auction-suggested-row .v34-suggest-metrics',
    'display:flex!important',
    '.auction-suggested-row .v34-suggest-metric',
    'border:0!important',
    'background:transparent!important',
    'font-size:9.5px!important',
]
for token in requirements:
    require(token in style_final, 'strategist V42 requirement missing: '+token)
require("const limit=document.fullscreenElement?8:4" in text or "const limit = fullImmersion ? 8 : 4" in text,
        'strategist renderer no longer guarantees 4 normal / 8 full-immersion suggestions')

# Preserve the already-fixed live constraints.
require('/* V38: no periodic full live-card refresh. */' in runtime_final,
        'periodic full live-card refresh regression')
require('Server autorevole' not in text and 'Frontend statico' not in text,
        'server-status chrome regression')

print(
    'V42 tests passed: strategist=2x2, metrics=unboxed, '
    f'BIJLOW market={bijlow_market:.2f} delta={bijlow_delta:.2f} hue={bijlow_hue:.1f}, '
    f'DE GEA market={degea_market:.2f} delta={degea_delta:.2f} hue={degea_hue:.1f}'
)

if text == original:
    print('V42: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V42 strategist/index correction applied')
