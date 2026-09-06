from pathlib import Path
import re

p=Path('home.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global s
    if old not in s:
        raise SystemExit(f'marker not found: {label}')
    s=s.replace(old,new,count)

# Lobby: render prepared session immediately after preparation/test.
rep("      $('prepare-auction')?.addEventListener('click', () => auctionAction({action:'prepareAuction'}, 'Asta preparata.'));\n      $('prepare-test-auction')?.addEventListener('click', () => auctionAction({action:'prepareTestAuction'}, 'Asta test preparata.'));",
    "      $('prepare-auction')?.addEventListener('click', async () => { await auctionAction({action:'prepareAuction'}, 'Asta preparata.'); await loadAuction({quiet:true}); });\n      $('prepare-test-auction')?.addEventListener('click', async () => { await auctionAction({action:'prepareTestAuction'}, 'Asta test preparata.'); await loadAuction({quiet:true}); });",
    'lobby prepare')

old_signals="""    function matchesFlag(player, flag) {
      if (flag === 'all') return true;
      if (flag === 'market') return player.market_flag === true;
      if (flag === 'new') return player.new_arrival === true;
      if (flag === 'penalties') return Number(player.penalty_probability || 0) > 0;
      if (flag === 'injury') return player.uncertain_return === true || (player.unavailable_until_round !== null && player.unavailable_until_round !== undefined && String(player.unavailable_until_round).trim() !== '');
      return true;
    }

    function auctionPlayerSignalBadges(player) {
      const signals = [
        {
          key: 'market',
          emoji: '🔄',
          label: 'Mercato',
          active: player?.market_flag === true
        },
        {
          key: 'injury',
          emoji: '🚑',
          label: 'Indisponibile',
          active:
            player?.uncertain_return === true
            || (
              player?.unavailable_until_round !== null
              && player?.unavailable_until_round !== undefined
              && String(player.unavailable_until_round).trim() !== ''
            )
        },
        {
          key: 'new',
          emoji: '🆕',
          label: 'Nuovo arrivo',
          active: player?.new_arrival === true
        },
        {
          key: 'penalties',
          emoji: '⚽',
          label: 'Rigorista',
          active: Number(player?.penalty_probability || 0) > 0
        }
      ].filter(signal => signal.active);

      return signals.length
        ? `<span class=\"auction-signal-list\">${signals.map(signal => `
            <span
              class=\"auction-signal-badge\"
              data-signal=\"${signal.key}\"
              title=\"${signal.label}\"
              aria-label=\"${signal.label}\"
            >${signal.emoji}</span>
          `).join('')}</span>`
        : '<span class=\"auction-signal-empty\">—</span>';
    }
"""
new_signals="""    function importedProbabilityPercent(value) {
      const n = Number(value);
      if (!Number.isFinite(n) || n <= 0) return 0;
      return Math.max(0, Math.min(100, n <= 1 ? n * 100 : n));
    }

    function importedProbabilitySignal(value, labels) {
      const pct = importedProbabilityPercent(value);
      if (!pct) return null;
      const level = pct >= 67 ? 'high' : pct >= 34 ? 'medium' : 'low';
      return { pct, level, label: `${labels[level]} · ${Math.round(pct)}%` };
    }

    function matchesFlag(player, flag) {
      if (flag === 'all') return true;
      if (flag === 'market') return player.market_flag === true;
      if (flag === 'new') return player.new_arrival === true;
      if (flag === 'penalties') return importedProbabilityPercent(player.penalty_probability) > 0;
      if (flag === 'free_kicks') return importedProbabilityPercent(player.free_kick_probability) > 0;
      if (flag === 'injury') return player.uncertain_return === true || (player.unavailable_until_round !== null && player.unavailable_until_round !== undefined && String(player.unavailable_until_round).trim() !== '');
      return true;
    }

    function auctionPlayerSignalBadges(player) {
      const penalty = importedProbabilitySignal(player?.penalty_probability, {
        high: 'Rigorista principale', medium: 'Possibile rigorista', low: 'Alternativa rigori'
      });
      const freeKick = importedProbabilitySignal(player?.free_kick_probability, {
        high: 'Piazzati principali', medium: 'Possibile tiratore piazzati', low: 'Alternativa piazzati'
      });
      const until = player?.unavailable_until_round;
      const injuryLabel = player?.uncertain_return === true
        ? (until !== null && until !== undefined && String(until).trim() !== '' ? `Rientro incerto · fino G${until}` : 'Rientro incerto')
        : (until !== null && until !== undefined && String(until).trim() !== '' ? `Indisponibile fino G${until}` : 'Indisponibile');
      const signals = [
        { key:'market', emoji:'🔄', label:'Situazione di mercato', active:player?.market_flag === true },
        { key:'injury', emoji:'🚑', label:injuryLabel, active:player?.uncertain_return === true || (until !== null && until !== undefined && String(until).trim() !== '') },
        { key:'new', emoji:'🆕', label:'Nuovo arrivo', active:player?.new_arrival === true },
        { key:'penalties', emoji: penalty?.level === 'high' ? '🎯' : '⚽', label:penalty?.label || '', active:Boolean(penalty) },
        { key:'free_kicks', emoji:'🥅', label:freeKick?.label || '', active:Boolean(freeKick) }
      ].filter(signal => signal.active);

      return signals.length
        ? `<span class=\"auction-signal-list\">${signals.map(signal => `<span class=\"auction-signal-badge\" data-signal=\"${signal.key}\" title=\"${esc(signal.label)}\" aria-label=\"${esc(signal.label)}\">${signal.emoji}</span>`).join('')}</span>`
        : '<span class=\"auction-signal-empty\">—</span>';
    }

    function strategicFinite(value) {
      const n = Number(value);
      return Number.isFinite(n) ? n : null;
    }

    function strategicFeature(player, key, fallback = null) {
      const v = strategicFinite(player?.strategic_features?.[key]);
      return v === null ? fallback : v;
    }

    function strategicPresencePercent(player) {
      let v = strategicFeature(player, 'forecast_presence', strategicFinite(player?.expected_titolarity));
      if (v === null) return 60;
      if (v <= 1) v *= 100;
      return Math.max(0, Math.min(100, v));
    }

    function strategicExpectedFantasyAverage(player) {
      return strategicFeature(player, 'forecast_fantasy_avg', strategicFinite(player?.expected_fantasy_avg)) ?? 0;
    }

    function strategicExpectedPrice(player) {
      const pfc = strategicFinite(player?.pfc);
      const pma = strategicFinite(player?.pma);
      if (pfc !== null && pma !== null) return Math.max(1, pfc * .65 + pma * .35);
      return Math.max(1, pfc ?? pma ?? 1);
    }

    function strategicWinningTargetAverage() {
      const rules = state.v9Rules || {};
      let target = rules.defense_rule_enabled
        ? (rules.clean_sheet_bonus_enabled ? 73.2 : 73.0)
        : (rules.clean_sheet_bonus_enabled ? 72.0 : 71.1);
      if (fantasyMode() === 'mantra') target -= .5;
      return target;
    }

    function strategicThresholdPrice(player) {
      const expectedPrice = strategicExpectedPrice(player);
      const fm = strategicExpectedFantasyAverage(player);
      const presence = strategicPresencePercent(player) / 100;
      const targetPerPlayer = strategicWinningTargetAverage() / 11;
      const trend = Math.max(-1, Math.min(1, strategicFeature(player, 'trend_age_adjusted', 0) || 0));
      const volatility = Math.max(0, Math.min(1, strategicFeature(player, 'volatility', .22) || 0));
      const slot = Math.max(1, Math.min(8, Number(player?.slot || 4)));
      const coverage = .55 + .45 * presence;
      const quality = targetPerPlayer > 0 ? (fm * coverage) / targetPerPlayer : 1;
      const trendFactor = 1 + trend * .10;
      const riskFactor = 1 - volatility * .10;
      const slotFactor = 1 + Math.max(0, 4 - slot) * .025;
      const contributionFactor = Math.max(.52, Math.min(1.72, quality * trendFactor * riskFactor * slotFactor));
      const initialCredits = Number(state.auction?.settings?.initial_credits || state.setup?.initial_credits || 500);
      return Math.max(1, Math.min(Math.round(initialCredits * .38), Math.round(expectedPrice * contributionFactor)));
    }

    function strategicValueIndex(player) {
      const threshold = strategicThresholdPrice(player);
      let denominator = strategicExpectedPrice(player);
      const session = state.auction?.auctionSession;
      if (session?.current_player_id === player?.id && Number(session?.current_bid || 0) > 0) denominator = Number(session.current_bid);
      return Math.max(1, Math.round((threshold / Math.max(1, denominator)) * 100));
    }

    function strategicIndexTitle(player) {
      return `Indice valore/prezzo: ${strategicValueIndex(player)} · soglia ${strategicThresholdPrice(player)} cr · prezzo atteso ${Math.round(strategicExpectedPrice(player))} cr · FV ${strategicExpectedFantasyAverage(player).toFixed(2)} · presenza ${Math.round(strategicPresencePercent(player))}%`;
    }
"""
rep(old_signals,new_signals,'signals')

rep('<option value="market">Mercato</option><option value="injury">Indisponibili</option><option value="new">Nuovi arrivi</option><option value="penalties">Rigoristi</option>',
    '<option value="market">Mercato</option><option value="injury">Indisponibili</option><option value="new">Nuovi arrivi</option><option value="penalties">Rigori</option><option value="free_kicks">Piazzati</option>',
    'signal filter')

old_head="""              <thead><tr>
                <th><button data-list-sort="role">Ruolo <span>↕</span></button></th>
                <th><button data-list-sort="name">Calciatore <span>↑</span></button></th>
                <th><button data-list-sort="team">Squadra <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="slot">Slot <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="pma">PMA <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="pfc">PFC <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="delta">Δ <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="fm">Exp.FM <span>↕</span></button></th>
                <th class="num-head"><button data-list-sort="tit">Exp.Tit. <span>↕</span></button></th>
              </tr></thead>"""
new_head="""              <thead><tr>
                <th class="auction-player-col-role"><button data-list-sort="role">Ruolo <span>↕</span></button></th>
                <th class="auction-player-col-name"><button data-list-sort="name">Calciatore <span>↑</span></button></th>
                <th class="auction-player-col-signals">Segn.</th>
                <th class="num-head auction-player-col-pfc"><button data-list-sort="pfc">PFC <span>↕</span></button></th>
                <th class="num-head auction-player-col-fm"><button data-list-sort="fm">FV <span>↕</span></button></th>
                <th class="num-head auction-player-col-pma"><button data-list-sort="pma">PMA <span>↕</span></button></th>
                <th class="num-head auction-player-col-supreme"><button data-list-sort="index">Indice <span>↕</span></button></th>
                <th class="auction-player-col-action">Pref.</th>
              </tr></thead>"""
rep(old_head,new_head,'list head')

rep("        tit: player.expected_titolarity\n      })[key];",
    "        tit: player.expected_titolarity,\n        index: strategicValueIndex(player)\n      })[key];",
    'sort index')

pattern=r"    function playerRow\(player, mode, extraClass = ''\) \{.*?\n    \}\n\n    function renderListTable\(\) \{"
replacement="""    function playerRow(player, mode, extraClass = '') {
      const roles = playerRoles(player, mode);
      const index = strategicValueIndex(player);
      return `
        <tr class="auction-list-compatible-row ${extraClass}" data-player-id="${esc(player.id)}">
          <td class="player-role-cell auction-player-col-role">${roles.map(role=>`<span class="rolebadge" data-role="${esc(role)}">${esc(role)}</span>`).join('')}</td>
          <td class="auction-player-col-name"><div class="player-main"><span class="auction-player-name-line"><span class="player-name">${esc(player.name)}</span>${flagEmoji(player.nationality_iso2) ? `<span>${flagEmoji(player.nationality_iso2)}</span>` : ''}</span><small class="auction-player-team-small">${esc(player.serie_a_team || '—')} · slot ${esc(player.slot ?? '—')} · tit ${Math.round(strategicPresencePercent(player))}%</small></div></td>
          <td class="auction-signal-cell auction-player-col-signals">${auctionPlayerSignalBadges(player)}</td>
          <td class="num auction-player-col-pfc"><strong>${formatAuctionPrice(player.pfc)}</strong></td>
          <td class="num auction-player-col-fm" title="Fanta media prevista">${formatNumber(strategicExpectedFantasyAverage(player))}</td>
          <td class="num auction-player-col-pma">${formatAuctionPrice(player.pma)}</td>
          <td class="num auction-player-col-supreme strategic-index-value" title="${esc(strategicIndexTitle(player))}">${index}</td>
          <td class="queue-cell auction-player-col-action"><span class="list-fav-slot"></span></td>
        </tr>
      `;
    }

    function renderListTable() {"""
s,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1: raise SystemExit(f'playerRow replace count={n}')
s=s.replace("'<tr><td colspan=\"9\" class=\"soft\" style=\"text-align:center;height:70px\">Nessun giocatore.</td></tr>'", "'<tr><td colspan=\"8\" class=\"soft\" style=\"text-align:center;height:70px\">Nessun giocatore.</td></tr>'",1)

# Show/populate auction index for all league users.
s=s.replace("      const showSupremeMetric =\n        auctionIsSuperAdmin();", "      const showSupremeMetric = true;")
s=s.replace('title="Indice riservato: formula crediti e Fanta media da definire"', 'title="Indice valore/prezzo: 100 = soglia sostenibile uguale al prezzo atteso"')
old_cell="""                  <td
                    class="num auction-player-col-supreme" data-auction-column="supreme"
                    data-supreme-metric-player="${esc(player.id)}"
                    title="Formula crediti e Fanta media da definire"
                  >
                    —
                  </td>"""
new_cell="""                  <td
                    class="num auction-player-col-supreme strategic-index-value" data-auction-column="supreme"
                    data-supreme-metric-player="${esc(player.id)}"
                    title="${esc(strategicIndexTitle(player))}"
                  >
                    ${strategicValueIndex(player)}
                  </td>"""
if old_cell not in s: raise SystemExit('auction index cell not found')
s=s.replace(old_cell,new_cell)

rep("function hearts(){const by=new Map((state.list?.players||[]).map(p=>[String(p.id),p]));document.querySelectorAll('#list-body tr[data-player-id]').forEach(r=>{const p=by.get(String(r.dataset.playerId)),h=r.querySelector('.player-main');if(!p||!h||h.querySelector('.v8heart'))return;",
    "function hearts(){const by=new Map((state.list?.players||[]).map(p=>[String(p.id),p]));document.querySelectorAll('#list-body tr[data-player-id]').forEach(r=>{const p=by.get(String(r.dataset.playerId)),h=r.querySelector('.list-fav-slot')||r.querySelector('.player-main');if(!p||!h||h.querySelector('.v8heart'))return;",
    'heart target')

style="""
  <style id="v10-index-list-style">
    #view-list .player-table{width:100%;min-width:720px;table-layout:fixed}
    #view-list .auction-player-col-role{width:64px}
    #view-list .auction-player-col-name{width:auto}
    #view-list .auction-player-col-signals{width:58px;text-align:center}
    #view-list .auction-player-col-pfc,#view-list .auction-player-col-fm,#view-list .auction-player-col-pma{width:58px;text-align:right}
    #view-list .auction-player-col-supreme{width:62px;text-align:right}
    #view-list .auction-player-col-action{width:48px;text-align:center}
    #view-list .auction-list-compatible-row td{height:32px;padding:3px 4px;overflow:hidden;text-overflow:ellipsis}
    #view-list .auction-player-name-line{display:flex;align-items:center;gap:4px;min-width:0}
    #view-list .auction-player-team-small{display:block;margin-top:1px;color:var(--soft);font-size:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    #view-list .player-main{min-width:0}
    #view-list .list-fav-slot{display:flex;justify-content:center;align-items:center}
    #view-list .v8heart{margin:0!important}
    .strategic-index-value{font-weight:950;font-variant-numeric:tabular-nums;color:#79bcff}
    .strategic-index-value[title]{cursor:help}
  </style>
"""
rep('\n</head>',style+'\n</head>','style')

p.write_text(s,encoding='utf-8')
