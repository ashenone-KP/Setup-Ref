// Top navbar: the hamburger toggles the dropdown menu on mobile.
(function () {
  var navbar = document.getElementById("navbar");
  var toggle = document.getElementById("navToggle");
  if (!navbar || !toggle) return;

  toggle.addEventListener("click", function () {
    navbar.classList.toggle("nav-open");
  });
  // Close the menu after tapping a link (mobile).
  navbar.addEventListener("click", function (e) {
    if (e.target.closest(".nav-link")) navbar.classList.remove("nav-open");
  });
})();

// Popups: open a <dialog> from a supervisor card or an [data-open-modal] button.
(function () {
  function opener(el) {
    var dlg = document.getElementById(el.getAttribute("data-modal") || el.getAttribute("data-open-modal"));
    if (!dlg || !dlg.showModal) return;
    el.addEventListener("click", function (e) { e.stopPropagation(); dlg.showModal(); });
    el.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); dlg.showModal(); }
    });
  }
  document.querySelectorAll(".staff-card").forEach(opener);
  document.querySelectorAll("[data-open-modal]").forEach(opener);

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
