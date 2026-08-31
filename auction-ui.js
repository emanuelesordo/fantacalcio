/* =========================================================
   auction-ui.js
   Layout dedicato dell'asta live.

   Quando la sessione passa a LIVE:
   - nasconde header, menu, lobby, KPI e sezioni non operative
   - mantiene visibili solo chiamata / giocatore / rilanci /
     Banditore / Vice
   - blocca lo scroll della pagina principale
   - assegna lo scroll ai contenitori operativi
   ========================================================= */

let auctionUiLastMode = null


function auctionUiApplyMode() {

  if (
    typeof auctionData
    === 'undefined'
  ) {
    return
  }


  const session =
    auctionData
      ?.auctionSession
    || null


  const isLive =
    session?.status
    === 'live'


  const isCallMode =
    Boolean(
      isLive
      &&
      !session?.current_player_id
    )


  const isBidMode =
    Boolean(
      isLive
      &&
      session?.current_player_id
    )


  document.body
    .classList
    .toggle(
      'auction-live-mode',
      isLive
    )


  document.body
    .classList
    .toggle(
      'auction-call-mode',
      isCallMode
    )


  document.body
    .classList
    .toggle(
      'auction-bid-mode',
      isBidMode
    )


  const nextMode =
    isCallMode
      ? 'call'
      : isBidMode
        ? 'bid'
        : 'lobby'


  /*
   * Quando cambia fase riportiamo all'inizio
   * soltanto i contenitori interni.
   * La pagina non viene fatta scorrere.
   */
  if (
    nextMode
    !== auctionUiLastMode
  ) {

    auctionUiLastMode =
      nextMode


    document
      .getElementById(
        'live-section'
      )
      ?.scrollTo({
        top: 0,
        behavior: 'instant'
      })


    document
      .getElementById(
        'call-candidates'
      )
      ?.scrollTo({
        top: 0,
        behavior: 'instant'
      })
  }
}


/*
 * Estendiamo il caricamento centrale senza modificare
 * il motore esistente.
 */
if (
  typeof loadLobby
  === 'function'
) {

  const auctionUiBaseLoadLobby =
    loadLobby


  loadLobby =
    async function () {

      await auctionUiBaseLoadLobby()

      auctionUiApplyMode()
    }
}


/*
 * Il primo load può essere partito prima del caricamento
 * di questo add-on.
 */
const auctionUiInitialRender =
  setInterval(
    () => {

      if (
        typeof auctionData
        === 'undefined'
        ||
        !auctionData
      ) {
        return
      }


      clearInterval(
        auctionUiInitialRender
      )


      auctionUiApplyMode()
    },
    100
  )


/*
 * Fallback leggerissimo: intercetta anche aggiornamenti
 * del live polling che non passano da loadLobby().
 */
setInterval(
  auctionUiApplyMode,
  500
)
