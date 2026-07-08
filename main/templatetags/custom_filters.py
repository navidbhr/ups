from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma as django_intcomma
from django.utils.safestring import mark_safe
from main.models import PageTranslation, StaticText

register = template.Library()


SAFE_HTML_TAGS = {
    'a', 'b', 'blockquote', 'br', 'code', 'del', 'em', 'figcaption', 'figure',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p',
    'pre', 's', 'span', 'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot',
    'th', 'thead', 'tr', 'u', 'ul',
}
VOID_HTML_TAGS = {'br', 'hr', 'img'}
DANGEROUS_HTML_TAGS = {
    'script', 'style', 'iframe', 'object', 'embed', 'svg', 'math', 'form',
    'input', 'button', 'textarea', 'select', 'link', 'meta',
}
SAFE_HTML_ATTRS = {
    '*': {'class', 'dir', 'title'},
    'a': {'href', 'title', 'target'},
    'img': {'src', 'alt', 'title', 'width', 'height', 'loading'},
    'td': {'colspan', 'rowspan'},
    'th': {'colspan', 'rowspan', 'scope'},
}
SAFE_LINK_URL_SCHEMES = {'http', 'https', 'mailto', 'tel'}
SAFE_MEDIA_URL_SCHEMES = {'http', 'https'}
SAFE_IFRAME_HOSTS = {'google.com', 'www.google.com', 'maps.google.com'}


def _is_safe_url(value, allowed_schemes):
    value = (value or '').strip()
    if not value:
        return False
    parsed = urlparse(value)
    if not parsed.scheme:
        return not parsed.netloc
    return parsed.scheme.lower() in allowed_schemes


def _is_safe_google_maps_url(value):
    parsed = urlparse((value or '').strip())
    host = parsed.netloc.lower()
    return (
        parsed.scheme == 'https'
        and host in SAFE_IFRAME_HOSTS
        and (parsed.path == '/maps' or parsed.path.startswith('/maps/'))
    )


class SafeHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in DANGEROUS_HTML_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth or tag not in SAFE_HTML_TAGS:
            return

        allowed_attrs = SAFE_HTML_ATTRS.get('*', set()) | SAFE_HTML_ATTRS.get(tag, set())
        rendered_attrs = []
        for name, value in attrs:
            name = name.lower()
            value = value or ''
            if name not in allowed_attrs:
                continue
            if name == 'href' and not _is_safe_url(value, SAFE_LINK_URL_SCHEMES):
                continue
            if name == 'src' and not _is_safe_url(value, SAFE_MEDIA_URL_SCHEMES):
                continue
            if name == 'target' and value not in {'_blank', '_self'}:
                continue
            rendered_attrs.append(f'{name}="{escape(value, quote=True)}"')

        if tag == 'a' and any(attr.startswith('target="_blank"') for attr in rendered_attrs):
            rendered_attrs.append('rel="noopener noreferrer"')

        attrs_text = f" {' '.join(rendered_attrs)}" if rendered_attrs else ''
        self.parts.append(f'<{tag}{attrs_text}>')

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in DANGEROUS_HTML_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth or tag not in SAFE_HTML_TAGS or tag in VOID_HTML_TAGS:
            return
        self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(escape(data))


class GoogleMapsIframeParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.iframe_attrs = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'iframe' and self.iframe_attrs is None:
            self.iframe_attrs = {name.lower(): value for name, value in attrs}


@register.filter
def sanitize_html(value):
    """Render a conservative subset of editor HTML without executable content."""
    parser = SafeHTMLParser()
    parser.feed(value or '')
    parser.close()
    return mark_safe(''.join(parser.parts))


@register.filter
def safe_map_iframe(value):
    """Render only Google Maps iframe embeds; drop anything else."""
    parser = GoogleMapsIframeParser()
    parser.feed(value or '')
    parser.close()

    attrs = parser.iframe_attrs or {}
    src = (attrs.get('src') or '').strip()
    if not _is_safe_google_maps_url(src):
        return ''

    rendered_attrs = [
        f'src="{escape(src, quote=True)}"',
        'width="100%"',
        'height="100%"',
        'style="border:0"',
        'loading="lazy"',
        'referrerpolicy="no-referrer-when-downgrade"',
    ]
    if 'allowfullscreen' in attrs:
        rendered_attrs.append('allowfullscreen')

    return mark_safe(f'<iframe {" ".join(rendered_attrs)}></iframe>')

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
