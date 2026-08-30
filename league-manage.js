const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const API_URL =
  `${SUPABASE_URL}/functions/v1/league-api`


let selectedLeague = null
let managementData = null


const leagueTitle =
  document.getElementById(
    'league-title'
  )

const message =
  document.getElementById(
    'page-message'
  )

const createTeamArea =
  document.getElementById(
    'create-team-area'
  )

const createTeamForm =
  document.getElementById(
    'create-team-form'
  )

const newTeamName =
  document.getElementById(
    'new-team-name'
  )

const teamsList =
  document.getElementById(
    'teams-list'
  )

const membersList =
  document.getElementById(
    'members-list'
  )

const viceSection =
  document.getElementById(
    'vice-section'
  )

const viceRequests =
  document.getElementById(
    'vice-requests'
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
   UTILITY
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
   SQUADRE
   ========================================================= */

function renderTeams() {

  const teams =
    managementData.teams || []


  teamsList.innerHTML = ''


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


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              team.name
            )}
          </h3>

          ${
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
          }

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


  if (
    managementData.teamLimit
    !== null
  ) {

    const info =
      document.createElement(
        'p'
      )

    info.className =
      'setting-help'

    info.textContent =
      `${teams.length} / ${managementData.teamLimit} squadre`


    teamsList.prepend(
      info
    )
  }
}


/* =========================================================
   MEMBRI
   ========================================================= */

function renderMembers() {

  const members =
    managementData.members || []


  membersList.innerHTML = ''


  if (
    members.length === 0
  ) {

    membersList.innerHTML = `
      <div class="empty-state">
        Nessun membro attivo.
      </div>
    `

    return
  }


  for (
    const member
    of members
  ) {

    const details =
      document.createElement(
        'details'
      )

    details.className =
      'user-row'


    const roles =
      new Set(
        member.leagueRoles || []
      )


    const teamDescription =
      member.team

        ? `${member.team.name} · ${roleLabel(
            member.team.role
          )}`

        : 'Nessuna squadra'


    details.innerHTML = `

      <summary>

        <div class="user-summary-name">

          <strong>
            ${escapeHtml(
              member.username
            )}
          </strong>

          <small>
            ${escapeHtml(
              teamDescription
            )}
          </small>

        </div>


        <div class="user-summary-status">

          ${
            roles.has(
              'league_admin'
            )

              ? `
                <span class="badge admin">
                  ADMIN LEGA
                </span>
              `

              : ''
          }


          ${
            roles.has(
              'auctioneer'
            )

              ? `
                <span class="badge">
                  BANDITORE
                </span>
              `

              : ''
          }


          ${
            roles.has(
              'presenter'
            )

              ? `
                <span class="badge">
                  PRESENTATORE
                </span>
              `

              : ''
          }


          ${
            member.team

              ? `
                <span class="badge good">
                  ${escapeHtml(
                    roleLabel(
                      member.team.role
                    )
                  )}
                </span>
              `

              : ''
          }

        </div>


        <span class="user-chevron">
          ⌄
        </span>

      </summary>


      <div class="user-detail">

        ${
          member.team

            ? `
              <p>
                Squadra:
                <strong>
                  ${escapeHtml(
                    member.team.name
                  )}
                </strong>
              </p>

              <p>
                Ruolo squadra:
                <strong>
                  ${escapeHtml(
                    roleLabel(
                      member.team.role
                    )
                  )}
                </strong>
              </p>
            `

            : `
              <p class="setting-help">
                Questo utente non è associato
                ad alcuna squadra.
              </p>
            `
        }


        ${
          managementData
            .permissions
            .canManageRoles

            ? `

              <div class="divider"></div>

              <p class="setting-help">
                Ruoli di lega
              </p>


              <label class="setting-row">

                <span>
                  <strong>
                    Admin Lega
                  </strong>

                  <small>
                    Gestione completa della lega.
                  </small>
                </span>

                <input
                  class="role-admin"
                  type="checkbox"

                  ${
                    roles.has(
                      'league_admin'
                    )
                      ? 'checked'
                      : ''
                  }
                >

              </label>


              <label class="setting-row">

                <span>
                  <strong>
                    Banditore
                  </strong>

                  <small>
                    Gestisce l'asta live
                    e conferma le assegnazioni.
                  </small>
                </span>

                <input
                  class="role-auctioneer"
                  type="checkbox"

                  ${
                    roles.has(
                      'auctioneer'
                    )
                      ? 'checked'
                      : ''
                  }
                >

              </label>


              <label class="setting-row">

                <span>
                  <strong>
                    Presentatore
                  </strong>

                  <small>
                    Accesso alla visualizzazione
                    TV/proiettore.
                  </small>
                </span>

                <input
                  class="role-presenter"
                  type="checkbox"

                  ${
                    roles.has(
                      'presenter'
                    )
                      ? 'checked'
                      : ''
                  }
                >

              </label>


              <button
                class="save-roles"
                type="button"
              >
                Salva ruoli
              </button>

            `

            : ''
        }

      </div>

    `


    if (
      managementData
        .permissions
        .canManageRoles
    ) {

      const saveButton =
        details.querySelector(
          '.save-roles'
        )


      saveButton.addEventListener(
        'click',
        async () => {

          await saveMemberRoles(
            member,
            details,
            saveButton
          )
        }
      )
    }


    membersList.appendChild(
      details
    )
  }
}


/* =========================================================
   SALVATAGGIO RUOLI
   ========================================================= */

async function saveMemberRoles(
  member,
  details,
  button
) {

  showMessage('')


  const desired = {

    league_admin:
      details
        .querySelector(
          '.role-admin'
        )
        .checked,

    auctioneer:
      details
        .querySelector(
          '.role-auctioneer'
        )
        .checked,

    presenter:
      details
        .querySelector(
          '.role-presenter'
        )
        .checked
  }


  const current =
    new Set(
      member.leagueRoles || []
    )


  const changes =
    Object.entries(
      desired
    )
      .filter(
        ([role, enabled]) =>
          current.has(role)
          !== enabled
      )


  if (
    changes.length === 0
  ) {

    showMessage(
      'Nessuna modifica da salvare.',
      'success'
    )

    return
  }


  button.disabled =
    true


  const originalText =
    button.textContent


  button.textContent =
    'Salvataggio...'


  try {

    for (
      const [
        role,
        enabled
      ]
      of changes
    ) {

      const data =
        await callApi({

          action:
            'setMemberRole',

          targetUserId:
            member.userId,

          role,

          enabled
        })


      if (!data?.ok) {

        throw new Error(
          data?.error ||
          'Impossibile aggiornare il ruolo.'
        )
      }
    }


    showMessage(
      `Ruoli di ${member.username} aggiornati.`,
      'success'
    )


    await loadManagement()


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


/* =========================================================
   RICHIESTE VICE
   ========================================================= */

function renderViceRequests() {

  const requests =
    managementData.viceRequests || []


  viceSection.hidden =
    !managementData
      .permissions
      .canApproveVice


  if (
    viceSection.hidden
  ) {

    return
  }


  viceRequests.innerHTML = ''


  if (
    requests.length === 0
  ) {

    viceRequests.innerHTML = `
      <div class="empty-state">
        Nessuna candidatura Vice
        in attesa.
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


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              request.username
            )}
          </h3>

          ${
            request.leagueApproved

              ? `
                <span class="badge good">
                  LEGA APPROVATA
                </span>
              `

              : `
                <span class="badge">
                  ATTESA ADMIN LEGA
                </span>
              `
          }

          <p class="setting-help">
            Vuole diventare Vice
            della tua squadra.
          </p>

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
      'Approva Vice'


    const rejectButton =
      document.createElement(
        'button'
      )

    rejectButton.type =
      'button'

    rejectButton.className =
      'danger'

    rejectButton.textContent =
      'Rifiuta'


    approveButton.addEventListener(
      'click',
      async () => {

        await handleViceAction(
          'approveVice',
          request,
          approveButton,
          rejectButton
        )
      }
    )


    rejectButton.addEventListener(
      'click',
      async () => {

        await handleViceAction(
          'rejectVice',
          request,
          rejectButton,
          approveButton
        )
      }
    )


    actions.append(
      approveButton,
      rejectButton
    )


    card.appendChild(
      actions
    )


    viceRequests.appendChild(
      card
    )
  }
}


async function handleViceAction(
  action,
  request,
  button,
  otherButton
) {

  showMessage('')


  button.disabled =
    true

  otherButton.disabled =
    true


  const originalText =
    button.textContent


  button.textContent =
    action === 'approveVice'
      ? 'Approvazione...'
      : 'Rifiuto...'


  try {

    const data =
      await callApi({

        action,

        viceUserId:
          request.userId
      })


    if (!data?.ok) {

      throw new Error(
        data?.error ||
        'Operazione non riuscita.'
      )
    }


    showMessage(
      action === 'approveVice'

        ? `${request.username} approvato come Vice.`

        : `Candidatura di ${request.username} rifiutata.`,
      'success'
    )


    await loadManagement()


  } catch (error) {

    console.error(error)


    showMessage(
      error.message ||
      'Errore durante l’operazione.',
      'error'
    )

  } finally {

    button.disabled =
      false

    otherButton.disabled =
      false

    button.textContent =
      originalText
  }
}


/* =========================================================
   CREA SQUADRA
   ========================================================= */

createTeamForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()


    showMessage('')


    const name =
      newTeamName
        .value
        .trim()


    if (
      name.length < 2
    ) {

      showMessage(
        'Inserisci un nome squadra valido.',
        'error'
      )

      return
    }


    const button =
      createTeamForm
        .querySelector(
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
            'createTeam',

          teamName:
            name
        })


      if (!data?.ok) {

        throw new Error(
          data?.error ||
          'Impossibile creare la squadra.'
        )
      }


      newTeamName.value =
        ''


      showMessage(
        `Squadra "${name}" creata.`,
        'success'
      )


      await loadManagement()


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
   LOAD
   ========================================================= */

async function loadManagement() {

  showMessage('')


  try {

    const data =
      await callApi({
        action:
          'getManagementData'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare la gestione della lega.',
        'error'
      )

      return
    }


    managementData =
      data


    leagueTitle.textContent =
      `Membri e squadre · ${data.league.name}`


    createTeamArea.hidden =
      !data.permissions
        .canCreateTeam


    renderTeams()

    renderMembers()

    renderViceRequests()


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


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html'

} else {

  loadManagement()
}
