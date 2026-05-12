from django.urls import path, include
from django.conf.urls.i18n import set_language
from .views import (
    home_view, category_list_view, category_detail_view, product_detail_view, product_list_view, 
    submit_product_consultation, project_list_view, project_detail_view,
    article_list_view, article_detail_view, contact_view, search_ajax, submit_contact_message
)

urlpatterns = [
    path('', home_view, name='home'),
    path('categories/', category_list_view, name='category_list'),
    path('category/<str:slug>/', category_detail_view, name='category_detail'),
    path('products/', product_list_view, name='product_list'),
    path('product/<str:slug>/', product_detail_view, name='product_detail'),
    path('projects/', project_list_view, name='project_list'),
    path('project/<str:slug>/', project_detail_view, name='project_detail'),
    path('articles/', article_list_view, name='article_list'),
    path('article/<str:slug>/', article_detail_view, name='article_detail'),
    path('contact/', contact_view, name='contact'),
    path('api/submit-consultation/', submit_product_consultation, name='submit_product_consultation'),
    path('api/submit-contact/', submit_contact_message, name='submit_contact_message'),
    path('api/search/', search_ajax, name='search_ajax'),
]
