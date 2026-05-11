// توابع تغییر زبان و تم
function changeLanguage(lang) {
    // ذخیره زبان در localStorage
    localStorage.setItem('selected_language', lang);

    // تغییر direction بر اساس زبان
    const html = document.documentElement;
    if (lang === 'en' || lang === 'ru') {
        html.setAttribute('dir', 'ltr');
        html.setAttribute('lang', lang);
    } else {
        html.setAttribute('dir', 'rtl');
        html.setAttribute('lang', lang);
    }

    // ارسال درخواست AJAX به endpoint تنظیم زبان Django
    fetch('/i18n/setlang/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({ language: lang })
    }).then(() => {
        // دریافت URL فعلی و حذف پارامتر lang قدیمی
        const url = new URL(window.location.href);
        url.searchParams.delete('lang');
        
        // ریلود صفحه برای اعمال تغییرات
        window.location.href = url.toString();
    });
}

// تابع کمکی برای دریافت CSRF token از کوکی‌ها
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// اعمال تم (تاریک/روشن)
function applyTheme(isDark) {
    if (isDark) {
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    }
}

// بررسی تم ذخیره شده هنگام لود صفحه
function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        applyTheme(true);
    } else {
        applyTheme(false);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // راه‌اندازی تم اولیه
    initTheme();

    // دکمه تغییر تم شناور
    const themeToggle = document.getElementById('theme-toggle');
    const headerThemeToggle = document.getElementById('header-theme-toggle');
    const mobileThemeToggle = document.getElementById('mobile-theme-toggle');

    function toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark');
        applyTheme(isDark);
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    if (headerThemeToggle) {
        headerThemeToggle.addEventListener('click', toggleTheme);
    }
    if (mobileThemeToggle) {
        mobileThemeToggle.addEventListener('click', toggleTheme);
    }

    // منوی موبایل
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // انیمیشن هدر هنگام اسکرول
    const header = document.querySelector('header');
    let lastScroll = 0;

    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }

        lastScroll = currentScroll;
    });
});
