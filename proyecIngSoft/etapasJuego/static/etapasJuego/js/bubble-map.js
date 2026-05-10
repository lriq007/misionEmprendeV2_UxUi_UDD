(() => {
  const map = document.getElementById('bubbleMap');
  if (!map) return;

  const nodes = Array.from(map.querySelectorAll('.spiral-question'));
  const panel = document.getElementById('bubbleAnswerPanel');
  const input = document.getElementById('bubbleAnswerInput');
  const panelQuestion = document.getElementById('bubblePanelQuestion');
  const hint = document.getElementById('bubbleAnswerHint');
  const counter = document.getElementById('bubbleAnswerCount');
  const saveBtn = document.getElementById('btnSaveBubble');
  const feedback = document.getElementById('bubbleFeedback');
  const payload = window.bubblePayload || {};
  const answers = new Map();
  let activeNode = null;

  const getCsrfToken = () => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  };

  const normalizeLines = (value) => String(value || '')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  const updateCounter = () => {
    if (!input || !counter || !hint) return;
    const length = input.value.trim().length;
    counter.textContent = `${length}/120`;
    hint.classList.toggle('is-warning', length > 0 && length < 8);
    hint.textContent = length > 0 && length < 8
      ? 'Agrega un poco mas de contexto para que puntue mejor.'
      : 'Mínimo 8 caracteres. Ideal: 40 a 60.';
  };

  const renderAnswers = (node) => {
    const list = node.querySelector('.answer-list');
    if (!list) return;
    list.innerHTML = '';
    const nodeAnswers = answers.get(node.dataset.key) || [];
    node.classList.toggle('has-answers', nodeAnswers.length > 0);
    nodeAnswers.forEach((answer) => {
      const chip = document.createElement('span');
      chip.className = 'answer-chip';
      chip.textContent = answer;
      list.appendChild(chip);
    });
  };

  const closePanel = () => {
    if (!panel) return;
    panel.hidden = true;
    panel.classList.remove('is-open');
    nodes.forEach((node) => node.classList.remove('is-active'));
    activeNode = null;
  };

  const openPanel = (node) => {
    if (!panel || !input) return;
    activeNode = node;
    nodes.forEach((item) => item.classList.toggle('is-active', item === node));
    if (panelQuestion) {
      panelQuestion.textContent = node.dataset.label || 'Pregunta';
    }
    panel.hidden = false;
    panel.classList.add('is-open');
    panel.style.removeProperty('left');
    panel.style.removeProperty('top');
    input.value = '';
    updateCounter();
    window.requestAnimationFrame(() => input.focus({ preventScroll: true }));
  };

  const showMessage = (msg, type = 'info') => {
    if (!feedback) return;
    feedback.textContent = msg;
    feedback.classList.remove('error', 'success');
    if (type === 'error') feedback.classList.add('error');
    if (type === 'success') feedback.classList.add('success');
  };

  const collectResponses = () => {
    const respuestas = {};
    nodes.forEach((node) => {
      const key = node.dataset.key;
      respuestas[key] = (answers.get(key) || []).join('\n');
    });
    return respuestas;
  };

  nodes.forEach((node) => {
    const key = node.dataset.key;
    const seed = node.querySelector('.bubble-seed');
    answers.set(key, normalizeLines(seed ? seed.value : ''));
    renderAnswers(node);

    node.querySelector('.question-trigger')?.addEventListener('click', () => {
      if (activeNode === node && panel && !panel.hidden) {
        closePanel();
      } else {
        openPanel(node);
      }
    });
  });

  input?.addEventListener('input', updateCounter);

  panel?.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!activeNode || !input) return;
    const value = input.value.trim().replace(/\s+/g, ' ');
    if (value.length < 8) {
      showMessage('Escribe una respuesta de al menos 8 caracteres.', 'error');
      input.focus();
      return;
    }
    const key = activeNode.dataset.key;
    answers.set(key, [...(answers.get(key) || []), value]);
    renderAnswers(activeNode);
    showMessage('Respuesta agregada. Finaliza el mapa para guardar.', 'success');
    closePanel();
  });

  document.addEventListener('click', (event) => {
    if (!panel || panel.hidden) return;
    const clickedPanel = panel.contains(event.target);
    const clickedNode = event.target.closest('.spiral-question');
    if (!clickedPanel && !clickedNode) closePanel();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closePanel();
  });

  if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
      const respuestas = collectResponses();
      saveBtn.disabled = true;
      showMessage('Guardando mapa completo...');
      try {
        const res = await fetch(payload.saveUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({
            desafio_numero: payload.numero,
            respuestas,
          }),
        });
        const data = await res.json();
        if (!res.ok || !data.ok) {
          showMessage('No se pudo guardar. Inténtalo nuevamente.', 'error');
        } else {
          showMessage('Mapa guardado correctamente.', 'success');
          if (window.TokenCounter) {
            window.TokenCounter.addOnce('bubble-save', 6);
          }
          if (data.redirect_url) {
            window.location.href = data.redirect_url;
          }
        }
      } catch (error) {
        console.error(error);
        showMessage('Ocurrió un error al guardar.', 'error');
      } finally {
        saveBtn.disabled = false;
      }
    });
  }
})();
