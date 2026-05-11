from .models import SiteSettings, Category, PageTranslation, Branch


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
        return ''


def site_settings(request):
    from django.utils.translation import get_language
    
    current_lang = get_language() or 'fa'
    
    # تبدیل کد زبان به فرمت مورد استفاده در مدل (fa, en, ar, ru)
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
    }
    lang = lang_map.get(current_lang.lower(), 'fa')
    
    main_branch = Branch.objects.filter(is_main=True, is_active=True).first()
    if not main_branch:
        main_branch = Branch.objects.filter(is_active=True).first()
    
    return {
        'settings': SiteSettings.objects.first(),
        'main_branch': main_branch,
        'categories': Category.objects.filter(parent__isnull=True),
        'current_lang': lang,
    }
