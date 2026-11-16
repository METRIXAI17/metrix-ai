/* Loads with the public page. Creative room + short refusal if the API is down. */
(function () {
  function apiBase() {
    var runtime = window.METRIX_RUNTIME || {};
    var b = runtime.apiBaseUrl || "";
    if (b) return String(b).replace(/\/$/, "");
    var h = location.hostname;
    if (h === "localhost" || h === "127.0.0.1") return "http://127.0.0.1:8787";
    return "https://metrix-ai-production.up.railway.app";
  }

  function bind() {
    var form = document.getElementById("creative-room");
    if (!form || form.dataset.alloBound === "1") return;
    form.dataset.alloBound = "1";
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var textEl = document.getElementById("creative-text");
      var text = (textEl && textEl.value || "").trim();
      var err = document.getElementById("creative-error");
      var out = document.getElementById("creative-out");
      var btn = document.getElementById("creative-send");
      if (err) err.textContent = "";
      if (!text) {
        if (err) err.textContent = "Пустой шаблон.";
        return;
      }
      if (btn) btn.disabled = true;
      var ctrl = new AbortController();
      var timer = setTimeout(function () { ctrl.abort(); }, 8000);
      fetch(apiBase() + "/api/v1/pure/green", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: ctrl.signal,
        body: JSON.stringify({ text: text, ticker: "MX", owner: "слот" }),
      }).then(function (res) {
        if (!res.ok) throw new Error("down");
        return res.json();
      }).then(function (data) {
        if (out) {
          out.hidden = false;
          out.textContent = String((data && data.text) || "").trim() || "Пусто после срезки.";
        }
      }).catch(function () {
        if (err) err.textContent = "Сервер не ответил. Короткий отказ.";
        if (out) out.hidden = true;
      }).finally(function () {
        clearTimeout(timer);
        if (btn) btn.disabled = false;
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind);
  else bind();
})();
