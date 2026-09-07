from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')
if 'v16-auction-queue-cards-runtime' in s:
    raise SystemExit('V16 already applied')

runtime=r'''
<script id="v16-auction-queue-cards-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V16_AUCTION__)return;
  window.__FANTA_V16_AUCTION__=1;

  const ownPresident=()=>typeof auctionHasPresidentRole==='function'&&auctionHasPresidentRole();
  const ownCallTurn=()=>typeof auctionOwnCallTurn==='function'&&auctionOwnCallTurn();
  const queueRows=()=>typeof auctionQueueRows==='function'?(auctionQueueRows()||[]):[];

  function v16FirstValidQueued(){
    const candidates=new Set((state.auction?.callCandidates||[]).map(p=>String(p.id)));
    return queueRows().find(q=>{
      const id=String(q?.player_id||q?.player?.id||'');
      if(!id||!candidates.has(id)||!q?.player)return false;
      if(typeof auctionPlayerMatchesCurrentRolePhase==='function'&&!auctionPlayerMatchesCurrentRolePhase(q.player))return false;
      return q.player.status==='available'||q.player.status==null;
    })||null;
  }

  function v16PreselectQueue(){
    const session=typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession;
    if(!session||session.status!=='live'||session.current_player_id||!ownPresident()||!ownCallTurn())return;
    if(state.auction?.callQueueSettings?.autoPaused===true)return;
    const q=v16FirstValidQueued();if(!q)return;
    const key=[session.id,session.current_nomination_team_id,session.nomination_deadline||session.nomination_starts_at||'',q.id].join('|');
    if(state.v16QueuePreselectKey===key&&String(state.auctionSelectedPlayerId||'')===String(q.player_id||q.player?.id||''))return;
    state.v16QueuePreselectKey=key;
    state.auctionSelectedPlayerId=q.player_id||q.player?.id||null;
    state.auctionOpeningBid=Math.max(1,Number(q.opening_bid||1));
  }

  function v16QueueNote(){
    const note=document.querySelector('.auction-queue-mode-note.is-auto');
    if(!note)return;
    const q=v16FirstValidQueued();
    if(ownPresident()&&ownCallTurn()&&q){
      const secs=Number(state.auction?.settings?.nomination_timeout_seconds||state.auction?.auctionSession?.setup_snapshot?.nomination_timeout_seconds||20);
      note.textContent=`Coda pronta · ${q.player?.name||'prima voce'} è già selezionato. Conferma CHIAMA entro ${secs}s.`;
    }else{
      note.textContent='Coda automatica · al tuo turno la prima voce valida viene preselezionata; la chiamata resta da confermare.';
    }
  }

  /* Il timer rilanci diventa attivo solo dopo timer_starts_at (2s dalla conferma chiamata). */
  if(typeof auctionBidTimerIsActive==='function'){
    auctionBidTimerIsActive=function(session=(typeof auctionSession==='function'?auctionSession():state.auction?.auctionSession)){
      if(!session||session.status!=='live'||!session.current_player_id||session.prestart_hold===true||session.hold_active===true||session.timer_expired_at||!session.timer_deadline)return false;
      const now=Date.now()+Number(state.serverOffsetMs||0),start=Date.parse(session.timer_starts_at||''),deadline=Date.parse(session.timer_deadline||'');
      if(Number.isFinite(start)&&now<start)return false;
      return Number.isFinite(deadline)&&deadline>now;
    };
  }

  function v16TrimCalledDetails(){
    const card=document.querySelector('.v14-called-details');if(!card)return;
    const remove=new Set(['ruoli','squadra','slot','volatilità','fv ultimo anno','fv ultimi 5']);
    card.querySelectorAll('.v14-called-grid>span').forEach(cell=>{
      const label=String(cell.querySelector('small')?.textContent||'').trim().toLowerCase();
      if(remove.has(label))cell.remove();
    });
    card.classList.add('v16-compact-called-details');
  }

  function v16AfterRender(){
    v16TrimCalledDetails();
    v16QueueNote();
  }

  if(typeof renderAuctionLive==='function'){
    const old=renderAuctionLive;
    renderAuctionLive=function(...args){
      v16PreselectQueue();
      const r=old(...args);
      queueMicrotask(v16AfterRender);
      return r;
    };
  }

  if(typeof loadAuction==='function'){
    const oldLoad=loadAuction;
    loadAuction=async function(...args){
      const r=await oldLoad(...args);
      v16PreselectQueue();
      if(state.view==='auction'&&state.auction?.auctionSession?.status==='live')renderAuctionLive();
      return r;
    };
  }

  const css=document.createElement('style');css.id='v16-auction-queue-cards-style';css.textContent=`
    /* Card dati giocatore: solo dati utili non già presenti nel blocco chiamata. */
    body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details{padding:4px 5px!important;gap:3px!important}
    body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details .v14-called-grid{grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:3px!important}
    body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details .v14-called-grid>span{min-height:31px!important;padding:2px 4px!important;display:flex!important;flex-direction:column!important;justify-content:center!important}
    body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details .v14-called-grid small{font-size:5.3px!important}
    body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details .v14-called-grid b{font-size:7.4px!important}

    /* SUGG e MAX affiancati sulla stessa linea e più leggibili. */
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-prices{
      display:flex!important;flex-direction:row!important;align-items:center!important;justify-content:flex-end!important;gap:6px!important;min-width:max-content!important;width:auto!important;white-space:nowrap!important
    }
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-prices b,
    html body.modern-glass #view-auction .auction-free-suggestions .auction-v7-prices small{
      display:inline-block!important;font-size:7.2px!important;line-height:1!important;font-weight:950!important;letter-spacing:.01em!important
    }

    /* Durante i 2 secondi iniziali i controlli di rilancio appaiono realmente non attivi. */
    #view-auction .auction-command-timer:has([data-auction-timer][aria-label*="partenza"]){opacity:.88}
    @media(max-width:900px){body.v10-index-owner #view-auction .v14-called-details.v16-compact-called-details .v14-called-grid{grid-template-columns:repeat(5,minmax(70px,1fr))!important;overflow-x:auto!important}}
  `;document.head.appendChild(css);

  if(state.view==='auction'){v16PreselectQueue();queueMicrotask(v16AfterRender);}
})();
</script>
'''
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
