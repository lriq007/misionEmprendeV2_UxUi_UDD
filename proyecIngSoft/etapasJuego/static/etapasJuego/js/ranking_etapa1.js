(() => {
  const root = document.querySelector("[data-ranking-app]");
  if (!root) return;

  const rankingUrl = root.dataset.rankingApiUrl;
  const rankingList = root.querySelector("[data-ranking-list]");
  const rankingStatus = root.querySelector("[data-ranking-status]");

  function renderEntries(entries) {
    if (!rankingList) return;
    rankingList.innerHTML = "";

    entries.forEach((entry) => {
      const card = document.createElement("article");
      card.className = "stage1-ranking-card";
      card.dataset.teamEntry = "";
      card.dataset.teamId = String(entry.team_id);
      card.innerHTML = `
        <div>
          <p class="stage1-ranking-card__position">${entry.position ? `#${entry.position}` : "-"}</p>
          <h3>${entry.team_name}</h3>
        </div>
        <div class="stage1-ranking-card__meta">
          <strong>${entry.elapsed_label || "--:--"}</strong>
          <span>${entry.status_label}</span>
        </div>
      `;
      rankingList.appendChild(card);
    });
  }

  async function refreshRanking() {
    if (!rankingUrl) return;
    try {
      const response = await fetch(rankingUrl, { headers: { Accept: "application/json" } });
      if (!response.ok) return;
      const payload = await response.json();
      if (!payload.success) return;

      renderEntries(payload.teams || []);
      if (rankingStatus) {
        rankingStatus.textContent = payload.all_finished
          ? "Todos los equipos ya cerraron la etapa."
          : "Seguimos esperando a que las demás tabletas completen o cierren su tiempo.";
      }
    } catch (error) {
      // Ignore transient polling failures.
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    window.setInterval(refreshRanking, 3000);
  });
})();
