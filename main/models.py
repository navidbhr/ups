from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


# --- کلاس پایه برای مدیریت زمان ---
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))

    class Meta:
        abstract = True


# --- تنظیمات سیستمی (Singleton) ---
class SiteSettings(models.Model):
    # مقادیر دیفالت اضافه شد تا سایت در حالت خام هم محتوای اولیه داشته باشد
    site_name = models.CharField(max_length=100, default="برهان یو پی اس", verbose_name=_("نام برند"))
    site_title = models.CharField(max_length=200, default="تولید و عرضه انواع UPS", verbose_name=_("عنوان سئو (Title Tag)"))
    site_description = models.TextField(default="مشاوره و خرید انواع دستگاه‌های یو پی اس صنعتی و خانگی با گارانتی معتبر.", verbose_name=_("توضیحات متا (Meta Description)"))
    keywords = models.CharField(max_length=500, blank=True, verbose_name=_("کلمات کلیدی (با کاما جدا کنید)"))
    logo = models.ImageField(upload_to='settings/', verbose_name=_("لوگوی رنگی (هدر)"))
    logo_light = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_("لوگوی سفید (فوتر)"))
    favicon = models.ImageField(upload_to='settings/', verbose_name=_("فاوآیکون"))

    hero_title = models.CharField(max_length=200, default="تامین انرژی پایدار با برهان", blank=True, verbose_name=_("تیتر بزرگ صفحه اصلی"))
    hero_subtitle = models.TextField(default="ارائه دهنده پیشرفته‌ترین سیستم‌های تامین برق اضطراری در ایران", blank=True, verbose_name=_("متن زیر تیتر صفحه اصلی"))
    hero_image = models.ImageField(upload_to='settings/', blank=True, verbose_name=_("تصویر بخش Hero"))
    cta_text = models.CharField(max_length=50, default="درخواست مشاوره", blank=True, verbose_name=_("متن دکمه فراخوان (CTA)"))
    cta_link = models.CharField(max_length=200, default="#consultation", blank=True, verbose_name=_("لینک دکمه فراخوان"))

    about_summary = models.TextField(default="شرکت برهان پیشرو در ارائه راهکارهای برق اضطراری...", blank=True, verbose_name=_("خلاصه درباره ما"))

    address = models.CharField(max_length=500, default="شیراز، دفتر مرکزی برهان", verbose_name=_("آدرس فیزیکی"))
    phone = models.CharField(max_length=20, default="071-00000000", verbose_name=_("شماره تماس"))
    email = models.EmailField(default="info@borhan.com", verbose_name=_("ایمیل پشتیبانی"))
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name=_("شماره مستقیم واتس‌اپ"))
    map_iframe = models.TextField(blank=True, verbose_name=_("کد Iframe نقشه گوگل"))

    instagram = models.URLField(blank=True, verbose_name=_("اینستاگرام"))
    telegram = models.URLField(blank=True, verbose_name=_("تلگرام"))
    linkedin = models.URLField(blank=True, verbose_name=_("لینکدین"))

    is_maintenance_mode = models.BooleanField(default=False, verbose_name=_("حالت تعمیر"))
    footer_copy_right = models.CharField(max_length=255, default="تمامی حقوق برای شرکت برهان محفوظ است.", verbose_name=_("متن کپی‌رایت"))
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name=_("Google Analytics ID"))

    class Meta:
        verbose_name = _("تنظیمات کلی سایت")
        verbose_name_plural = _("تنظیمات کلی سایت")

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_("خطای منطقی: شما نمی‌توانید بیش از یک رکورد تنظیمات بسازید."))
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.site_name


# --- مدیریت کاتالوگ محصولات ---
class Currency(TimeStampedModel):
    name = models.CharField(max_length=50, verbose_name=_("نام واحد"))
    symbol = models.CharField(max_length=10, verbose_name=_("نماد"))
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=2, default=1.0, verbose_name=_("نرخ تبدیل"))
    is_base = models.BooleanField(default=False, verbose_name=_("واحد پایه است؟"))

    class Meta:
        verbose_name = _("واحد پولی")
        verbose_name_plural = _("واحدهای پولی")

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    title = models.CharField(max_length=100, verbose_name=_("عنوان دسته‌بندی"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, verbose_name=_("نامک"))
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children',
                               verbose_name=_("دسته‌بندی والد"))
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name=_("تصویر"))
    description = models.TextField(null=True, blank=True, verbose_name=_("توضیحات سئو"))

    class Meta:
        verbose_name = _("دسته‌بندی")
        verbose_name_plural = _("دسته‌بندی‌ها")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(TimeStampedModel):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products',
                                 verbose_name=_("دسته‌بندی"))
    name = models.CharField(max_length=200, verbose_name=_("نام مدل دستگاه"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, verbose_name=_("نامک"))
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("کد محصول (SKU)"))
    main_image = models.ImageField(upload_to='products/main/', verbose_name=_("تصویر اصلی"))
    video_url = models.URLField(null=True, blank=True, verbose_name=_("لینک ویدیو"))
    video_file = models.FileField(upload_to='products/videos/', null=True, blank=True, verbose_name=_("فایل ویدیو"))
    base_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name=_("قیمت پایه"))
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name=_("واحد پولی"))
    show_price = models.BooleanField(default=True, verbose_name=_("نمایش قیمت؟"))
    is_in_stock = models.BooleanField(default=True, verbose_name=_("موجود؟"))
    warranty_months = models.PositiveIntegerField(default=12, verbose_name=_("گارانتی (ماه)"))
    short_description = models.TextField(verbose_name=_("توضیح کوتاه"))
    full_description = models.TextField(verbose_name=_("نقد و بررسی"))
    meta_title = models.CharField(max_length=60, null=True, blank=True, verbose_name=_("عنوان سئو"))
    meta_description = models.CharField(max_length=160, null=True, blank=True, verbose_name=_("توضیحات متا"))

    class Meta:
        verbose_name = _("محصول")
        verbose_name_plural = _("محصولات")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, null=True, blank=True)


class SpecificationGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نام گروه"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب نمایش"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("گروه مشخصات فنی")
        verbose_name_plural = _("گروه‌های مشخصات فنی")

    def __str__(self):
        return self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    group = models.ForeignKey(SpecificationGroup, on_delete=models.PROTECT)
    key = models.CharField(max_length=100, verbose_name=_("عنوان ویژگی"))
    value = models.CharField(max_length=255, verbose_name=_("مقدار"))


class ProductDocument(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100, verbose_name=_("عنوان فایل"))
    file = models.FileField(upload_to='products/documents/')
    document_type = models.CharField(max_length=50,
                                     choices=[('catalog', 'کاتالوگ'), ('manual', 'دفترچه'), ('software', 'نرم‌افزار')],
                                     default='catalog')


# --- وبلاگ و محتوا ---
class BlogCategory(TimeStampedModel):
    title = models.CharField(max_length=100, verbose_name=_("عنوان"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    meta_title = models.CharField(max_length=60, null=True, blank=True, verbose_name=_("عنوان سئو"))
    meta_description = models.CharField(max_length=160, null=True, blank=True, verbose_name=_("توضیحات متا"))

    class Meta:
        verbose_name = _("دسته‌بندی مقاله")
        verbose_name_plural = _("دسته‌بندی‌های مقالات")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Article(TimeStampedModel):
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='articles')
    title = models.CharField(max_length=250, verbose_name=_("عنوان مقاله"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True)
    image = models.ImageField(upload_to='blog/', verbose_name=_("تصویر شاخص"))
    content = CKEditor5Field('محتوا', config_name='extends')
    is_published = models.BooleanField(default=True, verbose_name=_("منتشر شده"))
    meta_title = models.CharField(max_length=60, null=True, blank=True, verbose_name=_("عنوان سئو"))
    meta_description = models.CharField(max_length=160, null=True, blank=True, verbose_name=_("توضیحات متا"))

    class Meta:
        verbose_name = _("مقاله")
        verbose_name_plural = _("مقالات")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


# --- سایر بخش‌های برندینگ ---
class ConsultationRequest(TimeStampedModel):
    full_name = models.CharField(max_length=150, verbose_name=_("نام"))
    phone_number = models.CharField(max_length=20, verbose_name=_("شماره"))
    company_name = models.CharField(max_length=150, blank=True, verbose_name=_("شرکت"))
    power_required = models.CharField(max_length=100, blank=True, verbose_name=_("توان (kVA)"))
    message = models.TextField(verbose_name=_("پیام"))
    is_checked = models.BooleanField(default=False, verbose_name=_("بررسی شده"))

    class Meta:
        verbose_name = _("درخواست مشاوره")
        verbose_name_plural = _("درخواست‌های مشاوره")


class Partner(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نام سازمان"))
    logo = models.ImageField(upload_to='partners/', verbose_name=_("لوگو"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("همکار تجاری")
        verbose_name_plural = _("همکاران")


class Project(TimeStampedModel):
    title = models.CharField(max_length=200, verbose_name=_("عنوان"))
    location = models.CharField(max_length=100, verbose_name=_("محل اجرا"))
    image = models.ImageField(upload_to='projects/', verbose_name=_("تصویر"))
    description = models.TextField(verbose_name=_("توضیحات"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب"))

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("پروژه موفق")
        verbose_name_plural = _("پروژه‌ها")


class FAQ(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='faqs')
    question = models.CharField(max_length=300, verbose_name=_("پرسش"))
    answer = models.TextField(verbose_name=_("پاسخ"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("سوال متداول")
        verbose_name_plural = _("سوالات متداول")


class Agent(models.Model):
    province = models.CharField(max_length=100, verbose_name=_("استان"))
    city = models.CharField(max_length=100, verbose_name=_("شهر"))
    agent_name = models.CharField(max_length=150, verbose_name=_("نام نماینده"))
    address = models.TextField(verbose_name=_("آدرس"))
    phone = models.CharField(max_length=50, verbose_name=_("تماس"))
    map_link = models.URLField(blank=True, verbose_name=_("لینک نقشه"))

    class Meta:
        verbose_name = _("نماینده")
        verbose_name_plural = _("نمایندگان")