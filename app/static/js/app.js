// Mobile sidebar drawer toggle.
(function () {
  var shell = document.getElementById("appShell");
  var toggle = document.getElementById("navToggle");
  if (!shell || !toggle) return;

  toggle.addEventListener("click", function () {
    shell.classList.toggle("nav-open");
  });

  // Close the drawer when the backdrop or a nav link is tapped.
  shell.addEventListener("click", function (e) {
    if (e.target.closest("[data-close-nav]") || e.target.closest(".nav-item")) {
      shell.classList.remove("nav-open");
    }
  });
})();
