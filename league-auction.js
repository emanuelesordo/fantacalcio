const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const API_URL =
  `${SUPABASE_URL}/functions/v1/auction-api`;

let selectedLeague = null;
let auctionData = null;

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


function fantasyModeLabel(value) {

  if (value === 'classic') {
    return 'Classic';
  }

  if (value === 'mantra') {
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


function timerLabel(
  mode,
  seconds
) {

  if (
    mode === 'fixed'
  ) {

    return `Fisso · ${seconds}s`;
  }


  if (
    mode === 'dynamic'
  ) {

    return 'Dinamico';
  }


  return '—';
}


function sessionStatusLabel(status) {

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


  return labels[status]
    || status
    || '—';
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

            Sessione:
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
      'Tutti i requisiti necessari sono soddisfatti.';
  }


  const canControl =
    auctionData.permissions
      .canControlAuction;


  controlArea.hidden =
    !canControl
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
              team.presidentUsername

                ? `
                  Presidente:
                  ${escapeHtml(
                    team.presidentUsername
                  )}
                `

                : 'Presidente non assegnato'
            }

          </small>

        </div>


        <span
          class="badge ${
            team.presidentUsername
              ? 'good'
              : 'warning'
          }"
        >

          ${
            team.presidentUsername
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
    auctionData.settings;


  if (!settings) {

    settingsBox.innerHTML = `
      <div class="empty-state">
        Setup non disponibile.
      </div>
    `;

    return;
  }


  settingsBox.innerHTML = [

    settingRow(
      'Modalità',
      fantasyModeLabel(
        settings.fantasy_mode
      )
    ),


    settingRow(
      'Crediti',
      settings.initial_credits
    ),


    settingRow(
      'Nomination',
      nominationLabel(
        settings.nomination_mode
      )
    ),


    settingRow(
      'Base asta',
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
      timerLabel(
        settings.timer_mode,
        settings.fixed_timer_seconds
      )
    ),


    settingRow(
      'Incremento minimo',
      '1 credito'
    )

  ].join('');
}


/* =========================================================
   SESSIONE PREPARATA
   ========================================================= */

function renderPreparedSession() {

  const session =
    auctionData.auctionSession;


  preparedSection.hidden =
    !session;


  if (!session) {

    teamOrderBox.innerHTML =
      '';

    return;
  }


  const order =
    auctionData.teamOrder
    || [];


  teamOrderBox.innerHTML =
    '';


  for (
    const item
    of order
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
              item.position
            )}.
            ${escapeHtml(
              item.team?.name
              || 'Squadra'
            )}
          </strong>

          <small>
            ${
              escapeHtml(
                item.team
                  ?.presidentUsername
                || 'Presidente'
              )
            }
          </small>

        </div>


        <span class="badge">
          ${escapeHtml(
            item.passes_used
          )}
          / 5 pass
        </span>

      </div>

    `;


    teamOrderBox.appendChild(
      row
    );
  }
}


/* =========================================================
   PREPARA ASTA
   ========================================================= */

prepareButton.addEventListener(
  'click',
  async () => {

    showMessage('');


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
        'Impossibile caricare la lobby.',
        'error'
      );

      return;
    }


    auctionData =
      data;


    leagueTitle.textContent =
      `Asta · ${data.league.name}`;


    leagueSubtitle.textContent =
      data.auctionSession

        ? `Sessione ${sessionStatusLabel(
            data.auctionSession.status
          )}`

        : 'Preparazione';


    if (setupTab) {

      setupTab.hidden =
        !data.permissions
          .isLeagueAdmin;
    }


    renderStatus();

    renderTeams();

    renderSettings();

    renderPreparedSession();


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
