(function () {
  function closeDrawer(drawer) {
    if (!drawer) return;
    drawer.classList.remove("is-open");
    drawer.setAttribute("aria-hidden", "true");
    const triggerId = drawer.dataset.triggerId;
    if (triggerId) {
      document.getElementById(triggerId)?.focus({ preventScroll: true });
    }
  }

  function openDrawer(drawer, trigger) {
    if (!drawer) return;
    if (trigger && !trigger.id) {
      trigger.id = `story-trigger-${Math.random().toString(36).slice(2)}`;
    }
    if (trigger) drawer.dataset.triggerId = trigger.id;
    drawer.classList.add("is-open");
    drawer.setAttribute("aria-hidden", "false");
    drawer.querySelector("[data-story-close]")?.focus({ preventScroll: true });
  }

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-story-open]");
    if (trigger) {
      const target = document.querySelector(trigger.dataset.storyOpen);
      openDrawer(target, trigger);
      return;
    }

    const close = event.target.closest("[data-story-close]");
    if (close) {
      closeDrawer(close.closest("[data-story-drawer]"));
      return;
    }

    const drawer = event.target.closest("[data-story-drawer]");
    if (drawer && event.target === drawer) {
      closeDrawer(drawer);
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll("[data-story-drawer].is-open").forEach(closeDrawer);
  });
})();
