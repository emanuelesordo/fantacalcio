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
   CAMPI
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


const classicRoster =
  document.getElementById(
    'classic-roster'
  )

const mantraRoster =
  document.getElementById(
    'mantra-roster'
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

const mantraSlots =
  document.getElementById(
    'mantra-slots'
  )


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


const timerPercent1 =
  document.getElementById(
    'timer-percent-1'
  )

const timerPercent2 =
  document.getElementById(
    'timer-percent-2'
  )

const timerPercent3 =
  document.getElementById(
    'timer-percent-3'
  )

const timerPercent4 =
  document.getElementById(
    'timer-percent-4'
  )


const timerSeconds1 =
  document.getElementById(
    'timer-seconds-1'
  )

const timerSeconds2 =
  document.getElementById(
    'timer-seconds-2'
  )

const timerSeconds3 =
  document.getElementById(
    'timer-seconds-3'
  )

const timerSeconds4 =
  document.getElementById(
    'timer-seconds-4'
  )

const timerSeconds5 =
  document.getElementById(
    'timer-seconds-5'
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


  const response =
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
   VISIBILITÀ CAMPI
   ========================================================= */

function updateConditionalFields() {

  classicRoster.hidden =
    fantasyMode.value
    !== 'classic'


  mantraRoster.hidden =
    fantasyMode.value
    !== 'mantra'


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


  mantraSlots.value =
    settings
      .roster_config
      ?.mantra
      ?.total_slots
      ?? 25


  nominationMode.value =
    settings.nomination_mode


  listSortBy.value =
    settings.list_sort_by


  listSortDirection.value =
    settings.list_sort_direction


  auctionBaseMode.value =
    settings.auction_base_mode


  bidMode.value =
    settings.bid_mode


  turnDirection.value =
    settings.turn_direction


  timerMode.value =
    settings.timer_mode


  fixedTimerSeconds.value =
    settings.fixed_timer_seconds


  const bands =
    settings
      .dynamic_timer_config
      ?.bands
      || []


  timerPercent1.value =
    bands[0]?.max_percent
    ?? 2

  timerSeconds1.value =
    bands[0]?.seconds
    ?? 5


  timerPercent2.value =
    bands[1]?.max_percent
    ?? 5

  timerSeconds2.value =
    bands[1]?.seconds
    ?? 7


  timerPercent3.value =
    bands[2]?.max_percent
    ?? 10

  timerSeconds3.value =
    bands[2]?.seconds
    ?? 9


  timerPercent4.value =
    bands[3]?.max_percent
    ?? 20

  timerSeconds4.value =
    bands[3]?.seconds
    ?? 12


  timerSeconds5.value =
    bands[4]?.seconds
    ?? 15


  updateConditionalFields()
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

          total_slots:
            Number(
              mantraSlots.value
            )
        }
      },


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
        ),


      dynamicTimerConfig: {

        bands: [

          {
            max_percent:
              Number(
                timerPercent1.value
              ),

            seconds:
              Number(
                timerSeconds1.value
              )
          },


          {
            max_percent:
              Number(
                timerPercent2.value
              ),

            seconds:
              Number(
                timerSeconds2.value
              )
          },


          {
            max_percent:
              Number(
                timerPercent3.value
              ),

            seconds:
              Number(
                timerSeconds3.value
              )
          },


          {
            max_percent:
              Number(
                timerPercent4.value
              ),

            seconds:
              Number(
                timerSeconds4.value
              )
          },


          {
            max_percent:
              null,

            seconds:
              Number(
                timerSeconds5.value
              )
          }

        ]
      }
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
