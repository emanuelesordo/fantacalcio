from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')

MARK='v33-manual-flow-mobile-index-runtime'
if MARK in s:
    raise SystemExit('V33 already present')

style=r'''
<style id="v33-manual-flow-mobile-index-style">
/* Numeric values are centered consistently in all data tables. */
table td.num,table th.num,table td.v33-numeric-cell,table th.v33-numeric-cell,
#view-list .v12-col-presence,#view-list .v12-col-pfc,#view-list .v12-col-pma,
#view-list .v12-col-delta,#view-list .v12-col-index,#view-list .v12-col-threshold,
#view-list .v12-col-expected,#view-list .v12-col-fmv,#view-list .v12-col-slot{
  text-align:center!important;
}

/* The private Index value is deliberately visible, but not visually dominant. */
body.v10-index-owner .strategic-index-value,
body.v10-index-owner #view-list td.v12-col-index,
body.v10-index-owner #view-auction td.v12-col-index{
  color:#d8c0ff!important;
  font-weight:950!important;
  text-shadow:0 0 8px rgba(181,137,255,.20)!important;
  background:rgba(151,103,255,.055)!important;
}

/* V33 continuous economic gradient: red <- yellow (zero) -> green. */
body.v10-index-owner #view-list tr.v33-index-market-row,
body.v10-index-owner #view-auction tr.v33-index-market-row{
  background:linear-gradient(90deg,
    hsl(var(--v33-market-hue) 76% 46% / var(--v33-market-alpha)),
    transparent 86%)!important;
  box-shadow:inset 3px 0 0 hsl(var(--v33-market-hue) 84% 51% / .78)!important;
  transition:background .16s ease,box-shadow .16s ease!important;
}

/* Manual live mode: queue and countdown timers disappear; controls remain manual. */
#view-auction.v33-manual-flow .v30-mobile-queue,
#view-auction.v33-manual-flow .auction-queue-card,
#view-auction.v33-manual-flow .auction-call-queue,
#view-auction.v33-manual-flow [data-auction-queue],
#view-auction.v33-manual-flow .v33-manual-hidden{
  display:none!important;
}
#view-auction.v33-manual-flow .v33-manual-status{
  display:flex!important;
}
.v33-manual-status{
  display:none;
  align-items:center;
  justify-content:center;
  min-height:28px;
  padding:4px 9px;
  border:1px solid rgba(245,190,66,.42);
  border-radius:8px;
  background:rgba(245,190,66,.09);
  color:#f5d77f;
  font-size:8px;
  font-weight:900;
  letter-spacing:.05em;
  text-transform:uppercase;
}
#v33-manual-live-toggle{
  min-height:34px!important;
  height:34px!important;
  padding:4px 9px!important;
  white-space:nowrap!important;
  font-size:8px!important;
  font-weight:950!important;
}
#v33-manual-live-toggle.active{
  border-color:rgba(245,190,66,.70)!important;
  background:rgba(245,190,66,.18)!important;
  color:#ffe19a!important;
}
.v33-setup-manual{
  display:grid;
  gap:6px;
  margin-top:8px;
  padding:10px;
  border:1px solid var(--line2);
  border-radius:10px;
  background:rgba(8,31,55,.46);
}
.v33-setup-manual label{
  display:flex!important;
  align-items:center!important;
  gap:8px!important;
  margin:0!important;
  font-weight:900!important;
}
.v33-setup-manual input[type="checkbox"]{width:18px!important;height:18px!important;flex:0 0 18px!important}
.v33-setup-manual small{color:var(--soft);font-size:8px;line-height:1.35}

/* Mobile Listone: identity + only TIT, PFC, PMA and FMV data. */
@media(max-width:820px){
  #view-list .player-table{
    width:100%!important;
    min-width:0!important;
    table-layout:auto!important;
  }
  #view-list .player-table th:nth-child(3),#view-list .player-table td:nth-child(3),
  #view-list .player-table th:nth-child(4),#view-list .player-table td:nth-child(4),
  #view-list .player-table th:nth-child(5),#view-list .player-table td:nth-child(5),
  #view-list .player-table th:nth-child(9),#view-list .player-table td:nth-child(9),
  #view-list .player-table th:nth-child(10),#view-list .player-table td:nth-child(10),
  #view-list .player-table th:nth-child(11),#view-list .player-table td:nth-child(11),
  #view-list .player-table th:nth-child(12),#view-list .player-table td:nth-child(12),
  #view-list .player-table th:nth-child(14),#view-list .player-table td:nth-child(14){display:none!important}

  #view-list .player-table th:nth-child(1),#view-list .player-table td:nth-child(1){width:58px!important;min-width:58px!important}
  #view-list .player-table th:nth-child(2),#view-list .player-table td:nth-child(2){width:auto!important;min-width:104px!important;text-align:left!important}
  #view-list .player-table th:nth-child(6),#view-list .player-table td:nth-child(6),
  #view-list .player-table th:nth-child(7),#view-list .player-table td:nth-child(7),
  #view-list .player-table th:nth-child(8),#view-list .player-table td:nth-child(8),
  #view-list .player-table th:nth-child(13),#view-list .player-table td:nth-child(13){width:54px!important;min-width:48px!important;text-align:center!important}
  #view-list .player-table th,#view-list .player-table td{padding-left:4px!important;padding-right:4px!important}

  /* Manual mode also removes the mobile queue row from the shell. */
  body.v23-mobile-auction #view-auction.v33-manual-flow .v23-mobile-shell{
    grid-template-rows:auto auto minmax(0,1fr) auto!important;
  }
}
</style>
'''

runtime=r'''
<script id="v33-manual-flow-mobile-index-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V33_MANUAL_FLOW__)return;
  window.__FANTA_V33_MANUAL_FLOW__=1;

  const ENDPOINT=`${SUPABASE_URL}/functions/v1/manual-auction-mode-api`;
  const q=(s,r=document)=>r.querySelector(s);
  const qa=(s,r=document)=>[...r.querySelectorAll(s)];
  const num=v=>Number.isFinite(Number(v))?Number(v):null;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const owner=()=>String(state.dashboard?.currentUser?.username||state.session?.user?.username||'').trim().toLowerCase()==='emanuelesordo';

  function session33(){return state.auction?.auctionSession||state.auction?.session||state.auctionSession||null}
  function manual33(){return session33()?.setup_snapshot?.manual_auction_flow===true}
  function playerPool33(){
    const lists=[state.list?.players,state.auction?.callCandidates,state.auction?.players,state.auction?.availablePlayers];
    const map=new Map();
    for(const list of lists)for(const p of (list||[]))if(p?.id)map.set(String(p.id),p);
    return map;
  }

  async function modeApi33(payload){
    return await api(ENDPOINT,payload,{quiet:true});
  }

  /* -------------------- setup -------------------- */
  let setupLeague33='';
  async function mountSetup33(){
    const form=document.getElementById('setup-form');
    if(!form)return;
    const leagueId=String(state.selectedLeague?.id||'');
    let box=form.querySelector('.v33-setup-manual');
    if(!box){
      box=document.createElement('section');
      box.className='v33-setup-manual';
      box.innerHTML=`<label><input type="checkbox" id="v33-manual-default"><span>Asta manuale · senza coda e timer</span></label><small>Nessun timer di chiamata o rilancio e nessuna coda automatica. Il Banditore/Admin conclude l'acquisto e usa PASSA TURNO quando vuole assegnare la chiamata al presidente successivo.</small>`;
      const anchor=[...form.querySelectorAll('button')].find(b=>/salva/i.test(b.textContent||''));
      if(anchor)anchor.before(box);else form.appendChild(box);
      const input=box.querySelector('#v33-manual-default');
      input.addEventListener('change',async()=>{
        const wanted=input.checked;input.disabled=true;
        try{
          const res=await modeApi33({action:'setDefault',enabled:wanted});
          input.checked=res?.enabled===true;
          if(typeof msg==='function')msg(input.checked?'Modalità asta manuale impostata.':'Modalità asta automatica ripristinata.','success');
        }catch(e){input.checked=!wanted;if(typeof msg==='function')msg(e?.message||'Impossibile salvare la modalità asta.','error')}
        finally{input.disabled=false}
      });
    }
    if(!leagueId||setupLeague33===leagueId)return;
    setupLeague33=leagueId;
    try{
      const res=await modeApi33({action:'getDefault'});
      const input=box.querySelector('#v33-manual-default');
      input.checked=res?.enabled===true;
      input.disabled=res?.canEdit!==true;
    }catch(e){console.warn('V33 setup manual mode',e)}
  }

  /* -------------------- live toggle -------------------- */
  function canControl33(){
    const p=state.auction?.permissions||{};
    if(p.canControlAuction||p.canAuctioneer||p.canManageAuction||p.isLeagueAdmin)return true;
    return Boolean(document.getElementById('auction-finish')||document.getElementById('auction-pass-turn'));
  }
  function liveHost33(){
    return q('#view-auction .auction-header-actions')||q('#view-auction .header-actions')||q('#view-auction .auction-toolbar')||q('#view-auction .v30-auction-functions')||q('#view-auction');
  }
  function mountLiveToggle33(){
    const view=document.getElementById('view-auction');if(!view)return;
    const enabled=manual33();
    view.classList.toggle('v33-manual-flow',enabled);
    markManualElements33(view,enabled);
    let status=view.querySelector('.v33-manual-status');
    if(!status){status=document.createElement('div');status.className='v33-manual-status';status.textContent='MANUALE · timer e coda disattivati · aggiudica e passa turno dal banditore';const host=liveHost33();if(host&&host!==view)host.prepend(status);else view.prepend(status)}
    if(!canControl33())return;
    let button=document.getElementById('v33-manual-live-toggle');
    const host=liveHost33();if(!host)return;
    if(!button){
      button=document.createElement('button');button.type='button';button.id='v33-manual-live-toggle';button.className='secondary';
      button.addEventListener('click',async()=>{
        const ses=session33();if(!ses?.id)return;
        const wanted=!manual33();button.disabled=true;
        try{
          const res=await modeApi33({action:'setLive',sessionId:ses.id,enabled:wanted});
          if(res?.auctionSession){
            if(state.auction?.auctionSession)state.auction.auctionSession=res.auctionSession;
            else if(state.auction?.session)state.auction.session=res.auctionSession;
          }else if(ses?.setup_snapshot){ses.setup_snapshot.manual_auction_flow=res?.enabled===true}
          if(typeof loadAuction==='function')await loadAuction({quiet:true,onlyIfChanged:false});
          if(typeof msg==='function')msg(wanted?'Modalità manuale: coda e timer disattivati.':'Modalità automatica: coda e timer ripristinati.','success');
        }catch(e){if(typeof msg==='function')msg(e?.message||'Impossibile cambiare modalità asta.','error')}
        finally{button.disabled=false;requestAnimationFrame(mountLiveToggle33)}
      });
    }
    if(button.parentElement!==host){
      const finish=document.getElementById('auction-finish');
      if(finish&&finish.parentElement===host)host.insertBefore(button,finish);else host.appendChild(button);
    }
    button.classList.toggle('active',enabled);
    button.textContent=enabled?'MANUALE · NO TIMER/CODA':'AUTO · CODA+TIMER';
    button.setAttribute('aria-pressed',enabled?'true':'false');
  }

  function markManualElements33(view,enabled){
    if(!enabled){qa('.v33-manual-hidden',view).forEach(el=>el.classList.remove('v33-manual-hidden'));return}
    const exactSelectors=['.v30-mobile-queue','.auction-queue-card','.auction-call-queue','[data-auction-queue]'];
    exactSelectors.forEach(sel=>qa(sel,view).forEach(el=>el.classList.add('v33-manual-hidden')));
    qa('button',view).forEach(b=>{
      const t=(b.textContent||'').trim().toUpperCase();
      if(t==='CODA'||t==='PAUSA CODA'||t==='OFFUSCA CODA')b.classList.add('v33-manual-hidden');
    });
    qa('section,article,div',view).forEach(el=>{
      if(el.children.length>30)return;
      const own=[...el.children].some(ch=>/^(PROSSIME CHIAMATE|CODA CHIAMATE)$/i.test((ch.textContent||'').trim()));
      if(own)el.classList.add('v33-manual-hidden');
    });
    /* Hide visual countdown boxes, but never HOLD / auction function buttons. */
    qa('[data-auction-timer],.auction-command-timer,.auction-timer-card,.timer-card',view).forEach(el=>el.classList.add('v33-manual-hidden'));
    qa('div,section,article',view).forEach(el=>{
      if(el.children.length>8)return;
      const first=(el.firstElementChild?.textContent||'').trim().toUpperCase();
      if(first==='TIMER'&&!el.closest('.v30-auction-functions'))el.classList.add('v33-manual-hidden');
    });
  }

  /* -------------------- continuous Index gradient -------------------- */
  function paintIndex33(){
    if(!owner())return;
    const players=playerPool33();
    qa('#view-list tr[data-player-id],#view-auction tr[data-player-id]').forEach(row=>{
      const p=players.get(String(row.dataset.playerId));if(!p)return;
      let idx=null;try{idx=num(typeof strategicValueIndex==='function'?strategicValueIndex(p):null)}catch{}
      const vals=[num(p?.pfc),num(p?.pma)].filter(v=>v!=null&&v>=0);
      if(idx==null||!vals.length)return;
      const market=vals.reduce((a,b)=>a+b,0)/vals.length;
      const delta=idx-market;
      const scale=Math.max(8,Math.abs(idx),Math.abs(market));
      const relative=delta/scale;
      const strength=clamp(Math.abs(relative)/.35,0,1);
      /* 52 = yellow at exactly zero; smoothly approach green 128 or red 0. */
      const hue=relative>=0?52+(128-52)*strength:52*(1-strength);
      const alpha=.060+.115*strength;
      row.classList.remove('v30-index-market-row');
      row.classList.add('v33-index-market-row');
      row.style.setProperty('--v33-market-hue',hue.toFixed(1));
      row.style.setProperty('--v33-market-alpha',alpha.toFixed(3));
      row.title=`Indice ${Math.round(idx)} cr · PFC/PMA medio ${market.toFixed(1)} · delta ${delta>=0?'+':''}${delta.toFixed(1)} cr`;
    });
  }

  /* -------------------- numeric cell alignment -------------------- */
  function centerNumbers33(root=document){
    qa('table td,table th',root).forEach(cell=>{
      if(cell.matches('.num')){cell.classList.add('v33-numeric-cell');return}
      if(cell.querySelector('button,input,select,.rolebadge'))return;
      const t=(cell.textContent||'').trim().replace(',','.');
      if(/^[+\-]?\d+(?:\.\d+)?(?:\s*%|\s*cr)?$/.test(t))cell.classList.add('v33-numeric-cell');
    });
  }

  let raf=0;
  function reconcile33(){
    cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{
      mountSetup33();
      mountLiveToggle33();
      centerNumbers33();
      paintIndex33();
    });
  }

  const mo=new MutationObserver(reconcile33);
  if(document.body)mo.observe(document.body,{subtree:true,childList:true});
  else document.addEventListener('DOMContentLoaded',()=>mo.observe(document.body,{subtree:true,childList:true}),{once:true});
  window.addEventListener('hashchange',reconcile33);
  window.addEventListener('resize',reconcile33,{passive:true});
  setInterval(reconcile33,1200);
  reconcile33();
})();
</script>
'''

if '</head>' not in s or '</body>' not in s:
    raise SystemExit('HTML structure not found')
s=s.replace('</head>',style+'\n</head>',1)
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('V33 applied')
