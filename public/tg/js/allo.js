/* Isolated freelance chip. Does not open the $50 door. */
(function () {
  document.addEventListener("click", function (ev) {
    var t = ev.target && ev.target.closest && ev.target.closest("[data-go='freelance']");
    if (!t) return;
    ev.preventDefault();
    ev.stopImmediatePropagation();
    var view = document.getElementById("view");
    if (!view) return;
    view.innerHTML =
      '<section class="room">' +
      '<div class="eyebrow room-label">Не вкладка</div>' +
      "<h1>Фриланс · <em>изолирован</em></h1>" +
      "<p class='lead room-desc'>Своя оплата. Не открывает Allo $50, Access и Флагман. Сигналов нет.</p>" +
      "</section>";
    try { history.replaceState(null, "", "#freelance"); } catch (e) {}
    window.scrollTo(0, 0);
  }, true);
})();
