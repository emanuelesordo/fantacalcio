const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const AUTH_URL =
  `${SUPABASE_URL}/functions/v1/simple-auth`


const loginForm =
  document.getElementById('login-form')

const usernameInput =
  document.getElementById('username')

const passwordInput =
  document.getElementById('password')

const message =
  document.getElementById('message')

const loggedArea =
  document.getElementById('logged-area')

const loginArea =
  document.getElementById('login-area')

const currentUsername =
  document.getElementById('current-username')

const logoutButton =
  document.getElementById('logout-button')


function showMessage(text, type = '') {
  message.textContent = text
  message.className = type
}


function saveSession(data) {

  localStorage.setItem(
    'fantacalcio_session',
    JSON.stringify({
      token: data.sessionToken,
      expiresAt: data.expiresAt,

      user: data.user
    })
  )
}


function readLocalSession() {

  const raw =
    localStorage.getItem(
      'fantacalcio_session'
    )

  if (!raw) {
    return null
  }

  try {

    return JSON.parse(raw)

  } catch {

    clearLocalSession()
    return null
  }
}


function clearLocalSession() {

  localStorage.removeItem(
    'fantacalcio_session'
  )
}


function showLogin() {

  loggedArea.hidden = true
  loginArea.hidden = false

  passwordInput.value = ''
}


function showLoggedUser(session) {

  currentUsername.textContent =
    session.user.username

  loginArea.hidden = true
  loggedArea.hidden = false
}


async function callAuth(body) {

  const response =
    await fetch(
      AUTH_URL,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json'
        },

        body:
          JSON.stringify(body)
      }
    )

  return await response.json()
}


/*
 * LOGIN
 */
loginForm.addEventListener(
  'submit',
  async event => {

    event.preventDefault()

    showMessage('')

    const username =
      usernameInput.value.trim()

    const password =
      passwordInput.value


    if (username.length < 2) {

      showMessage(
        'Inserisci un username valido.',
        'error'
      )

      return
    }


    if (password.length < 6) {

      showMessage(
        'La password deve avere almeno 6 caratteri.',
        'error'
      )

      return
    }


    try {

      const data =
        await callAuth({
          action: 'login',
          username,
          password
        })


      if (!data.ok) {

        showMessage(
          data.error ||
          'Errore durante l’accesso.',
          'error'
        )

        return
      }


      saveSession(data)

      showLoggedUser({
        user: data.user,
        expiresAt: data.expiresAt
      })


    } catch (error) {

      console.error(error)

      showMessage(
        'Impossibile contattare il server.',
        'error'
      )
    }
  }
)


/*
 * LOGOUT
 */
logoutButton.addEventListener(
  'click',
  async () => {

    const session =
      readLocalSession()


    /*
     * Prima togliamo immediatamente
     * la sessione dal browser.
     */
    clearLocalSession()

    showLogin()
    showMessage('')


    /*
     * Poi chiediamo al server
     * di revocarla.
     */
    if (session?.token) {

      try {

        await callAuth({
          action: 'logout',
          sessionToken:
            session.token
        })

      } catch (error) {

        console.error(
          'Errore logout server:',
          error
        )
      }
    }
  }
)


/*
 * AVVIO APP:
 * controlliamo sul SERVER
 * l'eventuale sessione salvata.
 */
async function initializeApp() {

  const localSession =
    readLocalSession()


  if (!localSession?.token) {

    showLogin()
    return
  }


  try {

    const data =
      await callAuth({
        action: 'validate',
        sessionToken:
          localSession.token
      })


    if (
      !data.ok ||
      !data.valid
    ) {

      clearLocalSession()
      showLogin()

      return
    }


    /*
     * Aggiorniamo i dati locali
     * con quelli ufficiali server.
     */
    localStorage.setItem(
      'fantacalcio_session',
      JSON.stringify({
        token:
          localSession.token,

        expiresAt:
          data.expiresAt,

        user:
          data.user
      })
    )


    showLoggedUser({
      user: data.user,
      expiresAt: data.expiresAt
    })


  } catch (error) {

    console.error(
      'Errore validazione sessione:',
      error
    )

    /*
     * Se il server è temporaneamente
     * irraggiungibile non cancelliamo
     * subito la sessione.
     */
    showLogin()

    showMessage(
      'Impossibile verificare la sessione.',
      'error'
    )
  }
}


initializeApp()
