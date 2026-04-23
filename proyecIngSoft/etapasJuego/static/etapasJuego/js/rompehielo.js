(() => {
  const root = document.querySelector("[data-rompehielo-app]");

  const formatClock = (totalSeconds) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  };

  function openTimeupOverlay() {
    if (typeof window.showTimeupOverlay === "function") {
      window.showTimeupOverlay();
      return;
    }

    const overlay = document.getElementById("timeup-overlay");
    if (!overlay) return;
    overlay.classList.add("is-open");
    overlay.setAttribute("aria-hidden", "false");
  }

  function startTimer(onComplete) {
    const timer = document.getElementById("rompehielo-timer");
    if (!timer) return;
    const timerPanel = timer.closest(".timer-panel");

    const seconds = Number.parseInt(timer.dataset.durationSeconds, 10);
    let remaining = Number.isFinite(seconds) ? seconds : 300;

    timer.textContent = formatClock(remaining);
    timerPanel?.classList.toggle("is-urgent", remaining <= 60);

    const intervalId = window.setInterval(() => {
      remaining -= 1;

      if (remaining > 0) {
        timer.textContent = formatClock(remaining);
        timerPanel?.classList.toggle("is-urgent", remaining <= 60);
        return;
      }

      timer.textContent = "00:00";
      timerPanel?.classList.add("is-urgent");
      window.clearInterval(intervalId);
      onComplete?.();
      openTimeupOverlay();
    }, 1000);
  }

  function createState() {
    if (!root) return null;

    return {
      questions: [],
      availableIds: [],
      selectedId: null,
      isBusy: false,
      isTimeUp: false,
      spinTimeoutId: null,
      bootstrapUrl: root.dataset.bootstrapUrl,
      wheel: root.querySelector("[data-roulette-wheel]"),
      segmentsContainer: root.querySelector("[data-roulette-segments]"),
      turnButton: root.querySelector("[data-turn-button]"),
      turnStatus: root.querySelector("[data-turn-status]"),
      cycleStatus: root.querySelector("[data-cycle-status]"),
      remainingCount: root.querySelector("[data-remaining-count]"),
      errorBanner: root.querySelector("[data-error-banner]"),
      errorTitle: root.querySelector("[data-error-title]"),
      errorMessage: root.querySelector("[data-error-message]"),
      questionOverlay: document.querySelector("[data-question-overlay]"),
      currentQuestion: document.querySelector("[data-current-question]"),
      questionEmoji: document.querySelector("[data-question-emoji]"),
      passButton: document.querySelector("[data-pass-button]"),
    };
  }

  function setTurnButton(state, label, disabled, retry = false) {
    const labelNode = state.turnButton.querySelector(".turn-button__text");
    if (labelNode) {
      labelNode.textContent = label;
    } else {
      state.turnButton.textContent = label;
    }
    state.turnButton.disabled = disabled;
    state.turnButton.classList.toggle("is-retry", retry);
  }

  function updateCycleStatus(state, recycled = false) {
    if (state.remainingCount) {
      state.remainingCount.textContent = String(state.availableIds.length);
    }

    if (!state.cycleStatus) {
      return;
    }

    if (recycled) {
      state.cycleStatus.textContent = "Nueva ronda iniciada. Todas las preguntas vuelven a estar disponibles.";
      return;
    }

    if (state.availableIds.length) {
      state.cycleStatus.textContent = `${state.availableIds.length} preguntas disponibles antes de reiniciar la rueda.`;
      return;
    }

    state.cycleStatus.textContent = "Ronda completa. La siguiente selección reiniciará automáticamente la ruleta.";
  }

  function clearError(state) {
    if (!state.errorBanner || !state.errorTitle || !state.errorMessage) {
      return;
    }

    state.errorBanner.hidden = true;
    state.errorTitle.textContent = "No pudimos preparar este turno.";
    state.errorMessage.textContent = "Intenta nuevamente con el mismo botón central.";
  }

  function showError(state, message, context = "turno") {
    if (state.errorBanner && state.errorTitle && state.errorMessage) {
      state.errorBanner.hidden = false;
      state.errorTitle.textContent = "No pudimos completar la dinámica.";
      state.errorMessage.textContent = `${message} Contexto: ${context}.`;
    }

    if (state.turnStatus) {
      state.turnStatus.textContent = "La pantalla sigue disponible para reintentar.";
    }
    state.isBusy = false;
    state.wheel?.classList.remove("is-spinning");
    setTurnButton(state, "Reintentar ruleta", false, true);
  }

  function renderSegments(state) {
    if (!state.segmentsContainer) return;

    state.segmentsContainer.innerHTML = "";
    const segmentAngle = 360 / state.questions.length;

    state.questions.forEach((question, index) => {
      const segment = document.createElement("div");
      const angle = segmentAngle * index + segmentAngle / 2;

      segment.className = "roulette-segment";
      segment.style.setProperty("--angle", `${angle}deg`);
      segment.dataset.questionId = String(question.id);

      if (question.id === state.selectedId) {
        segment.classList.add("is-selected");
      }

      const bubble = document.createElement("span");
      bubble.className = "roulette-segment__bubble";
      bubble.textContent = question.emoji || "✨";
      bubble.title = question.text;
      segment.appendChild(bubble);
      state.segmentsContainer.appendChild(segment);
    });
  }

  async function loadQuestions(state) {
    if (!state.bootstrapUrl) {
      showError(state, "No encontramos la ruta de bootstrap de la ruleta", "bootstrap_url");
      return;
    }

    setTurnButton(state, "Preparando ruleta...", true);
    if (state.turnStatus) {
      state.turnStatus.textContent = "Cargando preguntas del rompehielo...";
    }
    clearError(state);

    try {
      const response = await fetch(state.bootstrapUrl, {
        headers: { Accept: "application/json" },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const payload = await response.json();
      if (!payload.success || !Array.isArray(payload.questions) || payload.questions.length === 0) {
        throw new Error(payload.context || "invalid_payload");
      }

      state.questions = payload.questions;
      state.availableIds = payload.questions.map((question) => question.id);
      state.selectedId = null;
      renderSegments(state);
      updateCycleStatus(state);
      if (state.turnStatus) {
        state.turnStatus.textContent = "La ruleta está lista. Presiona el centro para comenzar la ronda.";
      }
      setTurnButton(state, "Comenzar ruleta", false);
    } catch (error) {
      showError(state, "No pudimos cargar las preguntas del rompehielo. Intenta nuevamente", error.message);
    }
  }

  function closeQuestionOverlay(state) {
    if (!state.questionOverlay) return;
    state.questionOverlay.hidden = true;
    state.questionOverlay.classList.remove("is-open");
    state.questionOverlay.setAttribute("aria-hidden", "true");
  }

  function openQuestionOverlay(state) {
    if (!state.questionOverlay) return;
    state.questionOverlay.hidden = false;
    state.questionOverlay.classList.add("is-open");
    state.questionOverlay.setAttribute("aria-hidden", "false");
  }

  function stopPendingTransitions(state) {
    window.clearTimeout(state.spinTimeoutId);
    state.spinTimeoutId = null;
  }

  function selectQuestion(state) {
    if (state.questions.length === 0) {
      throw new Error("empty_catalog");
    }

    let recycled = false;
    if (state.availableIds.length === 0) {
      state.availableIds = state.questions.map((question) => question.id);
      recycled = true;
    }

    const randomIndex = Math.floor(Math.random() * state.availableIds.length);
    const selectedId = state.availableIds.splice(randomIndex, 1)[0];
    const question = state.questions.find((item) => item.id === selectedId);

    if (!question) {
      throw new Error("missing_question");
    }

    return { question, recycled };
  }

  function applySelection(state, question, recycled) {
    if (!state.currentQuestion || !state.questionEmoji) {
      throw new Error("missing_question_overlay");
    }

    state.selectedId = question.id;
    state.currentQuestion.textContent = question.text;
    state.questionEmoji.textContent = question.emoji || "✨";
    if (state.turnStatus) {
      state.turnStatus.textContent = "Pregunta seleccionada. Comparte la respuesta y luego pasa la tablet.";
    }
    updateCycleStatus(state, recycled);
    renderSegments(state);
    openQuestionOverlay(state);
    setTurnButton(state, "Pregunta en curso", true);
  }

  function finishSpin(state) {
    state.isBusy = false;
    state.wheel?.classList.remove("is-spinning");
  }

  function spinRoulette(state) {
    if (state.isBusy || state.isTimeUp) return;

    if (state.questions.length === 0) {
      loadQuestions(state);
      return;
    }

    state.isBusy = true;
    clearError(state);
    closeQuestionOverlay(state);
    setTurnButton(state, "Girando...", true);
    if (state.turnStatus) {
      state.turnStatus.textContent = "La ruleta está girando para elegir la siguiente pregunta...";
    }
    state.wheel?.classList.remove("is-spinning");

    window.requestAnimationFrame(() => {
      state.wheel?.classList.add("is-spinning");
    });

    state.spinTimeoutId = window.setTimeout(() => {
      try {
        const { question, recycled } = selectQuestion(state);
        applySelection(state, question, recycled);
        finishSpin(state);
      } catch (error) {
        showError(state, "No pudimos actualizar la pregunta. Intenta nuevamente", error.message);
      }
    }, 1200);
  }

  function handlePassToNext(state) {
    if (state.isTimeUp) return;

    closeQuestionOverlay(state);
    if (state.turnStatus) {
      state.turnStatus.textContent = "Tablet lista para el siguiente compañero. Presiona “Girar” para comenzar el nuevo turno.";
    }
    setTurnButton(state, "Girar", false);
  }

  function handleTimeUp(state) {
    state.isTimeUp = true;
    stopPendingTransitions(state);
    closeQuestionOverlay(state);
    state.wheel?.classList.remove("is-spinning");
    setTurnButton(state, "Tiempo finalizado", true);
    if (state.passButton) {
      state.passButton.disabled = true;
    }
    if (state.turnStatus) {
      state.turnStatus.textContent = "El tiempo del rompehielo terminó. Avanzando al siguiente paso.";
    }
  }

  function initRompehielo() {
    const state = createState();
    if (!state) return;

    state.turnButton?.addEventListener("click", () => spinRoulette(state));
    state.passButton?.addEventListener("click", () => handlePassToNext(state));
    loadQuestions(state);
    startTimer(() => handleTimeUp(state));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRompehielo, { once: true });
  } else {
    initRompehielo();
  }
})();
