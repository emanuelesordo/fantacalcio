const SUPABASE_URL = 'https://yyklmhzjxzkvycmxkegx.supabase.co';
const API_URL = `${SUPABASE_URL}/functions/v1/list-api`;
const NATIONALITY_API_URL = `${SUPABASE_URL}/functions/v1/nationality-api`;
const IMPORT_CHUNK_SIZE = 75;

let selectedLeague = null;
let listData = null;
let activeRole = 'all';
let sortState = { key: 'name', direction: 'asc' };

const $ = id => document.getElementById(id);

const leagueTitle = $('league-title');
const leagueSubtitle = $('league-subtitle');
const message = $('page-message');
const setupTab = $('setup-tab');

const listImportSection = $('list-import-section');
const listImportForm = $('list-import-form');
const listFile = $('list-file');
const listReferenceDate = $('list-reference-date');
const listImportButton = $('list-import-button');
const listImportProgress = $('list-import-progress');

const importInfo = $('import-info');
const playersCount = $('players-count');
const fantasyMode = $('fantasy-mode');
const importDetails = $('import-details');

const roleFilterBar = $('role-filter-bar');
const playerFilterGrid = $('player-filter-grid');
const playerSearch = $('player-search');
const teamFilter = $('player-team-filter');
const slotFilter = $('player-slot-filter');
const flagFilter = $('player-flag-filter');
const filterResetButton = $('player-filter-reset');
const playerCountLine = $('player-count-line');
const filteredCount = $('filtered-count');
const playerTableWrap = $('player-table-wrap');
const playersTableBody = $('players-table-body');
const playersEmpty = $('players-empty');
const sortButtons = [...document.querySelectorAll('.player-sort-button')];

const superAdminNationalitySection = $('superadmin-nationality-section');
const nationalityEnrichButton = $('nationality-enrich-button');
const nationalityProgress = $('nationality-progress');

const superAdminStatsSection = $('superadmin-stats-section');
const advisoryImportForm = $('advisory-import-form');
const advisoryLabel = $('advisory-label');
const advisorySeason = $('advisory-season');
const advisoryReferenceDate = $('advisory-reference-date');
const advisoryFile = $('advisory-file');
const advisoryImportButton = $('advisory-import-button');
const advisoryProgress = $('advisory-progress');
const advisoryDatasets = $('advisory-datasets');

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

function showMessage(text = '', type = '') {
  message.textContent = text;
  message.className = `message ${type}`;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function formatDate(value) {
  if (!value) return '—';

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString('it-IT');
}

function formatDateTime(value) {
  if (!value) return '—';

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleString(
        'it-IT',
        {
          dateStyle: 'short',
          timeStyle: 'short'
        }
      );
}

function formatNumber(value, digits = 1) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return '—';
  }

  return Number(value).toLocaleString(
    'it-IT',
    {
      maximumFractionDigits: digits
    }
  );
}

function formatPercent(value) {
  return value === null || value === undefined
    ? '—'
    : `${formatNumber(value, 1)}%`;
}

function fantasyModeLabel(mode) {
  return mode === 'classic'
    ? 'Classic'
    : mode === 'mantra'
      ? 'Mantra'
      : '—';
}

function normalizeKey(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function normalizeHeader(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]/g, '');
}

function nullableNumber(value) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return null;
  }

  if (typeof value === 'number') {
    return Number.isFinite(value)
      ? value
      : null;
  }

  let text = String(value)
    .trim()
    .replace(/%$/, '');

  if (!text) return null;

  if (
    text.includes(',') &&
    !text.includes('.')
  ) {
    text = text.replace(',', '.');
  }

  const n = Number(text);

  return Number.isFinite(n)
    ? n
    : null;
}

function nullableInteger(value) {
  const n = nullableNumber(value);

  return n === null
    ? null
    : Math.round(n);
}

function toBoolean(value) {
  if (
    value === true ||
    value === 1
  ) {
    return true;
  }

  if (
    value === false ||
    value === 0 ||
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return false;
  }

  return [
    'true',
    '1',
    'yes',
    'si',
    'sì'
  ].includes(
    String(value)
      .trim()
      .toLowerCase()
  );
}

function splitMantraRoles(value) {
  return value
    ? String(value)
        .split(',')
        .map(v => v.trim())
        .filter(Boolean)
    : [];
}

function hasValue(value) {
  return !(
    value === null ||
    value === undefined ||
    value === '' ||
    value === 0
  );
}

function getTodayLocal() {
  const now = new Date();

  const y = now.getFullYear();

  const m = String(
    now.getMonth() + 1
  ).padStart(2, '0');

  const d = String(
    now.getDate()
  ).padStart(2, '0');

  return `${y}-${m}-${d}`;
}

function countryCodeToEmoji(code) {
  const iso = String(code || '')
    .trim()
    .toUpperCase();

  if (!/^[A-Z]{2}$/.test(iso)) {
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

async function callEndpoint(url, body) {
  const session = getSession();

  if (!session?.token) {
    window.location.href = 'index.html';
    return null;
  }

  let response;

  try {
    response = await fetch(
      url,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json'
        },

        body: JSON.stringify({
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
    data = await response.json();
  } catch {
    throw new Error(
      'Risposta non valida dal server.'
    );
  }

  if (response.status === 401) {
    window.location.href =
      'index.html';

    return null;
  }

  return data;
}

const callApi = body =>
  callEndpoint(
    API_URL,
    body
  );

const callNationalityApi = body =>
  callEndpoint(
    NATIONALITY_API_URL,
    body
  );

async function readSpreadsheetFile(
  file,
  preferAllSheet = true
) {
  if (
    typeof XLSX === 'undefined'
  ) {
    throw new Error(
      'Libreria XLSX non caricata.'
    );
  }

  const extension =
    file.name
      .split('.')
      .pop()
      ?.toLowerCase() || '';

  const workbook =
    XLSX.read(
      await file.arrayBuffer(),
      {
        type: 'array',
        cellDates: false
      }
    );

  if (!workbook.SheetNames?.length) {
    throw new Error(
      'Il file non contiene fogli leggibili.'
    );
  }

  let sheetName;

  if (
    preferAllSheet &&
    workbook.SheetNames.includes('ALL')
  ) {
    sheetName = 'ALL';
  } else {
    sheetName =
      workbook.SheetNames.find(
        name =>
          name
            .trim()
            .toLowerCase() !== 'info'
      ) ||
      workbook.SheetNames[0];
  }

  const rows =
    XLSX.utils.sheet_to_json(
      workbook.Sheets[sheetName],
      {
        defval: null,
        raw: true
      }
    );

  if (!rows.length) {
    throw new Error(
      'Il foglio selezionato non contiene righe.'
    );
  }

  return {
    rows,
    columns:
      Object.keys(rows[0]),
    sheetName,
    format:
      extension || 'xlsx'
  };
}

function findOriginalId(row) {
  for (
    const key
    of [
      'id',
      'playerId',
      'playerID',
      'player_id',
      'idPlayer',
      'idCalciatore',
      'idGiocatore'
    ]
  ) {
    if (
      row[key] !== null &&
      row[key] !== undefined &&
      row[key] !== ''
    ) {
      return String(row[key]);
    }
  }

  return null;
}

function normalizeFantaculoRow(
  row,
  rowIndex
) {
  const name =
    String(
      row.name ?? ''
    ).trim();

  const team =
    String(
      row.team ?? ''
    ).trim();

  const teamSlug =
    String(
      row.teamSlug ?? team
    ).trim();

  const classicRole =
    String(
      row.role ?? ''
    ).trim();

  const mantraRoles =
    splitMantraRoles(
      row.roleMantra
    );

  const originalId =
    findOriginalId(row);

  const sourcePlayerId =
    originalId ||
    [
      'fantaculo',
      normalizeKey(name),
      normalizeKey(teamSlug),
      normalizeKey(
        row.roleMantra ||
        classicRole
      ),
      rowIndex
    ].join(':');

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
        ].includes(classicRole)
          ? classicRole
          : null,

      mantra_roles:
        mantraRoles,

      pma:
        nullableNumber(row.pma),

      pfc:
        nullableNumber(row.pfc),

      pfc_pma_delta:
        nullableNumber(
          row.dpfcpma
        ),

      pma_range:
        row.pmaRange ?? null,

      pfc_range:
        row.pfcRange ?? null,

      slot:
        nullableInteger(row.slot),

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
        row.fasciaFc ?? null,

      tier_mantra:
        row.fasciaFr ?? null,

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
            row.calciomercato ?? ''
          ).trim()
        ),

      source_updated_at:
        row.updatedAt ?? null,

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

    raw: row
  };
}

async function importFantaculoList(
  file,
  referenceDate
) {
  const parsed =
    await readSpreadsheetFile(
      file,
      true
    );

  const missing =
    [
      'name',
      'team',
      'role'
    ].filter(
      column =>
        !parsed.columns.includes(column)
    );

  if (missing.length) {
    throw new Error(
      `Il file non sembra un listone Fantaculo. Colonne mancanti: ${missing.join(', ')}.`
    );
  }

  const normalizedRows =
    parsed.rows
      .map(
        (row, index) =>
          normalizeFantaculoRow(
            row,
            index + 1
          )
      )
      .filter(
        item =>
          item.normalized.name
      );

  if (!normalizedRows.length) {
    throw new Error(
      'Nessun giocatore valido trovato.'
    );
  }

  listImportProgress.textContent =
    `Preparazione di ${normalizedRows.length} giocatori...`;

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
    });

  if (!begin?.ok) {
    throw new Error(
      begin?.error ||
      'Impossibile iniziare l’import.'
    );
  }

  for (
    let start = 0;
    start < normalizedRows.length;
    start += IMPORT_CHUNK_SIZE
  ) {
    const end =
      Math.min(
        start + IMPORT_CHUNK_SIZE,
        normalizedRows.length
      );

    listImportProgress.textContent =
      `Importazione ${end} / ${normalizedRows.length}...`;

    const append =
      await callApi({
        action:
          'appendListImport',

        batchId:
          begin.batchId,

        rows:
          normalizedRows.slice(
            start,
            end
          )
      });

    if (!append?.ok) {
      throw new Error(
        append?.error ||
        'Errore durante il caricamento del listone.'
      );
    }
  }

  listImportProgress.textContent =
    'Finalizzazione listone...';

  const finish =
    await callApi({
      action:
        'finishListImport',

      batchId:
        begin.batchId
    });

  if (!finish?.ok) {
    throw new Error(
      finish?.error ||
      'Impossibile finalizzare il listone.'
    );
  }

  return finish.rowCount;
}

listImportForm.addEventListener(
  'submit',
  async event => {
    event.preventDefault();

    showMessage('');

    const file =
      listFile.files?.[0];

    if (!file) {
      return showMessage(
        'Seleziona un file XLSX o CSV.',
        'error'
      );
    }

    if (
      !listReferenceDate.value
    ) {
      return showMessage(
        'Indica la data di riferimento.',
        'error'
      );
    }

    listImportButton.disabled =
      true;

    const originalText =
      listImportButton.textContent;

    listImportButton.textContent =
      'Importazione...';

    try {
      const rowCount =
        await importFantaculoList(
          file,
          listReferenceDate.value
        );

      listImportProgress.textContent =
        `Import completato: ${rowCount} giocatori.`;

      showMessage(
        'Listone aggiornato correttamente.',
        'success'
      );

      listFile.value = '';

      await loadList();

    } catch (error) {
      console.error(error);

      listImportProgress.textContent =
        '';

      showMessage(
        error.message ||
        'Errore durante l’importazione.',
        'error'
      );

    } finally {
      listImportButton.disabled =
        false;

      listImportButton.textContent =
        originalText;
    }
  }
);

function getAvailableRoles() {
  return listData
    ?.settings
    ?.fantasyMode === 'mantra'
    ? [
        'Por',
        'B',
        'Dd',
        'Ds',
        'Dc',
        'E',
        'M',
        'C',
        'T',
        'W',
        'A',
        'Pc'
      ]
    : [
        'P',
        'D',
        'C',
        'A'
      ];
}

function getPlayerRoles(player) {
  return listData
    ?.settings
    ?.fantasyMode === 'mantra'
    ? (
        player.mantra_roles ||
        []
      )
    : (
        player.classic_role
          ? [player.classic_role]
          : []
      );
}

function renderRoleBadges(player) {
  return getPlayerRoles(player)
    .map(
      role =>
        `<span class="role-badge ${roleCssClass(role)}">${escapeHtml(role)}</span>`
    )
    .join('');
}

function renderRoleFilters() {
  const roles = [
    'all',
    ...getAvailableRoles()
  ];

  roleFilterBar.innerHTML =
    roles.map(
      role => {
        const label =
          role === 'all'
            ? 'ALL'
            : role;

        const cssRole =
          role === 'all'
            ? 'role-all'
            : roleCssClass(role);

        return `
          <button
            type="button"
            class="role-filter-button ${cssRole} ${activeRole === role ? 'active' : ''}"
            data-role="${escapeHtml(role)}"
          >
            ${escapeHtml(label)}
          </button>
        `;
      }
    ).join('');
}

function playerMatchesRole(player) {
  return (
    activeRole === 'all' ||
    getPlayerRoles(player)
      .includes(activeRole)
  );
}

function configureSecondaryFilters() {
  const players =
    listData?.players || [];

  const teams =
    [
      ...new Set(
        players
          .map(
            p =>
              p.serie_a_team
          )
          .filter(Boolean)
      )
    ].sort(
      (a, b) =>
        String(a)
          .localeCompare(
            String(b),
            'it'
          )
    );

  teamFilter.innerHTML =
    '<option value="all">Tutte</option>' +
    teams.map(
      team =>
        `<option value="${escapeHtml(team)}">${escapeHtml(team)}</option>`
    ).join('');

  const slots =
    [
      ...new Set(
        players
          .map(
            p =>
              Number(p.slot)
          )
          .filter(
            n =>
              Number.isFinite(n) &&
              n > 0
          )
      )
    ].sort(
      (a, b) =>
        a - b
    );

  slotFilter.innerHTML =
    '<option value="all">Tutti</option>' +
    slots.map(
      slot =>
        `<option value="${slot}">${slot}</option>`
    ).join('');
}

function matchesFlagFilter(player) {
  switch (flagFilter.value) {
    case 'market':
      return player.market_flag === true;

    case 'injury':
      return (
        player.uncertain_return === true ||
        hasValue(
          player.unavailable_until_round
        )
      );

    case 'new':
      return player.new_arrival === true;

    case 'penalties':
      return Number(
        player.penalty_probability || 0
      ) > 0;

    default:
      return true;
  }
}

function getSortValue(player, key) {
  const map = {
    name:
      player.name,

    team:
      player.serie_a_team,

    slot:
      player.slot,

    pma:
      player.pma,

    pfc:
      player.pfc,

    delta:
      player.pfc_pma_delta,

    fm:
      player.expected_fantasy_avg,

    tit:
      player.expected_titolarity
  };

  return map[key];
}

function comparePlayers(a, b) {
  const va =
    getSortValue(
      a,
      sortState.key
    );

  const vb =
    getSortValue(
      b,
      sortState.key
    );

  const mult =
    sortState.direction === 'asc'
      ? 1
      : -1;

  if (
    va === null ||
    va === undefined ||
    va === ''
  ) {
    return 1;
  }

  if (
    vb === null ||
    vb === undefined ||
    vb === ''
  ) {
    return -1;
  }

  const na =
    Number(va);

  const nb =
    Number(vb);

  const bothNumeric =
    Number.isFinite(na) &&
    Number.isFinite(nb) &&
    !Number.isNaN(
      Number(String(va))
    ) &&
    !Number.isNaN(
      Number(String(vb))
    );

  if (bothNumeric) {
    if (na === nb) {
      return String(a.name)
        .localeCompare(
          String(b.name),
          'it'
        );
    }

    return (
      na - nb
    ) * mult;
  }

  return String(va)
    .localeCompare(
      String(vb),
      'it',
      {
        sensitivity: 'base'
      }
    ) * mult;
}

function updateSortHeader() {
  sortButtons.forEach(
    button => {
      const active =
        button.dataset.sort ===
        sortState.key;

      button.classList.toggle(
        'active',
        active
      );

      button.querySelector(
        '.player-sort-indicator'
      ).textContent =
        active
          ? (
              sortState.direction === 'asc'
                ? '↑'
                : '↓'
            )
          : '↕';
    }
  );
}

function getFilteredPlayers() {
  const search =
    playerSearch.value
      .trim()
      .toLowerCase();

  return (
    listData?.players || []
  )
    .filter(
      player => {
        if (
          !playerMatchesRole(player)
        ) {
          return false;
        }

        if (
          teamFilter.value !== 'all' &&
          player.serie_a_team !==
            teamFilter.value
        ) {
          return false;
        }

        if (
          slotFilter.value !== 'all' &&
          String(player.slot) !==
            slotFilter.value
        ) {
          return false;
        }

        if (
          !matchesFlagFilter(player)
        ) {
          return false;
        }

        if (!search) {
          return true;
        }

        const haystack =
          [
            player.name,
            player.serie_a_team,
            player.classic_role,
            ...(
              player.mantra_roles ||
              []
            ),
            player.tier_classic,
            player.tier_mantra,
            player.nationality_name
          ]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();

        return haystack
          .includes(search);
      }
    )
    .sort(comparePlayers);
}

function getPlayerTier(player) {
  return listData
    ?.settings
    ?.fantasyMode === 'mantra'
    ? (
        player.tier_mantra ||
        '—'
      )
    : (
        player.tier_classic ||
        '—'
      );
}

function detailItem(
  label,
  value
) {
  return `
    <div class="player-detail-item">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
    </div>
  `;
}

function renderSignalBadges(player) {
  const badges = [];

  if (
    hasValue(
      player.penalty_probability
    )
  ) {
    badges.push(
      `<span class="badge good">Rigori ${escapeHtml(formatPercent(player.penalty_probability))}</span>`
    );
  }

  if (
    hasValue(
      player.free_kick_probability
    )
  ) {
    badges.push(
      `<span class="badge">Punizioni ${escapeHtml(formatPercent(player.free_kick_probability))}</span>`
    );
  }

  if (player.new_arrival) {
    badges.push(
      '<span class="badge">NUOVO ARRIVO</span>'
    );
  }

  if (player.market_flag) {
    badges.push(
      '<span class="badge warning">MERCATO</span>'
    );
  }

  if (player.uncertain_return) {
    badges.push(
      '<span class="badge warning">RIENTRO INCERTO</span>'
    );
  }

  if (
    hasValue(
      player.unavailable_until_round
    )
  ) {
    badges.push(
      `<span class="badge warning">OUT FINO G. ${escapeHtml(player.unavailable_until_round)}</span>`
    );
  }

  return badges.join('');
}

function renderPlayerDetail(player) {
  const items = [
    detailItem(
      'PFC range',
      player.pfc_range || '—'
    ),

    detailItem(
      'PMA range',
      player.pma_range || '—'
    ),

    detailItem(
      'Fascia',
      getPlayerTier(player)
    ),

    detailItem(
      'Nazionalità',
      player.nationality_name || '—'
    ),

    detailItem(
      'Ultima stagione FM',
      formatNumber(
        player.last_year_fantasy_avg,
        2
      )
    ),

    detailItem(
      'Ultima stagione tit.',
      formatPercent(
        player.last_year_titolarity
      )
    ),

    detailItem(
      'Ultime 5 FM',
      formatNumber(
        player.last_five_matches_fantasy_avg,
        2
      )
    ),

    detailItem(
      'Ultime 5 tit.',
      formatPercent(
        player.last_five_matches_titolarity
      )
    )
  ];

  return `
    <div class="player-detail-grid">
      ${items.join('')}
    </div>

    <div class="player-detail-flags">
      ${renderSignalBadges(player)}
    </div>

    ${
      player.source_updated_at
        ? `
          <p class="setting-help">
            Dati sorgente aggiornati
            ${escapeHtml(
              formatDateTime(
                player.source_updated_at
              )
            )}
          </p>
        `
        : ''
    }
  `;
}

function renderPlayers() {
  const players =
    getFilteredPlayers();

  playersTableBody.innerHTML = '';

  filteredCount.textContent =
    `${players.length} di ${listData?.players?.length || 0} giocatori`;

  if (!players.length) {
    playersEmpty.hidden = false;

    playersEmpty.textContent =
      listData?.players?.length
        ? 'Nessun giocatore corrisponde ai filtri.'
        : 'Nessun listone importato.';

    playerTableWrap.hidden =
      true;

    return;
  }

  playersEmpty.hidden = true;
  playerTableWrap.hidden = false;

  const fragment =
    document.createDocumentFragment();

  for (
    const player
    of players
  ) {
    const flag =
      countryCodeToEmoji(
        player.nationality_iso2
      );

    const delta =
      player.pfc_pma_delta === null ||
      player.pfc_pma_delta === undefined
        ? null
        : Number(
            player.pfc_pma_delta
          );

    const deltaClass =
      delta === null
        ? 'player-table-muted'
        : delta > 0
          ? 'player-delta-positive'
          : delta < 0
            ? 'player-delta-negative'
            : '';

    const deltaLabel =
      delta === null
        ? '—'
        : `${delta > 0 ? '+' : ''}${formatNumber(delta, 0)}`;

    const row =
      document.createElement('tr');

    row.className =
      'player-row';

    row.tabIndex = 0;

    row.dataset.playerId =
      player.id;

    row.innerHTML = `
      <td>
        <div class="player-main-cell">

          <span
            class="player-flag"
            title="${escapeHtml(player.nationality_name || '')}"
          >
            ${escapeHtml(flag)}
          </span>

          <div class="player-name-block">

            <span class="player-name">
              ${escapeHtml(player.name)}
            </span>

            <span class="player-role-badges">
              ${renderRoleBadges(player)}
            </span>

          </div>

        </div>
      </td>

      <td class="player-team">
        ${escapeHtml(player.serie_a_team || '—')}
      </td>

      <td class="player-number">
        ${escapeHtml(player.slot ?? '—')}
      </td>

      <td class="player-number">
        ${escapeHtml(formatNumber(player.pma, 0))}
      </td>

      <td class="player-number strong">
        ${escapeHtml(formatNumber(player.pfc, 0))}
      </td>

      <td class="player-number ${deltaClass}">
        ${escapeHtml(deltaLabel)}
      </td>

      <td class="player-number">
        ${escapeHtml(formatNumber(player.expected_fantasy_avg, 2))}
      </td>

      <td class="player-number">
        ${escapeHtml(formatPercent(player.expected_titolarity))}
      </td>
    `;

    const detailRow =
      document.createElement('tr');

    detailRow.className =
      'player-detail-row';

    detailRow.innerHTML =
      `<td colspan="8">${renderPlayerDetail(player)}</td>`;

    const toggleDetail = () => {
      const open =
        !detailRow.classList.contains(
          'is-open'
        );

      row.classList.toggle(
        'is-open',
        open
      );

      detailRow.classList.toggle(
        'is-open',
        open
      );
    };

    row.addEventListener(
      'click',
      toggleDetail
    );

    row.addEventListener(
      'keydown',
      event => {
        if (
          event.key === 'Enter' ||
          event.key === ' '
        ) {
          event.preventDefault();
          toggleDetail();
        }
      }
    );

    fragment.append(
      row,
      detailRow
    );
  }

  playersTableBody.appendChild(
    fragment
  );
}

function renderImportInfo() {
  const players =
    listData.players || [];

  const isSuperAdmin =
    listData.permissions
      .isSuperAdmin;

  setupTab.hidden =
    !listData.permissions
      .isLeagueAdmin;

  listImportSection.hidden =
    !listData.permissions
      .isLeagueAdmin;

  superAdminStatsSection.hidden =
    !isSuperAdmin;

  superAdminNationalitySection.hidden =
    !isSuperAdmin;

  playersCount.textContent =
    players.length;

  fantasyMode.textContent =
    fantasyModeLabel(
      listData.settings
        ?.fantasyMode
    );

  renderRoleFilters();
  configureSecondaryFilters();

  const hasPlayers =
    players.length > 0;

  roleFilterBar.hidden =
    !hasPlayers;

  playerFilterGrid.hidden =
    !hasPlayers;

  playerCountLine.hidden =
    !hasPlayers;

  if (!hasPlayers) {
    importInfo.hidden = true;

    playersEmpty.hidden = false;

    playersEmpty.textContent =
      'Nessun listone importato.';

    playerTableWrap.hidden =
      true;

    filteredCount.textContent = '';

    return;
  }

  importInfo.hidden = false;

  const batch =
    listData.importBatch;

  importDetails.textContent =
    batch
      ? [
          batch.source_filename ||
          'Listone',

          batch.reference_date
            ? `riferimento ${formatDate(batch.reference_date)}`
            : null,

          `${batch.row_count} giocatori`,

          batch.completed_at
            ? `importato ${formatDateTime(batch.completed_at)}`
            : null
        ]
          .filter(Boolean)
          .join(' · ')
      : 'Listone presente.';

  renderPlayers();
}

roleFilterBar.addEventListener(
  'click',
  event => {
    const button =
      event.target.closest(
        '.role-filter-button'
      );

    if (!button) return;

    activeRole =
      button.dataset.role ||
      'all';

    renderRoleFilters();
    renderPlayers();
  }
);

[
  playerSearch,
  teamFilter,
  slotFilter,
  flagFilter
].forEach(
  control => {
    control.addEventListener(
      control === playerSearch
        ? 'input'
        : 'change',
      renderPlayers
    );
  }
);

filterResetButton.addEventListener(
  'click',
  () => {
    activeRole = 'all';
    playerSearch.value = '';
    teamFilter.value = 'all';
    slotFilter.value = 'all';
    flagFilter.value = 'all';

    renderRoleFilters();
    renderPlayers();
  }
);

sortButtons.forEach(
  button => {
    button.addEventListener(
      'click',
      () => {
        const key =
          button.dataset.sort;

        if (!key) return;

        if (
          sortState.key === key
        ) {
          sortState.direction =
            sortState.direction === 'asc'
              ? 'desc'
              : 'asc';

        } else {
          sortState.key = key;

          sortState.direction =
            [
              'name',
              'team',
              'slot'
            ].includes(key)
              ? 'asc'
              : 'desc';
        }

        updateSortHeader();
        renderPlayers();
      }
    );
  }
);

nationalityEnrichButton.addEventListener(
  'click',
  async () => {
    showMessage('');

    nationalityEnrichButton.disabled =
      true;

    const originalText =
      nationalityEnrichButton.textContent;

    nationalityEnrichButton.textContent =
      'Ricerca in corso...';

    let processed = 0;
    let resolved = 0;
    let review = 0;
    let notFound = 0;

    try {
      for (
        let cycle = 0;
        cycle < 90;
        cycle++
      ) {
        const data =
          await callNationalityApi({
            action:
              'enrichBatch',

            limit: 6
          });

        if (!data?.ok) {
          throw new Error(
            data?.error ||
            'Errore durante la ricerca delle nazionalità.'
          );
        }

        processed +=
          data.processed || 0;

        resolved +=
          data.resolved || 0;

        review +=
          data.review || 0;

        notFound +=
          data.notFound || 0;

        nationalityProgress.textContent =
          `Analizzati ${processed} · trovati ${resolved} · da verificare ${review} · non trovati ${notFound} · mancanti ${data.remaining || 0}`;

        if (
          !data.remaining ||
          data.processed === 0
        ) {
          break;
        }
      }

      await loadList();

      showMessage(
        'Ricerca nazionalità completata.',
        'success'
      );

    } catch (error) {
      console.error(error);

      showMessage(
        error.message ||
        'Errore durante la ricerca delle nazionalità.',
        'error'
      );

    } finally {
      nationalityEnrichButton.disabled =
        false;

      nationalityEnrichButton.textContent =
        originalText;
    }
  }
);

function renderAdvisoryDatasets() {
  const datasets =
    listData
      ?.advisoryDatasets ||
    [];

  advisoryDatasets.innerHTML =
    datasets.length
      ? datasets.map(
          dataset => `
            <div class="list-row">

              <div class="list-row-main">

                <div class="list-row-title">

                  <strong>
                    ${escapeHtml(dataset.label)}
                  </strong>

                  <small>
                    ${escapeHtml(dataset.season || 'Stagione non indicata')}
                    ·
                    ${escapeHtml(dataset.row_count)}
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
                    ? `Riferimento ${escapeHtml(formatDate(dataset.reference_date))} · `
                    : ''
                }

                ${escapeHtml(dataset.source_filename || 'File')}
              </p>

            </div>
          `
        ).join('')
      : `
          <div class="empty-state">
            Nessun dataset aggiuntivo importato.
          </div>
        `;
}

function findColumnByAliases(
  columns,
  aliases
) {
  const aliasSet =
    new Set(
      aliases.map(
        normalizeHeader
      )
    );

  return columns.find(
    column =>
      aliasSet.has(
        normalizeHeader(column)
      )
  ) || null;
}

function getNumericMetrics(
  row,
  excludedColumns = []
) {
  const excluded =
    new Set(
      excludedColumns
        .filter(Boolean)
    );

  const result = {};

  for (
    const [key, value]
    of Object.entries(row)
  ) {
    if (
      excluded.has(key)
    ) {
      continue;
    }

    const n =
      nullableNumber(value);

    if (n !== null) {
      result[key] = n;
    }
  }

  return result;
}

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
    );

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
    );

  if (!nameColumn) {
    throw new Error(
      'Non riesco a individuare la colonna con il nome del giocatore.'
    );
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
    );

  const rows =
    parsed.rows
      .map(
        row => ({
          playerName:
            String(
              row[nameColumn] ?? ''
            ).trim(),

          team:
            teamColumn
              ? String(
                  row[teamColumn] ?? ''
                ).trim()
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
      );

  if (!rows.length) {
    throw new Error(
      'Il dataset non contiene giocatori validi.'
    );
  }

  advisoryProgress.textContent =
    `Preparazione di ${rows.length} righe...`;

  const begin =
    await callApi({
      action:
        'beginAdvisoryStatsImport',

      label,

      season:
        season || null,

      referenceDate:
        referenceDate || null,

      sourceFilename:
        file.name,

      sourceFormat:
        parsed.format,

      sourceColumns:
        parsed.columns
    });

  if (!begin?.ok) {
    throw new Error(
      begin?.error ||
      'Impossibile iniziare l’import.'
    );
  }

  let imported = 0;

  for (
    let start = 0;
    start < rows.length;
    start += IMPORT_CHUNK_SIZE
  ) {
    const end =
      Math.min(
        start + IMPORT_CHUNK_SIZE,
        rows.length
      );

    advisoryProgress.textContent =
      `Importazione ${end} / ${rows.length}...`;

    const append =
      await callApi({
        action:
          'appendAdvisoryStats',

        datasetId:
          begin.datasetId,

        rows:
          rows.slice(
            start,
            end
          )
      });

    if (!append?.ok) {
      throw new Error(
        append?.error ||
        'Errore durante l’importazione del dataset.'
      );
    }

    imported +=
      append.inserted || 0;
  }

  advisoryProgress.textContent =
    'Finalizzazione dataset...';

  const finish =
    await callApi({
      action:
        'finishAdvisoryStatsImport',

      datasetId:
        begin.datasetId
    });

  if (!finish?.ok) {
    throw new Error(
      finish?.error ||
      'Impossibile finalizzare il dataset.'
    );
  }

  return imported;
}

advisoryImportForm.addEventListener(
  'submit',
  async event => {
    event.preventDefault();

    showMessage('');

    const file =
      advisoryFile.files?.[0];

    const label =
      advisoryLabel.value.trim();

    if (!file) {
      return showMessage(
        'Seleziona un file XLSX o CSV.',
        'error'
      );
    }

    if (
      label.length < 2
    ) {
      return showMessage(
        'Inserisci un nome per il dataset.',
        'error'
      );
    }

    advisoryImportButton.disabled =
      true;

    const originalText =
      advisoryImportButton.textContent;

    advisoryImportButton.textContent =
      'Importazione...';

    try {
      const count =
        await importAdvisoryStats(
          file,
          label,
          advisorySeason.value.trim(),
          advisoryReferenceDate.value
        );

      advisoryProgress.textContent =
        `Dataset importato: ${count} righe.`;

      showMessage(
        'Statistiche aggiuntive importate.',
        'success'
      );

      advisoryFile.value = '';
      advisoryLabel.value = '';

      await loadList();

    } catch (error) {
      console.error(error);

      advisoryProgress.textContent =
        '';

      showMessage(
        error.message ||
        'Errore durante l’importazione delle statistiche.',
        'error'
      );

    } finally {
      advisoryImportButton.disabled =
        false;

      advisoryImportButton.textContent =
        originalText;
    }
  }
);

async function loadList() {
  showMessage('');

  try {
    const data =
      await callApi({
        action:
          'getList'
      });

    if (!data?.ok) {
      return showMessage(
        data?.error ||
        'Impossibile caricare il listone.',
        'error'
      );
    }

    listData = data;

    leagueTitle.textContent =
      `Listone · ${data.league.name}`;

    leagueSubtitle.textContent =
      fantasyModeLabel(
        data.settings
          ?.fantasyMode
      );

    activeRole = 'all';

    renderImportInfo();
    updateSortHeader();

    if (
      data.permissions
        .isSuperAdmin
    ) {
      renderAdvisoryDatasets();
    }

  } catch (error) {
    console.error(error);

    showMessage(
      error.message ||
      'Errore durante il caricamento.',
      'error'
    );
  }
}

listReferenceDate.value =
  getTodayLocal();

advisoryReferenceDate.value =
  getTodayLocal();

selectedLeague =
  getSelectedLeague();

if (!selectedLeague?.id) {
  window.location.href =
    'leagues.html';
} else {
  loadList();
}
