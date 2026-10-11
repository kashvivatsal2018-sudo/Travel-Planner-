/**
 * Main Application JavaScript: Mobile menu, alerts, and navigation state.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Mobile Menu Toggle
    const toggleBtn = document.getElementById("mobileMenuToggle");
    const navMenu = document.getElementById("navMenu");

    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener("click", () => {
            navMenu.classList.toggle("show");
            const icon = toggleBtn.querySelector("i");
            if (navMenu.classList.contains("show")) {
                icon.classList.remove("fa-bars");
                icon.classList.add("fa-xmark");
            } else {
                icon.classList.remove("fa-xmark");
                icon.classList.add("fa-bars");
            }
        });
    }

    // 2. Active Navigation Link Detection
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".nav-link");
    navLinks.forEach(link => {
        const href = link.getAttribute("href");
        if (href === currentPath || (href !== "/" && currentPath.startsWith(href))) {
            link.classList.add("active");
        }
    });

    // 3. Auto-Dismiss Flash Alerts after 6 seconds
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 400);
        }, 6000);
    });

    // 4. Questionnaire Selected Chips Counter
    const visitedChips = document.querySelectorAll("input[name='visited_destinations']");
    const visitedCounter = document.getElementById("visitedCountDisplay");
    if (visitedChips.length > 0 && visitedCounter) {
        const updateCounter = () => {
            const checkedCount = document.querySelectorAll("input[name='visited_destinations']:checked").length;
            visitedCounter.textContent = `${checkedCount} selected`;
        };
        visitedChips.forEach(chip => chip.addEventListener("change", updateCounter));
        updateCounter();
    }
});
