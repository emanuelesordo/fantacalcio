import re
import subprocess
import traceback
from pathlib import Path

SOURCE_COMMIT = 'a2a4422c1cb9d3d3a795844244f1a82f4cd1b288'
SOURCE_PATH = '.github/workflows/consolidate-auction-list-v24.yml'
ERROR_PATH = Path('.github/v24-error.txt')
try:
    workflow = subprocess.check_output(
        ['git', 'show', f'{SOURCE_COMMIT}:{SOURCE_PATH}'],
        text=True,
    )
    start_marker = "          python3 - <<'PY'\n"
    end_marker = "\n          PY\n\n      - name: Validate inline JavaScript and diff"
    start = workflow.find(start_marker)
    end = workflow.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        raise RuntimeError(f'V24 embedded consolidator not found: start={start}, end={end}')
    code = workflow[start + len(start_marker):end]
    lines = code.splitlines()
    normalized = [line[10:] if line.startswith('          ') else line for line in lines]
    code = '\n'.join(normalized) + '\n'

    structural = r"""patch_start = text.find('    function patchAuctionTopSelection() {')
patch_end = text.find('    function patchAuctionLiveDynamic() {', patch_start)
if patch_start < 0 or patch_end < 0:
    raise RuntimeError('patchAuctionTopSelection function markers not found')
patch_close = text.rfind('\n    }', patch_start, patch_end)
if patch_close < 0:
    raise RuntimeError('patchAuctionTopSelection closing brace not found')
call_state_block = '''\n      const callButton = $('auction-call-confirm');\n      if (callButton) {\n        const session = auctionSession();\n        callButton.disabled = !(\n          selected\n          && session?.status === 'live'\n          && !session.current_player_id\n          && session.prestart_hold !== true\n          && auctionHasPresidentRole()\n          && auctionOwnCallTurn()\n        );\n      }\n'''
text = text[:patch_close] + call_state_block + text[patch_close:]
"""
    code, n = re.subn(
        r"patch_marker = '''.*?text = text\.replace\(patch_marker, patch_insert, 1\)\n",
        structural,
        code,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise RuntimeError(f'Unable to replace brittle top-call patch fragment: {n}')

    compile(code, '<v24-consolidator>', 'exec')
    exec(code, {'__name__': '__main__'})
    ERROR_PATH.unlink(missing_ok=True)
except Exception:
    ERROR_PATH.write_text(traceback.format_exc(), encoding='utf-8')
    print(ERROR_PATH.read_text(encoding='utf-8'))
