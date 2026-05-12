(() => {
  const qs  = (s, p = document) => p.querySelector(s);
  const qsa = (s, p = document) => [...p.querySelectorAll(s)];

  // ── Story / Squad ─────────────────────────────────────────────────────────
  const storyView     = qs("[data-story-view]");
  const squadView     = qs("[data-squad-view]");
  const nextButton    = qs("[data-next-view]");
  const squadOptions  = qsa("[data-squad-option]");
  const squadStatus   = qs("[data-squad-status]");
  const squadContinue = qs("[data-squad-continue]");
  const squadOptionsEl = qs(".squad-options");

  // ── Challenge overlay ─────────────────────────────────────────────────────
  const overlay       = qs("[data-challenge-overlay]");
  const closeButton   = qs("[data-challenge-close]");
  const form          = qs("[data-challenge-form]");
  const topicField    = qs("[data-topic-field]");
  const challengeField = qs("[data-challenge-field]");
  const desafioField  = qs("[data-desafio-field]");
  const submitButton  = qs("[data-challenge-submit]");
  const actions       = qs("[data-challenge-actions]");
  const panels        = qsa("[data-topic-panel]");
  const backButtons   = qsa("[data-challenge-back]");

  // ── Photo panel ───────────────────────────────────────────────────────────
  const photoPanel       = qs("#team-photo-panel");
  const teamNameInput    = qs("#teamNameInput");
  const teamPhotoInput   = qs("#teamPhotoInput");
  const teamPhotoBtn     = qs("#teamPhotoBtn");
  const photoStateIdle   = qs("#photoStateIdle");
  const photoStateUp     = qs("#photoStateUploading");
  const photoStateOk     = qs("#photoStateSuccess");
  const teamPhotoPreview = qs("#teamPhotoPreview");
  const photoContinueBtn = qs("#photoContinueBtn");
  const photoErrorMsg    = qs("#photoErrorMsg");

  const CSRF_TOKEN = qs('meta[name="csrf-token"]')?.content ?? "";
  const FOTO_URL   = qs('meta[name="foto-equipo-url"]')?.content ?? "";

  // ── State ─────────────────────────────────────────────────────────────────
  let selectedSquad = null;
  let activePanel   = null;
  let squadLocked   = false;

  // ── Shared helpers ────────────────────────────────────────────────────────
  function setContinueEnabled(enabled) {
    if (!squadContinue) return;
    squadContinue.classList.toggle("is-disabled", !enabled);
    squadContinue.setAttribute("aria-disabled", enabled ? "false" : "true");
    squadContinue.disabled = !enabled;
  }

  function resetChallengeForm() {
    if (challengeField) challengeField.value  = "";
    if (desafioField)   desafioField.value    = "";
    if (submitButton)   submitButton.disabled = true;
    if (actions)        actions.hidden        = true;
    qsa("[data-challenge-choice]").forEach(c => c.classList.remove("is-selected"));
  }

  function resetPanel(panel) {
    if (!panel) return;
    const detail = qs("[data-challenge-detail]", panel);
    const video  = qs("[data-detail-video]",    panel);
    const empty  = qs("[data-video-empty]",     panel);
    panel.classList.remove("is-detail");
    if (detail) { detail.hidden = true; detail.classList.remove("is-active"); }
    if (video)  { try { video.pause(); } catch (_) {} video.removeAttribute("src"); video.load(); }
    if (empty)  { empty.hidden = false; }
  }

  function selectSquad(option) {
    selectedSquad = option;
    squadOptions.forEach(o => {
      const active = o === option;
      o.classList.toggle("is-selected", active);
      o.setAttribute("aria-checked", String(active));
      o.tabIndex = active ? 0 : -1;
    });
    if (squadStatus) {
      squadStatus.textContent = `Escuadrón ${option.dataset.topicName} seleccionado.`;
      squadStatus.classList.add("is-ready");
    }
    setContinueEnabled(true);
  }

  // ── Challenge overlay ─────────────────────────────────────────────────────
  function openOverlay() {
    if (!overlay || !selectedSquad) return;
    const topicId = selectedSquad.dataset.topicId ?? "";
    activePanel = panels.find(p => p.dataset.topicPanel === topicId) ?? null;
    panels.forEach(p => { p.hidden = p !== activePanel; resetPanel(p); });
    resetChallengeForm();
    if (topicField) topicField.value = topicId;
    overlay.hidden = false;
    overlay.classList.add("is-open");
    overlay.setAttribute("aria-hidden", "false");
    document.body.classList.add("challenge-modal-open");
    // Once locked, hide the close button so the user cannot go back to squad selection
    if (closeButton) closeButton.hidden = squadLocked;
  }

  function closeOverlay() {
    if (!overlay) return;
    // After squad is locked the challenge overlay is the point of no return
    if (squadLocked) return;
    panels.forEach(resetPanel);
    resetChallengeForm();
    overlay.classList.remove("is-open");
    overlay.setAttribute("aria-hidden", "true");
    overlay.hidden = true;
    document.body.classList.remove("challenge-modal-open");
    activePanel = null;
  }

  function showPicker() {
    if (!activePanel) return;
    resetPanel(activePanel);
    resetChallengeForm();
  }

  function selectChallenge(choice) {
    if (!activePanel || !choice) return;
    const detail = qs("[data-challenge-detail]", activePanel);
    const title  = qs("[data-detail-title]",     activePanel);
    const desc   = qs("[data-detail-desc]",      activePanel);
    const video  = qs("[data-detail-video]",     activePanel);
    const empty  = qs("[data-video-empty]",      activePanel);
    qsa("[data-challenge-choice]", activePanel).forEach(c => c.classList.toggle("is-selected", c === choice));
    if (topicField)     topicField.value     = choice.dataset.topicId     ?? "";
    if (challengeField) challengeField.value = choice.dataset.challengeId ?? "";
    if (desafioField)   desafioField.value   = choice.dataset.desafioId   ?? "";
    if (submitButton)   submitButton.disabled = !(choice.dataset.challengeId && choice.dataset.desafioId);
    if (actions)        actions.hidden = false;
    if (title) title.textContent = choice.dataset.title ?? "Desafío";
    if (desc)  desc.textContent  = choice.dataset.desc  ?? "";
    if (video) {
      try { video.pause(); } catch (_) {}
      video.removeAttribute("src");
      const src = choice.dataset.video ?? "";
      if (src) { video.src = src; video.load(); }
    }
    if (empty) empty.hidden = Boolean(choice.dataset.video);
    activePanel.classList.add("is-detail");
    if (detail) { detail.hidden = false; requestAnimationFrame(() => detail.classList.add("is-active")); }
  }

  // ── Photo Panel ───────────────────────────────────────────────────────────
  function showPhotoState(state) {
    if (photoStateIdle) photoStateIdle.hidden = state !== "idle";
    if (photoStateUp)   photoStateUp.hidden   = state !== "uploading";
    if (photoStateOk)   photoStateOk.hidden   = state !== "success";
    if (photoErrorMsg)  photoErrorMsg.hidden  = true;
  }

  function showPhotoError(msg) {
    showPhotoState("idle");
    if (photoErrorMsg) { photoErrorMsg.textContent = msg; photoErrorMsg.hidden = false; }
  }

  function lockBrowserBack() {
    history.pushState(null, "", location.href);
    window.addEventListener("popstate", () => history.pushState(null, "", location.href));
  }

  function openPhotoPanel() {
    if (!photoPanel) return;
    showPhotoState("idle");
    if (teamNameInput) {
      teamNameInput.disabled = false;
      teamNameInput.focus();
    }
    if (photoContinueBtn) {
      photoContinueBtn.disabled = true;
      photoContinueBtn.setAttribute("aria-disabled", "true");
    }
    // Prevent browser back navigation from this point on
    lockBrowserBack();
    photoPanel.hidden = false;
    photoPanel.classList.add("is-open");
    photoPanel.setAttribute("aria-hidden", "false");
  }

  function closePhotoPanel() {
    if (!photoPanel) return;
    photoPanel.classList.remove("is-open");
    photoPanel.setAttribute("aria-hidden", "true");
    photoPanel.hidden = true;
  }

  async function uploadTeamPhoto(file) {
    if (!FOTO_URL) { showPhotoError("URL de subida no configurada."); return; }
    const teamName = (teamNameInput?.value || "").trim();
    if (!teamName) {
      showPhotoError("Ingresen un nombre creativo y acorde al escuadrón seleccionado.");
      teamNameInput?.focus();
      return;
    }
    showPhotoState("uploading");
    const fd = new FormData();
    fd.append("foto_equipo", file);
    fd.append("nombre_equipo", teamName);
    try {
      const res  = await fetch(FOTO_URL, {
        method: "POST",
        headers: { "X-CSRFToken": CSRF_TOKEN },
        body: fd,
      });
      if (!res.ok) { showPhotoError("Error al subir la foto. Intenta de nuevo."); return; }
      const data = await res.json();
      if (data.ok) {
        if (teamPhotoPreview) teamPhotoPreview.src = URL.createObjectURL(file);
        showPhotoState("success");
        if (teamNameInput) teamNameInput.disabled = true;
        if (photoContinueBtn) {
          photoContinueBtn.disabled = false;
          photoContinueBtn.setAttribute("aria-disabled", "false");
        }
      } else {
        showPhotoError(data.msg || "Error al subir la foto. Intenta de nuevo.");
      }
    } catch (_) {
      showPhotoError("Error de conexión. Verifica tu red e intenta de nuevo.");
    }
  }

  teamPhotoBtn?.addEventListener("click", () => {
    if (!(teamNameInput?.value || "").trim()) {
      showPhotoError("Ingresen un nombre creativo y acorde al escuadrón seleccionado.");
      teamNameInput?.focus();
      return;
    }
    teamPhotoInput?.click();
  });

  teamPhotoInput?.addEventListener("change", () => {
    const file = teamPhotoInput?.files?.[0];
    if (!file) return;
    if (file.size > 8 * 1024 * 1024) {
      showPhotoError("La foto es demasiado grande (máx 8 MB). Elige otra.");
      return;
    }
    uploadTeamPhoto(file);
  });

  photoContinueBtn?.addEventListener("click", () => {
    if (photoContinueBtn?.disabled) return;
    // Irreversible: lock squad options
    squadLocked = true;
    if (squadOptionsEl) squadOptionsEl.classList.add("is-locked");
    closePhotoPanel();
    openOverlay();
  });

  // ── Squad card interaction ────────────────────────────────────────────────
  squadOptions.forEach(option => {
    option.addEventListener("click", () => {
      if (squadLocked) return;
      selectSquad(option);
      openPhotoPanel();
    });
    option.addEventListener("keydown", e => {
      if (e.key !== "Enter" && e.key !== " ") return;
      e.preventDefault();
      if (squadLocked) return;
      selectSquad(option);
      openPhotoPanel();
    });
  });

  squadContinue?.addEventListener("click", () => {
    if (squadContinue.getAttribute("aria-disabled") === "true") return;
    // If photo already uploaded, go straight to challenge overlay
    if (squadLocked) { openOverlay(); return; }
    openPhotoPanel();
  });

  // ── Story navigation ──────────────────────────────────────────────────────
  nextButton?.addEventListener("click", () => {
    storyView?.classList.remove("is-active");
    squadView?.classList.add("is-active");
  });

  // ── Challenge overlay events ──────────────────────────────────────────────
  qsa("[data-challenge-choice]").forEach(c => c.addEventListener("click", () => selectChallenge(c)));
  backButtons.forEach(btn => btn.addEventListener("click", showPicker));
  closeButton?.addEventListener("click", closeOverlay);

  overlay?.addEventListener("click", e => {
    if (e.target === overlay) closeOverlay();
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && overlay && !overlay.hidden) closeOverlay();
  });

  form?.addEventListener("submit", e => {
    if (!challengeField?.value || !desafioField?.value) e.preventDefault();
  });
})();
