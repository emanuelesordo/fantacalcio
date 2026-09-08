from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# Target price is an imported statistic: PMA.
# It must not be recomputed from PFC, strategy features or market heuristics.
expected_re = re.compile(
    r"    function strategicExpectedPrice\(player\) \{\n"
    r"      const pfc = strategicFinite\(player\?\.pfc\);\n"
    r"      const pma = strategicFinite\(player\?\.pma\);\n"
    r"      if \(pfc !== null && pma !== null\) return Math\.max\(1, pfc \* \.65 \+ pma \* \.35\);\n"
    r"      return Math\.max\(1, pfc \?\? pma \?\? 1\);\n"
    r"    \}"
)

expected_new = """    function strategicExpectedPrice(player) {
      const pma = strategicFinite(player?.pma);
      return Math.max(1, pma ?? 1);
    }"""

if expected_new not in text:
    text, count = expected_re.subn(expected_new, text, count=1)
    require(count == 1, 'strategicExpectedPrice legacy formula not found')

# Keep the vocabulary explicit in all user-facing surfaces that expose this value.
text = text.replace('Prezzo atteso', 'Prezzo target')
text = text.replace('prezzo atteso ${Math.round(strategicExpectedPrice(player))} cr',
                    'prezzo target ${Math.round(strategicExpectedPrice(player))} cr')

# Regression checks: exact PMA source, no old PFC/PMA weighted formula.
require(expected_new in text, 'PMA target-price function missing')
require('pfc * .65 + pma * .35' not in text,
        'legacy weighted target-price formula still present')
require("expected:{label:'Prezzo target'" in text,
        'target-price list/filter label not updated')
require('<small>Prezzo target</small>' in text,
        'called-player target-price label not updated')
require('prezzo target ${Math.round(strategicExpectedPrice(player))} cr' in text,
        'strategic index title not updated')

if text == original:
    print('Target price already uses PMA statistics')
else:
    path.write_text(text, encoding='utf-8')
    print('Target price now uses PMA statistics exactly')
