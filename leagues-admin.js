const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/leagues-api`


const message =
  document.getElementById(
    'page-message'
  )

const createForm =
  document.getElementById(
    'create-league-form'
  )

const leagueName =
  document.getElementById(
    'league-name'
  )

const pendingContainer =
  document.getElementById(
    'pending-leagues'
  )

const activeContainer =
  document.getElementById(
    'active-leagues'
  )

const otherContainer =
  document.getElementById(
    'other-leagues'
  )


/* =========================================================
   SESSIONE
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

            sessionToken:
              session.token
          })
      }
    )


  const data =
    await response.json()


  if (
    response.status === 401
    ||
    response.status === 403
  ) {

    throw new Error(
      data.error ||
      'Accesso non autorizzato.'
    )
  }


  return data
}


/* =========================================================
   UTILITY
   ========================================================= */

function escapeHtml(value) {

  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}


function formatDateTime(value) {

  if (!value) {
    return '—'
  }


  return new Date(value)
    .toLocaleString(
      'it-IT',
      {
        dateStyle: 'short',
        timeStyle: 'short'
      }
    )
}


/* =========================================================
   CARD LEGA
   ========================================================= */

function createLeagueCard(
  league
) {

  const card =
    document.createElement(
      'article'
    )

  card.className =
    'league-card'


  let badge = ''

  if (
    league.status === 'active'
  ) {

    badge =
      '<span class="badge good">ATTIVA</span>'

  } else if (
    league.status === 'pending'
  ) {

    badge =
      '<span class="badge">IN ATTESA</span>'

  } else if (
    league.status === 'rejected'
  ) {

    badge =
      '<span class="badge warning">RIFIUTATA</span>'

  } else {

    badge =
      '<span class="badge">ARCHIVIATA</span>'
  }


  card.innerHTML = `

    <div class="league-card-header">

      <div>

        <h3>
          ${escapeHtml(
            league.name
          )}
        </h3>

        ${badge}

        <p>
          Creata da
          <strong>
            ${escapeHtml(
              league.creator_username
              || '—'
            )}
          </strong>
        </p>

        <p>
          ${formatDateTime(
            league.created_at
          )}
        </p>


        ${
          league.status === 'active'

            ? `
              <span class="league-code">
                ${escapeHtml(
                  league.code
                )}
              </span>
            `

            : ''
        }

      </div>

    </div>

  `


  if (
    league.status === 'pending'
  ) {

    const actions =
      document.createElement(
        'div'
      )

    actions.className =
      'league-actions'


    const approveButton =
      document.createElement(
        'button'
      )

    approveButton.textContent =
      'Approva'


    const rejectButton =
      document.createElement(
        'button'
      )

    rejectButton.textContent =
      'Rifiuta'

    rejectButton.className =
      'danger'


    approveButton.addEventListener(
      'click',
      async () => {

        showMessage('')

        try {

          const data =
            await callApi({
              action:
                'approveLeague',

              leagueId:
                league.id
            })


          if (!data?.ok) {

            showMessage(
              data?.error ||
              'Errore durante l’approvazione.',
              'error'
            )

            return
          }


          showMessage(
            `${league.name} approvata.`,
            'success'
          )


          await loadLeagues()


        } catch (error) {

          showMessage(
            error.message,
            'error'
          )
        }
      }
    )


    rejectButton.addEventListener(
      'click',
      async () => {

        showMessage('')

        try {

          const data =
            await callApi({
              action:
                'rejectLeague',

              leagueId:
                league.id
            })


          if (!data?.ok) {

            showMessage(
              data?.error ||
              'Errore durante il rifiuto.',
              'error'
            )

            return
          }


          showMessage(
            `${league.name} rifiutata.`,
            'success'
          )


          await loadLeagues()


        } catch (error) {

          showMessage(
            error.message,
            'error'
          )
        }
      }
    )


    actions.append(
      approveButton,
      rejectButton
    )


    card.appendChild(
      actions
    )
  }


  return card
}


/* =========================================================
   RENDER
   ========================================================= */

function renderGroup(
  container,
  leagues,
  emptyText
) {

  container.innerHTML = ''


  if (
    leagues.length === 0
  ) {

    container.innerHTML = `
      <div class="empty-state">
        ${escapeHtml(emptyText)}
      </div>
    `

    return
  }


  for (
    const league
    of leagues
  ) {

    container.appendChild(
      createLeagueCard(
        league
      )
    )
  }
}


/* =========================================================
   LOAD
   ========================================================= */

async function loadLeagues() {

  try {

    const data =
      await callApi({
        action:
          'getAdminOverview'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare le leghe.',
        'error'
      )

      return
    }


    const leagues =
      data.leagues || []


    const pending =
      leagues.filter(
        l =>
          l.status === 'pending'
      )


    const active =
      leagues.filter(
        l =>
          l.status === 'active'
      )


    const other =
      leagues.filter(
        l =>
          l.status === 'rejected'
          ||
          l.status === 'archived'
      )


    renderGroup(
      pendingContainer,
      pending,
      'Nessuna richiesta in attesa.'
    )


    renderGroup(
      activeContainer,
      active,
      'Nessuna lega attiva.'
    )


    renderGroup(
      otherContainer,
      other,
      'Nessuna lega nello storico.'
    )


  } catch (error) {

    console.error(
      error
    )


    showMessage(
      error.message ||
      'Accesso non autorizzato.',
      'error'
    )
  }
}


/* =========================================================
   CREAZIONE
   ========================================================= */

createForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()

    showMessage('')


    const name =
      leagueName.value.trim()


    if (
      name.length < 2
    ) {

      showMessage(
        'Inserisci un nome valido.',
        'error'
      )

      return
    }


    try {

      const data =
        await callApi({
          action:
            'createLeague',

          name
        })


      if (!data?.ok) {

        showMessage(
          data?.error ||
          'Errore durante la creazione.',
          'error'
        )

        return
      }


      leagueName.value =
        ''


      showMessage(
        `Lega "${name}" creata.`,
        'success'
      )


      await loadLeagues()


    } catch (error) {

      console.error(
        error
      )


      showMessage(
        error.message ||
        'Errore durante la creazione.',
        'error'
      )
    }
  }
)


loadLeagues()
