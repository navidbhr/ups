// توابع تغییر زبان و تم
function changeLanguage(lang) {
    localStorage.setItem('selected_language', lang);

    const htmlEl = document.documentElement;
    if (lang === 'en' || lang === 'ru') {
        htmlEl.setAttribute('dir', 'ltr');
        htmlEl.setAttribute('lang', lang);
    } else {
        htmlEl.setAttribute('dir', 'rtl');
        htmlEl.setAttribute('lang', lang);
    }

    document.querySelectorAll('select[onchange*="changeLanguage"]').forEach(select => {
        select.value = lang;
    });

    const url = new URL(window.location.href);
    url.searchParams.delete('lang');
    url.searchParams.set('lang', lang);

    // واکشی دیتای جدید با پارامتر زبان
    fetch(url.toString(), {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html'
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

        // ۱. آپدیت کامل تگ هدر (شامل منوها، دکمه‌های CTA و جستجو)
        const newHeader = doc.querySelector('header');
        const currentHeader = document.querySelector('header');
        if (newHeader && currentHeader) {
            currentHeader.innerHTML = newHeader.innerHTML;
        }

        // ۲. آپدیت کامل بدنه اصلی (main)
        const newMain = doc.querySelector('main');
        const currentMain = document.querySelector('main');
        if (newMain && currentMain) {
            currentMain.innerHTML = newMain.innerHTML;

            // اجرای مجدد اسکریپت‌های درون main
            const scripts = currentMain.querySelectorAll('script');
            scripts.forEach(oldScript => {
                const newScript = document.createElement('script');
                Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                if (oldScript.innerHTML) newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                oldScript.parentNode.replaceChild(newScript, oldScript);
            });
        }

        // ۳. آپدیت کامل فوتر
        const newFooter = doc.querySelector('footer');
        const currentFooter = document.querySelector('footer');
        if (newFooter && currentFooter) {
            currentFooter.innerHTML = newFooter.innerHTML;
        }

        // ۴. مقداردهی مجدد پلاگین‌ها
        if (typeof AOS !== 'undefined') {
            document.querySelectorAll('[data-aos]').forEach(el => el.classList.remove('aos-animate'));
            AOS.init({ duration: 800, easing: 'ease-in-out', once: false, mirror: true, offset: 100 });
            setTimeout(() => AOS.refreshHard(), 100);
        }

        // ۵. راه‌اندازی مجدد رویدادهای جستجو و منوی موبایل چون هدر از نو نوشته شده است
        if (typeof initSearch === 'function') initSearch();

        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', function() {
                mobileMenu.classList.toggle('hidden');
            });
        }

        // تغییر تاریخچه مرورگر تا URL بدون رفرش آپدیت شود
        window.history.pushState({ lang: lang }, '', url.toString());
    })
    .catch(error => {
        console.error('خطا در تغییر زبان:', error);
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
    function toggleTheme() {
        const isDark = document.documentElement.classList.toggle('dark');
        applyTheme(isDark);
    }

    // استفاده از Event Delegation برای دکمه‌های تغییر تم
    document.addEventListener('click', function(e) {
        // چک می‌کنیم آیا کاربر روی دکمه‌های تم (یا المان‌های داخلشان مثل SVG) کلیک کرده یا نه
        const themeBtn = e.target.closest('#theme-toggle, #header-theme-toggle, #mobile-theme-toggle');

        if (themeBtn) {
            toggleTheme();
        }
    });

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
// جستجوی AJAX
let searchTimeout = null;
function initSearch() {
    const searchInput = document.getElementById('header-search-input');
    const searchDropdown = document.getElementById('search-results-dropdown');
    const searchLoading = document.getElementById('search-loading');
    
    if (!searchInput || !searchDropdown) return;
    
    // نمایش dropdown هنگام فوکوس
    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length > 0) {
            searchDropdown.classList.remove('hidden');
        }
    });
    
    // مخفی کردن dropdown هنگام کلیک بیرون
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
            searchDropdown.classList.add('hidden');
        }
    });
    
    // جستجو هنگام تایپ
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            searchDropdown.classList.add('hidden');
            return;
        }
        
        searchTimeout = setTimeout(function() {
            performSearch(query);
        }, 300);
    });
    
    function performSearch(query) {
        const currentLang = localStorage.getItem('selected_language') || 'fa';
        
        searchLoading.classList.remove('hidden');
        searchDropdown.classList.remove('hidden');
        
        // مخفی کردن همه بخش‌ها
        document.getElementById('search-products-section').classList.add('hidden');
        document.getElementById('search-categories-section').classList.add('hidden');
        document.getElementById('search-articles-section').classList.add('hidden');
        document.getElementById('search-projects-section').classList.add('hidden');
        document.getElementById('search-no-results').classList.add('hidden');
        
        // پاک کردن لیست‌ها
        document.getElementById('search-products-list').innerHTML = '';
        document.getElementById('search-categories-list').innerHTML = '';
        document.getElementById('search-articles-list').innerHTML = '';
        document.getElementById('search-projects-list').innerHTML = '';
        
        fetch(`/api/search/?q=${encodeURIComponent(query)}&lang=${currentLang}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            searchLoading.classList.add('hidden');
            
            let hasResults = false;
            
            // نمایش محصولات
            if (data.products && data.products.length > 0) {
                hasResults = true;
                const productsSection = document.getElementById('search-products-section');
                const productsList = document.getElementById('search-products-list');
                productsSection.classList.remove('hidden');
                
                data.products.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${item.url}" class="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                            ${item.image ? `<img src="${item.image}" alt="${item.title}" class="w-10 h-10 object-cover rounded">` : ''}
                            <span class="text-sm text-gray-900 dark:text-gray-100">${item.title}</span>
                        </a>
                    `;
                    productsList.appendChild(li);
                });
            }
            
            // نمایش دسته‌بندی‌ها
            if (data.categories && data.categories.length > 0) {
                hasResults = true;
                const categoriesSection = document.getElementById('search-categories-section');
                const categoriesList = document.getElementById('search-categories-list');
                categoriesSection.classList.remove('hidden');
                
                data.categories.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${item.url}" class="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                            ${item.image ? `<img src="${item.image}" alt="${item.title}" class="w-10 h-10 object-cover rounded">` : ''}
                            <span class="text-sm text-gray-900 dark:text-gray-100">${item.title}</span>
                        </a>
                    `;
                    categoriesList.appendChild(li);
                });
            }
            
            // نمایش مقالات
            if (data.articles && data.articles.length > 0) {
                hasResults = true;
                const articlesSection = document.getElementById('search-articles-section');
                const articlesList = document.getElementById('search-articles-list');
                articlesSection.classList.remove('hidden');
                
                data.articles.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${item.url}" class="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                            ${item.image ? `<img src="${item.image}" alt="${item.title}" class="w-10 h-10 object-cover rounded">` : ''}
                            <span class="text-sm text-gray-900 dark:text-gray-100">${item.title}</span>
                        </a>
                    `;
                    articlesList.appendChild(li);
                });
            }
            
            // نمایش پروژه‌ها
            if (data.projects && data.projects.length > 0) {
                hasResults = true;
                const projectsSection = document.getElementById('search-projects-section');
                const projectsList = document.getElementById('search-projects-list');
                projectsSection.classList.remove('hidden');
                
                data.projects.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <a href="${item.url}" class="flex items-center gap-3 px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                            ${item.image ? `<img src="${item.image}" alt="${item.title}" class="w-10 h-10 object-cover rounded">` : ''}
                            <span class="text-sm text-gray-900 dark:text-gray-100">${item.title}</span>
                        </a>
                    `;
                    projectsList.appendChild(li);
                });
            }
            
            // نمایش پیام بدون نتیجه
            if (!hasResults) {
                document.getElementById('search-no-results').classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            searchLoading.classList.add('hidden');
            searchDropdown.classList.add('hidden');
        });
    }
}

// اضافه کردن initSearch به DOMContentLoaded
const originalDOMContentLoaded = document.addEventListener.toString();
document.addEventListener("DOMContentLoaded", function() {
    initSearch();
});
