from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in s
assert 'Fantacalcio Live - tool per asta online' in s

# Idempotent cleanup for reruns.
s=re.sub(r'\n<style id="v32-mobile-sort-listone-style">.*?</style>\n','\n',s,flags=re.S)
s=re.sub(r'\n<script id="v32-mobile-sort-listone-runtime">.*?</script>\n','\n',s,flags=re.S)

# Fix V30 tooltip override: V21 breakdown exposes raw/useful/playerTarget,
# while V30 was reading rawPoints/usefulPoints/roleTarget and crashed Listone.
pat=re.compile(r'''  if\(typeof strategicIndexTitle==='function'&&typeof window\.v21IndexBreakdown==='function'\)\{\n    strategicIndexTitle=function\(player\)\{.*?\n    \};\n  \}''',re.S)
rep=r'''  if(typeof strategicIndexTitle==='function'&&typeof window.v21IndexBreakdown==='function'){
    strategicIndexTitle=function(player){
      const x=window.v21IndexBreakdown(player);if(!x)return'Indice non disponibile';
      const safe=(v,f=0)=>Number.isFinite(Number(v))?Number(v):f;
      const fmt=(v,d=1)=>safe(v).toFixed(d);
      const value=Math.max(0,Math.round(safe(x.value))),mantra=(state.auction?.settings?.fantasy_mode||state.setup?.fantasy_mode||state.list?.settings?.fantasyMode)==='mantra';
      const rules=state.v9Rules||{},classicBase=rules.defense_rule_enabled?(rules.clean_sheet_bonus_enabled?73.2:73.0):(rules.clean_sheet_bonus_enabled?72.0:71.1),source=`benchmark ${classicBase.toFixed(2)}${mantra?' - 0.50 Mantra':''}`;
      const target=safe(x.playerTarget,x.keeper?safe(x.keeperTarget,5.5):safe(x.outfieldTarget,6.65)),raw=safe(x.raw,x.rawPoints),useful=safe(x.useful,x.usefulPoints);
      return `Indice ${value} cr · ${x.keeper?'POR':'MOV'} · target squadra ${fmt(x.targetAverage,2)} (${source}) · target ruolo ${fmt(target,2)} · quota teorica titolare ${fmt(x.equilibriumBudget,1)} cr = ${fmt(x.budget,0)} × ${fmt(target,2)} / ${fmt(x.targetAverage,2)} · FMV ${fmt(x.fmv,2)} × ${fmt(x.games,1)} gare = ${fmt(raw,1)} pt · peso utilizzo slot ${safe(x.slot,4)}: ${fmt(safe(x.usage)*100,0)}% → ${fmt(useful,1)} pt utili · 1 pt = ${fmt(x.creditPerPoint,3)} cr · nessun prezzo di mercato`;
    };
  }'''
s,n=pat.subn(rep,s,count=1)
if n!=1:
    raise SystemExit(f'strategicIndexTitle V30 override replacement count={n}')

style=r'''
<style id="v32-mobile-sort-listone-style">
@media(max-width:820px){
  /* Live mobile free agents: compact sort strip below role filters. */
  body.v23-free-open .v23-mobile-drawer-free-panel{
    grid-template-rows:auto auto auto auto minmax(0,1fr)!important;
  }
  .v32-mobile-sort-strip{
    min-height:34px!important;
    display:flex!important;
    align-items:center!important;
    gap:3px!important;
    padding:3px 7px!important;
    overflow-x:auto!important;
    overflow-y:hidden!important;
    -webkit-overflow-scrolling:touch!important;
    scrollbar-width:none!important;
    border-bottom:1px solid var(--line)!important;
    background:#081d34!important;
  }
  .v32-mobile-sort-strip::-webkit-scrollbar{display:none!important}
  .v32-mobile-sort-strip button{
    flex:0 0 auto!important;
    min-width:52px!important;
    height:26px!important;
    min-height:26px!important;
    padding:2px 7px!important;
    border-radius:7px!important;
    background:#143251!important;
    border:1px solid rgba(84,129,172,.48)!important;
    color:#8fa8c0!important;
    font-size:7.5px!important;
    font-weight:900!important;
    white-space:nowrap!important;
  }
  .v32-mobile-sort-strip button.active{
    background:var(--primary)!important;
    color:#fff!important;
    border-color:rgba(118,176,255,.92)!important;
  }

  /* Mobile Listone tab: don't squeeze all columns into viewport. Scroll the table instead. */
  #view-list .panel:has(.player-table),
  #view-list .table-wrap,
  #view-list .drawer-table{
    min-width:0!important;
    overflow-x:auto!important;
    overflow-y:auto!important;
    -webkit-overflow-scrolling:touch!important;
    overscroll-behavior:contain!important;
  }
  #view-list .player-table{
    width:1180px!important;
    min-width:1180px!important;
    max-width:none!important;
    table-layout:fixed!important;
  }
  #view-list .player-table th,
  #view-list .player-table td{
    white-space:nowrap!important;
    overflow:hidden!important;
    text-overflow:ellipsis!important;
  }
  #view-list .player-table th button[data-list-sort]{
    width:100%!important;
    display:flex!important;
    align-items:center!important;
    justify-content:center!important;
    gap:2px!important;
  }
}
</style>
'''

runtime=r'''
<script id="v32-mobile-sort-listone-runtime">
(()=>{
  'use strict';
  if(window.__FANTA_V32_MOBILE_SORT_LISTONE__)return;
  window.__FANTA_V32_MOBILE_SORT_LISTONE__=1;

  const qs=(s,r=document)=>r.querySelector(s);
  const phone=()=>window.matchMedia('(max-width:820px)').matches;
  const n=v=>Number.isFinite(Number(v))?Number(v):null;

  function currentSort(){
    if(!state.v32MobileFreeSort)state.v32MobileFreeSort={key:'name',dir:1};
    return state.v32MobileFreeSort;
  }
  function roleRank(p){
    const mode=state.auction?.settings?.fantasy_mode||'classic';
    const order=mode==='mantra'?['Por','B','Dc','Dd','Ds','E','M','C','W','T','A','Pc']:['P','D','C','A'];
    let roles=[];try{roles=typeof playerRoles30==='function'?playerRoles30(p):typeof playerRoles==='function'?playerRoles(p,mode):[]}catch{}
    const ranks=roles.map(r=>order.indexOf(String(r))).filter(i=>i>=0);
    return ranks.length?Math.min(...ranks):999;
  }
  function metric(p,key){
    if(key==='role')return roleRank(p);
    if(key==='name')return String(p?.name||'');
    if(key==='team')return String(p?.serie_a_team||'');
    if(key==='pfc')return n(p?.pfc)??n(p?.quotation)??-Infinity;
    if(key==='fmv'){try{const v=typeof strategicExpectedFantasyAverage==='function'?strategicExpectedFantasyAverage(p):p?.expected_fantasy_avg;return n(v)??-Infinity}catch{return -Infinity}}
    if(key==='tit'){try{const v=typeof strategicPresencePercent==='function'?strategicPresencePercent(p):p?.expected_titolarity;return n(v)??-Infinity}catch{return -Infinity}}
    return String(p?.name||'');
  }
  window.v32SortMobileFreeCandidates=function(arr){
    const s=currentSort(),dir=s.dir||1,key=s.key||'name';
    return [...(arr||[])].sort((a,b)=>{
      const av=metric(a,key),bv=metric(b,key);
      let d=0;
      if(typeof av==='number'&&typeof bv==='number')d=av-bv;
      else d=String(av).localeCompare(String(bv),'it',{sensitivity:'base',numeric:true});
      if(!d)d=String(a?.name||'').localeCompare(String(b?.name||''),'it',{sensitivity:'base'});
      return d*dir;
    });
  };

  function ensureSortStrip(){
    if(!phone()||!document.body.classList.contains('v23-free-open'))return null;
    const role=qs('[data-v31-role-strip]');
    const search=qs('.v23-mobile-drawer-free-panel .v23-mobile-drawer-search');
    const anchor=role||search;if(!anchor)return null;
    let strip=qs('[data-v32-sort-strip]');
    if(!strip){strip=document.createElement('div');strip.className='v32-mobile-sort-strip';strip.dataset.v32SortStrip='1';anchor.insertAdjacentElement('afterend',strip);}
    return strip;
  }
  function renderSortStrip(){
    const strip=ensureSortStrip();if(!strip)return;
    const s=currentSort(),fields=[['role','RUOLO'],['name','NOME'],['team','SQUADRA'],['pfc','PFC'],['fmv','FMV'],['tit','TIT']];
    strip.innerHTML=fields.map(([k,l])=>`<button type="button" data-v32-sort="${k}" class="${s.key===k?'active':''}">${l}${s.key===k?(s.dir>0?' ↑':' ↓'):' ↕'}</button>`).join('');
  }

  document.addEventListener('click',e=>{
    const b=e.target.closest?.('[data-v32-sort]');if(!b)return;
    e.preventDefault();e.stopPropagation();
    const s=currentSort(),key=b.dataset.v32Sort;
    if(s.key===key)s.dir*=-1;else{s.key=key;s.dir=(['pfc','fmv','tit'].includes(key)?-1:1);}
    renderSortStrip();
    try{if(typeof renderFree30==='function')renderFree30();else if(typeof renderMobileFreeDrawer==='function')renderMobileFreeDrawer();}catch{}
  },true);

  const obs=new MutationObserver(()=>{if(phone()&&document.body.classList.contains('v23-free-open'))requestAnimationFrame(renderSortStrip);});
  obs.observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('hashchange',()=>setTimeout(renderSortStrip,0));
  setTimeout(renderSortStrip,0);
})();
</script>
'''

# Patch V31/V30 freeCandidates30 to apply the shared mobile sort helper.
free_pat=re.compile(r'''  function freeCandidates30\(\)\{\n    const input=qs\('\[data-v23-free-search\]'\),q=String\(input\?\.value\|\|''\)\.trim\(\);\n    return \(state\.auction\?\.callCandidates\|\|\[\]\)(.*?)(?:\.sort\(\(a,b\)=>String\(a\.name\|\|'\'\)\.localeCompare\(String\(b\.name\|\|'\'\),'it'\)\))\.slice\(0,120\);\n  \}''',re.S)
m=free_pat.search(s)
if not m:
    raise SystemExit('freeCandidates30 canonical block not found')
filters=m.group(1)
free_rep="""  function freeCandidates30(){
    const input=qs('[data-v23-free-search]'),q=String(input?.value||'').trim();
    const rows=(state.auction?.callCandidates||[])"""+filters+""";
    const sorted=typeof window.v32SortMobileFreeCandidates==='function'?window.v32SortMobileFreeCandidates(rows):rows.sort((a,b)=>String(a.name||'').localeCompare(String(b.name||''),'it'));
    return sorted.slice(0,120);
  }"""
s=free_pat.sub(free_rep,s,count=1)

# Render the sort strip whenever the drawer list rerenders.
s=s.replace('    renderRoleStrip31();\n    const queued=', '    renderRoleStrip31();\n    if(typeof renderSortStrip32===\'function\')renderSortStrip32();\n    const queued=',1) if 'function renderSortStrip32' in s else s

# Because the V32 runtime is appended after the V30 IIFE, expose a tiny hook the existing
# renderFree30 can call without needing access to scoped functions.
# Insert a global bridge just before runtime close if possible by replacing renderFree30 start.
s=s.replace("  function renderFree30(){\n    const host=qs('[data-v23-free-list]');if(!host||!document.body.classList.contains('v23-free-open'))return;\n    renderRoleStrip31();",
            "  function renderFree30(){\n    const host=qs('[data-v23-free-list]');if(!host||!document.body.classList.contains('v23-free-open'))return;\n    renderRoleStrip31();\n    if(typeof window.v32RenderMobileSortStrip==='function')window.v32RenderMobileSortStrip();",1)

# Expose render strip from the V32 runtime itself.
runtime=runtime.replace("  function renderSortStrip(){", "  function renderSortStrip(){")
runtime=runtime.replace("  document.addEventListener('click',e=>{", "  window.v32RenderMobileSortStrip=renderSortStrip;\n\n  document.addEventListener('click',e=>{")

if '</head>' not in s or '</body>' not in s:
    raise SystemExit('HTML closing markers missing')
s=s.replace('</head>',style+'\n</head>',1)
s=s.replace('</body>',runtime+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('V32 applied')
