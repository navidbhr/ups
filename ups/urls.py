from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from main.views import import_products_excel

urlpatterns = [
    path('admin/products/import/', import_products_excel, name='import_products_excel'),
    path('admin/', admin.site.urls),

    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('', include('main.urls')),
]

# این بخش برای لود شدن عکس‌ها در حالت توسعه (Debug=True) ضروری است
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
