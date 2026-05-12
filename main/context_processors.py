from .models import SiteSettings, Category, PageTranslation, Branch, StaticText


def get_text_by_key(key, lang='fa'):
    """دریافت متن بر اساس کلید و زبان"""
    try:
        translation = PageTranslation.objects.get(key=key)
        field_name = f'text_{lang}'
        text = getattr(translation, field_name, None)
        if not text and lang != 'fa':
            text = getattr(translation, 'text_fa', '')
        return text or ''
    except PageTranslation.DoesNotExist:
        # اگر PageTranslation نبود، StaticText را چک کن
        try:
            static = StaticText.objects.get(key=key)
            field_name = f'text_{lang}'
            text = getattr(static, field_name, None)
            if not text and lang != 'fa':
                text = getattr(static, 'text_fa', '')
            return text or static.default_text or key
        except StaticText.DoesNotExist:
            return ''


def site_settings(request):
    from django.utils.translation import get_language

    # اولویت‌بندی برای تشخیص زبان:
    # 1. زبان تنظیم شده در session توسط middleware
    # 2. زبان فعلی Django
    # 3. پیش‌فرض fa
    current_lang = getattr(request, 'LANGUAGE_CODE', None) or get_language() or 'fa'

    # تبدیل کد زبان به فرمت مورد استفاده در مدل (fa, en, ar, ru)
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'en': 'en',
        'fa': 'fa',
        'ar': 'ar',
        'ru': 'ru',
    }
    lang = lang_map.get(current_lang.lower(), 'fa')

    main_branch = Branch.objects.filter(is_main=True, is_active=True).first()
    if not main_branch:
        main_branch = Branch.objects.filter(is_active=True).first()

    # دریافت تنظیمات سایت
    settings_obj = SiteSettings.objects.first()

    # اگر settings_obj نبود، یک آبجکت خالی با مقادیر پیش‌فرض بساز
    if not settings_obj:
        class EmptySettings:
            hero_title = ''
            hero_subtitle = ''
            cta_text = ''
            cta_link = '#consultation'
            site_name = 'برهان یو پی اس'
            site_title = 'برهان یو پی اس'
            site_description = 'مشاوره و خرید انواع دستگاه‌های یو پی اس صنعتی و خانگی با گارانتی معتبر.'
            def get_hero_title(self, lang_code='fa'): return ''
            def get_hero_subtitle(self, lang_code='fa'): return ''
            def get_cta_text(self, lang_code='fa'): 
                from .models import StaticText
                return StaticText.get_text('cta_text', lang_code) or ''
        settings_obj = EmptySettings()
    else:
        # اضافه کردن متد get_cta_text به تنظیمات موجود برای اطمینان از لود چندزبانه
        def get_cta_text(lang_code='fa'):
            from .models import StaticText
            return StaticText.get_text('cta_text', lang_code) or settings_obj.cta_text or ''
        # Monkey patch
        settings_obj.get_cta_text = get_cta_text

    # دریافت تمام متون استاتیک مورد نیاز برای قالب
    static_texts = {}
    for key in [
        'hero_title', 'hero_subtitle', 'cta_text',
        'hero_stats_experience', 'hero_stats_projects', 'hero_stats_customers',
        'hero_badge_warranty', 'hero_badge_warranty_value', 'hero_badge_support', 'hero_badge_support_value',
        'categories_title', 'categories_subtitle',
        'view_products', 'category_placeholder_title', 'category_placeholder_desc',
        'products_title', 'products_subtitle', 'contact_us', 'details', 'view_details',
        'product_placeholder_price', 'product_placeholder_title', 'product_placeholder_desc',
        'view_all_products',
        'articles_title', 'articles_subtitle', 'read_more', 'article_placeholder_title', 'article_placeholder_desc',
        'projects_title', 'projects_subtitle', 'project_placeholder_title', 'project_placeholder_location', 'project_placeholder_desc',
        'partners_title', 'partners_subtitle', 'partner_placeholder',
        'consultation_title', 'consultation_subtitle', 'whatsapp',
        'contact_title', 'contact_subtitle',
        'form_name_label', 'form_name_placeholder',
        'form_phone_label', 'form_phone_placeholder',
        'form_company_label', 'form_company_placeholder',
        'form_power_label', 'form_power_placeholder',
        'form_message_label', 'form_message_placeholder',
        'form_submit',
        'contact_info_title', 'contact_address_label', 'contact_phone_label', 'contact_email_label',
        'not_in_stock',
        'footer_about', 'footer_quick_links', 'footer_contact_info', 'footer_location', 'google_map', 'footer_copyright',
        'main_branch', 'send_message',
        'home_menu_home', 'home_menu_categories', 'home_menu_products', 'home_menu_articles', 'home_menu_projects', 'home_menu_contact',
        'search_placeholder', 'no_results',
    ]:
        static_texts[key] = get_text_by_key(key, lang)

    return {
        'settings': settings_obj,
        'main_branch': main_branch,
        'categories': Category.objects.filter(parent__isnull=True),
        'current_lang': lang,
        'static_texts': static_texts,
        'get_text': lambda key: get_text_by_key(key, lang),
    }