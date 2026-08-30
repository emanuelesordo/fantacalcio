const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const API_URL =
  `${SUPABASE_URL}/functions/v1/rosters-api`;

let selectedLeague = null;
let rostersData = null;

const $ = id =>
  document.getElementById(id);

const leagueTitle =
  $('league-title');

const leagueSubtitle =
  $('league-subtitle');

const message =
  $('page-message');

const setupTab =
  $('setup-tab');

const leagueTeamCount =
  $('league-team-count');

const leaguePlayerCount =
  $('league-player-count');

const leagueSpent =
  $('league-spent');

const rostersBoard =
  $('rosters-board');


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
  message.textContent =
    text;

  message.className =
    `message ${type}`;
}


function escapeHtml(value) {
  return String(value ?? '')
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


function fantasyModeLabel(mode) {
  if (mode === 'classic') {
    return 'Classic';
  }

  if (mode === 'mantra') {
    return 'Mantra';
  }

  return '—';
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
        127397 +
        letter.charCodeAt(0)
    )
  );
}


function roleCssClass(role) {
  return `role-${String(role)
    .trim()
    .toLowerCase()}`;
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
   REGOLE ROSA
   ========================================================= */

function getRosterBounds() {
  const settings =
    rostersData.settings;

  if (
    settings.fantasy_mode
    === 'classic'
  ) {
    const classic =
      settings
        .roster_config
        ?.classic
      || {};

    const total =
      Number(
        classic.P || 0
      )
      +
      Number(
        classic.D || 0
      )
      +
      Number(
        classic.C || 0
      )
      +
      Number(
        classic.A || 0
      );

    return {
      min: total,
      max: total
    };
  }

  const total =
    settings
      .roster_config
      ?.mantra
      ?.total
    || {};

  return {
    min:
      Number(
        total.min || 0
      ),

    max:
      Number(
        total.max || 0
      )
  };
}


function getPlayerRoles(player) {
  if (
    rostersData
      .settings
      .fantasy_mode
    === 'mantra'
  ) {
    return player
      ?.mantra_roles
      || [];
  }

  return player
    ?.classic_role
      ? [
          player.classic_role
        ]
      : [];
}


function renderRoleBadges(player) {
  return getPlayerRoles(player)
    .map(
      role => `
        <span
          class="role-badge ${roleCssClass(role)}"
        >
          ${escapeHtml(role)}
        </span>
      `
    )
    .join('');
}


function getTeamConstraints(
  assignments
) {
  const settings =
    rostersData.settings;

  if (
    settings.fantasy_mode
    === 'classic'
  ) {
    const target =
      settings
        .roster_config
        ?.classic
      || {};

    const counts = {
      P: 0,
      D: 0,
      C: 0,
      A: 0
    };

    for (
      const assignment
      of assignments
    ) {
      const role =
        assignment
          .player
          ?.classic_role;

      if (
        Object.hasOwn(
          counts,
          role
        )
      ) {
        counts[role] += 1;
      }
    }

    return [
      `P ${counts.P}/${Number(target.P || 0)}`,
      `D ${counts.D}/${Number(target.D || 0)}`,
      `C ${counts.C}/${Number(target.C || 0)}`,
      `A ${counts.A}/${Number(target.A || 0)}`
    ];
  }

  const mantra =
    settings
      .roster_config
      ?.mantra
    || {};

  let goalkeepers = 0;

  for (
    const assignment
    of assignments
  ) {
    const roles =
      assignment
        .player
        ?.mantra_roles
      || [];

    if (
      roles.includes('Por')
      ||
      roles.includes('P')
    ) {
      goalkeepers += 1;
    }
  }

  const outfield =
    assignments.length
    - goalkeepers;

  return [
    `P ${goalkeepers}/${Number(mantra.goalkeepers?.min || 0)}–${Number(mantra.goalkeepers?.max || 0)}`,
    `Mov. ${outfield}/${Number(mantra.outfield?.min || 0)}–${Number(mantra.outfield?.max || 0)}`,
    `Tot. ${assignments.length}/${Number(mantra.total?.min || 0)}–${Number(mantra.total?.max || 0)}`
  ];
}


/* =========================================================
   GIOCATORE
   ========================================================= */

function renderPlayerRow(
  assignment
) {
  const player =
    assignment.player;

  if (!player) {
    return '';
  }

  const flag =
    countryCodeToEmoji(
      player.nationality_iso2
    );

  return `
    <div class="roster-player-row">

      <div class="roster-player-main">

        <span class="player-role-badges">
          ${renderRoleBadges(player)}
        </span>

        <span class="roster-player-name">
          ${escapeHtml(
            player.name
          )}
        </span>

        ${
          flag
            ? `
              <span
                class="player-flag"
                title="${escapeHtml(
                  player.nationality_name
                  || ''
                )}"
              >
                ${escapeHtml(flag)}
              </span>
            `
            : ''
        }

      </div>


      <div class="roster-player-club">
        ${escapeHtml(
          player.serie_a_team
          || '—'
        )}
      </div>


      <div class="roster-player-price">
        ${escapeHtml(
          assignment.purchase_price
        )}
      </div>

    </div>
  `;
}


/* =========================================================
   RENDER ROSE
   ========================================================= */

function renderRosters() {
  const teams =
    rostersData.teams
    || [];

  const assignments =
    rostersData.assignments
    || [];

  const initialCredits =
    Number(
      rostersData
        .settings
        .initial_credits
      || 0
    );

  const bounds =
    getRosterBounds();

  leagueTeamCount.textContent =
    teams.length;

  leaguePlayerCount.textContent =
    assignments.length;

  const totalSpent =
    assignments.reduce(
      (
        sum,
        assignment
      ) =>
        sum
        +
        Number(
          assignment.purchase_price
          || 0
        ),
      0
    );

  leagueSpent.textContent =
    totalSpent;

  rostersBoard.innerHTML =
    '';

  if (!teams.length) {
    rostersBoard.innerHTML = `
      <div class="empty-state">
        Nessuna squadra attiva nella lega.
      </div>
    `;

    return;
  }

  for (
    const team
    of teams
  ) {
    const teamAssignments =
      assignments
        .filter(
          assignment =>
            assignment.team_id
            === team.id
        )
        .sort(
          (a, b) =>
            Number(
              b.purchase_price
              || 0
            )
            -
            Number(
              a.purchase_price
              || 0
            )
        );

    const spent =
      teamAssignments.reduce(
        (
          sum,
          assignment
        ) =>
          sum
          +
          Number(
            assignment.purchase_price
            || 0
          ),
        0
      );

    const remaining =
      initialCredits
      - spent;

    const maxPlayers =
      Math.max(
        bounds.max,
        1
      );

    const progress =
      Math.min(
        100,
        Math.round(
          teamAssignments.length
          /
          maxPlayers
          *
          100
        )
      );

    const constraints =
      getTeamConstraints(
        teamAssignments
      );

    const card =
      document.createElement(
        'details'
      );

    card.className =
      'roster-team';

    card.innerHTML = `

      <summary>

        <div class="roster-team-main">

          <h3>
            ${escapeHtml(
              team.name
            )}
          </h3>

          <small>
            Presidente:
            ${escapeHtml(
              team.presidentUsername
              || 'non assegnato'
            )}
          </small>

        </div>


        <div class="roster-team-kpis">

          <span class="badge good roster-credit">
            ${escapeHtml(
              remaining
            )}
            crediti
          </span>

          <span class="badge">
            ${teamAssignments.length}/${bounds.max}
            giocatori
          </span>

          <span class="badge admin">
            Spesi
            ${escapeHtml(
              spent
            )}
          </span>

        </div>

      </summary>


      <div class="roster-body">

        <div
          class="roster-progress"
          style="--progress: ${progress}%"
        >
          <span></span>
        </div>


        <p class="setting-help">
          Rosa richiesta:
          ${
            bounds.min
            === bounds.max
              ? `${bounds.max} giocatori`
              : `${bounds.min}–${bounds.max} giocatori`
          }.
        </p>


        <div class="roster-constraints">

          ${
            constraints
              .map(
                value => `
                  <span class="badge">
                    ${escapeHtml(value)}
                  </span>
                `
              )
              .join('')
          }

          ${
            rostersData
              .settings
              .under_enabled
              ? `
                <span class="badge admin">
                  UNDER min.
                  ${escapeHtml(
                    rostersData
                      .settings
                      .under_min_count
                  )}
                </span>
              `
              : ''
          }

        </div>


        ${
          teamAssignments.length
            ? `
              <div class="roster-player-list">
                ${
                  teamAssignments
                    .map(
                      renderPlayerRow
                    )
                    .join('')
                }
              </div>
            `
            : `
              <div class="roster-empty">
                Nessun giocatore ancora assegnato.
              </div>
            `
        }

      </div>
    `;

    rostersBoard.appendChild(
      card
    );
  }
}


/* =========================================================
   LOAD
   ========================================================= */

async function loadRosters() {
  showMessage('');

  try {
    const data =
      await callApi({
        action:
          'getRosters'
      });

    if (!data?.ok) {
      showMessage(
        data?.error
        ||
        'Impossibile caricare le rose.',
        'error'
      );

      return;
    }

    rostersData =
      data;

    leagueTitle.textContent =
      `Rose · ${data.league.name}`;

    leagueSubtitle.textContent =
      `${fantasyModeLabel(
        data.settings
          .fantasy_mode
      )} · ${data.settings.initial_credits} crediti`;

    if (setupTab) {
      setupTab.hidden =
        !data.permissions
          .canAccessSetup;
    }

    renderRosters();

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
  loadRosters();
}
