(() => {
  document.documentElement.classList.add("ia-js");

  const root = document.documentElement;
  const storageKey = "interactive-article-theme";

  const getStoredTheme = () => {
    try {
      return localStorage.getItem(storageKey);
    } catch {
      return null;
    }
  };

  const storeTheme = (theme) => {
    try {
      localStorage.setItem(storageKey, theme);
    } catch {
      // Storage can be unavailable in private or embedded contexts; the visible theme still changes.
    }
  };

  const updateThemeButtons = (theme) => {
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      button.textContent = theme === "dark" ? "Světlý režim" : "Tmavý režim";
      button.setAttribute("aria-label", theme === "dark" ? "Přepnout na světlý režim" : "Přepnout na tmavý režim");
    });
  };

  const applyTheme = (theme, persist = true) => {
    root.setAttribute("data-theme", theme);
    updateThemeButtons(theme);
    if (persist) {
      storeTheme(theme);
    }
  };

  const initialTheme = getStoredTheme() || root.getAttribute("data-theme") || "light";
  applyTheme(initialTheme, false);

  document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
    button.addEventListener("click", () => {
      const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
    });
  });

  document.querySelectorAll("[data-ia-card]").forEach((card) => {
    const button = card.querySelector("[data-ia-card-button]");
    const panel = card.querySelector("[data-ia-card-panel]");
    if (!button || !panel) {
      return;
    }

    const setOpen = (open) => {
      card.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", String(open));
    };

    setOpen(button.getAttribute("aria-expanded") === "true" || card.classList.contains("is-open"));
    button.addEventListener("click", () => setOpen(!card.classList.contains("is-open")));
  });

  document.querySelectorAll("[data-expand-all]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-ia-card]").forEach((card) => {
        const control = card.querySelector("[data-ia-card-button]");
        card.classList.add("is-open");
        if (control) {
          control.setAttribute("aria-expanded", "true");
        }
      });
    });
  });

  document.querySelectorAll("[data-collapse-all]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll("[data-ia-card]").forEach((card) => {
        const control = card.querySelector("[data-ia-card-button]");
        card.classList.remove("is-open");
        if (control) {
          control.setAttribute("aria-expanded", "false");
        }
      });
    });
  });

  document.querySelectorAll("[data-ia-reveal]").forEach((reveal) => {
    const button = reveal.querySelector("[data-ia-reveal-button]");
    if (!button) {
      return;
    }

    const setOpen = (open) => {
      reveal.classList.toggle("is-open", open);
      button.setAttribute("aria-expanded", String(open));
    };

    setOpen(button.getAttribute("aria-expanded") === "true" || reveal.classList.contains("is-open"));
    button.addEventListener("click", () => setOpen(!reveal.classList.contains("is-open")));
  });

  document.querySelectorAll("[data-ia-tabs]").forEach((tabs) => {
    const tabButtons = Array.from(tabs.querySelectorAll("[role='tab']"));
    const panels = Array.from(tabs.querySelectorAll("[role='tabpanel']"));

    const selectTab = (selected) => {
      tabButtons.forEach((tab) => {
        const isSelected = tab === selected;
        tab.setAttribute("aria-selected", String(isSelected));
        tab.tabIndex = isSelected ? 0 : -1;
      });

      panels.forEach((panel) => {
        panel.hidden = panel.id !== selected.getAttribute("aria-controls");
      });
    };

    tabButtons.forEach((tab, index) => {
      tab.addEventListener("click", () => selectTab(tab));
      tab.addEventListener("keydown", (event) => {
        const direction = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
        if (!direction) {
          return;
        }

        event.preventDefault();
        const next = tabButtons[(index + direction + tabButtons.length) % tabButtons.length];
        selectTab(next);
        next.focus();
      });
    });

    selectTab(tabButtons.find((tab) => tab.getAttribute("aria-selected") === "true") || tabButtons[0]);
  });
})();
