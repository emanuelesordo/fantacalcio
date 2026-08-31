/* =========================================================
   league-join.js
   Onboarding lega atomico
   ========================================================= */

const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const ONBOARDING_API_URL =
  `${SUPABASE_URL}/functions/v1/onboarding-api`;


let previewData =
  null;


/* =========================================================
   DOM
   ========================================================= */

const joinMessage =
  document.getElementById(
    'join-message'
  );

const pendingSection =
  document.getElementById(
    'pending-section'
  );

const pendingList =
  document.getElementById(
    'pending-list'
  );

const leagueCode =
  document.getElementById(
    'league-code'
  );

const previewButton =
  document.getElementById(
    'preview-league-button'
  );

const requestSection =
  document.getElementById(
    'request-section'
  );

const previewLeagueName =
  document.getElementById(
    'preview-league-name'
  );

const previewLeagueCode =
  document.getElementById(
    'preview-league-code'
  );

const rolePresident =
  document.getElementById(
    'role-president'
  );

const roleVice =
  document.getElementById(
    'role-vice'
  );

const roleAuctioneer =
  document.getElementById(
    'role-auctioneer'
  );

const rolePresenter =
  document.getElementById(
    'role-presenter'
  );

const teamPanel =
  document.getElementById(
    'team-panel'
  );

const teamCreateChoice =
  document.getElementById(
    'team-create-choice'
  );

const teamModeExisting =
  document.getElementById(
    'team-mode-existing'
  );

const teamModeCreate =
  document.getElementById(
    'team-mode-create'
  );

const existingTeamArea =
  document.getElementById(
    'existing-team-area'
  );

const existingTeamSelect =
  document.getElementById(
    'existing-team-select'
  );

const newTeamArea =
  document.getElementById(
    'new-team-area'
  );

const newTeamName =
  document.getElementById(
    'new-team-name'
  );

const submitButton =
  document.getElementById(
    'submit-request-button'
  );


/* =========================================================
   STORAGE / UTILITY
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

  return String(
    value ?? ''
  )
    .replaceAll(
      '&',
      '&amp;'
    )
    .replaceAll(
      '<',
      '&lt;'
    )
    .replaceAll(
      '>',
      '&gt;'
    )
    .replaceAll(
      '"',
      '&quot;'
    )
    .replaceAll(
      "'",
      '&#039;'
    );
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


function selectedRoles() {

  return [
    rolePresident,
    roleVice,
    roleAuctioneer,
    rolePresenter
  ]
    .filter(
      checkbox =>
        checkbox.checked
    )
    .map(
      checkbox =>
        checkbox.value
    );
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
  })[role]
  || role;
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


  if (
    response.status === 401
  ) {

    window.location.href =
      'index.html';

    return null;
  }


  return data;
}


/* =========================================================
   RICHIESTE ESISTENTI
   ========================================================= */

function renderPendingRequests(
  requests
) {

  const useful =
    (requests || [])
      .filter(
        item =>
          item.status === 'pending'
          ||
          item.status === 'active'
      );


  pendingSection.hidden =
    useful.length === 0;


  if (!useful.length) {

    pendingList.innerHTML =
      '';

    return;
  }


  pendingList.innerHTML =
    useful
      .map(
        item => {

          const roles =
            (item.roles || [])
              .map(
                role => {

                  const status =
                    role.status === 'approved'
                      ? '✓'
                      : role.status === 'rejected'
                        ? '×'
                        : '…';


                  const teamName =
                    role.team?.name
                      ? ` · ${escapeHtml(
                          role.team.name
                        )}`
                      : '';


                  return `
                    <span class="badge ${
                      role.status === 'approved'
                        ? 'good'
                        : role.status === 'rejected'
                          ? 'warning'
                          : ''
                    }">
                      ${status}
                      ${escapeHtml(
                        role.label
                        ||
                        roleLabel(
                          role.role
                        )
                      )}
                      ${teamName}
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
                    ${roles}
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


    if (!data?.ok) {
      return;
    }


    renderPendingRequests(
      data.requests
      || []
    );


  } catch (error) {

    console.error(
      error
    );
  }
}


/* =========================================================
   PREVIEW LEGA
   ========================================================= */

function renderLeaguePreview() {

  const league =
    previewData
      ?.league;


  if (!league) {

    requestSection.hidden =
      true;

    return;
  }


  requestSection.hidden =
    false;


  previewLeagueName.textContent =
    league.name;


  previewLeagueCode.textContent =
    `Codice ${league.code}`;


  const membership =
    previewData
      ?.existingMembership;


  if (
    membership?.status === 'pending'
  ) {

    showMessage(
      'Hai già una richiesta di ingresso in attesa per questa lega.',
      'warning'
    );


    submitButton.disabled =
      true;


  } else if (
    membership?.status === 'active'
  ) {

    showMessage(
      'Sei già membro attivo di questa lega.',
      'success'
    );


    submitButton.disabled =
      true;


  } else {

    submitButton.disabled =
      false;
  }


  renderTeamOptions();

  renderTeamPanel();
}


function renderTeamOptions() {

  if (!previewData) {
    return;
  }


  const presidentSelected =
    rolePresident.checked;


  const viceSelected =
    roleVice.checked;


  const teams =
    previewData.teams
    || [];


  const eligible =
    teams
      .filter(
        team => {

          if (presidentSelected) {

            return !team.hasPresident;
          }


          if (viceSelected) {

            return team.hasPresident
              &&
              team.presidentStatus
              === 'active';
          }


          return true;
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
            value="${escapeHtml(
              team.id
            )}"
          >
            ${escapeHtml(
              team.name
            )}
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


/* =========================================================
   RUOLI / SQUADRA
   ========================================================= */

function renderTeamPanel() {

  const presidentSelected =
    rolePresident.checked;


  const viceSelected =
    roleVice.checked;


  const needsTeam =
    presidentSelected
    ||
    viceSelected;


  teamPanel.hidden =
    !needsTeam;


  if (!needsTeam) {

    teamModeExisting.checked =
      true;


    teamModeCreate.checked =
      false;


    newTeamName.value =
      '';


    return;
  }


  teamCreateChoice.hidden =
    !presidentSelected;


  if (
    viceSelected
    &&
    teamModeCreate.checked
  ) {

    teamModeExisting.checked =
      true;


    teamModeCreate.checked =
      false;
  }


  renderTeamMode();

  renderTeamOptions();
}


function renderTeamMode() {

  const create =
    teamModeCreate.checked;


  existingTeamArea.hidden =
    create;


  newTeamArea.hidden =
    !create;
}


rolePresident
  ?.addEventListener(
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


      renderTeamPanel();
    }
  );


roleVice
  ?.addEventListener(
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


      renderTeamPanel();
    }
  );


teamModeExisting
  ?.addEventListener(
    'change',
    renderTeamMode
  );


teamModeCreate
  ?.addEventListener(
    'change',
    renderTeamMode
  );


/* =========================================================
   CONTINUA CON CODICE
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

    console.error(
      error
    );


    previewData =
      null;


    requestSection.hidden =
      true;


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


previewButton
  ?.addEventListener(
    'click',
    previewLeague
  );


leagueCode
  ?.addEventListener(
    'keydown',
    event => {

      if (
        event.key === 'Enter'
      ) {

        event.preventDefault();

        previewLeague();
      }
    }
  );


leagueCode
  ?.addEventListener(
    'input',
    () => {

      leagueCode.value =
        leagueCode.value
          .toUpperCase();
    }
  );


/* =========================================================
   INVIA RICHIESTA
   ========================================================= */

submitButton
  ?.addEventListener(
    'click',
    async () => {

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


      const presidentSelected =
        roles.includes(
          'president'
        );


      const viceSelected =
        roles.includes(
          'vice'
        );


      let teamMode =
        'none';


      let teamId =
        null;


      let requestedTeamName =
        null;


      if (
        presidentSelected
        ||
        viceSelected
      ) {

        if (
          teamModeCreate.checked
        ) {

          teamMode =
            'create';


          requestedTeamName =
            newTeamName.value
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


        } else {

          teamMode =
            'existing';


          teamId =
            existingTeamSelect.value
            || null;


          if (!teamId) {

            showMessage(
              'Seleziona una squadra.',
              'error'
            );

            return;
          }
        }
      }


      submitButton.disabled =
        true;


      const oldText =
        submitButton.textContent;


      submitButton.textContent =
        'Invio...';


      showMessage('');


      try {

        const result =
          await onboardingApi({

            action:
              'submitJoinRequest',

            code:
              previewData
                .league
                .code,

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


        requestSection.hidden =
          true;


        previewData =
          null;


        rolePresident.checked =
          false;


        roleVice.checked =
          false;


        roleAuctioneer.checked =
          false;


        rolePresenter.checked =
          false;


        existingTeamSelect.value =
          '';


        newTeamName.value =
          '';


        await loadMyRequests();


      } catch (error) {

        console.error(
          error
        );


        showMessage(
          error.message
          ||
          'Errore durante l’invio della richiesta.',
          'error'
        );


      } finally {

        submitButton.disabled =
          false;


        submitButton.textContent =
          oldText;
      }
    }
  );


/* =========================================================
   BOOT
   ========================================================= */

if (!getSession()?.token) {

  window.location.href =
    'index.html';

} else {

  loadMyRequests();
}
