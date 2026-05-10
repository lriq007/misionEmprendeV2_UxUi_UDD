/**
 * StageOverlay — overlay flotante de espera + ranking.
 * Reemplaza la página espera_etapa.html como destino de navegación.
 *
 * Uso:
 *   StageOverlay.init({ etapaNum, pollUrl, rankingUrl })
 */
const StageOverlay = (() => {
  const MEDALS = ["🥇", "🥈", "🥉"];
  let _cfg = {};

  function _csrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : "";
  }

  function _fmt(s) {
    const m = Math.floor(s / 60);
    return String(m).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  }

  function _buildDOM() {
    if (document.getElementById("sov-root")) return;
    const host = document.createElement("div");
    host.id = "sov-root";
    host.innerHTML = `
      <div class="rk-overlay" id="sov-overlay" aria-hidden="true"
           role="dialog" aria-modal="true" aria-labelledby="sov-title">
        <div class="rk-panel">

          <!-- Estado: esperando -->
          <div id="sov-waiting">
            <div class="rk-header">
              <div class="rk-stage-badge" id="sov-badge"></div>
              <h2 class="rk-title" id="sov-title">Esperando equipos…</h2>
            </div>
            <div class="sov-waiting-body">
              <div class="sov-waiting-icon">⏳</div>
              <p class="sov-waiting-text">
                Cuando todos terminen verán el ranking juntos.
              </p>
              <div class="sov-dots">
                <span></span><span></span><span></span>
              </div>
              <p class="sov-wait-timer" id="sov-wait-timer">00:00</p>
            </div>
          </div>

          <!-- Estado: ranking (oculto hasta que todos terminen) -->
          <div id="sov-ranking" hidden>
            <div class="rk-header">
              <div class="rk-stage-badge" id="sov-rank-badge"></div>
              <h2 class="rk-title">Ranking Final</h2>
            </div>
            <div class="rk-list" id="sov-list"></div>
            <div class="rk-footer">
              <p class="rk-countdown" id="sov-countdown">
                Continuando en <strong id="sov-count">12</strong> s…
              </p>
              <button class="btn btn-primary" id="sov-continue" style="min-width:200px">
                Continuar →
              </button>
            </div>
          </div>

        </div>
      </div>
    `;
    document.body.appendChild(host);
  }

  function _open() {
    const ov = document.getElementById("sov-overlay");
    if (!ov) return;
    ov.classList.add("is-open");
    ov.setAttribute("aria-hidden", "false");
  }

  function _startWaitTimer() {
    let s = 0;
    const el = document.getElementById("sov-wait-timer");
    if (!el) return;
    const iv = setInterval(() => {
      s++;
      el.textContent = _fmt(s);
      if (!document.getElementById("sov-waiting") ||
          document.getElementById("sov-waiting").hidden) {
        clearInterval(iv);
      }
    }, 1000);
  }

  async function _poll() {
    try {
      const r = await fetch(_cfg.pollUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": _csrf() },
        body: "{}",
      });
      const data = await r.json();
      if (data.closed) { _showRanking(); return; }
    } catch (_e) {}
    setTimeout(_poll, 3000);
  }

  async function _showRanking() {
    let data;
    try {
      const r = await fetch(_cfg.rankingUrl, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      data = await r.json();
    } catch (_e) {
      setTimeout(_showRanking, 4000);
      return;
    }

    document.getElementById("sov-waiting").hidden = true;
    document.getElementById("sov-ranking").hidden = false;

    const badge = document.getElementById("sov-rank-badge");
    if (badge) badge.textContent = `ETAPA ${data.etapa_num} · ${data.stage_label.toUpperCase()}`;

    const list = document.getElementById("sov-list");
    if (list) {
      list.innerHTML = "";
      (data.entries || []).forEach((entry, idx) => {
        const medal = MEDALS[idx] || null;
        let scoreDetail = "";
        if (data.etapa_num === 1 && entry.elapsed_label && entry.elapsed_label !== "--:--") {
          scoreDetail = entry.elapsed_label;
        }
        if (data.etapa_num === 1 && entry.progress_pct != null && entry.progress_pct < 100) {
          scoreDetail = `${entry.progress_pct}% completo`;
        }
        const item = document.createElement("article");
        item.className = "rk-item" + (entry.is_mine ? " is-mine" : "");
        item.innerHTML = `
          <span class="rk-pos-col${medal ? " is-medal" : ""}">${medal || "#" + entry.position}</span>
          <span class="rk-name">
            ${entry.team_name}
            ${entry.is_mine ? '<span class="rk-you-badge">TÚ ★</span>' : ""}
          </span>
          <span class="rk-score">
            <span class="rk-score-main">${entry.score} pts</span>
            ${scoreDetail ? `<span class="rk-score-detail">${scoreDetail}</span>` : ""}
          </span>
        `;
        list.appendChild(item);
      });
      setTimeout(() => {
        list.querySelector(".is-mine")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }, 400);
    }

    const NEXT_URL = data.next_url;
    const countEl = document.getElementById("sov-count");
    let remaining = 12;
    const cd = setInterval(() => {
      remaining--;
      if (countEl) countEl.textContent = remaining;
      if (remaining <= 0) { clearInterval(cd); window.location.href = NEXT_URL; }
    }, 1000);
    document.getElementById("sov-continue")?.addEventListener("click", () => {
      clearInterval(cd);
      window.location.href = NEXT_URL;
    }, { once: true });
  }

  function init(cfg) {
    _cfg = cfg;
    _buildDOM();
    const NAMES = {
      1: "Sopa de Letras",
      2: "Mapa de Empatía",
      3: "Creación con Lego",
      4: "Pitch",
    };
    const badge = document.getElementById("sov-badge");
    if (badge) {
      badge.textContent = `ETAPA ${cfg.etapaNum} · ${(NAMES[cfg.etapaNum] || "Etapa " + cfg.etapaNum).toUpperCase()}`;
    }
    _open();
    _startWaitTimer();
    _poll();
  }

  return { init };
})();
