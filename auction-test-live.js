/* auction-test-live.js
   Add-on per asta di test con squadre reali.
   Richiede league-auction.js?v=2 caricato prima di questo file.
*/

const testUi = {
  bar: document.getElementById('simple-test-bar'),
  toggle: document.getElementById('simple-test-toggle'),
  help: document.getElementById('simple-test-help'),
  auctioneer: document.getElementById('test-auctioneer-panel'),
  team: document.getElementById('test-bid-team'),
  amount: document.getElementById('test-bid-amount'),
  bid: document.getElementById('test-place-bid'),
  award: document.getElementById('test-award-player'),
  finish: document.getElementById('test-finish-review'),
  bidHelp: document.getElementById('test-bid-help'),
  review: document.getElementById('test-roster-review'),
  reviewList: document.getElementById('test-roster-review-list'),
  print: document.getElementById('test-print-rosters'),
  csv: document.getElementById('test-download-csv'),
  purge: document.getElementById('test-purge-data'),
  csvNote: document.getElementById('test-csv-note')
};

let testLastBid = null;


function testSession() {
  return auctionData?.auctionSession || null;
}


function testEnabled() {
  return (
    testSession()?.is_test === true
    || auctionData?.testMode?.enabled === true
  );
}


function testCanControl() {
  return auctionData?.permissions?.canControlAuction === true;
}


function participatingTeams() {
  const ordered = (auctionData?.teamOrder || [])
    .map(item => item.team)
    .filter(Boolean);

  return ordered.length ? ordered : (auctionData?.teams || []);
}


function renderTestTeamList() {
  if (!testEnabled() || !teamsBox) return;

  teamsBox.innerHTML = (auctionData?.teams || [])
    .map(team => `
      <div class="list-row">
        <div class="list-row-main">
          <div class="list-row-title">
            <strong>${escapeHtml(team.name)}</strong>
            <small>
              ${
                team.president
                  ? `Presidente: ${escapeHtml(team.president.username)}`
                  : 'Nessun Presidente · nel test opera il Banditore'
              }
            </small>
          </div>
          <span class="badge good">TEST OK</span>
        </div>
      </div>
    `)
    .join('');
}


function renderTestMode() {
  if (!auctionData || !testUi.bar) return;

  const canControl = testCanControl();
  const session = testSession();
  const enabled = testEnabled();

  testUi.bar.hidden = !canControl;
  if (!canControl) return;

  testUi.toggle.checked = enabled;
  testUi.toggle.disabled = Boolean(session)
    || auctionData?.testMode?.canToggle === false;

  if (!enabled) {
    testUi.help.textContent =
      'Usa le squadre reali già create; nel test i Presidenti non sono obbligatori.';
    return;
  }

  const readiness = auctionData?.testReadiness || {
    ready: false,
    blockers: [],
    teamCount: 0
  };

  if (!session) {
    prepareButton.disabled = !readiness.ready;

    blockersBox.innerHTML = readiness.blockers?.length
      ? readiness.blockers
          .map(item => `• ${escapeHtml(item)}`)
          .join('<br>')
      : 'Modalità test pronta: i Presidenti non sono obbligatori.';

    const readinessBadge = statusLine?.querySelector('.badge');

    if (readinessBadge) {
      readinessBadge.textContent = readiness.ready
        ? 'TEST PRONTO'
        : 'TEST DA COMPLETARE';

      readinessBadge.classList.toggle(
        'good',
        readiness.ready
      );

      readinessBadge.classList.toggle(
        'warning',
        !readiness.ready
      );
    }

    testUi.help.textContent =
      `${readiness.teamCount || 0} squadre reali · minimo 2 · Presidenti non richiesti`;

  } else {
    testUi.help.textContent = session.status === 'review'
      ? 'Test concluso: le assegnazioni restano disponibili per il riepilogo.'
      : 'Sessione temporanea: Admin/Banditore può operare per tutte le squadre.';

    if (!statusLine?.querySelector('[data-simple-test-badge]')) {
      const badge = document.createElement('span');

      badge.className = 'badge warning';
      badge.dataset.simpleTestBadge = 'true';
      badge.textContent = 'TEST';

      statusLine?.appendChild(badge);
    }
  }

  if (session?.status === 'review') {
    phaseTitle.textContent = 'Riepilogo test';

    phaseSubtitle.textContent =
      'Controlla ed esporta le rose prima di eliminare i dati temporanei.';
  }

  renderTestTeamList();
}


function renderTestAuctioneer() {
  if (!testUi.auctioneer) return;

  const session = testSession();
  const player = auctionData?.currentPlayer;

  const show = Boolean(
    session?.is_test === true
    && session.status === 'live'
    && testCanControl()
    && player
  );

  testUi.auctioneer.hidden = !show;

  if (!show) return;

  const leaderId = session.current_bidder_team_id;
  const previousTeam = testUi.team.value;

  testUi.team.innerHTML = participatingTeams()
    .map(team => `
      <option
        value="${escapeHtml(team.id)}"
        ${team.id === leaderId ? 'disabled' : ''}
      >
        ${escapeHtml(team.name)}
        ${team.id === leaderId ? ' · leader' : ''}
      </option>
    `)
    .join('');

  if (
    previousTeam
    && participatingTeams().some(
      team =>
        team.id === previousTeam
        && team.id !== leaderId
    )
  ) {
    testUi.team.value = previousTeam;
  }

  const minimum = Math.max(
    1,
    Number(session.current_bid || 0) + 1
  );

  testUi.amount.min = String(minimum);

  if (
    testLastBid !== session.current_bid
    || !testUi.amount.value
    || Number(testUi.amount.value) < minimum
  ) {
    testUi.amount.value = String(minimum);
    testLastBid = session.current_bid;
  }

  const leader = auctionData?.currentBidderTeam;

  testUi.bidHelp.textContent = leader
    ? `Leader: ${leader.name} a ${session.current_bid}.`
    : session.current_bid
      ? `Base corrente: ${session.current_bid}. Nessun leader.`
      : 'Nessuna offerta registrata.';

  testUi.award.disabled =
    !leader
    || !session.current_bid;
}


function reviewData() {
  return auctionData?.rosterReview || null;
}


function renderTestReview() {
  if (!testUi.review) return;

  const session = testSession();
  const review = reviewData();

  const show = Boolean(
    session?.is_test === true
    && review
    && (
      review.totalAssignments > 0
      || session.status === 'review'
    )
  );

  testUi.review.hidden = !show;

  if (!show) {
    testUi.reviewList.innerHTML = '';
    return;
  }

  const finalReview =
    session.status === 'review';

  testUi.purge.hidden =
    !finalReview;

  testUi.print.disabled =
    review.totalAssignments < 1;

  testUi.csv.disabled =
    review.totalAssignments < 1;

  testUi.csvNote.textContent = finalReview
    ? 'Le assegnazioni restano intatte finché non premi “Elimina dati test”.'
    : 'Riepilogo parziale dell’asta di test in corso.';

  testUi.reviewList.innerHTML = review.teams
    .map(team => {
      const players = team.players?.length
        ? team.players
            .map(assignment => {
              const player =
                assignment.player || {};

              const roles =
                getPlayerRoles(player)
                  .join('/');

              return `
                <div class="setting-row">
                  <span>
                    <strong>
                      ${escapeHtml(
                        player.name || 'Giocatore'
                      )}
                    </strong>

                    <small>
                      ${escapeHtml(roles || '—')}
                      ·
                      ${escapeHtml(
                        player.serie_a_team || '—'
                      )}
                    </small>
                  </span>

                  <strong>
                    ${escapeHtml(
                      assignment.purchase_price
                    )}
                  </strong>
                </div>
              `;
            })
            .join('')
        : `
            <div class="empty-state">
              Nessun acquisto.
            </div>
          `;

      return `
        <div class="league-card">

          <div class="league-card-header">

            <div>
              <h3>
                ${escapeHtml(team.name)}
              </h3>

              <p>
                ${team.players.length} giocatori
                · spesi ${team.spent}
                · residui ${team.remaining}
              </p>
            </div>

            <span class="badge">
              ${team.spent}
            </span>

          </div>

          <div class="divider"></div>

          ${players}

        </div>
      `;
    })
    .join('');
}


async function refreshTestAuction() {
  await loadLobby();
}


testUi.toggle?.addEventListener(
  'change',
  async () => {
    const enabled =
      testUi.toggle.checked;

    testUi.toggle.disabled =
      true;

    try {
      const result = await callApi({
        action: 'setTestMode',
        enabled
      });

      if (!result?.ok) {
        throw new Error(
          result?.error
          || 'Impossibile modificare la modalità test.'
        );
      }

      showMessage(
        enabled
          ? 'Asta di test attivata.'
          : 'Asta di test disattivata.',
        'success'
      );

      await refreshTestAuction();

    } catch (error) {
      console.error(error);

      testUi.toggle.checked =
        !enabled;

      showMessage(
        error.message
        || 'Errore durante la modifica della modalità test.',
        'error'
      );

    } finally {
      renderTestMode();
    }
  }
);


testUi.bid?.addEventListener(
  'click',
  async () => {
    const session =
      testSession();

    const teamId =
      testUi.team.value;

    const amount =
      Number(testUi.amount.value);

    if (!session || !teamId) {
      showMessage(
        'Seleziona una squadra.',
        'error'
      );

      return;
    }

    const minimum = Math.max(
      1,
      Number(session.current_bid || 0) + 1
    );

    if (
      !Number.isInteger(amount)
      || amount < minimum
    ) {
      showMessage(
        `L’offerta minima è ${minimum}.`,
        'error'
      );

      return;
    }

    testUi.bid.disabled =
      true;

    const oldText =
      testUi.bid.textContent;

    testUi.bid.textContent =
      'Registrazione...';

    try {
      const result = await callApi({
        action: 'placeBid',
        sessionId: session.id,
        teamId,
        amount,
        source: 'TEST_BANDITORE'
      });

      if (!result?.ok) {
        throw new Error(
          result?.error
          || 'Impossibile registrare l’offerta.'
        );
      }

      showMessage(
        `Offerta ${amount} registrata.`,
        'success'
      );

      await refreshTestAuction();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        || 'Errore durante il rilancio.',
        'error'
      );

    } finally {
      testUi.bid.disabled =
        false;

      testUi.bid.textContent =
        oldText;
    }
  }
);


testUi.award?.addEventListener(
  'click',
  async () => {
    const session =
      testSession();

    const leader =
      auctionData?.currentBidderTeam;

    if (
      !session
      || !leader
      || !session.current_bid
    ) {
      showMessage(
        'Non c’è un leader da aggiudicare.',
        'error'
      );

      return;
    }

    testUi.award.disabled =
      true;

    const oldText =
      testUi.award.textContent;

    testUi.award.textContent =
      'Aggiudicazione...';

    try {
      const result = await callApi({
        action: 'awardPlayer',
        sessionId: session.id
      });

      if (!result?.ok) {
        throw new Error(
          result?.error
          || 'Impossibile aggiudicare il giocatore.'
        );
      }

      showMessage(
        `Giocatore aggiudicato a ${leader.name} per ${session.current_bid}.`,
        'success'
      );

      await refreshTestAuction();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        || 'Errore durante l’aggiudicazione.',
        'error'
      );

    } finally {
      testUi.award.disabled =
        false;

      testUi.award.textContent =
        oldText;
    }
  }
);


testUi.finish?.addEventListener(
  'click',
  async () => {
    const session =
      testSession();

    if (!session) return;

    testUi.finish.disabled =
      true;

    const oldText =
      testUi.finish.textContent;

    testUi.finish.textContent =
      'Chiusura...';

    try {
      const result = await callApi({
        action: 'finishTestReview',
        sessionId: session.id
      });

      if (!result?.ok) {
        throw new Error(
          result?.error
          || 'Impossibile terminare il test.'
        );
      }

      showMessage(
        'Test concluso. Le rose restano disponibili per controllo ed esportazione.',
        'success'
      );

      await refreshTestAuction();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        || 'Errore durante la chiusura del test.',
        'error'
      );

    } finally {
      testUi.finish.disabled =
        false;

      testUi.finish.textContent =
        oldText;
    }
  }
);


function printableRostersHtml() {
  const review =
    reviewData();

  if (
    !review
    || review.totalAssignments < 1
  ) {
    return '';
  }

  const leagueName =
    auctionData?.league?.name
    || 'Lega';

  const teams = review.teams
    .map(team => {
      const rows = team.players
        .map(assignment => {
          const player =
            assignment.player || {};

          const roles =
            getPlayerRoles(player)
              .join('/');

          return `
            <tr>
              <td>
                ${escapeHtml(roles || '—')}
              </td>

              <td>
                ${escapeHtml(
                  player.name || 'Giocatore'
                )}
              </td>

              <td>
                ${escapeHtml(
                  player.serie_a_team || '—'
                )}
              </td>

              <td class="price">
                ${escapeHtml(
                  assignment.purchase_price
                )}
              </td>
            </tr>
          `;
        })
        .join('');

      return `
        <section>

          <h2>
            ${escapeHtml(team.name)}
          </h2>

          <p>
            Spesi: ${team.spent}
            · Residui: ${team.remaining}
            · Giocatori: ${team.players.length}
          </p>

          <table>

            <thead>
              <tr>
                <th>Ruolo</th>
                <th>Giocatore</th>
                <th>Squadra</th>
                <th>Costo</th>
              </tr>
            </thead>

            <tbody>
              ${rows}
            </tbody>

          </table>

        </section>
      `;
    })
    .join('');

  return `<!DOCTYPE html>
<html lang="it">

<head>

<meta charset="UTF-8">

<title>
  Rose test - ${escapeHtml(leagueName)}
</title>

<style>

@page {
  size: A4 portrait;
  margin: 12mm;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  color: #111;
  font-size: 10px;
}

h1 {
  margin: 0 0 4mm;
  font-size: 18px;
}

h2 {
  margin: 0 0 1mm;
  font-size: 13px;
}

p {
  margin: 0 0 2mm;
  color: #444;
}

section {
  break-inside: avoid;
  margin-bottom: 6mm;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th,
td {
  border-bottom: 1px solid #ddd;
  padding: 1.5mm 2mm;
  text-align: left;
}

th {
  background: #f2f2f2;
  font-size: 9px;
  text-transform: uppercase;
}

th:first-child,
td:first-child {
  width: 14%;
}

th:nth-child(3),
td:nth-child(3) {
  width: 22%;
}

th:last-child,
td:last-child {
  width: 12%;
}

.price {
  text-align: right;
  font-weight: 700;
}

</style>

</head>

<body>

<h1>
  Rose test · ${escapeHtml(leagueName)}
</h1>

${teams}

<script>

window.addEventListener(
  'load',
  () => {
    setTimeout(
      () => window.print(),
      150
    );
  }
);

<\/script>

</body>

</html>`;
}


testUi.print?.addEventListener(
  'click',
  () => {
    const html =
      printableRostersHtml();

    if (!html) {
      showMessage(
        'Non ci sono rose da stampare.',
        'error'
      );

      return;
    }

    const printWindow =
      window.open(
        '',
        '_blank'
      );

    if (!printWindow) {
      showMessage(
        'Il browser ha bloccato la finestra di stampa.',
        'error'
      );

      return;
    }

    printWindow.document.open();

    printWindow.document.write(
      html
    );

    printWindow.document.close();
  }
);


function csvEscape(value) {
  const text =
    String(value ?? '');

  if (
    /[";\r\n]/.test(text)
  ) {
    return `"${text.replaceAll(
      '"',
      '""'
    )}"`;
  }

  return text;
}


function safeFileName(value) {
  return String(value || 'lega')
    .normalize('NFD')
    .replace(
      /[\u0300-\u036f]/g,
      ''
    )
    .replace(
      /[^a-zA-Z0-9_-]+/g,
      '_'
    )
    .replace(
      /^_+|_+$/g,
      ''
    )
    .toLowerCase()
    || 'lega';
}


function downloadTextFile(
  filename,
  content,
  mimeType
) {
  const blob =
    new Blob(
      [content],
      {
        type: mimeType
      }
    );

  const url =
    URL.createObjectURL(blob);

  const link =
    document.createElement('a');

  link.href =
    url;

  link.download =
    filename;

  document.body.appendChild(link);

  link.click();

  link.remove();

  setTimeout(
    () =>
      URL.revokeObjectURL(url),
    1000
  );
}


function fantacalcioCsv() {
  const review =
    reviewData();

  if (
    !review
    || review.totalAssignments < 1
  ) {
    return '';
  }

  const rows = [
    [
      'FantaSquadra',
      'Id',
      'Nome',
      'Ruolo',
      'Squadra',
      'Costo'
    ]
  ];

  for (
    const team
    of review.teams
  ) {
    for (
      const assignment
      of team.players
    ) {
      const player =
        assignment.player || {};

      rows.push([
        team.name,
        player.source_player_id || '',
        player.name || '',
        getPlayerRoles(player).join('/'),
        player.serie_a_team || '',
        assignment.purchase_price
      ]);
    }
  }

  return '\uFEFF'
    +
    rows
      .map(
        row =>
          row
            .map(csvEscape)
            .join(';')
      )
      .join('\r\n');
}


testUi.csv?.addEventListener(
  'click',
  () => {
    const csv =
      fantacalcioCsv();

    if (!csv) {
      showMessage(
        'Non ci sono rose da esportare.',
        'error'
      );

      return;
    }

    downloadTextFile(
      `rose_${safeFileName(
        auctionData?.league?.name
      )}.csv`,
      csv,
      'text/csv;charset=utf-8'
    );

    showMessage(
      'CSV rose scaricato.',
      'success'
    );
  }
);


testUi.purge?.addEventListener(
  'click',
  async () => {
    const session =
      testSession();

    if (!session) return;

    const confirmed =
      window.confirm(
        'Eliminare tutte le assegnazioni temporanee di questo test? '
        +
        'Le rose reali non verranno modificate.'
      );

    if (!confirmed) return;

    testUi.purge.disabled =
      true;

    const oldText =
      testUi.purge.textContent;

    testUi.purge.textContent =
      'Eliminazione...';

    try {
      const result = await callApi({
        action: 'purgeTest',
        sessionId: session.id
      });

      if (!result?.ok) {
        throw new Error(
          result?.error
          || 'Impossibile eliminare i dati del test.'
        );
      }

      showMessage(
        'Dati test eliminati. I giocatori del test sono nuovamente disponibili.',
        'success'
      );

      await refreshTestAuction();

    } catch (error) {
      console.error(error);

      showMessage(
        error.message
        || 'Errore durante l’eliminazione dei dati test.',
        'error'
      );

    } finally {
      testUi.purge.disabled =
        false;

      testUi.purge.textContent =
        oldText;
    }
  }
);


function renderAuctionTestAddon() {
  renderTestMode();
  renderTestAuctioneer();
  renderTestReview();
}


/* Ogni refresh della pagina Asta aggiorna anche l'add-on. */
const baseAuctionLoadLobby =
  loadLobby;


loadLobby = async function () {
  await baseAuctionLoadLobby();

  renderAuctionTestAddon();
};


/* Il primo load di league-auction.js può essere già partito. */
const initialTestRender =
  setInterval(
    () => {
      if (!auctionData) return;

      clearInterval(
        initialTestRender
      );

      renderAuctionTestAddon();
    },
    100
  );
