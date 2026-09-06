/* FANTACALCIO LIVE · V6Y + successive consolidated runtime */
'use strict';

(() => {
  if (window.__FANTA_V6Y_V7__) return;
  window.__FANTA_V6Y_V7__ = true;

  ENDPOINTS.v6y = `${SUPABASE_URL}/functions/v1/v6y-api`;

  Object.assign(state, {
    v7Preferences: state.v7Preferences || new Map(),
    v7Stats: state.v7Stats || new Map(),
    v7StrategyLeagueId: state.v7StrategyLeagueId || '',
    v7SuggestedDismissKey: state.v7SuggestedDismissKey || '',
    v7SuggestedDismissed: state.v7SuggestedDismissed || [],
    v7LastEventId: Number(state.v7LastEventId || 0),
    v7CatalogAsOf: state.v7CatalogAsOf || null,
    v7HotBusy: false
  });

  const norm = value => String(value || '')
    .trim().toLocaleLowerCase('it-IT').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, ' ').trim();

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

  async function v7Api(payload, options = {}) {
    return api(ENDPOINTS.v6y, payload, { quiet: true, ...options });
  }

  function v7Preference(player) {
    if (!player) return null;
    return state.v7Preferences.get(String(player.source_player_id || player.id || '')) || null;
  }

  function v7Stat(player) {
    if (!player) return null;
    return state.v7Stats.get(`${norm(player.name)}|${norm(player.serie_a_team)}`)
      || state.v7Stats.get(norm(player.name)) || null;
  }

  async function v7HydrateStrategy(force = false) {
    const leagueId = state.selectedLeague?.id || '';
    if (!leagueId || (!force && state.v7StrategyLeagueId === leagueId)) return;
    state.v7StrategyLeagueId = leagueId;

    try {
      const [prefs, stats] = await Promise.all([
        v7Api({ action: 'getPreferences' }),
        v7Api({ action: 'getStatsSnapshot' })
      ]);

      state.v7Preferences = new Map(
        (prefs?.preferences || []).map(item => [String(item.source_player_id), item])
      );

      const statMap = new Map();
      (stats?.rows || []).forEach(row => {
        const name = norm(row.playerNameNormalized);
        const team = norm(row.teamNormalized);
        if (name) {
          statMap.set(name, row);
          if (team) statMap.set(`${name}|${team}`, row);
        }
      });
      state.v7Stats = statMap;
    } catch (error) {
      console.warn('V6Y strategy hydrate:', error);
    }
  }

  function v7SuggestionContextKey() {
    return [auctionSession()?.id || '', auctionMyTeamId() || '', state.auction?.rolePhase?.key || 'free'].join('|');
  }

  function v7Dismissed() {
    const key = v7SuggestionContextKey();
    if (state.v7SuggestedDismissKey !== key) {
      state.v7SuggestedDismissKey = key;
      state.v7SuggestedDismissed = [];
    }
    return state.v7SuggestedDismissed;
  }

  function v7MantraFit(player) {
    if ((state.auction?.settings?.fantasy_mode || 'classic') === 'classic') return 0;
    const roles = playerRoles(player || {}, state.auction?.settings?.fantasy_mode);
    const flexibility = new Set(roles).size;
    return flexibility >= 3 ? 12 : flexibility === 2 ? 7 : flexibility === 1 ? 2 : 0;
  }

  function v7StrategicPrices(player, baseScore = 0) {
    const info = auctionMyTeamDashboardData();
    const pref = v7Preference(player);
    const pfc = Math.max(0, Number(player?.pfc || 0));
    const pma = Math.max(0, Number(player?.pma || 0));
    const quotation = Math.max(0, Number(player?.quotation || 0));
    const anchor = pfc || pma || quotation || 1;

    const historicalFactor = pfc > 0 && pma > 0 ? clamp(pma / pfc, .84, 1.16) : 1;
    const sameRole = new Set(playerRoles(player || {}, state.auction?.settings?.fantasy_mode));
    const liveRatios = (state.auction?.recentAwards || [])
      .filter(award => {
        const ap = award?.player || {};
        const price = Number(award?.price || award?.amount || 0);
        const ref = Number(ap?.pfc || 0);
        return price > 0 && ref > 0 && playerRoles(ap, state.auction?.settings?.fantasy_mode).some(r => sameRole.has(r));
      })
      .slice(0, 8)
      .map(award => clamp(Number(award.price || award.amount) / Number(award.player?.pfc || 1), .65, 1.55));
    const liveFactor = liveRatios.length
      ? clamp(liveRatios.reduce((a, b) => a + b, 0) / liveRatios.length, .82, 1.22)
      : 1;

    const corrected = anchor * (.78 + historicalFactor * .12 + liveFactor * .10);
    const scoreBoost = baseScore >= 90 ? .12 : baseScore >= 70 ? .08 : baseScore >= 45 ? .04 : 0;
    let suggested = Math.max(1, Math.round(corrected * (1 + scoreBoost)));
    let ceiling = Math.max(suggested, Math.round(corrected * (1.12 + scoreBoost)));

    if (pref?.expected_spend != null) suggested = Math.max(1, Math.round((suggested * 2 + Number(pref.expected_spend)) / 3));
    if (pref?.max_price != null) ceiling = Math.min(ceiling, Math.max(1, Number(pref.max_price)));

    const budget = Number(info?.maxBid);
    if (Number.isFinite(budget)) {
      ceiling = Math.min(ceiling, Math.max(0, budget));
      suggested = Math.min(suggested, ceiling);
    }

    return { suggested, ceiling, pfc, pma, liveFactor };
  }

  const originalSuggestedScore = auctionSuggestedCallScore;
  auctionSuggestedCallScore = function(player) {
    const item = originalSuggestedScore(player);
    if (!item) return null;
    const pref = v7Preference(player);
    const stat = v7Stat(player);
    const features = stat?.features || {};
    const preferenceBoost = pref?.strategy === 'top' ? 28 : pref?.is_favorite ? 14 : pref?.strategy === 'avoid' ? -90 : 0;
    const priorityBoost = Math.max(0, Number(pref?.priority || 0)) * 4;
    const trendBoost = Math.round(Number(features.trend_age_adjusted || 0) * 18);
    const confidenceBoost = Math.round(Number(features.trend_confidence || 0) * 4);
    const mantraBoost = v7MantraFit(player);
    item.score += preferenceBoost + priorityBoost + trendBoost + confidenceBoost + mantraBoost;
    item.preference = pref;
    item.features = features;
    item.mantraFit = mantraBoost;
    item.prices = v7StrategicPrices(player, item.score);
    return item;
  };

  const originalSuggestedCalls = auctionSuggestedCalls;
  auctionSuggestedCalls = function(limit = 4) {
    const dismissed = new Set(v7Dismissed().map(String));
    const all = (state.auction?.callCandidates || [])
      .map(auctionSuggestedCallScore)
      .filter(Boolean)
      .filter(item => !dismissed.has(String(item.player?.id || '')))
      .sort((a, b) => b.score - a.score || String(a.player?.name || '').localeCompare(String(b.player?.name || ''), 'it'));
    return all.slice(0, Math.max(1, Number(limit || 4)));
  };

  function v7SuggestionModal(playerId) {
    const player = (state.auction?.callCandidates || []).find(p => String(p.id) === String(playerId));
    const item = player ? auctionSuggestedCallScore(player) : null;
    if (!item) return;
    const roles = playerRoles(player, state.auction?.settings?.fantasy_mode);
    const score = clamp(Math.round(Number(item.score || 0)), 0, 100);
    const pref = item.preference || {};
    const prices = item.prices || v7StrategicPrices(player, item.score);

    let dialog = document.getElementById('auction-v7-strategy-dialog');
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.id = 'auction-v7-strategy-dialog';
      dialog.className = 'auction-v7-strategy-dialog';
      document.body.appendChild(dialog);
    }

    dialog.innerHTML = `
      <form class="auction-v7-modal" method="dialog">
        <header><div><small>CONSULENTE STRATEGICO</small><h3>${esc(player.name || 'Giocatore')}</h3><p>${roles.map(r => esc(r)).join('/')} · ${esc(player.serie_a_team || '—')}</p></div><button value="cancel" class="secondary">×</button></header>
        <div class="auction-v7-kpis">
          <span><small>SCORE</small><b>${score}</b></span>
          <span><small>SUGGERITO</small><b>${prices.suggested}</b></span>
          <span><small>MAX</small><b>${prices.ceiling}</b></span>
          <span><small>PFC</small><b>${prices.pfc || '—'}</b></span>
          <span><small>PMA</small><b>${prices.pma || '—'}</b></span>
          <span><small>Q</small><b>${formatNumber(player.quotation)}</b></span>
          <span><small>SLOT</small><b>${esc(player.slot ?? '—')}</b></span>
          <span><small>TREND</small><b>${esc(item.features?.trend_direction || '—')}</b></span>
        </div>
        <div class="auction-v7-reason"><b>Perché:</b> ${esc(item.reason || '')}${item.secondary ? ` · ${esc(item.secondary)}` : ''}${item.mantraFit ? ` · flessibilità Mantra +${item.mantraFit}` : ''}</div>
        <div class="auction-v7-pref-grid">
          <label>Strategia<select id="v7-pref-strategy"><option value="none">Normale</option><option value="favorite">Preferito</option><option value="top">Top target</option><option value="avoid">Da evitare</option></select></label>
          <label>Priorità<input id="v7-pref-priority" type="number" min="0" max="5" value="${Number(pref.priority || 0)}"></label>
          <label>Spesa attesa<input id="v7-pref-spend" type="number" min="0" value="${pref.expected_spend ?? ''}"></label>
          <label>Max personale<input id="v7-pref-max" type="number" min="0" value="${pref.max_price ?? ''}"></label>
        </div>
        <label>Nota privata<textarea id="v7-pref-note" rows="2" maxlength="500">${esc(pref.note || '')}</textarea></label>
        <div class="auction-v7-actions"><button type="button" class="secondary" id="v7-pref-favorite">${pref.is_favorite ? '★ PREFERITO' : '☆ PREFERITO'}</button><button type="button" id="v7-pref-save">SALVA STRATEGIA</button></div>
      </form>`;

    dialog.querySelector('#v7-pref-strategy').value = pref.strategy || 'none';
    dialog.querySelector('#v7-pref-favorite')?.addEventListener('click', async () => {
      await v7Api({ action: 'toggleFavorite', sourcePlayerId: player.source_player_id || player.id });
      await v7HydrateStrategy(true); dialog.close(); renderAuctionLive();
    });
    dialog.querySelector('#v7-pref-save')?.addEventListener('click', async () => {
      await v7Api({
        action: 'savePreference', sourcePlayerId: player.source_player_id || player.id,
        strategy: dialog.querySelector('#v7-pref-strategy').value,
        priority: Number(dialog.querySelector('#v7-pref-priority').value || 0),
        expectedSpend: dialog.querySelector('#v7-pref-spend').value,
        maxPrice: dialog.querySelector('#v7-pref-max').value,
        note: dialog.querySelector('#v7-pref-note').value,
        isFavorite: pref.is_favorite === true
      });
      await v7HydrateStrategy(true); dialog.close(); renderAuctionLive();
    });
    dialog.showModal();
  }

  renderAuctionSuggestedCalls = function() {
    const full = Boolean(document.fullscreenElement);
    const suggestions = auctionSuggestedCalls(full ? 8 : 4);
    if (!suggestions.length) return '';
    const canQueue = auctionHasPresidentRole();
    const actionLabel = auctionOwnCallTurn() && auctionQueueRows().length === 0 ? 'CHIAMA' : 'CODA';
    return `<section class="auction-suggested-calls ${full ? 'is-full-immersion' : ''}" aria-label="Chiamate suggerite"><div class="auction-suggested-head"><div><strong>Chiamate suggerite</strong><small>rosa · valore · trend · mercato live</small></div><span>LIVE</span></div><div class="auction-suggested-list">${suggestions.map((item, index) => {
      const player = item.player || {};
      const roles = playerRoles(player, state.auction?.settings?.fantasy_mode);
      const prices = item.prices || v7StrategicPrices(player, item.score);
      return `<div class="auction-suggested-row ${index === 0 ? 'is-must-have' : ''}" data-v7-detail="${esc(player.id)}" tabindex="0">
        <span class="auction-suggested-roles">${roles.map(role => `<span class="rolebadge" data-role="${esc(role)}">${esc(role)}</span>`).join('')}</span>
        <div class="auction-suggested-copy"><div class="auction-v7-name"><strong>${esc(player.name || 'Giocatore')}</strong>${index === 0 ? '<em>DA NON PERDERE</em>' : ''}${item.preference?.is_favorite ? '<i>★</i>' : ''}</div><small>${esc(player.serie_a_team || '—')} · score ${clamp(Math.round(item.score),0,100)}</small></div>
        <span class="auction-v7-prices"><b>SUGG ${prices.suggested}</b><small>MAX ${prices.ceiling}</small></span>
        <span class="auction-v7-suggest-actions"><button type="button" class="auction-v7-dismiss" data-v7-dismiss="${esc(player.id)}" title="Scarta suggerimento">×</button>${canQueue ? `<button type="button" class="auction-suggested-action" data-suggest-call="${esc(player.id)}">${actionLabel}</button>` : '<span class="auction-suggested-action-placeholder">VICE</span>'}</span>
      </div>`;
    }).join('')}</div></section>`;
  };

  function v7BindSuggestions(root = document) {
    root.querySelectorAll('[data-v7-dismiss]').forEach(button => {
      if (button.dataset.v7Bound) return; button.dataset.v7Bound = '1';
      button.addEventListener('click', event => {
        event.preventDefault(); event.stopPropagation();
        const id = String(button.dataset.v7Dismiss || '');
        if (id && !v7Dismissed().includes(id)) v7Dismissed().push(id);
        const holder = document.querySelector('.auction-free-suggestions');
        if (holder) { holder.innerHTML = renderAuctionSuggestedCalls(); attachAuctionCallQueueEvents(); }
      });
    });
    root.querySelectorAll('[data-v7-detail]').forEach(row => {
      if (row.dataset.v7Bound) return; row.dataset.v7Bound = '1';
      const open = event => {
        if (event.target.closest('button')) return;
        if (event.type === 'keydown' && !['Enter',' '].includes(event.key)) return;
        event.preventDefault(); v7SuggestionModal(row.dataset.v7Detail);
      };
      row.addEventListener('click', open); row.addEventListener('keydown', open);
    });
  }

  const originalAttachQueue = attachAuctionCallQueueEvents;
  attachAuctionCallQueueEvents = function(...args) {
    const value = originalAttachQueue(...args); v7BindSuggestions(document); return value;
  };

  function v7PatchLive() {
    const p = state.auction?.currentPlayer;
    if (p) {
      const item = auctionSuggestedCallScore(p);
      const prices = item?.prices || v7StrategicPrices(p, item?.score || 0);
      document.querySelectorAll('.auction-command-player small').forEach(meta => {
        if (!meta.querySelector('.auction-v7-live-price')) meta.insertAdjacentHTML('beforeend', `<span class="auction-v7-live-price"> · SUGG ${prices.suggested} · MAX ${prices.ceiling}${item ? ` · SCORE ${clamp(Math.round(item.score),0,100)}` : ''}</span>`);
      });
    }

    const info = auctionMyTeamDashboardData();
    const head = document.querySelector('.auction-team-column-roster-only .auction-team-roster-head');
    if (info && head && !head.querySelector('.auction-v7-roster-metrics')) {
      const max = Math.max(1, Number(info.rosterMax || info.rosterLimit || info.rosterMin || 1));
      const comp = Math.round((info.assignments.length / max) * 100);
      const fv = Math.round(info.assignments.reduce((sum, a) => sum + Number(a.player?.pfc || a.player?.quotation || 0), 0));
      const tit = info.assignments.map(a => Number(a.player?.expected_titolarity)).filter(Number.isFinite);
      const sol = tit.length ? Math.round(tit.reduce((a,b)=>a+b,0) / tit.length) : null;
      head.querySelector('.auction-roster-head-actions')?.insertAdjacentHTML('afterbegin', `<span class="auction-v7-roster-metrics" title="Completezza rosa · Fantavalore PFC · Solidità media titolarità">COMP ${comp}% <i>|</i> FV ${fv || '—'} <i>|</i> SOL ${sol ?? '—'}${sol !== null ? '%' : ''}</span>`);
    }
    v7BindSuggestions(document);
  }

  function v7CenterHtml() {
    const prefs = [...state.v7Preferences.values()];
    const fav = prefs.filter(p => p.is_favorite).length;
    const top = prefs.filter(p => p.strategy === 'top').length;
    const avoid = prefs.filter(p => p.strategy === 'avoid').length;
    const planned = prefs.reduce((sum,p) => sum + Number(p.expected_spend || 0), 0);
    return `<section class="panel auction-v7-center"><div class="between"><div><strong>Centro Strategico</strong><div class="small soft">Preferenze private · statistiche · piano d’asta</div></div><span class="badge primary">V6Y+</span></div><div class="auction-v7-center-grid"><span><small>Preferiti</small><b>${fav}</b></span><span><small>Top target</small><b>${top}</b></span><span><small>Da evitare</small><b>${avoid}</b></span><span><small>Budget pianificato</small><b>${planned}</b></span></div></section>`;
  }

  function v7PatchCenter() {
    const root = document.getElementById('auction-root');
    if (!root || root.querySelector('.auction-v7-center')) return;
    const lobby = root.querySelector('.auction-lobby');
    if (lobby) lobby.insertAdjacentHTML('afterbegin', v7CenterHtml());
    else if (auctionSession()?.status === 'prepared') root.insertAdjacentHTML('afterbegin', v7CenterHtml());
  }

  const originalRenderLive = renderAuctionLive;
  renderAuctionLive = function(...args) { const value = originalRenderLive(...args); v7PatchLive(); return value; };
  const originalRenderLobby = renderAuctionLobby;
  renderAuctionLobby = function(...args) { const value = originalRenderLobby(...args); v7PatchCenter(); return value; };
  const originalRenderPrepared = renderAuctionPrepared;
  renderAuctionPrepared = function(...args) { const value = originalRenderPrepared(...args); v7PatchCenter(); return value; };

  function v7OpenDb() {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open('fantacalcio_v6y', 1);
      req.onupgradeneeded = () => { if (!req.result.objectStoreNames.contains('cache')) req.result.createObjectStore('cache'); };
      req.onsuccess = () => resolve(req.result); req.onerror = () => reject(req.error);
    });
  }
  async function v7CachePut(key, value) {
    try { const db = await v7OpenDb(); const tx = db.transaction('cache','readwrite'); tx.objectStore('cache').put(value,key); } catch {}
  }
  async function v7CacheGet(key) {
    try { const db = await v7OpenDb(); return await new Promise((resolve,reject)=>{ const r=db.transaction('cache').objectStore('cache').get(key); r.onsuccess=()=>resolve(r.result); r.onerror=()=>reject(r.error); }); } catch { return null; }
  }

  async function v7SyncCatalog() {
    const leagueId = state.selectedLeague?.id; if (!leagueId || !state.auction) return;
    const key = `catalog:${leagueId}`;
    const cached = await v7CacheGet(key);
    if ((!state.auction.callCandidates || !state.auction.callCandidates.length) && cached?.players?.length) state.auction.callCandidates = cached.players;
    const response = await v7Api({ action: cached?.asOf ? 'getAuctionCatalogDelta' : 'getAuctionCatalog', since: cached?.asOf || undefined });
    if (!response) return;
    const map = new Map((cached?.players || state.auction.callCandidates || []).map(p => [String(p.id), p]));
    (response.players || []).forEach(p => map.set(String(p.id), p));
    (response.removedPlayerIds || []).forEach(id => map.delete(String(id)));
    const players = [...map.values()];
    state.v7CatalogAsOf = response.asOf || cached?.asOf || null;
    await v7CachePut(key, { players, asOf: state.v7CatalogAsOf });
  }

  const originalLoadAuction = loadAuction;
  loadAuction = async function(...args) {
    const result = await originalLoadAuction(...args);
    await Promise.allSettled([v7HydrateStrategy(), v7SyncCatalog()]);
    if (state.auction?.auctionSession?.status === 'live') v7PatchLive(); else v7PatchCenter();
    return result;
  };

  async function v7HotReconcile() {
    if (state.v7HotBusy || !state.auction?.auctionSession?.id) return;
    state.v7HotBusy = true;
    try {
      const sessionId = state.auction.auctionSession.id;
      const [hot, events] = await Promise.all([
        v7Api({ action: 'getHotState', sessionId }),
        v7Api({ action: 'getAuctionEventsSince', sessionId, afterId: state.v7LastEventId || 0, limit: 100 })
      ]);
      const evs = events?.events || [];
      state.v7LastEventId = Number(events?.lastEventId || hot?.lastEventId || state.v7LastEventId || 0);
      const structural = evs.some(e => /AWARD|ASSIGN|ROSTER|QUEUE|ROLE_PHASE|NOMINATION|CALL|UNDO|CREDIT|PASS|VICE/i.test(String(e.event_type || '')));
      if (structural) {
        await originalLoadAuction({ quiet: true, onlyIfChanged: true });
        await v7SyncCatalog();
        return;
      }
      if (hot?.state) {
        const beforePlayer = state.auction.auctionSession?.current_player_id;
        state.auction.auctionSession = { ...state.auction.auctionSession, ...hot.state };
        if (hot.currentPlayer) state.auction.currentPlayer = hot.currentPlayer;
        const teams = state.auction.teams || [];
        state.auction.currentBidderTeam = teams.find(t => t.id === hot.state.current_bidder_team_id) || state.auction.currentBidderTeam;
        state.auction.currentNominationTeam = teams.find(t => t.id === hot.state.current_nomination_team_id) || state.auction.currentNominationTeam;
        state.auction.recentBids = (hot.recentBids || []).map(b => ({ ...b, team: teams.find(t => t.id === b.team_id) || null }));
        if (beforePlayer !== hot.state.current_player_id) renderAuctionLive(); else patchAuctionLiveDynamic();
        renderTv(); v7PatchLive();
      }
    } catch (error) {
      console.warn('V6Y hot reconcile fallback:', error);
      await originalLoadAuction({ quiet: true, onlyIfChanged: true });
    } finally { state.v7HotBusy = false; }
  }

  const originalSchedule = scheduleAuctionReconcile;
  scheduleAuctionReconcile = function(delay = 80) {
    if (!state.session?.token || !['auction','tv'].includes(state.view)) return;
    if (auctionReconcileTimer) clearTimeout(auctionReconcileTimer);
    auctionReconcileTimer = setTimeout(() => { auctionReconcileTimer = null; void v7HotReconcile(); }, Math.max(0, Number(delay || 0)));
  };

  const style = document.createElement('style');
  style.textContent = `
    body.modern-glass #view-auction .auction-suggested-row{cursor:pointer}
    body.modern-glass #view-auction .auction-suggested-row.is-must-have{border-color:rgba(220,180,70,.78)!important;background:linear-gradient(145deg,rgba(220,180,70,.12),rgba(255,255,255,.025))!important;box-shadow:inset 0 0 0 1px rgba(220,180,70,.15)!important}
    .auction-v7-name{display:flex;align-items:center;gap:3px;min-width:0}.auction-v7-name strong{min-width:0;flex:1}.auction-v7-name em{font-style:normal;font-size:5px;font-weight:1000;color:#f0d276;border:1px solid rgba(220,180,70,.48);border-radius:99px;padding:1px 3px;white-space:nowrap}.auction-v7-name i{color:#f0d276;font-style:normal}
    .auction-v7-prices{display:grid;justify-items:end;min-width:55px;font-variant-numeric:tabular-nums}.auction-v7-prices b{font-size:6px;color:#79bcff}.auction-v7-prices small{font-size:5.5px;color:#68e0aa}.auction-v7-suggest-actions{display:flex;align-items:center;gap:2px}.auction-v7-dismiss{width:18px!important;min-width:18px!important;height:18px!important;min-height:18px!important;padding:0!important;border-radius:99px!important;background:rgba(255,255,255,.03)!important;border:1px solid rgba(255,255,255,.08)!important;color:#8199ad!important;font-size:10px!important}
    .auction-v7-live-price{color:#79bcff;font-weight:900}.auction-v7-roster-metrics{color:#b8cde0;font-size:7px;font-weight:950;white-space:nowrap}.auction-v7-roster-metrics i{color:#52708b;font-style:normal;margin:0 2px}
    .auction-v7-center{margin-bottom:6px}.auction-v7-center-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;margin-top:6px}.auction-v7-center-grid span{padding:5px;border:1px solid var(--line);border-radius:6px;background:var(--panel2);display:flex;align-items:center;justify-content:space-between}.auction-v7-center-grid small{color:var(--muted);font-size:7px}.auction-v7-center-grid b{font-size:12px}
    dialog.auction-v7-strategy-dialog{width:min(620px,calc(100vw - 20px));padding:0;border:1px solid rgba(109,167,255,.35);border-radius:14px;background:#091d33;color:#f5f8ff;box-shadow:0 24px 70px rgba(0,0,0,.58)}dialog.auction-v7-strategy-dialog::backdrop{background:rgba(2,8,16,.72);backdrop-filter:blur(6px)}.auction-v7-modal{display:grid;gap:9px;padding:12px}.auction-v7-modal header{display:flex;justify-content:space-between;gap:8px}.auction-v7-modal h3{margin:2px 0;font-size:20px}.auction-v7-modal p{margin:0;color:#9bb7da;font-size:8px}.auction-v7-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px}.auction-v7-kpis span{padding:6px;border:1px solid #28598e;border-radius:7px;background:#0d2b4a}.auction-v7-kpis small{display:block;color:#7896b1;font-size:6px}.auction-v7-kpis b{display:block;font-size:13px;margin-top:2px}.auction-v7-reason{padding:7px;border:1px solid rgba(109,167,255,.18);border-radius:7px;background:rgba(109,167,255,.05);font-size:8px}.auction-v7-pref-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}.auction-v7-actions{display:flex;justify-content:flex-end;gap:5px}@media(max-width:620px){.auction-v7-kpis,.auction-v7-center-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
  `;
  document.head.appendChild(style);

  void v7HydrateStrategy(true).then(() => { if (state.view === 'auction') { v7PatchCenter(); v7PatchLive(); } });
})();
