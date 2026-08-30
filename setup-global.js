const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const ADMIN_URL =
  `${SUPABASE_URL}/functions/v1/global-admin`


const message =
  document.getElementById(
    'admin-message'
  )

const allowLeagueCreation =
  document.getElementById(
    'allow-league-creation'
  )

const multiLeagueEnabled =
  document.getElementById(
    'multi-league-enabled'
  )

const saveSettingsButton =
  document.getElementById(
    'save-global-settings'
  )

const usersList =
  document.getElementById(
    'users-list'
  )


let currentUserId = null


function getSession() {

  try {

    return JSON.parse(
      localStorage.getItem(
        'fantacalcio_session'
      )
    )

  } catch {

    return null
  }
}


function showMessage(
  text,
  type = ''
) {

  message.textContent = text
  message.className = type
}


async function callAdmin(body) {

  const session =
    getSession()

  if (!session?.token) {
    window.location.href =
      'index.html'

    return
  }


  const response =
    await fetch(
      ADMIN_URL,
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



function getEffectiveMultiLeague(
  user
) {

  if (
    user.multi_league_override
      === 'disabled'
  ) {
    return false
  }


  if (
    user.multi_league_override
      === 'enabled'
  ) {

    if (
      !user.multi_league_override_until
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


  return multiLeagueEnabled.checked
}



function renderUsers(users) {

  usersList.innerHTML = ''


  for (const user of users) {

    const card =
      document.createElement('article')

    card.className =
      'user-admin-card'


    const effective =
      getEffectiveMultiLeague(user)


    card.innerHTML = `

      <div class="user-admin-heading">

        <div>
          <strong>
            ${escapeHtml(user.username)}
          </strong>

          ${
            user.id === currentUserId
              ? '<small>Tu</small>'
              : ''
          }
        </div>

        <span>
          Multi-lega effettivo:
          <strong>
            ${effective ? 'ON' : 'OFF'}
          </strong>
        </span>

      </div>


      <label class="setting-row">

        <span>
          Account attivo
        </span>

        <input
          class="user-enabled"
          type="checkbox"
          ${user.is_enabled
            ? 'checked'
            : ''}
        >

      </label>


      <label class="setting-row">

        <span>
          Super Admin
        </span>

        <input
          class="user-super-admin"
          type="checkbox"
          ${user.is_super_admin
            ? 'checked'
            : ''}
        >

      </label>


      <label>

        Multi-lega

        <select
          class="user-multi-league"
        >

          <option
            value="inherit"
            ${
              user.multi_league_override
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
              user.multi_league_override
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
              user.multi_league_override
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
          user.multi_league_override_until

            ? `Scadenza abilitazione:
               ${formatDate(
                 user.multi_league_override_until
               )}`

            : 'Nessuna scadenza attiva'
        }

      </p>


      <button
        class="save-user"
        type="button"
      >
        Salva utente
      </button>

    `


    const saveButton =
      card.querySelector(
        '.save-user'
      )


    saveButton.addEventListener(
      'click',
      async () => {

        showMessage('')


        const enabled =
          card.querySelector(
            '.user-enabled'
          ).checked


        const superAdmin =
          card.querySelector(
            '.user-super-admin'
          ).checked


        const multiLeague =
          card.querySelector(
            '.user-multi-league'
          ).value


        const data =
          await callAdmin({
            action: 'updateUser',

            targetUserId:
              user.id,

            isEnabled:
              enabled,

            isSuperAdmin:
              superAdmin,

            multiLeagueOverride:
              multiLeague
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
          'Utente aggiornato.',
          'success'
        )


        await loadDashboard()
      }
    )


    usersList.appendChild(card)
  }
}



function escapeHtml(value) {

  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}



function formatDate(value) {

  const [
    year,
    month,
    day
  ] = value.split('-')

  return `${day}/${month}/${year}`
}



async function loadDashboard() {

  try {

    const data =
      await callAdmin({
        action: 'getDashboard'
      })


    if (!data?.ok) {

      showMessage(
        data?.error ||
        'Impossibile caricare il setup.',
        'error'
      )

      return
    }


    currentUserId =
      data.currentUserId


    allowLeagueCreation.checked =
      data.settings
        .allow_league_creation


    multiLeagueEnabled.checked =
      data.settings
        .multi_league_enabled


    renderUsers(
      data.users
    )


  } catch (error) {

    console.error(error)

    showMessage(
      error.message ||
      'Accesso non autorizzato.',
      'error'
    )
  }
}



saveSettingsButton.addEventListener(
  'click',
  async () => {

    try {

      showMessage('')


      const data =
        await callAdmin({

          action:
            'updateSettings',

          allowLeagueCreation:
            allowLeagueCreation.checked,

          multiLeagueEnabled:
            multiLeagueEnabled.checked
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
        'Impostazioni salvate.',
        'success'
      )


      /*
       * Aggiorniamo anche
       * l'indicazione multi-lega
       * degli utenti.
       */
      await loadDashboard()


    } catch (error) {

      console.error(error)

      showMessage(
        error.message,
        'error'
      )
    }
  }
)


loadDashboard()
