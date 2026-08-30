const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const API_URL =
  `${SUPABASE_URL}/functions/v1/auction-api`;

let selectedLeague = null;
let auctionData = null;
let localTeamOrder = [];

const $ = id =>
  document.getElementById(id);

const leagueTitle =
  $('league-title');

const leagueSubtitle =
  $('league-subtitle');

const pageMessage =
  $('page-message');

const setupTab =
  $('setup-tab');

const phaseTitle =
  $('auction-phase-title');

const phaseSubtitle =
  $('auction-phase-subtitle');

const statusLine =
  $('auction-status-line');

const blockersBox =
  $('auction-blockers');

const controlArea =
  $('auction-control-area');

const prepareButton =
  $('prepare-auction-button');

const teamsBox =
  $('auction-teams');

const settingsBox =
  $('auction-settings');

const preparedSection =
  $('prepared-session-section');

const teamOrderBox =
  $('auction-team-order');

const teamOrderActions =
  $('team-order-actions');

const saveTeamOrderButton =
  $('save-team-order-button');

const startAuctionButton =
  $('start-auction-button');

const liveSection =
  $('live-section');

const liveHelp =
  $('live-help');

const currentPlayerBox =
  $('current-player-box');

const callPanel =
  $('call-panel');

const callTeamTitle =
  $('call-team-title');

const callPermissionHelp =
  $('call-permission-help');

const callFormArea =
  $('call-form-area');

const callPlayerSearch =
  $('call-player-search');

const openingBidField =
  $('opening-bid-field');

const openingBid =
  $('opening-bid');

const callCandidates =
  $('call-candidates');


/* =========================================================
   STORAGE
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


/* =========================================================
   UTILITY
   ========================================================= */

function showMessage(
  text = '',
  type = ''
) {

  pageMessage.textContent =
    text;

  pageMessage.className =
    `message ${type}`;
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


function formatNumber(
  value,
  digits = 1
) {

  if (
    value === null
    ||
    value === undefined
    ||
    Number.isNaN(
      Number(value)
    )
  ) {

    return '—';
  }


  return Number(value)
    .toLocaleString(
      'it-IT',
      {
        maximumFractionDigits:
          digits
      }
    );
}


function formatPercent(value) {

  if (
    value === null
    ||
    value === undefined
  ) {

    return '—';
  }


  return `${formatNumber(
    value,
    1
  )}%`;
}


function countryCodeToEmoji(code) {

  const iso =
    String(code || '')
      .trim()
      .toUpperCase();


  if (
    !/^[A-Z]{2}$/.test(iso)
  ) {

    return '';
  }


  return String.fromCodePoint(
    ...[...iso].map(
      letter =>
        127397
        +
        letter.charCodeAt(0)
    )
  );
}


function fantasyModeLabel(value) {

  if (
    value === 'classic'
  ) {

    return 'Classic';
  }


  if (
    value === 'mantra'
  ) {

    return 'Mantra';
  }


  return '—';
}


function nominationLabel(value) {

  const labels = {

    call:
      'Chiamata',

    list:
      'Lista',

    random:
      'Casuale'
  };


  return labels[value]
    || value
    || '—';
}


function bidModeLabel(value) {

  const labels = {

    wild:
      'Rilancio libero',

    turn:
      'A turno'
  };


  return labels[value]
    || value
    || '—';
}


function sessionStatusLabel(value) {

  const labels = {

    prepared:
      'Preparata',

    live:
      'In corso',

    paused:
      'In pausa',

    completed:
      'Terminata',

    cancelled:
      'Annullata'
  };


  return labels[value]
    || value
    || '—';
}


function getSessionSettings() {

  return auctionData
    ?.auctionSession
    ?.setup_snapshot
    ||
    auctionData
      ?.settings
    ||
    {};
}


function getPlayerRoles(player) {

  if (!player) {
    return [];
  }


  const mode =
    getSessionSettings()
      .fantasy_mode;


  if (
    mode === 'mantra'
  ) {

    return player.mantra_roles
      || [];
  }


  return player.classic_role
    ? [
        player.classic_role
      ]
    : [];
}


function renderRoleBadges(player) {

  return getPlayerRoles(player)
    .map(
      role => `
        <span class="badge">
          ${escapeHtml(role)}
        </span>
      `
    )
    .join('');
}


/* =========================================================
   API
   ========================================================= */

async function callApi(body) {

  const session =
    getSession();


  if (!session?.token) {

    window.location.href =
      'index.html';

    return null;
  }


  let response;


  try {

    response =
      await fetch(
        API_URL,
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
      'Impossibile contattare il server.'
    );
  }


  let data;


  try {

    data =
      await response.json();

  } catch {

    throw new Error(
      'Risposta non valida dal server.'
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
   STATUS
   ========================================================= */

function renderStatus() {

  const readiness =
    auctionData.readiness;


  const session =
    auctionData.auctionSession;


  statusLine.innerHTML = `

    <span
      class="badge ${
        readiness.ready
          ? 'good'
          : 'warning'
      }"
    >
      ${
        readiness.ready
          ? 'PRONTA'
          : 'DA COMPLETARE'
      }
    </span>


    <span class="badge">
      ${escapeHtml(
        readiness.playerCount
      )}
      giocatori
    </span>


    <span class="badge">
      ${escapeHtml(
        readiness.teamCount
      )}
      /
      ${escapeHtml(
        readiness.expectedTeamCount
      )}
      squadre
    </span>


    <span class="badge">
      ${escapeHtml(
        readiness.presidentCount
      )}
      Presidenti
    </span>


    ${
      session

        ? `
          <span class="badge admin">
            ${escapeHtml(
              sessionStatusLabel(
                session.status
              )
            )}
          </span>
        `

        : ''
    }

  `;


  if (
    session?.status
    === 'live'
  ) {

    phaseTitle.textContent =
      'Asta in corso';

    phaseSubtitle.textContent =
      nominationLabel(
        session
          .setup_snapshot
          ?.nomination_mode
      );


  } else if (
    session?.status
    === 'prepared'
  ) {

    phaseTitle.textContent =
      'Sessione preparata';

    phaseSubtitle.textContent =
      'Definisci l’ordine e avvia l’asta';


  } else {

    phaseTitle.textContent =
      'Preparazione';

    phaseSubtitle.textContent =
      'Controlli prima dell’avvio';
  }


  if (
    readiness.blockers.length
  ) {

    blockersBox.innerHTML =
      readiness.blockers
        .map(
          blocker =>
            `• ${escapeHtml(blocker)}`
        )
        .join('<br>');

  } else {

    blockersBox.textContent =
      session
        ? 'Configurazione valida.'
        : 'Tutti i requisiti necessari sono soddisfatti.';
  }


  controlArea.hidden =
    !auctionData
      .permissions
      .canControlAuction
    ||
    Boolean(session);


  prepareButton.disabled =
    !readiness.ready;
}


/* =========================================================
   SQUADRE
   ========================================================= */

function renderTeams() {

  const teams =
    auctionData.teams
    || [];


  teamsBox.innerHTML =
    '';


  if (
    !teams.length
  ) {

    teamsBox.innerHTML = `
      <div class="empty-state">
        Nessuna squadra attiva.
      </div>
    `;

    return;
  }


  for (
    const team
    of teams
  ) {

    const row =
      document.createElement(
        'div'
      );


    row.className =
      'list-row';


    row.innerHTML = `

      <div class="list-row-main">

        <div class="list-row-title">

          <strong>
            ${escapeHtml(
              team.name
            )}
          </strong>

          <small>

            ${
              team.president

                ? `
                  Presidente:
                  ${escapeHtml(
                    team
                      .president
                      .username
                  )}
                `

                : 'Presidente non assegnato'
            }

          </small>

        </div>


        <span
          class="badge ${
            team.president
              ? 'good'
              : 'warning'
          }"
        >

          ${
            team.president
              ? 'OK'
              : 'MANCA PRESIDENTE'
          }

        </span>

      </div>

    `;


    teamsBox.appendChild(
      row
    );
  }
}


/* =========================================================
   SETUP
   ========================================================= */

function settingRow(
  label,
  value
) {

  return `

    <div class="setting-row">

      <span>
        <strong>
          ${escapeHtml(label)}
        </strong>
      </span>

      <strong>
        ${escapeHtml(value)}
      </strong>

    </div>

  `;
}


function renderSettings() {

  const settings =
    getSessionSettings();


  const rows = [

    settingRow(
      'Modalità',
      fantasyModeLabel(
        settings.fantasy_mode
      )
    ),

    settingRow(
      'Crediti',
      settings.initial_credits
      ?? '—'
    ),

    settingRow(
      'Nomination',
      nominationLabel(
        settings.nomination_mode
      )
    ),

    settingRow(
      'Base',
      settings.auction_base_mode
      === 'quotation'
        ? 'Quotazione'
        : 'Libera'
    ),

    settingRow(
      'Rilanci',
      bidModeLabel(
        settings.bid_mode
      )
    ),

    settingRow(
      'Timer',
      settings.timer_mode
      === 'fixed'
        ? `Fisso · ${
            settings
              .fixed_timer_seconds
          }s`
        : 'Dinamico'
    ),

    settingRow(
      'Incremento',
      '1 credito'
    )
  ];


  if (
    settings.nomination_mode
    === 'list'
  ) {

    rows.push(
      settingRow(
        'Ordine lista',
        `${
          settings.list_sort_by
          === 'quotation'
            ? 'Quotazione'
            : 'Alfabetico'
        } · ${
          String(
            settings
              .list_sort_direction
            || 'asc'
          )
            .toUpperCase()
        }`
      )
    );
  }


  if (
    settings.bid_mode
    === 'turn'
  ) {

    rows.push(
      settingRow(
        'Direzione',
        settings.turn_direction
        === 'counterclockwise'
          ? 'Antiorario'
          : 'Orario'
      )
    );
  }


  settingsBox.innerHTML =
    rows.join('');
}


/* =========================================================
   ORDINE SQUADRE
   ========================================================= */

function moveTeam(
  index,
  direction
) {

  const newIndex =
    index + direction;


  if (
    newIndex < 0
    ||
    newIndex
      >= localTeamOrder.length
  ) {

    return;
  }


  const copy =
    [
      ...localTeamOrder
    ];


  [
    copy[index],
    copy[newIndex]
  ] = [
    copy[newIndex],
    copy[index]
  ];


  localTeamOrder =
    copy;


  renderTeamOrder();
}


function renderTeamOrder() {

  const session =
    auctionData
      .auctionSession;


  preparedSection.hidden =
    !session
    ||
    session.status
    !== 'prepared';


  if (
    !session
    ||
    session.status
    !== 'prepared'
  ) {

    teamOrderBox.innerHTML =
      '';

    teamOrderActions.hidden =
      true;

    return;
  }


  teamOrderBox.innerHTML =
    '';


  const editable =
    auctionData
      .permissions
      .canControlAuction;


  localTeamOrder
    .forEach(
      (
        item,
        index
      ) => {

        const row =
          document.createElement(
            'div'
          );


        row.className =
          'list-row';


        row.innerHTML = `

          <div class="list-row-main">

            <div class="list-row-title">

              <strong>
                ${index + 1}.
                ${escapeHtml(
                  item.team
                    ?.name
                  || 'Squadra'
                )}
              </strong>

              <small>
                ${
                  escapeHtml(
                    item.team
                      ?.president
                      ?.username
                    || 'Presidente'
                  )
                }
              </small>

            </div>


            ${
              editable

                ? `
                  <div class="league-actions">

                    <button
                      type="button"
                      class="secondary"
                      data-move-team="-1"
                      data-index="${index}"
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
                      data-move-team="1"
                      data-index="${index}"
                      ${
                        index
                        ===
                        localTeamOrder.length
                        - 1
                          ? 'disabled'
                          : ''
                      }
                    >
                      ↓
                    </button>

                  </div>
                `

                : ''
            }

          </div>

        `;


        teamOrderBox.appendChild(
          row
        );
      }
    );


  teamOrderActions.hidden =
    !editable;
}


/* =========================================================
   CURRENT PLAYER
   ========================================================= */

function renderCurrentPlayer() {

  const session =
    auctionData
      .auctionSession;


  const isLive =
    session
    &&
    (
      session.status
      === 'live'
      ||
      session.status
      === 'paused'
    );


  liveSection.hidden =
    !isLive;


  if (!isLive) {

    currentPlayerBox.innerHTML =
      '';

    callPanel.hidden =
      true;

    return;
  }


  const settings =
    getSessionSettings();


  const player =
    auctionData
      .currentPlayer;


  if (player) {

    const flag =
      countryCodeToEmoji(
        player.nationality_iso2
      );


    const bid =
      session.current_bid;


    const bidder =
      auctionData
        .currentBidderTeam;


    currentPlayerBox.innerHTML = `

      <div class="league-card">

        <div class="league-card-header">

          <div>

            <h3>

              ${
                flag
                  ? `${escapeHtml(flag)} `
                  : ''
              }

              ${escapeHtml(
                player.name
              )}

            </h3>

            <p>

              ${escapeHtml(
                player.serie_a_team
                || '—'
              )}

              ·

              ${renderRoleBadges(
                player
              )}

            </p>

          </div>


          <div class="user-summary-status">

            ${
              player.slot

                ? `
                  <span class="badge">
                    Slot
                    ${escapeHtml(
                      player.slot
                    )}
                  </span>
                `

                : ''
            }

            ${
              player.pfc
              !== null
              &&
              player.pfc
              !== undefined

                ? `
                  <span class="badge admin">
                    PFC
                    ${escapeHtml(
                      formatNumber(
                        player.pfc,
                        0
                      )
                    )}
                  </span>
                `

                : ''
            }

          </div>

        </div>


        <div class="divider"></div>


        <div class="stats-grid">

          <div class="stat-card">

            <span class="stat-label">
              Offerta corrente
            </span>

            <span class="stat-value">
              ${escapeHtml(
                bid ?? '—'
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              Leader
            </span>

            <span class="stat-value">
              ${escapeHtml(
                bidder
                  ?.name
                || 'Nessuno'
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              Expected FM
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatNumber(
                  player
                    .expected_fantasy_avg,
                  2
                )
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              Titolarità
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatPercent(
                  player
                    .expected_titolarity
                )
              )}
            </span>

          </div>

        </div>

      </div>

    `;


    liveHelp.textContent =
      bidder

        ? `${
            bidder.name
          } guida a ${
            bid
          }`

        : (
            bid
            !== null
            &&
            bid !== undefined

              ? `Base ${bid} · nessuna offerta`

              : 'In attesa della prima offerta'
          );


    callPanel.hidden =
      true;

    return;
  }


  currentPlayerBox.innerHTML = `

    <div class="empty-state">
      Nessun giocatore ancora in asta.
    </div>

  `;


  if (
    settings.nomination_mode
    === 'call'
  ) {

    renderCallPanel();

  } else {

    callPanel.hidden =
      true;
  }
}


/* =========================================================
   CHIAMATA
   ========================================================= */

function getFilteredCallCandidates() {

  const search =
    callPlayerSearch
      .value
      .trim()
      .toLowerCase();


  const candidates =
    auctionData
      .callCandidates
    || [];


  const filtered =
    !search
      ? candidates
      : candidates
          .filter(
            player => {

              const haystack =
                [
                  player.name,
                  player.serie_a_team,
                  player.classic_role,
                  ...(
                    player.mantra_roles
                    || []
                  )
                ]
                  .filter(Boolean)
                  .join(' ')
                  .toLowerCase();


              return haystack
                .includes(search);
            }
          );


  return filtered.slice(
    0,
    30
  );
}


function renderCallCandidates() {

  const candidates =
    getFilteredCallCandidates();


  callCandidates.innerHTML =
    '';


  if (!candidates.length) {

    callCandidates.innerHTML = `
      <div class="empty-state">
        Nessun giocatore trovato.
      </div>
    `;

    return;
  }


  const baseMode =
    getSessionSettings()
      .auction_base_mode;


  for (
    const player
    of candidates
  ) {

    const row =
      document.createElement(
        'div'
      );


    row.className =
      'list-row';


    row.innerHTML = `

      <div class="list-row-main">

        <div class="list-row-title">

          <strong>
            ${escapeHtml(
              player.name
            )}
          </strong>

          <small>

            ${escapeHtml(
              player.serie_a_team
              || '—'
            )}

            ·

            ${escapeHtml(
              getPlayerRoles(
                player
              )
                .join(', ')
              || '—'
            )}

            ${
              baseMode
              === 'quotation'

                ? `
                  · Q.
                  ${escapeHtml(
                    player.quotation
                    ?? '—'
                  )}
                `

                : ''
            }

          </small>

        </div>


        <button
          type="button"
          data-call-player
          data-player-id="${escapeHtml(
            player.id
          )}"
        >
          Chiama
        </button>

      </div>

    `;


    callCandidates.appendChild(
      row
    );
  }
}


function renderCallPanel() {

  const team =
    auctionData
      .currentNominationTeam;


  const canCall =
    auctionData
      .permissions
      .canCallCurrentPlayer;


  const settings =
    getSessionSettings();


  callPanel.hidden =
    false;


  callTeamTitle.textContent =
    team
      ? `Chiamata · ${team.name}`
      : 'Chiamata';


  if (canCall) {

    callPermissionHelp.textContent =
      'È il tuo turno: scegli il giocatore da chiamare.';

  } else {

    callPermissionHelp.textContent =
      team
        ? `In attesa del Presidente di ${team.name}.`
        : 'In attesa della squadra di turno.';
  }


  callFormArea.hidden =
    !canCall;


  if (!canCall) {
    return;
  }


  openingBidField.hidden =
    settings.auction_base_mode
    === 'quotation';


  if (
    settings.auction_base_mode
    !== 'quotation'
    &&
    (
      !openingBid.value
      ||
      Number(
        openingBid.value
      ) < 1
    )
  ) {

    openingBid.value =
      '1';
  }


  renderCallCandidates();
}


/* =========================================================
   AZIONI ORDINE
   ========================================================= */

teamOrderBox.addEventListener(
  'click',
  event => {

    const button =
      event.target.closest(
        '[data-move-team]'
      );


    if (!button) {
      return;
    }


    moveTeam(
      Number(
        button.dataset.index
      ),
      Number(
        button.dataset.moveTeam
      )
    );
  }
);


saveTeamOrderButton.addEventListener(
  'click',
  async () => {

    const session =
      auctionData
        .auctionSession;


    if (!session) {
      return;
    }


    saveTeamOrderButton.disabled =
      true;


    const oldText =
      saveTeamOrderButton.textContent;


    saveTeamOrderButton.textContent =
      'Salvataggio...';


    try {

      const result =
        await callApi({

          action:
            'saveTeamOrder',

          sessionId:
            session.id,

          teamIds:
            localTeamOrder
              .map(
                item =>
                  item.team_id
              )
        });


      if (!result?.ok) {

        throw new Error(
          result?.error
          ||
          'Impossibile salvare l’ordine.'
        );
      }


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
        'Errore durante il salvataggio.',
        'error'
      );


    } finally {

      saveTeamOrderButton.disabled =
        false;


      saveTeamOrderButton.textContent =
        oldText;
    }
  }
);


/* =========================================================
   AVVIA ASTA
   ========================================================= */

startAuctionButton.addEventListener(
  'click',
  async () => {

    const session =
      auctionData
        .auctionSession;


    if (!session) {
      return;
    }


    startAuctionButton.disabled =
      true;


    const oldText =
      startAuctionButton.textContent;


    startAuctionButton.textContent =
      'Avvio...';


    try {

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
        'Asta avviata.',
        'success'
      );


      await loadLobby();


    } catch (error) {

      console.error(error);


      showMessage(
        error.message
        ||
        'Errore durante l’avvio.',
        'error'
      );


    } finally {

      startAuctionButton.disabled =
        false;


      startAuctionButton.textContent =
        oldText;
    }
  }
);


/* =========================================================
   PREPARA ASTA
   ========================================================= */

prepareButton.addEventListener(
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

      prepareButton.disabled =
        false;


      prepareButton.textContent =
        oldText;
    }
  }
);


/* =========================================================
   CHIAMA GIOCATORE
   ========================================================= */

callPlayerSearch.addEventListener(
  'input',
  renderCallCandidates
);


callCandidates.addEventListener(
  'click',
  async event => {

    const button =
      event.target.closest(
        '[data-call-player]'
      );


    if (!button) {
      return;
    }


    const session =
      auctionData
        .auctionSession;


    const playerId =
      button.dataset.playerId;


    if (
      !session
      ||
      !playerId
    ) {

      return;
    }


    const settings =
      getSessionSettings();


    let base =
      null;


    if (
      settings.auction_base_mode
      !== 'quotation'
    ) {

      base =
        Number(
          openingBid.value
        );


      if (
        !Number.isInteger(base)
        ||
        base < 1
      ) {

        showMessage(
          'La base d’asta deve essere almeno 1.',
          'error'
        );

        return;
      }
    }


    button.disabled =
      true;


    const oldText =
      button.textContent;


    button.textContent =
      'Chiamata...';


    try {

      const result =
        await callApi({

          action:
            'callPlayer',

          sessionId:
            session.id,

          playerId,

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


      button.textContent =
        oldText;
    }
  }
);


/* =========================================================
   RENDER COMPLETO
   ========================================================= */

function renderAll() {

  renderStatus();

  renderTeams();

  renderSettings();


  localTeamOrder =
    (
      auctionData.teamOrder
      || []
    )
      .map(
        item => ({
          ...item
        })
      );


  renderTeamOrder();

  renderCurrentPlayer();
}


/* =========================================================
   LOAD
   ========================================================= */

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


    leagueTitle.textContent =
      `Asta · ${
        data.league.name
      }`;


    leagueSubtitle.textContent =
      data.auctionSession

        ? `Sessione ${
            sessionStatusLabel(
              data
                .auctionSession
                .status
            )
          }`

        : 'Preparazione';


    if (setupTab) {

      setupTab.hidden =
        !data
          .permissions
          .isLeagueAdmin;
    }


    renderAll();


  } catch (error) {

    console.error(error);


    showMessage(
      error.message
      ||
      'Errore durante il caricamento.',
      'error'
    );
  }
}


/* =========================================================
   START
   ========================================================= */

selectedLeague =
  getSelectedLeague();


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html';

} else {

  loadLobby();
}
