document.addEventListener("DOMContentLoaded", function() {
  // Intersection Observer for scroll animations
  const animItems = document.querySelectorAll(".skill-item, .project-card");

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
});
