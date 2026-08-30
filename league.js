const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/league-api`


const title =
  document.getElementById(
    'league-title'
  )

const subtitle =
  document.getElementById(
    'league-subtitle'
  )

const message =
  document.getElementById(
    'page-message'
  )

const leagueCode =
  document.getElementById(
    'league-code'
  )

const teamsCount =
  document.getElementById(
    'teams-count'
  )

const rolesContainer =
  document.getElementById(
    'my-roles'
  )

const myTeamContainer =
  document.getElementById(
    'my-team'
  )

const teamsList =
  document.getElementById(
    'teams-list'
  )

const adminSection =
  document.getElementById(
    'admin-section'
  )

const pendingRequests =
  document.getElementById(
    'pending-requests'
  )

const setupTab =
  document.getElementById(
    'setup-tab'
  )


let selectedLeague = null


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

    league_admin:
      'Admin Lega',

    auctioneer:
      'Banditore',

    presenter:
      'Presentatore',

    president:
      'Presidente',

    vice:
      'Vice'
  }


  return labels[role] || role
}


/* =========================================================
   API
   ========================================================= */

async function callApi(body) {

  const session =
    getSession()


  if (
    !session?.token
  ) {

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
   RUOLI
   ========================================================= */

function renderRoles(data) {

  const roles = []


  if (
    data.permissions
      .isSuperAdmin
  ) {

    roles.push(
      'Super Admin'
    )
  }


  for (
    const role
    of data.leagueRoles || []
  ) {

    roles.push(
      roleLabel(role)
    )
  }


  if (
    data.myTeam?.role
  ) {

    let teamRole =
      roleLabel(
        data.myTeam.role
      )


    if (
      data.myTeam.status
      !== 'active'
    ) {

      teamRole +=
        ' · in attesa'
    }


    roles.push(
      teamRole
    )
  }


  const uniqueRoles =
    [...new Set(roles)]


  if (
    uniqueRoles.length === 0
  ) {

    rolesContainer.innerHTML = `
      <span class="badge">
        Membro
      </span>
    `

    return
  }


  rolesContainer.innerHTML =
    uniqueRoles
      .map(
        role => `
          <span class="badge admin">
            ${escapeHtml(role)}
          </span>
        `
      )
      .join(' ')
}


/* =========================================================
   MIA SQUADRA
   ========================================================= */

function renderMyTeam(
  myTeam
) {

  if (
    !myTeam?.team
  ) {

    myTeamContainer.innerHTML = `
      <div class="empty-state">
        Non hai una squadra associata
        in questa lega.
      </div>
    `

    return
  }


  let statusBadge = ''


  if (
    myTeam.status === 'active'
  ) {

    statusBadge = `
      <span class="badge good">
        ATTIVO
      </span>
    `

  } else {

    statusBadge = `
      <span class="badge">
        IN ATTESA
      </span>
    `
  }


  let note = ''


  if (
    myTeam.role === 'vice'
    &&
    myTeam.status === 'pending'
  ) {

    if (
      myTeam.league_approved_at
      &&
      !myTeam.president_approved_at
    ) {

      note =
        'Accesso alla lega approvato. In attesa dell’approvazione del Presidente.'

    } else if (
      !myTeam.league_approved_at
    ) {

      note =
        'In attesa dell’approvazione dell’Admin Lega.'
    }
  }


  myTeamContainer.innerHTML = `

    <div class="league-card">

      <h3>
        ${escapeHtml(
          myTeam.team.name
        )}
      </h3>

      ${statusBadge}

      <p>
        Ruolo:
        <strong>
          ${escapeHtml(
            roleLabel(
              myTeam.role
            )
          )}
        </strong>
      </p>

      ${
        note
          ? `
            <p class="setting-help">
              ${escapeHtml(note)}
            </p>
          `
          : ''
      }

    </div>

  `
}


/* =========================================================
   SQUADRE
   ========================================================= */

function renderTeams(
  teams
) {

  teamsList.innerHTML = ''


  const activeTeams =
    teams.filter(
      team =>
        team.status === 'active'
    )


  teamsCount.textContent =
    activeTeams.length


  if (
    teams.length === 0
  ) {

    teamsList.innerHTML = `
      <div class="empty-state">
        Nessuna squadra presente.
      </div>
    `

    return
  }


  for (
    const team
    of teams
  ) {

    const card =
      document.createElement(
        'article'
      )

    card.className =
      'league-card'


    const statusBadge =
      team.status === 'active'

        ? `
          <span class="badge good">
            ATTIVA
          </span>
        `

        : `
          <span class="badge">
            IN ATTESA
          </span>
        `


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              team.name
            )}
          </h3>

          ${statusBadge}

          <p>

            Presidente:

            <strong>
              ${escapeHtml(
                team.presidentUsername
                || 'non assegnato'
              )}
            </strong>

          </p>

        </div>

      </div>

    `


    teamsList.appendChild(
      card
    )
  }
}


/* =========================================================
   RICHIESTE ADMIN
   ========================================================= */

function renderRequests(
  requests
) {

  pendingRequests.innerHTML = ''


  if (
    requests.length === 0
  ) {

    pendingRequests.innerHTML = `
      <div class="empty-state">
        Nessuna richiesta in attesa.
      </div>
    `

    return
  }


  for (
    const request
    of requests
  ) {

    const card =
      document.createElement(
        'article'
      )

    card.className =
      'league-card'


    const team =
      request.team


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              request.username
            )}
          </h3>


          ${
            team

              ? `
                <p>
                  Squadra:
                  <strong>
                    ${escapeHtml(
                      team.teamName
                    )}
                  </strong>
                </p>

                <p>
                  Candidatura:
                  <strong>
                    ${escapeHtml(
                      roleLabel(
                        team.role
                      )
                    )}
                  </strong>
                </p>

                ${
                  team.teamStatus === 'pending'

                    ? `
                      <span class="badge">
                        NUOVA SQUADRA
                      </span>
                    `

                    : ''
                }
              `

              : `
                <p>
                  Nessuna candidatura squadra trovata.
                </p>
              `
          }

        </div>

      </div>

    `


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

    approveButton.type =
      'button'

    approveButton.textContent =
      'Approva'


    const rejectButton =
      document.createElement(
        'button'
      )

    rejectButton.type =
      'button'

    rejectButton.textContent =
      'Rifiuta'

    rejectButton.className =
      'danger'


    approveButton.addEventListener(
      'click',
      async () => {

        showMessage('')


        approveButton.disabled =
          true

        rejectButton.disabled =
          true


        const originalText =
          approveButton.textContent


        approveButton.textContent =
          'Approvazione...'


        try {

          const data =
            await callApi({
              action:
                'approveMember',

              targetUserId:
                request.userId
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
            `${request.username} approvato.`,
            'success'
          )


          await loadDashboard()


        } catch (error) {

          console.error(error)


          showMessage(
            error.message ||
            'Errore durante l’approvazione.',
            'error'
          )

        } finally {

          approveButton.disabled =
            false

          rejectButton.disabled =
            false

          approveButton.textContent =
            originalText
        }
      }
    )


    rejectButton.addEventListener(
      'click',
      async () => {

        showMessage('')


        approveButton.disabled =
          true

        rejectButton.disabled =
          true


        const originalText =
          rejectButton.textContent


        rejectButton.textContent =
          'Rifiuto...'


        try {

          const data =
            await callApi({
              action:
                'rejectMember',

              targetUserId:
                request.userId
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
            `${request.username} rifiutato.`,
            'success'
          )


          await loadDashboard()


        } catch (error) {

          console.error(error)


          showMessage(
            error.message ||
            'Errore durante il rifiuto.',
            'error'
          )

        } finally {

          approveButton.disabled =
            false

          rejectButton.disabled =
            false

          rejectButton.textContent =
            originalText
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


    pendingRequests.appendChild(
      card
    )
  }
}


/* =========================================================
   DASHBOARD
   ========================================================= */

async function loadDashboard() {

  showMessage('')


  try {

    const data =
      await callApi({
        action:
          'getDashboard'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile aprire la lega.',
        'error'
      )

      return
    }


    /* =====================================================
       HEADER
       ===================================================== */

    title.textContent =
      data.league.name


    subtitle.textContent =
      `Lega attiva · ${data.currentUser.username}`


    /* =====================================================
       PANORAMICA
       ===================================================== */

    leagueCode.textContent =
      data.league.code


    renderRoles(
      data
    )


    renderMyTeam(
      data.myTeam
    )


    renderTeams(
      data.teams || []
    )


    /* =====================================================
       SETUP
       Visibile solo agli Admin Lega.
       ===================================================== */

    if (setupTab) {

      setupTab.hidden =
        !data.permissions
          .isLeagueAdmin
    }


    /* =====================================================
       AMMINISTRAZIONE
       ===================================================== */

    adminSection.hidden =
      !data.permissions
        .canManageMembers


    if (
      data.permissions
        .canManageMembers
    ) {

      renderRequests(
        data.pendingRequests || []
      )
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

selectedLeague =
  getSelectedLeague()


if (
  !selectedLeague?.id
) {

  window.location.href =
    'leagues.html'

} else {

  loadDashboard()
}
