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
        // دریافت URL فعلی و حذف پارامتر lang قدیمی
        const url = new URL(window.location.href);
        url.searchParams.delete('lang');
        
        // اضافه کردن پارامتر lang جدید به URL برای ویو
        url.searchParams.set('lang', lang);
        
        // فچ کردن محتوای جدید فقط برای بخش اصلی صفحه
        fetch(url.toString(), {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html fragment'
            }
        })
        .then(response => response.text())
        .then(html => {
            // استخراج فقط بخش main content از پاسخ
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMain = doc.querySelector('main') || doc.querySelector('body');
            const currentMain = document.querySelector('main') || document.querySelector('body');
            
            if (newMain && currentMain) {
                // حفظ هدر و فوتر - فقط محتوای داخل main عوض شود
                currentMain.innerHTML = newMain.innerHTML;
                
                // اجرای مجدد اسکریپت‌های داخل محتوای جدید
                const scripts = currentMain.querySelectorAll('script');
                scripts.forEach(oldScript => {
                    const newScript = document.createElement('script');
                    Array.from(oldScript.attributes).forEach(attr => {
                        newScript.setAttribute(attr.name, attr.value);
                    });
                    if (oldScript.innerHTML.trim()) {
                        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                    }
                    oldScript.parentNode.replaceChild(newScript, oldScript);
                });
                
                // اجرای مجدد AOS برای انیمیشن‌ها
                if (typeof AOS !== 'undefined') {
                    AOS.refresh();
                }
                
                // بروزرسانی سلکتورهای زبان
                document.querySelectorAll('select[onchange*="changeLanguage"]').forEach(select => {
                    select.value = lang;
                });
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
            
            // به‌روزرسانی URL بدون ریلود
            window.history.pushState({ lang: lang }, '', url.toString());
        })
        .catch(error => {
            console.log('Error fetching content:', error);
            // در صورت خطا، ریلود معمولی انجام می‌شود
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
