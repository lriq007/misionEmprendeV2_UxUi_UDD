document.addEventListener("DOMContentLoaded", () => {
  const stage = document.querySelector(".pitch-stage");
  const overlay = document.querySelector("[data-editor-overlay]");
  const form = document.querySelector("[data-pitch-form]");
  const fields = Array.from(document.querySelectorAll(".pitch-field"));
  const tabs = Array.from(document.querySelectorAll("[data-tab]"));
  const steps = Array.from(document.querySelectorAll("[data-step]"));
  const cards = Array.from(document.querySelectorAll("[data-paper-card]"));
  const feedback = document.getElementById("pitchFeedback");
  const saveButton = document.getElementById("btnGuardarPitch");
  const completedCount = document.getElementById("pitch-token-count");
  const finalCard = document.querySelector("[data-final-card]");
  const paperContent = document.querySelector(".pitch-paper__content");
  const emptyState = document.querySelector("[data-empty-state]");
  const pitchPaper = document.querySelector("[data-pitch-paper]");
  const paperHeader = document.querySelector("[data-paper-header]");
  const howtoOverlay = document.getElementById("howto-overlay");
  let activeIndex = 0;

  const getCsrfToken = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  };

  const setFeedback = (message, type = "info") => {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.dataset.state = type;
  };

  const setEditorOpen = (isOpen, shouldFocus = false) => {
    if (!overlay) return;
    overlay.classList.toggle("is-open", isOpen);
    overlay.setAttribute("aria-hidden", isOpen ? "false" : "true");
    if (isOpen && shouldFocus) {
      window.setTimeout(() => {
        fields[activeIndex]?.focus();
      }, 120);
    }
  };

  const showStep = (index) => {
    activeIndex = Math.max(0, Math.min(index, steps.length - 1));
    const activeKey = steps[activeIndex]?.dataset.step;
    steps.forEach((step, stepIndex) => {
      step.classList.toggle("is-active", stepIndex === activeIndex);
    });
    tabs.forEach((tab, tabIndex) => {
      tab.classList.toggle("is-active", tabIndex === activeIndex);
      tab.setAttribute("aria-selected", tabIndex === activeIndex ? "true" : "false");
    });
    cards.forEach((card) => {
      card.classList.toggle("is-active", card.dataset.paperCard === activeKey);
    });
  };

  const getFirstEditableIndex = () => {
    const emptyIndex = fields.findIndex((field) => !field.value.trim());
    return emptyIndex >= 0 ? emptyIndex : activeIndex;
  };

  const showStepByKey = (key) => {
    const index = steps.findIndex((step) => step.dataset.step === key);
    showStep(index >= 0 ? index : 0);
  };

  const updateCounters = () => {
    let filled = 0;
    fields.forEach((field) => {
      const max = Number(field.dataset.max) || field.maxLength || 0;
      const counter = document.getElementById(`count-${field.dataset.key}`);
      if (counter) counter.textContent = `${field.value.length} / ${max}`;
      if (field.value.trim()) filled += 1;
      const card = document.querySelector(`[data-paper-card="${field.dataset.key}"]`);
      card?.classList.toggle("is-complete", Boolean(field.value.trim()));
    });
    if (completedCount) completedCount.textContent = String(filled);
  };

  const updatePaper = () => {
    fields.forEach((field) => {
      const target = document.querySelector(`[data-paper-field="${field.dataset.key}"]`);
      if (!target) return;
      target.textContent = field.value.trim() || "Pendiente de redacción.";
    });
  };

  document.querySelector("[data-open-editor]")?.addEventListener("click", () => {
    showStep(getFirstEditableIndex());
    setEditorOpen(true, true);
  });

  document.querySelector("[data-close-editor]")?.addEventListener("click", () => setEditorOpen(false));

  overlay?.addEventListener("click", (event) => {
    if (event.target === overlay) setEditorOpen(false);
  });

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      showStep(index);
      fields[activeIndex]?.focus();
    });
  });

  cards.forEach((card) => {
    const openCardEditor = () => {
      if (paperContent?.hidden) return;
      showStepByKey(card.dataset.paperCard);
      setEditorOpen(true, true);
    };
    card.addEventListener("click", openCardEditor);
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openCardEditor();
      }
    });
  });

  fields.forEach((field) => {
    field.addEventListener("input", updateCounters);
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!stage || !saveButton) return;

    const payload = {};
    fields.forEach((field) => {
      payload[field.dataset.key] = field.value.trim();
    });

    saveButton.disabled = true;
    setFeedback("Guardando pitch...");

    try {
      const response = await fetch(stage.dataset.saveUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.msg || "No se pudo guardar el pitch.");
      }

      updatePaper();
      emptyState?.setAttribute("hidden", "");
      pitchPaper?.classList.remove("is-empty");
      paperHeader?.removeAttribute("hidden");
      paperContent?.removeAttribute("hidden");
      finalCard?.removeAttribute("hidden");
      document.querySelector(".pitch-base")?.classList.add("has-final");
      setFeedback("Pitch guardado. La hoja ya está lista para la negociación.", "success");
      setEditorOpen(false);
      if (window.TokenCounter) {
        window.TokenCounter.addOnce("pitch-guardado", 4);
      }
    } catch (error) {
      setFeedback(error.message || "No se pudo guardar. Intenten nuevamente.", "error");
    } finally {
      saveButton.disabled = false;
    }
  });

  document.querySelector("[data-open-howto]")?.addEventListener("click", () => {
    howtoOverlay?.classList.add("is-open");
    howtoOverlay?.setAttribute("aria-hidden", "false");
  });

  document.querySelector("[data-close-howto]")?.addEventListener("click", () => {
    howtoOverlay?.classList.remove("is-open");
    howtoOverlay?.setAttribute("aria-hidden", "true");
  });

  howtoOverlay?.addEventListener("click", (event) => {
    if (event.target === howtoOverlay) {
      howtoOverlay.classList.remove("is-open");
      howtoOverlay.setAttribute("aria-hidden", "true");
    }
  });

  const timer = document.getElementById("e4-timer");
  if (timer) {
    const duration = Number(timer.dataset.durationSeconds) || 600;
    let remaining = duration;
    timer.textContent = formatTime(remaining);

    const interval = window.setInterval(async () => {
      remaining = Math.max(0, remaining - 1);
      timer.textContent = formatTime(remaining);
      if (remaining > 0) return;

      window.clearInterval(interval);
      try {
        if (stage?.dataset.timeupUrl) {
          const response = await fetch(stage.dataset.timeupUrl, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCsrfToken(),
            },
            body: "{}",
          });
          const data = await response.json();
          if (data.redirect_url) {
            window.location.href = data.redirect_url;
            return;
          }
        }
      } catch (_) {
        if (typeof window.showTimeupOverlay === "function") {
          window.showTimeupOverlay();
        }
      }
    }, 1000);
  }

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  }

  updateCounters();
  updatePaper();
  showStep(0);
});
