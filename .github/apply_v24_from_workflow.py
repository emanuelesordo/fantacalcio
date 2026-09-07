import subprocess

SOURCE_COMMIT = 'a2a4422c1cb9d3d3a795844244f1a82f4cd1b288'
SOURCE_PATH = '.github/workflows/consolidate-auction-list-v24.yml'
workflow = subprocess.check_output(
    ['git', 'show', f'{SOURCE_COMMIT}:{SOURCE_PATH}'],
    text=True,
)
start_marker = "          python3 - <<'PY'\n"
end_marker = "\n          PY\n\n      - name: Validate inline JavaScript and diff"
start = workflow.find(start_marker)
end = workflow.find(end_marker, start + len(start_marker))
if start < 0 or end < 0:
    raise RuntimeError('V24 embedded consolidator not found in source workflow')
code = workflow[start + len(start_marker):end]
lines = code.splitlines()
normalized = [line[10:] if line.startswith('          ') else line for line in lines]
code = '\n'.join(normalized) + '\n'
compile(code, '<v24-consolidator>', 'exec')
exec(code, {'__name__': '__main__'})
