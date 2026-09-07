from pathlib import Path
import textwrap

workflow = Path('.github/workflows/consolidate-auction-list-v24.yml').read_text(encoding='utf-8')
start_marker = "          python3 - <<'PY'\n"
end_marker = "\n          PY\n\n      - name: Validate inline JavaScript and diff"
start = workflow.find(start_marker)
end = workflow.find(end_marker, start + len(start_marker))
if start < 0 or end < 0:
    raise RuntimeError('V24 embedded consolidator not found in source workflow')
code = workflow[start + len(start_marker):end]
# The workflow literal block adds ten spaces to every Python line.
lines = code.splitlines()
normalized = []
for line in lines:
    normalized.append(line[10:] if line.startswith('          ') else line)
code = '\n'.join(normalized) + '\n'
compile(code, '<v24-consolidator>', 'exec')
exec(code, {'__name__': '__main__'})
