from django.shortcuts import render, get_object_or_404

from main.models import Product, Category


def home_view(request):
    return render(request, 'main/home.html')


