document.addEventListener("DOMContentLoaded", function() {
  // Intersection Observer for scroll animations
  const animItems = document.querySelectorAll(".skill-item, .project-card, .dashboard-card");

  const observerOptions = {
      root: null,
      rootMargin: "0px",
      threshold: 0.1
  };

  const observerCallback = (entries, observer) => {
      entries.forEach(entry => {
          if (entry.isIntersecting) {
              entry.target.style.opacity = 1;
              entry.target.style.transform = "translateY(0)";
              entry.target.style.transition = "opacity 0.5s ease, transform 0.8s ease";
              observer.unobserve(entry.target);
          }
      });
  };

  const observer = new IntersectionObserver(observerCallback, observerOptions);

  animItems.forEach(item => {
      observer.observe(item);
  });

  // Light/Dark Theme Toggle Logic
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    const currentTheme = localStorage.getItem("theme") || "light";
    
    // Set initial state matching cached theme
    if (currentTheme === "dark") {
      updateThemeIcon(themeToggle, "dark");
    }

    themeToggle.addEventListener("click", function(e) {
      e.preventDefault();
      document.body.classList.toggle("dark-mode");
      const theme = document.body.classList.contains("dark-mode") ? "dark" : "light";
      localStorage.setItem("theme", theme);
      updateThemeIcon(themeToggle, theme);
    });
  }

  function updateThemeIcon(btn, theme) {
    const svg = btn.querySelector(".theme-toggle-icon");
    if (!svg) return;
    if (theme === "dark") {
      svg.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
    } else {
      svg.innerHTML = `
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      `;
    }
  }
  // Experience Slider Logic
  const expSlides = document.querySelectorAll(".experience-slide");
  const prevBtn = document.getElementById("exp-prev-btn");
  const nextBtn = document.getElementById("exp-next-btn");
  const counter = document.getElementById("exp-counter");

  if (expSlides.length > 0 && prevBtn && nextBtn) {
    let currentSlide = 0;
    const totalSlides = expSlides.length;

    function updateSlider(index) {
      currentSlide = (index + totalSlides) % totalSlides;

      expSlides.forEach((slide, i) => {
        if (i === currentSlide) {
          slide.classList.add("active");
        } else {
          slide.classList.remove("active");
        }
      });

      if (counter) {
        const currentPadded = String(currentSlide + 1).padStart(2, "0");
        const totalPadded = String(totalSlides).padStart(2, "0");
        counter.textContent = `${currentPadded} / ${totalPadded}`;
      }
    }

    prevBtn.addEventListener("click", function(e) {
      e.preventDefault();
      updateSlider(currentSlide - 1);
    });

    nextBtn.addEventListener("click", function(e) {
      e.preventDefault();
      updateSlider(currentSlide + 1);
    });

    // Touch swipe support for mobile
    let touchStartX = 0;
    const slidesContainer = document.querySelector(".experience-slides");
    if (slidesContainer) {
      slidesContainer.addEventListener("touchstart", function(e) {
        touchStartX = e.changedTouches[0].screenX;
      }, { passive: true });

      slidesContainer.addEventListener("touchend", function(e) {
        const touchEndX = e.changedTouches[0].screenX;
        const diffX = touchStartX - touchEndX;
        if (Math.abs(diffX) > 40) {
          if (diffX > 0) {
            updateSlider(currentSlide + 1);
          } else {
            updateSlider(currentSlide - 1);
          }
        }
      }, { passive: true });
    }

    // Keyboard navigation
    const expSection = document.getElementById("experience");
    if (expSection) {
      expSection.addEventListener("keydown", function(e) {
        if (e.key === "ArrowLeft") {
          updateSlider(currentSlide - 1);
        } else if (e.key === "ArrowRight") {
          updateSlider(currentSlide + 1);
        }
      });
    }

    updateSlider(0);
  }

  // Analytics & Dashboards Filter Logic
  const filterBtns = document.querySelectorAll(".analytics-filter-btn");
  const dashboardCards = document.querySelectorAll(".dashboard-card");

  if (filterBtns.length > 0 && dashboardCards.length > 0) {
    filterBtns.forEach(btn => {
      btn.addEventListener("click", function() {
        filterBtns.forEach(b => b.classList.remove("active"));
        this.classList.add("active");

        const filter = this.getAttribute("data-filter");

        dashboardCards.forEach(card => {
          const category = card.getAttribute("data-category");
          if (filter === "all" || category === filter) {
            card.style.display = "flex";
            setTimeout(() => {
              card.style.opacity = "1";
              card.style.transform = "translateY(0)";
            }, 30);
          } else {
            card.style.opacity = "0";
            card.style.transform = "translateY(20px)";
            setTimeout(() => {
              card.style.display = "none";
            }, 250);
          }
        });
      });
    });
  }

  // Dashboard Fullscreen Modal Logic
  const dashModal = document.getElementById("dashboard-modal");
  const modalIframe = document.getElementById("modal-dashboard-iframe");
  const modalTitle = document.getElementById("modal-dashboard-title");
  const modalBadge = document.getElementById("modal-dashboard-badge");
  const modalNotice = document.getElementById("modal-placeholder-notice");
  const modalClose = document.getElementById("modal-close-btn");
  const modalBackdrop = document.querySelector(".dashboard-modal-backdrop");

  function openDashboardModal(card) {
    if (!dashModal) return;

    const viewport = card.querySelector(".dashboard-viewport");
    const titleEl = card.querySelector(".dashboard-title");
    const category = card.getAttribute("data-category");
    const embedUrl = viewport ? (viewport.getAttribute("data-embed-url") || "") : "";
    const title = titleEl ? titleEl.textContent.trim() : "Interactive Dashboard";

    if (modalTitle) modalTitle.textContent = title;

    if (modalBadge) {
      if (category === "powerbi") {
        modalBadge.textContent = "Power BI";
        modalBadge.className = "modal-dashboard-badge powerbi-tag";
      } else {
        modalBadge.textContent = "Excel";
        modalBadge.className = "modal-dashboard-badge excel-tag";
      }
    }

    if (embedUrl && (embedUrl.startsWith("http://") || embedUrl.startsWith("https://"))) {
      if (modalIframe) {
        modalIframe.src = embedUrl;
        modalIframe.style.display = "block";
      }
      if (modalNotice) modalNotice.style.display = "none";
    } else {
      if (modalIframe) {
        modalIframe.src = "";
        modalIframe.style.display = "none";
      }
      if (modalNotice) modalNotice.style.display = "block";
    }

    dashModal.classList.add("is-open");
    dashModal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeDashboardModal() {
    if (!dashModal) return;
    dashModal.classList.remove("is-open");
    dashModal.setAttribute("aria-hidden", "true");
    if (modalIframe) modalIframe.src = "";
    document.body.style.overflow = "";
  }

  document.querySelectorAll(".dashboard-fullscreen-btn, .preview-action-btn").forEach(btn => {
    btn.addEventListener("click", function(e) {
      e.preventDefault();
      e.stopPropagation();
      const card = this.closest(".dashboard-card");
      if (card) openDashboardModal(card);
    });
  });

  // Also clicking preview screen opens modal
  document.querySelectorAll(".dashboard-preview-screen").forEach(screen => {
    screen.addEventListener("click", function(e) {
      // If clicked inside the action button, event already caught
      const card = this.closest(".dashboard-card");
      if (card) openDashboardModal(card);
    });
  });

  if (modalClose) modalClose.addEventListener("click", closeDashboardModal);
  if (modalBackdrop) modalBackdrop.addEventListener("click", closeDashboardModal);

  document.addEventListener("keydown", function(e) {
    if (e.key === "Escape" && dashModal && dashModal.classList.contains("is-open")) {
      closeDashboardModal();
    }
  });
});

