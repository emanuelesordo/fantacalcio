from pathlib import Path
import re
p=Path('home.html')
t=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in t
assert 'Fantacalcio Live - tool per asta online' in t

# Manual mode must disable timers/autoplay, not the queue itself.
t=t.replace("    const exactSelectors=['.v30-mobile-queue','.auction-queue-card','.auction-call-queue','[data-auction-queue]'];",
            "    const exactSelectors=[]; // V34: queue stays usable in manual mode")
t=t.replace("button.textContent=enabled?'MANUALE · NO TIMER/CODA':'AUTO · CODA+TIMER';",
            "button.textContent=enabled?'MANUALE · NO TIMER':'AUTO · CODA+TIMER';")
t=t.replace("status.textContent='MANUALE · timer e coda disattivati · aggiudica e passa turno dal banditore';",
            "status.textContent='MANUALE · timer disattivati · coda a chiamata manuale';")
t=t.replace("msg(wanted?'Modalità manuale: coda e timer disattivati.':'Modalità automatica: coda e timer ripristinati.','success');",
            "msg(wanted?'Modalità manuale: timer disattivati, coda disponibile con chiamata manuale.':'Modalità automatica: coda e timer ripristinati.','success');")

# Remove the old V33 queue-hiding CSS and the shell row removal.
t=re.sub(r'/\* Manual live mode: queue and countdown timers disappear; controls remain manual\. \*/\n#view-auction\.v33-manual-flow \.v30-mobile-queue,\n#view-auction\.v33-manual-flow \.auction-queue-card,\n#view-auction\.v33-manual-flow \.auction-call-queue,\n#view-auction\.v33-manual-flow \[data-auction-queue\],\n#view-auction\.v33-manual-flow \.v33-manual-hidden\{\n  display:none!important;\n\}\n','/* V34: manual mode keeps the queue visible; timer controls alone are disabled by runtime. */\n',t)
t=t.replace("  #view-list .player-table th,#view-list .player-table td{padding-left:4px!important;padding-right:4px!important}\n\n  /* Manual mode also removes the mobile queue row from the shell. */\n  body.v23-mobile-auction #view-auction.v33-manual-flow .v23-mobile-shell{\n    grid-template-rows:auto auto minmax(0,1fr) auto!important;\n  }",
            "  #view-list .player-table th,#view-list .player-table td{padding-left:4px!important;padding-right:4px!important}")

# Existing desktop queue already has a green manual-call button: make it available in manual flow even if autoplay is not paused.
t=t.replace("      const manualCallAvailable =\n        autoPaused\n        && auctionOwnCallTurn()\n        && !auctionSession()?.current_player_id;",
            "      const manualFlowQueue = auctionSession()?.setup_snapshot?.manual_auction_flow === true;\n\n      const manualCallAvailable =\n        (autoPaused || manualFlowQueue)\n        && auctionOwnCallTurn()\n        && !auctionSession()?.current_player_id;")
t=t.replace("                                : autoPaused\n                                  ? `\n                                      <button\n                                        type=\"button\"\n                                        class=\"auction-queue-call\"",
            "                                : (autoPaused || manualFlowQueue)\n                                  ? `\n                                      <button\n                                        type=\"button\"\n                                        class=\"auction-queue-call\"")
t=t.replace("title=\"${manualCallAvailable ? 'Chiama questo giocatore adesso' : 'Disponibile al tuo turno quando la coda è in pausa'}\"",
            "title=\"${manualCallAvailable ? 'Chiama questo giocatore adesso' : 'Disponibile al tuo turno'}\"")

# Reclaim the old top-banner padding; keep only the small floating back control.
marker='<style id="v34b-manual-queue-cleanup-style">'
t=re.sub(r'\n<style id="v34b-manual-queue-cleanup-style">.*?</style>\n','\n',t,flags=re.S)
extra='''\n<style id="v34b-manual-queue-cleanup-style">\nbody.auction-live .auction-root{padding-top:0!important}\n#view-auction.v33-manual-flow .v33-manual-status{display:none!important}\n#view-auction.v33-manual-flow .v30-mobile-queue,\n#view-auction.v33-manual-flow .auction-queue-card,\n#view-auction.v33-manual-flow .auction-call-queue,\n#view-auction.v33-manual-flow [data-auction-queue]{display:grid!important}\n@media(max-width:820px){body.v23-mobile-auction #view-auction.v33-manual-flow .v23-mobile-shell{grid-template-rows:auto auto auto minmax(0,1fr) auto!important}}\n</style>\n'''
t=t.replace('</head>',extra+'\n</head>',1)
assert 'manualFlowQueue' in t
assert '<title>Fantacalcio Live</title>' in t
p.write_text(t,encoding='utf-8')
print('V34b manual queue cleanup applied')
