from pathlib import Path

p=Path('home.html')
t=p.read_text(encoding='utf-8')
old="x.roleTarget.toFixed(2)"
if old not in t:
    raise SystemExit('V30 roleTarget marker not found')
t=t.replace(old,"x.playerTarget.toFixed(2)")
p.write_text(t,encoding='utf-8')
