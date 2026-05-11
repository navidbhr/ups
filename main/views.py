from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from main.models import Product, Category, Article, Project, Partner, ProductConsultationRequest


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

    # دریافت زبان فعلی از پارامتر URL یا سشن یا پیش‌فرض
    current_lang = request.GET.get('lang') or request.session.get('language') or get_language() or 'fa'

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

    # ذخیره زبان در سشن
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
        'not_in_stock',
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
