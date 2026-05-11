from .models import SiteSettings, Category


def site_settings(request):
    return {
        'settings': SiteSettings.objects.first(),
        'categories': Category.objects.filter(parent__isnull=True)
    }