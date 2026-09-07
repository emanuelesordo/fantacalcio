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
    compile(code, '<v24-consolidator>', 'exec')
    exec(code, {'__name__': '__main__'})
    ERROR_PATH.unlink(missing_ok=True)
except Exception:
    ERROR_PATH.write_text(traceback.format_exc(), encoding='utf-8')
    print(ERROR_PATH.read_text(encoding='utf-8'))
