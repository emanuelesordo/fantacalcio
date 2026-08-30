const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/league-api`


let selectedLeague = null


const form =
  document.getElementById(
    'setup-form'
  )

const message =
  document.getElementById(
    'page-message'
  )

const leagueTitle =
  document.getElementById(
    'league-title'
  )


/* =========================================================
   FORMATO
   ========================================================= */

const fantasyMode =
  document.getElementById(
    'fantasy-mode'
  )

const initialCredits =
  document.getElementById(
    'initial-credits'
  )

const teamCount =
  document.getElementById(
    'team-count'
  )


/* =========================================================
   CLASSIC
   ========================================================= */

const classicRoster =
  document.getElementById(
    'classic-roster'
  )

const slotP =
  document.getElementById(
    'slot-p'
  )

const slotD =
  document.getElementById(
    'slot-d'
  )

const slotC =
  document.getElementById(
    'slot-c'
  )

const slotA =
  document.getElementById(
    'slot-a'
  )


/* =========================================================
   MANTRA
   ========================================================= */

const mantraRoster =
  document.getElementById(
    'mantra-roster'
  )

const mantraGkMin =
  document.getElementById(
    'mantra-gk-min'
  )

const mantraGkMax =
  document.getElementById(
    'mantra-gk-max'
  )

const mantraOutfieldMin =
  document.getElementById(
    'mantra-outfield-min'
  )

const mantraOutfieldMax =
  document.getElementById(
    'mantra-outfield-max'
  )

const mantraTotalMin =
  document.getElementById(
    'mantra-total-min'
  )

const mantraTotalMax =
  document.getElementById(
    'mantra-total-max'
  )


/* =========================================================
   UNDER
   ========================================================= */

const underEnabled =
  document.getElementById(
    'under-enabled'
  )

const underSettings =
  document.getElementById(
    'under-settings'
  )

const underMinCount =
  document.getElementById(
    'under-min-count'
  )


/* =========================================================
   CHIAMATA
   ========================================================= */

const nominationMode =
  document.getElementById(
    'nomination-mode'
  )

const listSettings =
  document.getElementById(
    'list-settings'
  )

const listSortBy =
  document.getElementById(
    'list-sort-by'
  )

const listSortDirection =
  document.getElementById(
    'list-sort-direction'
  )


/* =========================================================
   ASTA
   ========================================================= */

const auctionBaseMode =
  document.getElementById(
    'auction-base-mode'
  )

const bidMode =
  document.getElementById(
    'bid-mode'
  )

const turnSettings =
  document.getElementById(
    'turn-settings'
  )

const turnDirection =
  document.getElementById(
    'turn-direction'
  )


/* =========================================================
   TIMER
   ========================================================= */

const timerMode =
  document.getElementById(
    'timer-mode'
  )

const fixedTimerSettings =
  document.getElementById(
    'fixed-timer-settings'
  )

const dynamicTimerSettings =
  document.getElementById(
    'dynamic-timer-settings'
  )

const fixedTimerSeconds =
  document.getElementById(
    'fixed-timer-seconds'
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
   MESSAGGI
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
          method: 'POST',

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
   VISIBILITÀ CONDIZIONALE
   ========================================================= */

function updateConditionalFields() {

  classicRoster.hidden =
    fantasyMode.value
    !== 'classic'


  mantraRoster.hidden =
    fantasyMode.value
    !== 'mantra'


  underSettings.hidden =
    !underEnabled.checked


  listSettings.hidden =
    nominationMode.value
    !== 'list'


  turnSettings.hidden =
    bidMode.value
    !== 'turn'


  fixedTimerSettings.hidden =
    timerMode.value
    !== 'fixed'


  dynamicTimerSettings.hidden =
    timerMode.value
    !== 'dynamic'
}


/* =========================================================
   POPOLA FORM
   ========================================================= */

function populateForm(
  settings
) {

  fantasyMode.value =
    settings.fantasy_mode


  initialCredits.value =
    settings.initial_credits


  teamCount.value =
    settings.team_count


  /* Classic */

  slotP.value =
    settings
      .roster_config
      ?.classic
      ?.P
      ?? 3


  slotD.value =
    settings
      .roster_config
      ?.classic
      ?.D
      ?? 8


  slotC.value =
    settings
      .roster_config
      ?.classic
      ?.C
      ?? 8


  slotA.value =
    settings
      .roster_config
      ?.classic
      ?.A
      ?? 6


  /* Mantra */

  mantraGkMin.value =
    settings
      .roster_config
      ?.mantra
      ?.goalkeepers
      ?.min
      ?? 2


  mantraGkMax.value =
    settings
      .roster_config
      ?.mantra
      ?.goalkeepers
      ?.max
      ?? 3


  mantraOutfieldMin.value =
    settings
      .roster_config
      ?.mantra
      ?.outfield
      ?.min
      ?? 22


  mantraOutfieldMax.value =
    settings
      .roster_config
      ?.mantra
      ?.outfield
      ?.max
      ?? 23


  mantraTotalMin.value =
    settings
      .roster_config
      ?.mantra
      ?.total
      ?.min
      ?? 25


  mantraTotalMax.value =
    settings
      .roster_config
      ?.mantra
      ?.total
      ?.max
      ?? 25


  /* UNDER */

  underEnabled.checked =
    settings.under_enabled
    === true


  underMinCount.value =
    settings.under_min_count
    > 0
      ? settings.under_min_count
      : 1


  /* Chiamata */

  nominationMode.value =
    settings.nomination_mode


  listSortBy.value =
    settings.list_sort_by


  listSortDirection.value =
    settings.list_sort_direction


  /* Asta */

  auctionBaseMode.value =
    settings.auction_base_mode


  bidMode.value =
    settings.bid_mode


  turnDirection.value =
    settings.turn_direction


  /* Timer */

  timerMode.value =
    settings.timer_mode


  fixedTimerSeconds.value =
    settings.fixed_timer_seconds


  updateConditionalFields()
}


/* =========================================================
   VALIDAZIONE CLIENT
   ========================================================= */

function validateLocalSetup() {

  if (
    fantasyMode.value === 'mantra'
  ) {

    const gkMin =
      Number(
        mantraGkMin.value
      )

    const gkMax =
      Number(
        mantraGkMax.value
      )

    const outfieldMin =
      Number(
        mantraOutfieldMin.value
      )

    const outfieldMax =
      Number(
        mantraOutfieldMax.value
      )

    const totalMin =
      Number(
        mantraTotalMin.value
      )

    const totalMax =
      Number(
        mantraTotalMax.value
      )


    if (
      gkMin > gkMax
    ) {

      return 'Il minimo dei Portieri non può superare il massimo.'
    }


    if (
      outfieldMin > outfieldMax
    ) {

      return 'Il minimo dei giocatori di movimento non può superare il massimo.'
    }


    if (
      totalMin > totalMax
    ) {

      return 'Il minimo totale non può superare il massimo totale.'
    }


    if (
      totalMin <
      gkMin + outfieldMin
    ) {

      return (
        'Il minimo totale non può essere inferiore ' +
        'alla somma dei minimi di Portieri e giocatori di movimento.'
      )
    }


    if (
      totalMax >
      gkMax + outfieldMax
    ) {

      return (
        'Il massimo totale non può essere superiore ' +
        'alla somma dei massimi di Portieri e giocatori di movimento.'
      )
    }
  }


  if (
    underEnabled.checked
  ) {

    const underMin =
      Number(
        underMinCount.value
      )


    if (
      !Number.isInteger(underMin)
      ||
      underMin < 1
    ) {

      return 'Inserisci un numero minimo valido di giocatori UNDER.'
    }


    let rosterMaximum


    if (
      fantasyMode.value === 'classic'
    ) {

      rosterMaximum =
        Number(slotP.value)
        +
        Number(slotD.value)
        +
        Number(slotC.value)
        +
        Number(slotA.value)

    } else {

      rosterMaximum =
        Number(
          mantraTotalMax.value
        )
    }


    if (
      underMin > rosterMaximum
    ) {

      return (
        'Il numero minimo di UNDER non può superare ' +
        'la dimensione massima della rosa.'
      )
    }
  }


  return null
}


/* =========================================================
   LOAD SETUP
   ========================================================= */

async function loadSetup() {

  showMessage('')


  try {

    const data =
      await callApi({
        action:
          'getSetup'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare il Setup.',
        'error'
      )

      return
    }


    leagueTitle.textContent =
      `Setup · ${data.league.name}`


    populateForm(
      data.settings
    )


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
   SALVATAGGIO
   ========================================================= */

form.addEventListener(
  'submit',
  async event => {

    event.preventDefault()


    showMessage('')


    const localError =
      validateLocalSetup()


    if (localError) {

      showMessage(
        localError,
        'error'
      )

      return
    }


    const button =
      document.getElementById(
        'save-setup'
      )


    button.disabled =
      true


    const originalText =
      button.textContent


    button.textContent =
      'Salvataggio...'


    const setup = {

      fantasyMode:
        fantasyMode.value,


      initialCredits:
        Number(
          initialCredits.value
        ),


      teamCount:
        Number(
          teamCount.value
        ),


      rosterConfig: {

        classic: {

          P:
            Number(
              slotP.value
            ),

          D:
            Number(
              slotD.value
            ),

          C:
            Number(
              slotC.value
            ),

          A:
            Number(
              slotA.value
            )
        },


        mantra: {

          goalkeepers: {

            min:
              Number(
                mantraGkMin.value
              ),

            max:
              Number(
                mantraGkMax.value
              )
          },


          outfield: {

            min:
              Number(
                mantraOutfieldMin.value
              ),

            max:
              Number(
                mantraOutfieldMax.value
              )
          },


          total: {

            min:
              Number(
                mantraTotalMin.value
              ),

            max:
              Number(
                mantraTotalMax.value
              )
          }
        }
      },


      underEnabled:
        underEnabled.checked,


      underMinCount:
        underEnabled.checked

          ? Number(
              underMinCount.value
            )

          : 0,


      nominationMode:
        nominationMode.value,


      listSortBy:
        listSortBy.value,


      listSortDirection:
        listSortDirection.value,


      auctionBaseMode:
        auctionBaseMode.value,


      bidMode:
        bidMode.value,


      turnDirection:
        turnDirection.value,


      timerMode:
        timerMode.value,


      fixedTimerSeconds:
        Number(
          fixedTimerSeconds.value
        )
    }


    try {

      const data =
        await callApi({

          action:
            'updateSetup',

          setup
        })


      if (!data?.ok) {

        showMessage(
          data?.error ||
          'Impossibile salvare il Setup.',
          'error'
        )

        return
      }


      populateForm(
        data.settings
      )


      showMessage(
        'Setup salvato.',
        'success'
      )


    } catch (error) {

      console.error(error)


      showMessage(
        error.message ||
        'Errore durante il salvataggio.',
        'error'
      )

    } finally {

      button.disabled =
        false


      button.textContent =
        originalText
    }
  }
)


/* =========================================================
   EVENTI
   ========================================================= */

fantasyMode.addEventListener(
  'change',
  updateConditionalFields
)


underEnabled.addEventListener(
  'change',
  updateConditionalFields
)


nominationMode.addEventListener(
  'change',
  updateConditionalFields
)


bidMode.addEventListener(
  'change',
  updateConditionalFields
)


timerMode.addEventListener(
  'change',
  updateConditionalFields
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

  loadSetup()
}
