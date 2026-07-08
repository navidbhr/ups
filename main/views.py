from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
import json
import openpyxl

from main.models import Product, ProductPrice, ProductSpecification, SpecificationGroup, Category, Currency, Article, Project, Partner, ProductConsultationRequest, BlogCategory, ContactMessage, FAQ, Agent, HomepageImage, HomeSlider


def product_price_prefetch():
    return Prefetch(
        'prices',
        queryset=ProductPrice.objects.filter(is_active=True).select_related('currency').order_by('order', 'id'),
    )


def apply_article_translation(article, lang):
    article.display_title = article.get_title(lang)
    article.display_content = article.get_content(lang)
    article.display_meta_title = article.get_meta_title(lang)
    article.display_meta_description = article.get_meta_description(lang)
    return article


def apply_project_translation(project, lang):
    project.display_title = project.get_title(lang)
    project.display_location = project.get_location(lang)
    project.display_description = project.get_description(lang)
    return project

def home_view(request):
    from django.utils.translation import get_language
    from .models import Branch, HomepageImage, HomeSlider, StaticText, SiteSettings

    # بررسی اینکه آیا درخواست AJAX است یا نه
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    categories = Category.objects.filter(parent__isnull=True)[:6]
    products = Product.objects.filter(is_in_stock=True).select_related('currency').prefetch_related(product_price_prefetch())[:8]
    articles = list(Article.objects.filter(is_published=True)[:6])
    projects = list(Project.objects.filter(is_published=True)[:6])
    partners = Partner.objects.all()
    
    # مدل‌های جدید برای صفحه اصلی
    faqs = FAQ.objects.filter(product__isnull=True).order_by('order')[:10]  # سوالات متداول عمومی
    agents = Agent.objects.order_by('province', 'city')[:20]  # نمایندگان برتر
    homepage_images = HomepageImage.objects.filter(is_active=True).order_by('order')
    slider_images = HomeSlider.objects.filter(is_active=True).order_by('order')
    
    # گروه‌بندی تصاویر صفحه اصلی بر اساس section
    hero_images = homepage_images.filter(section='hero')[:3]
    about_images = homepage_images.filter(section='about')[:3]
    products_images = homepage_images.filter(section='products')[:3]
    projects_images = homepage_images.filter(section='projects')[:3]
    partners_images = homepage_images.filter(section='partners')[:3]

    # دریافت زبان فعلی - اولویت با پارامتر URL است، سپس سشن، سپس زبان پیش‌فرض جنگو
    # در درخواست AJAX، زبان از پارامتر URL خوانده می‌شود که توسط JS اضافه شده
    url_lang = request.GET.get('lang')
    session_lang = request.session.get('language')
    django_lang = get_language()
    
    if url_lang:
        current_lang = url_lang
    elif session_lang:
        current_lang = session_lang
    elif django_lang:
        current_lang = django_lang
    else:
        current_lang = 'fa'

    # تبدیل کد زبان به فرمت کوتاه
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    articles = [apply_article_translation(article, current_lang) for article in articles]
    projects = [apply_project_translation(project, current_lang) for project in projects]

    slider_images = list(slider_images)
    for slide in slider_images:
        slide.display_title = slide.get_title(current_lang)
        slide.display_subtitle = slide.get_subtitle(current_lang)
    # ذخیره زبان در سشن برای درخواست‌های بعدی
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # اگر SiteSettings وجود نداشت، یک آبجکت خالی با متدهای لازم بساز
    if not settings:
        class EmptySettings:
            def get_hero_title(self):
                return ''
            def get_hero_subtitle(self):
                return ''
            def get_cta_text(self):
                return ''
            @property
            def cta_link(self):
                return '/contact/'
            @property
            def hero_image(self):
                return ''
        settings = EmptySettings()

    # بارگذاری تمام متون استاتیک برای اطمینان از لود صحیح
    static_texts = {}
    for key in [
        'hero_title', 'hero_subtitle', 'cta_text',
        'hero_stats_experience', 'hero_stats_projects', 'hero_stats_customers',
        'hero_badge_warranty', 'hero_badge_warranty_value', 'hero_badge_support', 'hero_badge_support_value',
        'categories_title', 'categories_subtitle',
        'view_products', 'category_placeholder_title', 'category_placeholder_desc',
        'products_title', 'products_subtitle', 'contact_us', 'details',
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
        'form_submit', 'form_submit_button',
        'contact_info_title', 'contact_address_label', 'contact_phone_label', 'contact_email_label',
        'not_in_stock', 'search_placeholder', 'no_results','faq_title', 'faq_subtitle', 'faq_empty',
        'agents_title', 'agents_subtitle', 'agents_map_link', 'agents_empty',
        'mobile_menu_title', 'search_loading', 'toggle_theme', 'about_project', 'back_to_projects', 'related_projects', 'view_details',
        'back_to_articles', 'related_articles', 'no_related'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'categories': categories,
        'products': products,
        'articles': articles,
        'projects': projects,
        'partners': partners,
        'faqs': faqs,
        'agents': agents,
        'hero_images': hero_images,
        'about_images': about_images,
        'products_images': products_images,
        'projects_images': projects_images,
        'partners_images': partners_images,
        'slider_images': slider_images,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }

    return render(request, 'main/home.html', context)


def submit_product_consultation(request):
    """پردازش درخواست مشاوره محصول از طریق AJAX"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    product_id = data.get('product_id')
    full_name = data.get('full_name', '').strip()
    phone_number = data.get('phone_number', '').strip()

    if not product_id or not full_name or not phone_number:
        return JsonResponse({
            'success': False,
            'message': 'Product, name, and phone number are required.'
        }, status=400)

    product = get_object_or_404(Product, pk=product_id)

    ProductConsultationRequest.objects.create(
        product=product,
        full_name=full_name,
        phone_number=phone_number,
        email=data.get('email', '').strip(),
        company_name=data.get('company_name', '').strip(),
        quantity_needed=data.get('quantity_needed', '').strip(),
        application=data.get('application', '').strip(),
        message=data.get('message', '').strip(),
    )

    return JsonResponse({
        'success': True,
        'message': 'Your request was submitted successfully.'
    })


def category_list_view(request):
    """نمایش لیست تمام دسته‌بندی‌ها"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    categories = Category.objects.filter(parent__isnull=True)
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'categories_title', 'categories_subtitle', 'view_products', 'details',
        'category_placeholder_title', 'category_placeholder_desc', 'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'categories': categories,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/category_list.html', context)


def category_detail_view(request, slug):
    """نمایش جزئیات دسته‌بندی و محصولات آن"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_in_stock=True).select_related('currency').prefetch_related(product_price_prefetch())
    child_categories = Category.objects.filter(parent=category)
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'categories_title', 'categories_subtitle', 'view_products', 'details',
        'product_placeholder_price', 'product_placeholder_title', 'product_placeholder_desc',
        'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'category': category,
        'products': products,
        'products_count': products.count(),
        'child_categories': child_categories,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/category_detail.html', context)


def product_detail_view(request, slug):
    """نمایش جزئیات محصول"""
    from django.utils.translation import get_language

    product = get_object_or_404(
        Product.objects.select_related('category', 'currency').prefetch_related(
            product_price_prefetch(), 'gallery', 'specifications__group', 'documents', 'faqs'
        ),
        slug=slug
    )
    
    # محصولات مرتبط (همان دسته‌بندی به جز محصول فعلی)
    related_products = Product.objects.filter(
        category=product.category,
        is_in_stock=True
    ).exclude(pk=product.pk).select_related('currency').prefetch_related(product_price_prefetch())[:4]
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    context = {
        'product': product,
        'related_products': related_products,
        'current_lang': current_lang,
    }
    
    return render(request, 'main/product_detail.html', context)


def product_list_view(request):
    """نمایش لیست همه محصولات"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    products = Product.objects.filter(is_in_stock=True).select_related('currency').prefetch_related(product_price_prefetch())
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'products_title', 'products_subtitle', 'no_image', 'contact_for_price', 'view_details', 'no_products',
        'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'products': products,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/product_list.html', context)


def project_list_view(request):
    """نمایش لیست پروژه‌ها"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    projects = list(Project.objects.filter(is_published=True).order_by('order', '-created_at'))
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    projects = [apply_project_translation(project, current_lang) for project in projects]
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'projects_title', 'projects_subtitle', 'details', 'no_results', 'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'projects': projects,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/project_list.html', context)


def project_detail_view(request, slug):
    """نمایش جزئیات پروژه"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    project_qs = Project.objects.all()
    if not request.user.is_staff:
        project_qs = project_qs.filter(is_published=True)

    project = get_object_or_404(project_qs, slug=slug)
    
    # پروژه‌های مرتبط (سایر پروژه‌ها)
    related_projects = list(Project.objects.filter(
        is_published=True
    ).exclude(pk=project.pk).order_by('order', '-created_at')[:4])
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    project = apply_project_translation(project, current_lang)
    related_projects = [apply_project_translation(item, current_lang) for item in related_projects]
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'projects_title', 'about_project', 'back_to_projects', 'related_projects', 'view_details',
        'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'project': project,
        'related_projects': related_projects,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/project_detail.html', context)


def article_list_view(request):
    """نمایش لیست مقالات"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    articles = Article.objects.filter(is_published=True).order_by('-created_at')
    categories = BlogCategory.objects.all()
    
    # فیلتر بر اساس دسته‌بندی
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(BlogCategory, slug=category_slug)
        articles = articles.filter(category=category)
    else:
        category = None
        
    articles = list(articles)
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    articles = [apply_article_translation(article, current_lang) for article in articles]
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'articles_title', 'articles_subtitle', 'categories', 'all_categories', 
        'read_more', 'no_results', 'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'articles': articles,
        'categories': categories,
        'current_category': category,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/article_list.html', context)


def article_detail_view(request, slug):
    """نمایش جزئیات مقاله"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    article_qs = Article.objects.all()
    if not request.user.is_staff:
        article_qs = article_qs.filter(is_published=True)

    article = get_object_or_404(article_qs, slug=slug)
    
    # مقالات مرتبط (همان دسته‌بندی به جز مقاله فعلی)
    related_articles = list(Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(pk=article.pk).order_by('-created_at')[:4])
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    article = apply_article_translation(article, current_lang)
    related_articles = [apply_article_translation(item, current_lang) for item in related_articles]
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک
    static_texts = {}
    for key in [
        'articles_title', 'back_to_articles', 'related_articles', 'no_related',
        'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'article': article,
        'related_articles': related_articles,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/article_detail.html', context)


def contact_view(request):
    """نمایش صفحه تماس با ما"""
    from django.utils.translation import get_language
    from .models import Branch, StaticText, SiteSettings

    branches = Branch.objects.filter(is_active=True)
    
    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    # بارگذاری تنظیمات سایت
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    # بارگذاری متون استاتیک برای صفحه تماس
    static_texts = {}
    for key in [
        'contact_title', 'contact_subtitle',
        'form_name_label', 'form_name_placeholder',
        'form_phone_label', 'form_phone_placeholder',
        'form_company_label', 'form_company_placeholder',
        'form_power_label', 'form_power_placeholder',
        'form_message_label', 'form_message_placeholder',
        'form_submit', 'send_message', 'main_branch',
        'contact_info_title', 'contact_address_label', 'contact_phone_label', 'contact_email_label',
        'whatsapp', 'cta_text', 'form_submit_button', 'search_loading', 'toggle_theme'
    ]:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    context = {
        'branches': branches,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    return render(request, 'main/contact.html', context)


def submit_contact_message(request):
    """پردازش پیام ارسالی از صفحه تماس با ما"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON'}, status=400)

    full_name = data.get('full_name', '').strip()
    phone_number = data.get('phone_number', '').strip()
    message = data.get('message', '').strip()

    if not full_name or not phone_number or not message:
        return JsonResponse({
            'success': False,
            'message': 'Name, phone number, and message are required.'
        }, status=400)

    ContactMessage.objects.create(
        full_name=full_name,
        phone_number=phone_number,
        company_name=data.get('company_name', '').strip(),
        power_required=data.get('power_required', '').strip(),
        message=message,
    )

    return JsonResponse({
        'success': True,
        'message': 'Your message was submitted successfully.'
    })


def search_ajax(request):
    """جستجوی AJAX برای محصولات، دسته‌بندی‌ها، مقالات و پروژه‌ها"""
    from django.utils.translation import get_language
    from django.db.models import Q

    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': {'products': [], 'categories': [], 'articles': [], 'projects': []}})
    
    # دریافت زبان فعلی
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {
        'fa-ir': 'fa',
        'en-us': 'en',
        'ar': 'ar',
        'ru': 'ru',
        'fa': 'fa',
        'en': 'en',
    }
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    
    results = {
        'products': [],
        'categories': [],
        'articles': [],
        'projects': []
    }
    
    # جستجو در محصولات
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(short_description__icontains=query),
        is_in_stock=True
    )[:5]
    
    for product in products:
        results['products'].append({
            'type': 'product',
            'title': product.name,
            'url': f'/product/{product.slug}/',
            'image': product.main_image.url if product.main_image else '',
        })
    
    # جستجو در دسته‌بندی‌ها
    categories = Category.objects.filter(
        Q(title__icontains=query)
    )[:5]
    
    for category in categories:
        results['categories'].append({
            'type': 'category',
            'title': category.title,
            'url': f'/category/{category.slug}/',
            'image': category.image.url if category.image else '',
        })
    
    # جستجو در مقالات
    if current_lang == 'en':
        articles = Article.objects.filter(
            Q(title_en__icontains=query) | Q(content_en__icontains=query),
            is_published=True
        )[:5]
    elif current_lang == 'ar':
        articles = Article.objects.filter(
            Q(title_ar__icontains=query) | Q(content_ar__icontains=query),
            is_published=True
        )[:5]
    elif current_lang == 'ru':
        articles = Article.objects.filter(
            Q(title_ru__icontains=query) | Q(content_ru__icontains=query),
            is_published=True
        )[:5]
    else:
        articles = Article.objects.filter(
            Q(title_fa__icontains=query) | Q(content_fa__icontains=query),
            is_published=True
        )[:5]
    
    for article in articles:
        results['articles'].append({
            'type': 'article',
            'title': article.get_title(current_lang),
            'url': f'/article/{article.slug}/',
            'image': article.image.url if article.image else '',
        })
    
    # جستجو در پروژه‌ها
    if current_lang == 'en':
        projects = Project.objects.filter(
            Q(title_en__icontains=query) | Q(description_en__icontains=query),
            is_published=True
        )[:5]
    elif current_lang == 'ar':
        projects = Project.objects.filter(
            Q(title_ar__icontains=query) | Q(description_ar__icontains=query),
            is_published=True
        )[:5]
    elif current_lang == 'ru':
        projects = Project.objects.filter(
            Q(title_ru__icontains=query) | Q(description_ru__icontains=query),
            is_published=True
        )[:5]
    else:
        projects = Project.objects.filter(
            Q(title_fa__icontains=query) | Q(description_fa__icontains=query),
            is_published=True
        )[:5]
    
    for project in projects:
        results['projects'].append({
            'type': 'project',
            'title': project.get_title(current_lang),
            'url': f'/project/{project.slug}/',
            'image': project.image.url if project.image else '',
        })
    
    return JsonResponse(results)


@staff_member_required
def import_products_excel(request):
    results = []

    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            wb = openpyxl.load_workbook(excel_file, read_only=True)

            # --- Sheet 1: Products ---
            if 'Products' not in wb.sheetnames:
                results.append({'type': 'error', 'message': 'شیت Products در فایل یافت نشد.'})
            else:
                ws = wb['Products']
                headers = [str(cell.value).strip() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                required_cols = {'sku', 'name', 'category'}
                if not required_cols.intersection(headers):
                    results.append({'type': 'error', 'message': 'ستون‌های مورد نیاز (sku, name, category) در شیت Products یافت نشد.'})
                else:
                    created, updated, errors = 0, 0, 0
                    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                        row_data = dict(zip(headers, [str(v).strip() if v else '' for v in row]))
                        sku = row_data.get('sku', '')
                        if not sku:
                            continue
                        try:
                            category_title = row_data.get('category', '')
                            if not category_title:
                                results.append({'type': 'error', 'message': f'ردیف {row_idx}: دسته‌بندی مشخص نشده است.'})
                                errors += 1
                                continue

                            category = Category.objects.filter(title=category_title).first()
                            if not category:
                                results.append({'type': 'error', 'message': f'ردیف {row_idx}: دسته‌بندی "{category_title}" یافت نشد.'})
                                errors += 1
                                continue

                            currency_symbol = row_data.get('currency', '')
                            currency = None
                            if currency_symbol:
                                currency = Currency.objects.filter(symbol=currency_symbol).first()
                                if not currency:
                                    currency = Currency.objects.filter(name__icontains=currency_symbol).first()

                            name = row_data.get('name', '')
                            if not name:
                                results.append({'type': 'error', 'message': f'ردیف {row_idx}: نام محصول مشخص نشده است.'})
                                errors += 1
                                continue

                            product, is_new = Product.objects.update_or_create(
                                sku=sku,
                                defaults={
                                    'name': name,
                                    'category': category,
                                    'base_price': _parse_decimal(row_data.get('base_price', '0')),
                                    'currency': currency,
                                    'short_description': row_data.get('short_description', ''),
                                    'full_description': row_data.get('full_description', ''),
                                    'is_in_stock': _parse_bool(row_data.get('is_in_stock', 'True')),
                                    'show_price': _parse_bool(row_data.get('show_price', 'True')),
                                    'warranty_months': _parse_int(row_data.get('warranty_months', '12')),
                                    'meta_title': row_data.get('meta_title', '') or '',
                                    'meta_description': row_data.get('meta_description', '') or '',
                                }
                            )
                            if is_new:
                                created += 1
                            else:
                                updated += 1
                        except Exception as e:
                            results.append({'type': 'error', 'message': f'ردیف {row_idx} (SKU: {sku}): {str(e)}'})
                            errors += 1

                    results.append({'type': 'success', 'message': f'محصولات: {created} ایجاد، {updated} آپدیت، {errors} خطا.'})

            # --- Sheet 2: Prices ---
            if 'Prices' in wb.sheetnames:
                ws = wb['Prices']
                headers = [str(cell.value).strip() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if 'sku' in headers and 'amount' in headers:
                    price_created, price_errors = 0, 0
                    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                        row_data = dict(zip(headers, [str(v).strip() if v else '' for v in row]))
                        sku = row_data.get('sku', '')
                        if not sku:
                            continue
                        try:
                            product = Product.objects.filter(sku=sku).first()
                            if not product:
                                price_errors += 1
                                continue
                            currency_symbol = row_data.get('currency', '')
                            currency = None
                            if currency_symbol:
                                currency = Currency.objects.filter(symbol=currency_symbol).first()
                                if not currency:
                                    currency = Currency.objects.filter(name__icontains=currency_symbol).first()
                            amount = _parse_decimal(row_data.get('amount', '0'))
                            if amount <= 0:
                                continue
                            ProductPrice.objects.create(
                                product=product,
                                amount=amount,
                                currency=currency,
                                label=row_data.get('label', ''),
                                is_active=_parse_bool(row_data.get('is_active', 'True')),
                                order=_parse_int(row_data.get('order', '0')),
                            )
                            price_created += 1
                        except Exception:
                            price_errors += 1
                    results.append({'type': 'success', 'message': f'قیمت‌ها: {price_created} ایجاد، {price_errors} خطا.'})

            # --- Sheet 3: Specifications ---
            if 'Specifications' in wb.sheetnames:
                ws = wb['Specifications']
                headers = [str(cell.value).strip() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if 'sku' in headers and 'key' in headers and 'value' in headers:
                    spec_created, spec_errors = 0, 0
                    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                        row_data = dict(zip(headers, [str(v).strip() if v else '' for v in row]))
                        sku = row_data.get('sku', '')
                        if not sku:
                            continue
                        try:
                            product = Product.objects.filter(sku=sku).first()
                            if not product:
                                spec_errors += 1
                                continue
                            group_name = row_data.get('group', 'عمومی')
                            group, _ = SpecificationGroup.objects.get_or_create(name=group_name)
                            ProductSpecification.objects.update_or_create(
                                product=product,
                                key=row_data['key'],
                                defaults={
                                    'group': group,
                                    'value': row_data['value'],
                                }
                            )
                            spec_created += 1
                        except Exception:
                            spec_errors += 1
                    results.append({'type': 'success', 'message': f'مشخصات فنی: {spec_created} ایجاد، {spec_errors} خطا.'})

            wb.close()

        except Exception as e:
            results.append({'type': 'error', 'message': f'خطا در خواندن فایل: {str(e)}'})

    return render(request, 'admin/import_products.html', {'results': results})


def product_advisor_view(request):
    from django.utils.translation import get_language
    from django.db.models import Q
    from .models import StaticText, SiteSettings, AdvisorSetting

    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'
    lang_map = {'fa-ir': 'fa', 'en-us': 'en', 'ar': 'ar', 'ru': 'ru', 'fa': 'fa', 'en': 'en'}
    current_lang = lang_map.get(current_lang.lower(), 'fa')
    request.session['language'] = current_lang

    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None

    advisor_config = AdvisorSetting.get_settings()

    static_texts = {}
    for key in ['products_title', 'no_image', 'contact_for_price', 'view_details', 'no_products', 'advisor_error_min_appliances']:
        try:
            static_obj = StaticText.objects.get(key=key)
            field_name = f'text_{current_lang}'
            text = getattr(static_obj, field_name, None)
            if not text and current_lang != 'fa':
                text = getattr(static_obj, 'text_fa', '')
            static_texts[key] = text or static_obj.default_text or ''
        except StaticText.DoesNotExist:
            static_texts[key] = ''

    # Preset appliances
    presets = [
        {'key': 'lamp', 'name': 'لامپ کم مصرف LED', 'power': 15},
        {'key': 'tv', 'name': 'تلویزیون و رسیور', 'power': 120},
        {'key': 'pc', 'name': 'کامپیوتر رومیزی', 'power': 250},
        {'key': 'laptop', 'name': 'لپ‌تاپ', 'power': 60},
        {'key': 'fridge', 'name': 'یخچال معمولی', 'power': 300},
        {'key': 'modem', 'name': 'مودم اینترنت', 'power': 15},
        {'key': 'fan', 'name': 'کولر آبی', 'power': 500},
        {'key': 'split', 'name': 'اسپلیت ۹۰۰۰', 'power': 900},
        {'key': 'pump', 'name': 'پمپ آب ۱ اسب', 'power': 750},
        {'key': 'server', 'name': 'سرور رک', 'power': 600},
    ]

    recommendations = None
    form_data = {}
    selected_appliances = []
    results_summary = {}

    if request.method == 'POST':
        form_data = {
            'application': request.POST.get('application', ''),
            'budget_max': request.POST.get('budget_max', ''),
            'backup_hours': request.POST.get('backup_hours', str(advisor_config.default_backup_hours if advisor_config else 4)),
            'safety_margin': request.POST.get('safety_margin', str(advisor_config.default_safety_margin if advisor_config else 25)),
            'system_efficiency': request.POST.get('system_efficiency', str(advisor_config.default_efficiency if advisor_config else 85)),
            'battery_voltage': request.POST.get('battery_voltage', str(advisor_config.default_battery_voltage if advisor_config else 48)),
            'power_factor': request.POST.get('power_factor', str(advisor_config.default_power_factor if advisor_config else 0.8)),
            'dod': request.POST.get('dod', str(advisor_config.default_dod if advisor_config else 50)),
            'system_phase': request.POST.get('system_phase', '1phase'),
        }

        # Parse appliances from POST
        names = request.POST.getlist('app_name[]')
        powers = request.POST.getlist('app_power[]')
        qties = request.POST.getlist('app_qty[]')
        hours = request.POST.getlist('app_hours[]')

        pf = _parse_decimal(form_data.get('power_factor', '0.8'))
        if pf <= 0: pf = 0.8

        total_load_watts = 0
        total_load_va = 0

        for i in range(len(names)):
            if names[i].strip():
                p = _parse_decimal(powers[i]) if i < len(powers) else 0
                q = _parse_int(qties[i]) if i < len(qties) else 1
                h = _parse_decimal(hours[i]) if i < len(hours) else 0
                selected_appliances.append({
                    'name': names[i].strip(),
                    'power': p,
                    'qty': q,
                    'hours': h,
                    'total_watts': p * q,
                    'total_wh': p * q * h,
                })
                total_load_watts += p * q
                total_load_va += p * q / pf

        if total_load_watts == 0:
            return render(request, 'main/product_advisor.html', {
                'presets': presets,
                'recommendations': None,
                'selected_appliances': [],
                'form_data': form_data,
                'results_summary': {},
                'advisor_config': advisor_config,
                'current_lang': current_lang,
                'static_texts': static_texts,
                'settings': settings,
                'error': static_texts.get('advisor_error_min_appliances', 'حداقل یک وسیله مصرفی وارد کنید.'),
            })

        pf = _parse_decimal(form_data.get('power_factor', '0.8'))
        if pf <= 0: pf = 0.8
        sm = _parse_decimal(form_data.get('safety_margin', '25'))
        eff = _parse_decimal(form_data.get('system_efficiency', '85'))
        dod = _parse_decimal(form_data.get('dod', '50'))
        bv = _parse_decimal(form_data.get('battery_voltage', '48'))
        bh = _parse_decimal(form_data.get('backup_hours', '4'))

        inverter_power_va = total_load_va * (1 + sm / 100)
        inverter_power_w = total_load_watts * (1 + sm / 100)
        total_energy = total_load_watts * bh
        battery_ah = total_energy / (bv * (dod / 100) * (eff / 100)) if bv > 0 and dod > 0 and eff > 0 else 0

        results_summary = {
            'total_load_watts': round(total_load_watts),
            'total_load_va': round(total_load_va),
            'inverter_power_va': round(inverter_power_va),
            'inverter_power_w': round(inverter_power_w),
            'total_energy': round(total_energy),
            'battery_ah': round(battery_ah, 1),
            'battery_voltage': bv,
            'system_phase': form_data.get('system_phase', '1phase'),
        }

        # --- Product Matching ---
        qs = Product.objects.filter(is_in_stock=True).select_related('category', 'currency')

        # Filter by advisor categories
        if advisor_config and advisor_config.pk:
            allowed_cats = advisor_config.categories.all()
            if allowed_cats.exists():
                qs = qs.filter(category__in=allowed_cats)

        # Filter by budget
        budget = _parse_decimal(form_data.get('budget_max', '0'))
        if budget > 0:
            qs = qs.filter(base_price__lte=budget)

        # Match by power specs
        spec_keys_str = advisor_config.power_spec_keys if advisor_config and advisor_config.power_spec_keys else "توان,قدرت,power,VA,W"
        spec_keys = [k.strip() for k in spec_keys_str.split(',') if k.strip()]

        matching_product_ids = set()
        for key in spec_keys:
            specs = ProductSpecification.objects.filter(
                key__icontains=key
            ).exclude(value__isnull=True).exclude(value='')
            for spec in specs:
                try:
                    spec_val = _parse_decimal(spec.value)
                    if spec_val > 0 and spec_val >= inverter_power_va * 0.7:
                        matching_product_ids.add(spec.product_id)
                except:
                    pass

        # Also match by name/description containing power values
        power_str = str(int(inverter_power_va))
        name_q = Q(name__icontains=power_str) | Q(short_description__icontains=power_str)
        name_products = Product.objects.filter(name_q, is_in_stock=True).values_list('id', flat=True)
        matching_product_ids.update(name_products)

        if matching_product_ids:
            qs = qs.filter(id__in=matching_product_ids)

        recommendations = qs.prefetch_related(product_price_prefetch())[:30]

    return render(request, 'main/product_advisor.html', {
        'presets': presets,
        'recommendations': recommendations,
        'selected_appliances': selected_appliances,
        'form_data': form_data,
        'results_summary': results_summary,
        'advisor_config': advisor_config,
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
        'error': request.POST.get('error', ''),
    })


def _parse_decimal(val):
    if not val:
        return 0
    try:
        val = str(val).replace(',', '').strip()
        return float(val)
    except (ValueError, TypeError):
        return 0


def _parse_int(val):
    if not val:
        return 0
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return 0


def _parse_bool(val):
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in ('true', '1', 'yes', 'بله', 'فعال')
