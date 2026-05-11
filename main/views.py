from django.shortcuts import render, get_object_or_404

from main.models import Product, Category, Article, Project, Partner


def home_view(request):
    from django.utils.translation import get_language
    from .models import Branch, HomepageImage, HomeSlider
    
    categories = Category.objects.filter(parent__isnull=True)[:6]
    products = Product.objects.filter(is_in_stock=True)[:8]
    articles = Article.objects.filter(is_published=True)[:6]
    projects = Project.objects.all()[:6]
    partners = Partner.objects.all()
    
    # دریافت زبان فعلی
    current_lang = get_language() or 'fa'
    
    context = {
        'categories': categories,
        'products': products,
        'articles': articles,
        'projects': projects,
        'partners': partners,
        'current_lang': current_lang,
    }
    
    return render(request, 'main/home.html', context)


def category_detail_view(request, slug):
    """نمایش جزئیات دسته‌بندی و محصولات آن"""
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_in_stock=True).select_related('currency')
    child_categories = Category.objects.filter(parent=category)
    
    context = {
        'category': category,
        'products': products,
        'products_count': products.count(),
        'child_categories': child_categories,
    }
    
    return render(request, 'main/category_detail.html', context)


def product_detail_view(request, slug):
    """نمایش جزئیات محصول"""
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
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'main/product_detail.html', context)


