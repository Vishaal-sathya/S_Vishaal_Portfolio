document.addEventListener("DOMContentLoaded", function() {
  const skillItems = document.querySelectorAll(".skill-item");

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
              entry.target.style.transition = "opacity 0.3s ease, transform 0.7s ease";
              observer.unobserve(entry.target);
          }
      });
  };

  const observer = new IntersectionObserver(observerCallback, observerOptions);

  skillItems.forEach(item => {
      observer.observe(item);
  });
});
