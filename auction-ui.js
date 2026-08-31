/* =========================================================
   auction-ui.js
   UI operativa asta:
   - quick bid +1/+2/+3/+5/+10 con conferma separata
   - drawer svincolati a destra con scroll interno
   - timer visuale con finestra tecnica di sincronizzazione
   ========================================================= */

const auctionUiQuickOffsets = [1, 2, 3, 5, 10];

const auctionUiElements = {
  liveQuick: document.getElementById('live-bid-quick'),
  liveSelect: document.getElementById('live-bid-amount'),
  liveSelected: document.getElementById('live-selected-bid'),
  liveConfirm: document.getElementById('live-bid-button'),
  auctioneerQuick: document.getElementById('auctioneer-bid-quick'),
  auctioneerSelect: document.getElementById('auctioneer-bid-amount'),
  auctioneerSelected: document.getElementById('auctioneer-selected-bid'),
  callFormArea: document.getElementById('call-form-area'),
  freeAgentsDrawer: document.getElementById('free-agents-drawer'),
  freeAgentsToggle: document.getElementById('free-agents-toggle'),
  freeAgentsToggleIcon: document.getElementById('free-agents-toggle-icon'),
  freeAgentsCount: document.getElementById('free-agents-count'),
  freeAgentsList: document.getElementById('call-candidates'),
  freeAgentsSearch: document.getElementById('call-player-search'),
  timer: document.getElementById('auction-timer-display'),
  timerStatus: document.getElementById('auction-timer-display-status')
};

let auctionUiLastMode = null;
let auctionUiFreeAgentsKey = '';
let auctionUiDrawerCollapsed = false;


/* =========================================================
   STATO / MODALITÀ
   ========================================================= */

function auctionUiSession() {
  return typeof auctionData !== 'undefined'
    ? auctionData?.auctionSession || null
    : null;
}


function auctionUiIsLive() {
  return auctionUiSession()?.status === 'live';
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

  const isLive = auctionUiIsLive();
  const isCallMode = auctionUiIsCallMode();
  const isBidMode = auctionUiIsBidMode();

  document.body.classList.toggle(
    'auction-live-mode',
    isLive
  );

  document.body.classList.toggle(
    'auction-call-mode',
    isCallMode
  );

  document.body.classList.toggle(
    'auction-bid-mode',
    isBidMode
  );

  const nextMode =
    isCallMode
      ? 'call'
      : isBidMode
        ? 'bid'
        : 'lobby';

  if (nextMode === auctionUiLastMode) return;

  auctionUiLastMode = nextMode;

  document
    .getElementById('live-section')
    ?.scrollTo({
      top: 0,
      behavior: 'instant'
    });

  auctionUiElements
    .freeAgentsList
    ?.scrollTo({
      top: 0,
      behavior: 'instant'
    });
}


/* =========================================================
   TIMER VISUALE
   ========================================================= */

function auctionUiNowMs() {
  return typeof liveNowMs === 'function'
    ? liveNowMs()
    : Date.now();
}


function auctionUiFormatSeconds(milliseconds) {
  return `${Math.max(
    0,
    Math.ceil(milliseconds / 1000)
  )}s`;
}


function auctionUiRenderTimer() {
  const timer = auctionUiElements.timer;
  const status = auctionUiElements.timerStatus;

  if (!timer || !status) return;

  const session = auctionUiSession();

  if (
    !session ||
    session.status !== 'live' ||
    !session.current_player_id
  ) {
    timer.textContent = '—';
    status.textContent = 'In attesa';
    return;
  }

  if (session.hold_active === true) {
    const holdSeconds =
      Number(session.hold_remaining_seconds);

    timer.textContent =
      Number.isFinite(holdSeconds)
        ? `${Math.max(
            0,
            Math.ceil(holdSeconds)
          )}s`
        : '—';

    status.textContent =
      'HOLD — timer sospeso';

    return;
  }

  if (session.timer_expired_at) {
    timer.textContent = '0s';

    status.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';

    return;
  }

  if (!session.timer_deadline) {
    timer.textContent = '—';

    status.textContent =
      session.current_bidder_team_id
        ? 'Timer non avviato'
        : 'In attesa della prima offerta';

    return;
  }

  const deadline =
    Date.parse(session.timer_deadline);

  if (!Number.isFinite(deadline)) {
    timer.textContent = '—';

    status.textContent =
      'Timer non disponibile';

    return;
  }

  const rawRemaining =
    Math.max(
      0,
      deadline - auctionUiNowMs()
    );

  const configuredSeconds =
    Number(session.current_timer_seconds);

  const configuredMs =
    Number.isFinite(configuredSeconds) &&
    configuredSeconds > 0
      ? configuredSeconds * 1000
      : null;

  /*
   * I 3 secondi tecnici concessi dal server
   * non vengono visualizzati come countdown.
   *
   * Durante quel tempo il timer rimane al
   * valore pieno configurato.
   */
  const visibleRemaining =
    configuredMs === null
      ? rawRemaining
      : Math.min(
          rawRemaining,
          configuredMs
        );

  timer.textContent =
    auctionUiFormatSeconds(
      visibleRemaining
    );

  if (rawRemaining <= 0) {
    status.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';

  } else if (
    configuredMs !== null &&
    rawRemaining > configuredMs + 100
  ) {
    status.textContent =
      'Sincronizzazione dispositivi…';

  } else {
    status.textContent =
      'Tempo residuo';
  }
}


/* =========================================================
   QUICK BID
   ========================================================= */

function auctionUiBidAnchor() {
  const session = auctionUiSession();

  return session
    ? Math.max(
        0,
        Number(
          session.current_bid || 0
        )
      )
    : 0;
}


function auctionUiMinimumBid() {
  if (
    typeof nextValidBid === 'function'
  ) {
    return Number(
      nextValidBid() || 1
    );
  }

  return Math.max(
    1,
    auctionUiBidAnchor() + 1
  );
}


function auctionUiPresidentMaxBid() {
  if (
    typeof liveActorTeamId !== 'function' ||
    typeof capacityForTeam !== 'function'
  ) {
    return 0;
  }

  const teamId =
    liveActorTeamId();

  if (!teamId) return 0;

  const capacity =
    capacityForTeam(teamId);

  return Math.max(
    0,
    Number(
      capacity?.max_bid || 0
    )
  );
}


function auctionUiAuctioneerMaxBid() {
  return typeof maxCapacityAcrossTeams
    === 'function'
      ? Math.max(
          0,
          Number(
            maxCapacityAcrossTeams() || 0
          )
        )
      : 0;
}


function auctionUiSelectedAmount(select) {
  return Math.max(
    0,
    Number(
      select?.value || 0
    )
  );
}


function auctionUiQuickButtonHtml(
  offset,
  target,
  selected,
  disabled
) {
  return `
    <button
      type="button"
      class="auction-quick-bid-button ${
        selected
          ? 'is-selected'
          : ''
      }"
      data-quick-bid="${target}"
      ${disabled ? 'disabled' : ''}
    >
      <span>
        +${offset}
      </span>

      <strong>
        ${target}
      </strong>
    </button>
  `;
}


function auctionUiRenderQuickGrid(
  container,
  select,
  maximum
) {
  if (!container || !select) return;

  const selected =
    auctionUiSelectedAmount(select);

  const current =
    auctionUiBidAnchor();

  const minimum =
    auctionUiMinimumBid();

  container.innerHTML =
    auctionUiQuickOffsets
      .map(offset => {
        const target =
          current + offset;

        const disabled =
          target < minimum ||
          target > maximum;

        return auctionUiQuickButtonHtml(
          offset,
          target,
          selected === target,
          disabled
        );
      })
      .join('');
}


function auctionUiRenderQuickBids() {
  const session =
    auctionUiSession();

  if (
    !session ||
    session.status !== 'live' ||
    !session.current_player_id
  ) {
    return;
  }

  /*
   * PRESIDENTE
   */
  auctionUiRenderQuickGrid(
    auctionUiElements.liveQuick,
    auctionUiElements.liveSelect,
    auctionUiPresidentMaxBid()
  );

  const liveSelected =
    auctionUiSelectedAmount(
      auctionUiElements.liveSelect
    );

  if (
    auctionUiElements.liveSelected
  ) {
    auctionUiElements
      .liveSelected
      .textContent =
        liveSelected > 0
          ? `Selezionato ${liveSelected}`
          : 'Selezionato —';
  }

  if (
    auctionUiElements.liveConfirm
  ) {
    auctionUiElements
      .liveConfirm
      .textContent =
        liveSelected > 0
          ? `Conferma ${liveSelected}`
          : 'Conferma rilancio';
  }

  /*
   * BANDITORE
   */
  auctionUiRenderQuickGrid(
    auctionUiElements.auctioneerQuick,
    auctionUiElements.auctioneerSelect,
    auctionUiAuctioneerMaxBid()
  );

  const auctioneerSelected =
    auctionUiSelectedAmount(
      auctionUiElements.auctioneerSelect
    );

  if (
    auctionUiElements
      .auctioneerSelected
  ) {
    auctionUiElements
      .auctioneerSelected
      .textContent =
        auctioneerSelected > 0
          ? `Selezionato ${auctioneerSelected}`
          : 'Selezionato —';
  }
}


function auctionUiSelectQuickAmount(
  select,
  amount
) {
  if (!select) return;

  const optionExists =
    Array
      .from(
        select.options || []
      )
      .some(
        option =>
          Number(option.value)
          === amount
      );

  if (!optionExists) return;

  select.value =
    String(amount);

  /*
   * Il change informa il vecchio motore
   * del nuovo importo, ma NON effettua
   * alcuna offerta.
   */
  select.dispatchEvent(
    new Event(
      'change',
      {
        bubbles: true
      }
    )
  );

  auctionUiRenderQuickBids();
}


auctionUiElements
  .liveQuick
  ?.addEventListener(
    'click',
    event => {
      const button =
        event.target.closest(
          '[data-quick-bid]'
        );

      if (
        !button ||
        button.disabled
      ) {
        return;
      }

      auctionUiSelectQuickAmount(
        auctionUiElements.liveSelect,
        Number(
          button.dataset.quickBid
        )
      );
    }
  );


auctionUiElements
  .auctioneerQuick
  ?.addEventListener(
    'click',
    event => {
      const button =
        event.target.closest(
          '[data-quick-bid]'
        );

      if (
        !button ||
        button.disabled
      ) {
        return;
      }

      auctionUiSelectQuickAmount(
        auctionUiElements.auctioneerSelect,
        Number(
          button.dataset.quickBid
        )
      );
    }
  );


auctionUiElements
  .auctioneerSelect
  ?.addEventListener(
    'change',
    auctionUiRenderQuickBids
  );


/* =========================================================
   LISTA SVINCOLATI
   ========================================================= */

function auctionUiPlayerRoles(player) {
  if (
    typeof getPlayerRoles === 'function'
  ) {
    return getPlayerRoles(
      player
    ).join('/');
  }

  if (
    Array.isArray(
      player?.mantra_roles
    )
  ) {
    return player
      .mantra_roles
      .join('/');
  }

  return (
    player?.classic_role || '—'
  );
}


function auctionUiFilteredFreeAgents() {
  const source =
    typeof auctionData !== 'undefined'
      ? auctionData
          ?.callCandidates || []
      : [];

  const query =
    String(
      auctionUiElements
        .freeAgentsSearch
        ?.value || ''
    )
      .trim()
      .toLowerCase();

  if (!query) {
    return source;
  }

  return source.filter(
    player => {
      const roles =
        auctionUiPlayerRoles(
          player
        );

      return [
        player.name,
        player.serie_a_team,
        player.classic_role,
        roles
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(query);
    }
  );
}


function auctionUiRenderFreeAgents(
  force = false
) {
  const list =
    auctionUiElements.freeAgentsList;

  if (!list) return;

  if (!auctionUiIsCallMode()) {
    auctionUiFreeAgentsKey = '';
    return;
  }

  const filtered =
    auctionUiFilteredFreeAgents();

  const total =
    typeof auctionData !== 'undefined'
      ? auctionData
          ?.callCandidates
          ?.length || 0
      : 0;

  if (
    auctionUiElements.freeAgentsCount
  ) {
    auctionUiElements
      .freeAgentsCount
      .textContent =
        filtered.length === total
          ? `${total}`
          : `${filtered.length}/${total}`;
  }

  const query =
    String(
      auctionUiElements
        .freeAgentsSearch
        ?.value || ''
    )
      .trim()
      .toLowerCase();

  const key =
    [
      query,
      filtered.length,
      filtered[0]?.id || '',
      filtered[
        filtered.length - 1
      ]?.id || ''
    ].join('|');

  if (
    !force &&
    key === auctionUiFreeAgentsKey
  ) {
    return;
  }

  auctionUiFreeAgentsKey = key;

  const previousScroll =
    list.scrollTop;

  if (!filtered.length) {
    list.innerHTML = `
      <div class="empty-state">
        Nessun giocatore trovato.
      </div>
    `;

    return;
  }

  /*
   * Nessuno slice(0, 50):
   * ora può essere caricata l'intera lista,
   * perché lo scroll è del contenitore.
   */
  list.innerHTML =
    filtered
      .map(
        player => {
          const roles =
            auctionUiPlayerRoles(
              player
            );

          return `
            <button
              type="button"
              class="list-row"
              data-call-player="${escapeHtml(
                player.id
              )}"
            >
              <span class="list-row-main">

                <span class="list-row-title">

                  <strong>
                    ${escapeHtml(
                      player.name
                    )}
                  </strong>

                  <small>
                    ${escapeHtml(
                      roles || '—'
                    )}
                    ·
                    ${escapeHtml(
                      player.serie_a_team
                      || '—'
                    )}
                    · Q.
                    ${escapeHtml(
                      player.quotation
                      ?? '—'
                    )}
                  </small>

                </span>

              </span>
            </button>
          `;
        }
      )
      .join('');

  list.scrollTop =
    previousScroll;
}


auctionUiElements
  .freeAgentsSearch
  ?.addEventListener(
    'input',
    () => {
      auctionUiRenderFreeAgents(
        true
      );
    }
  );


/* =========================================================
   DRAWER SVINCOLATI
   ========================================================= */

function auctionUiRenderDrawer() {
  const area =
    auctionUiElements.callFormArea;

  const drawer =
    auctionUiElements.freeAgentsDrawer;

  const toggle =
    auctionUiElements.freeAgentsToggle;

  if (
    !area ||
    !drawer ||
    !toggle
  ) {
    return;
  }

  area.classList.toggle(
    'free-agents-collapsed',
    auctionUiDrawerCollapsed
  );

  drawer.classList.toggle(
    'is-collapsed',
    auctionUiDrawerCollapsed
  );

  toggle.setAttribute(
    'aria-expanded',
    auctionUiDrawerCollapsed
      ? 'false'
      : 'true'
  );

  toggle.title =
    auctionUiDrawerCollapsed
      ? 'Mostra lista svincolati'
      : 'Nascondi lista svincolati';

  if (
    auctionUiElements
      .freeAgentsToggleIcon
  ) {
    auctionUiElements
      .freeAgentsToggleIcon
      .textContent =
        auctionUiDrawerCollapsed
          ? '‹'
          : '›';
  }
}


auctionUiElements
  .freeAgentsToggle
  ?.addEventListener(
    'click',
    () => {
      auctionUiDrawerCollapsed =
        !auctionUiDrawerCollapsed;

      try {
        localStorage.setItem(
          'fantacalcio_free_agents_collapsed',
          auctionUiDrawerCollapsed
            ? '1'
            : '0'
        );
      } catch {
        // Preferenza non essenziale.
      }

      auctionUiRenderDrawer();
    }
  );


try {
  auctionUiDrawerCollapsed =
    localStorage.getItem(
      'fantacalcio_free_agents_collapsed'
    ) === '1';

} catch {
  auctionUiDrawerCollapsed = false;
}


/* =========================================================
   INTEGRAZIONE CON MOTORE ESISTENTE
   ========================================================= */

function auctionUiRenderExtras() {
  auctionUiApplyMode();
  auctionUiRenderDrawer();
  auctionUiRenderQuickBids();
  auctionUiRenderFreeAgents();
}


/*
 * Il motore live continua a fare tutto il lavoro
 * server-side. Qui aggiungiamo soltanto la nuova UI.
 */
if (
  typeof renderAuctionLiveControls
  === 'function'
) {
  const auctionUiBaseRenderAuctionLiveControls =
    renderAuctionLiveControls;

  renderAuctionLiveControls =
    function () {
      auctionUiBaseRenderAuctionLiveControls();
      auctionUiRenderExtras();
    };
}


/*
 * Aggiornamento anche dopo le operazioni manuali
 * che richiamano loadLobby().
 */
if (
  typeof loadLobby === 'function'
) {
  const auctionUiBaseLoadLobby =
    loadLobby;

  loadLobby =
    async function () {
      await auctionUiBaseLoadLobby();
      auctionUiRenderExtras();
    };
}


/* =========================================================
   LOOP VISUALE
   ========================================================= */

/*
 * Solo il display viene aggiornato a 100 ms.
 * Non genera chiamate al server.
 */
setInterval(
  auctionUiRenderTimer,
  100
);


/*
 * Controlla eventuali passaggi
 * lobby / chiamata / rilanci.
 */
setInterval(
  auctionUiApplyMode,
  500
);


/*
 * Primo render quando auctionData
 * è disponibile.
 */
const auctionUiInitialRender =
  setInterval(
    () => {
      if (
        typeof auctionData === 'undefined' ||
        !auctionData
      ) {
        return;
      }

      clearInterval(
        auctionUiInitialRender
      );

      auctionUiRenderExtras();
      auctionUiRenderTimer();
    },
    100
  );
