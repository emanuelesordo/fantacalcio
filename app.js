const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

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


function getSession() {

  const raw =
    localStorage.getItem('fantacalcio_session')

  if (!raw) {
    return null
  }

  try {

    const session = JSON.parse(raw)

    if (
      new Date(session.expiresAt).getTime()
      <= Date.now()
    ) {

      localStorage.removeItem(
        'fantacalcio_session'
      )

      return null
    }

    return session

  } catch {

    localStorage.removeItem(
      'fantacalcio_session'
    )

    return null
  }

}


function showLoggedUser(session) {

  currentUsername.textContent =
    session.user.username

  loginArea.hidden = true
  loggedArea.hidden = false

}


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

      const response = await fetch(
        `${SUPABASE_URL}/functions/v1/simple-auth`,
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json'
          },

          body: JSON.stringify({
            username,
            password
          })
        }
      )

      const data = await response.json()

      if (!data.ok) {
        showMessage(
          data.error ||
          'Errore durante l’accesso.',
          'error'
        )
        return
      }

      saveSession(data)

      showLoggedUser(
        getSession()
      )

    } catch (error) {

      console.error(error)

      showMessage(
        'Impossibile contattare il server.',
        'error'
      )

    }

  }
)


logoutButton.addEventListener(
  'click',
  () => {

    localStorage.removeItem(
      'fantacalcio_session'
    )

    loggedArea.hidden = true
    loginArea.hidden = false

    passwordInput.value = ''

    showMessage('')

  }
)


const currentSession = getSession()

if (currentSession) {
  showLoggedUser(currentSession)
}
