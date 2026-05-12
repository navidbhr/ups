// توابع تغییر زبان و تم
function changeLanguage(lang) {
    // ذخیره زبان در localStorage
    localStorage.setItem('selected_language', lang);

    // تغییر direction بر اساس زبان
    const htmlEl = document.documentElement;
    if (lang === 'en' || lang === 'ru') {
        htmlEl.setAttribute('dir', 'ltr');
        htmlEl.setAttribute('lang', lang);
    } else {
        htmlEl.setAttribute('dir', 'rtl');
        htmlEl.setAttribute('lang', lang);
    }

    // به‌روزرسانی تمام سلکتورهای زبان در صفحه
    document.querySelectorAll('select[onchange*="changeLanguage"]').forEach(select => {
        select.value = lang;
    });

    // ارسال درخواست AJAX به endpoint تنظیم زبان Django
    fetch('/i18n/setlang/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: new URLSearchParams({ language: lang })
    }).then(() => {
        const url = new URL(window.location.href);
        url.searchParams.delete('lang');
        url.searchParams.set('lang', lang);
        
        fetch(url.toString(), {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html fragment'
            }
        })
        .then(response => response.text())
        .then(html => {
            if (!html || !html.trim()) {
                window.location.href = url.toString();
                return;
            }

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMain = doc.querySelector('main') || doc.querySelector('body');
            const currentMain = document.querySelector('main') || document.querySelector('body');
            
            if (newMain && currentMain && newMain.innerHTML.trim()) {
                currentMain.innerHTML = newMain.innerHTML;
                
                // اجرای مجدد اسکریپت‌های داخل محتوای جدید
                const scripts = currentMain.querySelectorAll('script');
                scripts.forEach(oldScript => {
                    const newScript = document.createElement('script');
                    Array.from(oldScript.attributes).forEach(attr => {
                        newScript.setAttribute(attr.name, attr.value);
                    });
                    if (oldScript.innerHTML) {
                        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                    }
                    oldScript.parentNode.replaceChild(newScript, oldScript);
                });
                
                // مقداردهی مجدد کامل انیمیشن‌های AOS
                // استفاده از init مجدد بجای refresh تا المان‌های جدید DOM شناسایی شوند
                if (typeof AOS !== 'undefined') {
                    // اول کلاس‌های قدیمی که باعث مخفی ماندن میشوند را حذف میکنیم
                    document.querySelectorAll('[data-aos]').forEach(el => {
                        el.classList.remove('aos-animate');
                    });
                    
                    // راه‌اندازی مجدد برای اعمال به المان‌های جدید
                    AOS.init({
                        duration: 800,
                        easing: 'ease-in-out',
                        once: false,
                        mirror: true,
                        offset: 100,
                    });
                    
                    // فراخوانی refreshHard برای اطمینان از اعمال تغییرات
                    setTimeout(() => {
                        AOS.refreshHard();
                    }, 100);
                }

                // به‌روزرسانی دکمه‌های CTA در هدر
                const newCtaDesktop = doc.querySelector('#header-cta-link');
                const newCtaMobile = doc.querySelector('#mobile-cta-link');
                const currentCtaDesktop = document.querySelector('#header-cta-link');
                const currentCtaMobile = document.querySelector('#mobile-cta-link');
                
                if (newCtaDesktop && currentCtaDesktop) {
                    currentCtaDesktop.textContent = newCtaDesktop.textContent;
                    currentCtaDesktop.href = newCtaDesktop.href;
                }
                if (newCtaMobile && currentCtaMobile) {
                    currentCtaMobile.textContent = newCtaMobile.textContent;
                    currentCtaMobile.href = newCtaMobile.href;
                }
                
                // به‌روزرسانی منوی موبایل لینک‌ها
                const newMobileMenu = doc.querySelector('#mobile-menu');
                const currentMobileMenu = document.querySelector('#mobile-menu');
                if (newMobileMenu && currentMobileMenu) {
                    currentMobileMenu.innerHTML = newMobileMenu.innerHTML;
                }
                
                window.history.pushState({ lang: lang }, '', url.toString());
            } else {
                window.location.href = url.toString();
            }
        })
        .catch(error => {
            console.error('Error fetching content:', error);
            window.location.href = url.toString();
        });
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