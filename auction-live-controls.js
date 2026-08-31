/* auction-live-controls.js
   STEP 4
   Timer server-side, HOLD, turni, picker AUTO/MANUAL,
   pannello Banditore, correzioni e capacità massima d'offerta.
*/

const liveUi = {
  panel: document.getElementById('live-control-panel'),
  timerValue: document.getElementById('live-timer-value'),
  timerStatus: document.getElementById('live-timer-status'),
  turnBadge: document.getElementById('live-turn-badge'),
  passBadge: document.getElementById('live-pass-badge'),
  hold: document.getElementById('live-hold-button'),
  controls: document.getElementById('live-president-controls'),
  bidAmount: document.getElementById('live-bid-amount'),
  pickerMode: document.getElementById('live-picker-mode'),
  pickerAuto: document.getElementById('live-picker-auto-button'),
  maxBid: document.getElementById('live-max-bid'),
  bid: document.getElementById('live-bid-button'),
  turnActions: document.getElementById('live-turn-actions'),
  pass: document.getElementById('live-pass-button'),
  abandon: document.getElementById('live-abandon-button'),
  help: document.getElementById('live-action-help')
};

const auctioneerUi = {
  panel: document.getElementById('auctioneer-panel'),
  amount: document.getElementById('auctioneer-bid-amount'),
  pickerMode: document.getElementById('auctioneer-picker-mode'),
  actionMode: document.getElementById('auctioneer-action-mode'),
  pickerAuto: document.getElementById('auctioneer-picker-auto-button'),
  teamButtons: document.getElementById('auctioneer-team-buttons'),
  award: document.getElementById('auctioneer-award-player'),
  finishTest: document.getElementById('test-finish-review'),
  help: document.getElementById('auctioneer-help'),
  recent: document.getElementById('auction-recent-bids')
};

let liveServerOffsetMs = 0;
let liveTimerSyncing = false;
let livePolling = false;

let presidentPickerMode = 'auto';
let auctioneerPickerMode = 'auto';
let pickerPlayerId = null;

function liveSession() {
  return auctionData?.auctionSession || null;
}

function liveSettings() {
  return (
    liveSession()?.setup_snapshot
    ||
    auctionData?.settings
    ||
    {}
  );
}

function liveBidMode() {
  return liveSettings()?.bid_mode || 'wild';
}

function liveMyTeamId() {
  return auctionData?.myTeam?.teamId || null;
}

function liveCurrentTurnTeam() {
  return auctionData?.currentTurnTeam || null;
}

function liveIsController() {
  return (
    auctionData?.permissions?.canControlAuction
    === true
  );
}

function liveIsPresident() {
  return (
    auctionData?.permissions?.isPresident
    === true
  );
}

function liveTeamState(teamId) {
  return (
    auctionData?.teamOrder
    || []
  )
    .find(
      item =>
        item.team_id === teamId
    )
    || null;
}

function capacityForTeam(teamId) {
  return (
    auctionData?.bidCapacities
    || []
  )
    .find(
      item =>
        item.team_id === teamId
    )
    || null;
}

function maxCapacityAcrossTeams() {
  return (
    auctionData?.bidCapacities
    || []
  )
    .reduce(
      (max, item) =>
        Math.max(
          max,
          Number(
            item.max_bid || 0
          )
        ),
      0
    );
}

function nextValidBid() {
  const session =
    liveSession();

  if (!session) {
    return 1;
  }

  if (
    !session.current_bidder_team_id
  ) {
    return Math.max(
      1,
      Number(
        session.current_bid
        || 1
      )
    );
  }

  return Math.max(
    1,
    Number(
      session.current_bid
      || 0
    )
    +
    1
  );
}

function capacityReasonLabel(reason) {
  const labels = {
    CLASSIC_ROLE_FULL:
      'ruolo completo',

    CLASSIC_ROSTER_FULL:
      'rosa completa',

    MANTRA_ROSTER_FULL:
      'rosa completa',

    MANTRA_GOALKEEPER_FULL:
      'portieri completi',

    MANTRA_OUTFIELD_FULL:
      'movimento completo',

    MANTRA_MINIMA_IMPOSSIBLE:
      'vincoli Mantra',

    NO_BUDGET_FOR_REQUIRED_SLOTS:
      'crediti da riservare',

    PLAYER_ROLE_MISSING:
      'ruolo non disponibile'
  };

  return (
    labels[reason]
    ||
    'non disponibile'
  );
}

function rebuildPickerOptions(
  select,
  maxBid
) {
  if (!select) return;

  const maximum =
    Math.max(
      0,
      Number(
        maxBid || 0
      )
    );

  if (
    Number(
      select.dataset.maxBid
      || -1
    )
    === maximum
  ) {
    return;
  }

  select.innerHTML =
    '';

  if (maximum < 1) {
    select.dataset.maxBid =
      '0';

    return;
  }

  const fragment =
    document.createDocumentFragment();

  for (
    let amount = 1;
    amount <= maximum;
    amount += 1
  ) {
    const option =
      document.createElement(
        'option'
      );

    option.value =
      String(amount);

    option.textContent =
      String(amount);

    fragment.appendChild(
      option
    );
  }

  select.appendChild(
    fragment
  );

  select.dataset.maxBid =
    String(maximum);
}

function setPickerValue(
  select,
  value
) {
  if (!select) return;

  const maximum =
    Number(
      select.dataset.maxBid
      || 0
    );

  if (maximum < 1) {
    return;
  }

  select.value =
    String(
      Math.min(
        maximum,
        Math.max(
          1,
          Number(
            value || 1
          )
        )
      )
    );
}

function resetPickersForNewPlayer() {
  const playerId =
    auctionData?.currentPlayer?.id
    || null;

  if (
    playerId === pickerPlayerId
  ) {
    return;
  }

  pickerPlayerId =
    playerId;

  presidentPickerMode =
    'auto';

  auctioneerPickerMode =
    'auto';
}

function renderPresidentPickerMode() {
  if (
    !liveUi.pickerMode
    ||
    !liveUi.pickerAuto
  ) {
    return;
  }

  const auto =
    presidentPickerMode === 'auto';

  liveUi.pickerMode.textContent =
    auto
      ? 'AUTO'
      : 'MANUAL';

  liveUi.pickerMode.classList.toggle(
    'good',
    auto
  );

  liveUi.pickerMode.classList.toggle(
    'warning',
    !auto
  );

  liveUi.pickerAuto.hidden =
    auto;
}

function renderAuctioneerPickerMode() {
  if (
    !auctioneerUi.pickerMode
    ||
    !auctioneerUi.pickerAuto
  ) {
    return;
  }

  const auto =
    auctioneerPickerMode === 'auto';

  auctioneerUi.pickerMode.textContent =
    auto
      ? 'AUTO'
      : 'MANUAL';

  auctioneerUi.pickerMode.classList.toggle(
    'good',
    auto
  );

  auctioneerUi.pickerMode.classList.toggle(
    'warning',
    !auto
  );

  auctioneerUi.pickerAuto.hidden =
    auto;
}

function makePresidentPickerManual() {
  presidentPickerMode =
    'manual';

  renderPresidentPickerMode();
}

function makeAuctioneerPickerManual() {
  auctioneerPickerMode =
    'manual';

  renderAuctioneerPickerMode();
  renderAuctioneerActionMode();
  renderAuctioneerTeamButtons();
}

[
  'pointerdown',
  'touchstart',
  'wheel'
]
  .forEach(
    eventName => {
      liveUi.bidAmount
        ?.addEventListener(
          eventName,
          makePresidentPickerManual,
          {
            passive: true
          }
        );

      auctioneerUi.amount
        ?.addEventListener(
          eventName,
          makeAuctioneerPickerManual,
          {
            passive: true
          }
        );
    }
  );

liveUi.bidAmount
  ?.addEventListener(
    'change',
    makePresidentPickerManual
  );

auctioneerUi.amount
  ?.addEventListener(
    'change',
    () => {
      makeAuctioneerPickerManual();
      renderAuctioneerActionMode();
      renderAuctioneerTeamButtons();
    }
  );

liveUi.pickerAuto
  ?.addEventListener(
    'click',
    () => {
      presidentPickerMode =
        'auto';

      setPickerValue(
        liveUi.bidAmount,
        nextValidBid()
      );

      renderPresidentPickerMode();
    }
  );

auctioneerUi.pickerAuto
  ?.addEventListener(
    'click',
    () => {
      auctioneerPickerMode =
        'auto';

      setPickerValue(
        auctioneerUi.amount,
        nextValidBid()
      );

      renderAuctioneerPickerMode();
      renderAuctioneerActionMode();
      renderAuctioneerTeamButtons();
    }
  );

function updateLiveServerOffset() {
  const serverNow =
    Date.parse(
      auctionData?.serverNow
      || ''
    );

  if (
    Number.isFinite(
      serverNow
    )
  ) {
    liveServerOffsetMs =
      serverNow
      -
      Date.now();
  }
}

function liveNowMs() {
  return (
    Date.now()
    +
    liveServerOffsetMs
  );
}

function liveRemainingMs() {
  const session =
    liveSession();

  if (!session) {
    return null;
  }

  if (
    session.hold_active === true
  ) {
    const seconds =
      Number(
        session.hold_remaining_seconds
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

  return Number.isFinite(
    deadline
  )
    ? Math.max(
        0,
        deadline
        -
        liveNowMs()
      )
    : null;
}

function formatLiveTimer(milliseconds) {
  if (
    milliseconds === null
    ||
    milliseconds === undefined
  ) {
    return '—';
  }

  return `${
    Math.max(
      0,
      Math.ceil(
        milliseconds / 1000
      )
    )
  }s`;
}

async function syncExpiredLiveTimer() {
  const session =
    liveSession();

  if (
    !session
    ||
    liveTimerSyncing
    ||
    session.status !== 'live'
    ||
    session.hold_active === true
    ||
    session.timer_expired_at
    ||
    !session.timer_deadline
  ) {
    return;
  }

  const remaining =
    liveRemainingMs();

  if (
    remaining === null
    ||
    remaining > 0
  ) {
    return;
  }

  liveTimerSyncing =
    true;

  try {
    const result =
      await callApi({
        action:
          'syncTimer',

        sessionId:
          session.id
      });

    if (result?.ok) {
      await refreshLiveAuctionState();
    }

  } catch (error) {
    console.error(error);

  } finally {
    liveTimerSyncing =
      false;
  }
}

function renderLiveTimer() {
  if (
    !liveUi.timerValue
    ||
    !liveUi.timerStatus
  ) {
    return;
  }

  const session =
    liveSession();

  if (
    !session
    ||
    session.status !== 'live'
  ) {
    liveUi.timerValue.textContent =
      '—';

    liveUi.timerStatus.textContent =
      'In attesa';

    return;
  }

  if (
    session.hold_active === true
  ) {
    liveUi.timerValue.textContent =
      formatLiveTimer(
        liveRemainingMs()
      );

    liveUi.timerStatus.textContent =
      'HOLD — timer sospeso';

    return;
  }

  if (
    session.timer_expired_at
  ) {
    liveUi.timerValue.textContent =
      '0s';

    liveUi.timerStatus.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';

    return;
  }

  const remaining =
    liveRemainingMs();

  if (
    remaining === null
  ) {
    liveUi.timerValue.textContent =
      '—';

    liveUi.timerStatus.textContent =
      session.current_bidder_team_id
        ? 'Timer non avviato'
        : 'In attesa della prima offerta';

    return;
  }

  liveUi.timerValue.textContent =
    formatLiveTimer(
      remaining
    );

  liveUi.timerStatus.textContent =
    'Tempo residuo';

  if (
    remaining <= 0
  ) {
    syncExpiredLiveTimer();
  }
}

function liveActorTeamId() {
  const session =
    liveSession();

  if (!session) {
    return null;
  }

  const myTeamId =
    liveMyTeamId();

  if (
    liveBidMode() === 'turn'
  ) {
    const turnTeam =
      liveCurrentTurnTeam();

    if (!turnTeam) {
      return null;
    }

    if (
      liveIsPresident()
      &&
      myTeamId === turnTeam.id
    ) {
      return turnTeam.id;
    }

    if (
      liveIsController()
    ) {
      return turnTeam.id;
    }

    return null;
  }

  return (
    liveIsPresident()
    &&
    myTeamId
      ? myTeamId
      : null
  );
}

function renderLiveControls() {
  if (!liveUi.panel) {
    return;
  }

  updateLiveServerOffset();
  resetPickersForNewPlayer();

  const session =
    liveSession();

  const player =
    auctionData?.currentPlayer;

  const show =
    Boolean(
      session
      &&
      session.status === 'live'
      &&
      player
    );

  liveUi.panel.hidden =
    !show;

  if (!show) {
    presidentPickerMode =
      'auto';

    return;
  }

  const mode =
    liveBidMode();

  const turnTeam =
    liveCurrentTurnTeam();

  const leader =
    auctionData?.currentBidderTeam;

  const actorTeamId =
    liveActorTeamId();

  const actorState =
    actorTeamId
      ? liveTeamState(actorTeamId)
      : null;

  const capacity =
    actorTeamId
      ? capacityForTeam(actorTeamId)
      : null;

  liveUi.turnBadge.hidden =
    mode !== 'turn';

  if (
    mode === 'turn'
  ) {
    liveUi.turnBadge.textContent =
      turnTeam
        ? `Turno: ${turnTeam.name}`
        : 'Nessun turno attivo';
  }

  liveUi.passBadge.hidden =
    mode !== 'turn'
    ||
    !actorTeamId;

  if (
    mode === 'turn'
    &&
    actorTeamId
  ) {
    liveUi.passBadge.textContent =
      `PASS ${
        Number(
          actorState?.passes_used
          || 0
        )
      }/5`;
  }

  liveUi.hold.hidden =
    !liveIsController();

  if (
    liveIsController()
  ) {
    liveUi.hold.textContent =
      session.hold_active === true
        ? 'Riprendi'
        : 'HOLD';
  }

  let canBid =
    Boolean(
      actorTeamId
      &&
      actorTeamId
      !==
      session.current_bidder_team_id
      &&
      capacity
      &&
      capacity.allowed === true
      &&
      Number(
        capacity.max_bid || 0
      )
      >=
      nextValidBid()
    );

  if (
    mode === 'wild'
    &&
    !liveIsPresident()
  ) {
    canBid =
      false;
  }

  liveUi.controls.hidden =
    !canBid;

  if (!canBid) {
    liveUi.turnActions.hidden =
      true;

    if (
      actorTeamId
      &&
      capacity
      &&
      capacity.allowed !== true
    ) {
      liveUi.help.textContent =
        `Offerta non disponibile: ${
          capacityReasonLabel(
            capacity.reason
          )
        }.`;

    } else if (
      actorTeamId
      &&
      capacity
      &&
      Number(
        capacity.max_bid || 0
      )
      <
      nextValidBid()
    ) {
      liveUi.help.textContent =
        `Massimo spendibile ${capacity.max_bid}: impossibile rilanciare.`;

    } else if (
      mode === 'turn'
      &&
      !turnTeam
    ) {
      liveUi.help.textContent =
        'Nessuna squadra attiva: attesa Banditore.';

    } else if (
      mode === 'turn'
      &&
      turnTeam
    ) {
      liveUi.help.textContent =
        `In attesa di ${turnTeam.name}.`;

    } else {
      liveUi.help.textContent =
        '';
    }

    renderPresidentPickerMode();
    renderLiveTimer();

    return;
  }

  const maxBid =
    Math.max(
      0,
      Number(
        capacity.max_bid || 0
      )
    );

  rebuildPickerOptions(
    liveUi.bidAmount,
    maxBid
  );

  if (
    presidentPickerMode === 'auto'
  ) {
    setPickerValue(
      liveUi.bidAmount,
      nextValidBid()
    );
  }

  liveUi.maxBid.textContent =
    `Max ${maxBid}`;

  renderPresidentPickerMode();

  if (
    mode === 'turn'
  ) {
    liveUi.turnActions.hidden =
      false;

    const passes =
      Number(
        actorState?.passes_used
        || 0
      );

    liveUi.pass.disabled =
      passes >= 5;

    liveUi.help.textContent =
      liveIsPresident()
      &&
      liveMyTeamId() === actorTeamId
        ? (
            leader
              ? `È il tuo turno. ${leader.name} è in testa a ${session.current_bid}.`
              : 'È il tuo turno: puoi rilanciare, passare o abbandonare.'
          )
        : `Proxy Banditore per ${turnTeam?.name || 'squadra attiva'}.`;

  } else {
    liveUi.turnActions.hidden =
      true;

    liveUi.help.textContent =
      leader
        ? `${leader.name} è in testa a ${session.current_bid}.`
        : `Prima offerta valida: ${nextValidBid()}.`;
  }

  renderLiveTimer();
}

function auctioneerSelectedAmount() {
  return Number(
    auctioneerUi.amount?.value
    || 0
  );
}

function auctioneerIsCorrection() {
  const session =
    liveSession();

  if (
    !session
    ||
    !session.current_bidder_team_id
    ||
    session.current_bid === null
    ||
    session.current_bid === undefined
  ) {
    return false;
  }

  return (
    auctioneerSelectedAmount()
    <=
    Number(
      session.current_bid
    )
  );
}

function renderAuctioneerActionMode() {
  if (!auctioneerUi.actionMode) {
    return;
  }

  const correction =
    auctioneerIsCorrection();

  auctioneerUi.actionMode.textContent =
    correction
      ? 'CORREZIONE'
      : 'VOCALE';

  auctioneerUi.actionMode.classList.toggle(
    'warning',
    correction
  );

  auctioneerUi.actionMode.classList.toggle(
    'good',
    !correction
  );
}

function auctioneerTeamCanSubmit(teamId) {
  const session =
    liveSession();

  if (!session) {
    return false;
  }

  const amount =
    auctioneerSelectedAmount();

  const capacity =
    capacityForTeam(teamId);

  if (
    !capacity
    ||
    capacity.allowed !== true
    ||
    amount < 1
    ||
    amount
    >
    Number(
      capacity.max_bid || 0
    )
  ) {
    return false;
  }

  if (
    auctioneerIsCorrection()
  ) {
    return true;
  }

  if (
    teamId ===
    session.current_bidder_team_id
  ) {
    return false;
  }

  if (
    liveBidMode() === 'turn'
    &&
    teamId !==
    session.current_turn_team_id
  ) {
    return false;
  }

  return true;
}

function renderAuctioneerTeamButtons() {
  if (!auctioneerUi.teamButtons) {
    return;
  }

  const orderedTeams =
    (
      auctionData?.teamOrder || []
    )
      .map(
        item =>
          item.team
      )
      .filter(Boolean);

  const teams =
    orderedTeams.length
      ? orderedTeams
      : (
          auctionData?.teams || []
        );

  auctioneerUi.teamButtons.innerHTML =
    teams
      .map(
        team => {
          const capacity =
            capacityForTeam(
              team.id
            );

          const maxBid =
            Number(
              capacity?.max_bid
              || 0
            );

          const enabled =
            auctioneerTeamCanSubmit(
              team.id
            );

          const subtitle =
            capacity?.allowed === true
              ? `max ${maxBid}`
              : capacityReasonLabel(
                  capacity?.reason
                );

          return `
            <button
              type="button"
              class="secondary"
              data-auctioneer-team="${escapeHtml(team.id)}"
              ${enabled ? '' : 'disabled'}
            >
              ${escapeHtml(team.name)}
              ·
              ${escapeHtml(subtitle)}
            </button>
          `;
        }
      )
      .join('');
}

function renderRecentBids() {
  if (!auctioneerUi.recent) {
    return;
  }

  const bids =
    auctionData?.recentBids || [];

  if (!bids.length) {
    auctioneerUi.recent.innerHTML = `
      <div class="empty-state">
        Nessuna offerta registrata.
      </div>
    `;

    return;
  }

  auctioneerUi.recent.innerHTML =
    bids
      .map(
        bid => `
          <div class="setting-row">

            <span>

              <strong>
                ${escapeHtml(
                  bid.team?.name
                  || 'Squadra'
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

function renderAuctioneerPanel() {
  if (!auctioneerUi.panel) {
    return;
  }

  resetPickersForNewPlayer();

  const session =
    liveSession();

  const player =
    auctionData?.currentPlayer;

  const show =
    Boolean(
      session
      &&
      session.status === 'live'
      &&
      player
      &&
      liveIsController()
    );

  auctioneerUi.panel.hidden =
    !show;

  if (!show) {
    auctioneerPickerMode =
      'auto';

    return;
  }

  rebuildPickerOptions(
    auctioneerUi.amount,
    maxCapacityAcrossTeams()
  );

  if (
    auctioneerPickerMode === 'auto'
  ) {
    setPickerValue(
      auctioneerUi.amount,
      nextValidBid()
    );
  }

  renderAuctioneerPickerMode();
  renderAuctioneerActionMode();
  renderAuctioneerTeamButtons();
  renderRecentBids();

  const leader =
    auctionData?.currentBidderTeam;

  const selected =
    auctioneerSelectedAmount();

  if (
    auctioneerIsCorrection()
  ) {
    auctioneerUi.help.textContent =
      `Importo ${selected}: verrà registrato come CORREZIONE BANDITORE.`;

  } else if (leader) {
    auctioneerUi.help.textContent =
      `${leader.name} guida a ${session.current_bid}. Tocca la squadra che ha rilanciato.`;

  } else {
    auctioneerUi.help.textContent =
      `Prima offerta valida: ${nextValidBid()}. Tocca la squadra offerente.`;
  }

  auctioneerUi.award.disabled =
    !leader
    ||
    !session.current_bid;

  if (
    auctioneerUi.finishTest
  ) {
    auctioneerUi.finishTest.hidden =
      session.is_test !== true;
  }
}

liveUi.hold?.addEventListener(
  'click',
  async () => {
    const session =
      liveSession();

    if (!session) {
      return;
    }

    liveUi.hold.disabled =
      true;

    try {
      const result =
        await callApi({
          action:
            'setHold',

          sessionId:
            session.id,

          hold:
            session.hold_active !== true
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile modificare HOLD.'
        );
      }

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante HOLD.',
        'error'
      );

    } finally {
      liveUi.hold.disabled =
        false;
    }
  }
);

liveUi.bid?.addEventListener(
  'click',
  async () => {
    const session =
      liveSession();

    const teamId =
      liveActorTeamId();

    const amount =
      Number(
        liveUi.bidAmount.value
      );

    if (
      !session
      ||
      !teamId
    ) {
      showMessage(
        'Non puoi rilanciare in questo momento.',
        'error'
      );

      return;
    }

    const capacity =
      capacityForTeam(teamId);

    if (
      !capacity
      ||
      capacity.allowed !== true
    ) {
      showMessage(
        'La squadra non può acquistare questo giocatore.',
        'error'
      );

      return;
    }

    if (
      amount < nextValidBid()
    ) {
      showMessage(
        'Offerta superata.',
        'error'
      );

      return;
    }

    if (
      amount
      >
      Number(
        capacity.max_bid || 0
      )
    ) {
      showMessage(
        `Offerta massima consentita: ${capacity.max_bid}.`,
        'error'
      );

      return;
    }

    liveUi.bid.disabled =
      true;

    try {
      const result =
        await callApi({
          action:
            'placeBid',

          sessionId:
            session.id,

          teamId,

          amount,

          source:
            liveIsController()
            &&
            !(
              liveIsPresident()
              &&
              liveMyTeamId() === teamId
            )
              ? 'VOCALE'
              : 'APP'
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile registrare l’offerta.'
        );
      }

      presidentPickerMode =
        'auto';

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante il rilancio.',
        'error'
      );

    } finally {
      liveUi.bid.disabled =
        false;
    }
  }
);

auctioneerUi.teamButtons?.addEventListener(
  'click',
  async event => {
    const button =
      event.target.closest(
        '[data-auctioneer-team]'
      );

    if (
      !button
      ||
      button.disabled
    ) {
      return;
    }

    const session =
      liveSession();

    const teamId =
      button.dataset.auctioneerTeam;

    const amount =
      auctioneerSelectedAmount();

    if (
      !session
      ||
      !teamId
      ||
      !Number.isInteger(amount)
      ||
      amount < 1
    ) {
      return;
    }

    button.disabled =
      true;

    try {
      const correction =
        auctioneerIsCorrection();

      const result =
        await callApi({
          action:
            correction
              ? 'correctBid'
              : 'placeBid',

          sessionId:
            session.id,

          teamId,

          amount,

          ...(
            correction
              ? {}
              : {
                  source:
                    'VOCALE'
                }
          )
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          (
            correction
              ? 'Impossibile correggere l’offerta.'
              : 'Impossibile registrare l’offerta.'
          )
        );
      }

      auctioneerPickerMode =
        'auto';

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore nel pannello Banditore.',
        'error'
      );

    } finally {
      button.disabled =
        false;
    }
  }
);

auctioneerUi.award?.addEventListener(
  'click',
  async () => {
    const session =
      liveSession();

    const leader =
      auctionData?.currentBidderTeam;

    if (
      !session
      ||
      !leader
      ||
      !session.current_bid
    ) {
      showMessage(
        'Non c’è un leader da aggiudicare.',
        'error'
      );

      return;
    }

    auctioneerUi.award.disabled =
      true;

    const playerName =
      auctionData?.currentPlayer?.name
      ||
      'Giocatore';

    const price =
      session.current_bid;

    try {
      const result =
        await callApi({
          action:
            'awardPlayer',

          sessionId:
            session.id
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile confermare l’aggiudicazione.'
        );
      }

      presidentPickerMode =
        'auto';

      auctioneerPickerMode =
        'auto';

      showMessage(
        `${playerName} aggiudicato a ${leader.name} per ${price}.`,
        'success'
      );

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante l’aggiudicazione.',
        'error'
      );

    } finally {
      auctioneerUi.award.disabled =
        false;
    }
  }
);

liveUi.pass?.addEventListener(
  'click',
  async () => {
    const session =
      liveSession();

    const teamId =
      liveActorTeamId();

    if (
      !session
      ||
      !teamId
    ) {
      return;
    }

    liveUi.pass.disabled =
      true;

    try {
      const result =
        await callApi({
          action:
            'passTurn',

          sessionId:
            session.id,

          teamId
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile passare.'
        );
      }

      presidentPickerMode =
        'auto';

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante PASSA.',
        'error'
      );

    } finally {
      liveUi.pass.disabled =
        false;
    }
  }
);

liveUi.abandon?.addEventListener(
  'click',
  async () => {
    const session =
      liveSession();

    const teamId =
      liveActorTeamId();

    if (
      !session
      ||
      !teamId
    ) {
      return;
    }

    const confirmed =
      window.confirm(
        'Abbandonare definitivamente l’asta di questo giocatore per la squadra attiva?'
      );

    if (!confirmed) {
      return;
    }

    liveUi.abandon.disabled =
      true;

    try {
      const result =
        await callApi({
          action:
            'abandonTurn',

          sessionId:
            session.id,

          teamId
        });

      if (!result?.ok) {
        throw new Error(
          result?.error
          ||
          'Impossibile abbandonare.'
        );
      }

      presidentPickerMode =
        'auto';

      await loadLobby();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        ||
        'Errore durante ABBANDONA.',
        'error'
      );

    } finally {
      liveUi.abandon.disabled =
        false;
    }
  }
);

function renderAuctionLiveControls() {
  renderLiveControls();
  renderAuctioneerPanel();
}

async function refreshLiveAuctionState() {
  if (
    livePolling
    ||
    document.hidden
  ) {
    return;
  }

  const session =
    liveSession();

  if (
    !session
    ||
    session.status !== 'live'
  ) {
    return;
  }

  livePolling =
    true;

  try {
    const data =
      await callApi({
        action:
          'getLobby'
      });

    if (!data?.ok) {
      return;
    }

    auctionData =
      data;

    leagueTitle.textContent =
      `Asta · ${data.league.name}`;

    leagueSubtitle.textContent =
      `Sessione ${
        sessionStatusLabel(
          data.auctionSession?.status
        )
      }`;

    renderAll();
    renderAuctionLiveControls();

    if (
      typeof renderAuctionTestAddon
      === 'function'
    ) {
      renderAuctionTestAddon();
    }

  } catch (error) {
    console.error(error);

  } finally {
    livePolling =
      false;
  }
}

setInterval(
  renderLiveTimer,
  250
);

setInterval(
  refreshLiveAuctionState,
  1800
);

const baseLiveLoadLobby =
  loadLobby;

loadLobby =
  async function () {
    await baseLiveLoadLobby();
    renderAuctionLiveControls();
  };

const initialLiveRender =
  setInterval(
    () => {
      if (!auctionData) {
        return;
      }

      clearInterval(
        initialLiveRender
      );

      renderAuctionLiveControls();
    },
    100
  );
