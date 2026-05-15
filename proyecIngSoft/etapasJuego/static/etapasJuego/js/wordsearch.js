/* global CSRF_TOKEN */
(() => {
  const qs = (s, p = document) => p.querySelector(s);
  const qsa = (s, p = document) => [...p.querySelectorAll(s)];
  const POST = (url, data) => fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": CSRF_TOKEN },
    body: JSON.stringify(data || {}),
  }).then((r) => r.json());

  const COLORS = ["#fb7185", "#60a5fa"];
  const STATUS_PENDING = "PENDING";
  const STATUS_PLAYING = "PLAYING";
  const STATUS_FINISHED = "FINISHED";
  const STATUS_TIME_UP = "TIME_UP";

  let BOARD = [];
  let WORDS = [];
  let FOUND = new Set();
  /*nuevo 12/5 */
  let FOUND_CELLS = new Set();
  let PROGRESS = 0;
  let ACTIVE = {};
  let LOCKED = new Set();
  let BOARD_SIZE = 10;
  let CURRENT_STATUS = STATUS_PENDING;
  let isComplete = false;
  let isStarted = false;
  let timerIntervalId = null;
  let readyAtIso = null;

  const root = qs("[data-stage1-app]");
  const elBoard = qs("#ws-board");
  const elWords = qs("#ws-words");
  const elProgress = qs("#ws-progress");
  const elComplete = qs("#complete-overlay");
  const elTimer = qs("#ws-timer");
  const introOverlay = qs("#stage1-intro-overlay");
  const startButton = qs("#stage1-start-button");
  const startError = qs("#stage1-start-error");
  const startUrl = root?.dataset.startUrl;
  const timeupUrl = root?.dataset.timeupUrl;
  const rankingUrl = root?.dataset.rankingUrl;

  const key = (i, j) => `${i},${j}`;

  function setBoardInteractive(enabled) {
    if (!elBoard) return;
    elBoard.classList.toggle("is-disabled", !enabled);
    elBoard.setAttribute("aria-disabled", enabled ? "false" : "true");
  }

  function formatSeconds(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  function getRemainingSeconds(totalSeconds) {
    if (!readyAtIso) return totalSeconds;
    const readyAt = new Date(readyAtIso);
    if (Number.isNaN(readyAt.getTime())) return totalSeconds;
    const elapsed = Math.max(Math.floor((Date.now() - readyAt.getTime()) / 1000), 0);
    return Math.max(totalSeconds - elapsed, 0);
  }

  /* Nuevo 12/5 */
  function paintBoard() {

    elBoard.style.gridTemplateColumns =
      `repeat(${BOARD_SIZE}, var(--ws-cell-size, 42px))`;

    elBoard.innerHTML = "";

    for (let i = 0; i < BOARD_SIZE; i += 1) {

      for (let j = 0; j < BOARD_SIZE; j += 1) {

        const cell = document.createElement("div");

        cell.className = "ws-cell";

        cell.dataset.i = i;

        cell.dataset.j = j;

        cell.textContent =
          (BOARD[i][j] || "")
          .toString()
          .toUpperCase();

        // Mantener destacadas las celdas encontradas
        if (FOUND_CELLS.has(key(i, j))) {

          cell.classList.add("found");

        }

        elBoard.appendChild(cell);

      }

    }

  }
  /* Fin nuevo 12/5 */

  function updateProgress() {
    if (!elProgress) return;
    const value = Math.max(0, Math.min(100, PROGRESS));
    elProgress.textContent = `Progreso: ${value.toFixed(0)}%`;
    elProgress.style.setProperty("--progress", `${value}%`);
    elProgress.setAttribute("aria-label", `Progreso de la sopa de letras: ${value.toFixed(0)}%`);
  }

  function paintWords() {
    elWords.innerHTML = "";
    for (const word of WORDS) {
      const item = document.createElement("li");
      item.textContent = word;
      if (FOUND.has(word)) item.classList.add("found");
      elWords.appendChild(item);
    }
    updateProgress();
  }

  function lockCellsFromActive() {
    qsa(".ws-cell").forEach((cell) => {
      const cellKey = key(+cell.dataset.i, +cell.dataset.j);
      cell.classList.toggle("locked", LOCKED.has(cellKey));
    });
  }

  function colorActivePaths() {
    qsa(".ws-cell").forEach((cell) => {
      cell.style.outline = "";
    });
    Object.values(ACTIVE).forEach((selection) => {
      selection.path.forEach(([i, j]) => {
        const cell = qs(`.ws-cell[data-i="${i}"][data-j="${j}"]`);
        if (cell) cell.style.outline = `3px solid ${selection.color}`;
      });
    });
  }
  /* Nuevo 12/5 */
  function markFound(word, path = []) {

    FOUND.add(word);

    path.forEach(([i, j]) => {

      FOUND_CELLS.add(
        key(i, j)
      );

    });

  }
  /* FIn 12/5 */

  function showComplete() {
    isComplete = true;
    CURRENT_STATUS = STATUS_FINISHED;
    if (elComplete) {
      elComplete.classList.add("is-open");
      elComplete.setAttribute("aria-hidden", "false");
    }
  }

  function closeIntroOverlay() {
    if (!introOverlay) return;
    introOverlay.classList.remove("is-open");
    introOverlay.setAttribute("aria-hidden", "true");
    introOverlay.hidden = true;
    introOverlay.style.display = "none";
  }

  function openIntroOverlay() {
    if (!introOverlay) return;
    introOverlay.hidden = false;
    introOverlay.classList.add("is-open");
    introOverlay.setAttribute("aria-hidden", "false");
    introOverlay.style.display = "";
  }

  async function goToRanking() {
    if (rankingUrl) {
      window.location.href = rankingUrl;
    }
  }

  async function notifyTimeUpAndRedirect() {
    let redirectUrl = rankingUrl;
    if (timeupUrl) {
      try {
        const data = await POST(timeupUrl, {});
        if (data && data.redirect_url) redirectUrl = data.redirect_url;
      } catch (error) {
        // use fallback on error
      }
    }
    window.location.href = redirectUrl;
  }

  const pointerMap = new Map();

  function getCellFromPointerEvent(event) {
    const element = document.elementFromPoint(event.clientX, event.clientY);
    if (!element || !element.classList || !element.classList.contains("ws-cell")) return null;

    const i = +element.dataset.i;
    const j = +element.dataset.j;
    if (LOCKED.has(key(i, j))) return null;

    return { i, j };
  }

  async function flushExtend(pointerId) {
    const info = pointerMap.get(pointerId);
    if (!info || info.inFlight || !info.pendingCell) return;

    info.inFlight = true;
    const nextCell = info.pendingCell;
    info.pendingCell = null;

    try {
      const response = await POST("/etapasJuego/api/select/extend/", {
        selection_id: info.selection_id,
        cell: [nextCell.i, nextCell.j],
      });
      if (response.ok) {
        ACTIVE = response.active_selections || ACTIVE;
        LOCKED = new Set((response.locked_cells || []).map((entry) => `${entry[0]},${entry[1]}`));
        info.lastCellKey = key(nextCell.i, nextCell.j);
        lockCellsFromActive();
        colorActivePaths();
      }
    } finally {
      const latest = pointerMap.get(pointerId);
      if (!latest) return;

      latest.inFlight = false;
      if (latest.pendingCell) {
        flushExtend(pointerId);
      } else if (latest.released && !latest.committing) {
        finalizePointerSelection(pointerId);
      }
    }
  }

  function queueExtend(pointerId, cell) {
    const info = pointerMap.get(pointerId);
    if (!info || !cell) return;

    const cellKey = key(cell.i, cell.j);
    const pendingKey = info.pendingCell ? key(info.pendingCell.i, info.pendingCell.j) : null;
    if (cellKey === info.lastCellKey || cellKey === pendingKey) return;

    info.pendingCell = cell;
    flushExtend(pointerId);
  }

  async function finalizePointerSelection(pointerId) {
    const info = pointerMap.get(pointerId);
    if (!info || info.committing) return;

    if (info.inFlight || info.pendingCell) {
      info.released = true;
      return;
    }

    info.committing = true;
    pointerMap.delete(pointerId);

    const response = await POST("/etapasJuego/api/select/commit/", {
      selection_id: info.selection_id,
    });
    if (!response.ok) {
      ACTIVE = {};
      LOCKED = new Set();
      lockCellsFromActive();
      colorActivePaths();
      return;
    }

    /* Nuevo */
    if (response.result === "found" && response.word) {

      const selection = ACTIVE[info.selection_id];
      const foundPath = selection ? selection.path : [];
      const foundKeys = new Set(foundPath.map(([i, j]) => key(i, j)));

      markFound(response.word, foundPath);

      if (window.TokenCounter) {
        window.TokenCounter.addOnce(`ws-word-${response.word}`, 2);
      }

      paintWords();

      qsa(".ws-cell").forEach((cell) => {
        if (foundKeys.has(key(+cell.dataset.i, +cell.dataset.j))) {
          cell.classList.add("found");
          cell.style.outline = "";
        }
      });

    } else if (response.result === "already_found") {

      qsa(".ws-cell").forEach((cell) => {

        if (
          cell.style.outline &&
          cell.style.outline.includes(info.color)
        ) {

          cell.animate(
            [
              { background: "#fde68a" },
              { background: "#f3f4f6" }
            ],
            {
              duration: 600
            }
          );

          cell.style.outline = "";

        }

      });

    } else {

      qsa(".ws-cell").forEach((cell) => {

        if (
          cell.style.outline &&
          cell.style.outline.includes(info.color)
        ) {

          cell.animate(
            [
              { transform: "translateX(0px)" },
              { transform: "translateX(6px)" },
              { transform: "translateX(0px)" }
            ],
            {
              duration: 150
            }
          );

          cell.style.outline = "";

        }

      });

    }
/*fin nuevo */

    ACTIVE = {};
    LOCKED = new Set();
    lockCellsFromActive();
    colorActivePaths();

    if (response.found_words) {
      FOUND = new Set(response.found_words);
    }
    if (typeof response.progress_pct === "number") {
      PROGRESS = response.progress_pct;
      updateProgress();
    }

    if (response.status) {
      CURRENT_STATUS = response.status;
    }

    if (response.ended) {
      showComplete();
      window.setTimeout(() => {
        window.location.href = response.redirect_url || rankingUrl;
      }, 1000);
    }
  }

  async function pointerDown(event) {
    if (!isStarted || CURRENT_STATUS !== STATUS_PLAYING) return;
    if (!(event.target.classList.contains("ws-cell"))) return;

    const i = +event.target.dataset.i;
    const j = +event.target.dataset.j;
    if (LOCKED.has(key(i, j))) return;

    const color = pointerMap.size === 0 ? COLORS[0] : COLORS[1];
    const response = await POST("/etapasJuego/api/select/start/", { color, start: [i, j] });
    if (!response.ok) return;

    pointerMap.set(event.pointerId, {
      selection_id: response.selection_id,
      color,
      lastCellKey: key(i, j),
      pendingCell: null,
      inFlight: false,
      released: false,
      committing: false,
    });
    ACTIVE = response.active_selections || ACTIVE;
    LOCKED = new Set((response.locked_cells || []).map((entry) => `${entry[0]},${entry[1]}`));
    lockCellsFromActive();
    colorActivePaths();
    event.target.setPointerCapture(event.pointerId);
  }

  async function pointerMove(event) {
    if (!isStarted || CURRENT_STATUS !== STATUS_PLAYING) return;
    if (!pointerMap.has(event.pointerId)) return;

    const cell = getCellFromPointerEvent(event);
    queueExtend(event.pointerId, cell);
  }

  async function pointerUp(event) {
    if (!pointerMap.has(event.pointerId)) return;
    const info = pointerMap.get(event.pointerId);
    if (info) {
      info.released = true;
    }
    await finalizePointerSelection(event.pointerId);
  }

  function bindEvents() {
    elBoard.addEventListener("pointerdown", pointerDown);
    elBoard.addEventListener("pointermove", pointerMove);
    elBoard.addEventListener("pointerup", pointerUp);
    elBoard.addEventListener("pointercancel", pointerUp);
    elBoard.addEventListener("lostpointercapture", pointerUp);
  }

  async function init() {
    const response = await POST("/etapasJuego/api/init/", {});
    BOARD = response.soup || [];
    WORDS = response.words || [];
    FOUND = new Set(response.found_words || []);
    PROGRESS = typeof response.progress_pct === "number"
      ? response.progress_pct
      : (typeof response.progress === "number" ? response.progress : 0);
    BOARD_SIZE = response.board_size || 10;
    CURRENT_STATUS = response.status || STATUS_PENDING;
    isStarted = Boolean(response.ready);
    isComplete = Boolean(response.ended);
    readyAtIso = response.ready_at || null;

    if (elComplete) elComplete.hidden = true;

    paintBoard();
    paintWords();
    lockCellsFromActive();
    colorActivePaths();

    setBoardInteractive(isStarted && CURRENT_STATUS === STATUS_PLAYING);
    if (isStarted) {
      closeIntroOverlay();
    } else {
      openIntroOverlay();
    }
  }

  function startSimpleTimer(durationSeconds = 300) {
    if (!elTimer) return;
    window.clearInterval(timerIntervalId);

    let remaining = durationSeconds;
    const format = (time) => formatSeconds(time);
    elTimer.textContent = format(remaining);

    if (remaining <= 0) {
      if (isComplete) {
        goToRanking();
      } else {
        notifyTimeUpAndRedirect();
      }
      return;
    }

    timerIntervalId = window.setInterval(() => {
      remaining = Math.max(remaining - 1, 0);
      elTimer.textContent = format(remaining);

      if (remaining !== 0) return;

      window.clearInterval(timerIntervalId);
      timerIntervalId = null;
      if (isComplete) {
        goToRanking();
        return;
      }
      notifyTimeUpAndRedirect();
    }, 1000);
  }

  async function handleStart() {
    if (!startUrl || !startButton) return;
    if (startError) {
      startError.hidden = true;
    }
    startButton.disabled = true;
    try {
      const response = await POST(startUrl, {});
      if (!response || response.ok !== true) {
        startButton.disabled = false;
        if (startError) {
          startError.hidden = false;
        }
        return;
      }
      isStarted = true;
      CURRENT_STATUS = response.status || STATUS_PLAYING;
      readyAtIso = response.ready_at || new Date().toISOString();
      closeIntroOverlay();
      setBoardInteractive(true);
      const duration = parseInt(elTimer?.dataset.durationSeconds, 10);
      startSimpleTimer(Number.isFinite(duration) ? duration : 300);
    } catch (error) {
      startButton.disabled = false;
      if (startError) {
        startError.hidden = false;
      }
    }
  }

  window.__stage1WordsearchLoaded = true;
  window.__stage1StartBridge = handleStart;

  document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();

    try {
      await init();
    } catch (error) {
      if (startError) {
        startError.hidden = false;
        startError.textContent = "No pudimos cargar la etapa. Recarga e intenta nuevamente.";
      }
      return;
    }

    const tokensFromServer = Number(qs("#ws-timer")?.dataset.tokensTotal || Number.NaN);
    if (window.TokenCounter && Number.isFinite(tokensFromServer)) {
      window.TokenCounter.set(tokensFromServer);
    }

    if (isStarted && CURRENT_STATUS === STATUS_PLAYING) {
      const duration = parseInt(elTimer?.dataset.durationSeconds, 10);
      startSimpleTimer(Number.isFinite(duration) ? getRemainingSeconds(duration) : 300);
    }
  });
})();
