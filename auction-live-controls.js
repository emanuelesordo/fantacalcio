/* auction-live-controls.js
   Timer server-side, HOLD e rilanci a turno.
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
  bid: document.getElementById('live-bid-button'),
  turnActions: document.getElementById('live-turn-actions'),
  pass: document.getElementById('live-pass-button'),
  abandon: document.getElementById('live-abandon-button'),
  help: document.getElementById('live-action-help')
};

let liveServerOffsetMs = 0;
let liveTimerSyncing = false;
let livePolling = false;
let liveLastBid = null;


function liveSession() {
  return auctionData?.auctionSession || null;
}


function liveSettings() {
  return liveSession()?.setup_snapshot || auctionData?.settings || {};
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
  return auctionData?.permissions?.canControlAuction === true;
}


function liveIsPresident() {
  return auctionData?.permissions?.isPresident === true;
}


function liveTeamState(teamId) {
  return (auctionData?.teamOrder || [])
    .find(item => item.team_id === teamId) || null;
}


function updateLiveServerOffset() {
  const serverNow = Date.parse(auctionData?.serverNow || '');

  if (Number.isFinite(serverNow)) {
    liveServerOffsetMs = serverNow - Date.now();
  }
}


function liveNowMs() {
  return Date.now() + liveServerOffsetMs;
}


function liveRemainingMs() {
  const session = liveSession();

  if (!session) return null;

  if (session.hold_active === true) {
    const seconds = Number(session.hold_remaining_seconds);

    return Number.isFinite(seconds)
      ? Math.max(0, seconds * 1000)
      : null;
  }

  if (!session.timer_deadline) return null;

  const deadline = Date.parse(session.timer_deadline);

  return Number.isFinite(deadline)
    ? Math.max(0, deadline - liveNowMs())
    : null;
}


function formatLiveTimer(milliseconds) {
  if (milliseconds === null || milliseconds === undefined) {
    return '—';
  }

  return `${Math.max(0, Math.ceil(milliseconds / 1000))}s`;
}


async function syncExpiredLiveTimer() {
  const session = liveSession();

  if (
    !session
    || liveTimerSyncing
    || session.status !== 'live'
    || session.hold_active === true
    || session.timer_expired_at
    || !session.timer_deadline
  ) {
    return;
  }

  const remaining = liveRemainingMs();

  if (remaining === null || remaining > 0) return;

  liveTimerSyncing = true;

  try {
    const result = await callApi({
      action: 'syncTimer',
      sessionId: session.id
    });

    if (result?.ok) {
      await refreshLiveAuctionState();
    }
  } catch (error) {
    console.error(error);
  } finally {
    liveTimerSyncing = false;
  }
}


function renderLiveTimer() {
  if (!liveUi.timerValue || !liveUi.timerStatus) return;

  const session = liveSession();

  if (!session || session.status !== 'live') {
    liveUi.timerValue.textContent = '—';
    liveUi.timerStatus.textContent = 'In attesa';
    return;
  }

  if (session.hold_active === true) {
    liveUi.timerValue.textContent = formatLiveTimer(liveRemainingMs());
    liveUi.timerStatus.textContent = 'HOLD — timer sospeso';
    return;
  }

  if (session.timer_expired_at) {
    liveUi.timerValue.textContent = '0s';
    liveUi.timerStatus.textContent =
      'TIMER SCADUTO — ATTESA BANDITORE';
    return;
  }

  const remaining = liveRemainingMs();

  if (remaining === null) {
    liveUi.timerValue.textContent = '—';
    liveUi.timerStatus.textContent = session.current_bidder_team_id
      ? 'Timer non avviato'
      : 'In attesa della prima offerta';
    return;
  }

  liveUi.timerValue.textContent = formatLiveTimer(remaining);
  liveUi.timerStatus.textContent = 'Tempo residuo';

  if (remaining <= 0) {
    syncExpiredLiveTimer();
  }
}


function liveActorTeamId() {
  const session = liveSession();

  if (!session) return null;

  const myTeamId = liveMyTeamId();

  if (liveBidMode() === 'turn') {
    const turnTeam = liveCurrentTurnTeam();

    if (!turnTeam) return null;

    if (liveIsPresident() && myTeamId === turnTeam.id) {
      return turnTeam.id;
    }

    if (liveIsController()) {
      return turnTeam.id;
    }

    return null;
  }

  if (liveIsPresident() && myTeamId) {
    return myTeamId;
  }

  return null;
}


function renderLiveControls() {
  if (!liveUi.panel) return;

  updateLiveServerOffset();

  const session = liveSession();
  const player = auctionData?.currentPlayer;

  const show = Boolean(
    session
    && session.status === 'live'
    && player
  );

  liveUi.panel.hidden = !show;

  if (!show) return;

  const mode = liveBidMode();
  const turnTeam = liveCurrentTurnTeam();
  const leader = auctionData?.currentBidderTeam;
  const actorTeamId = liveActorTeamId();
  const actorState = actorTeamId
    ? liveTeamState(actorTeamId)
    : null;

  liveUi.turnBadge.hidden = mode !== 'turn';

  if (mode === 'turn') {
    liveUi.turnBadge.textContent = turnTeam
      ? `Turno: ${turnTeam.name}`
      : 'Nessun turno attivo';
  }

  liveUi.passBadge.hidden =
    mode !== 'turn' || !actorTeamId;

  if (mode === 'turn' && actorTeamId) {
    liveUi.passBadge.textContent =
      `PASS ${Number(actorState?.passes_used || 0)}/5`;
  }

  liveUi.hold.hidden = !liveIsController();

  if (liveIsController()) {
    liveUi.hold.textContent =
      session.hold_active === true
        ? 'Riprendi'
        : 'HOLD';
  }

  let canBid = Boolean(
    actorTeamId
    && actorTeamId !== session.current_bidder_team_id
  );

  if (mode === 'wild' && !liveIsPresident()) {
    canBid = false;
  }

  liveUi.controls.hidden = !canBid;

  if (!canBid) {
    liveUi.turnActions.hidden = true;

    if (mode === 'turn' && !turnTeam) {
      liveUi.help.textContent =
        'Nessuna squadra attiva: attesa Banditore.';
    } else if (mode === 'turn' && turnTeam) {
      liveUi.help.textContent =
        `In attesa di ${turnTeam.name}.`;
    } else {
      liveUi.help.textContent = '';
    }

    renderLiveTimer();
    return;
  }

  const minimum = Math.max(
    1,
    Number(session.current_bid || 0) + 1
  );

  liveUi.bidAmount.min = String(minimum);

  if (
    liveLastBid !== session.current_bid
    || !liveUi.bidAmount.value
    || Number(liveUi.bidAmount.value) < minimum
  ) {
    liveUi.bidAmount.value = String(minimum);
    liveLastBid = session.current_bid;
  }

  if (mode === 'turn') {
    liveUi.turnActions.hidden = false;

    const passes = Number(actorState?.passes_used || 0);

    liveUi.pass.disabled = passes >= 5;

    if (
      liveIsPresident()
      && liveMyTeamId() === actorTeamId
    ) {
      liveUi.help.textContent = leader
        ? `È il tuo turno. ${leader.name} è in testa a ${session.current_bid}.`
        : 'È il tuo turno: puoi rilanciare, passare o abbandonare.';
    } else {
      liveUi.help.textContent =
        `Pannello proxy Banditore per ${turnTeam?.name || 'squadra attiva'}.`;
    }
  } else {
    liveUi.turnActions.hidden = true;

    liveUi.help.textContent = leader
      ? `${leader.name} è in testa a ${session.current_bid}.`
      : 'Inserisci la prima offerta.';
  }

  renderLiveTimer();
}


liveUi.hold?.addEventListener('click', async () => {
  const session = liveSession();

  if (!session) return;

  liveUi.hold.disabled = true;

  try {
    const result = await callApi({
      action: 'setHold',
      sessionId: session.id,
      hold: session.hold_active !== true
    });

    if (!result?.ok) {
      throw new Error(
        result?.error || 'Impossibile modificare HOLD.'
      );
    }

    await loadLobby();

  } catch (error) {
    console.error(error);

    showMessage(
      error.message || 'Errore durante HOLD.',
      'error'
    );

  } finally {
    liveUi.hold.disabled = false;
  }
});


liveUi.bid?.addEventListener('click', async () => {
  const session = liveSession();
  const teamId = liveActorTeamId();
  const amount = Number(liveUi.bidAmount.value);

  if (!session || !teamId) {
    showMessage(
      'Non puoi rilanciare in questo momento.',
      'error'
    );
    return;
  }

  const minimum = Math.max(
    1,
    Number(session.current_bid || 0) + 1
  );

  if (!Number.isInteger(amount) || amount < minimum) {
    showMessage('Offerta superata.', 'error');
    return;
  }

  liveUi.bid.disabled = true;

  try {
    const result = await callApi({
      action: 'placeBid',
      sessionId: session.id,
      teamId,
      amount,
      source:
        liveIsController()
        && !(
          liveIsPresident()
          && liveMyTeamId() === teamId
        )
          ? 'VOCALE'
          : 'APP'
    });

    if (!result?.ok) {
      throw new Error(
        result?.error || 'Impossibile registrare l’offerta.'
      );
    }

    await loadLobby();

  } catch (error) {
    console.error(error);

    showMessage(
      error.message || 'Errore durante il rilancio.',
      'error'
    );

  } finally {
    liveUi.bid.disabled = false;
  }
});


liveUi.pass?.addEventListener('click', async () => {
  const session = liveSession();
  const teamId = liveActorTeamId();

  if (!session || !teamId) return;

  liveUi.pass.disabled = true;

  try {
    const result = await callApi({
      action: 'passTurn',
      sessionId: session.id,
      teamId
    });

    if (!result?.ok) {
      throw new Error(
        result?.error || 'Impossibile passare.'
      );
    }

    await loadLobby();

  } catch (error) {
    console.error(error);

    showMessage(
      error.message || 'Errore durante PASSA.',
      'error'
    );

  } finally {
    liveUi.pass.disabled = false;
  }
});


liveUi.abandon?.addEventListener('click', async () => {
  const session = liveSession();
  const teamId = liveActorTeamId();

  if (!session || !teamId) return;

  const confirmed = window.confirm(
    'Abbandonare definitivamente l’asta di questo giocatore per la squadra attiva?'
  );

  if (!confirmed) return;

  liveUi.abandon.disabled = true;

  try {
    const result = await callApi({
      action: 'abandonTurn',
      sessionId: session.id,
      teamId
    });

    if (!result?.ok) {
      throw new Error(
        result?.error || 'Impossibile abbandonare.'
      );
    }

    await loadLobby();

  } catch (error) {
    console.error(error);

    showMessage(
      error.message || 'Errore durante ABBANDONA.',
      'error'
    );

  } finally {
    liveUi.abandon.disabled = false;
  }
});


async function refreshLiveAuctionState() {
  if (livePolling || document.hidden) return;

  const session = liveSession();

  if (!session || session.status !== 'live') return;

  livePolling = true;

  try {
    const data = await callApi({
      action: 'getLobby'
    });

    if (!data?.ok) return;

    auctionData = data;

    leagueTitle.textContent =
      `Asta · ${data.league.name}`;

    leagueSubtitle.textContent =
      `Sessione ${sessionStatusLabel(
        data.auctionSession?.status
      )}`;

    renderAll();
    renderLiveControls();

    if (typeof renderAuctionTestAddon === 'function') {
      renderAuctionTestAddon();
    }

  } catch (error) {
    console.error(error);

  } finally {
    livePolling = false;
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


loadLobby = async function () {
  await baseLiveLoadLobby();
  renderLiveControls();
};


const initialLiveRender =
  setInterval(
    () => {
      if (!auctionData) return;

      clearInterval(
        initialLiveRender
      );

      renderLiveControls();
    },
    100
  );
