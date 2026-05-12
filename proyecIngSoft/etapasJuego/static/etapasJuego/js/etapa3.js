(() => {
  const form = document.getElementById("etapa3-form");
  const input = document.getElementById("legoInput");
  const btn = document.getElementById("legoBtn");
  const img = document.getElementById("legoImg");
  const clear = document.getElementById("legoClear");
  const status = document.getElementById("legoStatus");
  const epicMessage = document.getElementById("legoEpicMessage");

  if (!input || !btn || !img) return;

  const MAX_SIZE = 8 * 1024 * 1024;
  let hasSavedImage = btn.dataset.hasSavedImage === "true";
  let objectUrl = null;

  function setStatus(message, isSuccess = false) {
    if (!status) return;
    status.textContent = message;
    status.classList.toggle("is-success", isSuccess);
  }

  function setDroppedFile(file) {
    if (!window.DataTransfer) return;
    const transfer = new DataTransfer();
    transfer.items.add(file);
    input.files = transfer.files;
  }

  function resetPreview() {
    if (objectUrl) {
      URL.revokeObjectURL(objectUrl);
      objectUrl = null;
    }
    img.removeAttribute("src");
    img.hidden = true;
    btn.classList.remove("has-image");
    hasSavedImage = false;
    if (clear) clear.hidden = true;
    if (epicMessage) epicMessage.hidden = true;
    setStatus("Esperando imagen del producto.");
  }

  function showPreview(file) {
    if (!file) return false;

    if (!file.type || !file.type.startsWith("image/")) {
      setStatus("El archivo debe ser una imagen JPG o PNG.");
      return false;
    }

    if (file.size > MAX_SIZE) {
      setStatus("La imagen supera el limite de 8 MB.");
      return false;
    }

    if (objectUrl) URL.revokeObjectURL(objectUrl);
    objectUrl = URL.createObjectURL(file);
    img.src = objectUrl;
    img.hidden = false;
    btn.classList.add("has-image");
    if (clear) clear.hidden = false;
    if (epicMessage) epicMessage.hidden = false;
    setStatus("Prototipo detectado.", true);

    if (window.TokenCounter) {
      window.TokenCounter.addOnce("lego-upload", 6);
    }

    return true;
  }

  input.addEventListener("change", (event) => {
    showPreview(event.target.files?.[0]);
  });

  btn.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      input.click();
    }
  });

  ["dragenter", "dragover"].forEach((eventName) => {
    btn.addEventListener(eventName, (event) => {
      event.preventDefault();
      event.stopPropagation();
      btn.classList.add("is-dragover");
    });
  });

  ["dragleave", "dragend", "drop"].forEach((eventName) => {
    btn.addEventListener(eventName, (event) => {
      event.preventDefault();
      event.stopPropagation();
      btn.classList.remove("is-dragover");
    });
  });

  btn.addEventListener("drop", (event) => {
    const file = event.dataTransfer?.files?.[0];
    if (!file) return;
    setDroppedFile(file);
    showPreview(file);
  });

  clear?.addEventListener("click", () => {
    input.click();
  });

  form?.addEventListener("submit", (event) => {
    if (input.files?.length || hasSavedImage) return;
    event.preventDefault();
    setStatus("Suban una foto clara del prototipo antes de avanzar.");
    btn.focus();
  });

  if (hasSavedImage) {
    img.hidden = false;
    btn.classList.add("has-image");
    if (clear) clear.hidden = false;
    if (epicMessage) epicMessage.hidden = false;
    setStatus("Prototipo detectado.", true);
  } else {
    resetPreview();
  }
})();

(() => {
  const timer = document.getElementById("e3-timer");
  if (!timer) return;

  const duration = Number.parseInt(timer.dataset.durationSeconds, 10);
  let remaining = Number.isFinite(duration) ? duration : 15 * 60;

  function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const rest = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(rest).padStart(2, "0")}`;
  }

  timer.textContent = formatTime(remaining);

  const interval = window.setInterval(() => {
    remaining = Math.max(remaining - 1, 0);
    timer.textContent = formatTime(remaining);

    if (remaining === 0) {
      window.clearInterval(interval);
    }
  }, 1000);
})();
