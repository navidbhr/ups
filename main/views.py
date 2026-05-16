from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json

from main.models import Product, Category, Article, Project, Partner, ProductConsultationRequest, BlogCategory, ContactMessage, FAQ, Agent, HomepageImage, HomeSlider


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
    products = Product.objects.filter(is_in_stock=True)[:8]
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
    products = Product.objects.filter(category=category, is_in_stock=True).select_related('currency')
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
            'gallery', 'specifications__group', 'documents', 'faqs'
        ),
        slug=slug
    )
    
    # محصولات مرتبط (همان دسته‌بندی به جز محصول فعلی)
    related_products = Product.objects.filter(
        category=product.category,
        is_in_stock=True
    ).exclude(pk=product.pk).select_related('currency')[:4]
    
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

    products = Product.objects.filter(is_in_stock=True).select_related('currency')
    
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