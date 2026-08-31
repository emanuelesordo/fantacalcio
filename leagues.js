const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/leagues-api`


const message =
  document.getElementById(
    'page-message'
  )

const myLeagues =
  document.getElementById(
    'my-leagues'
  )

const joinSection =
  document.getElementById(
    'join-section'
  )

const createSection =
  document.getElementById(
    'create-section'
  )

const createDescription =
  document.getElementById(
    'create-description'
  )

const createForm =
  document.getElementById(
    'create-league-form'
  )

const newLeagueName =
  document.getElementById(
    'new-league-name'
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
   UI
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


function escapeHtml(value) {

  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}


function roleLabel(role) {

  const labels = {

    president:
      'Presidente',

    vice:
      'Vice'
  }

  return labels[role] || '—'
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
          method:
            'POST',

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
   LE MIE LEGHE
   ========================================================= */

function renderMemberships(
  memberships
) {

  myLeagues.innerHTML = ''


  const visibleMemberships =
    memberships.filter(
      membership =>
        membership.league
        &&
        [
          'pending',
          'active'
        ].includes(
          membership.league.status
        )
        &&
        [
          'pending',
          'active'
        ].includes(
          membership.status
        )
    )


  if (
    visibleMemberships.length === 0
  ) {

    myLeagues.innerHTML = `
      <div class="empty-state">
        Non sei ancora iscritto
        ad alcuna lega.
      </div>
    `

    return
  }


  for (
    const membership
    of visibleMemberships
  ) {

    const league =
      membership.league

    const team =
      membership.team


    const card =
      document.createElement(
        'article'
      )

    card.className =
      'league-card'


    let statusBadge


    if (
      membership.status === 'active'
      &&
      league.status === 'active'
    ) {

      statusBadge = `
        <span class="badge good">
          ATTIVA
        </span>
      `

    } else {

      statusBadge = `
        <span class="badge">
          IN ATTESA
        </span>
      `
    }


    let teamInfo = ''


    if (team) {

      let teamStatus = ''


      if (
        team.membershipStatus
        === 'active'
      ) {

        teamStatus = `
          <span class="badge good">
            ${escapeHtml(
              roleLabel(
                team.role
              )
            )}
          </span>
        `

      } else {

        teamStatus = `
          <span class="badge">
            ${escapeHtml(
              roleLabel(
                team.role
              )
            )}
            · IN ATTESA
          </span>
        `
      }


      teamInfo = `

        <p>
          Squadra:
          <strong>
            ${escapeHtml(
              team.name
            )}
          </strong>
        </p>

        <div>
          ${teamStatus}
        </div>

      `
    }


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              league.name
            )}
          </h3>

          ${statusBadge}

          ${teamInfo}

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


    /*
     * Solo una membership attiva
     * permette di entrare realmente
     * nella dashboard della lega.
     */

    if (
      membership.status === 'active'
      &&
      league.status === 'active'
    ) {

      const actions =
        document.createElement(
          'div'
        )

      actions.className =
        'league-actions'


      const selectButton =
        document.createElement(
          'button'
        )

      selectButton.type =
        'button'

      selectButton.textContent =
        'Entra nella lega'


      selectButton.addEventListener(
        'click',
        () => {

          localStorage.setItem(
            'fantacalcio_selected_league',
            JSON.stringify({
              id:
                league.id,

              name:
                league.name,

              code:
                league.code
            })
          )

          window.location.href =
            'league.html'
        }
      )


      actions.appendChild(
        selectButton
      )


      card.appendChild(
        actions
      )
    }


    myLeagues.appendChild(
      card
    )
  }
}


/* =========================================================
   CREA NUOVA LEGA
   ========================================================= */

createForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()

    showMessage('')


    const name =
      newLeagueName
        .value
        .trim()


    if (
      name.length < 2
    ) {

      showMessage(
        'Inserisci un nome lega valido.',
        'error'
      )

      return
    }


    const button =
      createForm.querySelector(
        'button[type="submit"]'
      )

    button.disabled =
      true


    const originalText =
      button.textContent

    button.textContent =
      'Creazione...'


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


      newLeagueName.value =
        ''


      if (
        data.league
          ?.league_status
        === 'active'
      ) {

        showMessage(
          'Lega creata e attivata.',
          'success'
        )

      } else {

        showMessage(
          'Richiesta di creazione inviata al Super Admin.',
          'success'
        )
      }


      await loadHome()


    } catch (error) {

      console.error(error)

      showMessage(
        error.message ||
        'Errore durante la creazione.',
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
   CARICAMENTO HOME
   ========================================================= */

async function loadHome() {

  try {

    const data =
      await callApi({
        action:
          'getLeagueHome'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare le leghe.',
        'error'
      )

      return
    }


    renderMemberships(
      data.memberships || []
    )


    /*
     * Mostra "Unisciti"
     * solo se l'utente può utilizzare
     * un'altra lega.
     */

    joinSection.hidden =
      !data.permissions
        .canUseAnotherLeague


    /*
     * Mostra "Crea"
     * solo quando la creazione
     * è consentita.
     */

    createSection.hidden =
      !data.permissions
        .canCreateLeague


    if (
      data.user.isSuperAdmin
    ) {

      createDescription.textContent =
        'Come Super Admin, la nuova lega sarà attiva immediatamente.'

    } else {

      createDescription.textContent =
        'La nuova lega dovrà essere approvata dal Super Admin.'
    }


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
   START
   ========================================================= */

loadHome()
