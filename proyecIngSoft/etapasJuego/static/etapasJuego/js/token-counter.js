(() => {
  const STORAGE_TOTAL = "token_counter_total_v1";
  const STORAGE_EVENTS = "token_counter_events_v1";

  const qs = (s, p = document) => p.querySelector(s);

  const loadTotal = () => {
    const val = Number(localStorage.getItem(STORAGE_TOTAL));
    return Number.isFinite(val) ? val : 0;
  };
  const saveTotal = (val) => localStorage.setItem(STORAGE_TOTAL, String(val));

  const loadEvents = () => {
    try {
      const raw = localStorage.getItem(STORAGE_EVENTS);
      if (!raw) return new Set();
      return new Set(JSON.parse(raw));
    } catch (e) {
      return new Set();
    }
  };
  const saveEvents = (events) => {
    localStorage.setItem(STORAGE_EVENTS, JSON.stringify([...events]));
  };

  let eventsSet = loadEvents();
  let total = loadTotal();
  let elCounter = null;
  let elValue = null;

  function ensureStyles() {
    if (document.getElementById("token-counter-styles")) return;
    const style = document.createElement("style");
    style.id = "token-counter-styles";
    style.textContent = `
      #token-counter.token-counter {
        top: 108px;
        right: 18px;
        gap: 17px;
        padding: 20px 32px 20px 26px;
        border-radius: 23px;
        background: linear-gradient(135deg, rgba(255,209,71,0.18) 0%, #1D232A 70%);
        box-shadow:
          0 8px 32px rgba(0,0,0,0.45),
          0 0 0 1px rgba(255,209,71,0.45),
          0 0 28px rgba(255,209,71,0.2);
        border: 1px solid rgba(255,209,71,0.45);
      }
      #token-counter .token-counter-bolt {
        width: 2.9rem;
        height: 2.9rem;
        fill: #FFD147;
        flex-shrink: 0;
        filter: drop-shadow(0 0 8px rgba(255,209,71,0.9));
      }
      #token-counter .token-counter-body {
        display: flex;
        flex-direction: column;
        gap: 1px;
      }
      #token-counter .token-counter-label {
        font-size: 1rem;
        letter-spacing: 0.12em;
        color: #A7C3D6;
        line-height: 1;
      }
      #token-counter .token-counter-value {
        font-size: 2.9rem;
        line-height: 1;
        font-weight: 900;
        color: #FFD147;
        text-shadow: 0 0 18px rgba(255,209,71,0.75);
      }
    `;
    document.head.appendChild(style);
  }

  function ensureCounter() {
    if (elCounter) return;
    ensureStyles();
    elCounter = document.createElement("div");
    elCounter.id = "token-counter";
    elCounter.className = "token-counter";
    elCounter.innerHTML = `
      <svg class="token-counter-bolt" viewBox="0 0 24 24" aria-hidden="true">
        <path d="M13 2 L4 14 H11 L10 22 L20 9 H13 Z"/>
      </svg>
      <span class="token-counter-body">
        <span class="token-counter-label">Puntos</span>
        <span class="token-counter-value" id="token-counter-value">0</span>
      </span>
    `;
    document.body.appendChild(elCounter);
    elValue = qs("#token-counter-value");
  }

  function render() {
    if (!elValue) return;
    elValue.textContent = total;
  }

  function flash() {
    if (!elCounter) return;
    elCounter.classList.add("flash");
    clearTimeout(elCounter._t);
    elCounter._t = setTimeout(() => elCounter.classList.remove("flash"), 900);
  }

  function add(amount = 0) {
    const delta = Number(amount) || 0;
    if (!delta) return total;
    total = Math.max(0, Math.round(total + delta));
    saveTotal(total);
    render();
    flash();
    return total;
  }

  function addOnce(key, amount = 0) {
    if (!key) return total;
    if (eventsSet.has(key)) return total;
    eventsSet.add(key);
    saveEvents(eventsSet);
    return add(amount);
  }

  function set(value = 0) {
    total = Math.max(0, Math.round(Number(value) || 0));
    saveTotal(total);
    render();
    return total;
  }

  document.addEventListener("DOMContentLoaded", () => {
    ensureCounter();
    total = loadTotal();
    render();
  });

  window.TokenCounter = {
    add,
    addOnce,
    set,
    get: () => total,
  };
})();
