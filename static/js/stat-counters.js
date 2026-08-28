// GeoGuard AI — animated stat counters (index.html only)
// Counts each .stat-number[data-value] up from 0 when it scrolls into view.
// Safe to include on every page: does nothing if no matching elements exist.

document.addEventListener("DOMContentLoaded", function () {

    const counters = document.querySelectorAll(".stat-number[data-value]");
    if (!counters.length) return;

    const animateCounter = (el) => {
        const target = parseInt(el.getAttribute("data-value"), 10) || 0;
        const duration = 1500;
        const start = performance.now();

        const step = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            el.textContent = Math.floor(eased * target);

            if (progress < 1) {
                requestAnimationFrame(step);
            } else {
                el.textContent = target;
            }
        };

        requestAnimationFrame(step);
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.4 });

    counters.forEach((counter) => observer.observe(counter));

});