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

  } catch (error) {

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
   PREVIEW CODICE LEGA
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


    <div class="section-heading">

      <span class="section-label">
        FOUND
      </span>

      <div>

        <h2>
          ${escapeHtml(
            data.league.name
          )}
        </h2>

        <p>
          Codice:
          ${escapeHtml(
            data.league.code
          )}
        </p>

      </div>

    </div>


    <div
      id="join-team-list"
      class="list"
    ></div>


    <div class="divider"></div>


    <h3>
      Crea una nuova squadra
    </h3>


    <p class="setting-help">
      Se la squadra non esiste ancora,
      puoi crearla e candidarti
      automaticamente come Presidente.
    </p>


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
        Nessuna squadra disponibile.
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


      const description =
        team.hasPresident

          ? `
            Presidente:
            ${escapeHtml(
              team.presidentUsername
              || 'assegnato'
            )}
            · candidatura come Vice
          `

          : `
            Nessun Presidente
            · candidatura come Presidente
          `


      row.innerHTML = `

        <div class="list-row-main">

          <div class="list-row-title">

            <strong>
              ${escapeHtml(
                team.name
              )}
            </strong>

            <small>
              ${description}
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


      const button =
        row.querySelector(
          '.join-team-button'
        )


      button.addEventListener(
        'click',
        async () => {

          await joinExistingTeam(
            team.id,
            button
          )
        }
      )


      teamList.appendChild(
        row
      )
    }
  }


  const newTeamForm =
    document.getElementById(
      'new-team-form'
    )


  newTeamForm.addEventListener(
    'submit',
    async event => {

      event.preventDefault()


      const input =
        document.getElementById(
          'new-team-name'
        )


      const button =
        newTeamForm.querySelector(
          'button[type="submit"]'
        )


      await joinNewTeam(
        input.value.trim(),
        button
      )
    }
  )
}


/* =========================================================
   ISCRIZIONE A SQUADRA ESISTENTE
   ========================================================= */

async function joinExistingTeam(
  teamId,
  button
) {

  if (!currentPreview?.league?.code) {

    showMessage(
      'Lega non valida.',
      'error'
    )

    return
  }


  showMessage('')


  button.disabled =
    true


  const originalText =
    button.textContent


  button.textContent =
    'Invio...'


  try {

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

    currentPreview =
      null

    codeInput.value =
      ''


    showMessage(
      `Richiesta inviata. Candidatura come ${role}.`,
      'success'
    )


    await loadHome()


  } catch (error) {

    console.error(error)


    showMessage(
      error.message ||
      'Errore durante la richiesta.',
      'error'
    )

  } finally {

    button.disabled =
      false

    button.textContent =
      originalText
  }
}


/* =========================================================
   CREAZIONE SQUADRA + ISCRIZIONE
   ========================================================= */

async function joinNewTeam(
  teamName,
  button
) {

  if (!currentPreview?.league?.code) {

    showMessage(
      'Lega non valida.',
      'error'
    )

    return
  }


  if (
    teamName.length < 2
  ) {

    showMessage(
      'Inserisci un nome squadra valido.',
      'error'
    )

    return
  }


  showMessage('')


  button.disabled =
    true


  const originalText =
    button.textContent


  button.textContent =
    'Invio...'


  try {

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

    currentPreview =
      null

    codeInput.value =
      ''


    showMessage(
      'Squadra creata. Richiesta inviata come Presidente.',
      'success'
    )


    await loadHome()


  } catch (error) {

    console.error(error)


    showMessage(
      error.message ||
      'Errore durante la richiesta.',
      'error'
    )

  } finally {

    button.disabled =
      false

    button.textContent =
      originalText
  }
}


/* =========================================================
   CERCA LEGA TRAMITE CODICE
   ========================================================= */

codeForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()


    showMessage('')


    leaguePreview.hidden =
      true

    currentPreview =
      null


    const code =
      codeInput
        .value
        .trim()
        .toUpperCase()


    if (!code) {

      showMessage(
        'Inserisci un codice lega.',
        'error'
      )

      return
    }


    const button =
      codeForm.querySelector(
        'button[type="submit"]'
      )


    button.disabled =
      true


    const originalText =
      button.textContent


    button.textContent =
      'Cerco...'


    try {

      const data =
        await callApi({

          action:
            'previewLeagueCode',

          code
        })


      if (!data?.ok) {

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


    } catch (error) {

      console.error(error)


      showMessage(
        error.message ||
        'Errore durante la ricerca.',
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
