from django.urls import path, include
from .views import home_view, category_detail_view, product_detail_view, product_list_view, submit_product_consultation

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('', home_view, name='home'),
    path('products/', product_list_view, name='product_list'),
    path('category/<str:slug>/', category_detail_view, name='category_detail'),
    path('product/<str:slug>/', product_detail_view, name='product_detail'),
    path('api/submit-consultation/', submit_product_consultation, name='submit_product_consultation'),
]
