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

  const closeOnBackdrop = (dialog) => {
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) {
        dialog.close();
      }
    });
  };

  const wireDialogClose = (dialog) => {
    dialog.querySelectorAll("[data-ia-dialog-close]").forEach((button) => {
      button.addEventListener("click", () => dialog.close());
    });
    closeOnBackdrop(dialog);
  };

  const dialogSupported = typeof HTMLDialogElement !== "undefined";

  if (dialogSupported) {
    const detailCards = Array.from(document.querySelectorAll("[data-ia-detail-card]"));

    if (detailCards.length) {
      const detailDialog = document.createElement("dialog");
      detailDialog.className = "ia-detail-dialog";
      detailDialog.innerHTML = `
        <div class="ia-detail-dialog-shell">
          <button class="ia-dialog-close" type="button" aria-label="Zavřít detail" data-ia-dialog-close>×</button>
          <div class="ia-detail-dialog-content ia-prose" data-ia-detail-dialog-content></div>
        </div>
      `;
      document.body.appendChild(detailDialog);
      wireDialogClose(detailDialog);

      let detailReturnFocus = null;

      detailDialog.addEventListener("close", () => {
        if (detailReturnFocus) {
          detailReturnFocus.focus();
          detailReturnFocus = null;
        }
      });

      detailCards.forEach((card) => {
        const button = card.querySelector("[data-ia-detail-open]");
        const content = card.querySelector("[data-ia-detail-content]");

        if (!button || !content) {
          return;
        }

        content.hidden = true;
        button.setAttribute("aria-haspopup", "dialog");

        button.addEventListener("click", () => {
          detailReturnFocus = button;
          detailDialog.querySelector("[data-ia-detail-dialog-content]").innerHTML = content.innerHTML;
          detailDialog.showModal();
        });
      });
    }

    const imagePattern = /\.(avif|gif|jpe?g|png|svg|webp)(?:[?#].*)?$/i;
    const imageLinks = Array.from(document.querySelectorAll(".ia-figure a"));

    if (imageLinks.length) {
      const lightbox = document.createElement("dialog");
      lightbox.className = "ia-lightbox-dialog";
      lightbox.innerHTML = `
        <div class="ia-lightbox-shell">
          <button class="ia-dialog-close" type="button" aria-label="Zavřít obrázek" data-ia-dialog-close>×</button>
          <div class="ia-lightbox-toolbar" aria-label="Ovládání obrázku">
            <button class="ia-lightbox-zoom" type="button" data-ia-lightbox-zoom>Přiblížit</button>
          </div>
          <div class="ia-lightbox-viewport" data-ia-lightbox-viewport>
            <img class="ia-lightbox-img" alt="" data-ia-lightbox-image>
          </div>
          <p class="ia-lightbox-caption" data-ia-lightbox-caption></p>
        </div>
      `;
      document.body.appendChild(lightbox);
      wireDialogClose(lightbox);

      let lightboxReturnFocus = null;
      let lightboxZoomValue = 1;
      let lightboxBaseWidth = 0;
      let isLightboxPanning = false;
      let lightboxPanMoved = false;
      let lightboxPanStartX = 0;
      let lightboxPanStartY = 0;
      let lightboxPanStartLeft = 0;
      let lightboxPanStartTop = 0;
      let pinchStartDistance = 0;
      let pinchStartZoom = 1;
      const activePointers = new Map();
      const lightboxImage = lightbox.querySelector("[data-ia-lightbox-image]");
      const lightboxViewport = lightbox.querySelector("[data-ia-lightbox-viewport]");
      const lightboxZoom = lightbox.querySelector("[data-ia-lightbox-zoom]");

      const clampZoom = (zoom) => Math.min(3, Math.max(1, zoom));

      const updateLightboxBaseWidth = () => {
        if (lightboxZoomValue === 1) {
          lightboxBaseWidth = lightboxImage.clientWidth || lightboxImage.naturalWidth || lightboxBaseWidth;
        }
      };

      const setLightboxZoom = (zoom, origin) => {
        updateLightboxBaseWidth();

        const previousScrollWidth = lightboxViewport.scrollWidth;
        const previousScrollHeight = lightboxViewport.scrollHeight;
        const viewportRect = lightboxViewport.getBoundingClientRect();
        const originX = origin ? origin.clientX - viewportRect.left : lightboxViewport.clientWidth / 2;
        const originY = origin ? origin.clientY - viewportRect.top : lightboxViewport.clientHeight / 2;
        const ratioX = previousScrollWidth ? (lightboxViewport.scrollLeft + originX) / previousScrollWidth : 0.5;
        const ratioY = previousScrollHeight ? (lightboxViewport.scrollTop + originY) / previousScrollHeight : 0.5;

        lightboxZoomValue = clampZoom(zoom);
        const isZoomed = lightboxZoomValue > 1.01;
        lightbox.classList.toggle("is-zoomed", isZoomed);
        lightboxZoom.textContent = isZoomed ? `Zoom ${lightboxZoomValue.toFixed(1)}×` : "Přiblížit";
        lightboxZoom.setAttribute("aria-label", "Změnit přiblížení obrázku");

        if (isZoomed) {
          const baseWidth = lightboxBaseWidth || lightboxImage.clientWidth || lightboxImage.naturalWidth;
          lightboxImage.style.width = `${Math.round(baseWidth * lightboxZoomValue)}px`;
          lightboxImage.style.maxWidth = "none";
          lightboxImage.style.maxHeight = "none";
        } else {
          lightboxZoomValue = 1;
          lightboxImage.style.width = "";
          lightboxImage.style.maxWidth = "";
          lightboxImage.style.maxHeight = "";
          lightboxViewport.scrollTo({ top: 0, left: 0 });
          updateLightboxBaseWidth();
        }

        window.requestAnimationFrame(() => {
          if (!isZoomed) {
            return;
          }

          lightboxViewport.scrollLeft = Math.max(0, lightboxViewport.scrollWidth * ratioX - originX);
          lightboxViewport.scrollTop = Math.max(0, lightboxViewport.scrollHeight * ratioY - originY);
        });
      };

      const cycleLightboxZoom = () => {
        if (lightboxZoomValue >= 2.95) {
          setLightboxZoom(1);
        } else {
          setLightboxZoom(lightboxZoomValue + 0.5);
        }
      };

      const pointerDistance = (first, second) => Math.hypot(first.clientX - second.clientX, first.clientY - second.clientY);

      const pointerMidpoint = (first, second) => ({
        clientX: (first.clientX + second.clientX) / 2,
        clientY: (first.clientY + second.clientY) / 2,
      });

      const endLightboxPan = () => {
        isLightboxPanning = false;
        lightboxViewport.classList.remove("is-panning");
      };

      lightbox.addEventListener("close", () => {
        lightboxImage.removeAttribute("src");
        setLightboxZoom(1);
        lightboxBaseWidth = 0;
        activePointers.clear();
        endLightboxPan();
        if (lightboxReturnFocus) {
          lightboxReturnFocus.focus();
          lightboxReturnFocus = null;
        }
      });

      lightboxZoom.addEventListener("click", cycleLightboxZoom);
      lightboxImage.addEventListener("click", (event) => {
        if (lightboxPanMoved) {
          event.preventDefault();
          lightboxPanMoved = false;
          return;
        }

        cycleLightboxZoom();
      });
      lightboxImage.addEventListener("load", () => {
        updateLightboxBaseWidth();
        setLightboxZoom(lightboxZoomValue);
      });
      lightboxViewport.addEventListener("wheel", (event) => {
        event.preventDefault();
        const zoomFactor = event.deltaY < 0 ? 1.12 : 0.88;
        setLightboxZoom(lightboxZoomValue * zoomFactor, event);
      }, { passive: false });
      lightboxViewport.addEventListener("pointerdown", (event) => {
        activePointers.set(event.pointerId, event);

        if (activePointers.size === 2) {
          const pointers = Array.from(activePointers.values());
          pinchStartDistance = pointerDistance(pointers[0], pointers[1]);
          pinchStartZoom = lightboxZoomValue;
          endLightboxPan();
          event.preventDefault();
          return;
        }

        if (lightboxZoomValue <= 1.01 || event.button !== 0) {
          return;
        }

        isLightboxPanning = true;
        lightboxPanMoved = false;
        lightboxPanStartX = event.clientX;
        lightboxPanStartY = event.clientY;
        lightboxPanStartLeft = lightboxViewport.scrollLeft;
        lightboxPanStartTop = lightboxViewport.scrollTop;
        lightboxViewport.classList.add("is-panning");
        lightboxViewport.setPointerCapture(event.pointerId);
        event.preventDefault();
      });
      lightboxViewport.addEventListener("pointermove", (event) => {
        if (activePointers.has(event.pointerId)) {
          activePointers.set(event.pointerId, event);
        }

        if (activePointers.size === 2 && pinchStartDistance) {
          const pointers = Array.from(activePointers.values());
          const distance = pointerDistance(pointers[0], pointers[1]);
          setLightboxZoom(pinchStartZoom * (distance / pinchStartDistance), pointerMidpoint(pointers[0], pointers[1]));
          event.preventDefault();
          return;
        }

        if (!isLightboxPanning) {
          return;
        }

        if (Math.abs(event.clientX - lightboxPanStartX) > 3 || Math.abs(event.clientY - lightboxPanStartY) > 3) {
          lightboxPanMoved = true;
        }
        lightboxViewport.scrollLeft = lightboxPanStartLeft - (event.clientX - lightboxPanStartX);
        lightboxViewport.scrollTop = lightboxPanStartTop - (event.clientY - lightboxPanStartY);
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach((eventName) => {
        lightboxViewport.addEventListener(eventName, (event) => {
          activePointers.delete(event.pointerId);
          if (activePointers.size < 2) {
            pinchStartDistance = 0;
          }
          if (eventName !== "pointerleave" || isLightboxPanning) {
            endLightboxPan();
          }
        });
      });
      lightbox.addEventListener("keydown", (event) => {
        if (event.key === "+" || event.key === "=") {
          event.preventDefault();
          setLightboxZoom(lightboxZoomValue + 0.25);
        } else if (event.key === "-" || event.key === "_") {
          event.preventDefault();
          setLightboxZoom(lightboxZoomValue - 0.25);
        }
      });

      imageLinks.forEach((link) => {
        const image = link.querySelector("img.ia-image");
        const href = link.getAttribute("href");

        if (!image || !href || !imagePattern.test(href)) {
          return;
        }

        link.addEventListener("click", (event) => {
          event.preventDefault();
          lightboxReturnFocus = link;

          const caption = lightbox.querySelector("[data-ia-lightbox-caption]");
          const figureCaption = link.closest(".ia-figure")?.querySelector("figcaption");

          setLightboxZoom(1);
          lightboxImage.src = href;
          lightboxImage.alt = image.alt || "";
          caption.textContent = figureCaption?.textContent || "";
          caption.hidden = !caption.textContent;
          lightbox.showModal();
          window.requestAnimationFrame(() => {
            updateLightboxBaseWidth();
            setLightboxZoom(1);
          });
        });
      });
    }
  }
})();
