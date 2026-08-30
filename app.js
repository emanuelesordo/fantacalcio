const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co'

const AUTH_URL =
  `${SUPABASE_URL}/functions/v1/simple-auth`


/* =========================================================
   ELEMENTI PAGINA
   ========================================================= */

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

const globalSetupLink =
  document.getElementById('global-setup-link')


/* =========================================================
   COSTANTI
   ========================================================= */

const SESSION_STORAGE_KEY =
  'fantacalcio_session'


/* =========================================================
   INTERFACCIA
   ========================================================= */

function showMessage(
  text = '',
  type = ''
) {

  if (!message) {
    return
  }

  message.textContent = text
  message.className = type
}


function showLogin() {

  if (loggedArea) {
    loggedArea.hidden = true
  }

  if (loginArea) {
    loginArea.hidden = false
  }

  if (globalSetupLink) {
    globalSetupLink.hidden = true
  }
}


function hideAllAreas() {

  if (loginArea) {
    loginArea.hidden = true
  }

  if (loggedArea) {
    loggedArea.hidden = true
  }
}


function showLoggedUser(session) {

  if (!session?.user) {
    showLogin()
    return
  }

  if (currentUsername) {
    currentUsername.textContent =
      session.user.username
  }

  /*
   * Il collegamento al Setup Globale
   * compare esclusivamente ai Super Admin.
   */
  if (globalSetupLink) {

    globalSetupLink.hidden =
      session.user.isSuperAdmin !== true
  }

  if (loginArea) {
    loginArea.hidden = true
  }

  if (loggedArea) {
    loggedArea.hidden = false
  }
}


/* =========================================================
   SESSIONE LOCALE
   ========================================================= */

function saveLocalSession(session) {

  localStorage.setItem(
    SESSION_STORAGE_KEY,
    JSON.stringify(session)
  )
}


function readLocalSession() {

  const raw =
    localStorage.getItem(
      SESSION_STORAGE_KEY
    )

  if (!raw) {
    return null
  }

  try {

    const session =
      JSON.parse(raw)

    if (
      !session ||
      typeof session !== 'object'
    ) {

      clearLocalSession()
      return null
    }


    if (!session.token) {

      clearLocalSession()
      return null
    }


    /*
     * Primo controllo locale.
     *
     * La verifica definitiva viene comunque
     * sempre fatta successivamente dal server.
     */
    if (session.expiresAt) {

      const expiry =
        new Date(
          session.expiresAt
        ).getTime()

      if (
        Number.isFinite(expiry)
        &&
        expiry <= Date.now()
      ) {

        clearLocalSession()
        return null
      }
    }

    return session

  } catch (error) {

    console.error(
      'Sessione locale non valida:',
      error
    )

    clearLocalSession()

    return null
  }
}


function clearLocalSession() {

  localStorage.removeItem(
    SESSION_STORAGE_KEY
  )
}


/* =========================================================
   CHIAMATE AL SERVER AUTH
   ========================================================= */

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


  let data

  try {

    data =
      await response.json()

  } catch {

    throw new Error(
      'Risposta non valida dal server.'
    )
  }


  return {
    response,
    data
  }
}


/* =========================================================
   VALIDAZIONE SESSIONE
   ========================================================= */

async function validateSession(
  sessionToken
) {

  const {
    response,
    data
  } = await callAuth({
    action: 'validate',

    sessionToken
  })


  if (
    !response.ok ||
    !data?.ok ||
    !data?.valid
  ) {

    return null
  }


  return {
    token:
      sessionToken,

    expiresAt:
      data.expiresAt,

    user: {
      id:
        data.user.id,

      username:
        data.user.username,

      isSuperAdmin:
        data.user.isSuperAdmin === true
    }
  }
}


/* =========================================================
   LOGIN / REGISTRAZIONE
   ========================================================= */

if (loginForm) {

  loginForm.addEventListener(
    'submit',
    async event => {

      event.preventDefault()

      showMessage('')


      const username =
        usernameInput
          ?.value
          ?.trim()
        || ''


      const password =
        passwordInput
          ?.value
        || ''


      if (
        username.length < 2
        ||
        username.length > 30
      ) {

        showMessage(
          'Inserisci un username valido.',
          'error'
        )

        return
      }


      if (
        password.length < 6
      ) {

        showMessage(
          'La password deve avere almeno 6 caratteri.',
          'error'
        )

        return
      }


      try {

        const {
          response,
          data
        } = await callAuth({

          action:
            'login',

          username,
          password
        })


        if (
          !response.ok ||
          !data?.ok
        ) {

          showMessage(
            data?.error
            ||
            'Errore durante l’accesso.',
            'error'
          )

          return
        }


        /*
         * La risposta LOGIN contiene il token.
         *
         * Facciamo subito una VALIDATE in modo
         * da recuperare anche i privilegi
         * aggiornati dell'utente, compreso
         * isSuperAdmin.
         */

        const validatedSession =
          await validateSession(
            data.sessionToken
          )


        if (!validatedSession) {

          showMessage(
            'Sessione creata ma non validabile.',
            'error'
          )

          return
        }


        saveLocalSession(
          validatedSession
        )


        showLoggedUser(
          validatedSession
        )


        if (passwordInput) {
          passwordInput.value = ''
        }


        if (data.isNew) {

          showMessage(
            'Account creato correttamente.',
            'success'
          )

        } else {

          showMessage('')
        }


      } catch (error) {

        console.error(
          'Errore login:',
          error
        )

        showMessage(
          'Impossibile contattare il server.',
          'error'
        )
      }
    }
  )
}


/* =========================================================
   LOGOUT
   ========================================================= */

if (logoutButton) {

  logoutButton.addEventListener(
    'click',
    async () => {

      const session =
        readLocalSession()


      /*
       * Rimuoviamo subito la sessione
       * dal dispositivo.
       */
      clearLocalSession()

      showLogin()
      showMessage('')


      if (passwordInput) {
        passwordInput.value = ''
      }


      /*
       * Poi la revochiamo anche lato server.
       */
      if (session?.token) {

        try {

          const {
            response,
            data
          } = await callAuth({

            action:
              'logout',

            sessionToken:
              session.token
          })


          if (
            !response.ok ||
            !data?.ok
          ) {

            console.error(
              'Logout server non riuscito:',
              data
            )
          }


        } catch (error) {

          console.error(
            'Errore durante il logout server:',
            error
          )
        }
      }
    }
  )
}


/* =========================================================
   AVVIO APP
   ========================================================= */

async function initializeApp() {

  /*
   * Evitiamo che venga mostrato per un istante
   * il login mentre stiamo verificando
   * una sessione già esistente.
   */
  hideAllAreas()

  showMessage('')


  const localSession =
    readLocalSession()


  /*
   * Nessuna sessione salvata.
   */
  if (!localSession?.token) {

    showLogin()

    return
  }


  /*
   * Sessione trovata:
   * la controlliamo sempre sul server.
   */
  try {

    const validatedSession =
      await validateSession(
        localSession.token
      )


    /*
     * Token scaduto, revocato
     * o account disabilitato.
     */
    if (!validatedSession) {

      clearLocalSession()

      showLogin()

      return
    }


    /*
     * Aggiorniamo localStorage con
     * i dati ufficiali restituiti
     * dal server.
     */
    saveLocalSession(
      validatedSession
    )


    showLoggedUser(
      validatedSession
    )


  } catch (error) {

    console.error(
      'Errore validazione sessione:',
      error
    )


    /*
     * IMPORTANTE:
     * se c'è solo un problema temporaneo
     * di rete NON cancelliamo il token.
     *
     * Così non perdiamo una sessione valida.
     */
    showLogin()

    showMessage(
      'Impossibile verificare la sessione. Riprova.',
      'error'
    )
  }
}


/* =========================================================
   START
   ========================================================= */

initializeApp()
