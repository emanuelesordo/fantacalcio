const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/list-api`

const IMPORT_CHUNK_SIZE = 75


let selectedLeague = null
let listData = null


/* =========================================================
   DOM
   ========================================================= */

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


const listImportSection =
  document.getElementById(
    'list-import-section'
  )

const listImportForm =
  document.getElementById(
    'list-import-form'
  )

const listFile =
  document.getElementById(
    'list-file'
  )

const listReferenceDate =
  document.getElementById(
    'list-reference-date'
  )

const listImportButton =
  document.getElementById(
    'list-import-button'
  )

const listImportProgress =
  document.getElementById(
    'list-import-progress'
  )


const importInfo =
  document.getElementById(
    'import-info'
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

const roleFilter =
  document.getElementById(
    'player-role-filter'
  )

const playerSort =
  document.getElementById(
    'player-sort'
  )

const filteredCount =
  document.getElementById(
    'filtered-count'
  )

const playersList =
  document.getElementById(
    'players-list'
  )


const superAdminStatsSection =
  document.getElementById(
    'superadmin-stats-section'
  )

const advisoryImportForm =
  document.getElementById(
    'advisory-import-form'
  )

const advisoryLabel =
  document.getElementById(
    'advisory-label'
  )

const advisorySeason =
  document.getElementById(
    'advisory-season'
  )

const advisoryReferenceDate =
  document.getElementById(
    'advisory-reference-date'
  )

const advisoryFile =
  document.getElementById(
    'advisory-file'
  )

const advisoryImportButton =
  document.getElementById(
    'advisory-import-button'
  )

const advisoryProgress =
  document.getElementById(
    'advisory-progress'
  )

const advisoryDatasets =
  document.getElementById(
    'advisory-datasets'
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
   UTILITY GENERALI
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
    )
}


function formatDate(value) {

  if (!value) {
    return '—'
  }


  const date =
    new Date(value)


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return String(value)
  }


  return date
    .toLocaleDateString(
      'it-IT'
    )
}


function formatDateTime(value) {

  if (!value) {
    return '—'
  }


  const date =
    new Date(value)


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return String(value)
  }


  return date
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

    return '—'
  }


  return Number(value)
    .toLocaleString(
      'it-IT',
      {
        maximumFractionDigits:
          digits
      }
    )
}


function formatPercent(value) {

  if (
    value === null
    ||
    value === undefined
  ) {

    return '—'
  }


  return `${formatNumber(
    value,
    1
  )}%`
}


function fantasyModeLabel(mode) {

  if (
    mode === 'classic'
  ) {

    return 'Classic'
  }


  if (
    mode === 'mantra'
  ) {

    return 'Mantra'
  }


  return '—'
}


function normalizeKey(value) {

  return String(
    value ?? ''
  )
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(
      /[\u0300-\u036f]/g,
      ''
    )
    .replace(
      /[^a-z0-9]+/g,
      '-'
    )
    .replace(
      /^-+|-+$/g,
      ''
    )
}


function normalizeHeader(value) {

  return String(
    value ?? ''
  )
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(
      /[\u0300-\u036f]/g,
      ''
    )
    .replace(
      /[^a-z0-9]/g,
      ''
    )
}


function nullableNumber(value) {

  if (
    value === null
    ||
    value === undefined
    ||
    value === ''
  ) {

    return null
  }


  if (
    typeof value === 'number'
  ) {

    return Number.isFinite(value)
      ? value
      : null
  }


  let text =
    String(value)
      .trim()
      .replace(
        /%$/,
        ''
      )


  if (!text) {
    return null
  }


  if (
    text.includes(',')
    &&
    !text.includes('.')
  ) {

    text =
      text.replace(
        ',',
        '.'
      )
  }


  const number =
    Number(text)


  return Number.isFinite(number)
    ? number
    : null
}


function nullableInteger(value) {

  const number =
    nullableNumber(value)


  if (number === null) {
    return null
  }


  return Math.round(number)
}


function toBoolean(value) {

  if (
    value === true
    ||
    value === 1
  ) {

    return true
  }


  if (
    value === false
    ||
    value === 0
    ||
    value === null
    ||
    value === undefined
    ||
    value === ''
  ) {

    return false
  }


  const text =
    String(value)
      .trim()
      .toLowerCase()


  return [
    'true',
    '1',
    'yes',
    'si',
    'sì'
  ]
    .includes(text)
}


function splitMantraRoles(value) {

  if (!value) {
    return []
  }


  return String(value)
    .split(',')
    .map(
      role =>
        role.trim()
    )
    .filter(Boolean)
}


function hasValue(value) {

  return !(
    value === null
    ||
    value === undefined
    ||
    value === ''
    ||
    value === 0
  )
}


function getTodayLocal() {

  const now =
    new Date()


  const year =
    now.getFullYear()

  const month =
    String(
      now.getMonth() + 1
    )
      .padStart(
        2,
        '0'
      )

  const day =
    String(
      now.getDate()
    )
      .padStart(
        2,
        '0'
      )


  return `${year}-${month}-${day}`
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
   LETTURA XLSX / CSV
   ========================================================= */

async function readSpreadsheetFile(
  file,
  preferAllSheet = true
) {

  if (
    typeof XLSX === 'undefined'
  ) {

    throw new Error(
      'Libreria XLSX non caricata.'
    )
  }


  const extension =
    file.name
      .split('.')
      .pop()
      ?.toLowerCase()
      || ''


  const buffer =
    await file.arrayBuffer()


  const workbook =
    XLSX.read(
      buffer,
      {
        type:
          'array',

        cellDates:
          false
      }
    )


  if (
    !workbook.SheetNames
      ?.length
  ) {

    throw new Error(
      'Il file non contiene fogli leggibili.'
    )
  }


  let sheetName = null


  if (
    preferAllSheet
    &&
    workbook.SheetNames
      .includes('ALL')
  ) {

    sheetName =
      'ALL'

  } else {

    sheetName =
      workbook.SheetNames
        .find(
          name =>
            name
              .trim()
              .toLowerCase()
            !== 'info'
        )
      ||
      workbook.SheetNames[0]
  }


  const sheet =
    workbook.Sheets[
      sheetName
    ]


  const rows =
    XLSX.utils
      .sheet_to_json(
        sheet,
        {
          defval:
            null,

          raw:
            true
        }
      )


  if (
    rows.length === 0
  ) {

    throw new Error(
      'Il foglio selezionato non contiene righe.'
    )
  }


  const columns =
    Object.keys(
      rows[0]
    )


  return {

    rows,

    columns,

    sheetName,

    format:
      extension || 'xlsx'
  }
}


/* =========================================================
   MAPPATURA FANTACULO
   ========================================================= */

function findOriginalId(row) {

  const possibleKeys = [
    'id',
    'playerId',
    'playerID',
    'player_id',
    'idPlayer',
    'idCalciatore',
    'idGiocatore'
  ]


  for (
    const key
    of possibleKeys
  ) {

    if (
      row[key] !== null
      &&
      row[key] !== undefined
      &&
      row[key] !== ''
    ) {

      return String(
        row[key]
      )
    }
  }


  return null
}


function normalizeFantaculoRow(
  row,
  rowIndex
) {

  const name =
    String(
      row.name ?? ''
    )
      .trim()


  const team =
    String(
      row.team ?? ''
    )
      .trim()


  const teamSlug =
    String(
      row.teamSlug
      ?? team
    )
      .trim()


  const classicRole =
    String(
      row.role ?? ''
    )
      .trim()


  const mantraRoles =
    splitMantraRoles(
      row.roleMantra
    )


  const originalId =
    findOriginalId(row)


  const sourcePlayerId =
    originalId
    ||
    [
      'fantaculo',
      normalizeKey(name),
      normalizeKey(teamSlug),
      normalizeKey(
        row.roleMantra
        || classicRole
      ),
      rowIndex
    ]
      .join(':')


  return {

    rowIndex,

    sourcePlayerId,


    normalized: {

      name,

      team,

      classic_role:
        [
          'P',
          'D',
          'C',
          'A'
        ]
          .includes(
            classicRole
          )
          ? classicRole
          : null,

      mantra_roles:
        mantraRoles,


      pma:
        nullableNumber(
          row.pma
        ),

      pfc:
        nullableNumber(
          row.pfc
        ),

      pfc_pma_delta:
        nullableNumber(
          row.dpfcpma
        ),

      pma_range:
        row.pmaRange
        ?? null,

      pfc_range:
        row.pfcRange
        ?? null,

      slot:
        nullableInteger(
          row.slot
        ),


      expected_titolarity:
        nullableNumber(
          row.expectedTitolarita
        ),

      expected_fantasy_avg:
        nullableNumber(
          row.expectedFantamedia
        ),


      penalty_probability:
        nullableNumber(
          row.penaltyProbability
        ),

      free_kick_probability:
        nullableNumber(
          row.freeKickProbability
        ),

      unavailable_until_round:
        nullableInteger(
          row.unavailableUntilRound
        ),


      tier_classic:
        row.fasciaFc
        ?? null,

      tier_mantra:
        row.fasciaFr
        ?? null,


      uncertain_return:
        toBoolean(
          row.rientroIncerto
        ),

      new_arrival:
        toBoolean(
          row.newArrival
        ),

      market_flag:
        Boolean(
          String(
            row.calciomercato
            ?? ''
          )
            .trim()
        ),


      source_updated_at:
        row.updatedAt
        ?? null,


      last_three_year_titolarity:
        nullableNumber(
          row.lastThreeYearTitolarity
        ),

      last_five_year_base_rating:
        nullableNumber(
          row.lastFiveYearVotoBase
        ),

      last_five_year_fantasy_avg:
        nullableNumber(
          row.lastFiveYearFantamedia
        ),

      last_five_year_titolarity:
        nullableNumber(
          row.lastFiveYearTitolarity
        ),


      last_year_base_rating:
        nullableNumber(
          row.lastYearVotoBase
        ),

      last_year_fantasy_avg:
        nullableNumber(
          row.lastYearFantamedia
        ),

      last_year_titolarity:
        nullableNumber(
          row.lastYearTitolarity
        ),


      last_five_matches_base_rating:
        nullableNumber(
          row.lastFiveMatchesVotoBase
        ),

      last_five_matches_fantasy_avg:
        nullableNumber(
          row.lastFiveMatchesFantamedia
        ),

      last_five_matches_titolarity:
        nullableNumber(
          row.lastFiveMatchesTitolarity
        ),


      current_season_base_rating:
        nullableNumber(
          row.currentSeasonVotoBase
        ),

      current_season_fantasy_avg:
        nullableNumber(
          row.currentSeasonFantamedia
        ),

      current_season_titolarity:
        nullableNumber(
          row.currentSeasonTitolarity
        )
    },


    /*
     * Qui conserviamo TUTTE le colonne
     * presenti nel file originale.
     */
    raw:
      row
  }
}


/* =========================================================
   IMPORT LISTONE
   ========================================================= */

async function importFantaculoList(
  file,
  referenceDate
) {

  const parsed =
    await readSpreadsheetFile(
      file,
      true
    )


  const requiredColumns = [
    'name',
    'team',
    'role'
  ]


  const missing =
    requiredColumns
      .filter(
        column =>
          !parsed.columns
            .includes(column)
      )


  if (
    missing.length > 0
  ) {

    throw new Error(
      `Il file non sembra un listone Fantaculo. Colonne mancanti: ${
        missing.join(', ')
      }.`
    )
  }


  const normalizedRows =
    parsed.rows
      .map(
        (
          row,
          index
        ) =>
          normalizeFantaculoRow(
            row,
            index + 1
          )
      )
      .filter(
        item =>
          item.normalized.name
      )


  if (
    normalizedRows.length === 0
  ) {

    throw new Error(
      'Nessun giocatore valido trovato.'
    )
  }


  listImportProgress.textContent =
    `Preparazione di ${
      normalizedRows.length
    } giocatori...`


  const begin =
    await callApi({

      action:
        'beginListImport',

      sourceFilename:
        file.name,

      sourceFormat:
        parsed.format,

      sourceColumns:
        parsed.columns,

      referenceDate
    })


  if (!begin?.ok) {

    throw new Error(
      begin?.error
      ||
      'Impossibile iniziare l’import.'
    )
  }


  const batchId =
    begin.batchId


  for (
    let start = 0;
    start < normalizedRows.length;
    start += IMPORT_CHUNK_SIZE
  ) {

    const end =
      Math.min(
        start + IMPORT_CHUNK_SIZE,
        normalizedRows.length
      )


    const chunk =
      normalizedRows
        .slice(
          start,
          end
        )


    listImportProgress.textContent =
      `Importazione ${
        end
      } / ${
        normalizedRows.length
      }...`


    const append =
      await callApi({

        action:
          'appendListImport',

        batchId,

        rows:
          chunk
      })


    if (!append?.ok) {

      throw new Error(
        append?.error
        ||
        'Errore durante il caricamento del listone.'
      )
    }
  }


  listImportProgress.textContent =
    'Finalizzazione listone...'


  const finish =
    await callApi({

      action:
        'finishListImport',

      batchId
    })


  if (!finish?.ok) {

    throw new Error(
      finish?.error
      ||
      'Impossibile finalizzare il listone.'
    )
  }


  return finish.rowCount
}


listImportForm
  .addEventListener(
    'submit',
    async event => {

      event.preventDefault()


      showMessage('')


      const file =
        listFile.files?.[0]


      if (!file) {

        showMessage(
          'Seleziona un file XLSX o CSV.',
          'error'
        )

        return
      }


      if (
        !listReferenceDate.value
      ) {

        showMessage(
          'Indica la data di riferimento.',
          'error'
        )

        return
      }


      listImportButton.disabled =
        true


      const originalText =
        listImportButton.textContent


      listImportButton.textContent =
        'Importazione...'


      try {

        const rowCount =
          await importFantaculoList(
            file,
            listReferenceDate.value
          )


        listImportProgress.textContent =
          `Import completato: ${
            rowCount
          } giocatori.`


        showMessage(
          'Listone aggiornato correttamente.',
          'success'
        )


        listFile.value =
          ''


        await loadList()


      } catch (error) {

        console.error(error)


        listImportProgress.textContent =
          ''


        showMessage(
          error.message
          ||
          'Errore durante l’importazione.',
          'error'
        )

      } finally {

        listImportButton.disabled =
          false


        listImportButton.textContent =
          originalText
      }
    }
  )


/* =========================================================
   RUOLI E FILTRI
   ========================================================= */

function configureRoleFilter() {

  const mode =
    listData
      ?.settings
      ?.fantasyMode


  if (
    mode === 'mantra'
  ) {

    const roles = [
      'Por',
      'B',
      'Dc',
      'Dd',
      'Ds',
      'E',
      'W',
      'M',
      'C',
      'T',
      'A',
      'Pc'
    ]


    roleFilter.innerHTML = `
      <option value="all">
        Tutti i ruoli
      </option>

      ${
        roles
          .map(
            role => `
              <option value="${role}">
                ${role}
              </option>
            `
          )
          .join('')
      }
    `

  } else {

    roleFilter.innerHTML = `
      <option value="all">
        Tutti i ruoli
      </option>

      <option value="P">P</option>
      <option value="D">D</option>
      <option value="C">C</option>
      <option value="A">A</option>
    `
  }
}


function getPlayerRole(player) {

  const mode =
    listData
      ?.settings
      ?.fantasyMode


  if (
    mode === 'mantra'
  ) {

    return (
      player.mantra_roles
      || []
    )
      .join(', ')
      || '—'
  }


  return player.classic_role
    || '—'
}


function getPlayerTier(player) {

  const mode =
    listData
      ?.settings
      ?.fantasyMode


  if (
    mode === 'mantra'
  ) {

    return player.tier_mantra
      || '—'
  }


  return player.tier_classic
    || '—'
}


function playerMatchesRole(
  player,
  role
) {

  if (
    role === 'all'
  ) {

    return true
  }


  const mode =
    listData
      ?.settings
      ?.fantasyMode


  if (
    mode === 'mantra'
  ) {

    return (
      player.mantra_roles
      || []
    )
      .includes(role)
  }


  return player.classic_role
    === role
}


/* =========================================================
   ORDINAMENTO
   ========================================================= */

function numericSortValue(
  value,
  fallback = -Infinity
) {

  const number =
    Number(value)


  return Number.isFinite(number)
    ? number
    : fallback
}


function sortPlayers(players) {

  const mode =
    playerSort.value


  const result =
    [...players]


  if (
    mode === 'pfc-desc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          b.pfc
        )
        -
        numericSortValue(
          a.pfc
        )
    )

  } else if (
    mode === 'pma-desc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          b.pma
        )
        -
        numericSortValue(
          a.pma
        )
    )

  } else if (
    mode === 'delta-desc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          b.pfc_pma_delta
        )
        -
        numericSortValue(
          a.pfc_pma_delta
        )
    )

  } else if (
    mode === 'fm-desc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          b.expected_fantasy_avg
        )
        -
        numericSortValue(
          a.expected_fantasy_avg
        )
    )

  } else if (
    mode === 'tit-desc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          b.expected_titolarity
        )
        -
        numericSortValue(
          a.expected_titolarity
        )
    )

  } else if (
    mode === 'slot-asc'
  ) {

    result.sort(
      (a, b) =>
        numericSortValue(
          a.slot,
          Infinity
        )
        -
        numericSortValue(
          b.slot,
          Infinity
        )
    )

  } else {

    result.sort(
      (a, b) =>
        String(
          a.name
        )
          .localeCompare(
            String(
              b.name
            ),
            'it'
          )
    )
  }


  return result
}


/* =========================================================
   FILTRO LISTA
   ========================================================= */

function getFilteredPlayers() {

  const players =
    listData?.players
    || []


  const search =
    playerSearch
      .value
      .trim()
      .toLowerCase()


  const role =
    roleFilter.value


  const filtered =
    players
      .filter(
        player => {

          if (
            !playerMatchesRole(
              player,
              role
            )
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
              ...(player.mantra_roles || []),
              player.tier_classic,
              player.tier_mantra
            ]
              .filter(Boolean)
              .join(' ')
              .toLowerCase()


          return haystack
            .includes(search)
        }
      )


  return sortPlayers(
    filtered
  )
}


/* =========================================================
   BADGE GIOCATORE
   ========================================================= */

function deltaBadge(player) {

  if (
    player.pfc_pma_delta
    === null
    ||
    player.pfc_pma_delta
    === undefined
  ) {

    return ''
  }


  const delta =
    Number(
      player.pfc_pma_delta
    )


  const sign =
    delta > 0
      ? '+'
      : ''


  const cssClass =
    delta > 0
      ? 'good'
      : delta < 0
        ? 'warning'
        : ''


  return `
    <span class="badge ${cssClass}">
      Δ ${sign}${escapeHtml(
        formatNumber(
          delta,
          0
        )
      )}
    </span>
  `
}


/* =========================================================
   RENDER GIOCATORI
   ========================================================= */

function renderPlayers() {

  const players =
    getFilteredPlayers()


  playersList.innerHTML =
    ''


  filteredCount.textContent =
    `${players.length} di ${
      listData?.players?.length
      || 0
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


    const tier =
      getPlayerTier(
        player
      )


    const lastYearVisible =
      hasValue(
        player.last_year_fantasy_avg
      )
      ||
      hasValue(
        player.last_year_titolarity
      )
      ||
      hasValue(
        player.last_year_base_rating
      )


    const lastFiveVisible =
      hasValue(
        player.last_five_matches_fantasy_avg
      )
      ||
      hasValue(
        player.last_five_matches_titolarity
      )
      ||
      hasValue(
        player.last_five_matches_base_rating
      )


    const currentSeasonVisible =
      hasValue(
        player.current_season_fantasy_avg
      )
      ||
      hasValue(
        player.current_season_titolarity
      )
      ||
      hasValue(
        player.current_season_base_rating
      )


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
              getPlayerRole(
                player
              )
            )}
          </small>

        </div>


        <div class="user-summary-status">

          ${
            player.pfc_range

              ? `
                <span class="badge admin">
                  PFC ${
                    escapeHtml(
                      player.pfc_range
                    )
                  }
                </span>
              `

              : ''
          }


          ${
            player.pma_range

              ? `
                <span class="badge">
                  PMA ${
                    escapeHtml(
                      player.pma_range
                    )
                  }
                </span>
              `

              : ''
          }


          ${deltaBadge(player)}


          ${
            player.slot

              ? `
                <span class="badge">
                  Slot ${
                    escapeHtml(
                      player.slot
                    )
                  }
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


        <div class="stats-grid">

          <div class="stat-card">

            <span class="stat-label">
              Expected FM
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatNumber(
                  player.expected_fantasy_avg,
                  2
                )
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              Titolarità attesa
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatPercent(
                  player.expected_titolarity
                )
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              PFC
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatNumber(
                  player.pfc,
                  1
                )
              )}
            </span>

          </div>


          <div class="stat-card">

            <span class="stat-label">
              PMA
            </span>

            <span class="stat-value">
              ${escapeHtml(
                formatNumber(
                  player.pma,
                  1
                )
              )}
            </span>

          </div>

        </div>


        <div class="divider"></div>


        <p>
          Fascia:
          <strong>
            ${escapeHtml(tier)}
          </strong>
        </p>


        ${
          hasValue(
            player.penalty_probability
          )

            ? `
              <span class="badge good">
                Rigori ${
                  escapeHtml(
                    formatPercent(
                      player.penalty_probability
                    )
                  )
                }
              </span>
            `

            : ''
        }


        ${
          hasValue(
            player.free_kick_probability
          )

            ? `
              <span class="badge">
                Punizioni ${
                  escapeHtml(
                    formatPercent(
                      player.free_kick_probability
                    )
                  )
                }
              </span>
            `

            : ''
        }


        ${
          player.new_arrival

            ? `
              <span class="badge">
                NUOVO ARRIVO
              </span>
            `

            : ''
        }


        ${
          player.market_flag

            ? `
              <span class="badge warning">
                MERCATO DA MONITORARE
              </span>
            `

            : ''
        }


        ${
          player.uncertain_return

            ? `
              <span class="badge warning">
                RIENTRO INCERTO
              </span>
            `

            : ''
        }


        ${
          hasValue(
            player.unavailable_until_round
          )

            ? `
              <p class="setting-help">
                Indisponibile indicativamente
                fino alla giornata
                <strong>
                  ${
                    escapeHtml(
                      player.unavailable_until_round
                    )
                  }
                </strong>.
              </p>
            `

            : ''
        }


        ${
          lastYearVisible

            ? `
              <div class="divider"></div>

              <h3>
                Ultima stagione
              </h3>

              <p>
                Voto base:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.last_year_base_rating,
                        2
                      )
                    )
                  }
                </strong>
                · Fantamedia:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.last_year_fantasy_avg,
                        2
                      )
                    )
                  }
                </strong>
                · Titolarità:
                <strong>
                  ${
                    escapeHtml(
                      formatPercent(
                        player.last_year_titolarity
                      )
                    )
                  }
                </strong>
              </p>
            `

            : ''
        }


        ${
          lastFiveVisible

            ? `
              <div class="divider"></div>

              <h3>
                Ultime 5 partite
              </h3>

              <p>
                Voto base:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.last_five_matches_base_rating,
                        2
                      )
                    )
                  }
                </strong>
                · Fantamedia:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.last_five_matches_fantasy_avg,
                        2
                      )
                    )
                  }
                </strong>
                · Titolarità:
                <strong>
                  ${
                    escapeHtml(
                      formatPercent(
                        player.last_five_matches_titolarity
                      )
                    )
                  }
                </strong>
              </p>
            `

            : ''
        }


        ${
          currentSeasonVisible

            ? `
              <div class="divider"></div>

              <h3>
                Stagione corrente
              </h3>

              <p>
                Voto base:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.current_season_base_rating,
                        2
                      )
                    )
                  }
                </strong>
                · Fantamedia:
                <strong>
                  ${
                    escapeHtml(
                      formatNumber(
                        player.current_season_fantasy_avg,
                        2
                      )
                    )
                  }
                </strong>
                · Titolarità:
                <strong>
                  ${
                    escapeHtml(
                      formatPercent(
                        player.current_season_titolarity
                      )
                    )
                  }
                </strong>
              </p>
            `

            : ''
        }


        ${
          player.source_updated_at

            ? `
              <p class="setting-help">
                Dati aggiornati:
                ${
                  escapeHtml(
                    formatDateTime(
                      player.source_updated_at
                    )
                  )
                }
              </p>
            `

            : ''
        }

      </div>

    `


    playersList.appendChild(
      row
    )
  }
}


/* =========================================================
   INFO IMPORT
   ========================================================= */

function renderImportInfo() {

  const players =
    listData.players
    || []


  setupTab.hidden =
    !listData
      .permissions
      .isLeagueAdmin


  listImportSection.hidden =
    !listData
      .permissions
      .isLeagueAdmin


  superAdminStatsSection.hidden =
    !listData
      .permissions
      .isSuperAdmin


  playersCount.textContent =
    players.length


  fantasyMode.textContent =
    fantasyModeLabel(
      listData
        .settings
        ?.fantasyMode
    )


  configureRoleFilter()


  if (
    players.length === 0
  ) {

    importInfo.hidden =
      true


    toolbar.hidden =
      true


    filteredCount.textContent =
      ''


    playersList.innerHTML = `
      <div class="empty-state">
        Nessun listone importato.
      </div>
    `


    return
  }


  importInfo.hidden =
    false


  toolbar.hidden =
    false


  const batch =
    listData.importBatch


  if (batch) {

    importDetails.textContent =
      [
        batch.source_filename
        || 'Listone',

        batch.reference_date
          ? `riferimento ${
              formatDate(
                batch.reference_date
              )
            }`
          : null,

        `${batch.row_count} giocatori`,

        batch.completed_at
          ? `importato ${
              formatDateTime(
                batch.completed_at
              )
            }`
          : null
      ]
        .filter(Boolean)
        .join(' · ')

  } else {

    importDetails.textContent =
      'Listone presente.'
  }


  renderPlayers()
}


/* =========================================================
   DATASET SUPER ADMIN
   ========================================================= */

function renderAdvisoryDatasets() {

  advisoryDatasets.innerHTML =
    ''


  const datasets =
    listData
      ?.advisoryDatasets
    || []


  if (
    datasets.length === 0
  ) {

    advisoryDatasets.innerHTML = `
      <div class="empty-state">
        Nessun dataset aggiuntivo importato.
      </div>
    `

    return
  }


  for (
    const dataset
    of datasets
  ) {

    const row =
      document.createElement(
        'div'
      )


    row.className =
      'list-row'


    row.innerHTML = `

      <div class="list-row-main">

        <div class="list-row-title">

          <strong>
            ${escapeHtml(
              dataset.label
            )}
          </strong>

          <small>
            ${
              escapeHtml(
                dataset.season
                || 'Stagione non indicata'
              )
            }
            ·
            ${
              escapeHtml(
                dataset.row_count
              )
            }
            righe
          </small>

        </div>


        <span class="badge good">
          ATTIVO
        </span>

      </div>


      <p class="setting-help">
        ${
          dataset.reference_date
            ? `Riferimento ${
                escapeHtml(
                  formatDate(
                    dataset.reference_date
                  )
                )
              } · `
            : ''
        }

        ${
          escapeHtml(
            dataset.source_filename
            || 'File'
          )
        }
      </p>

    `


    advisoryDatasets.appendChild(
      row
    )
  }
}


/* =========================================================
   RICONOSCIMENTO COLONNE DATASET EXTRA
   ========================================================= */

function findColumnByAliases(
  columns,
  aliases
) {

  const aliasSet =
    new Set(
      aliases.map(
        normalizeHeader
      )
    )


  return columns.find(
    column =>
      aliasSet.has(
        normalizeHeader(
          column
        )
      )
  )
  || null
}


function getNumericMetrics(
  row,
  excludedColumns = []
) {

  const result = {}


  const excluded =
    new Set(
      excludedColumns
        .filter(Boolean)
    )


  for (
    const [
      key,
      value
    ]
    of Object.entries(row)
  ) {

    if (
      excluded.has(key)
    ) {

      continue
    }


    const number =
      nullableNumber(
        value
      )


    if (
      number !== null
    ) {

      result[key] =
        number
    }
  }


  return result
}


/* =========================================================
   IMPORT DATASET SUPER ADMIN
   ========================================================= */

async function importAdvisoryStats(
  file,
  label,
  season,
  referenceDate
) {

  const parsed =
    await readSpreadsheetFile(
      file,
      false
    )


  const nameColumn =
    findColumnByAliases(
      parsed.columns,
      [
        'name',
        'nome',
        'player',
        'player name',
        'giocatore',
        'calciatore',
        'nome giocatore',
        'nome calciatore'
      ]
    )


  if (!nameColumn) {

    throw new Error(
      'Non riesco a individuare la colonna con il nome del giocatore.'
    )
  }


  const teamColumn =
    findColumnByAliases(
      parsed.columns,
      [
        'team',
        'squadra',
        'club',
        'societa',
        'società',
        'team name'
      ]
    )


  const normalizedRows =
    parsed.rows
      .map(
        row => ({

          playerName:
            String(
              row[nameColumn]
              ?? ''
            )
              .trim(),

          team:
            teamColumn
              ? String(
                  row[teamColumn]
                  ?? ''
                )
                  .trim()
              : '',

          numericMetrics:
            getNumericMetrics(
              row,
              [
                nameColumn,
                teamColumn
              ]
            ),

          raw:
            row
        })
      )
      .filter(
        row =>
          row.playerName
      )


  if (
    normalizedRows.length === 0
  ) {

    throw new Error(
      'Il dataset non contiene giocatori validi.'
    )
  }


  advisoryProgress.textContent =
    `Preparazione di ${
      normalizedRows.length
    } righe...`


  const begin =
    await callApi({

      action:
        'beginAdvisoryStatsImport',

      label,

      season:
        season || null,

      referenceDate:
        referenceDate
        || null,

      sourceFilename:
        file.name,

      sourceFormat:
        parsed.format,

      sourceColumns:
        parsed.columns
    })


  if (!begin?.ok) {

    throw new Error(
      begin?.error
      ||
      'Impossibile iniziare l’import.'
    )
  }


  const datasetId =
    begin.datasetId


  let imported = 0


  for (
    let start = 0;
    start < normalizedRows.length;
    start += IMPORT_CHUNK_SIZE
  ) {

    const end =
      Math.min(
        start + IMPORT_CHUNK_SIZE,
        normalizedRows.length
      )


    const chunk =
      normalizedRows.slice(
        start,
        end
      )


    advisoryProgress.textContent =
      `Importazione ${
        end
      } / ${
        normalizedRows.length
      }...`


    const append =
      await callApi({

        action:
          'appendAdvisoryStats',

        datasetId,

        rows:
          chunk
      })


    if (!append?.ok) {

      throw new Error(
        append?.error
        ||
        'Errore durante l’importazione del dataset.'
      )
    }


    imported +=
      append.inserted
      || 0
  }


  advisoryProgress.textContent =
    'Finalizzazione dataset...'


  const finish =
    await callApi({

      action:
        'finishAdvisoryStatsImport',

      datasetId
    })


  if (!finish?.ok) {

    throw new Error(
      finish?.error
      ||
      'Impossibile finalizzare il dataset.'
    )
  }


  return imported
}


advisoryImportForm
  .addEventListener(
    'submit',
    async event => {

      event.preventDefault()


      showMessage('')


      const file =
        advisoryFile
          .files?.[0]


      const label =
        advisoryLabel
          .value
          .trim()


      if (!file) {

        showMessage(
          'Seleziona un file XLSX o CSV.',
          'error'
        )

        return
      }


      if (
        label.length < 2
      ) {

        showMessage(
          'Inserisci un nome per il dataset.',
          'error'
        )

        return
      }


      advisoryImportButton.disabled =
        true


      const originalText =
        advisoryImportButton.textContent


      advisoryImportButton.textContent =
        'Importazione...'


      try {

        const count =
          await importAdvisoryStats(

            file,

            label,

            advisorySeason
              .value
              .trim(),

            advisoryReferenceDate
              .value
        )


        advisoryProgress.textContent =
          `Dataset importato: ${
            count
          } righe.`


        showMessage(
          'Statistiche aggiuntive importate.',
          'success'
        )


        advisoryFile.value =
          ''


        advisoryLabel.value =
          ''


        await loadList()


      } catch (error) {

        console.error(error)


        advisoryProgress.textContent =
          ''


        showMessage(
          error.message
          ||
          'Errore durante l’importazione delle statistiche.',
          'error'
        )

      } finally {

        advisoryImportButton.disabled =
          false


        advisoryImportButton.textContent =
          originalText
      }
    }
  )


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
        data?.error
        ||
        'Impossibile caricare il listone.',
        'error'
      )

      return
    }


    listData =
      data


    leagueTitle.textContent =
      `Listone · ${
        data.league.name
      }`


    leagueSubtitle.textContent =
      fantasyModeLabel(
        data
          .settings
          ?.fantasyMode
      )


    renderImportInfo()


    if (
      data.permissions
        .isSuperAdmin
    ) {

      renderAdvisoryDatasets()
    }


  } catch (error) {

    console.error(error)


    showMessage(
      error.message
      ||
      'Errore durante il caricamento.',
      'error'
    )
  }
}


/* =========================================================
   EVENTI FILTRI
   ========================================================= */

playerSearch
  .addEventListener(
    'input',
    renderPlayers
  )


roleFilter
  .addEventListener(
    'change',
    renderPlayers
  )


playerSort
  .addEventListener(
    'change',
    renderPlayers
  )


/* =========================================================
   START
   ========================================================= */

listReferenceDate.value =
  getTodayLocal()


advisoryReferenceDate.value =
  getTodayLocal()


selectedLeague =
  getSelectedLeague()


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html'

} else {

  loadList()
}
