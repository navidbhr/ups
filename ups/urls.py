from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    
    # آدرس‌های مربوط به ویرایشگر متن (CKEditor 5)
    path("ckeditor5/", include('django_ckeditor_5.urls')),
]

# استفاده از i18n_patterns برای پشتیبانی از چندزبانه
urlpatterns += i18n_patterns(
    path('', include('main.urls')),
)

# این بخش برای لود شدن عکس‌ها در حالت توسعه (Debug=True) ضروری است
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)