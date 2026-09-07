from pathlib import Path
import re

p=Path('home.html')
text=p.read_text(encoding='utf-8')
assert '<title>Fantacalcio Live</title>' in text
assert 'Fantacalcio Live - tool per asta online' in text

text=re.sub(r'\n<style id="v26-home-tv-style">.*?</style>\n','\n',text,flags=re.S)

style=r'''
<style id="v26-home-tv-style">
/* V26 · Home: cards must never escape the cockpit. */
#view-home{
  height:100%!important;
  min-height:0!important;
  overflow:hidden!important;
}
#view-home .home-layout{
  height:100%!important;
  min-height:0!important;
  overflow:hidden!important;
}
#view-home .home-col{
  min-height:0!important;
  max-height:100%!important;
  overflow:hidden!important;
}
#view-home .home-col > .panel,
#view-home .home-col > section,
#view-home .home-col > article{
  min-height:0!important;
  max-height:100%!important;
  overflow:auto!important;
  overscroll-behavior:contain;
  scrollbar-gutter:stable;
}
#view-home .inner-scroll{
  min-height:0!important;
  overflow:auto!important;
  overscroll-behavior:contain;
}

/* V26 · Presenter / TV view. */
#view-tv{
  height:100%!important;
  min-height:0!important;
  overflow:hidden!important;
}
#view-tv .tv-shell{
  height:100%!important;
  min-height:0!important;
  display:grid!important;
  grid-template-rows:auto minmax(0,1fr)!important;
  gap:8px!important;
}
#view-tv .tv-call-strip{
  min-height:108px;
  padding:12px 14px!important;
  display:grid!important;
  grid-template-columns:minmax(260px,2.2fr) repeat(5,minmax(92px,.72fr)) auto;
  align-items:stretch;
  gap:8px;
  overflow:hidden;
}
#view-tv .tv-call-main,
#view-tv .tv-call-stat,
#view-tv .tv-call-actions{
  min-width:0;
  border:1px solid rgba(109,167,255,.16);
  border-radius:14px;
  background:rgba(255,255,255,.035);
}
#view-tv .tv-call-main{
  padding:10px 14px;
  display:flex;
  flex-direction:column;
  justify-content:center;
}
#view-tv .tv-call-main h1{
  margin:3px 0 0;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  font-size:clamp(28px,3.4vw,54px);
  line-height:.98;
}
#view-tv .tv-call-label,
#view-tv .tv-call-stat span{
  color:var(--muted);
  font-size:9px;
  font-weight:900;
  letter-spacing:.08em;
  text-transform:uppercase;
}
#view-tv .tv-call-stat{
  padding:9px 10px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  text-align:center;
}
#view-tv .tv-call-stat strong{
  display:block;
  width:100%;
  margin-top:5px;
  overflow:hidden;
  text-overflow:ellipsis;
  white-space:nowrap;
  color:var(--text);
  font-size:clamp(17px,1.65vw,28px);
  font-weight:900;
}
#view-tv #tv-bid{
  color:#82f0c5!important;
  font-size:clamp(26px,2.4vw,42px)!important;
}
#view-tv #tv-timer{
  margin:5px 0 0!important;
  font-size:clamp(24px,2.4vw,42px)!important;
  font-weight:950!important;
}
#view-tv .tv-call-actions{
  padding:8px;
  display:grid;
  align-content:center;
  gap:6px;
}
#view-tv .tv-call-actions button{white-space:nowrap}

#view-tv .tv-rosters-stage{
  min-height:0!important;
  height:100%!important;
  overflow:hidden!important;
  padding:8px!important;
}
#view-tv .tv-rosters-grid{
  --tv-roster-cols:5;
  height:100%!important;
  min-height:0!important;
  display:grid!important;
  grid-template-columns:repeat(var(--tv-roster-cols),minmax(0,1fr))!important;
  grid-auto-rows:minmax(0,1fr)!important;
  gap:6px!important;
  overflow:hidden!important;
}
#view-tv .tv-rosters-grid details.team-card{
  height:100%!important;
  min-height:0!important;
  max-height:100%!important;
  display:grid!important;
  grid-template-rows:auto minmax(0,1fr)!important;
  overflow:hidden!important;
  border-radius:12px!important;
}
#view-tv .tv-rosters-grid details.team-card > summary{
  min-height:0!important;
  padding:5px 7px!important;
  pointer-events:none;
}
#view-tv .tv-rosters-grid .roster-body{
  min-height:0!important;
  height:100%!important;
  overflow:hidden!important;
  padding:3px!important;
  display:grid!important;
  grid-template-rows:repeat(var(--tv-player-count,1),minmax(0,1fr))!important;
  gap:2px!important;
}
#view-tv .tv-rosters-grid .roster-player{
  min-height:0!important;
  height:auto!important;
  padding:1px 4px!important;
  align-items:center!important;
  overflow:hidden!important;
  font-size:clamp(6px,.58vw,9px)!important;
}
#view-tv .tv-rosters-grid .roster-player strong,
#view-tv .tv-rosters-grid .roster-player small{
  overflow:hidden!important;
  text-overflow:ellipsis!important;
  white-space:nowrap!important;
}
#view-tv .tv-rosters-grid button,
#view-tv .tv-rosters-grid input,
#view-tv .tv-rosters-grid select,
#view-tv .tv-rosters-grid textarea{
  display:none!important;
}

@media(max-width:1100px){
  #view-tv .tv-call-strip{
    grid-template-columns:minmax(220px,1.7fr) repeat(3,minmax(86px,.7fr));
  }
  #view-tv .tv-call-actions{grid-column:auto}
}
</style>
'''

text=text.replace('</head>',style+'\n</head>',1)

new_tv='''      <!-- TV -->
      <section id="view-tv" class="view no-page-scroll">
        <div class="tv-shell">
          <section class="panel tv-call-strip" aria-label="Chiamata corrente">
            <div class="tv-call-main">
              <span class="tv-call-label">Giocatore chiamato</span>
              <h1 id="tv-player-name">In attesa</h1>
            </div>
            <div class="tv-call-stat"><span>Ruolo</span><strong id="tv-player-role">—</strong></div>
            <div class="tv-call-stat"><span>Squadra</span><strong id="tv-player-team">—</strong></div>
            <div class="tv-call-stat"><span>Offerta più alta</span><strong id="tv-bid">—</strong></div>
            <div class="tv-call-stat"><span>Miglior offerente</span><strong id="tv-leader">—</strong></div>
            <div class="tv-call-stat"><span>Timer</span><strong id="tv-timer">—</strong></div>
            <div class="tv-call-actions">
              <span id="tv-status-badge" class="badge"></span>
              <button id="tv-fullscreen" class="secondary" type="button">Schermo intero</button>
            </div>
          </section>
          <section class="panel tv-rosters-stage" aria-label="Panoramica rose">
            <div id="tv-rosters-grid" class="tv-rosters-grid"></div>
          </section>
        </div>
      </section>

    </main>'''
pattern=r'      <!-- TV -->\s*<section id="view-tv" class="view no-page-scroll">.*?</section>\s*\n\s*</main>'
text,n=re.subn(pattern,new_tv,text,count=1,flags=re.S)
if n!=1:
    raise RuntimeError(f'TV markup replacement count={n}')

new_render=r'''    let tvRostersLoadingV26 = false;

    async function renderTvRostersV26(){
      const target = $('tv-rosters-grid');
      if (!target) return;

      if (!state.rosters) {
        if (tvRostersLoadingV26) return;
        tvRostersLoadingV26 = true;
        try {
          await loadRosters();
        } catch (_) {
          return;
        } finally {
          tvRostersLoadingV26 = false;
        }
      }

      if (!state.rosters) return;
      renderRosters();
      const source = $('rosters-grid');
      if (!source) return;

      target.innerHTML = source.innerHTML;
      const cards = [...target.querySelectorAll('details.team-card')];
      cards.forEach(card => {
        card.open = true;
        const body = card.querySelector('.roster-body');
        const count = Math.max(1, body?.children?.length || 1);
        card.style.setProperty('--tv-player-count', String(count));
      });

      const count = cards.length;
      const cols = count <= 6
        ? Math.max(1, count)
        : Math.min(6, Math.ceil(count / 2));
      target.style.setProperty('--tv-roster-cols', String(cols));
    }

    function renderTv(){
      const d=state.auction;if(!d)return;
      const s=d.auctionSession,p=d.currentPlayer;
      const status=$('tv-status-badge');
      const name=$('tv-player-name');
      const role=$('tv-player-role');
      const team=$('tv-player-team');
      const bid=$('tv-bid');
      const leader=$('tv-leader');
      if(status) status.textContent=s?.status||'NESSUNA ASTA';
      if(name) name.textContent=p?.name||'In attesa';
      if(role) role.textContent=p?playerRoles(p,d.settings?.fantasy_mode).join('/'):'—';
      if(team) team.textContent=p?.serie_a_team||'—';
      if(bid) bid.textContent=s?.current_bid||'—';
      if(leader) leader.textContent=d.currentBidderTeam
        ? auctionTeamReference(d.currentBidderTeam, d.currentBidderTeam?.name || 'Squadra')
        : 'Nessuno';
      renderTvTimer();
      void renderTvRostersV26();
    }

    function renderTvTimer(){'''
pattern2=r'    function renderTv\(\)\{.*?\n    \}\n\n    function renderTvTimer\(\)\{'
text,n2=re.subn(pattern2,new_render,text,count=1,flags=re.S)
if n2!=1:
    raise RuntimeError(f'renderTv replacement count={n2}')

p.write_text(text,encoding='utf-8')
