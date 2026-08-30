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

const codeForm =
  document.getElementById(
    'league-code-form'
  )

const codeInput =
  document.getElementById(
    'league-code'
  )

const leaguePreview =
  document.getElementById(
    'league-preview'
  )

const createForm =
  document.getElementById(
    'create-league-form'
  )

const newLeagueName =
  document.getElementById(
    'new-league-name'
  )


let currentPreview = null


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

  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}


function roleLabel(role) {

  if (role === 'president') {
    return 'Presidente'
  }

  if (role === 'vice') {
    return 'Vice'
  }

  return '—'
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


  if (response.status === 401) {

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


  if (
    memberships.length === 0
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
    of memberships
  ) {

    if (!membership.league) {
      continue
    }


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


    const statusBadge =
      membership.status === 'active'
      &&
      league.status === 'active'

        ? `
          <span class="badge good">
            ATTIVA
          </span>
        `

        : membership.status === 'pending'

          ? `
            <span class="badge">
              IN ATTESA
            </span>
          `

          : `
            <span class="badge warning">
              ${escapeHtml(
                membership.status.toUpperCase()
              )}
            </span>
          `


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              league.name
            )}
          </h3>

          ${statusBadge}


          ${
            team

              ? `
                <p>
                  Squadra:
                  <strong>
                    ${escapeHtml(
                      team.name
                    )}
                  </strong>
                </p>

                <p>
                  Ruolo:
                  <strong>
                    ${roleLabel(
                      team.role
                    )}
                  </strong>
                </p>
              `

              : ''
          }


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

      selectButton.textContent =
        'Seleziona lega'


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


          showMessage(
            `${league.name} selezionata.`,
            'success'
          )
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
   PREVIEW LEGA
   ========================================================= */

function renderLeaguePreview(
  data
) {

  currentPreview =
    data


  leaguePreview.hidden =
    false


  const teams =
    data.teams || []


  leaguePreview.innerHTML = `

    <div class="divider"></div>


    <h3>
      ${escapeHtml(
        data.league.name
      )}
    </h3>


    <p class="setting-help">
      Codice:
      ${escapeHtml(
        data.league.code
      )}
    </p>


    <div
      id="join-team-list"
      class="list"
    ></div>


    <div class="divider"></div>


    <h3>
      Crea nuova squadra
    </h3>


    <form id="new-team-form">

      <label>

        Nome squadra

        <input
          id="new-team-name"
          type="text"
          minlength="2"
          maxlength="60"
          placeholder="Es. Real Spritz"
          required
        >

      </label>


      <button type="submit">
        Crea squadra e richiedi iscrizione
      </button>

    </form>

  `


  const teamList =
    document.getElementById(
      'join-team-list'
    )


  if (
    teams.length === 0
  ) {

    teamList.innerHTML = `
      <div class="empty-state">
        Nessuna squadra già disponibile.
        Puoi crearne una nuova.
      </div>
    `

  } else {

    for (
      const team
      of teams
    ) {

      const row =
        document.createElement(
          'div'
        )

      row.className =
        'list-row'


      row.innerHTML = `

        <div class="list-row-main">

          <div class="list-row-title">

            <strong>
              ${escapeHtml(
                team.name
              )}
            </strong>

            <small>
              ${
                team.hasPresident

                  ? `Presidente:
                     ${escapeHtml(
                       team.presidentUsername
                       || 'assegnato'
                     )}
                     · Ti candiderai come Vice`

                  : 'Nessun Presidente · Ti candiderai come Presidente'
              }
            </small>

          </div>


          <button
            type="button"
            class="join-team-button"
          >
            Scegli
          </button>

        </div>

      `


      row
        .querySelector(
          '.join-team-button'
        )
        .addEventListener(
          'click',
          async () => {

            await joinExistingTeam(
              team.id
            )
          }
        )


      teamList.appendChild(
        row
      )
    }
  }


  document
    .getElementById(
      'new-team-form'
    )
    .addEventListener(
      'submit',
      async event => {

        event.preventDefault()


        const input =
          document.getElementById(
            'new-team-name'
          )


        await joinNewTeam(
          input.value.trim()
        )
      }
    )
}


/* =========================================================
   RICHIESTE
   ========================================================= */

async function joinExistingTeam(
  teamId
) {

  showMessage('')


  const data =
    await callApi({

      action:
        'joinExistingTeam',

      code:
        currentPreview.league.code,

      teamId
    })


  if (!data?.ok) {

    showMessage(
      data?.error ||
      'Errore durante la richiesta.',
      'error'
    )

    return
  }


  const role =
    roleLabel(
      data.request
        ?.requested_role
    )


  leaguePreview.hidden =
    true


  showMessage(
    `Richiesta inviata. Candidatura come ${role}.`,
    'success'
  )


  await loadHome()
}


async function joinNewTeam(
  teamName
) {

  showMessage('')


  if (
    teamName.length < 2
  ) {

    showMessage(
      'Inserisci un nome squadra valido.',
      'error'
    )

    return
  }


  const data =
    await callApi({

      action:
        'joinNewTeam',

      code:
        currentPreview.league.code,

      teamName
    })


  if (!data?.ok) {

    showMessage(
      data?.error ||
      'Errore durante la richiesta.',
      'error'
    )

    return
  }


  leaguePreview.hidden =
    true


  showMessage(
    'Squadra creata. Richiesta di iscrizione inviata come Presidente.',
    'success'
  )


  await loadHome()
}


/* =========================================================
   CERCA CODICE
   ========================================================= */

codeForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()

    showMessage('')


    const code =
      codeInput
        .value
        .trim()
        .toUpperCase()


    const data =
      await callApi({

        action:
          'previewLeagueCode',

        code
      })


    if (!data?.ok) {

      leaguePreview.hidden =
        true


      showMessage(
        data?.error ||
        'Lega non trovata.',
        'error'
      )

      return
    }


    renderLeaguePreview(
      data
    )
  }
)


/* =========================================================
   CREA LEGA
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
  }
)


/* =========================================================
   HOME
   ========================================================= */

async function loadHome() {

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
   * Può entrare in un'ulteriore
   * lega?
   */

  joinSection.hidden =
    !data.permissions
      .canUseAnotherLeague


  /*
   * Può crearne una?
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
}


loadHome()
