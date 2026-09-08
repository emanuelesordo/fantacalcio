from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')

STYLE_ID = 'v47-list-hide-style'
RUNTIME_ID = 'v47-list-hide-runtime'

# Idempotent: remove prior V47 blocks if this patcher is re-run.
text = re.sub(r'\s*<style id=["\']' + STYLE_ID + r'["\']>.*?</style>\s*', '\n', text, flags=re.S)
text = re.sub(r'\s*<script id=["\']' + RUNTIME_ID + r'["\']>.*?</script>\s*', '\n', text, flags=re.S)

if 'id="list-body"' not in text and "id='list-body'" not in text:
    raise SystemExit('Listone tbody #list-body not found')
if '</body>' not in text:
    raise SystemExit('closing body tag not found')

style = r'''
<style id="v47-list-hide-style">
/* V47 · hide individual players from the GENERAL Listone, tab-local only. */
#view-list #list-body .v47-list-name-host{
  position:relative!important;
  padding-right:25px!important;
}
#view-list #list-body .v47-list-hide{
  position:absolute!important;
  top:50%!important;
  right:3px!important;
  transform:translateY(-50%)!important;
  width:18px!important;
  min-width:18px!important;
  height:18px!important;
  min-height:18px!important;
  padding:0!important;
  margin:0!important;
  border-radius:5px!important;
  border:1px solid rgba(255,120,135,.35)!important;
  background:rgba(120,28,43,.28)!important;
  color:#ff9eaa!important;
  font-size:13px!important;
  font-weight:900!important;
  line-height:16px!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  z-index:3!important;
  opacity:.72!important;
}
#view-list #list-body tr:hover .v47-list-hide,
#view-list #list-body .v47-list-hide:focus-visible{
  opacity:1!important;
}
#view-list .v47-list-restore{
  width:auto!important;
  min-width:34px!important;
  min-height:27px!important;
  height:27px!important;
  padding:2px 7px!important;
  margin-left:auto!important;
  font-size:8px!important;
  white-space:nowrap!important;
}
</style>
'''

runtime = r'''
<script id="v47-list-hide-runtime">
(() => {
  'use strict';
  if (window.__FANTA_V47_LIST_HIDE__) return;
  window.__FANTA_V47_LIST_HIDE__ = 1;

  const KEY = 'fantacalcio:v47:listone-hidden-player-ids';
  let hidden = new Set();
  let listObserver = null;

  function readHidden(){
    try{
      const raw = JSON.parse(sessionStorage.getItem(KEY) || '[]');
      hidden = new Set(Array.isArray(raw) ? raw.map(String) : []);
    }catch{
      hidden = new Set();
    }
  }

  function saveHidden(){
    try{ sessionStorage.setItem(KEY, JSON.stringify([...hidden])); }catch{}
  }

  function restoreControl(){
    const rolebar = document.querySelector('#view-list .rolebar');
    if(!rolebar) return;
    let button = rolebar.querySelector('.v47-list-restore');
    if(!hidden.size){
      button?.remove();
      return;
    }
    if(!button){
      button = document.createElement('button');
      button.type = 'button';
      button.className = 'secondary v47-list-restore';
      button.addEventListener('click', event => {
        event.preventDefault();
        event.stopPropagation();
        hidden.clear();
        saveHidden();
        decorateList();
      });
      rolebar.appendChild(button);
    }
    button.textContent = `↺ ${hidden.size}`;
    button.title = `Ripristina ${hidden.size} giocator${hidden.size === 1 ? 'e' : 'i'} nascosti in questa tab`;
    button.setAttribute('aria-label', button.title);
  }

  function nameHost(row){
    return row.querySelector(
      '.v15-name,.v13-name,.v12-col-name,.auction-player-col-name,.player-name-cell'
    ) || row.cells?.[1] || null;
  }

  function decorateRow(row){
    const id = String(row?.dataset?.playerId || '');
    if(!id) return;

    const isHidden = hidden.has(id);
    row.hidden = isHidden;
    row.style.display = isHidden ? 'none' : '';
    if(isHidden) return;

    const host = nameHost(row);
    if(!host || host.querySelector('.v47-list-hide')) return;
    host.classList.add('v47-list-name-host');

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'v47-list-hide';
    button.dataset.v47HideListPlayer = id;
    button.textContent = '×';
    button.title = 'Nascondi dalla lista in questa tab';
    button.setAttribute('aria-label', button.title);
    button.addEventListener('click', event => {
      event.preventDefault();
      event.stopPropagation();
      event.stopImmediatePropagation();
      hidden.add(id);
      saveHidden();
      row.hidden = true;
      row.style.display = 'none';
      restoreControl();
    }, true);
    host.appendChild(button);
  }

  function decorateList(){
    const body = document.getElementById('list-body');
    if(!body) return;
    body.querySelectorAll('tr[data-player-id]').forEach(decorateRow);
    restoreControl();
  }

  function attachObserver(){
    const body = document.getElementById('list-body');
    if(!body) return false;
    if(listObserver) listObserver.disconnect();
    listObserver = new MutationObserver(() => decorateList());
    listObserver.observe(body, {childList:true, subtree:true});
    decorateList();
    return true;
  }

  readHidden();
  if(!attachObserver()){
    document.addEventListener('DOMContentLoaded', attachObserver, {once:true});
  }
  window.addEventListener('hashchange', () => requestAnimationFrame(() => {
    if(!listObserver) attachObserver();
    decorateList();
  }));

  // Renderers replace tbody rows; wrapping the canonical renderer gives immediate decoration.
  if(typeof window.renderListTable === 'function'){
    const originalRenderListTable = window.renderListTable;
    window.renderListTable = function(...args){
      const result = originalRenderListTable.apply(this,args);
      queueMicrotask(decorateList);
      return result;
    };
  }

  requestAnimationFrame(decorateList);
})();
</script>
'''

text = text.replace('</body>', style + '\n' + runtime + '\n</body>', 1)

# Regression guards: this feature must target the GENERAL Listone, not the auction-only table.
for needle in [
    'id="v47-list-hide-style"',
    'id="v47-list-hide-runtime"',
    "document.getElementById('list-body')",
    "sessionStorage.setItem(KEY",
    "className = 'v47-list-hide'",
    "#view-list #list-body",
    "Ripristina ${hidden.size}",
]:
    if needle not in text:
        raise SystemExit(f'V47 assertion failed: {needle}')

path.write_text(text, encoding='utf-8')
print('V47 Listone hide control applied')
