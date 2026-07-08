from django.contrib import admin
from django.db.models import Prefetch
from .models import (
    Category, Product, ProductImage, SpecificationGroup,
    ProductPrice, ProductSpecification, ProductDocument, Currency, SiteSettings,
    BlogCategory, Partner, FAQ, Agent, Project, ConsultationRequest, Article,
    Branch, PageTranslation, HomepageImage, HomeSlider, ProductConsultationRequest, StaticText, ContactMessage,
    AdvisorSetting,
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


class ProductPriceInline(admin.TabularInline):
    model = ProductPrice
    extra = 1


# --- Admins ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'base_price', 'price_summary', 'is_in_stock', 'updated_at')
    list_filter = ('category', 'is_in_stock', 'currency')
    search_fields = ('name', 'sku')
    readonly_fields = ('slug',)
    inlines = [ProductPriceInline, ProductImageInline, ProductSpecificationInline, ProductDocumentInline]
    fieldsets = (
        ('اطلاعات اصلی', {'fields': ('category', 'name', 'slug', 'sku', 'is_in_stock', 'warranty_months')}),
        ('قیمت‌گذاری', {'fields': ('base_price', 'currency', 'show_price')}),
        ('رسانه', {'fields': ('main_image', 'video_url', 'video_file'), 'classes': ('collapse',)}),
        ('سئو و محتوا', {'fields': ('short_description', 'full_description', 'meta_title', 'meta_description'),
                         'classes': ('collapse',)}),
    )
    change_list_template = "admin/product_change_list.html"

    @admin.display(description='قیمت‌ها')
    def price_summary(self, obj):
        prices = obj.display_prices
        if not prices:
            return 'تماس بگیرید'
        return '، '.join(f'{price.amount:g} {price.currency.symbol}' for price in prices)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'currency').prefetch_related(
            Prefetch(
                'prices',
                queryset=ProductPrice.objects.filter(is_active=True).select_related('currency').order_by('order', 'id'),
            )
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


@admin.register(StaticText)
class StaticTextAdmin(admin.ModelAdmin):
    list_display = ('key', 'default_text', 'text_fa', 'text_en')
    list_filter = ('text_fa', 'text_en', 'text_ar', 'text_ru')
    search_fields = ('key', 'default_text', 'description', 'text_fa', 'text_en')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('اطلاعات کلید', {
            'fields': ('key', 'description'),
            'description': 'کلید باید منحصر به فرد باشد. مثال: home_welcome_message'
        }),
        ('متن پیش‌فرض', {
            'fields': ('default_text',),
            'description': 'متنی که اگر ترجمه‌ای موجود نباشد نمایش داده می‌شود'
        }),
        ('ترجمه فارسی', {
            'fields': ('text_fa',),
        }),
        ('English Translation', {
            'fields': ('text_en',),
        }),
        ('الترجمة العربية', {
            'fields': ('text_ar',),
        }),
        ('Русский перевод', {
            'fields': ('text_ru',),
        }),
        ('زمان', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
    list_display = ('title_fa', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    readonly_fields = ('slug',)
    fieldsets = (
        ('محتوا', {'fields': ('title_fa', 'title_en', 'title_ar', 'title_ru', 'slug', 'category', 'image', 'content_fa', 'content_en', 'content_ar', 'content_ru', 'is_published')}),
        ('سئو 📈', {'fields': ('meta_title_fa', 'meta_title_en', 'meta_title_ar', 'meta_title_ru', 'meta_description_fa', 'meta_description_en', 'meta_description_ar', 'meta_description_ru'), 'classes': ('collapse',)}),
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
    list_display = ('title_fa', 'location_fa', 'order', 'is_published')
    list_editable = ('order',)
    list_filter = ('is_published',)


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent_name', 'province', 'city')
    list_filter = ('province',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'company_name', 'power_required', 'is_read', 'is_replied', 'created_at')
    list_filter = ('is_read', 'is_replied', 'created_at')
    search_fields = ('full_name', 'phone_number', 'company_name', 'message')
    list_editable = ('is_read', 'is_replied')
    readonly_fields = ('created_at', 'updated_at')


# سایر مدل‌های ساده
admin.site.register(BlogCategory)
admin.site.register(Category)
admin.site.register(Currency)
admin.site.register(SpecificationGroup)


@admin.register(AdvisorSetting)
class AdvisorSettingAdmin(admin.ModelAdmin):
    fieldsets = (
        ('عنوان و توضیحات', {'fields': ('title_fa', 'title_en', 'subtitle_fa', 'subtitle_en')}),
        ('دسته‌بندی‌ها', {'fields': ('categories',), 'description': 'اگر خالی باشد همه دسته‌بندی‌ها نمایش داده می‌شوند.'}),
        ('مقادیر پیش‌فرض محاسبات', {'fields': ('default_backup_hours', 'default_safety_margin', 'default_efficiency',
                                                   'default_battery_voltage', 'default_power_factor', 'default_dod')}),
        ('تنظیمات توان', {'fields': ('power_spec_keys',)}),
        ('عنوان بخش‌ها', {'fields': ('section_application_title', 'section_appliances_title', 'section_technical_title',
                                       'section_results_title', 'section_recommendations_title')}),
        ('متن دکمه‌ها و پیام‌ها', {'fields': ('submit_btn_text', 'add_row_btn_text', 'preset_label',
                                               'no_appliances_msg', 'no_results_msg', 'no_results_hint',
                                               'empty_state_title', 'empty_state_msg', 'select_placeholder')}),
        ('برچسب‌های نوع کاربری', {'fields': ('application_office_label', 'application_home_label',
                                              'application_server_label', 'application_industrial_label')}),
        ('سئو', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
        ('وضعیت', {'fields': ('is_active',)}),
    )
