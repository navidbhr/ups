from django.shortcuts import render, get_object_or_404

from main.models import Product, Category, Article, Project, Partner


def home_view(request):
    categories = Category.objects.filter(parent__isnull=True)[:6]
    products = Product.objects.filter(is_in_stock=True)[:8]
    articles = Article.objects.filter(is_published=True)[:6]
    projects = Project.objects.all()[:6]
    partners = Partner.objects.all()
    
    context = {
        'categories': categories,
        'products': products,
        'articles': articles,
        'projects': projects,
        'partners': partners,
    }
    
    return render(request, 'main/home.html', context)


