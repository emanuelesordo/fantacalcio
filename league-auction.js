/* =========================================================
   league-auction.js
   BASE PAGINA ASTA
   ========================================================= */

const SUPABASE_URL = 'https://yyklmhzjxzkvycmxkegx.supabase.co';
const AUCTION_API_URL = `${SUPABASE_URL}/functions/v1/auction-api`;

let selectedLeague = null;
let auctionData = null;
let workingTeamOrder = [];

const message = document.getElementById('page-message');
const leagueTitle = document.getElementById('league-title');
const leagueSubtitle = document.getElementById('league-subtitle');
const setupTab = document.getElementById('setup-tab');
const phaseTitle = document.getElementById('auction-phase-title');
const phaseSubtitle = document.getElementById('auction-phase-subtitle');
const statusLine = document.getElementById('auction-status-line');
const blockersBox = document.getElementById('auction-blockers');
const controlArea = document.getElementById('auction-control-area');
const prepareButton = document.getElementById('prepare-auction-button');
const teamsBox = document.getElementById('auction-teams');
const settingsBox = document.getElementById('auction-settings');
const preparedSection = document.getElementById('prepared-session-section');
const teamOrderBox = document.getElementById('auction-team-order');
const teamOrderActions = document.getElementById('team-order-actions');
const saveTeamOrderButton = document.getElementById('save-team-order-button');
const startAuctionButton = document.getElementById('start-auction-button');
const liveSection = document.getElementById('live-section');
const liveHelp = document.getElementById('live-help');
const currentPlayerBox = document.getElementById('current-player-box');
const callPanel = document.getElementById('call-panel');
const callTeamTitle = document.getElementById('call-team-title');
const callPermissionHelp = document.getElementById('call-permission-help');
const callFormArea = document.getElementById('call-form-area');
const callPlayerSearch = document.getElementById('call-player-search');
const openingBidField = document.getElementById('opening-bid-field');
const openingBid = document.getElementById('opening-bid');
const callCandidates = document.getElementById('call-candidates');

function getSession() {
  try {
    const raw = localStorage.getItem('fantacalcio_session');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function getSelectedLeague() {
  try {
    const raw = localStorage.getItem('fantacalcio_selected_league');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function getPlayerRoles(player) {
  if (!player) return [];

  const mantra = Array.isArray(player.mantra_roles)
    ? player.mantra_roles.filter(Boolean)
    : [];

  if (mantra.length) return mantra;

  return player.classic_role
    ? [player.classic_role]
    : [];
}

function sessionStatusLabel(status) {
  return ({
    prepared: 'preparata',
    live: 'live',
    paused: 'in pausa',
    review: 'riepilogo test',
    completed: 'completata',
    cancelled: 'annullata'
  })[status] || 'da preparare';
}

function showMessage(text = '', type = '') {
  if (!message) return;

  message.textContent = text;
  message.className = `message ${type}`;
}

function activeAuctionSettings() {
  return (
    auctionData?.auctionSession?.setup_snapshot
    ||
    auctionData?.settings
    ||
    {}
  );
}

function nominationModeLabel(value) {
  return ({
    call: 'Chiamata',
    list: 'Lista',
    random: 'Casuale'
  })[value] || value || '—';
}

function bidModeLabel(value) {
  return ({
    wild: 'Libero',
    turn: 'A turno'
  })[value] || value || '—';
}

function timerModeLabel(settings) {
  if (settings?.timer_mode === 'fixed') {
    return `Fisso · ${Number(settings.fixed_timer_seconds || 0)}s`;
  }

  if (settings?.timer_mode === 'dynamic') {
    return 'Dinamico';
  }

  return '—';
}

function baseModeLabel(value) {
  return ({
    free: 'Libera',
    quotation: 'Quotazione'
  })[value] || value || '—';
}

async function callApi(body) {
  const session = getSession();

  if (!session?.token) {
    window.location.href = 'index.html';
    return null;
  }

  if (!selectedLeague?.id) {
    window.location.href = 'leagues.html';
    return null;
  }

  let response;

  try {
    response = await fetch(
      AUCTION_API_URL,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          ...body,
          leagueId: selectedLeague.id,
          sessionToken: session.token
        })
      }
    );
  } catch {
    throw new Error(
      'Impossibile contattare il server.'
    );
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error(
      'Risposta non valida dal server.'
    );
  }

  if (response.status === 401) {
    window.location.href = 'index.html';
    return null;
  }

  return data;
}

function renderHeader() {
  if (!auctionData) return;

  leagueTitle.textContent =
    `Asta · ${auctionData.league.name}`;

  const status =
    auctionData?.auctionSession?.status;

  leagueSubtitle.textContent =
    status
      ? `Sessione ${sessionStatusLabel(status)}`
      : 'Preparazione asta';

  if (setupTab) {
    setupTab.hidden =
      !auctionData?.permissions?.isLeagueAdmin;
  }
}

function renderStatus() {
  if (!auctionData) return;

  const session =
    auctionData?.auctionSession;

  const readiness =
    auctionData?.readiness
    || {
      ready: false,
      blockers: []
    };

  if (!session) {
    phaseTitle.textContent =
      'Preparazione';

    phaseSubtitle.textContent =
      'Controlli prima dell’avvio';

    statusLine.innerHTML = `
      <span class="badge ${readiness.ready ? 'good' : 'warning'}">
        ${readiness.ready ? 'PRONTA' : 'DA COMPLETARE'}
      </span>

      <span class="badge">
        ${Number(readiness.teamCount || 0)} squadre
      </span>

      <span class="badge">
        ${Number(readiness.playerCount || 0)} giocatori
      </span>
    `;

    blockersBox.innerHTML =
      readiness.blockers?.length
        ? readiness.blockers
            .map(
              item =>
                `• ${escapeHtml(item)}`
            )
            .join('<br>')
        : 'Tutti i requisiti dell’asta reale sono soddisfatti.';

    const canControl =
      auctionData?.permissions?.canControlAuction
      === true;

    controlArea.hidden =
      !canControl;

    if (prepareButton) {
      prepareButton.disabled =
        !readiness.ready;

      prepareButton.title =
        readiness.ready
          ? 'Prepara la sessione d’asta reale.'
          : (
              readiness.blockers?.join(' ')
              ||
              'Asta reale non pronta.'
            );
    }

    return;
  }

  phaseTitle.textContent =
    session.status === 'prepared'
      ? 'Sessione preparata'
      : session.status === 'live'
        ? 'Asta live'
        : session.status === 'review'
          ? 'Riepilogo test'
          : 'Asta';

  phaseSubtitle.textContent =
    session.is_test
      ? 'Sessione temporanea'
      : 'Sessione ufficiale';

  statusLine.innerHTML = `
    <span class="badge ${session.status === 'live' ? 'good' : ''}">
      ${escapeHtml(
        sessionStatusLabel(
          session.status
        ).toUpperCase()
      )}
    </span>

    ${
      session.is_test
        ? '<span class="badge warning">TEST</span>'
        : ''
    }
  `;

  blockersBox.textContent =
    session.status === 'prepared'
      ? 'Definisci l’ordine delle squadre e avvia l’asta.'
      : session.status === 'live'
        ? 'Sessione in corso.'
        : session.status === 'review'
          ? 'Controlla le rose del test prima della cancellazione.'
          : '';

  controlArea.hidden =
    true;
}

function renderTeams() {
  if (!teamsBox) return;

  const teams =
    auctionData?.teams || [];

  if (!teams.length) {
    teamsBox.innerHTML = `
      <div class="empty-state">
        Nessuna squadra attiva.
      </div>
    `;

    return;
  }

  teamsBox.innerHTML =
    teams
      .map(
        team => `
          <div class="list-row">

            <div class="list-row-main">

              <div class="list-row-title">

                <strong>
                  ${escapeHtml(team.name)}
                </strong>

                <small>
                  ${
                    team.president
                      ? `Presidente: ${escapeHtml(team.president.username)}`
                      : 'Presidente non assegnato'
                  }
                </small>

              </div>

              <span class="badge ${team.president ? 'good' : 'warning'}">
                ${team.president ? 'OK' : 'SENZA PRESIDENTE'}
              </span>

            </div>

          </div>
        `
      )
      .join('');
}

function renderSettings() {
  if (!settingsBox) return;

  const settings =
    activeAuctionSettings();

  if (
    !settings
    ||
    Object.keys(settings).length === 0
  ) {
    settingsBox.innerHTML = `
      <div class="empty-state">
        Setup non disponibile.
      </div>
    `;

    return;
  }

  const direction =
    settings.turn_direction === 'counterclockwise'
      ? 'Antiorario'
      : 'Orario';

  const rows = [
    [
      'Modalità',
      settings.fantasy_mode === 'mantra'
        ? 'Mantra'
        : 'Classic'
    ],
    [
      'Crediti',
      settings.initial_credits ?? '—'
    ],
    [
      'Chiamata',
      nominationModeLabel(
        settings.nomination_mode
      )
    ],
    [
      'Base',
      baseModeLabel(
        settings.auction_base_mode
      )
    ],
    [
      'Rilanci',
      bidModeLabel(
        settings.bid_mode
      )
    ],
    [
      'Direzione',
      settings.bid_mode === 'turn'
        ? direction
        : '—'
    ],
    [
      'Timer',
      timerModeLabel(settings)
    ]
  ];

  settingsBox.innerHTML =
    rows
      .map(
        ([label, value]) => `
          <div class="setting-row">

            <span>
              ${escapeHtml(label)}
            </span>

            <strong>
              ${escapeHtml(value)}
            </strong>

          </div>
        `
      )
      .join('');
}

function syncWorkingTeamOrder() {
  const serverIds =
    (auctionData?.teamOrder || [])
      .map(
        item =>
          item.team_id
      );

  const same =
    serverIds.length
    === workingTeamOrder.length
    &&
    serverIds.every(
      id =>
        workingTeamOrder.includes(id)
    );

  if (!same) {
    workingTeamOrder =
      [...serverIds];
  }
}

function orderedTeamObject(teamId) {
  return (
    auctionData?.teams || []
  )
    .find(
      team =>
        team.id === teamId
    )
    || null;
}

function moveTeam(index, delta) {
  const newIndex =
    index + delta;

  if (
    newIndex < 0
    ||
    newIndex >= workingTeamOrder.length
  ) {
    return;
  }

  const copy =
    [...workingTeamOrder];

  [
    copy[index],
    copy[newIndex]
  ] = [
    copy[newIndex],
    copy[index]
  ];

  workingTeamOrder =
    copy;

  renderPreparedSession();
}

function renderPreparedSession() {
  if (
    !preparedSection
    ||
    !teamOrderBox
  ) {
    return;
  }

  const session =
    auctionData?.auctionSession;

  const show =
    session?.status === 'prepared';

  preparedSection.hidden =
    !show;

  if (!show) {
    teamOrderBox.innerHTML =
      '';

    return;
  }

  syncWorkingTeamOrder();

  teamOrderBox.innerHTML =
    workingTeamOrder
      .map(
        (teamId, index) => {
          const team =
            orderedTeamObject(teamId);

          const president =
            team?.president
              ? `Presidente: ${escapeHtml(team.president.username)}`
              : session.is_test
                ? 'Senza Presidente · gestibile dal Banditore'
                : 'Presidente non assegnato';

          const controls =
            auctionData?.permissions?.canControlAuction
              ? `
                  <div class="league-actions">

                    <button
                      type="button"
                      class="secondary"
                      data-order-up="${index}"
                      ${
                        index === 0
                          ? 'disabled'
                          : ''
                      }
                    >
                      ↑
                    </button>

                    <button
                      type="button"
                      class="secondary"
                      data-order-down="${index}"
                      ${
                        index
                        ===
                        workingTeamOrder.length - 1
                          ? 'disabled'
                          : ''
                      }
                    >
                      ↓
                    </button>

                  </div>
                `
              : '';

          return `
            <div class="list-row">

              <div class="list-row-main">

                <div class="list-row-title">

                  <strong>
                    ${index + 1}. ${escapeHtml(team?.name || 'Squadra')}
                  </strong>

                  <small>
                    ${president}
                  </small>

                </div>

                ${controls}

              </div>

            </div>
          `;
        }
      )
      .join('');

  const canControl =
    auctionData?.permissions?.canControlAuction
    === true;

  if (teamOrderActions) {
    teamOrderActions.hidden =
      !canControl;
  }

  if (saveTeamOrderButton) {
    saveTeamOrderButton.disabled =
      !canControl
      ||
      workingTeamOrder.length < 1;
  }

  if (startAuctionButton) {
    startAuctionButton.disabled =
      !canControl
      ||
      workingTeamOrder.length < 1;
  }
}

teamOrderBox?.addEventListener(
  'click',
  event => {
    const up =
      event.target.closest(
        '[data-order-up]'
      );

    if (up) {
      moveTeam(
        Number(
          up.dataset.orderUp
        ),
        -1
      );

      return;
    }

    const down =
      event.target.closest(
        '[data-order-down]'
      );

    if (down) {
      moveTeam(
        Number(
          down.dataset.orderDown
        ),
        1
      );
    }
  }
);

async function saveCurrentTeamOrder() {
  const session =
    auctionData?.auctionSession;

  if (
    !session
    ||
    !workingTeamOrder.length
  ) {
    return false;
  }

  const result =
    await callApi({
      action:
        'saveTeamOrder',

      sessionId:
        session.id,

      teamIds:
        workingTeamOrder
    });

  if (!result?.ok) {
    throw new Error(
      result?.error
      ||
      'Impossibile salvare l’ordine delle squadre.'
    );
  }

  return true;
}

function renderCurrentPlayer() {
  if (
    !liveSection
    ||
    !currentPlayerBox
  ) {
    return;
  }

  const session =
    auctionData?.auctionSession;

  const show =
    session?.status === 'live';

  liveSection.hidden =
    !show;

  if (!show) {
    currentPlayerBox.innerHTML =
      '';

    return;
  }

  const player =
    auctionData?.currentPlayer;

  const settings =
    activeAuctionSettings();

  if (!player) {
    currentPlayerBox.innerHTML = `
      <div class="empty-state">
        ${
          settings.nomination_mode === 'call'
            ? 'In attesa della chiamata del prossimo giocatore.'
            : 'Nessun giocatore corrente.'
        }
      </div>
    `;

    if (liveHelp) {
      liveHelp.textContent =
        settings.nomination_mode === 'call'
          ? 'Turno di chiamata'
          : 'Asta in corso';
    }

    return;
  }

  const roles =
    getPlayerRoles(player)
      .join('/');

  const leader =
    auctionData?.currentBidderTeam;

  const currentBid =
    session.current_bid;

  currentPlayerBox.innerHTML = `
    <div class="league-card">

      <div class="league-card-header">

        <div>

          <h2>
            ${escapeHtml(player.name)}
          </h2>

          <p>
            ${escapeHtml(roles || '—')}
            ·
            ${escapeHtml(player.serie_a_team || '—')}
            · Q.
            ${escapeHtml(player.quotation ?? '—')}
          </p>

        </div>

        <span class="badge good">
          ${currentBid ?? '—'}
        </span>

      </div>

      <div class="divider"></div>

      <div class="setting-row">
        <span>Offerta corrente</span>
        <strong>${currentBid ?? '—'}</strong>
      </div>

      <div class="setting-row">
        <span>Leader</span>
        <strong>
          ${
            leader
              ? escapeHtml(leader.name)
              : 'Nessuno'
          }
        </strong>
      </div>

    </div>
  `;

  if (liveHelp) {
    liveHelp.textContent =
      leader
        ? `${leader.name} guida a ${currentBid}.`
        : currentBid
          ? `Base corrente ${currentBid}.`
          : 'In attesa della prima offerta.';
  }
}

function renderCallCandidates() {
  if (!callCandidates) return;

  const source =
    auctionData?.callCandidates
    || [];

  const query =
    String(
      callPlayerSearch?.value || ''
    )
      .trim()
      .toLowerCase();

  const filtered =
    source
      .filter(
        player => {
          if (!query) {
            return true;
          }

          return [
            player.name,
            player.serie_a_team,
            player.classic_role,
            ...(
              Array.isArray(
                player.mantra_roles
              )
                ? player.mantra_roles
                : []
            )
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase()
            .includes(query);
        }
      )
      .slice(
        0,
        50
      );

  if (!filtered.length) {
    callCandidates.innerHTML = `
      <div class="empty-state">
        Nessun giocatore trovato.
      </div>
    `;

    return;
  }

  callCandidates.innerHTML =
    filtered
      .map(
        player => `
          <button
            type="button"
            class="list-row"
            data-call-player="${escapeHtml(player.id)}"
          >

            <span class="list-row-main">

              <span class="list-row-title">

                <strong>
                  ${escapeHtml(player.name)}
                </strong>

                <small>
                  ${escapeHtml(getPlayerRoles(player).join('/') || '—')}
                  ·
                  ${escapeHtml(player.serie_a_team || '—')}
                  · Q.
                  ${escapeHtml(player.quotation ?? '—')}
                </small>

              </span>

            </span>

          </button>
        `
      )
      .join('');
}

function renderCallPanel() {
  if (!callPanel) return;

  const session =
    auctionData?.auctionSession;

  const settings =
    activeAuctionSettings();

  const show =
    Boolean(
      session
      &&
      session.status === 'live'
      &&
      settings.nomination_mode === 'call'
      &&
      !session.current_player_id
    );

  callPanel.hidden =
    !show;

  if (!show) {
    if (callCandidates) {
      callCandidates.innerHTML =
        '';
    }

    return;
  }

  const team =
    auctionData?.currentNominationTeam;

  if (callTeamTitle) {
    callTeamTitle.textContent =
      team
        ? `Chiamata · ${team.name}`
        : 'Chiamata';
  }

  const canCall =
    auctionData?.permissions?.canCallCurrentPlayer
    === true;

  if (callFormArea) {
    callFormArea.hidden =
      !canCall;
  }

  if (callPermissionHelp) {
    callPermissionHelp.textContent =
      canCall
        ? (
            session.is_test
            &&
            auctionData?.permissions?.canControlAuction
              ? 'Modalità test: Admin/Banditore può effettuare la chiamata per la squadra di turno.'
              : 'Seleziona il giocatore da chiamare.'
          )
        : (
            team
              ? `In attesa del Presidente di ${team.name}.`
              : 'In attesa della squadra di chiamata.'
          );
  }

  if (openingBidField) {
    openingBidField.hidden =
      settings.auction_base_mode
      === 'quotation';
  }

  renderCallCandidates();
}

callPlayerSearch?.addEventListener(
  'input',
  renderCallCandidates
);

callCandidates?.addEventListener(
  'click',
  async event => {
    const button =
      event.target.closest(
        '[data-call-player]'
      );

    if (!button) return;

    const session =
      auctionData?.auctionSession;

    if (!session) return;

    const settings =
      activeAuctionSettings();

    const base =
      settings.auction_base_mode === 'quotation'
        ? null
        : Number(
            openingBid?.value
          );

    if (
      settings.auction_base_mode !== 'quotation'
      &&
      (
        !Number.isInteger(base)
        ||
        base < 1
      )
    ) {
      showMessage(
        'La base d’asta deve essere almeno 1.',
        'error'
      );

      return;
    }

    button.disabled =
      true;

    try {
      const result =
        await callApi({
          action:
            'callPlayer',

          sessionId:
            session.id,

          playerId:
            button.dataset.callPlayer,

          openingBid:
            base
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile chiamare il giocatore.'
        );
      }

      showMessage(
        'Giocatore chiamato.',
        'success'
      );

      if (callPlayerSearch) {
        callPlayerSearch.value =
          '';
      }

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante la chiamata.',
        'error'
      );

    } finally {
      button.disabled =
        false;
    }
  }
);

function renderAll() {
  if (!auctionData) return;

  renderHeader();
  renderStatus();
  renderTeams();
  renderSettings();
  renderPreparedSession();
  renderCurrentPlayer();
  renderCallPanel();
}

async function loadLobby() {
  showMessage('');

  try {
    const data =
      await callApi({
        action:
          'getLobby'
      });

    if (!data?.ok) {
      showMessage(
        data?.error
        ||
        'Impossibile caricare l’asta.',
        'error'
      );

      return;
    }

    auctionData =
      data;

    renderAll();

  } catch (error) {
    console.error(error);

    showMessage(
      error.message
      ||
      'Errore durante il caricamento dell’asta.',
      'error'
    );
  }
}

prepareButton?.addEventListener(
  'click',
  async () => {
    prepareButton.disabled =
      true;

    const oldText =
      prepareButton.textContent;

    prepareButton.textContent =
      'Preparazione...';

    try {
      const result =
        await callApi({
          action:
            'prepareAuction'
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile preparare l’asta.'
        );
      }

      showMessage(
        'Sessione d’asta preparata.',
        'success'
      );

      workingTeamOrder =
        [];

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante la preparazione.',
        'error'
      );

    } finally {
      prepareButton.textContent =
        oldText;

      if (
        auctionData
        &&
        !auctionData.auctionSession
      ) {
        prepareButton.disabled =
          !auctionData?.readiness?.ready;
      }
    }
  }
);

saveTeamOrderButton?.addEventListener(
  'click',
  async () => {
    saveTeamOrderButton.disabled =
      true;

    const oldText =
      saveTeamOrderButton.textContent;

    saveTeamOrderButton.textContent =
      'Salvataggio...';

    try {
      await saveCurrentTeamOrder();

      showMessage(
        'Ordine squadre salvato.',
        'success'
      );

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante il salvataggio dell’ordine.',
        'error'
      );

    } finally {
      saveTeamOrderButton.textContent =
        oldText;

      saveTeamOrderButton.disabled =
        false;
    }
  }
);

startAuctionButton?.addEventListener(
  'click',
  async () => {
    const session =
      auctionData?.auctionSession;

    if (!session) return;

    startAuctionButton.disabled =
      true;

    const oldText =
      startAuctionButton.textContent;

    startAuctionButton.textContent =
      'Avvio...';

    try {
      await saveCurrentTeamOrder();

      const result =
        await callApi({
          action:
            'startAuction',

          sessionId:
            session.id
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile avviare l’asta.'
        );
      }

      showMessage(
        session.is_test
          ? 'Asta di test avviata.'
          : 'Asta avviata.',
        'success'
      );

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante l’avvio dell’asta.',
        'error'
      );

    } finally {
      startAuctionButton.textContent =
        oldText;

      startAuctionButton.disabled =
        false;
    }
  }
);

selectedLeague =
  getSelectedLeague();

if (!selectedLeague?.id) {
  window.location.href =
    'leagues.html';
} else {
  loadLobby();
}
