from pathlib import Path

p=Path('home.html')
s=p.read_text(encoding='utf-8')

if 'v12-listone-columns-runtime' in s:
    raise SystemExit('V12 already applied')

# Fix injury interpretation: 0 means not unavailable.
s=s.replace("if (flag === 'injury') return player.uncertain_return === true || (player.unavailable_until_round !== null && player.unavailable_until_round !== undefined && String(player.unavailable_until_round).trim() !== '');",
            "if (flag === 'injury') return player.uncertain_return === true || Number(player.unavailable_until_round || 0) > 0;")
s=s.replace("const injuryLabel = player?.uncertain_return === true\n        ? (until !== null && until !== undefined && String(until).trim() !== '' ? `Rientro incerto · fino G${until}` : 'Rientro incerto')\n        : (until !== null && until !== undefined && String(until).trim() !== '' ? `Indisponibile fino G${until}` : 'Indisponibile');",
            "const injuryRound = Number(until || 0);\n      const injuryLabel = player?.uncertain_return === true\n        ? (injuryRound > 0 ? `Rientro incerto · fino G${injuryRound}` : 'Rientro incerto')\n        : (injuryRound > 0 ? `Indisponibile fino G${injuryRound}` : '');")
s=s.replace("{ key:'injury', emoji:'🚑', label:injuryLabel, active:player?.uncertain_return === true || (until !== null && until !== undefined && String(until).trim() !== '') },",
            "{ key:'injury', emoji:'🚑', label:injuryLabel, active:player?.uncertain_return === true || injuryRound > 0 },")

runtime=r'''
<script id="v12-listone-columns-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V12_LISTONE__)return;
  window.__FANTA_V12_LISTONE__=1;

  const fmtPrice=v=>{const n=Number(v);return Number.isFinite(n)?String(Math.round(n)):'—'};
  const fmtDec=(v,d=2)=>{const n=Number(v);return Number.isFinite(n)?n.toFixed(d).replace('.',','):'—'};
  const escV=v=>typeof esc==='function'?esc(v):String(v??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
  const rolesV=(p,m)=>typeof playerRoles==='function'?playerRoles(p,m):[];
  const presenceV=p=>typeof strategicPresencePercent==='function'?strategicPresencePercent(p):Number(p?.expected_titolarity||0);
  const fmV=p=>typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):Number(p?.expected_fantasy_avg||0);
  const thresholdV=p=>typeof strategicThresholdPrice==='function'?strategicThresholdPrice(p):null;
  const expectedV=p=>typeof strategicExpectedPrice==='function'?strategicExpectedPrice(p):null;
  const indexV=p=>typeof strategicValueIndex==='function'?strategicValueIndex(p):'—';
  const signalV=p=>typeof auctionPlayerSignalBadges==='function'?auctionPlayerSignalBadges(p):'';
  const deltaV=p=>{
    const direct=Number(p?.pfc_pma_delta);
    if(Number.isFinite(direct))return direct;
    const a=Number(p?.pfc),b=Number(p?.pma);
    return Number.isFinite(a)&&Number.isFinite(b)?a-b:null;
  };

  function v12Row(player,mode,extraClass=''){
    const roles=rolesV(player,mode),delta=deltaV(player),idx=indexV(player),thr=thresholdV(player),exp=expectedV(player),fm=fmV(player),pr=presenceV(player);
    const deltaClass=delta==null?'':delta>0?'positive':delta<0?'negative':'';
    return `<tr class="auction-list-compatible-row ${extraClass}" data-player-id="${escV(player.id)}">
      <td class="player-role-cell v12-col-role">${roles.map(r=>`<span class="rolebadge" data-role="${escV(r)}">${escV(r)}</span>`).join('')}</td>
      <td class="v12-col-name"><span class="player-name">${escV(player.name||'—')}</span></td>
      <td class="v12-col-team">${escV(player.serie_a_team||'—')}</td>
      <td class="auction-signal-cell v12-col-badges">${signalV(player)}</td>
      <td class="num v12-col-slot">${escV(player.slot??'—')}</td>
      <td class="num v12-col-presence">${Number.isFinite(Number(pr))?Math.round(Number(pr))+'%':'—'}</td>
      <td class="num v12-col-pfc"><strong>${fmtPrice(player.pfc)}</strong></td>
      <td class="num v12-col-pma">${fmtPrice(player.pma)}</td>
      <td class="num v12-col-delta ${deltaClass}">${delta==null?'—':(delta>0?'+':'')+fmtPrice(delta)}</td>
      <td class="num v12-col-index strategic-index-value" title="${typeof strategicIndexTitle==='function'?escV(strategicIndexTitle(player)):''}">${idx}</td>
      <td class="num v12-col-threshold">${fmtPrice(thr)}</td>
      <td class="num v12-col-expected">${fmtPrice(exp)}</td>
      <td class="num v12-col-fmv">${fmtDec(fm,2)}</td>
      <td class="v12-col-fav"><span class="list-fav-slot"></span></td>
    </tr>`;
  }

  function v12PatchHeader(){
    const thead=document.querySelector('#view-list .player-table thead');
    if(!thead)return;
    thead.innerHTML=`<tr>
      <th class="v12-col-role">Ruoli</th>
      <th class="v12-col-name"><button data-list-sort="name">Nome ↕</button></th>
      <th class="v12-col-team"><button data-list-sort="team">Squadra ↕</button></th>
      <th class="v12-col-badges">Badge</th>
      <th class="v12-col-slot"><button data-list-sort="slot">Slot ↕</button></th>
      <th class="v12-col-presence">% Tit</th>
      <th class="v12-col-pfc"><button data-list-sort="pfc">PFC ↕</button></th>
      <th class="v12-col-pma"><button data-list-sort="pma">PMA ↕</button></th>
      <th class="v12-col-delta">Delta</th>
      <th class="v12-col-index"><button data-list-sort="index">Indice ↕</button></th>
      <th class="v12-col-threshold">Soglia</th>
      <th class="v12-col-expected">Prezzo atteso</th>
      <th class="v12-col-fmv"><button data-list-sort="fm">FMV ↕</button></th>
      <th class="v12-col-fav">Pref.</th>
    </tr>`;
  }

  function v12PatchListLayout(){
    const view=document.getElementById('view-list');if(!view)return;
    const layout=view.querySelector('.list-view-layout');if(!layout)return;
    const panels=[...layout.children].filter(x=>x.classList?.contains('panel'));
    if(panels[0])panels[0].classList.add('v12-hide-strip');
    const toolbar=panels[1]||layout.querySelector('.panel:has(#list-rolebar)');
    if(toolbar)toolbar.classList.add('v12-toolbar');
    const rolebar=document.getElementById('list-rolebar');
    const filters=toolbar?.querySelector('.filters');
    if(toolbar&&rolebar&&filters){
      let row=toolbar.querySelector('.v12-toolbar-row');
      if(!row){row=document.createElement('div');row.className='v12-toolbar-row';toolbar.prepend(row);row.append(rolebar,filters);}
    }
    v12PatchHeader();
  }

  if(typeof playerRow==='function')playerRow=v12Row;
  if(typeof renderListTable==='function'){
    const old=renderListTable;
    renderListTable=function(...a){const r=old(...a);v12PatchHeader();if(typeof hearts==='function')hearts();return r;};
  }
  if(typeof loadList==='function'){
    const old=loadList;
    loadList=async function(...a){const r=await old(...a);v12PatchListLayout();renderListTable();return r;};
  }

  const style=document.createElement('style');style.id='v12-listone-columns-style';style.textContent=`
    #view-list .v12-hide-strip{display:none!important}
    #view-list .list-view-layout{grid-template-rows:auto minmax(0,1fr)!important;gap:5px!important}
    #view-list .v12-toolbar{padding:4px 6px!important;min-height:38px!important}
    #view-list .v12-toolbar-row{display:grid!important;grid-template-columns:auto minmax(0,1fr)!important;gap:6px!important;align-items:center!important;min-height:30px!important}
    #view-list .v12-toolbar-row #list-rolebar{display:flex!important;flex-wrap:nowrap!important;gap:2px!important;overflow-x:auto!important;min-width:0!important}
    #view-list .v12-toolbar-row .rolebtn{min-width:30px!important;height:28px!important;min-height:28px!important;padding:2px 5px!important;font-size:8px!important}
    #view-list .v12-toolbar-row .filters{display:grid!important;grid-template-columns:minmax(180px,1.7fr) 135px 88px 135px 64px!important;gap:4px!important;align-items:center!important;margin:0!important}
    #view-list .v12-toolbar-row .filters label{display:grid!important;grid-template-columns:auto minmax(0,1fr)!important;align-items:center!important;gap:4px!important;font-size:7px!important;white-space:nowrap!important}
    #view-list .v12-toolbar-row .filters input,#view-list .v12-toolbar-row .filters select,#view-list .v12-toolbar-row .filters button{height:28px!important;min-height:28px!important;padding:2px 6px!important;font-size:8px!important}
    #view-list .player-table{min-width:1180px!important;table-layout:fixed!important}
    #view-list .player-table th,#view-list .player-table td{font-size:8px!important;padding:4px 5px!important;height:34px!important;vertical-align:middle!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
    #view-list .player-table th{font-size:7px!important;text-transform:uppercase!important;letter-spacing:.04em!important;text-align:center!important}
    #view-list .player-table th button{font-size:7px!important;text-align:center!important;padding:0!important}
    #view-list .player-name{font-size:9px!important;font-weight:900!important}
    #view-list .v12-col-role{width:74px!important;text-align:left!important}
    #view-list .v12-col-name{width:170px!important;text-align:left!important}
    #view-list .v12-col-team{width:105px!important;text-align:left!important}
    #view-list .v12-col-badges{width:84px!important;text-align:center!important}
    #view-list .v12-col-slot{width:48px!important;text-align:center!important}
    #view-list .v12-col-presence{width:56px!important;text-align:center!important}
    #view-list .v12-col-pfc,#view-list .v12-col-pma,#view-list .v12-col-delta{width:56px!important;text-align:right!important}
    #view-list .v12-col-index{width:58px!important;text-align:center!important}
    #view-list .v12-col-threshold{width:62px!important;text-align:right!important}
    #view-list .v12-col-expected{width:82px!important;text-align:right!important}
    #view-list .v12-col-fmv{width:58px!important;text-align:right!important}
    #view-list .v12-col-fav{width:48px!important;text-align:center!important}
    #view-list .rolebadge{font-size:6.5px!important;height:17px!important;min-height:17px!important;padding:1px 3px!important}
    #view-list .auction-signal-list{display:flex!important;justify-content:center!important;gap:2px!important;flex-wrap:nowrap!important}
    #view-list .auction-signal-badge{width:16px!important;height:16px!important;font-size:8px!important}
    @media(max-width:1200px){#view-list .v12-toolbar-row{grid-template-columns:1fr!important}#view-list .v12-toolbar-row .filters{grid-template-columns:minmax(150px,1.5fr) 110px 80px 110px 58px!important}}
  `;document.head.appendChild(style);

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',v12PatchListLayout);else v12PatchListLayout();
})();
</script>
'''
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('V12 applied')
