/* =========================================================
   auction-vice.js
   - Segnali privati Vice -> Presidente
   - refresh automatico lobby non-live
   - integrazione tab TV
   ========================================================= */

const viceUi = {
  panel: document.getElementById('vice-signal-panel'),
  current: document.getElementById('vice-signal-current'),
  controls: document.getElementById('vice-signal-controls'),
  push: document.getElementById('vice-signal-push'),
  stop: document.getElementById('vice-signal-stop'),
  limit: document.getElementById('vice-signal-limit'),
  limitSend: document.getElementById('vice-signal-limit-send'),
  clear: document.getElementById('vice-signal-clear')
}

const vicePresenterTab =
  document.getElementById('presenter-tab')

let vicePolling = false
let viceLastLobbyRefreshAt = 0


/* =========================================================
   STATO
   ========================================================= */

function viceIsPresident() {
  return auctionData?.permissions?.isPresident === true
}

function viceIsVice() {
  return auctionData?.permissions?.isVice === true
}

function viceMyTeamId() {
  return auctionData?.myTeam?.teamId || null
}

function viceSession() {
  return auctionData?.auctionSession || null
}


/* =========================================================
   TAB TV
   ========================================================= */

function viceRenderPresenterTab() {
  if (!vicePresenterTab) return

  vicePresenterTab.hidden = !Boolean(
    auctionData?.permissions?.isPresenter
    || auctionData?.permissions?.isLeagueAdmin
    || auctionData?.permissions?.isAuctioneer
    || auctionData?.permissions?.isSuperAdmin
  )
}


/* =========================================================
   SEGNALE VICE
   ========================================================= */

function viceSignalLabel(signal) {
  if (!signal) return 'Nessun segnale'
  if (signal.type === 'push') return 'RILANCIA'
  if (signal.type === 'stop') return 'STOP'

  if (signal.type === 'limit') {
    return `FINO A ${Number(signal.amount || 0)}`
  }

  return 'Nessun segnale'
}

function viceRebuildLimitOptions() {
  const select = viceUi.limit
  if (!select) return

  const myTeamId = viceMyTeamId()

  const capacity =
    (auctionData?.bidCapacities || [])
      .find(item => item.team_id === myTeamId)
    || null

  const session = viceSession()
  const currentBid = Number(session?.current_bid || 0)
  const hasLeader = Boolean(session?.current_bidder_team_id)

  const minimum = Math.max(
    1,
    hasLeader
      ? currentBid + 1
      : currentBid || 1
  )

  const maximum = Math.max(
    minimum,
    Number(capacity?.max_bid || minimum)
  )

  if (
    Number(select.dataset.min || -1) === minimum
    && Number(select.dataset.max || -1) === maximum
  ) {
    return
  }

  select.innerHTML = ''

  const fragment =
    document.createDocumentFragment()

  for (
    let amount = minimum;
    amount <= maximum;
    amount += 1
  ) {
    const option =
      document.createElement('option')

    option.value = String(amount)
    option.textContent = String(amount)

    fragment.appendChild(option)
  }

  select.appendChild(fragment)

  select.dataset.min = String(minimum)
  select.dataset.max = String(maximum)
}

function viceRenderSignal() {
  const panel = viceUi.panel
  if (!panel) return

  const session = viceSession()
  const player = auctionData?.currentPlayer || null

  const show = Boolean(
    session
    && session.status === 'live'
    && player
    && viceMyTeamId()
    && (
      viceIsPresident()
      || viceIsVice()
    )
  )

  panel.hidden = !show
  if (!show) return

  const signal =
    auctionData?.viceSignal || null

  const isVice =
    viceIsVice()

  viceUi.controls.hidden =
    !isVice

  if (!signal) {
    viceUi.current.innerHTML = `
      <div class="list-row vice-signal-empty">
        <div class="list-row-main">
          <div class="list-row-title">
            <strong>Nessun segnale</strong>
            <small>
              ${
                isVice
                  ? 'Invia un suggerimento al Presidente.'
                  : 'Il Vice non ha inviato suggerimenti per questo giocatore.'
              }
            </small>
          </div>
        </div>
      </div>
    `
  } else {
    const signalClass =
      signal.type === 'stop'
        ? 'warning'
        : signal.type === 'push'
          ? 'good'
          : ''

    viceUi.current.innerHTML = `
      <div class="list-row vice-signal-active">
        <div class="list-row-main">
          <div class="list-row-title">
            <strong>
              ${escapeHtml(signal.viceUsername || 'Vice')}
            </strong>

            <small>
              Segnale per
              ${escapeHtml(player.name || 'il giocatore corrente')}
            </small>
          </div>

          <span class="badge ${signalClass}">
            ${escapeHtml(viceSignalLabel(signal))}
          </span>
        </div>
      </div>
    `
  }

  if (isVice) {
    viceRebuildLimitOptions()
  }
}


/* =========================================================
   INVIO SEGNALE
   ========================================================= */

async function viceSendSignal(
  signalType,
  amount = null,
  button = null
) {
  const session =
    viceSession()

  if (
    !session
    || session.status !== 'live'
    || !auctionData?.currentPlayer
  ) {
    showMessage(
      'Nessun giocatore attualmente all’asta.',
      'error'
    )
    return
  }

  if (!viceIsVice()) {
    showMessage(
      'Solo il Vice può inviare segnali.',
      'error'
    )
    return
  }

  if (button) {
    button.disabled = true
  }

  try {
    const result =
      await callApi({
        action: 'sendViceSignal',
        signalType,
        amount
      })

    if (!result?.ok) {
      throw new Error(
        result?.error
        || 'Impossibile inviare il segnale.'
      )
    }

    showMessage('')

    await viceRefreshAuction(true)

  } catch (error) {
    console.error(error)

    showMessage(
      error.message
      || 'Errore durante l’invio del segnale.',
      'error'
    )

  } finally {
    if (button) {
      button.disabled = false
    }
  }
}

viceUi.push?.addEventListener(
  'click',
  () =>
    viceSendSignal(
      'push',
      null,
      viceUi.push
    )
)

viceUi.stop?.addEventListener(
  'click',
  () =>
    viceSendSignal(
      'stop',
      null,
      viceUi.stop
    )
)

viceUi.limitSend?.addEventListener(
  'click',
  () => {
    const amount =
      Number(viceUi.limit?.value || 0)

    if (
      !Number.isInteger(amount)
      || amount < 1
    ) {
      showMessage(
        'Seleziona un limite valido.',
        'error'
      )
      return
    }

    viceSendSignal(
      'limit',
      amount,
      viceUi.limitSend
    )
  }
)

viceUi.clear?.addEventListener(
  'click',
  () =>
    viceSendSignal(
      'clear',
      null,
      viceUi.clear
    )
)


/* =========================================================
   RENDER AGGIUNTIVO
   ========================================================= */

function viceRender() {
  viceRenderPresenterTab()
  viceRenderSignal()
}

/*
 * auction-live-controls.js richiama renderAuctionLiveControls()
 * a ogni aggiornamento live.
 * Lo estendiamo senza sostituire il file precedente.
 */
if (
  typeof renderAuctionLiveControls
  === 'function'
) {
  const viceBaseRenderAuctionLiveControls =
    renderAuctionLiveControls

  renderAuctionLiveControls =
    function () {
      viceBaseRenderAuctionLiveControls()
      viceRender()
    }
}

/*
 * Aggancio anche loadLobby(), così il pannello viene aggiornato
 * dopo azioni manuali e durante la preparazione.
 */
if (
  typeof loadLobby
  === 'function'
) {
  const viceBaseLoadLobby =
    loadLobby

  loadLobby =
    async function () {
      await viceBaseLoadLobby()
      viceRender()
    }
}


/* =========================================================
   REFRESH AUTOMATICO
   ========================================================= */

async function viceRefreshAuction(
  force = false
) {
  if (
    vicePolling
    || document.hidden
  ) {
    return
  }

  const status =
    viceSession()?.status || null

  /*
   * LIVE ha già il polling rapido del file live-controls.
   * PREPARED non viene aggiornato automaticamente perché
   * l'Admin potrebbe stare riordinando le squadre.
   */
  if (
    !force
    && (
      status === 'live'
      || status === 'prepared'
    )
  ) {
    return
  }

  const now =
    Date.now()

  if (
    !force
    && (
      now
      - viceLastLobbyRefreshAt
    ) < 5000
  ) {
    return
  }

  vicePolling = true
  viceLastLobbyRefreshAt = now

  try {
    await loadLobby()

  } catch (error) {
    console.error(error)

  } finally {
    vicePolling = false
  }
}

setInterval(
  () =>
    viceRefreshAuction(),
  1000
)

document.addEventListener(
  'visibilitychange',
  () => {
    if (!document.hidden) {
      viceRefreshAuction(true)
    }
  }
)

window.addEventListener(
  'focus',
  () =>
    viceRefreshAuction(true)
)


/* Primo render nel caso i dati siano già arrivati. */
const viceInitialRender =
  setInterval(
    () => {
      if (!auctionData) return

      clearInterval(
        viceInitialRender
      )

      viceRender()
    },
    100
  )
