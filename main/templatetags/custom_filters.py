from django import template
from django.contrib.humanize.templatetags.humanize import intcomma as django_intcomma
from main.models import PageTranslation, StaticText

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def intcomma(value):
    """Add comma to numbers"""
    return django_intcomma(value)


@register.simple_tag(takes_context=True)
def get_text(context, key):
    """دریافت متن از دیتابیس بر اساس کلید و زبان فعلی"""
    from django.utils.translation import get_language
    
    lang = context.get('current_lang', 'fa')
    if not lang:
        lang = get_language() or 'fa'
    
    # تبدیل کد زبان به فرمت کوتاه
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'en': 'en',
        'ar': 'ar',
        'ru': 'ru',
    }
    lang = lang_map.get(lang.lower(), 'fa')
    
    # اول در مدل StaticText جستجو کن
    text = StaticText.get_text(key, lang)
    if text and text != key:
        return text
    
    # اگر نبود، در PageTranslation جستجو کن
    try:
        translation = PageTranslation.objects.get(key=key)
        field_name = f'text_{lang}'
        text = getattr(translation, field_name, None)
        if not text and lang != 'fa':
            text = getattr(translation, 'text_fa', '')
        return text or ''
    except PageTranslation.DoesNotExist:
        return ''
