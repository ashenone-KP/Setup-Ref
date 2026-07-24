// Sidebar behaviour:
//  - Desktop (> 860px): the toggle collapses the sidebar to an icon-only rail,
//    and the choice is remembered in localStorage.
//  - Mobile (<= 860px): the toggle opens/closes the off-canvas drawer.
(function () {
  var shell = document.getElementById("appShell");
  var toggle = document.getElementById("navToggle");
  if (!shell) return;

  var DESKTOP = 861;
  var STORE_KEY = "sm.sidebarCollapsed";

  // Restore the remembered desktop state.
  try {
    if (localStorage.getItem(STORE_KEY) === "1" && window.innerWidth >= DESKTOP) {
      shell.classList.add("sidebar-collapsed");
    }
  } catch (e) { /* ignore storage errors */ }

  if (toggle) {
    toggle.addEventListener("click", function () {
      if (window.innerWidth >= DESKTOP) {
        var collapsed = shell.classList.toggle("sidebar-collapsed");
        try { localStorage.setItem(STORE_KEY, collapsed ? "1" : "0"); } catch (e) {}
      } else {
        shell.classList.toggle("nav-open");
      }
    });
  }

  // On mobile, close the drawer when the backdrop or a nav link is tapped.
  shell.addEventListener("click", function (e) {
    if (e.target.closest("[data-close-nav]") || e.target.closest(".nav-item")) {
      shell.classList.remove("nav-open");
    }
  });
})();

// Supervisor popups: clicking a card opens its <dialog>.
(function () {
  document.querySelectorAll(".staff-card").forEach(function (card) {
    var dlg = document.getElementById(card.getAttribute("data-modal"));
    if (!dlg || !dlg.showModal) return;
    card.addEventListener("click", function () { dlg.showModal(); });
    card.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dlg.showModal(); }
    });
  });

  document.querySelectorAll("dialog.modal").forEach(function (dlg) {
    dlg.querySelectorAll("[data-close]").forEach(function (btn) {
      btn.addEventListener("click", function () { dlg.close(); });
    });
    // Click on the backdrop (the dialog element itself) closes it.
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg) dlg.close();
    });
  });
})();
