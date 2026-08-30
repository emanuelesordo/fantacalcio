const SUPABASE_URL =
  'https://yyklmhzjxzkvycmxkegx.supabase.co';

const API_URL =
  `${SUPABASE_URL}/functions/v1/league-api`;

let selectedLeague = null;
let managementData = null;

const $ = id =>
  document.getElementById(id);

const leagueTitle =
  $('league-title');

const message =
  $('page-message');

const createTeamArea =
  $('create-team-area');

const createTeamForm =
  $('create-team-form');

const newTeamName =
  $('new-team-name');

const teamsList =
  $('teams-list');

const membersList =
  $('members-list');

const viceSection =
  $('vice-section');

const viceRequests =
  $('vice-requests');


/* =========================================================
   STORAGE
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


function getSelectedLeague() {

  try {

    const raw =
      localStorage.getItem(
        'fantacalcio_selected_league'
      );

    return raw
      ? JSON.parse(raw)
      : null;

  } catch {

    return null;
  }
}


/* =========================================================
   UTILITY
   ========================================================= */

function showMessage(
  text = '',
  type = ''
) {

  message.textContent =
    text;

  message.className =
    `message ${type}`;
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


function roleLabel(role) {

  const labels = {

    league_admin:
      'Admin Lega',

    auctioneer:
      'Banditore',

    presenter:
      'Presentatore',

    president:
      'Presidente',

    vice:
      'Vice'
  };


  return labels[role]
    || role;
}


/* =========================================================
   API
   ========================================================= */

async function callApi(body) {

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
        API_URL,
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

              leagueId:
                selectedLeague.id,

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
   SQUADRE
   ========================================================= */

function renderTeams() {

  const teams =
    managementData?.teams
    || [];


  const limit =
    Number(
      managementData?.teamLimit
      || 0
    );


  teamsList.innerHTML =
    '';


  if (
    teams.length === 0
  ) {

    teamsList.innerHTML = `
      <div class="empty-state">
        Nessuna squadra presente.
        ${
          limit
            ? `Puoi crearne fino a ${limit}.`
            : ''
        }
      </div>
    `;

    return;
  }


  for (
    const team
    of teams
  ) {

    const card =
      document.createElement(
        'div'
      );


    card.className =
      'league-card';


    card.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              team.name
            )}
          </h3>

          <p>
            ${
              team.presidentUsername

                ? `
                  Presidente:
                  <strong>
                    ${escapeHtml(
                      team.presidentUsername
                    )}
                  </strong>
                `

                : 'Nessun Presidente assegnato'
            }
          </p>

        </div>


        <span
          class="badge ${
            team.status === 'active'
              ? 'good'
              : ''
          }"
        >
          ${
            team.status === 'active'
              ? 'ATTIVA'
              : escapeHtml(
                  team.status
                )
          }
        </span>

      </div>

    `;


    teamsList.appendChild(
      card
    );
  }


  if (limit) {

    const info =
      document.createElement(
        'p'
      );


    info.className =
      'setting-help';


    info.textContent =
      `${teams.length} di ${limit} squadre create`;


    teamsList.appendChild(
      info
    );
  }
}


/* =========================================================
   BADGE MEMBRO
   ========================================================= */

function renderMemberBadges(member) {

  const badges = [];


  for (
    const role
    of member.leagueRoles || []
  ) {

    badges.push(`
      <span class="badge admin">
        ${escapeHtml(
          roleLabel(role)
        )}
      </span>
    `);
  }


  if (
    member.team
  ) {

    badges.push(`
      <span class="badge good">
        ${escapeHtml(
          roleLabel(
            member.team.role
          )
        )}
        ·
        ${escapeHtml(
          member.team.teamName
        )}
      </span>
    `);
  }


  return badges.join('');
}


/* =========================================================
   MEMBRI
   ========================================================= */

function renderMembers() {

  const members =
    managementData?.members
    || [];


  membersList.innerHTML =
    '';


  if (
    members.length === 0
  ) {

    membersList.innerHTML = `
      <div class="empty-state">
        Nessun membro attivo.
      </div>
    `;

    return;
  }


  const canManageRoles =
    managementData
      ?.permissions
      ?.canManageRoles
    === true;


  for (
    const member
    of members
  ) {

    const row =
      document.createElement(
        'details'
      );


    row.className =
      'user-row';


    const currentRoles =
      new Set(
        member.leagueRoles
        || []
      );


    row.innerHTML = `

      <summary>

        <div class="user-summary-name">

          <strong>
            ${escapeHtml(
              member.username
            )}
          </strong>

          <small>
            ${
              member.team

                ? `
                  ${escapeHtml(
                    member.team.teamName
                  )}
                  ·
                  ${escapeHtml(
                    roleLabel(
                      member.team.role
                    )
                  )}
                `

                : 'Nessuna squadra'
            }
          </small>

        </div>


        <div class="user-summary-status">

          ${renderMemberBadges(
            member
          )}

        </div>


        <span class="user-chevron">
          ⌄
        </span>

      </summary>


      <div class="user-detail">

        ${
          canManageRoles

            ? `

              <div class="user-metadata">

                <label>

                  <input
                    type="checkbox"
                    data-member-role="league_admin"
                    ${
                      currentRoles.has(
                        'league_admin'
                      )
                        ? 'checked'
                        : ''
                    }
                  >

                  Admin Lega

                </label>


                <label>

                  <input
                    type="checkbox"
                    data-member-role="auctioneer"
                    ${
                      currentRoles.has(
                        'auctioneer'
                      )
                        ? 'checked'
                        : ''
                    }
                  >

                  Banditore

                </label>


                <label>

                  <input
                    type="checkbox"
                    data-member-role="presenter"
                    ${
                      currentRoles.has(
                        'presenter'
                      )
                        ? 'checked'
                        : ''
                    }
                  >

                  Presentatore

                </label>

              </div>


              <button
                type="button"
                class="secondary"
                data-save-member-roles
                data-user-id="${escapeHtml(
                  member.userId
                )}"
              >
                Salva ruoli
              </button>

            `

            : `

              <p class="setting-help">
                Solo un Admin Lega può modificare
                i ruoli.
              </p>

            `
        }

      </div>

    `;


    /*
     * Conserviamo i ruoli attuali direttamente
     * sull'elemento per calcolare solo le modifiche.
     */

    row.dataset.currentRoles =
      JSON.stringify(
        member.leagueRoles
        || []
      );


    membersList.appendChild(
      row
    );
  }
}


/* =========================================================
   SALVA RUOLI
   ========================================================= */

async function saveMemberRoles(
  button
) {

  const userId =
    button.dataset.userId;


  const row =
    button.closest(
      '.user-row'
    );


  if (
    !userId
    ||
    !row
  ) {

    return;
  }


  let originalRoles = [];


  try {

    originalRoles =
      JSON.parse(
        row.dataset
          .currentRoles
        || '[]'
      );

  } catch {

    originalRoles = [];
  }


  const originalSet =
    new Set(
      originalRoles
    );


  const desiredSet =
    new Set(
      [
        ...row.querySelectorAll(
          '[data-member-role]'
        )
      ]
        .filter(
          checkbox =>
            checkbox.checked
        )
        .map(
          checkbox =>
            checkbox.dataset
              .memberRole
        )
    );


  const allRoles = [
    'league_admin',
    'auctioneer',
    'presenter'
  ];


  const changes =
    allRoles
      .filter(
        role =>
          originalSet.has(role)
          !==
          desiredSet.has(role)
      );


  if (
    changes.length === 0
  ) {

    showMessage(
      'Nessuna modifica da salvare.',
      'success'
    );

    return;
  }


  button.disabled =
    true;


  const oldText =
    button.textContent;


  button.textContent =
    'Salvataggio...';


  try {

    for (
      const role
      of changes
    ) {

      const result =
        await callApi({

          action:
            'setMemberRole',

          targetUserId:
            userId,

          role,

          enabled:
            desiredSet.has(role)
        });


      if (!result?.ok) {

        throw new Error(
          result?.error
          ||
          'Impossibile modificare il ruolo.'
        );
      }
    }


    showMessage(
      'Ruoli aggiornati.',
      'success'
    );


    await loadManagement();


  } catch (error) {

    console.error(error);


    showMessage(
      error.message
      ||
      'Errore durante il salvataggio.',
      'error'
    );


  } finally {

    button.disabled =
      false;


    button.textContent =
      oldText;
  }
}


/* =========================================================
   VICE
   ========================================================= */

function renderViceRequests() {

  const requests =
    managementData
      ?.viceRequests
    || [];


  const canApprove =
    managementData
      ?.permissions
      ?.canApproveVice
    === true;


  viceSection.hidden =
    !canApprove;


  viceRequests.innerHTML =
    '';


  if (!canApprove) {
    return;
  }


  if (
    requests.length === 0
  ) {

    viceRequests.innerHTML = `
      <div class="empty-state">
        Nessuna richiesta Vice da approvare.
      </div>
    `;

    return;
  }


  for (
    const request
    of requests
  ) {

    const row =
      document.createElement(
        'div'
      );


    row.className =
      'league-card';


    row.innerHTML = `

      <div class="league-card-header">

        <div>

          <h3>
            ${escapeHtml(
              request.username
            )}
          </h3>

          <p>
            ${
              request.leagueApproved

                ? 'Approvato dall’Admin Lega'

                : 'In attesa dell’Admin Lega'
            }
          </p>

        </div>


        <span
          class="badge ${
            request.leagueApproved
              ? 'good'
              : ''
          }"
        >
          VICE
        </span>

      </div>


      <div class="league-actions">

        <button
          type="button"
          class="success"
          data-approve-vice
          data-user-id="${escapeHtml(
            request.userId
          )}"
        >
          Approva
        </button>


        <button
          type="button"
          class="danger"
          data-reject-vice
          data-user-id="${escapeHtml(
            request.userId
          )}"
        >
          Rifiuta
        </button>

      </div>

    `;


    viceRequests.appendChild(
      row
    );
  }
}


/* =========================================================
   CREATE TEAM
   ========================================================= */

createTeamForm
  .addEventListener(
    'submit',
    async event => {

      event.preventDefault();


      showMessage('');


      const teamName =
        newTeamName
          .value
          .trim();


      if (
        teamName.length < 2
      ) {

        showMessage(
          'Inserisci un nome valido per la squadra.',
          'error'
        );

        return;
      }


      const button =
        createTeamForm
          .querySelector(
            'button[type="submit"]'
          );


      button.disabled =
        true;


      const oldText =
        button.textContent;


      button.textContent =
        'Creazione...';


      try {

        const result =
          await callApi({

            action:
              'createTeam',

            teamName
          });


        if (!result?.ok) {

          throw new Error(
            result?.error
            ||
            'Impossibile creare la squadra.'
          );
        }


        newTeamName.value =
          '';


        showMessage(
          'Squadra creata.',
          'success'
        );


        await loadManagement();


      } catch (error) {

        console.error(error);


        showMessage(
          error.message
          ||
          'Errore durante la creazione.',
          'error'
        );


      } finally {

        button.disabled =
          false;


        button.textContent =
          oldText;
      }
    }
  );


/* =========================================================
   EVENTI MEMBRI
   ========================================================= */

membersList
  .addEventListener(
    'click',
    event => {

      const button =
        event.target.closest(
          '[data-save-member-roles]'
        );


      if (!button) {
        return;
      }


      saveMemberRoles(
        button
      );
    }
  );


/* =========================================================
   EVENTI VICE
   ========================================================= */

viceRequests
  .addEventListener(
    'click',
    async event => {

      const approveButton =
        event.target.closest(
          '[data-approve-vice]'
        );


      const rejectButton =
        event.target.closest(
          '[data-reject-vice]'
        );


      const button =
        approveButton
        ||
        rejectButton;


      if (!button) {
        return;
      }


      const userId =
        button.dataset.userId;


      if (!userId) {
        return;
      }


      const action =
        approveButton
          ? 'approveVice'
          : 'rejectVice';


      button.disabled =
        true;


      try {

        const result =
          await callApi({

            action,

            targetUserId:
              userId
          });


        if (!result?.ok) {

          throw new Error(
            result?.error
            ||
            'Impossibile completare l’operazione.'
          );
        }


        showMessage(
          approveButton
            ? 'Vice approvato.'
            : 'Richiesta Vice rifiutata.',
          'success'
        );


        await loadManagement();


      } catch (error) {

        console.error(error);


        showMessage(
          error.message
          ||
          'Errore durante l’operazione.',
          'error'
        );


      } finally {

        button.disabled =
          false;
      }
    }
  );


/* =========================================================
   LOAD
   ========================================================= */

async function loadManagement() {

  showMessage('');


  try {

    const data =
      await callApi({
        action:
          'getManagementData'
      });


    if (!data?.ok) {

      showMessage(
        data?.error
        ||
        'Impossibile caricare la gestione della lega.',
        'error'
      );

      return;
    }


    managementData =
      data;


    leagueTitle.textContent =
      `Membri e squadre · ${
        data.league.name
      }`;


    createTeamArea.hidden =
      !data.permissions
        .canCreateTeam;


    renderTeams();

    renderMembers();

    renderViceRequests();


  } catch (error) {

    console.error(error);


    showMessage(
      error.message
      ||
      'Errore durante il caricamento.',
      'error'
    );
  }
}


/* =========================================================
   START
   ========================================================= */

selectedLeague =
  getSelectedLeague();


if (!selectedLeague?.id) {

  window.location.href =
    'leagues.html';

} else {

  loadManagement();
}
