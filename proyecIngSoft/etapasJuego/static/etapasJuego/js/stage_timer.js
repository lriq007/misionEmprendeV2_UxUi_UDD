/**
 * stage_timer.js — Generic per-stage countdown timer.
 * Reads config from data attributes on [data-stage-timer]:
 *   data-duration-seconds   Total seconds for the stage
 *   data-timeup-url         Endpoint to call when time runs out
 *   data-csrf-token         CSRF token for the POST request
 *
 * Also reads [data-global-timer] for the global session elapsed counter.
 *   data-elapsed-seconds    Seconds already elapsed in the session
 */
(() => {
  // ── Per-stage countdown ──────────────────────────────────────────────────
  const timerEl = document.querySelector("[data-stage-timer]");
  if (timerEl) {
    const duration   = parseInt(timerEl.dataset.durationSeconds, 10) || 600;
    const timeupUrl  = timerEl.dataset.timeupUrl || "";
    const csrf       = timerEl.dataset.csrfToken || getCsrf();

    let remaining = duration;

    const display = timerEl.querySelector("[data-stage-timer-display]") || timerEl;
    display.textContent = fmt(remaining);

    const intervalId = setInterval(async () => {
      remaining = Math.max(remaining - 1, 0);
      display.textContent = fmt(remaining);

      if (remaining === 0) {
        clearInterval(intervalId);
        if (timeupUrl) {
          try {
            const r = await fetch(timeupUrl, {
              method: "POST",
              headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
              body: "{}",
            });
            const data = await r.json();
            if (data.redirect_url) {
              window.location.href = data.redirect_url;
              return;
            }
          } catch (_) {}
        }
        // Fallback: show a message
        display.textContent = "¡Tiempo!";
      }
    }, 1000);
  }

  // ── Global session elapsed counter (counts up) ───────────────────────────
  const globalEl = document.querySelector("[data-global-timer]");
  if (globalEl) {
    let elapsed = parseInt(globalEl.dataset.elapsedSeconds, 10) || 0;
    const gDisplay = globalEl.querySelector("[data-global-timer-display]") || globalEl;
    gDisplay.textContent = fmt(elapsed);
    setInterval(() => {
      elapsed++;
      gDisplay.textContent = fmt(elapsed);
    }, 1000);
  }

  // ── Helpers ───────────────────────────────────────────────────────────────
  function fmt(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : "";
  }
})();
