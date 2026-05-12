from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from main.models import Product, Category, Article, Project, Partner, ProductConsultationRequest, BlogCategory


def home_view(request):
    from django.utils.translation import get_language
    from .models import Branch, HomepageImage, HomeSlider, StaticText, SiteSettings

    # بررسی اینکه آیا درخواست AJAX است یا نه
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    categories = Category.objects.filter(parent__isnull=True)[:6]
    products = Product.objects.filter(is_in_stock=True)[:8]
    articles = Article.objects.filter(is_published=True)[:6]
    projects = Project.objects.all()[:6]
    partners = Partner.objects.all()

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
        'form_submit',
        'contact_info_title', 'contact_address_label', 'contact_phone_label', 'contact_email_label',
        'not_in_stock', 'search_placeholder', 'no_results',
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
        'current_lang': current_lang,
        'static_texts': static_texts,
        'settings': settings,
    }
    
    # اگر درخواست AJAX بود، فقط تکه‌ای از تمپلیت را برگردان
    if is_ajax:
        return render(request, 'main/home_content.html', context)
    
    return render(request, 'main/home.html', context)


@csrf_exempt
def submit_product_consultation(request):
    """پردازش درخواست مشاوره محصول از طریق AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, pk=product_id)
            
            consultation = ProductConsultationRequest.objects.create(
                product=product,
                full_name=data.get('full_name', ''),
                phone_number=data.get('phone_number', ''),
                email=data.get('email', ''),
                company_name=data.get('company_name', ''),
                quantity_needed=data.get('quantity_needed', ''),
                application=data.get('application', ''),
                message=data.get('message', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'درخواست شما با موفقیت ثبت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'خطا در ثبت درخواست: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'متد نامعتبر'}, status=405)


def category_detail_view(request, slug):
    """نمایش جزئیات دسته‌بندی و محصولات آن"""
    from django.utils.translation import get_language

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

    context = {
        'category': category,
        'products': products,
        'products_count': products.count(),
        'child_categories': child_categories,
        'current_lang': current_lang,
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

    context = {
        'products': products,
        'current_lang': current_lang,
    }
    
    return render(request, 'main/product_list.html', context)


def project_list_view(request):
    """نمایش لیست پروژه‌ها"""
    from django.utils.translation import get_language
    from .models import StaticText, SiteSettings

    projects = Project.objects.filter(is_published=True).order_by('order', '-created_at')
    
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
        'projects_title', 'projects_subtitle', 'details', 'no_results',
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

    project = get_object_or_404(Project, slug=slug)
    
    # پروژه‌های مرتبط (سایر پروژه‌ها)
    related_projects = Project.objects.filter(
        is_published=True
    ).exclude(pk=project.pk).order_by('order', '-created_at')[:4]
    
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
        'projects_title', 'about_project', 'back_to_projects', 'related_projects', 'view_details',
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
        'articles_title', 'articles_subtitle', 'categories', 'all_categories', 
        'read_more', 'no_results',
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

    article = get_object_or_404(Article, slug=slug)
    
    # مقالات مرتبط (همان دسته‌بندی به جز مقاله فعلی)
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(pk=article.pk).order_by('-created_at')[:4]
    
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
        'articles_title', 'back_to_articles', 'related_articles', 'no_related',
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
        'form_submit',
        'contact_info_title', 'contact_address_label', 'contact_phone_label', 'contact_email_label',
        'whatsapp',
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


@csrf_exempt
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
