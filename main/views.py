from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from main.models import Product, Category, Article, Project, Partner, ProductConsultationRequest


def home_view(request):
    from django.utils.translation import get_language
    from .models import Branch, HomepageImage, HomeSlider

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

    context = {
        'categories': categories,
        'products': products,
        'articles': articles,
        'projects': projects,
        'partners': partners,
        'current_lang': current_lang,
    }
    
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
