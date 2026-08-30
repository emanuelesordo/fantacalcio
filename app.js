import { supabase } from './supabase.js'

const loginForm = document.getElementById('login-form')
const usernameInput = document.getElementById('username')
const passwordInput = document.getElementById('password')
const message = document.getElementById('message')
const loggedArea = document.getElementById('logged-area')
const loginArea = document.getElementById('login-area')
const currentUsername = document.getElementById('current-username')
const logoutButton = document.getElementById('logout-button')

function normalizeUsername(username) {
  return username
    .normalize('NFKC')
    .trim()
    .toLowerCase()
}

async function sha256(text) {
  const data = new TextEncoder().encode(text)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)

  return Array.from(new Uint8Array(hashBuffer))
    .map(byte => byte.toString(16).padStart(2, '0'))
    .join('')
}

async function getTechnicalEmail(usernameNormalized) {
  const hash = await sha256(usernameNormalized)

  return `u_${hash.slice(0, 60)}@fantacalcio.invalid`
}

function showMessage(text, type = '') {
  message.textContent = text
  message.className = type
}

async function showLoggedUser(user) {
  const { data: profile, error } = await supabase
    .from('profiles')
    .select('username')
    .eq('id', user.id)
    .single()

  if (error) {
    showMessage('Errore nel caricamento del profilo.', 'error')
    return
  }

  currentUsername.textContent = profile.username

  loginArea.hidden = true
  loggedArea.hidden = false
}

loginForm.addEventListener('submit', async event => {
  event.preventDefault()

  showMessage('')

  const username = usernameInput.value.trim()
  const usernameNormalized = normalizeUsername(username)
  const password = passwordInput.value

  if (username.length < 2) {
    showMessage('Inserisci un username valido.', 'error')
    return
  }

  if (password.length < 6) {
    showMessage('La password deve avere almeno 6 caratteri.', 'error')
    return
  }

  const email = await getTechnicalEmail(usernameNormalized)

  /*
   * 1. Proviamo prima il login.
   */
  const {
    data: loginData,
    error: loginError
  } = await supabase.auth.signInWithPassword({
    email,
    password
  })

  if (!loginError) {
    await showLoggedUser(loginData.user)
    return
  }

  /*
   * Se l'errore non è semplicemente "credenziali errate",
   * non proviamo a creare un nuovo account.
   */
  if (loginError.code !== 'invalid_credentials') {
    console.error(loginError)
    showMessage('Errore durante l’accesso.', 'error')
    return
  }

  /*
   * 2. Il login non è riuscito.
   * Proviamo quindi a creare l'utente.
   */
  const {
    data: signupData,
    error: signupError
  } = await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        username,
        username_normalized: usernameNormalized
      }
    }
  })

  if (signupError) {
    if (signupError.code === 'user_already_exists') {
      showMessage(
        'Username già utilizzato o password errata.',
        'error'
      )
      return
    }

    console.error(signupError)
    showMessage('Errore durante la creazione dell’account.', 'error')
    return
  }

  showMessage('Account creato.', 'success')

  await showLoggedUser(signupData.user)
})

logoutButton.addEventListener('click', async () => {
  await supabase.auth.signOut()

  loggedArea.hidden = true
  loginArea.hidden = false

  passwordInput.value = ''
  showMessage('')
})

const {
  data: { session }
} = await supabase.auth.getSession()

if (session?.user) {
  await showLoggedUser(session.user)
}
