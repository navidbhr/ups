from django.urls import path
from .views import home_view, category_detail_view # اضافه کردن ویو جدید

urlpatterns = [
    path('', home_view, name='home'),
    # مسیر برای دسته‌بندی‌ها با استفاده از slug
    path('category/<slug:slug>/', category_detail_view, name='category_detail'),
]