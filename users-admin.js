const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const ADMIN_URL =
  `${SUPABASE_URL}/functions/v1/global-admin`


const message =
  document.getElementById('admin-message')

const usersList =
  document.getElementById('users-list')

const userSearch =
  document.getElementById('user-search')

const userFilter =
  document.getElementById('user-filter')

const usersCount =
  document.getElementById('users-count')


let users = []
let currentUserId = null
let globalMultiLeague = false


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


function showMessage(
  text = '',
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

    return null
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
      dateStyle: 'short',
      timeStyle: 'short'
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
  ] = value.split('-')

  return `${day}/${month}/${year}`
}



function effectiveMultiLeague(user) {

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


  return globalMultiLeague
}



function filteredUsers() {

  const search =
    userSearch.value
      .trim()
      .toLowerCase()


  const filter =
    userFilter.value


  return users.filter(
    user => {

      const matchesSearch =
        user.username
          .toLowerCase()
          .includes(search)


      if (!matchesSearch) {
        return false
      }


      if (filter === 'active') {
        return user.is_enabled
      }


      if (filter === 'disabled') {
        return !user.is_enabled
      }


      if (filter === 'superadmin') {
        return user.is_super_admin
      }


      if (filter === 'multileague') {
        return effectiveMultiLeague(user)
      }


      return true
    }
  )
}



function renderUsers() {

  usersList.innerHTML = ''


  const visibleUsers =
    filteredUsers()


  usersCount.textContent =
    `${visibleUsers.length} utenti visualizzati su ${users.length}`


  for (const user of visibleUsers) {

    const card =
      document.createElement('article')


    card.className =
      'user-admin-card'


    const effective =
      effectiveMultiLeague(user)


    const isCurrent =
      user.id === currentUserId


    card.innerHTML = `

      <div class="user-admin-heading">

        <div>

          <strong class="user-admin-name">
            ${escapeHtml(user.username)}
          </strong>

          ${
            isCurrent
              ? '<span class="user-badge">TU</span>'
              : ''
          }

          ${
            user.is_super_admin
              ? '<span class="user-badge">SUPER ADMIN</span>'
              : ''
          }

          ${
            !user.is_enabled
              ? '<span class="user-badge warning">DISATTIVATO</span>'
              : ''
          }

        </div>


        <div class="multi-league-status">

          Multi-lega

          <strong>
            ${effective ? 'ON' : 'OFF'}
          </strong>

        </div>

      </div>


      <div class="user-admin-details">

        <div>
          <span>Registrato</span>
          <strong>
            ${formatDateTime(user.created_at)}
          </strong>
        </div>

        <div>
          <span>Ultimo accesso</span>
          <strong>
            ${formatDateTime(user.last_login_at)}
          </strong>
        </div>

      </div>


      <label class="setting-row">

        <span>
          Account attivo
        </span>

        <input
          class="user-enabled"
          type="checkbox"
          ${user.is_enabled ? 'checked' : ''}
          ${isCurrent ? 'disabled' : ''}
        >

      </label>


      <label class="setting-row">

        <span>
          Super Admin
        </span>

        <input
          class="user-super-admin"
          type="checkbox"
          ${user.is_super_admin ? 'checked' : ''}
          ${isCurrent ? 'disabled' : ''}
        >

      </label>


      <label class="user-select-field">

        <span>
          Multi-lega
        </span>

        <select class="user-multi-league">

          <option
            value="inherit"
            ${
              user.multi_league_override === 'inherit'
                ? 'selected'
                : ''
            }
          >
            Eredita dal setup globale
          </option>

          <option
            value="enabled"
            ${
              user.multi_league_override === 'enabled'
                ? 'selected'
                : ''
            }
          >
            Abilitato forzatamente
          </option>

          <option
            value="disabled"
            ${
              user.multi_league_override === 'disabled'
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
          user.multi_league_override === 'enabled'
          &&
          user.multi_league_override_until

            ? `Abilitazione valida fino al
               ${formatDate(
                 user.multi_league_override_until
               )}`

            : user.multi_league_override === 'disabled'

              ? 'Multi-lega disabilitato per questo utente.'

              : 'Segue il Setup Globale.'
        }

      </p>


      <button
        class="save-user"
        type="button"
      >
        Salva modifiche
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
            `Utente ${user.username} aggiornato.`,
            'success'
          )


          await loadUsers()


        } catch (error) {

          console.error(error)

          showMessage(
            error.message,
            'error'
          )
        }
      }
    )


    usersList.appendChild(card)
  }
}



async function loadUsers() {

  try {

    const data =
      await callAdmin({
        action: 'getDashboard'
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
      data.users


    currentUserId =
      data.currentUserId


    globalMultiLeague =
      data.settings
        .multi_league_enabled


    renderUsers()


  } catch (error) {

    console.error(error)

    showMessage(
      error.message ||
      'Accesso non autorizzato.',
      'error'
    )
  }
}



userSearch.addEventListener(
  'input',
  renderUsers
)


userFilter.addEventListener(
  'change',
  renderUsers
)


loadUsers()
