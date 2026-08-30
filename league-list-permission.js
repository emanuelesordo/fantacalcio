/* =========================================================
   LISTONE - CORREZIONE VISIBILITÀ PERMESSI
   ========================================================= */

(function () {

  const MAX_ATTEMPTS = 100;
  const INTERVAL_MS = 100;

  let attempts = 0;


  function applyPermissions() {

    attempts += 1;


    /*
     * listData viene valorizzato da league-list.js
     * dopo la chiamata getList.
     */

    if (
      typeof listData === 'undefined'
      ||
      !listData?.permissions
    ) {

      if (
        attempts < MAX_ATTEMPTS
      ) {

        setTimeout(
          applyPermissions,
          INTERVAL_MS
        )
      }

      return
    }


    const permissions =
      listData.permissions || {}


    const isSuperAdmin =
      permissions.isSuperAdmin
      === true


    const isLeagueAdmin =
      permissions.isLeagueAdmin
      === true


    const canAccessSetup =
      permissions.canAccessSetup
      === true
      ||
      isSuperAdmin
      ||
      isLeagueAdmin


    const canManageList =
      permissions.canManageList
      === true
      ||
      isSuperAdmin
      ||
      isLeagueAdmin


    const setupTab =
      document.getElementById(
        'setup-tab'
      )


    const importSection =
      document.getElementById(
        'list-import-section'
      )


    const nationalitySection =
      document.getElementById(
        'superadmin-nationality-section'
      )


    const statsSection =
      document.getElementById(
        'superadmin-stats-section'
      )


    if (setupTab) {

      setupTab.hidden =
        !canAccessSetup
    }


    if (importSection) {

      importSection.hidden =
        !canManageList
    }


    if (nationalitySection) {

      nationalitySection.hidden =
        !isSuperAdmin
    }


    if (statsSection) {

      statsSection.hidden =
        !isSuperAdmin
    }
  }


  window.addEventListener(
    'DOMContentLoaded',
    applyPermissions
  )

})()
