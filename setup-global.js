const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const ADMIN_URL =
  `${SUPABASE_URL}/functions/v1/global-admin`


const message =
  document.getElementById('admin-message')

const allowLeagueCreation =
  document.getElementById('allow-league-creation')

const multiLeagueEnabled =
  document.getElementById('multi-league-enabled')

const saveSettingsButton =
  document.getElementById('save-global-settings')


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



async function loadSettings() {

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


    allowLeagueCreation.checked =
      data.settings.allow_league_creation


    multiLeagueEnabled.checked =
      data.settings.multi_league_enabled


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


    } catch (error) {

      console.error(error)

      showMessage(
        error.message,
        'error'
      )
    }
  }
)


loadSettings()
