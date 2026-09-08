from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# Correct target semantics
# - TARGET = the team FP target shown in Strategia > Statistiche vittoria
# - do not confuse it with PMA
# - strategic calculations must read the exact same targetAverage() value
# - restore strategicExpectedPrice() to its original market-price estimate
# ==========================================================

# 1) Undo the mistaken PMA-as-target change.
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

# The value above is a market estimate, not the strategic target.
text = text.replace('Prezzo target', 'Prezzo atteso')
text = text.replace('prezzo target ${Math.round(strategicExpectedPrice(player))} cr',
                    'prezzo atteso ${Math.round(strategicExpectedPrice(player))} cr')

# 2) Export the exact target used by Strategia > Statistiche vittoria.
target_average_block = """  function targetAverage(){
    const r=state.v9Rules||{};
    let v=r.defense_rule_enabled?(r.clean_sheet_bonus_enabled?BENCH.avg.both:BENCH.avg.def):(r.clean_sheet_bonus_enabled?BENCH.avg.clean:BENCH.avg.none);
    if(mode()==='mantra') v-=.5;
    return v;
  }"""
exported_block = target_average_block + "\n  window.v9StrategyTargetAverage=targetAverage;"
if 'window.v9StrategyTargetAverage=targetAverage;' not in text:
    require(target_average_block in text, 'Strategia targetAverage() block not found')
    text = text.replace(target_average_block, exported_block, 1)

# 3) Make the strategic engine consume that exact value.
legacy_win_target_re = re.compile(
    r"    function strategicWinningTargetAverage\(\) \{\n"
    r"      const rules = state\.v9Rules \|\| \{\};\n"
    r"      let target = rules\.defense_rule_enabled\n"
    r"        \? \(rules\.clean_sheet_bonus_enabled \? 73\.2 : 73\.0\)\n"
    r"        : \(rules\.clean_sheet_bonus_enabled \? 72\.0 : 71\.1\);\n"
    r"      if \(fantasyMode\(\) === 'mantra'\) target -= \.5;\n"
    r"      return target;\n"
    r"    \}"
)
shared_win_target = """    function strategicWinningTargetAverage() {
      const shared = typeof window.v9StrategyTargetAverage === 'function'
        ? strategicFinite(window.v9StrategyTargetAverage())
        : null;
      if (shared !== null) return shared;
      const rules = state.v9Rules || {};
      let target = rules.defense_rule_enabled
        ? (rules.clean_sheet_bonus_enabled ? 73.2 : 73.0)
        : (rules.clean_sheet_bonus_enabled ? 72.0 : 71.1);
      if (fantasyMode() === 'mantra') target -= .5;
      return target;
    }"""
if shared_win_target not in text:
    text, count = legacy_win_target_re.subn(shared_win_target, text, count=1)
    require(count == 1, 'strategicWinningTargetAverage() legacy block not found')

# Regression checks.
require('window.v9StrategyTargetAverage=targetAverage;' in text,
        'Strategia target is not exported')
require("typeof window.v9StrategyTargetAverage === 'function'" in text,
        'strategic engine is not reading the strategy target')
require('const pfc = strategicFinite(player?.pfc);' in text and
        'pfc * .65 + pma * .35' in text,
        'market price estimate was not restored')
require('Prezzo target' not in text,
        'PMA/price is still mislabeled as target')
require('Punti squadra target' in text,
        'strategy target KPI missing')
require("const target=typeof strategicWinningTargetAverage==='function'?Number(strategicWinningTargetAverage()||72):72;" in text,
        'index credit-per-point no longer uses the strategy FP target')

if text == original:
    print('Strategy FP target already canonical')
else:
    path.write_text(text, encoding='utf-8')
    print('Canonical target = Strategia FP target; PMA target mistake reverted')
