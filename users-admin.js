const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const ADMIN_URL =
  `${SUPABASE_URL}/functions/v1/global-admin`


const message =
  document.getElementById(
    'admin-message'
  )

const usersList =
  document.getElementById(
    'users-list'
  )

const userSearch =
  document.getElementById(
    'user-search'
  )

const userFilter =
  document.getElementById(
    'user-filter'
  )

const usersCount =
  document.getElementById(
    'users-count'
  )


let users = []

let currentUserId = null

let globalMultiLeague = false


/* =========================================================
   SESSIONE
   ========================================================= */

function getSession() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_session'
      )

    if (!raw) {
      return null
    }

    return JSON.parse(raw)

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
   API SUPER ADMIN
   ========================================================= */

async function callAdmin(body) {

  const session =
    getSession()


  if (!session?.token) {

    window.location.href =
      'index.html'

    return null
  }


  const response =
    await fetch(
      ADMIN_URL,
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


  const date =
    new Date(value)


  return date.toLocaleString(
    'it-IT',
    {
      dateStyle:
        'short',

      timeStyle:
        'short'
    }
  )
}


function formatDate(value) {

  if (!value) {
    return '—'
  }


  const [
    year,
    month,
    day
  ] =
    value.split('-')


  return `${day}/${month}/${year}`
}


/* =========================================================
   MULTI LEGA EFFETTIVO
   ========================================================= */

function effectiveMultiLeague(
  user
) {

  /*
   * Override OFF:
   * vince sempre.
   */

  if (
    user.multi_league_override
      === 'disabled'
  ) {

    return false
  }


  /*
   * Override ON:
   * valido fino alla scadenza.
   */

  if (
    user.multi_league_override
      === 'enabled'
  ) {

    if (
      !user
        .multi_league_override_until
    ) {

      return true
    }


    const expiry =
      new Date(
        `${user.multi_league_override_until}T23:59:59`
      )


    if (
      expiry.getTime()
      >= Date.now()
    ) {

      return true
    }
  }


  /*
   * Altrimenti eredita
   * il setup globale.
   */

  return globalMultiLeague
}


/* =========================================================
   FILTRI
   ========================================================= */

function getFilteredUsers() {

  const search =
    userSearch
      .value
      .trim()
      .toLowerCase()


  const filter =
    userFilter.value


  return users.filter(
    user => {

      const username =
        user.username
          .toLowerCase()


      if (
        !username.includes(search)
      ) {

        return false
      }


      switch (filter) {

        case 'active':

          return user.is_enabled


        case 'disabled':

          return !user.is_enabled


        case 'superadmin':

          return user.is_super_admin


        case 'multileague':

          return effectiveMultiLeague(
            user
          )


        default:

          return true
      }
    }
  )
}


/* =========================================================
   RENDER UTENTI
   ========================================================= */

function renderUsers() {

  usersList.innerHTML = ''


  const visibleUsers =
    getFilteredUsers()


  usersCount.textContent =
    `${visibleUsers.length} di ${users.length} utenti`


  if (
    visibleUsers.length === 0
  ) {

    usersList.innerHTML = `
      <div class="empty-state">
        Nessun utente trovato.
      </div>
    `

    return
  }


  for (
    const user
    of visibleUsers
  ) {

    const isCurrentUser =
      user.id === currentUserId


    const multiLeague =
      effectiveMultiLeague(user)


    const row =
      document.createElement(
        'details'
      )


    row.className =
      'user-row'


    row.innerHTML = `

      <summary>

        <div class="user-summary-name">

          <strong>
            ${escapeHtml(
              user.username
            )}
          </strong>


          <small>
            ${
              isCurrentUser

                ? 'Il tuo account'

                : 'Account utente'
            }
          </small>

        </div>


        <div class="user-summary-status">

          ${
            user.is_enabled

              ? `
                <span
                  class="badge good"
                >
                  ATTIVO
                </span>
              `

              : `
                <span
                  class="badge warning"
                >
                  DISATTIVATO
                </span>
              `
          }


          ${
            user.is_super_admin

              ? `
                <span
                  class="badge admin"
                >
                  SUPER ADMIN
                </span>
              `

              : ''
          }


          <span class="badge">

            MULTI
            ${multiLeague
              ? 'ON'
              : 'OFF'}

          </span>

        </div>


        <span class="user-chevron">
          ⌄
        </span>

      </summary>


      <div class="user-detail">


        <div class="user-metadata">

          <div>

            <span>
              Registrazione
            </span>

            <strong>
              ${formatDateTime(
                user.created_at
              )}
            </strong>

          </div>


          <div>

            <span>
              Ultimo accesso
            </span>

            <strong>
              ${formatDateTime(
                user.last_login_at
              )}
            </strong>

          </div>

        </div>


        <label class="setting-row">

          <span>

            <strong>
              Account attivo
            </strong>

            <small>
              Permette l'accesso
              all'applicazione.
            </small>

          </span>


          <input
            class="user-enabled"
            type="checkbox"

            ${
              user.is_enabled
                ? 'checked'
                : ''
            }

            ${
              isCurrentUser
                ? 'disabled'
                : ''
            }
          >

        </label>


        <label class="setting-row">

          <span>

            <strong>
              Super Admin
            </strong>

            <small>
              Gestione globale
              dell'app.
            </small>

          </span>


          <input
            class="user-super-admin"
            type="checkbox"

            ${
              user.is_super_admin
                ? 'checked'
                : ''
            }

            ${
              isCurrentUser
                ? 'disabled'
                : ''
            }
          >

        </label>


        <label
          class="user-select-field"
        >

          <span>
            Multi-lega
          </span>


          <select
            class="user-multi-league"
          >

            <option
              value="inherit"

              ${
                user
                  .multi_league_override
                  === 'inherit'

                  ? 'selected'
                  : ''
              }
            >
              Eredita dal setup globale
            </option>


            <option
              value="enabled"

              ${
                user
                  .multi_league_override
                  === 'enabled'

                  ? 'selected'
                  : ''
              }
            >
              Abilitato forzatamente
            </option>


            <option
              value="disabled"

              ${
                user
                  .multi_league_override
                  === 'disabled'

                  ? 'selected'
                  : ''
              }
            >
              Disabilitato forzatamente
            </option>

          </select>

        </label>


        <p class="setting-help">

          ${
            user
              .multi_league_override
              === 'enabled'
            &&
            user
              .multi_league_override_until

              ? `
                Override ON valido
                fino al
                ${formatDate(
                  user
                    .multi_league_override_until
                )}
              `

              : user
                  .multi_league_override
                  === 'disabled'

                ? `
                  Override personale:
                  multi-lega OFF.
                `

                : `
                  Il valore viene ereditato
                  dal Setup Globale.
                `
          }

        </p>


        <button
          class="save-user"
          type="button"
        >
          Salva modifiche
        </button>

      </div>

    `


    const saveButton =
      row.querySelector(
        '.save-user'
      )


    saveButton.addEventListener(
      'click',
      async event => {

        /*
         * Evitiamo che il click
         * chiuda accidentalmente
         * il dettaglio.
         */
        event.stopPropagation()


        showMessage('')


        const enabled =
          row
            .querySelector(
              '.user-enabled'
            )
            .checked


        const superAdmin =
          row
            .querySelector(
              '.user-super-admin'
            )
            .checked


        const multiLeagueOverride =
          row
            .querySelector(
              '.user-multi-league'
            )
            .value


        try {

          const data =
            await callAdmin({

              action:
                'updateUser',

              targetUserId:
                user.id,

              isEnabled:
                enabled,

              isSuperAdmin:
                superAdmin,

              multiLeagueOverride
            })


          if (!data?.ok) {

            showMessage(
              data?.error ||
              'Errore durante il salvataggio.',
              'error'
            )

            return
          }


          showMessage(
            `${user.username} aggiornato.`,
            'success'
          )


          await loadUsers()


        } catch (error) {

          console.error(
            error
          )


          showMessage(
            error.message ||
            'Errore durante il salvataggio.',
            'error'
          )
        }
      }
    )


    usersList.appendChild(
      row
    )
  }
}


/* =========================================================
   CARICAMENTO
   ========================================================= */

async function loadUsers() {

  try {

    const data =
      await callAdmin({
        action:
          'getDashboard'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare gli utenti.',
        'error'
      )

      return
    }


    users =
      data.users || []


    currentUserId =
      data.currentUserId


    globalMultiLeague =
      data.settings
        ?.multi_league_enabled
      === true


    renderUsers()


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
   EVENTI
   ========================================================= */

userSearch.addEventListener(
  'input',
  renderUsers
)


userFilter.addEventListener(
  'change',
  renderUsers
)


/* =========================================================
   START
   ========================================================= */

loadUsers()
