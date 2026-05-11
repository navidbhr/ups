from django.contrib import admin
from .models import (
    Category, Product, ProductImage, SpecificationGroup,
    ProductSpecification, ProductDocument, Currency, SiteSettings,
    BlogCategory, Partner, FAQ, Agent, Project, ConsultationRequest, Article,
    Branch, PageTranslation, HomepageImage, HomeSlider, ProductConsultationRequest
)


# --- Inlines ---
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # کلاس collapse حذف شد تا باگ جزمین برطرف شود


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2
    # کلاس collapse حذف شد


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    # کلاس collapse حذف شد


# --- Admins ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'base_price', 'is_in_stock', 'updated_at')
    list_filter = ('category', 'is_in_stock', 'currency')
    search_fields = ('name', 'sku')
    readonly_fields = ('slug',)
    inlines = [ProductImageInline, ProductSpecificationInline, ProductDocumentInline]
    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('category', 'name', 'slug', 'sku', 'is_in_stock', 'warranty_months')}),
        ('قیمت‌گذاری', {'fields': ('base_price', 'currency', 'show_price')}),
        ('رسانه', {'fields': ('main_image', 'video_url', 'video_file'), 'classes': ('collapse',)}),
        ('سئو و محتوا', {'fields': ('short_description', 'full_description', 'meta_title', 'meta_description'),
                         'classes': ('collapse',)}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    fieldsets = (
        ('برند 🏷️',
         {'fields': ('site_name', 'site_title', 'site_description', 'keywords', 'logo', 'logo_light', 'favicon')}),
        ('Hero 🚀', {'fields': ('hero_title', 'hero_subtitle', 'hero_image', 'cta_text', 'cta_link')}),
        ('درباره ما 🏢', {'fields': ('about_summary',)}),
        ('شبکه‌های اجتماعی 📱', {'fields': ('instagram', 'telegram', 'linkedin')}),
        ('سیستم ⚙️',
         {'fields': ('is_maintenance_mode', 'footer_copy_right', 'google_analytics_id'), 'classes': ('collapse',)}),
    )


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_main', 'is_active', 'phone', 'order')
    list_editable = ('is_main', 'is_active', 'order')
    list_filter = ('is_main', 'is_active')
    search_fields = ('name', 'address', 'phone')
    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('name', 'is_main', 'is_active', 'order')}),
        ('اطلاعات تماس', {'fields': ('address', 'phone', 'email', 'whatsapp_number')}),
        ('نقشه', {'fields': ('map_iframe',), 'classes': ('collapse',)}),
    )


@admin.register(PageTranslation)
class PageTranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'text_fa')
    search_fields = ('key', 'text_fa', 'text_en')


@admin.register(HomepageImage)
class HomepageImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'order', 'is_active', 'created_at')
    list_filter = ('section', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'description')


@admin.register(HomeSlider)
class HomeSliderAdmin(admin.ModelAdmin):
    list_display = ('title_fa', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('order', 'is_active')
    search_fields = ('title_fa', 'title_en')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    readonly_fields = ('slug',)
    fieldsets = (
        ('محتوا', {'fields': ('title', 'slug', 'category', 'image', 'content', 'is_published')}),
        ('سئو 📈', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
    )


@admin.register(ConsultationRequest)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'is_checked', 'created_at')
    list_editable = ('is_checked',)
    list_filter = ('is_checked',)


@admin.register(ProductConsultationRequest)
class ProductConsultationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'product', 'phone_number', 'is_checked', 'created_at')
    list_editable = ('is_checked',)
    list_filter = ('is_checked', 'product')
    search_fields = ('full_name', 'phone_number', 'email', 'company_name')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'product', 'order')
    list_editable = ('order',)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'order')
    list_editable = ('order',)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'province', 'city')
    list_filter = ('province',)


# سایر مدل‌های ساده
admin.site.register(BlogCategory)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(SpecificationGroup)
