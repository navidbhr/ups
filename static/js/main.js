document.addEventListener("DOMContentLoaded", function() {
    const header = document.getElementById("main-header");

    // انیمیشن منوی چسبان هنگام اسکرول
    window.addEventListener("scroll", function() {
        if (window.scrollY > 50) {
            header.classList.add("sticky");
        } else {
            header.classList.remove("sticky");
        }
    });

    // لاجیک ساده برای منوی موبایل (نسخه اولیه)
    const mobileToggle = document.querySelector(".mobile-menu-toggle");
    const mainNav = document.querySelector(".main-nav");

    if (mobileToggle) {
        mobileToggle.addEventListener("click", function() {
            mainNav.style.display = mainNav.style.display === "block" ? "none" : "block";
        });
    }
});