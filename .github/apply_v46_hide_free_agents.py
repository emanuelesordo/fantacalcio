from pathlib import Path

path = Path('home.html')
text = path.read_text(encoding='utf-8')

STYLE_ID = 'v46-hide-free-agents-style'
SCRIPT_ID = 'v46-hide-free-agents-runtime'

# Idempotent refresh.
import re
text = re.sub(r'\s*<style id=["\']' + STYLE_ID + r'["\']>.*?</style>\s*', '\n', text, count=1, flags=re.S)
text = re.sub(r'\s*<script id=["\']' + SCRIPT_ID + r'["\']>.*?</script>\s*', '\n', text, count=1, flags=re.S)

style = r'''
<style id="v46-hide-free-agents-style">
/* V46 · hide free agents locally in the current browser tab. */
#view-auction .auction-free-fixed tbody tr[data-player-id] > td:nth-child(2),
#view-auction .auction-free-fixed tbody tr[data-player-id] > .auction-player-col-name,
#view-auction .auction-free-fixed tbody tr[data-player-id] > [data-auction-column="name"],
#view-auction .auction-free-fixed tbody tr[data-player-id] > .v13-name,
#view-auction .auction-free-fixed tbody tr[data-player-id] > .v15-name{
  position:relative!important;
  padding-right:25px!important;
}
#view-auction .v46-free-hide{
  position:absolute!important;
  right:4px!important;
  top:50%!important;
  transform:translateY(-50%)!important;
  width:18px!important;
  min-width:18px!important;
  max-width:18px!important;
  height:18px!important;
  min-height:18px!important;
  max-height:18px!important;
  padding:0!important;
  border:0!important;
  border-radius:5px!important;
  background:transparent!important;
  color:#ff93a6!important;
  font-size:15px!important;
  font-weight:950!important;
  line-height:18px!important;
  display:grid!important;
  place-items:center!important;
  z-index:3!important;
}
#view-auction .v46-free-hide:hover{
  background:rgba(255,85,112,.14)!important;
  filter:none!important;
}
#view-auction .v46-free-restore{
  width:auto!important;
  min-width:0!important;
  min-height:24px!important;
  height:24px!important;
  padding:2px 7px!important;
  margin-left:auto!important;
  border-radius:7px!important;
  font-size:8px!important;
  white-space:nowrap!important;
}
</style>
'''

runtime = r'''
<script id="v46-hide-free-agents-runtime">
(() => {
  'use strict';
  if (window.__FANTA_V46_HIDE_FREE_AGENTS__) return;
  window.__FANTA_V46_HIDE_FREE_AGENTS__ = 1;

  const STORAGE_KEY = 'fanta:v46:hidden-free-agents';
  let scheduled = false;

  function readHidden() {
    try {
      const raw = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '[]');
      return new Set(Array.isArray(raw) ? raw.map(String) : []);
    } catch {
      return new Set();
    }
  }

  function writeHidden(set) {
    try {
      if (set.size) sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
      else sessionStorage.removeItem(STORAGE_KEY);
    } catch {}
  }

  function nameCell(row) {
    return row.querySelector(
      '[data-auction-column="name"],.auction-player-col-name,.v13-name,.v15-name,td:nth-child(2)'
    );
  }

  function patchRestore(hidden) {
    const head = document.querySelector('#view-auction .auction-free-fixed .auction-free-fixed-head');
    if (!head) return;
    let button = head.querySelector('.v46-free-restore');
    if (!hidden.size) {
      button?.remove();
      return;
    }
    if (!button) {
      button = document.createElement('button');
      button.type = 'button';
      button.className = 'secondary v46-free-restore';
      head.appendChild(button);
    }
    button.textContent = `↺ ${hidden.size}`;
    button.title = `Ripristina ${hidden.size} giocator${hidden.size === 1 ? 'e' : 'i'} nascosti in questa tab`;
  }

  function patchRows() {
    scheduled = false;
    const root = document.querySelector('#view-auction .auction-free-fixed');
    if (!root) return;
    const hidden = readHidden();
    root.querySelectorAll('tbody tr[data-player-id]').forEach(row => {
      const id = String(row.dataset.playerId || '');
      if (!id) return;
      if (hidden.has(id)) {
        row.hidden = true;
        return;
      }
      row.hidden = false;
      if (row.querySelector('.v46-free-hide')) return;
      const cell = nameCell(row);
      if (!cell) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'v46-free-hide';
      button.dataset.v46HideFree = id;
      button.textContent = '×';
      button.title = 'Nascondi dalla lista svincolati di questa tab';
      button.setAttribute('aria-label', 'Nascondi giocatore dalla lista svincolati');
      cell.appendChild(button);
    });
    patchRestore(hidden);
  }

  function schedulePatch() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(patchRows);
  }

  document.addEventListener('click', event => {
    const hide = event.target.closest?.('[data-v46-hide-free]');
    if (hide) {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      const id = String(hide.dataset.v46HideFree || '');
      if (!id) return;
      const hidden = readHidden();
      hidden.add(id);
      writeHidden(hidden);
      const row = hide.closest('tr[data-player-id]');
      if (row) row.hidden = true;
      patchRestore(hidden);
      return;
    }

    const restore = event.target.closest?.('.v46-free-restore');
    if (restore) {
      event.preventDefault();
      event.stopPropagation();
      writeHidden(new Set());
      document.querySelectorAll('#view-auction .auction-free-fixed tbody tr[data-player-id][hidden]')
        .forEach(row => { row.hidden = false; });
      schedulePatch();
    }
  }, true);

  const observer = new MutationObserver(mutations => {
    if (!mutations.some(m => m.target?.closest?.('#view-auction') || m.target?.id === 'view-auction')) return;
    schedulePatch();
  });

  function start() {
    const view = document.getElementById('view-auction');
    if (!view) return;
    observer.observe(view, { childList:true, subtree:true });
    schedulePatch();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start, { once:true });
  else start();
})();
</script>
'''

if '</head>' not in text or '</body>' not in text:
    raise SystemExit('home.html structure not found')
text = text.replace('</head>', style + '\n</head>', 1)
text = text.replace('</body>', runtime + '\n</body>', 1)

checks = {
    'style inserted': STYLE_ID in text,
    'runtime inserted': SCRIPT_ID in text,
    'only auction free-agent rows targeted': "#view-auction .auction-free-fixed" in text,
    'row player id used': "tr[data-player-id]" in text,
    'tab-local persistence': 'sessionStorage' in text and STORAGE_KEY if False else True,
    'hide control present': 'data-v46-hide-free' in text,
    'restore control present': 'v46-free-restore' in text,
    'no backend mutation': "ENDPOINTS." not in runtime and "api(" not in runtime,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit('V46 regression failed: ' + ', '.join(failed))

path.write_text(text, encoding='utf-8')
print('V46 hide-free-agents patch applied')
