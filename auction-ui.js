/* =========================================================
   auction-ui.js
   UI asta:
   - quick bid +1/+2/+3/+5/+10
   - conferma separata
   - drawer Svincolati = Listone
   - tutti gli svincolati
   - filtri ruolo multipli (ALL esclusivo), ricerca, squadra,
     slot, segnalazioni
   - ordinamento tabella
   - timer visuale sincronizzato
   ========================================================= */

const $auction = id => document.getElementById(id);

const auctionUi = {
  liveQuick: $auction('live-bid-quick'),
  liveSelect: $auction('live-bid-amount'),
  liveSelected: $auction('live-selected-bid'),
  liveConfirm: $auction('live-bid-button'),
  auctioneerQuick: $auction('auctioneer-bid-quick'),
  auctioneerSelect: $auction('auctioneer-bid-amount'),
  auctioneerSelected: $auction('auctioneer-selected-bid'),
  callFormArea: $auction('call-form-area'),
  drawer: $auction('free-agents-drawer'),
  toggle: $auction('free-agents-toggle'),
  toggleIcon: $auction('free-agents-toggle-icon'),
  totalCount: $auction('free-agents-count'),
  roleBar: $auction('auction-role-filter-bar'),
  search: $auction('call-player-search'),
  team: $auction('auction-player-team-filter'),
  slot: $auction('auction-player-slot-filter'),
  flag: $auction('auction-player-flag-filter'),
  reset: $auction('auction-player-filter-reset'),
  filteredCount: $auction('auction-filtered-count'),
  sortLabel: $auction('auction-sort-label'),
  tableWrap: $auction('auction-player-table-wrap'),
  body: $auction('call-candidates'),
  timer: $auction('auction-timer-display'),
  timerStatus: $auction('auction-timer-display-status')
};

const QUICK_OFFSETS = [1, 2, 3, 5, 10];

let auctionUiLastMode = null;
let auctionUiDrawerCollapsed = false;
let auctionUiRoles = new Set(['all']);
let auctionUiSort = { key: 'name', direction: 'asc' };
let auctionUiOptionsKey = '';
let auctionUiRenderKey = '';

/* Rimuove il listener di ricerca del vecchio renderer da 50 righe. */
if (auctionUi.search) {
  const oldSearch = auctionUi.search;
  const cleanSearch = oldSearch.cloneNode(true);
  oldSearch.replaceWith(cleanSearch);
  auctionUi.search = cleanSearch;
}

/* =========================================================
   STATO
   ========================================================= */

function auctionUiSession() {
  return typeof auctionData !== 'undefined'
    ? auctionData?.auctionSession || null
    : null;
}

function auctionUiSettings() {
  return (
    auctionUiSession()?.setup_snapshot ||
    (typeof auctionData !== 'undefined' ? auctionData?.settings : null) ||
    {}
  );
}

function auctionUiFantasyMode() {
  return auctionUiSettings()?.fantasy_mode || 'classic';
}

function auctionUiIsCallMode() {
  const session = auctionUiSession();
  return Boolean(
    session &&
    session.status === 'live' &&
    !session.current_player_id
  );
}

function auctionUiIsBidMode() {
  const session = auctionUiSession();
  return Boolean(
    session &&
    session.status === 'live' &&
    session.current_player_id
  );
}

function auctionUiApplyMode() {
  if (typeof auctionData === 'undefined') return;

  const live = auctionUiSession()?.status === 'live';
  const call = auctionUiIsCallMode();
  const bid = auctionUiIsBidMode();

  document.body.classList.toggle('auction-live-mode', live);
  document.body.classList.toggle('auction-call-mode', call);
  document.body.classList.toggle('auction-bid-mode', bid);

  const nextMode = call ? 'call' : bid ? 'bid' : 'lobby';
  if (nextMode === auctionUiLastMode) return;

  auctionUiLastMode = nextMode;

  $auction('live-section')?.scrollTo({
    top: 0,
    behavior: 'instant'
  });

  auctionUi.tableWrap?.scrollTo({
    top: 0,
    left: 0,
    behavior: 'instant'
  });
}

/* =========================================================
   TIMER
   ========================================================= */

function auctionUiNowMs() {
  return typeof liveNowMs === 'function'
    ? liveNowMs()
    : Date.now();
}

function auctionUiRenderTimer() {
  if (!auctionUi.timer || !auctionUi.timerStatus) return;

  const session = auctionUiSession();

  if (
    !session ||
    session.status !== 'live' ||
    !session.current_player_id
  ) {
    auctionUi.timer.textContent = '—';
    auctionUi.timerStatus.textContent = 'In attesa';
    return;
  }

  if (session.hold_active === true) {
    const seconds = Number(session.hold_remaining_seconds);

    auctionUi.timer.textContent = Number.isFinite(seconds)
      ? `${Math.max(0, Math.ceil(seconds))}s`
      : '—';

    auctionUi.timerStatus.textContent = 'HOLD — timer sospeso';
    return;
  }

  if (session.timer_expired_at) {
    auctionUi.timer.textContent = '0s';
    auctionUi.timerStatus.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';
    return;
  }

  if (!session.timer_deadline) {
    auctionUi.timer.textContent = '—';
    auctionUi.timerStatus.textContent = session.current_bidder_team_id
      ? 'Timer non avviato'
      : 'In attesa della prima offerta';
    return;
  }

  const deadline = Date.parse(session.timer_deadline);

  if (!Number.isFinite(deadline)) {
    auctionUi.timer.textContent = '—';
    auctionUi.timerStatus.textContent = 'Timer non disponibile';
    return;
  }

  const rawMs = Math.max(0, deadline - auctionUiNowMs());
  const configuredSeconds = Number(session.current_timer_seconds);

  const configuredMs =
    Number.isFinite(configuredSeconds) && configuredSeconds > 0
      ? configuredSeconds * 1000
      : null;

  const visibleMs =
    configuredMs === null
      ? rawMs
      : Math.min(rawMs, configuredMs);

  auctionUi.timer.textContent =
    `${Math.max(0, Math.ceil(visibleMs / 1000))}s`;

  if (rawMs <= 0) {
    auctionUi.timerStatus.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';
  } else if (
    configuredMs !== null &&
    rawMs > configuredMs + 100
  ) {
    auctionUi.timerStatus.textContent =
      'Sincronizzazione dispositivi…';
  } else {
    auctionUi.timerStatus.textContent = 'Tempo residuo';
  }
}

/* =========================================================
   QUICK BID
   ========================================================= */

function auctionUiCurrentBid() {
  return Math.max(
    0,
    Number(auctionUiSession()?.current_bid || 0)
  );
}

function auctionUiMinimumBid() {
  return typeof nextValidBid === 'function'
    ? Number(nextValidBid() || 1)
    : Math.max(1, auctionUiCurrentBid() + 1);
}

function auctionUiPresidentMax() {
  if (
    typeof liveActorTeamId !== 'function' ||
    typeof capacityForTeam !== 'function'
  ) {
    return 0;
  }

  const teamId = liveActorTeamId();
  const capacity = teamId ? capacityForTeam(teamId) : null;

  return Math.max(0, Number(capacity?.max_bid || 0));
}

function auctionUiAuctioneerMax() {
  return typeof maxCapacityAcrossTeams === 'function'
    ? Math.max(0, Number(maxCapacityAcrossTeams() || 0))
    : 0;
}

function auctionUiQuickButton(offset, amount, selected, disabled) {
  return `
    <button
      type="button"
      class="auction-quick-bid-button ${selected ? 'is-selected' : ''}"
      data-quick-bid="${amount}"
      ${disabled ? 'disabled' : ''}
    >
      <span>+${offset}</span>
      <strong>${amount}</strong>
    </button>
  `;
}

function auctionUiRenderQuickGrid(container, select, maximum) {
  if (!container || !select) return;

  const selected = Number(select.value || 0);
  const current = auctionUiCurrentBid();
  const minimum = auctionUiMinimumBid();

  container.innerHTML = QUICK_OFFSETS.map(offset => {
    const amount = current + offset;
    const disabled = amount < minimum || amount > maximum;

    return auctionUiQuickButton(
      offset,
      amount,
      selected === amount,
      disabled
    );
  }).join('');
}

function auctionUiRenderQuickBids() {
  if (!auctionUiIsBidMode()) return;

  auctionUiRenderQuickGrid(
    auctionUi.liveQuick,
    auctionUi.liveSelect,
    auctionUiPresidentMax()
  );

  const presidentSelected = Number(auctionUi.liveSelect?.value || 0);

  if (auctionUi.liveSelected) {
    auctionUi.liveSelected.textContent = presidentSelected > 0
      ? `Selezionato ${presidentSelected}`
      : 'Selezionato —';
  }

  if (auctionUi.liveConfirm) {
    auctionUi.liveConfirm.textContent = presidentSelected > 0
      ? `Conferma ${presidentSelected}`
      : 'Conferma rilancio';
  }

  auctionUiRenderQuickGrid(
    auctionUi.auctioneerQuick,
    auctionUi.auctioneerSelect,
    auctionUiAuctioneerMax()
  );

  const auctioneerSelected =
    Number(auctionUi.auctioneerSelect?.value || 0);

  if (auctionUi.auctioneerSelected) {
    auctionUi.auctioneerSelected.textContent = auctioneerSelected > 0
      ? `Selezionato ${auctioneerSelected}`
      : 'Selezionato —';
  }
}

function auctionUiSelectAmount(select, amount) {
  if (!select) return;

  const exists = Array.from(select.options || [])
    .some(option => Number(option.value) === amount);

  if (!exists) return;

  select.value = String(amount);

  select.dispatchEvent(
    new Event('change', { bubbles: true })
  );

  auctionUiRenderQuickBids();
}

auctionUi.liveQuick?.addEventListener('click', event => {
  const button = event.target.closest('[data-quick-bid]');
  if (!button || button.disabled) return;

  auctionUiSelectAmount(
    auctionUi.liveSelect,
    Number(button.dataset.quickBid)
  );
});

auctionUi.auctioneerQuick?.addEventListener('click', event => {
  const button = event.target.closest('[data-quick-bid]');
  if (!button || button.disabled) return;

  auctionUiSelectAmount(
    auctionUi.auctioneerSelect,
    Number(button.dataset.quickBid)
  );
});

auctionUi.auctioneerSelect?.addEventListener(
  'change',
  auctionUiRenderQuickBids
);

/* =========================================================
   DATI LISTONE
   ========================================================= */

function auctionUiPlayers() {
  return typeof auctionData !== 'undefined'
    ? auctionData?.callCandidates || []
    : [];
}

function auctionUiPlayerRoles(player) {
  if (auctionUiFantasyMode() === 'classic') {
    return player?.classic_role
      ? [player.classic_role]
      : [];
  }

  const mantra = Array.isArray(player?.mantra_roles)
    ? player.mantra_roles.filter(Boolean)
    : [];

  return mantra.length
    ? mantra
    : player?.classic_role
      ? [player.classic_role]
      : [];
}

function auctionUiRoleClass(role) {
  return String(role || '')
    .trim()
    .toLowerCase()
    .replaceAll(' ', '-');
}

function auctionUiRoleOrder() {
  return auctionUiFantasyMode() === 'classic'
    ? ['P', 'D', 'C', 'A']
    : ['Por', 'B', 'Dc', 'Dd', 'Ds', 'E', 'M', 'C', 'W', 'T', 'A', 'Pc'];
}

/* =========================================================
   FILTRI RUOLO
   ========================================================= */

function auctionUiRenderRoleFilters() {
  if (!auctionUi.roleBar) return;

  const all = `
    <button
      type="button"
      class="role-filter-button role-all ${auctionUiRoles.has('all') ? 'active' : ''}"
      data-auction-role="all"
    >
      ALL
    </button>
  `;

  const roles = auctionUiRoleOrder().map(role => `
    <button
      type="button"
      class="role-filter-button role-${auctionUiRoleClass(role)} ${auctionUiRoles.has(role) ? 'active' : ''}"
      data-auction-role="${escapeHtml(role)}"
    >
      ${escapeHtml(role)}
    </button>
  `).join('');

  auctionUi.roleBar.innerHTML = all + roles;
}

function auctionUiToggleRole(role) {
  if (role === 'all') {
    auctionUiRoles = new Set(['all']);
  } else {
    auctionUiRoles.delete('all');

    if (auctionUiRoles.has(role)) {
      auctionUiRoles.delete(role);
    } else {
      auctionUiRoles.add(role);
    }

    if (!auctionUiRoles.size) {
      auctionUiRoles.add('all');
    }
  }

  auctionUiRenderRoleFilters();
  auctionUiRenderListone(true);
}

auctionUi.roleBar?.addEventListener('click', event => {
  const button = event.target.closest('[data-auction-role]');
  if (!button) return;

  auctionUiToggleRole(button.dataset.auctionRole);
});

/* =========================================================
   OPZIONI FILTRI
   ========================================================= */

function auctionUiSetOptions(select, values, allLabel) {
  if (!select) return;

  const previous = select.value;

  select.innerHTML = `
    <option value="all">${escapeHtml(allLabel)}</option>
    ${values.map(value => `
      <option value="${escapeHtml(value)}">
        ${escapeHtml(value)}
      </option>
    `).join('')}
  `;

  if (
    Array.from(select.options)
      .some(option => option.value === previous)
  ) {
    select.value = previous;
  }
}

function auctionUiRefreshFilterOptions() {
  const players = auctionUiPlayers();

  const teams = [...new Set(
    players
      .map(player => player.serie_a_team)
      .filter(Boolean)
  )].sort((a, b) =>
    String(a).localeCompare(String(b), 'it', {
      sensitivity: 'base'
    })
  );

  const slots = [...new Set(
    players
      .map(player => player.slot)
      .filter(value =>
        value !== null &&
        value !== undefined &&
        String(value).trim() !== ''
      )
      .map(String)
  )].sort((a, b) =>
    String(a).localeCompare(String(b), 'it', {
      numeric: true
    })
  );

  const key = JSON.stringify({
    teams,
    slots,
    mode: auctionUiFantasyMode()
  });

  if (key === auctionUiOptionsKey) return;
  auctionUiOptionsKey = key;

  auctionUiSetOptions(auctionUi.team, teams, 'Tutte');
  auctionUiSetOptions(auctionUi.slot, slots, 'Tutti');
  auctionUiRenderRoleFilters();
}

/* =========================================================
   FILTRAGGIO
   ========================================================= */

function auctionUiMatchesRole(player) {
  if (auctionUiRoles.has('all')) return true;

  return auctionUiPlayerRoles(player)
    .some(role => auctionUiRoles.has(role));
}

function auctionUiMatchesFlag(player, flag) {
  if (flag === 'all') return true;

  if (flag === 'market') {
    return player?.market_flag === true;
  }

  if (flag === 'new') {
    return player?.new_arrival === true;
  }

  if (flag === 'injury') {
    return Boolean(
      player?.uncertain_return === true ||
      (
        player?.unavailable_until_round !== null &&
        player?.unavailable_until_round !== undefined &&
        String(player.unavailable_until_round).trim() !== ''
      )
    );
  }

  if (flag === 'penalties') {
    return Number(player?.penalty_probability || 0) > 0;
  }

  return true;
}

function auctionUiFilteredPlayers() {
  const query = String(auctionUi.search?.value || '')
    .trim()
    .toLowerCase();

  const team = auctionUi.team?.value || 'all';
  const slot = auctionUi.slot?.value || 'all';
  const flag = auctionUi.flag?.value || 'all';

  return auctionUiPlayers().filter(player => {
    if (!auctionUiMatchesRole(player)) return false;

    if (
      team !== 'all' &&
      String(player.serie_a_team || '') !== team
    ) {
      return false;
    }

    if (
      slot !== 'all' &&
      String(player.slot ?? '') !== slot
    ) {
      return false;
    }

    if (!auctionUiMatchesFlag(player, flag)) {
      return false;
    }

    if (!query) return true;

    const searchable = [
      player.name,
      player.serie_a_team,
      player.classic_role,
      ...auctionUiPlayerRoles(player),
      player.slot
    ]
      .filter(value => value !== null && value !== undefined)
      .join(' ')
      .toLowerCase();

    return searchable.includes(query);
  });
}

/* =========================================================
   ORDINAMENTO
   ========================================================= */

function auctionUiSortValue(player, key) {
  const values = {
    name: player?.name || '',
    team: player?.serie_a_team || '',
    slot: player?.slot,
    pma: player?.pma,
    pfc: player?.pfc,
    delta: player?.pfc_pma_delta,
    fm: player?.expected_fantasy_avg,
    tit: player?.expected_titolarity
  };

  return values[key];
}

function auctionUiCompare(a, b) {
  const emptyA = a === null || a === undefined || a === '';
  const emptyB = b === null || b === undefined || b === '';

  if (emptyA && emptyB) return 0;
  if (emptyA) return 1;
  if (emptyB) return -1;

  const numberA = Number(a);
  const numberB = Number(b);

  if (Number.isFinite(numberA) && Number.isFinite(numberB)) {
    return numberA - numberB;
  }

  return String(a).localeCompare(String(b), 'it', {
    sensitivity: 'base',
    numeric: true
  });
}

function auctionUiSortedPlayers(players) {
  const factor =
    auctionUiSort.direction === 'asc'
      ? 1
      : -1;

  return [...players].sort((a, b) => {
    const result = auctionUiCompare(
      auctionUiSortValue(a, auctionUiSort.key),
      auctionUiSortValue(b, auctionUiSort.key)
    );

    if (result !== 0) return result * factor;

    return String(a?.name || '').localeCompare(
      String(b?.name || ''),
      'it',
      { sensitivity: 'base' }
    );
  });
}

function auctionUiUpdateSortHeader() {
  document
    .querySelectorAll('[data-auction-sort]')
    .forEach(button => {
      const active =
        button.dataset.auctionSort === auctionUiSort.key;

      button.classList.toggle('active', active);

      const indicator =
        button.querySelector('.player-sort-indicator');

      if (indicator) {
        indicator.textContent = active
          ? auctionUiSort.direction === 'asc'
            ? '↑'
            : '↓'
          : '↕';
      }
    });

  if (auctionUi.sortLabel) {
    const labels = {
      name: 'Nome',
      team: 'Squadra',
      slot: 'Slot',
      pma: 'PMA',
      pfc: 'PFC',
      delta: 'Δ',
      fm: 'Exp. FM',
      tit: 'Exp. Tit.'
    };

    auctionUi.sortLabel.textContent =
      `${labels[auctionUiSort.key] || auctionUiSort.key} ${
        auctionUiSort.direction === 'asc' ? '↑' : '↓'
      }`;
  }
}

$auction('auction-player-table-wrap')
  ?.querySelector('thead')
  ?.addEventListener('click', event => {
    const button = event.target.closest('[data-auction-sort]');
    if (!button) return;

    const key = button.dataset.auctionSort;

    if (auctionUiSort.key === key) {
      auctionUiSort.direction =
        auctionUiSort.direction === 'asc'
          ? 'desc'
          : 'asc';
    } else {
      auctionUiSort = {
        key,
        direction: 'asc'
      };
    }

    auctionUiRenderListone(true);
  });

/* =========================================================
   CELLE / BADGE
   ========================================================= */

function auctionUiFlagEmoji(iso2) {
  const code = String(iso2 || '')
    .trim()
    .toUpperCase();

  if (!/^[A-Z]{2}$/.test(code)) return '';

  return [...code]
    .map(char =>
      String.fromCodePoint(
        127397 + char.charCodeAt(0)
      )
    )
    .join('');
}

function auctionUiRoleBadges(player) {
  return auctionUiPlayerRoles(player)
    .map(role => `
      <span class="role-badge role-${auctionUiRoleClass(role)}">
        ${escapeHtml(role)}
      </span>
    `)
    .join('');
}

function auctionUiSignalBadges(player) {
  const badges = [];

  if (player?.market_flag === true) {
    badges.push(
      '<span class="player-alert-flag" title="Mercato">⇄</span>'
    );
  }

  if (player?.new_arrival === true) {
    badges.push(
      '<span class="player-alert-flag" title="Nuovo arrivo">NEW</span>'
    );
  }

  if (
    player?.uncertain_return === true ||
    (
      player?.unavailable_until_round !== null &&
      player?.unavailable_until_round !== undefined &&
      String(player.unavailable_until_round).trim() !== ''
    )
  ) {
    badges.push(
      '<span class="player-alert-flag warning" title="Indisponibile / rientro incerto">!</span>'
    );
  }

  if (Number(player?.penalty_probability || 0) > 0) {
    badges.push(
      '<span class="player-alert-flag" title="Possibile rigorista">PEN</span>'
    );
  }

  return badges.join('');
}

function auctionUiNumber(value) {
  if (value === null || value === undefined || value === '') {
    return '—';
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return escapeHtml(value);
  }

  return Number.isInteger(number)
    ? String(number)
    : number.toFixed(2).replace(/\.?0+$/, '');
}

function auctionUiPlayerRow(player) {
  const delta = Number(player?.pfc_pma_delta);

  const deltaClass = Number.isFinite(delta)
    ? delta > 0
      ? 'player-delta-positive'
      : delta < 0
        ? 'player-delta-negative'
        : ''
    : '';

  const flag = auctionUiFlagEmoji(player?.nationality_iso2);

  return `
    <tr
      class="player-row auction-call-player-row"
      data-call-player="${escapeHtml(player.id)}"
      title="Chiama ${escapeHtml(player.name || 'giocatore')}"
    >
      <td>
        <div class="player-main-cell">
          <span class="player-role-badges">
            ${auctionUiRoleBadges(player)}
          </span>

          <span class="player-name-block">
            <span class="player-name">
              ${escapeHtml(player.name || '—')}
            </span>

            ${
              flag
                ? `
                  <span
                    class="player-flag"
                    title="${escapeHtml(
                      player.nationality_name ||
                      player.nationality_iso2 ||
                      ''
                    )}"
                  >
                    ${flag}
                  </span>
                `
                : ''
            }

            <span class="player-alert-flags">
              ${auctionUiSignalBadges(player)}
            </span>
          </span>
        </div>
      </td>

      <td class="player-team">
        ${escapeHtml(player.serie_a_team || '—')}
      </td>

      <td class="player-number">
        ${escapeHtml(player.slot ?? '—')}
      </td>

      <td class="player-number">
        ${auctionUiNumber(player.pma)}
      </td>

      <td class="player-number strong">
        ${auctionUiNumber(player.pfc)}
      </td>

      <td class="player-number ${deltaClass}">
        ${auctionUiNumber(player.pfc_pma_delta)}
      </td>

      <td class="player-number">
        ${auctionUiNumber(player.expected_fantasy_avg)}
      </td>

      <td class="player-number">
        ${auctionUiNumber(player.expected_titolarity)}
      </td>
    </tr>
  `;
}

/* =========================================================
   RENDER LISTONE NEL DRAWER
   ========================================================= */

function auctionUiRenderListone(force = false) {
  if (!auctionUi.body) return;

  if (!auctionUiIsCallMode()) {
    auctionUiRenderKey = '';
    return;
  }

  auctionUiRefreshFilterOptions();

  const filtered = auctionUiFilteredPlayers();
  const sorted = auctionUiSortedPlayers(filtered);
  const total = auctionUiPlayers().length;

  if (auctionUi.totalCount) {
    auctionUi.totalCount.textContent =
      `${total} giocatori`;
  }

  if (auctionUi.filteredCount) {
    auctionUi.filteredCount.textContent =
      `${filtered.length} di ${total}`;
  }

  auctionUiUpdateSortHeader();

  const key = JSON.stringify({
    q: auctionUi.search?.value || '',
    team: auctionUi.team?.value || 'all',
    slot: auctionUi.slot?.value || 'all',
    flag: auctionUi.flag?.value || 'all',
    roles: [...auctionUiRoles].sort(),
    sort: auctionUiSort,
    total,
    first: sorted[0]?.id || '',
    last: sorted.at(-1)?.id || ''
  });

  if (!force && key === auctionUiRenderKey) return;
  auctionUiRenderKey = key;

  const oldScroll = auctionUi.tableWrap?.scrollTop || 0;

  auctionUi.body.innerHTML = sorted.length
    ? sorted.map(auctionUiPlayerRow).join('')
    : `
      <tr>
        <td colspan="8" class="player-table-empty">
          Nessun giocatore trovato.
        </td>
      </tr>
    `;

  if (auctionUi.tableWrap) {
    auctionUi.tableWrap.scrollTop = oldScroll;
  }
}

function auctionUiFilterChanged() {
  auctionUiRenderListone(true);
}

auctionUi.search?.addEventListener('input', auctionUiFilterChanged);
auctionUi.team?.addEventListener('change', auctionUiFilterChanged);
auctionUi.slot?.addEventListener('change', auctionUiFilterChanged);
auctionUi.flag?.addEventListener('change', auctionUiFilterChanged);

auctionUi.reset?.addEventListener('click', () => {
  if (auctionUi.search) auctionUi.search.value = '';
  if (auctionUi.team) auctionUi.team.value = 'all';
  if (auctionUi.slot) auctionUi.slot.value = 'all';
  if (auctionUi.flag) auctionUi.flag.value = 'all';

  auctionUiRoles = new Set(['all']);
  auctionUiSort = {
    key: 'name',
    direction: 'asc'
  };

  auctionUiRenderRoleFilters();
  auctionUiRenderListone(true);
});

/* =========================================================
   DRAWER
   ========================================================= */

function auctionUiRenderDrawer() {
  if (
    !auctionUi.callFormArea ||
    !auctionUi.drawer ||
    !auctionUi.toggle
  ) {
    return;
  }

  auctionUi.callFormArea.classList.toggle(
    'free-agents-collapsed',
    auctionUiDrawerCollapsed
  );

  auctionUi.drawer.classList.toggle(
    'is-collapsed',
    auctionUiDrawerCollapsed
  );

  auctionUi.toggle.setAttribute(
    'aria-expanded',
    auctionUiDrawerCollapsed ? 'false' : 'true'
  );

  auctionUi.toggle.title = auctionUiDrawerCollapsed
    ? 'Mostra lista svincolati'
    : 'Nascondi lista svincolati';

  if (auctionUi.toggleIcon) {
    auctionUi.toggleIcon.textContent =
      auctionUiDrawerCollapsed ? '‹' : '›';
  }
}

auctionUi.toggle?.addEventListener('click', () => {
  auctionUiDrawerCollapsed = !auctionUiDrawerCollapsed;

  try {
    localStorage.setItem(
      'fantacalcio_free_agents_collapsed',
      auctionUiDrawerCollapsed ? '1' : '0'
    );
  } catch {
    // Preferenza non essenziale.
  }

  auctionUiRenderDrawer();
});

try {
  auctionUiDrawerCollapsed =
    localStorage.getItem(
      'fantacalcio_free_agents_collapsed'
    ) === '1';
} catch {
  auctionUiDrawerCollapsed = false;
}

/* =========================================================
   INTEGRAZIONE CON IL MOTORE ESISTENTE
   ========================================================= */

/*
 * Il vecchio renderCallPanel chiama renderCallCandidates().
 * Lo sostituiamo: niente più slice(0, 50).
 */
if (typeof renderCallCandidates === 'function') {
  renderCallCandidates = function () {
    auctionUiRenderListone(true);
  };
}

function auctionUiRenderExtras() {
  auctionUiApplyMode();
  auctionUiRenderDrawer();
  auctionUiRenderQuickBids();
  auctionUiRenderListone();
}

if (typeof renderAuctionLiveControls === 'function') {
  const baseRenderAuctionLiveControls =
    renderAuctionLiveControls;

  renderAuctionLiveControls = function () {
    baseRenderAuctionLiveControls();
    auctionUiRenderExtras();
  };
}

if (typeof loadLobby === 'function') {
  const baseLoadLobby = loadLobby;

  loadLobby = async function () {
    await baseLoadLobby();
    auctionUiRenderExtras();
  };
}

/* Display timer: solo client, nessuna chiamata server. */
setInterval(auctionUiRenderTimer, 100);

/* Cambi fase lobby/chiamata/rilanci. */
setInterval(auctionUiApplyMode, 500);

/* Primo render. */
const auctionUiInitialRender = setInterval(() => {
  if (
    typeof auctionData === 'undefined' ||
    !auctionData
  ) {
    return;
  }

  clearInterval(auctionUiInitialRender);

  auctionUiRenderExtras();
  auctionUiRenderTimer();
}, 100);
