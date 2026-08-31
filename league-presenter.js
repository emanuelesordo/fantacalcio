/* =========================================================
   league-presenter.js
   Vista Presentatore / TV - sola lettura
   ========================================================= */

const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const PRESENTER_API_URL =
  `${SUPABASE_URL}/functions/v1/presenter-api`;


let selectedLeague =
  null;

let presenterData =
  null;

let serverOffsetMs =
  0;

let refreshBusy =
  false;


/* =========================================================
   DOM
   ========================================================= */

const tvMessage =
  document.getElementById(
    'tv-message'
  );

const tvLeagueTitle =
  document.getElementById(
    'tv-league-title'
  );

const tvLeagueSubtitle =
  document.getElementById(
    'tv-league-subtitle'
  );

const tvFullscreenButton =
  document.getElementById(
    'tv-fullscreen-button'
  );

const tvLayoutSettings =
  document.getElementById(
    'tv-layout-settings'
  );

const tvLayoutMode =
  document.getElementById(
    'tv-layout-mode'
  );

const tvShowTeams =
  document.getElementById(
    'tv-show-teams'
  );

const tvShowBids =
  document.getElementById(
    'tv-show-bids'
  );

const tvSaveLayout =
  document.getElementById(
    'tv-save-layout'
  );

const tvStatusTitle =
  document.getElementById(
    'tv-status-title'
  );

const tvStatusSubtitle =
  document.getElementById(
    'tv-status-subtitle'
  );

const tvSessionBadge =
  document.getElementById(
    'tv-session-badge'
  );

const tvTurnBadge =
  document.getElementById(
    'tv-turn-badge'
  );

const tvTestBadge =
  document.getElementById(
    'tv-test-badge'
  );

const tvPlayerSection =
  document.getElementById(
    'tv-player-section'
  );

const tvPlayerName =
  document.getElementById(
    'tv-player-name'
  );

const tvPlayerMeta =
  document.getElementById(
    'tv-player-meta'
  );

const tvCurrentBid =
  document.getElementById(
    'tv-current-bid'
  );

const tvCurrentLeader =
  document.getElementById(
    'tv-current-leader'
  );

const tvTimer =
  document.getElementById(
    'tv-timer'
  );

const tvTimerStatus =
  document.getElementById(
    'tv-timer-status'
  );

const tvTeamsSection =
  document.getElementById(
    'tv-teams-section'
  );

const tvTeamsList =
  document.getElementById(
    'tv-teams-list'
  );

const tvBidsSection =
  document.getElementById(
    'tv-bids-section'
  );

const tvBidsList =
  document.getElementById(
    'tv-bids-list'
  );


/* =========================================================
   STORAGE / UTILITY
   ========================================================= */

function getSession() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_session'
      );


    return raw
      ? JSON.parse(raw)
      : null;

  } catch {

    return null;
  }
}


function getSelectedLeague() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_selected_league'
      );


    return raw
      ? JSON.parse(raw)
      : null;

  } catch {

    return null;
  }
}


function escapeHtml(value) {

  return String(
    value ?? ''
  )
    .replaceAll(
      '&',
      '&amp;'
    )
    .replaceAll(
      '<',
      '&lt;'
    )
    .replaceAll(
      '>',
      '&gt;'
    )
    .replaceAll(
      '"',
      '&quot;'
    )
    .replaceAll(
      "'",
      '&#039;'
    );
}


function showTvMessage(
  text = '',
  type = ''
) {

  if (!tvMessage) {
    return;
  }


  tvMessage.textContent =
    text;


  tvMessage.className =
    `message ${type}`;
}


function playerRoles(player) {

  if (!player) {
    return [];
  }


  const mantra =
    Array.isArray(
      player.mantra_roles
    )
      ? player.mantra_roles
          .filter(Boolean)
      : [];


  if (mantra.length) {
    return mantra;
  }


  return player.classic_role
    ? [
        player.classic_role
      ]
    : [];
}


function sessionLabel(status) {

  return ({
    prepared:
      'PREPARATA',

    live:
      'LIVE',

    paused:
      'PAUSA',

    review:
      'REVIEW',

    completed:
      'COMPLETATA'
  })[status]
  || 'IN ATTESA';
}


/* =========================================================
   API
   ========================================================= */

async function presenterApi(body) {

  const session =
    getSession();


  if (!session?.token) {

    window.location.href =
      'index.html';

    return null;
  }


  if (!selectedLeague?.id) {

    window.location.href =
      'leagues.html';

    return null;
  }


  let response;


  try {

    response =
      await fetch(
        PRESENTER_API_URL,
        {
          method:
            'POST',

          headers: {
            'Content-Type':
              'application/json'
          },

          body:
            JSON.stringify({
              ...body,

              leagueId:
                selectedLeague.id,

              sessionToken:
                session.token
            })
        }
      );

  } catch {

    throw new Error(
      'Impossibile contattare il server Presentatore.'
    );
  }


  let data;


  try {

    data =
      await response.json();

  } catch {

    throw new Error(
      'Risposta non valida dal server Presentatore.'
    );
  }


  if (
    response.status === 401
  ) {

    window.location.href =
      'index.html';

    return null;
  }


  return data;
}


/* =========================================================
   SERVER CLOCK
   ========================================================= */

function updateServerOffset() {

  const serverNow =
    Date.parse(
      presenterData
        ?.serverNow
      || ''
    );


  if (
    Number.isFinite(
      serverNow
    )
  ) {

    serverOffsetMs =
      serverNow
      -
      Date.now();
  }
}


function nowMs() {

  return Date.now()
    +
    serverOffsetMs;
}


function remainingTimerMs() {

  const session =
    presenterData
      ?.auctionSession;


  if (!session) {
    return null;
  }


  if (
    session.hold_active
    === true
  ) {

    const seconds =
      Number(
        session
          .hold_remaining_seconds
      );


    return Number.isFinite(
      seconds
    )
      ? Math.max(
          0,
          seconds * 1000
        )
      : null;
  }


  if (
    !session.timer_deadline
  ) {

    return null;
  }


  const deadline =
    Date.parse(
      session.timer_deadline
    );


  if (
    !Number.isFinite(
      deadline
    )
  ) {

    return null;
  }


  return Math.max(
    0,
    deadline
    -
    nowMs()
  );
}


function renderTimer() {

  if (
    !tvTimer
    ||
    !tvTimerStatus
  ) {

    return;
  }


  const session =
    presenterData
      ?.auctionSession;


  if (
    !session
    ||
    session.status
    !== 'live'
  ) {

    tvTimer.textContent =
      '—';


    tvTimerStatus.textContent =
      'In attesa';


    return;
  }


  if (
    session.hold_active
    === true
  ) {

    const remaining =
      remainingTimerMs();


    tvTimer.textContent =
      remaining === null
        ? '—'
        : `${
            Math.ceil(
              remaining / 1000
            )
          }s`;


    tvTimerStatus.textContent =
      'HOLD';


    return;
  }


  if (
    session.timer_expired_at
  ) {

    tvTimer.textContent =
      '0s';


    tvTimerStatus.textContent =
      'ATTESA BANDITORE';


    return;
  }


  const remaining =
    remainingTimerMs();


  if (remaining === null) {

    tvTimer.textContent =
      '—';


    tvTimerStatus.textContent =
      session.current_bidder_team_id
        ? 'Timer non avviato'
        : 'Prima offerta';


    return;
  }


  tvTimer.textContent =
    `${
      Math.max(
        0,
        Math.ceil(
          remaining / 1000
        )
      )
    }s`;


  tvTimerStatus.textContent =
    'Tempo residuo';
}


/* =========================================================
   LAYOUT
   ========================================================= */

function applyLayout() {

  const settings =
    presenterData
      ?.tvSettings
    || {};


  const mode =
    settings.layout_mode
    || 'standard';


  tvTeamsSection.hidden =
    settings.show_team_table
    === false;


  tvBidsSection.hidden =
    settings.show_recent_bids
    === false;


  /*
   * Manteniamo un solo style.css.
   * I layout cambiano la quantità di informazioni visibili.
   */
  if (
    mode === 'focus'
  ) {

    tvTeamsSection.hidden =
      true;


    tvBidsSection.hidden =
      true;


  } else if (
    mode === 'compact'
  ) {

    tvBidsSection.hidden =
      true;
  }


  if (
    tvLayoutMode
  ) {

    tvLayoutMode.value =
      mode;
  }


  if (
    tvShowTeams
  ) {

    tvShowTeams.checked =
      settings.show_team_table
      !== false;
  }


  if (
    tvShowBids
  ) {

    tvShowBids.checked =
      settings.show_recent_bids
      !== false;
  }
}


/* =========================================================
   RENDER
   ========================================================= */

function renderHeader() {

  const league =
    presenterData
      ?.league;


  tvLeagueTitle.textContent =
    league
      ? `TV · ${league.name}`
      : 'TV Asta';


  tvLeagueSubtitle.textContent =
    presenterData
      ?.auctionSession
      ? 'Vista Presentatore'
      : 'In attesa di una sessione';
}


function renderStatus() {

  const session =
    presenterData
      ?.auctionSession;


  if (!session) {

    tvStatusTitle.textContent =
      'In attesa';


    tvStatusSubtitle.textContent =
      'Nessuna sessione attiva';


    tvSessionBadge.textContent =
      'IN ATTESA';


    tvSessionBadge.className =
      'badge';


    tvTurnBadge.hidden =
      true;


    tvTestBadge.hidden =
      true;


    return;
  }


  tvStatusTitle.textContent =
    session.status === 'live'
      ? 'Asta in corso'
      : session.status === 'prepared'
        ? 'Asta preparata'
        : session.status === 'review'
          ? 'Riepilogo test'
          : 'Sessione';


  tvStatusSubtitle.textContent =
    session.is_test
      ? 'Sessione temporanea'
      : 'Sessione ufficiale';


  tvSessionBadge.textContent =
    sessionLabel(
      session.status
    );


  tvSessionBadge.className =
    session.status === 'live'
      ? 'badge good'
      : 'badge';


  tvTestBadge.hidden =
    session.is_test
    !== true;


  const turn =
    presenterData
      ?.currentTurnTeam;


  const nomination =
    presenterData
      ?.currentNominationTeam;


  const turnText =
    turn
      ? `Turno: ${turn.name}`
      : nomination
        ? `Chiamata: ${nomination.name}`
        : '';


  tvTurnBadge.hidden =
    !turnText;


  tvTurnBadge.textContent =
    turnText;
}


function renderPlayer() {

  const player =
    presenterData
      ?.currentPlayer;


  const session =
    presenterData
      ?.auctionSession;


  if (
    !session
    ||
    session.status
    !== 'live'
  ) {

    tvPlayerName.textContent =
      '—';


    tvPlayerMeta.textContent =
      'In attesa';


    tvCurrentBid.textContent =
      '—';


    tvCurrentLeader.textContent =
      '—';


    return;
  }


  if (!player) {

    tvPlayerName.textContent =
      'Prossima chiamata';


    tvPlayerMeta.textContent =
      presenterData
        ?.currentNominationTeam
        ? `Turno di ${
            presenterData
              .currentNominationTeam
              .name
          }`
        : 'In attesa';


    tvCurrentBid.textContent =
      '—';


    tvCurrentLeader.textContent =
      '—';


    return;
  }


  tvPlayerName.textContent =
    player.name
    || 'Giocatore';


  const roles =
    playerRoles(
      player
    )
      .join('/');


  tvPlayerMeta.textContent =
    [
      roles,
      player.serie_a_team,
      player.quotation !== null
      &&
      player.quotation !== undefined
        ? `Q. ${player.quotation}`
        : null
    ]
      .filter(Boolean)
      .join(' · ');


  tvCurrentBid.textContent =
    session.current_bid
    ?? '—';


  tvCurrentLeader.textContent =
    presenterData
      ?.currentBidderTeam
      ?.name
    || 'Nessuno';
}


function renderTeams() {

  const teams =
    presenterData
      ?.teams
    || [];


  if (!teams.length) {

    tvTeamsList.innerHTML = `
      <div class="empty-state">
        Nessuna squadra disponibile.
      </div>
    `;

    return;
  }


  tvTeamsList.innerHTML =
    teams
      .map(
        team => `

          <div class="setting-row">

            <span>

              <strong>
                ${escapeHtml(
                  team.name
                )}
              </strong>

              <small>
                ${escapeHtml(
                  team.playerCount
                )} giocatori
                · spesi
                ${escapeHtml(
                  team.spent
                )}
              </small>

            </span>


            <strong>
              ${escapeHtml(
                team.remaining
              )}
            </strong>

          </div>

        `
      )
      .join('');
}


function renderBids() {

  const bids =
    presenterData
      ?.recentBids
    || [];


  if (!bids.length) {

    tvBidsList.innerHTML = `
      <div class="empty-state">
        Nessuna offerta registrata.
      </div>
    `;

    return;
  }


  tvBidsList.innerHTML =
    bids
      .map(
        bid => `

          <div class="setting-row">

            <span>

              <strong>
                ${escapeHtml(
                  bid.teamName
                )}
              </strong>

              <small>
                ${escapeHtml(
                  bid.source
                  || 'APP'
                )}
              </small>

            </span>


            <strong>
              ${escapeHtml(
                bid.amount
              )}
            </strong>

          </div>

        `
      )
      .join('');
}


function renderPermissions() {

  const canEdit =
    presenterData
      ?.permissions
      ?.canEditLayout
    === true;


  tvLayoutSettings.hidden =
    !canEdit;
}


function renderAll() {

  if (!presenterData) {
    return;
  }


  updateServerOffset();

  renderHeader();

  renderStatus();

  renderPlayer();

  renderTeams();

  renderBids();

  renderPermissions();

  applyLayout();

  renderTimer();
}


/* =========================================================
   LOAD / POLL
   ========================================================= */

async function loadPresenterState(
  silent = false
) {

  if (refreshBusy) {
    return;
  }


  refreshBusy =
    true;


  if (!silent) {
    showTvMessage('');
  }


  try {

    const data =
      await presenterApi({
        action:
          'getState'
      });


    if (!data?.ok) {

      throw new Error(
        data?.error
        ||
        'Impossibile caricare la vista TV.'
      );
    }


    presenterData =
      data;


    renderAll();


  } catch (error) {

    console.error(
      error
    );


    if (!silent) {

      showTvMessage(
        error.message
        ||
        'Errore vista Presentatore.',
        'error'
      );
    }


  } finally {

    refreshBusy =
      false;
  }
}


/* =========================================================
   SALVA LAYOUT
   ========================================================= */

tvSaveLayout
  ?.addEventListener(
    'click',
    async () => {

      tvSaveLayout.disabled =
        true;


      const oldText =
        tvSaveLayout.textContent;


      tvSaveLayout.textContent =
        'Salvataggio...';


      try {

        const result =
          await presenterApi({

            action:
              'updateLayout',

            layoutMode:
              tvLayoutMode.value,

            showTeamTable:
              tvShowTeams.checked,

            showRecentBids:
              tvShowBids.checked
          });


        if (!result?.ok) {

          throw new Error(
            result?.error
            ||
            'Impossibile salvare il layout.'
          );
        }


        showTvMessage(
          'Layout TV salvato.',
          'success'
        );


        await loadPresenterState(
          true
        );


      } catch (error) {

        console.error(
          error
        );


        showTvMessage(
          error.message
          ||
          'Errore salvataggio layout.',
          'error'
        );


      } finally {

        tvSaveLayout.disabled =
          false;


        tvSaveLayout.textContent =
          oldText;
      }
    }
  );


/* =========================================================
   FULLSCREEN
   ========================================================= */

tvFullscreenButton
  ?.addEventListener(
    'click',
    async () => {

      try {

        if (!document.fullscreenElement) {

          await document
            .documentElement
            .requestFullscreen();

        } else {

          await document
            .exitFullscreen();
        }

      } catch (error) {

        console.error(
          error
        );


        showTvMessage(
          'Schermo intero non disponibile in questo browser.',
          'error'
        );
      }
    }
  );


document
  .addEventListener(
    'fullscreenchange',
    () => {

      if (!tvFullscreenButton) {
        return;
      }


      tvFullscreenButton.textContent =
        document.fullscreenElement
          ? 'Esci da schermo intero'
          : 'Schermo intero';
    }
  );


/* =========================================================
   LOOP
   ========================================================= */

setInterval(
  renderTimer,
  250
);


setInterval(
  () =>
    loadPresenterState(
      true
    ),
  1500
);


/* =========================================================
   BOOT
   ========================================================= */

selectedLeague =
  getSelectedLeague();


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html';

} else {

  loadPresenterState();
}
