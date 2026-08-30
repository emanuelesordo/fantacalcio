const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/list-api`


let selectedLeague = null
let listData = null


const leagueTitle =
  document.getElementById(
    'league-title'
  )

const leagueSubtitle =
  document.getElementById(
    'league-subtitle'
  )

const message =
  document.getElementById(
    'page-message'
  )

const setupTab =
  document.getElementById(
    'setup-tab'
  )

const importInfo =
  document.getElementById(
    'import-info'
  )

const adminImportNote =
  document.getElementById(
    'admin-import-note'
  )

const playersCount =
  document.getElementById(
    'players-count'
  )

const fantasyMode =
  document.getElementById(
    'fantasy-mode'
  )

const importDetails =
  document.getElementById(
    'import-details'
  )

const toolbar =
  document.getElementById(
    'list-toolbar'
  )

const playerSearch =
  document.getElementById(
    'player-search'
  )

const statusFilter =
  document.getElementById(
    'player-status-filter'
  )

const filteredCount =
  document.getElementById(
    'filtered-count'
  )

const playersList =
  document.getElementById(
    'players-list'
  )


/* =========================================================
   STORAGE
   ========================================================= */

function getSession() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_session'
      )

    return raw
      ? JSON.parse(raw)
      : null

  } catch {

    return null
  }
}


function getSelectedLeague() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_selected_league'
      )

    return raw
      ? JSON.parse(raw)
      : null

  } catch {

    return null
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
    text

  message.className =
    `message ${type}`
}


function escapeHtml(value) {

  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}


function formatDateTime(value) {

  if (!value) {
    return '—'
  }


  return new Date(value)
    .toLocaleString(
      'it-IT',
      {
        dateStyle:
          'short',

        timeStyle:
          'short'
      }
    )
}


function statusLabel(status) {

  const labels = {

    available:
      'Disponibile',

    in_auction:
      'In asta',

    assigned:
      'Assegnato',

    excluded:
      'Escluso'
  }


  return labels[status]
    || status
}


function fantasyModeLabel(mode) {

  if (mode === 'classic') {
    return 'Classic'
  }

  if (mode === 'mantra') {
    return 'Mantra'
  }

  return '—'
}


/* =========================================================
   API
   ========================================================= */

async function callApi(body) {

  const session =
    getSession()


  if (!session?.token) {

    window.location.href =
      'index.html'

    return null
  }


  let response


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
      )

  } catch {

    throw new Error(
      'Impossibile contattare il server.'
    )
  }


  let data


  try {

    data =
      await response.json()

  } catch {

    throw new Error(
      'Risposta non valida dal server.'
    )
  }


  if (
    response.status === 401
  ) {

    window.location.href =
      'index.html'

    return null
  }


  return data
}


/* =========================================================
   FILTRI
   ========================================================= */

function getFilteredPlayers() {

  const players =
    listData?.players || []


  const search =
    playerSearch
      .value
      .trim()
      .toLowerCase()


  const status =
    statusFilter.value


  return players.filter(
    player => {

      if (
        status !== 'all'
        &&
        player.status !== status
      ) {

        return false
      }


      if (!search) {
        return true
      }


      const haystack =
        [
          player.name,
          player.serie_a_team,
          player.classic_role,
          ...(player.mantra_roles || [])
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()


      return haystack.includes(
        search
      )
    }
  )
}


/* =========================================================
   RUOLI
   ========================================================= */

function renderPlayerRole(player) {

  const mode =
    listData
      ?.settings
      ?.fantasyMode


  if (mode === 'mantra') {

    const roles =
      player.mantra_roles || []


    if (
      roles.length === 0
    ) {

      return '—'
    }


    return roles.join(', ')
  }


  return player.classic_role
    || '—'
}


/* =========================================================
   RENDER LISTONE
   ========================================================= */

function renderPlayers() {

  const players =
    getFilteredPlayers()


  playersList.innerHTML =
    ''


  filteredCount.textContent =
    `${players.length} di ${
      listData?.players?.length || 0
    } giocatori`


  if (
    players.length === 0
  ) {

    playersList.innerHTML = `
      <div class="empty-state">
        Nessun giocatore trovato.
      </div>
    `

    return
  }


  for (
    const player
    of players
  ) {

    const row =
      document.createElement(
        'details'
      )


    row.className =
      'user-row'


    let statusClass = ''


    if (
      player.status === 'available'
    ) {

      statusClass =
        'good'

    } else if (
      player.status === 'excluded'
    ) {

      statusClass =
        'warning'
    }


    row.innerHTML = `

      <summary>

        <div class="user-summary-name">

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
              renderPlayerRole(
                player
              )
            )}
          </small>

        </div>


        <div class="user-summary-status">

          <span
            class="badge ${statusClass}"
          >
            ${escapeHtml(
              statusLabel(
                player.status
              )
            )}
          </span>


          ${
            player.quotation
              !== null
              &&
              player.quotation
              !== undefined

              ? `
                <span class="badge">
                  Q. ${escapeHtml(
                    player.quotation
                  )}
                </span>
              `

              : ''
          }

        </div>


        <span class="user-chevron">
          ⌄
        </span>

      </summary>


      <div class="user-detail">

        <div class="user-metadata">

          <div>

            <span>
              ID originale
            </span>

            <strong>
              ${escapeHtml(
                player.source_player_id
              )}
            </strong>

          </div>


          <div>

            <span>
              Squadra Serie A
            </span>

            <strong>
              ${escapeHtml(
                player.serie_a_team
                || '—'
              )}
            </strong>

          </div>


          <div>

            <span>
              Ruolo
            </span>

            <strong>
              ${escapeHtml(
                renderPlayerRole(
                  player
                )
              )}
            </strong>

          </div>


          <div>

            <span>
              Quotazione
            </span>

            <strong>
              ${escapeHtml(
                player.quotation
                ?? '—'
              )}
            </strong>

          </div>

        </div>

      </div>

    `


    playersList.appendChild(
      row
    )
  }
}


/* =========================================================
   IMPORT INFO
   ========================================================= */

function renderImportInfo() {

  const players =
    listData.players || []


  playersCount.textContent =
    players.length


  fantasyMode.textContent =
    fantasyModeLabel(
      listData
        .settings
        ?.fantasyMode
    )


  setupTab.hidden =
    !listData
      .permissions
      .isLeagueAdmin


  adminImportNote.hidden =
    !listData
      .permissions
      .isLeagueAdmin


  if (
    players.length === 0
  ) {

    importInfo.hidden =
      true

    toolbar.hidden =
      true


    playersList.innerHTML = `
      <div class="empty-state">
        Nessun listone importato.
      </div>
    `


    filteredCount.textContent =
      ''

    return
  }


  importInfo.hidden =
    false

  toolbar.hidden =
    false


  const batch =
    listData.importBatch


  if (batch) {

    const filename =
      batch.source_filename
      || 'File sorgente'


    importDetails.textContent =
      `${filename} · ${
        batch.row_count
      } righe · importato ${
        formatDateTime(
          batch.imported_at
        )
      }`

  } else {

    importDetails.textContent =
      'Listone presente.'
  }


  renderPlayers()
}


/* =========================================================
   LOAD
   ========================================================= */

async function loadList() {

  showMessage('')


  try {

    const data =
      await callApi({
        action:
          'getList'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare il listone.',
        'error'
      )

      return
    }


    listData =
      data


    leagueTitle.textContent =
      `Listone · ${data.league.name}`


    leagueSubtitle.textContent =
      fantasyModeLabel(
        data
          .settings
          ?.fantasyMode
      )


    renderImportInfo()


  } catch (error) {

    console.error(error)


    showMessage(
      error.message ||
      'Errore durante il caricamento.',
      'error'
    )
  }
}


/* =========================================================
   EVENTI
   ========================================================= */

playerSearch.addEventListener(
  'input',
  renderPlayers
)


statusFilter.addEventListener(
  'change',
  renderPlayers
)


/* =========================================================
   START
   ========================================================= */

selectedLeague =
  getSelectedLeague()


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html'

} else {

  loadList()
}
