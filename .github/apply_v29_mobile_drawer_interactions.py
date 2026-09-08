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

# Full mobile mode is now the only phone mode. Do not gate drawers on saved mode.
block=block.replace("    if(getMode()!=='full')return;\n", "")
block=block.replace("const mode=getMode();", "const mode='full';")

# Do not close the drawer by tapping the backdrop; only the X closes it.
block=block.replace(
    "if(e.target.closest('.v23-drawer-close')||e.target.classList.contains('v23-drawer-backdrop')){closeDrawer();return;}",
    "if(e.target.closest('.v23-drawer-close')){closeDrawer();return;}"
)

# Guarantee LASCIA is physically in the same row as LIBERO + OK, regardless of older markup layers.
if 'function normalizeMobileActionRow(' not in block:
    anchor="  function syncButtons(shell){"
    helper="""  function normalizeMobileActionRow(shell){
    const freeRow=qs('.v23-free-bid',shell),leave=qs('[data-v23-proxy=\"leave\"]',shell);
    if(freeRow&&leave&&leave.parentElement!==freeRow)freeRow.appendChild(leave);
    if(leave)leave.classList.add('danger');
  }

"""
    if anchor not in block:
        raise SystemExit('syncButtons anchor not found')
    block=block.replace(anchor, helper+anchor, 1)

# Call normalization from every mobile sync.
sync_anchor="    const drawers=qs('.v23-mobile-drawers',shell);if(drawers)drawers.hidden=mode!=='full';syncButtons(shell);syncDrawerTargets();"
if sync_anchor in block:
    block=block.replace(sync_anchor, "    const drawers=qs('.v23-mobile-drawers',shell);if(drawers)drawers.hidden=false;normalizeMobileActionRow(shell);syncButtons(shell);syncDrawerTargets();", 1)
else:
    # fallback for spacing variants
    block=block.replace("syncButtons(shell);syncDrawerTargets();", "normalizeMobileActionRow(shell);syncButtons(shell);syncDrawerTargets();", 1)

# Hide/remove the compact/reduced switch. Complete mode remains active directly.
# CSS final authority is inserted before the end of the mobile runtime CSS template.
css_marker="      @media(max-width:390px){.v23-mobile-drawer-row{grid-template-columns:86px minmax(0,1fr) 78px!important;gap:6px!important}.v23-mobile-drawer-roles .rolebadge{min-width:25px!important;height:26px!important;padding:2px 5px!important;font-size:9px!important}.v23-mobile-drawer-row>button{font-size:9px!important}}"
css_extra="""
      /* V29: phone auction has only COMPLETE mode. */
      body.v23-mobile-auction .v23-header-mode{display:none!important}

      /* The drawer itself never scrolls: only its row list does. */
      .v23-mobile-drawer-panel{overflow:hidden!important;min-height:0!important;max-height:none!important;pointer-events:auto!important;z-index:2101!important}
      .v23-mobile-drawer-list{height:100%!important;min-height:0!important;max-height:100%!important;overflow-y:auto!important;overflow-x:hidden!important;-webkit-overflow-scrolling:touch!important;overscroll-behavior:contain!important;touch-action:pan-y!important;scrollbar-gutter:stable!important}
      .v23-mobile-drawer-row{flex:none!important;min-width:0!important}

      /* Backdrop is visual only: closing is exclusively through the X. */
      .v23-drawer-backdrop{pointer-events:none!important}
      .v23-mobile-drawer-search,.v23-mobile-drawer-search input,.v23-mobile-drawer-list{pointer-events:auto!important}

      /* LIBERO | OK | LASCIA always share one row. */
      .v23-free-bid{grid-template-columns:minmax(0,1fr) 72px 86px!important;align-items:stretch!important}
      .v23-free-bid [data-v23-proxy=\"leave\"]{display:block!important;grid-column:3!important;grid-row:1!important;width:100%!important;min-width:0!important;max-width:none!important;height:48px!important;min-height:48px!important;margin:0!important;padding:4px 6px!important;background:var(--danger)!important;border-color:#c4526d!important;color:#fff!important;font-size:10px!important;font-weight:900!important;border-radius:10px!important}
      .v23-free-bid [data-v23-free-ok]{grid-column:2!important;grid-row:1!important}
      .v23-free-bid label{grid-column:1!important;grid-row:1!important}
      .v23-main-actions:empty{display:none!important}
"""
if 'V29: phone auction has only COMPLETE mode.' not in block:
    if css_marker in block:
        block=block.replace(css_marker, css_marker+css_extra, 1)
    else:
        # Inject before the CSS template closes.
        needle="    }\n  `;document.head.appendChild(css);"
        if needle not in block:
            raise SystemExit('mobile CSS closing marker not found')
        block=block.replace(needle, css_extra+"    }\n  `;document.head.appendChild(css);", 1)

# Remove any existing mode switch from the DOM during sync so it cannot reserve layout width.
active_anchor="    const active=isPhone()&&isLive();shell.hidden=!active;if(headerMode)headerMode.hidden=!active;"
if active_anchor in block:
    block=block.replace(active_anchor, "    const active=isPhone()&&isLive();shell.hidden=!active;if(headerMode){headerMode.hidden=true;headerMode.remove();}", 1)

text=text[:start]+block+text[end:]
p.write_text(text,encoding='utf-8')
