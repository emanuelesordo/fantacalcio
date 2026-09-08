from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

start=text.find('<script id="v23-mobile-auction-mode-runtime">')
end=text.find('</script>', start)
if start < 0 or end < 0:
    raise SystemExit('mobile auction runtime not found')
block=text[start:end]

# Add role-family color helpers once.
anchor="  function mobileEsc(v){try{return typeof esc==='function'?esc(v):String(v??'')}catch{return String(v??'')}}\n"
helper="""  function mobileEsc(v){try{return typeof esc==='function'?esc(v):String(v??'')}catch{return String(v??'')}}\n  function mobileRoleTone(role){\n    const r=String(role||'').trim().toLowerCase();\n    if(['p','por'].includes(r))return 'por';\n    if(['d','b','dc','dd','ds'].includes(r))return 'def';\n    if(['e','m','c'].includes(r))return 'mid';\n    if(['w','t'].includes(r))return 'wing';\n    if(['a','pc'].includes(r))return 'att';\n    return 'other';\n  }\n  function mobileRoleBadges(rr){\n    return (rr||[]).map(r=>`<i class=\"rolebadge v23-role-${mobileRoleTone(r)}\">${mobileEsc(r)}</i>`).join('');\n  }\n"""
if 'function mobileRoleTone(' not in block:
    if anchor not in block: raise SystemExit('mobileEsc anchor missing')
    block=block.replace(anchor, helper, 1)

# Rebuild mobile roster and free-agent rows with separate role / identity / action columns.
block=re.sub(
    r"  function renderMobileRosterDrawer\(\)\{.*?\n  \}\n  function renderMobileFreeDrawer\(\)\{.*?\n  \}",
    """  function renderMobileRosterDrawer(){
    const host=qs('[data-v23-roster-list]');if(!host)return;
    const rows=myInfo()?.assignments||[];
    host.innerHTML=rows.map(a=>{
      const p=mobileAssignmentPlayer(a),rr=roles(p),price=a?.purchase_price??a?.price??a?.amount??'—';
      return `<div class=\"v23-mobile-drawer-row v23-mobile-roster-row\"><div class=\"v23-mobile-drawer-roles\">${mobileRoleBadges(rr)}</div><div class=\"v23-mobile-drawer-player\"><strong>${mobileEsc(p?.name||a?.player_name||'Giocatore')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div><div class=\"v23-mobile-drawer-price\">${mobileEsc(price)} cr</div></div>`;
    }).join('')||'<div class=\"v23-mobile-empty\">Rosa vuota.</div>';
  }
  function renderMobileFreeDrawer(){
    const host=qs('[data-v23-free-list]');if(!host)return;
    const q=qs('[data-v23-free-search]')?.value||'';const can=mobileCanCall();
    host.innerHTML=mobileFreeCandidates(q).map(p=>`<div class=\"v23-mobile-drawer-row v23-mobile-free-row\"><div class=\"v23-mobile-drawer-roles\">${mobileRoleBadges(roles(p))}</div><div class=\"v23-mobile-drawer-player\"><strong>${mobileEsc(p?.name||'—')}</strong><small>${mobileEsc(p?.serie_a_team||'—')}</small></div><button type=\"button\" data-v23-mobile-call=\"${mobileEsc(p.id)}\" ${can?'':'disabled'}>CHIAMA</button></div>`).join('')||'<div class=\"v23-mobile-empty\">Nessun giocatore disponibile.</div>';
  }""",
    block,
    count=1,
    flags=re.S,
)

# Tighten drawer rows and apply the same role palette used by the Mantra visual language.
old_css=re.compile(r"      \.v23-mobile-drawer-row\{.*?\.v23-mobile-empty\{padding:16px!important;text-align:center!important;color:var\(--soft\)!important\}", re.S)
new_css="""      .v23-mobile-drawer-row{min-height:58px!important;display:grid!important;grid-template-columns:98px minmax(0,1fr) 88px!important;gap:8px!important;align-items:center!important;padding:5px 7px!important;border:1px solid var(--line)!important;border-radius:8px!important;background:var(--panel2)!important}
      .v23-mobile-drawer-roles{min-width:0!important;display:flex!important;align-items:center!important;align-content:center!important;justify-content:flex-start!important;gap:3px!important;flex-wrap:wrap!important}
      .v23-mobile-drawer-roles .rolebadge{min-width:28px!important;height:28px!important;padding:2px 7px!important;border-radius:7px!important;font-style:normal!important;font-size:10px!important;font-weight:950!important;line-height:1!important;border:1px solid rgba(255,255,255,.22)!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.12)!important}
      .v23-mobile-drawer-roles .v23-role-por{background:#f4b629!important;color:#152238!important}
      .v23-mobile-drawer-roles .v23-role-def{background:#4f9d2f!important;color:#fff!important}
      .v23-mobile-drawer-roles .v23-role-mid{background:#2f73d5!important;color:#fff!important}
      .v23-mobile-drawer-roles .v23-role-wing{background:#b018b8!important;color:#fff!important}
      .v23-mobile-drawer-roles .v23-role-att{background:#c82f45!important;color:#fff!important}
      .v23-mobile-drawer-roles .v23-role-other{background:#486786!important;color:#fff!important}
      .v23-mobile-drawer-player{min-width:0!important;min-height:48px!important;display:flex!important;flex-direction:column!important;justify-content:center!important;align-items:flex-start!important;text-align:left!important}
      .v23-mobile-drawer-player strong{display:block!important;width:100%!important;font-size:12px!important;line-height:1.1!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
      .v23-mobile-drawer-player small{display:block!important;width:100%!important;margin-top:4px!important;color:var(--soft)!important;font-size:9px!important;line-height:1.05!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
      .v23-mobile-drawer-row>button{align-self:center!important;justify-self:stretch!important;width:100%!important;min-width:0!important;height:42px!important;min-height:42px!important;max-height:42px!important;padding:4px 6px!important;border-radius:10px!important;font-size:10px!important;line-height:1!important}
      .v23-mobile-drawer-price{align-self:center!important;justify-self:end!important;min-width:0!important;color:var(--text)!important;font-size:11px!important;font-weight:900!important;white-space:nowrap!important;text-align:right!important}
      .v23-mobile-empty{padding:16px!important;text-align:center!important;color:var(--soft)!important}
      @media(max-width:390px){.v23-mobile-drawer-row{grid-template-columns:86px minmax(0,1fr) 78px!important;gap:6px!important}.v23-mobile-drawer-roles .rolebadge{min-width:25px!important;height:26px!important;padding:2px 5px!important;font-size:9px!important}.v23-mobile-drawer-row>button{font-size:9px!important}}"""
if not old_css.search(block):
    raise SystemExit('drawer row CSS block not found')
block=old_css.sub(new_css, block, count=1)

text=text[:start]+block+text[end:]
p.write_text(text,encoding='utf-8')
