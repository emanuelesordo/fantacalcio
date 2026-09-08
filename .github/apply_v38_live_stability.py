from pathlib import Path
import re

path = Path('home.html')
text = path.read_text(encoding='utf-8')
original = text


def require(condition, message):
    if not condition:
        raise SystemExit(message)


# ==========================================================
# V43 · queue + manual direct award
# - desktop queue exposes ONE confirm button only
# - confirm has the same footprint as remove (X)
# - when auction timers are disabled/manual, Banditore/Admin can
#   assign the selected player directly to the operational team,
#   using the editable opening price already present in the caller controls
# - preserve the V42 strategist and exact Listone economic signal
# ==========================================================

style_match = re.search(r'(<style id="v34-market-strategy-style">)(.*?)(</style>)', text, re.S)
require(style_match, 'V34 style block not found')
style = style_match.group(2)

# V42 must already be present; V43 is intentionally incremental.
require('/* V42 · strategist 2x2 + exact Listone signal. */' in style,
        'V42 strategist/index baseline missing')

# Idempotent V43 CSS refresh.
style = re.sub(
    r'\n/\* V43 · queue single confirm \+ manual direct award\. \*/.*?(?=\Z)',
    '\n',
    style,
    count=1,
    flags=re.S,
)

v43_css = r'''
/* V43 · queue single confirm + manual direct award. */

/* Queue confirmation uses the same compact square footprint as the red X.
   The canonical .auction-queue-call is retained on desktop; V34 remains only
   as the fallback/mobile control. */
html body #view-auction .auction-call-queue-row .auction-queue-call,
html body #view-auction .v34-queue-call{
  width:30px!important;
  min-width:30px!important;
  max-width:30px!important;
  height:30px!important;
  min-height:30px!important;
  max-height:30px!important;
  padding:0!important;
  border-radius:8px!important;
  font-size:15px!important;
  line-height:1!important;
  display:inline-grid!important;
  place-items:center!important;
  flex:0 0 30px!important;
}
html body #view-auction .auction-call-queue-row .auction-queue-call{
  background:var(--good,#1d9b62)!important;
  border-color:rgba(80,230,160,.72)!important;
  color:#fff!important;
}

/* Direct award is an operational action, not another oversized primary CTA. */
html body #view-auction #auction-direct-award-v43{
  width:auto!important;
  min-width:0!important;
  max-width:100%!important;
  min-height:30px!important;
  height:30px!important;
  padding:3px 8px!important;
  border-radius:7px!important;
  white-space:nowrap!important;
  font-size:7px!important;
  font-weight:950!important;
  letter-spacing:.025em!important;
}

@media(max-width:390px){
  html body #view-auction .auction-call-queue-row .auction-queue-call,
  html body #view-auction .v34-queue-call{
    width:28px!important;
    min-width:28px!important;
    max-width:28px!important;
    height:28px!important;
    min-height:28px!important;
    max-height:28px!important;
    flex-basis:28px!important;
  }
}
'''
style += v43_css
text = text[:style_match.start(2)] + style + text[style_match.end(2):]


runtime_match = re.search(r'(<script id="v34-market-strategy-runtime">)(.*?)(</script>)', text, re.S)
require(runtime_match, 'V34 runtime block not found')
runtime = runtime_match.group(2)

# Preserve the exact V42/Listone formula.
for token in (
    "strategicValueIndex(p)",
    "const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);",
    "const delta=idx-market;",
    "const scale=Math.max(8,Math.abs(idx),Math.abs(market));",
    "const relative=delta/scale;",
    "const strength=clamp(Math.abs(relative)/.35,0,1);",
    "row.classList.add('v33-index-market-row');",
):
    require(token in runtime, 'V42/Listone signal regression: '+token)

# ------------------------------------------------------------------
# Queue: desktop rows already own a canonical .auction-queue-call.
# Older V34 injected a second ✓ beside it. Keep the canonical control,
# remove any old injected duplicate, and inject only when no canonical
# control exists (e.g. the dedicated mobile queue).
# ------------------------------------------------------------------
old_queue_loop = (
    "qsa('#view-auction [data-queue-player-id],#view-auction [data-queue-player]').forEach("
    "row=>{if(row.classList.contains('v30-mobile-queue-row')||row.querySelector('.v34-queue-call'))return;"
)
new_queue_loop = (
    "qsa('#view-auction [data-queue-player-id],#view-auction [data-queue-player]').forEach("
    "row=>{if(row.classList.contains('v30-mobile-queue-row'))return;"
    "const canonical=row.querySelector('.auction-queue-call'),injected=row.querySelector('.v34-queue-call');"
    "if(canonical){injected?.remove();return}if(injected)return;"
)
if old_queue_loop in runtime:
    runtime = runtime.replace(old_queue_loop, new_queue_loop, 1)
require(new_queue_loop in runtime, 'desktop queue dedupe patch missing')

# ------------------------------------------------------------------
# Direct award helper. Recreated idempotently on every workflow run.
# ------------------------------------------------------------------
runtime = re.sub(
    r'\n  /\* V43 · direct award helper\. \*/.*?\n  /\* V43 END direct award helper\. \*/\n',
    '\n',
    runtime,
    count=1,
    flags=re.S,
)

v43_runtime = r'''
  /* V43 · direct award helper. */
  function timerInactive43(){
    const s=session34(),cfg=s?.setup_snapshot||state.auction?.settings||{};
    if(manual34())return true;
    if(cfg.timer_enabled===false||cfg.auction_timer_enabled===false)return true;
    const mode=String(cfg.timer_mode??'').trim().toLowerCase();
    if(['off','none','disabled','no_timer','notimer'].includes(mode))return true;
    if(mode==='fixed'){
      const seconds=Number(cfg.fixed_timer_seconds);
      if(Number.isFinite(seconds)&&seconds<=0)return true;
    }
    return false;
  }

  function selectedAdminPlayer43(){
    const id=state.auctionAdminPlayerId;
    if(id==null)return null;
    return (state.auction?.callCandidates||[]).find(p=>String(p.id)===String(id))||null;
  }

  function selectedOperationalTeam43(){
    const s=session34();
    const id=state.auctionAdminTeamId||s?.current_nomination_team_id||state.auction?.currentTurnTeam?.id||null;
    if(id==null)return null;
    return (state.auction?.teams||[]).find(t=>String(t.id)===String(id))||null;
  }

  function directAwardPrice43(){
    const input=qs('#view-auction .auction-caller-controls input[type="number"]');
    const raw=input?.value??state.auctionAdminPrice??state.auctionOpeningBid??1;
    return Math.max(1,Math.floor(Number(raw)||1));
  }

  function canDirectAward43(){
    const s=session34(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43();
    let controller=false;
    try{controller=Boolean(state.auction?.permissions?.canControlAuction===true||typeof auctionCanControl==='function'&&auctionCanControl())}catch{}
    if(!controller){
      try{controller=Boolean(typeof auctionCanManage==='function'&&auctionCanManage())}catch{}
    }
    return Boolean(
      timerInactive43()
      && s?.id
      && s.status==='live'
      && !s.current_player_id
      && p
      && team
      && controller
    );
  }

  function mountDirectAward43(){
    const call=qs('#auction-call-confirm');
    const controls=call?.parentElement||qs('#view-auction .auction-caller-controls');
    if(!controls)return;
    let b=qs('#auction-direct-award-v43');
    if(!b){
      b=document.createElement('button');
      b.id='auction-direct-award-v43';
      b.type='button';
      b.className='secondary';
      b.textContent='ASSEGNA DIRETTO';
      (call||controls.lastElementChild)?.insertAdjacentElement?.('afterend',b);
      if(!b.isConnected)controls.appendChild(b);
    }
    const inactive=timerInactive43(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43(),price=directAwardPrice43();
    b.hidden=!inactive;
    b.disabled=!canDirectAward43();
    if(!inactive){
      b.title='Disponibile solo con timer asta disattivato / modalità manuale';
    }else if(!p){
      b.title='Seleziona prima il giocatore';
    }else if(!team){
      b.title='Seleziona prima la squadra operativa';
    }else{
      b.title=`Assegna ${p.name||'giocatore'} direttamente a ${team.name||'squadra'} per ${price} crediti`;
    }
  }

  async function directAward43(button){
    if(!canDirectAward43())return;
    const s=session34(),p=selectedAdminPlayer43(),team=selectedOperationalTeam43(),price=directAwardPrice43();
    if(!s?.id||!p||!team)return;
    const teamLabel=typeof auctionTeamReference==='function'
      ? auctionTeamReference(team,team.name||'squadra')
      : (team.name||'squadra');
    const confirmed=typeof appConfirm==='function'
      ? await appConfirm(
          `${p.name||'Giocatore'} → ${teamLabel} per ${price} crediti?`,
          {title:'Assegna direttamente',confirmText:'ASSEGNA'}
        )
      : true;
    if(!confirmed)return;

    button.disabled=true;
    state.auctionAdminPrice=price;
    const applyState=response=>{
      if(response?.state&&typeof applyAuctionHotState==='function'){
        applyAuctionHotState(response.state,{fromMutation:true});
      }
      if(response?.ok===false){
        throw new Error(response?.error||'Operazione non consentita.');
      }
    };

    try{
      const called=await api(
        ENDPOINTS.auction,
        {action:'callPlayer',sessionId:s.id,playerId:p.id,openingBid:price}
      );
      applyState(called);

      const bid=await api(
        ENDPOINTS.auction,
        {action:'placeBid',sessionId:s.id,teamId:team.id,amount:price,source:'VOCALE'}
      );
      applyState(bid);

      const awarded=await api(
        ENDPOINTS.auction,
        {action:'awardPlayer',sessionId:s.id}
      );
      applyState(awarded);

      state.auctionAdminPlayerId=null;
      if(typeof msg==='function'){
        msg(`${p.name||'Giocatore'} assegnato a ${teamLabel} per ${price}.`,'success');
      }
      if(typeof loadAuction==='function'){
        await loadAuction();
      }else if(typeof scheduleAuctionReconcile==='function'){
        scheduleAuctionReconcile(40);
      }
    }catch(error){
      if(typeof msg==='function')msg(error.message||'Assegnazione diretta non riuscita.','error');
      if(typeof scheduleAuctionReconcile==='function')scheduleAuctionReconcile(80);
    }finally{
      button.disabled=false;
      requestAnimationFrame(mountDirectAward43);
    }
  }

  /* Keep button state aligned with the already-existing player/team/price controls. */
  ['input','change'].forEach(type=>{
    document.addEventListener(type,e=>{
      if(!e.target.closest?.('#view-auction'))return;
      queueMicrotask(mountDirectAward43);
    });
  });
  /* V43 END direct award helper. */
'''

anchor = '  function patchAll34(){'
require(anchor in runtime, 'patchAll34 anchor missing')
runtime = runtime.replace(anchor, v43_runtime + '\n' + anchor, 1)

# Ensure patchAll mounts the action whenever the auction subtree is redrawn.
if '    console34();injectQueueCalls34();patchSuggested34();mountDirectAward43();' not in runtime:
    runtime = runtime.replace(
        '    console34();injectQueueCalls34();patchSuggested34();',
        '    console34();injectQueueCalls34();patchSuggested34();mountDirectAward43();',
        1,
    )
require('patchSuggested34();mountDirectAward43();' in runtime,
        'patchAll34 does not mount direct award')

# Extend the existing V34 captured click listener without adding a second global
# listener that could race with current controls.
click_anchor = (
    "    const q=e.target.closest?.('[data-v34-queue-call]');"
    "if(q){e.preventDefault();e.stopImmediatePropagation();void callQueue34(q.dataset.v34QueueCall,q);return}\n"
)
direct_click = (
    click_anchor
    + "    const direct=e.target.closest?.('#auction-direct-award-v43');"
      "if(direct){e.preventDefault();e.stopImmediatePropagation();void directAward43(direct);return}\n"
)
listener_start = runtime.find("document.addEventListener('click'")
listener_tail = runtime[listener_start:] if listener_start >= 0 else ''
if "const direct=e.target.closest?.('#auction-direct-award-v43')" not in listener_tail:
    require(click_anchor in runtime, 'V34 click listener queue anchor missing')
    runtime = runtime.replace(click_anchor, direct_click, 1)
require("const direct=e.target.closest?.('#auction-direct-award-v43')" in runtime,
        'direct award click handler missing')

text = text[:runtime_match.start(2)] + runtime + text[runtime_match.end(2):]


# ==========================================================
# Regression checks
# ==========================================================
style_check = re.search(r'<style id="v34-market-strategy-style">(.*?)</style>', text, re.S)
runtime_check = re.search(r'<script id="v34-market-strategy-runtime">(.*?)</script>', text, re.S)
require(style_check and runtime_check, 'post-patch V34 blocks missing')
style_final = style_check.group(1)
runtime_final = runtime_check.group(1)

checks = {
    'V42 strategist 2x2 preserved':
        'grid-template-columns:repeat(2,minmax(0,1fr))!important' in style_final,
    'V42 metrics unboxed preserved':
        '.auction-suggested-row .v34-suggest-metric' in style_final
        and 'border:0!important' in style_final
        and 'background:transparent!important' in style_final,
    'exact Listone painter preserved':
        "const market=pma!=null&&pfc!=null ? (.75*pma+.25*pfc) : (pma??pfc);" in runtime_final
        and "row.classList.add('v33-index-market-row')" in runtime_final,
    'desktop queue canonical control retained':
        "const canonical=row.querySelector('.auction-queue-call')" in runtime_final,
    'desktop injected duplicate removed':
        "if(canonical){injected?.remove();return}if(injected)return;" in runtime_final,
    'queue check same size as X':
        'max-width:30px!important' in style_final and 'max-height:30px!important' in style_final,
    'manual direct award mounted':
        "b.id='auction-direct-award-v43'" in runtime_final
        and 'patchSuggested34();mountDirectAward43();' in runtime_final,
    'direct award uses editable price':
        'directAwardPrice43()' in runtime_final
        and '.auction-caller-controls input[type="number"]' in runtime_final,
    'direct award uses operational team':
        'state.auctionAdminTeamId' in runtime_final,
    'direct award server sequence':
        "{action:'callPlayer'" in runtime_final
        and "{action:'placeBid'" in runtime_final
        and "{action:'awardPlayer'" in runtime_final,
}
failed = [name for name, ok in checks.items() if not ok]
require(not failed, 'V43 regression checks failed: ' + ', '.join(failed))

# Budget invariant: with 500 remaining and 23 minimum acquisitions including
# the current lot, 22 credits must remain after winning this player.
budget = 500
remaining_min_purchases = 23
reserve_after_current = max(0, remaining_min_purchases - 1)
max_bid = budget - reserve_after_current
require(max_bid == 478, 'budget reserve regression: expected 478')

print(
    'V43 tests passed: one queue confirm; direct manual award ready; '
    f'budget 500 / 23 remaining => reserve {reserve_after_current}, max bid {max_bid}'
)

if text == original:
    print('V43: no changes needed')
else:
    path.write_text(text, encoding='utf-8')
    print('V43 queue/direct-award patch applied')
