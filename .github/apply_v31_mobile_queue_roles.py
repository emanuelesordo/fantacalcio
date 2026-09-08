from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

# Idempotent cleanup.
text=re.sub(r'\n<style id="v31-mobile-queue-roles-style">.*?</style>\n','\n',text,flags=re.S)
text=re.sub(r'\n<script id="v31-mobile-queue-roles-runtime">.*?</script>\n','\n',text,flags=re.S)

# ------------------------------------------------------------------
# Mobile main header: BACK | TURN | CREDITS/MAX only.
# Remove the auction PAUSE control added by V30; queue pause belongs
# to the queue card header instead.
# ------------------------------------------------------------------
start=text.find('<script id="v23-mobile-auction-mode-runtime">')
end=text.find('</script>',start)
if start<0 or end<0:
    raise SystemExit('v23 mobile runtime not found')
block=text[start:end]

pat=re.compile(r'''  function ensureV30MobileHeader\(shell\)\{.*?\n  function syncButtons\(shell\)\{''',re.S)
replacement='''  function ensureV30MobileHeader(shell){
    qsa('.v23-header-mode').forEach(n=>n.remove());
    const head=qs('.v23-mobile-head',shell);if(!head)return;
    qs('[data-v30-pause]',head)?.remove();
    let back=qs('[data-v30-back]',head);
    if(!back){back=document.createElement('button');back.type='button';back.className='secondary v30-mobile-back';back.dataset.v30Back='1';back.setAttribute('aria-label','Torna al menu principale');back.textContent='←';head.prepend(back);}
  }

  function syncButtons(shell){'''
block,n=pat.subn(replacement,block,count=1)
if n!=1:
    raise SystemExit(f'header helper replacement count={n}')
block=block.replace('syncV30MobilePause(shell);','')
# Remove stale pause click branch while preserving BACK.
block=re.sub(r'''\n\s*const pause=e\.target\.closest\?\.\('\[data-v30-pause\]'\);\n\s*if\(pause\)\{.*?\}\n''','\n',block,count=1,flags=re.S)
text=text[:start]+block+text[end:]

# ------------------------------------------------------------------
# V30 mobile queue runtime: add role strip/filtering and phase-aware
# actions directly inside the canonical mobile free-agent renderer.
# ------------------------------------------------------------------
start=text.find('<script id="v30-index-mobile-queue-runtime">')
end=text.find('</script>',start)
if start<0 or end<0:
    raise SystemExit('v30 queue runtime not found')
block=text[start:end]

if 'function phaseAllowed31(' not in block:
    anchor='  function freeCandidates30(){'
    helper=r'''  function phaseAllowed31(p){
    try{return typeof auctionPlayerMatchesCurrentRolePhase==='function'?Boolean(auctionPlayerMatchesCurrentRolePhase(p)):true}catch{return true}
  }
  function roleOrder31(){
    const mode=state.auction?.settings?.fantasy_mode||'classic';
    const canonical=mode==='mantra'?['Por','B','Dc','Dd','Ds','E','M','C','W','T','A','Pc']:['P','D','C','A'];
    const seen=new Set();
    (state.auction?.callCandidates||[]).forEach(p=>playerRoles30(p).forEach(r=>seen.add(String(r))));
    return [...canonical.filter(r=>seen.has(r)),...[...seen].filter(r=>!canonical.includes(r)).sort((a,b)=>a.localeCompare(b,'it'))];
  }
  function roleFilterContext31(){
    const s=state.auction?.auctionSession||{};
    return [s.id||'',state.auction?.rolePhase?.key||'',s.role_phase_index??'',(state.auction?.callCandidates||[]).length].join('|');
  }
  function ensureRoleFilter31(){
    const ctx=roleFilterContext31(),all=roleOrder31();
    if(!state.v31MobileRoleFilter||state.v31MobileRoleFilter.ctx!==ctx){
      const enabled=new Set();
      (state.auction?.callCandidates||[]).filter(phaseAllowed31).forEach(p=>playerRoles30(p).forEach(r=>enabled.add(String(r))));
      const selected=all.filter(r=>enabled.has(r));
      state.v31MobileRoleFilter={ctx,selected:selected.length?selected:[...all]};
    }
    return state.v31MobileRoleFilter;
  }
  function playerMatchesRoleFilter31(p){
    const f=ensureRoleFilter31(),selected=new Set(f.selected||[]);
    if(!selected.size)return true;
    return playerRoles30(p).some(r=>selected.has(String(r)));
  }
  function ensureRoleStrip31(){
    const search=qs('.v23-mobile-drawer-free-panel .v23-mobile-drawer-search');if(!search)return null;
    let strip=qs('[data-v31-role-strip]');
    if(!strip){strip=document.createElement('div');strip.className='v31-mobile-role-strip';strip.dataset.v31RoleStrip='1';search.insertAdjacentElement('afterend',strip);}
    return strip;
  }
  function renderRoleStrip31(){
    const strip=ensureRoleStrip31();if(!strip)return;
    const f=ensureRoleFilter31(),all=roleOrder31(),selected=new Set(f.selected||[]),allOn=all.length>0&&all.every(r=>selected.has(r));
    strip.innerHTML=`<button type="button" data-v31-role="__ALL__" class="${allOn?'active':''}">ALL</button>${all.map(r=>`<button type="button" data-v31-role="${esc30(r)}" class="v23-role-${roleTone30(r)} ${selected.has(r)?'active':''}">${esc30(r)}</button>`).join('')}`;
  }

'''
    if anchor not in block:
        raise SystemExit('freeCandidates30 anchor missing')
    block=block.replace(anchor,helper+anchor,1)

# Canonical free candidates: keep fuzzy search + mobile role filter.
old="""    return (state.auction?.callCandidates||[]).filter(p=>(!p.status||p.status==='available')&&String(p.id)!==String(state.auction?.auctionSession?.current_player_id||'')).filter(p=>{if(!q)return true;try{return typeof playerSearchRank==='function'?playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null:String(p.name||'').toLowerCase().includes(q.toLowerCase())}catch{return true}}).sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'it')).slice(0,120);"""
new="""    return (state.auction?.callCandidates||[]).filter(p=>(!p.status||p.status==='available')&&String(p.id)!==String(state.auction?.auctionSession?.current_player_id||'')).filter(playerMatchesRoleFilter31).filter(p=>{if(!q)return true;try{return typeof playerSearchRank==='function'?playerSearchRank(p,q,state.auction?.settings?.fantasy_mode||'classic')!==null:String(p.name||'').toLowerCase().includes(q.toLowerCase())}catch{return true}}).sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'it')).slice(0,120);"""
if old not in block:
    raise SystemExit('freeCandidates30 pipeline target missing')
block=block.replace(old,new,1)

# Render role strip and make actions phase-aware per player.
old_head="""  function renderFree30(){
    const host=qs('[data-v23-free-list]');if(!host||!document.body.classList.contains('v23-free-open'))return;
    const queued=new Set(queueRows30().map(x=>String(x.player_id))),callable=canCall30(),queueable=canQueue30(),oldTop=host.scrollTop;
    host.innerHTML=freeCandidates30().map(p=>{const inQueue=queued.has(String(p.id)),fm=fmv30(p),tit=tit30(p);return `"""
new_head="""  function renderFree30(){
    const host=qs('[data-v23-free-list]');if(!host||!document.body.classList.contains('v23-free-open'))return;
    renderRoleStrip31();
    const queued=new Set(queueRows30().map(x=>String(x.player_id))),callable=canCall30(),queueable=canQueue30(),oldTop=host.scrollTop;
    host.innerHTML=freeCandidates30().map(p=>{const inQueue=queued.has(String(p.id)),fm=fmv30(p),tit=tit30(p),phaseAllowed=phaseAllowed31(p);return `"""
if old_head not in block:
    raise SystemExit('renderFree30 header target missing')
block=block.replace(old_head,new_head,1)
block=block.replace("${callable?'':'disabled'}>CHIAMA</button><button type=\"button\" class=\"v30-queue-add\" data-v30-mobile-queue-add=\"${esc30(p.id)}\" ${queueable&&!inQueue?'':'disabled'}>${inQueue?'IN CODA':'CODA'}</button>","${callable&&phaseAllowed?'':'disabled'}>CHIAMA</button><button type=\"button\" class=\"v30-queue-add\" data-v30-mobile-queue-add=\"${esc30(p.id)}\" ${queueable&&phaseAllowed&&!inQueue?'':'disabled'}>${inQueue?'IN CODA':'CODA'}</button>",1)

# Add role-strip click handling inside the V30 event delegation.
click_anchor="""  document.addEventListener('click',e=>{
    const direct=e.target.closest?.('[data-v30-mobile-direct]');"""
click_new="""  document.addEventListener('click',e=>{
    const role=e.target.closest?.('[data-v31-role]');if(role){
      e.preventDefault();e.stopPropagation();
      const f=ensureRoleFilter31(),all=roleOrder31(),key=role.dataset.v31Role;
      if(key==='__ALL__'){f.selected=[...all];}
      else{
        const s=new Set(f.selected||[]);
        if(s.has(key)&&s.size>1)s.delete(key);else s.add(key);
        f.selected=all.filter(r=>s.has(r));
      }
      renderRoleStrip31();renderFree30();return;
    }
    const direct=e.target.closest?.('[data-v30-mobile-direct]');"""
if click_anchor not in block:
    raise SystemExit('V30 delegated click anchor missing')
block=block.replace(click_anchor,click_new,1)

text=text[:start]+block+text[end:]

style=r'''
<style id="v31-mobile-queue-roles-style">
@media(max-width:820px){
  /* Main mobile header: BACK | TURN | CREDITS/MAX. No auction-pause button. */
  body.v23-mobile-auction .v23-mobile-head{
    grid-template-columns:40px minmax(0,1fr) 110px!important;
  }
  body.v23-mobile-auction .v30-mobile-pause,
  body.v23-mobile-auction [data-v30-pause]{display:none!important}

  /* Queue pause belongs to the queue card header. */
  .v31-queue-head-actions{display:flex!important;align-items:center!important;gap:5px!important;margin-left:auto!important}
  .v31-queue-pause{height:25px!important;min-height:25px!important;min-width:58px!important;padding:2px 6px!important;border-radius:7px!important;font-size:7px!important;font-weight:900!important}
  .v31-queue-pause.is-paused{background:var(--good)!important;color:#fff!important}

  /* Free-agent role strip: horizontal, scrollable, phase defaults active. */
  .v31-mobile-role-strip{
    display:flex!important;align-items:center!important;gap:3px!important;
    min-height:36px!important;padding:4px 7px!important;overflow-x:auto!important;overflow-y:hidden!important;
    -webkit-overflow-scrolling:touch!important;scrollbar-width:none!important;
    border-bottom:1px solid var(--line)!important;background:#0a213b!important;
  }
  .v31-mobile-role-strip::-webkit-scrollbar{display:none!important}
  .v31-mobile-role-strip button{
    flex:0 0 auto!important;min-width:34px!important;height:27px!important;min-height:27px!important;
    padding:2px 7px!important;border-radius:7px!important;background:#173554!important;color:#8ea5bc!important;
    border:1px solid rgba(85,128,170,.45)!important;font-size:8px!important;font-weight:900!important;opacity:.48!important;
  }
  .v31-mobile-role-strip button.active{opacity:1!important;color:#fff!important;box-shadow:0 0 0 1px rgba(255,255,255,.18) inset!important}
  .v31-mobile-role-strip button[data-v31-role="__ALL__"].active{background:var(--primary)!important}
  .v31-mobile-role-strip .v23-role-por.active{background:#f4b629!important;color:#152238!important}
  .v31-mobile-role-strip .v23-role-def.active{background:#4f9d2f!important}
  .v31-mobile-role-strip .v23-role-mid.active{background:#2f73d5!important}
  .v31-mobile-role-strip .v23-role-wing.active{background:#b018b8!important}
  .v31-mobile-role-strip .v23-role-att.active{background:#c82f45!important}

  /* Drawer rows gain one header row, without stealing list scroll space. */
  body.v23-free-open .v23-mobile-drawer-free-panel{
    grid-template-rows:auto auto auto minmax(0,1fr)!important;
  }
}
</style>
'''

runtime=r'''
<script id="v31-mobile-queue-roles-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V31_MOBILE_QUEUE_ROLES__)return;
  window.__FANTA_V31_MOBILE_QUEUE_ROLES__=1;
  const qs=(s,r=document)=>r.querySelector(s);
  function canManage(){try{return typeof auctionCanManageCallQueue==='function'&&auctionCanManageCallQueue()}catch{return false}}
  function syncQueuePause(){
    const card=qs('.v30-mobile-queue'),head=card?.querySelector(':scope>header');if(!head)return;
    qs('[data-v30-pause]')?.remove();
    let actions=qs('.v31-queue-head-actions',head);
    if(!actions){
      actions=document.createElement('div');actions.className='v31-queue-head-actions';
      const count=qs('[data-v30-queue-count]',head);if(count)actions.appendChild(count);
      const b=document.createElement('button');b.type='button';b.className='secondary v31-queue-pause';b.dataset.v31QueuePause='1';actions.appendChild(b);head.appendChild(actions);
    }
    const paused=state.auction?.callQueueSettings?.autoPaused===true,b=qs('[data-v31-queue-pause]',head);if(!b)return;
    b.textContent=paused?'RIPRENDI':'PAUSA';b.classList.toggle('is-paused',paused);b.disabled=!canManage();
    b.title=paused?'Riattiva l’autoplay della coda':'Metti in pausa l’autoplay della coda';
  }
  async function toggleQueuePause(){
    if(!canManage())return;
    const current=state.auction?.callQueueSettings?.autoPaused===true,next=!current;
    try{if(typeof setAuctionQueuePausePending==='function')setAuctionQueuePausePending(next);}catch{}
    state.auction.callQueueSettings={...(state.auction.callQueueSettings||{}),autoPaused:next};syncQueuePause();
    try{if(typeof patchAuctionCallQueueUi==='function')patchAuctionCallQueueUi();}catch{}
    try{
      if(typeof persistAuctionQueuePaused==='function'){await persistAuctionQueuePaused(next,{quiet:false});}
      else{
        const s=state.auction?.auctionSession;if(!s?.id)throw new Error('Sessione asta non disponibile.');
        await api(ENDPOINTS.auction,{action:'setCallQueuePaused',sessionId:s.id,paused:next},{quiet:false});
      }
    }catch(err){state.auction.callQueueSettings={...(state.auction.callQueueSettings||{}),autoPaused:current};syncQueuePause();if(typeof msg==='function')msg(err.message||'Aggiornamento coda non riuscito.','error');}
  }
  document.addEventListener('click',e=>{const b=e.target.closest?.('[data-v31-queue-pause]');if(!b)return;e.preventDefault();e.stopPropagation();void toggleQueuePause();},true);
  let raf=0;function schedule(){cancelAnimationFrame(raf);raf=requestAnimationFrame(syncQueuePause)}
  const root=document.getElementById('view-auction');if(root)new MutationObserver(schedule).observe(root,{subtree:true,childList:true});
  window.addEventListener('hashchange',schedule);setInterval(()=>{if(document.body.classList.contains('v23-mobile-auction'))syncQueuePause();},900);schedule();
})();
</script>
'''

if '</head>' not in text or '</body>' not in text:
    raise SystemExit('closing markers missing')
text=text.replace('</head>',style+'\n</head>',1)
text=text.replace('</body>',runtime+'\n</body>',1)
p.write_text(text,encoding='utf-8')
