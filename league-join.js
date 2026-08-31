/* =========================================================
   league-join.js
   Onboarding lega atomico - v3
   ========================================================= */

const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const ONBOARDING_API_URL =
  `${SUPABASE_URL}/functions/v1/onboarding-api`;

let previewData = null;


/* =========================================================
   DOM
   ========================================================= */

const joinMessage =
  document.getElementById('join-message');

const pendingSection =
  document.getElementById('pending-section');

const pendingList =
  document.getElementById('pending-list');

const leagueCodeSection =
  document.getElementById('league-code-section');

const leagueCode =
  document.getElementById('league-code');

const previewButton =
  document.getElementById('preview-league-button');

const rolesSection =
  document.getElementById('roles-section');

const previewLeagueName =
  document.getElementById('preview-league-name');

const previewLeagueCode =
  document.getElementById('preview-league-code');

const rolePresident =
  document.getElementById('role-president');

const roleVice =
  document.getElementById('role-vice');

const roleAuctioneer =
  document.getElementById('role-auctioneer');

const rolePresenter =
  document.getElementById('role-presenter');

const rolesContinueButton =
  document.getElementById('roles-continue-button');

const rolesHelp =
  document.getElementById('roles-help');

const teamSection =
  document.getElementById('team-section');

const teamStepDescription =
  document.getElementById('team-step-description');

const teamCreateChoice =
  document.getElementById('team-create-choice');

const teamModeExisting =
  document.getElementById('team-mode-existing');

const teamModeCreate =
  document.getElementById('team-mode-create');

const existingTeamArea =
  document.getElementById('existing-team-area');

const existingTeamSelect =
  document.getElementById('existing-team-select');

const newTeamArea =
  document.getElementById('new-team-area');

const newTeamNameInput =
  document.getElementById('new-team-name');

const teamBackButton =
  document.getElementById('team-back-button');

const submitTeamRequestButton =
  document.getElementById('submit-team-request-button');

const noTeamConfirmSection =
  document.getElementById('no-team-confirm-section');

const noTeamSummary =
  document.getElementById('no-team-summary');

const noTeamBackButton =
  document.getElementById('no-team-back-button');

const submitNoTeamRequestButton =
  document.getElementById('submit-no-team-request-button');


/* =========================================================
   UTILITY
   ========================================================= */

function getSession() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_session'
      );

    return raw
      ? JSON.parse(raw)
      : null;

  } catch {

    return null;
  }
}


function escapeHtml(value) {

  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}


function showMessage(
  text = '',
  type = ''
) {

  joinMessage.textContent =
    text;

  joinMessage.className =
    `message ${type}`;
}


function roleLabel(role) {

  return ({
    president:
      'Presidente',

    vice:
      'Vice',

    auctioneer:
      'Banditore',

    presenter:
      'Presentatore'
  })[role] || role;
}


function selectedRoles() {

  return [
    rolePresident,
    roleVice,
    roleAuctioneer,
    rolePresenter
  ]
    .filter(
      input =>
        input?.checked
    )
    .map(
      input =>
        input.value
    );
}


function requiresTeam(roles) {

  return roles.includes('president')
    ||
    roles.includes('vice');
}


function hideStep3() {

  teamSection.hidden =
    true;

  noTeamConfirmSection.hidden =
    true;
}


function scrollToSection(element) {

  element?.scrollIntoView({
    behavior:
      'smooth',

    block:
      'start'
  });
}


/* =========================================================
   API
   ========================================================= */

async function onboardingApi(body) {

  const session =
    getSession();


  if (!session?.token) {

    window.location.href =
      'index.html';

    return null;
  }


  let response;


  try {

    response =
      await fetch(
        ONBOARDING_API_URL,
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
      );

  } catch {

    throw new Error(
      'Impossibile contattare il server.'
    );
  }


  let data;


  try {

    data =
      await response.json();

  } catch {

    throw new Error(
      'Risposta non valida dal server.'
    );
  }


  if (response.status === 401) {

    window.location.href =
      'index.html';

    return null;
  }


  return data;
}


/* =========================================================
   RICHIESTE ESISTENTI
   ========================================================= */

function renderMyRequests(requests) {

  const rows =
    (requests || [])
      .filter(
        item =>
          ['pending', 'active']
            .includes(item.status)
      );


  pendingSection.hidden =
    rows.length === 0;


  if (!rows.length) {

    pendingList.innerHTML =
      '';

    return;
  }


  pendingList.innerHTML =
    rows
      .map(
        item => {

          const roleBadges =
            (item.roles || [])
              .map(
                role => {

                  const state =
                    role.status === 'approved'
                      ? '✓'
                      : role.status === 'rejected'
                        ? '×'
                        : '…';

                  const team =
                    role.team?.name
                      ? ` · ${escapeHtml(role.team.name)}`
                      : '';

                  return `
                    <span class="badge ${
                      role.status === 'approved'
                        ? 'good'
                        : role.status === 'rejected'
                          ? 'warning'
                          : ''
                    }">
                      ${state}
                      ${escapeHtml(
                        role.label
                        || roleLabel(role.role)
                      )}
                      ${team}
                    </span>
                  `;
                }
              )
              .join(' ');


          return `
            <div class="list-row">
              <div class="list-row-main">

                <div class="list-row-title">

                  <strong>
                    ${escapeHtml(
                      item.league?.name
                      || 'Lega'
                    )}
                  </strong>

                  <small>
                    ${
                      item.status === 'pending'
                        ? 'Richiesta di ingresso in attesa'
                        : 'Ingresso approvato'
                    }
                  </small>

                  <div
                    class="league-actions"
                    style="margin-top:8px"
                  >
                    ${roleBadges}
                  </div>

                </div>

                <span class="badge ${
                  item.status === 'active'
                    ? 'good'
                    : ''
                }">
                  ${
                    item.status === 'active'
                      ? 'ATTIVA'
                      : 'PENDING'
                  }
                </span>

              </div>
            </div>
          `;
        }
      )
      .join('');
}


async function loadMyRequests() {

  try {

    const data =
      await onboardingApi({
        action:
          'getMyRequests'
      });

    if (data?.ok) {

      renderMyRequests(
        data.requests || []
      );
    }

  } catch (error) {

    console.error(error);
  }
}


/* =========================================================
   PREVIEW LEGA
   ========================================================= */

function resetRequestForm() {

  rolePresident.checked =
    false;

  roleVice.checked =
    false;

  roleAuctioneer.checked =
    false;

  rolePresenter.checked =
    false;

  teamModeExisting.checked =
    true;

  teamModeCreate.checked =
    false;

  existingTeamSelect.value =
    '';

  newTeamNameInput.value =
    '';

  hideStep3();

  updateRolesUi();
}


function renderLeaguePreview() {

  const league =
    previewData?.league;


  if (!league) {

    rolesSection.hidden =
      true;

    hideStep3();

    return;
  }


  rolesSection.hidden =
    false;

  previewLeagueName.textContent =
    league.name;

  previewLeagueCode.textContent =
    `Codice ${league.code}`;


  resetRequestForm();


  const membership =
    previewData.existingMembership;


  if (
    membership?.status === 'pending'
  ) {

    showMessage(
      'Hai già una richiesta di ingresso in attesa per questa lega.',
      'warning'
    );

    rolesContinueButton.disabled =
      true;

  } else if (
    membership?.status === 'active'
  ) {

    showMessage(
      'Sei già membro attivo di questa lega.',
      'success'
    );

    rolesContinueButton.disabled =
      true;

  } else {

    rolesContinueButton.disabled =
      false;

    showMessage('');
  }


  scrollToSection(
    rolesSection
  );
}


/* =========================================================
   RUOLI
   ========================================================= */

function updateRolesUi() {

  const roles =
    selectedRoles();

  const needsTeam =
    requiresTeam(roles);


  rolesContinueButton.textContent =
    needsTeam
      ? 'Continua alla squadra'
      : 'Continua';


  if (!roles.length) {

    rolesHelp.textContent =
      'Seleziona almeno un ruolo. Presidente e Vice richiedono una squadra; Banditore e Presentatore no.';

  } else if (needsTeam) {

    rolesHelp.textContent =
      'Hai selezionato Presidente o Vice: nel prossimo passaggio dovrai indicare la squadra.';

  } else {

    rolesHelp.textContent =
      'Banditore e Presentatore non richiedono alcuna squadra.';
  }


  hideStep3();
}


rolePresident.addEventListener(
  'change',
  () => {

    if (
      rolePresident.checked
      &&
      roleVice.checked
    ) {

      roleVice.checked =
        false;
    }

    updateRolesUi();
  }
);


roleVice.addEventListener(
  'change',
  () => {

    if (
      roleVice.checked
      &&
      rolePresident.checked
    ) {

      rolePresident.checked =
        false;
    }

    updateRolesUi();
  }
);


roleAuctioneer.addEventListener(
  'change',
  updateRolesUi
);


rolePresenter.addEventListener(
  'change',
  updateRolesUi
);


rolesContinueButton.addEventListener(
  'click',
  () => {

    const roles =
      selectedRoles();


    if (!roles.length) {

      showMessage(
        'Seleziona almeno un ruolo.',
        'error'
      );

      return;
    }


    showMessage('');


    if (requiresTeam(roles)) {

      renderTeamStep(roles);

    } else {

      renderNoTeamConfirmation(
        roles
      );
    }
  }
);


/* =========================================================
   STEP SQUADRA
   ========================================================= */

function renderTeamOptions(roles) {

  const teams =
    previewData?.teams || [];

  const wantsPresident =
    roles.includes('president');

  const wantsVice =
    roles.includes('vice');


  const eligible =
    teams.filter(
      team => {

        if (wantsPresident) {

          return !team.hasPresident;
        }

        if (wantsVice) {

          return team.hasPresident
            &&
            team.presidentStatus
            === 'active';
        }

        return false;
      }
    );


  existingTeamSelect.innerHTML =
    `
      <option value="">
        Seleziona...
      </option>
    `
    +
    eligible
      .map(
        team => `
          <option
            value="${escapeHtml(team.id)}"
          >
            ${escapeHtml(team.name)}
            ${
              team.hasPresident
                ? ' · Presidente presente'
                : ' · senza Presidente'
            }
          </option>
        `
      )
      .join('');
}


function renderTeamStep(roles) {

  const wantsPresident =
    roles.includes('president');

  const wantsVice =
    roles.includes('vice');


  noTeamConfirmSection.hidden =
    true;

  teamSection.hidden =
    false;

  teamCreateChoice.hidden =
    !wantsPresident;


  if (wantsVice) {

    teamModeExisting.checked =
      true;

    teamModeCreate.checked =
      false;

    teamStepDescription.textContent =
      'Scegli la squadra del Presidente che vuoi affiancare.';

  } else {

    teamStepDescription.textContent =
      'Scegli una squadra senza Presidente oppure creane una nuova.';
  }


  renderTeamMode();

  renderTeamOptions(roles);

  scrollToSection(
    teamSection
  );
}


function renderTeamMode() {

  const create =
    teamModeCreate.checked;

  existingTeamArea.hidden =
    create;

  newTeamArea.hidden =
    !create;
}


teamModeExisting.addEventListener(
  'change',
  renderTeamMode
);


teamModeCreate.addEventListener(
  'change',
  renderTeamMode
);


teamBackButton.addEventListener(
  'click',
  () => {

    teamSection.hidden =
      true;

    scrollToSection(
      rolesSection
    );
  }
);


/* =========================================================
   CONFERMA SENZA SQUADRA
   ========================================================= */

function renderNoTeamConfirmation(roles) {

  teamSection.hidden =
    true;

  noTeamConfirmSection.hidden =
    false;


  noTeamSummary.innerHTML = `
    <div class="list-row">
      <div class="list-row-main">

        <div class="list-row-title">

          <strong>
            ${escapeHtml(
              previewData?.league?.name
              || 'Lega'
            )}
          </strong>

          <small>
            Nessuna squadra richiesta
          </small>

        </div>

        <div class="league-actions">

          ${
            roles
              .map(
                role => `
                  <span class="badge good">
                    ${escapeHtml(
                      roleLabel(role)
                    )}
                  </span>
                `
              )
              .join('')
          }

        </div>

      </div>
    </div>
  `;


  scrollToSection(
    noTeamConfirmSection
  );
}


noTeamBackButton.addEventListener(
  'click',
  () => {

    noTeamConfirmSection.hidden =
      true;

    scrollToSection(
      rolesSection
    );
  }
);


/* =========================================================
   CERCA LEGA
   ========================================================= */

async function previewLeague() {

  const code =
    leagueCode.value
      .trim()
      .toUpperCase();


  if (code.length < 2) {

    showMessage(
      'Inserisci il codice della lega.',
      'error'
    );

    return;
  }


  previewButton.disabled =
    true;

  const oldText =
    previewButton.textContent;

  previewButton.textContent =
    'Controllo...';

  showMessage('');


  try {

    const data =
      await onboardingApi({
        action:
          'previewLeague',

        code
      });


    if (!data?.ok) {

      throw new Error(
        data?.error
        ||
        'Lega non trovata.'
      );
    }


    previewData =
      data;

    leagueCode.value =
      data.league.code;

    renderLeaguePreview();


  } catch (error) {

    console.error(error);

    previewData =
      null;

    rolesSection.hidden =
      true;

    hideStep3();

    showMessage(
      error.message
      ||
      'Errore durante la ricerca della lega.',
      'error'
    );


  } finally {

    previewButton.disabled =
      false;

    previewButton.textContent =
      oldText;
  }
}


previewButton.addEventListener(
  'click',
  previewLeague
);


leagueCode.addEventListener(
  'keydown',
  event => {

    if (event.key === 'Enter') {

      event.preventDefault();

      previewLeague();
    }
  }
);


leagueCode.addEventListener(
  'input',
  () => {

    leagueCode.value =
      leagueCode.value
        .toUpperCase();


    if (
      previewData
      &&
      leagueCode.value
        .trim()
        .toUpperCase()
      !==
      String(
        previewData.league.code
      )
        .trim()
        .toUpperCase()
    ) {

      previewData =
        null;

      rolesSection.hidden =
        true;

      hideStep3();
    }
  }
);


/* =========================================================
   INVIA RICHIESTA
   ========================================================= */

async function submitJoinRequest({
  teamMode = 'none',
  teamId = null,
  requestedTeamName = null,
  button
}) {

  if (!previewData?.league) {

    showMessage(
      'Prima verifica il codice della lega.',
      'error'
    );

    return;
  }


  const roles =
    selectedRoles();


  if (!roles.length) {

    showMessage(
      'Seleziona almeno un ruolo.',
      'error'
    );

    return;
  }


  if (!requiresTeam(roles)) {

    teamMode =
      'none';

    teamId =
      null;

    requestedTeamName =
      null;
  }


  button.disabled =
    true;

  const oldText =
    button.textContent;

  button.textContent =
    'Invio...';

  showMessage('');


  try {

    const result =
      await onboardingApi({
        action:
          'submitJoinRequest',

        code:
          previewData.league.code,

        roles,

        teamMode,

        teamId,

        newTeamName:
          requestedTeamName
      });


    if (!result?.ok) {

      throw new Error(
        result?.error
        ||
        'Impossibile inviare la richiesta.'
      );
    }


    showMessage(
      'Richiesta inviata. L’Admin della lega può ora approvarla.',
      'success'
    );


    previewData =
      null;

    rolesSection.hidden =
      true;

    hideStep3();

    rolePresident.checked =
      false;

    roleVice.checked =
      false;

    roleAuctioneer.checked =
      false;

    rolePresenter.checked =
      false;

    teamModeExisting.checked =
      true;

    teamModeCreate.checked =
      false;

    existingTeamSelect.value =
      '';

    newTeamNameInput.value =
      '';

    leagueCode.value =
      '';


    await loadMyRequests();


    scrollToSection(
      pendingSection.hidden
        ? leagueCodeSection
        : pendingSection
    );


  } catch (error) {

    console.error(error);

    showMessage(
      error.message
      ||
      'Errore durante l’invio della richiesta.',
      'error'
    );


  } finally {

    button.disabled =
      false;

    button.textContent =
      oldText;
  }
}


submitTeamRequestButton.addEventListener(
  'click',
  async () => {

    const roles =
      selectedRoles();


    if (!requiresTeam(roles)) {

      showMessage(
        'La selezione dei ruoli è cambiata. Torna allo step Ruoli.',
        'error'
      );

      return;
    }


    if (teamModeCreate.checked) {

      const requestedTeamName =
        newTeamNameInput.value
          .trim();


      if (
        requestedTeamName.length < 2
      ) {

        showMessage(
          'Inserisci il nome della nuova squadra.',
          'error'
        );

        return;
      }


      await submitJoinRequest({
        teamMode:
          'create',

        teamId:
          null,

        requestedTeamName,

        button:
          submitTeamRequestButton
      });

      return;
    }


    const teamId =
      existingTeamSelect.value
      || null;


    if (!teamId) {

      showMessage(
        'Seleziona una squadra.',
        'error'
      );

      return;
    }


    await submitJoinRequest({
      teamMode:
        'existing',

      teamId,

      requestedTeamName:
        null,

      button:
        submitTeamRequestButton
    });
  }
);


submitNoTeamRequestButton.addEventListener(
  'click',
  async () => {

    const roles =
      selectedRoles();


    if (requiresTeam(roles)) {

      showMessage(
        'Hai selezionato Presidente o Vice: devi indicare una squadra.',
        'error'
      );

      return;
    }


    await submitJoinRequest({
      teamMode:
        'none',

      teamId:
        null,

      requestedTeamName:
        null,

      button:
        submitNoTeamRequestButton
    });
  }
);


/* =========================================================
   START
   ========================================================= */

if (!getSession()?.token) {

  window.location.href =
    'index.html';

} else {

  loadMyRequests();

  updateRolesUi();
}
