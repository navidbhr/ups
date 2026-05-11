from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field


def generate_unique_slug(model_class, field_value, instance_pk=None):
    """
    تابع کمکی برای تولید slug یکتا و جلوگیری از خطای دیتابیس هنگام نام‌های تکراری
    """
    base_slug = slugify(field_value, allow_unicode=True) or "item"
    unique_slug = base_slug
    num = 1
    qs = model_class.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=unique_slug).exists():
        unique_slug = f"{base_slug}-{num}"
        num += 1
    return unique_slug


# --- کلاس پایه برای مدیریت زمان ---
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))

    class Meta:
        abstract = True


# --- مدیریت متون ثابت صفحات در ۴ زبان ---
class PageTranslation(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True, help_text=_("مثال: home_welcome_message یا footer_about"), verbose_name=_("کلید متن"))
    text_fa = models.TextField(verbose_name=_("متن (فارسی)"))
    text_en = models.TextField(blank=True, verbose_name=_("متن (انگلیسی)"))
    text_ar = models.TextField(blank=True, verbose_name=_("متن (عربی)"))
    text_ru = models.TextField(blank=True, verbose_name=_("متن (روسی)"))

    class Meta:
        verbose_name = _("ترجمه متن صفحه")
        verbose_name_plural = _("ترجمه متون صفحات")

    def __str__(self):
        return self.key

    @classmethod
    def get_text(cls, key, lang_code):
        """دریافت متن بر اساس زبان"""
        try:
            obj = cls.objects.get(key=key)
            field_map = {
                'fa': 'text_fa',
                'en': 'text_en',
                'ar': 'text_ar',
                'ru': 'text_ru',
            }
            field_name = field_map.get(lang_code, 'text_fa')
            text = getattr(obj, field_name, None)
            
            if text:
                return text
            # اگر ترجمه نبود، متن فارسی را برگردان
            return obj.text_fa or key
        except cls.DoesNotExist:
            return key


# --- مدیریت خودکار متون ثابت ---
class StaticTextManager(models.Manager):
    """مدیریت خودکار برای ایجاد کلیدهای متون ثابت"""
    
    def get_or_create_from_code(self, key, default_text="", description=""):
        """ایجاد خودکار کلید اگر وجود نداشته باشد"""
        obj, created = self.get_or_create(
            key=key,
            defaults={
                'default_text': default_text,
                'description': description,
                'text_fa': default_text,  # پیش‌فرض فارسی است
            }
        )
        return obj


class StaticText(TimeStampedModel):
    """
    مدل برای مدیریت تمام متون ثابت پروژه.
    شما فقط نیاز دارید متن و ترجمه آن را در پنل ادمین وارد کنید.
    کلیدها به صورت خودکار شناسایی می‌شوند.
    """
    key = models.CharField(max_length=255, unique=True, verbose_name=_("کلید متن"))
    description = models.CharField(max_length=500, blank=True, verbose_name=_("توضیحات"))
    
    # فیلدهای ترجمه
    text_fa = models.TextField(blank=True, null=True, verbose_name="فارسی")
    text_en = models.TextField(blank=True, null=True, verbose_name="English")
    text_ar = models.TextField(blank=True, null=True, verbose_name="العربية")
    text_ru = models.TextField(blank=True, null=True, verbose_name="Русский")
    
    # فیلد پیش‌فرض (اگر ترجمه‌ای نباشد، این نمایش داده می‌شود)
    default_text = models.TextField(blank=True, null=True, verbose_name=_("متن پیش‌فرض"))
    
    objects = StaticTextManager()

    class Meta:
        verbose_name = _("متن ثابت")
        verbose_name_plural = _("متون ثابت (ترجمه خودکار)")
        ordering = ['key']

    def __str__(self):
        display_text = self.default_text[:30] if self.default_text else 'No default'
        return f"{self.key} - {display_text}"

    @classmethod
    def get_text(cls, key, lang_code):
        """دریافت متن بر اساس زبان"""
        try:
            obj = cls.objects.get(key=key)
            field_map = {
                'fa': 'text_fa',
                'en': 'text_en',
                'ar': 'text_ar',
                'ru': 'text_ru',
            }
            field_name = field_map.get(lang_code, 'default_text')
            text = getattr(obj, field_name, None)
            
            if text:
                return text
            return obj.default_text or key
        except cls.DoesNotExist:
            # اگر رکورد وجود نداشت، کلید را برگردان
            return key


# --- تنظیمات سیستمی (Singleton) ---
class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="برهان یو پی اس", verbose_name=_("نام برند"))
    site_title = models.CharField(max_length=200, default="تولید و عرضه انواع UPS", verbose_name=_("عنوان سئو (Title Tag)"))
    site_description = models.TextField(default="مشاوره و خرید انواع دستگاه‌های یو پی اس...", verbose_name=_("توضیحات متا (Meta Description)"))
    keywords = models.CharField(max_length=500, blank=True, verbose_name=_("کلمات کلیدی (با کاما جدا کنید)"))
    logo = models.ImageField(upload_to='settings/', verbose_name=_("لوگوی رنگی (هدر)"))
    logo_light = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_("لوگوی سفید (فوتر)"))
    favicon = models.ImageField(upload_to='settings/', verbose_name=_("فاوآیکون"))

    hero_title = models.CharField(max_length=200, default="تامین انرژی پایدار با برهان", blank=True, verbose_name=_("تیتر بزرگ صفحه اصلی"))
    hero_subtitle = models.TextField(default="ارائه دهنده پیشرفته‌ترین سیستم‌های تامین برق اضطراری", blank=True, verbose_name=_("متن زیر تیتر صفحه اصلی"))
    hero_image = models.ImageField(upload_to='settings/', blank=True, verbose_name=_("تصویر بخش Hero"))
    cta_text = models.CharField(max_length=50, default="درخواست مشاوره", blank=True, verbose_name=_("متن دکمه فراخوان (CTA)"))
    cta_link = models.CharField(max_length=200, default="#consultation", blank=True, verbose_name=_("لینک دکمه فراخوان"))

    about_summary = models.TextField(default="شرکت برهان پیشرو در ارائه راهکارهای برق اضطراری...", blank=True, verbose_name=_("خلاصه درباره ما"))

    # فیلدهای مربوط به آدرس و شماره تماس حذف و به مدل Branch منتقل شدند

    instagram = models.URLField(blank=True, verbose_name=_("اینستاگرام"))
    telegram = models.URLField(blank=True, verbose_name=_("تلگرام"))
    linkedin = models.URLField(blank=True, verbose_name=_("لینکدین"))

    is_maintenance_mode = models.BooleanField(default=False, verbose_name=_("حالت تعمیر"))
    footer_copy_right = models.CharField(max_length=255, default="تمامی حقوق برای شرکت برهان محفوظ است.", verbose_name=_("متن کپی‌رایت"))
    google_analytics_id = models.CharField(max_length=50, blank=True, verbose_name=_("Google Analytics ID"))

    class Meta:
        verbose_name = _("تنظیمات کلی سایت")
        verbose_name_plural = _("تنظیمات کلی سایت")

    def clean(self):
        # خطای منطقی قبلی: این بررسی نباید در save باشد، بلکه باید در clean باشد تا فرم ادمین بتواند خطا را به درستی نمایش دهد
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_("شما نمی‌توانید بیش از یک رکورد تنظیمات بسازید."))

    def __str__(self):
        return self.site_name


# --- مدیریت شعب شرکت ---
class Branch(TimeStampedModel):
    name = models.CharField(max_length=100, verbose_name=_("نام شعبه (مثلا دفتر مرکزی)"))
    address = models.TextField(verbose_name=_("آدرس فیزیکی"))
    phone = models.CharField(max_length=50, verbose_name=_("شماره تماس"))
    email = models.EmailField(verbose_name=_("ایمیل شعبه"), blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name=_("شماره مستقیم واتس‌اپ"))
    map_iframe = models.TextField(blank=True, verbose_name=_("کد Iframe نقشه گوگل"))
    is_main = models.BooleanField(default=False, verbose_name=_("شعبه مرکزی"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب نمایش"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("شعبه")
        verbose_name_plural = _("شعب")

    def clean(self):
        if self.is_main:
            qs = Branch.objects.filter(is_main=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(_("تنها یک شعبه می‌تواند به عنوان شعبه مرکزی ثبت شود."))

    def __str__(self):
        return f"{self.name} {'(مرکزی)' if self.is_main else ''}"


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
            self.slug = generate_unique_slug(Category, self.title, self.pk)
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
            self.slug = generate_unique_slug(Product, self.name, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery', verbose_name=_("محصول"))
    image = models.ImageField(upload_to='products/gallery/', verbose_name=_("تصویر"))
    alt_text = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("متن جایگزین (Alt)"))
    
    class Meta:
        verbose_name = _("تصویر گالری محصول")
        verbose_name_plural = _("گالری تصاویر محصولات")


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications', verbose_name=_("محصول"))
    group = models.ForeignKey(SpecificationGroup, on_delete=models.PROTECT, verbose_name=_("گروه مشخصات"))
    key = models.CharField(max_length=100, verbose_name=_("عنوان ویژگی"))
    value = models.CharField(max_length=255, verbose_name=_("مقدار"))

    class Meta:
        verbose_name = _("مشخصه فنی")
        verbose_name_plural = _("مشخصات فنی")
        unique_together = ('product', 'key')


class ProductDocument(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='documents', verbose_name=_("محصول"))
    title = models.CharField(max_length=100, verbose_name=_("عنوان فایل"))
    file = models.FileField(upload_to='products/documents/', verbose_name=_("فایل"))
    document_type = models.CharField(max_length=50,
                                     choices=[('catalog', 'کاتالوگ'), ('manual', 'دفترچه'), ('software', 'نرم‌افزار')],
                                     default='catalog', verbose_name=_("نوع مستند"))

    class Meta:
        verbose_name = _("مستند محصول")
        verbose_name_plural = _("مستندات محصولات")


# --- وبلاگ و محتوا ---
class BlogCategory(TimeStampedModel):
    title = models.CharField(max_length=100, verbose_name=_("عنوان"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, verbose_name=_("نامک"))
    meta_title = models.CharField(max_length=60, null=True, blank=True, verbose_name=_("عنوان سئو"))
    meta_description = models.CharField(max_length=160, null=True, blank=True, verbose_name=_("توضیحات متا"))

    class Meta:
        verbose_name = _("دسته‌بندی مقاله")
        verbose_name_plural = _("دسته‌بندی‌های مقالات")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(BlogCategory, self.title, self.pk)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Article(TimeStampedModel):
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name=_("دسته‌بندی"))
    title = models.CharField(max_length=250, verbose_name=_("عنوان مقاله"))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, verbose_name=_("نامک"))
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
            self.slug = generate_unique_slug(Article, self.title, self.pk)
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
        ordering = ['-created_at']
        verbose_name = _("درخواست مشاوره")
        verbose_name_plural = _("درخواست‌های مشاوره")


class ProductConsultationRequest(TimeStampedModel):
    """مدل برای درخواست مشاوره مخصوص هر محصول"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='consultation_requests', verbose_name=_("محصول"))
    full_name = models.CharField(max_length=150, verbose_name=_("نام و نام خانوادگی"))
    phone_number = models.CharField(max_length=20, verbose_name=_("شماره تماس"))
    email = models.EmailField(blank=True, verbose_name=_("ایمیل"))
    company_name = models.CharField(max_length=150, blank=True, verbose_name=_("نام شرکت/سازمان"))
    quantity_needed = models.CharField(max_length=50, blank=True, verbose_name=_("تعداد مورد نیاز"))
    application = models.CharField(max_length=200, blank=True, verbose_name=_("کاربرد مورد نظر"))
    message = models.TextField(blank=True, verbose_name=_("پیام اضافی"))
    is_checked = models.BooleanField(default=False, verbose_name=_("بررسی شده"))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("درخواست مشاوره محصول")
        verbose_name_plural = _("درخواست‌های مشاوره محصولات")

    def __str__(self):
        return f"{self.full_name} - {self.product.name}"


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='faqs', verbose_name=_("محصول"))
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
    
    # اضافه کردن فیلدهای زمان به صورت دستی با مقدار دیفالت برای رفع ارور مایگریشن
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ بروزرسانی"))

    class Meta:
        verbose_name = _("نماینده")
        verbose_name_plural = _("نمایندگان")


# --- مدیریت تصاویر صفحه اصلی ---
class HomepageImage(models.Model):
    """مدل برای مدیریت عکس‌های صفحه اصلی از پنل ادمین"""
    title = models.CharField(max_length=100, verbose_name=_("عنوان تصویر"))
    image = models.ImageField(upload_to='homepage/', verbose_name=_("تصویر"))
    section = models.CharField(
        max_length=50,
        choices=[
            ('hero', 'بخش Hero'),
            ('about', 'بخش درباره ما'),
            ('products', 'بخش محصولات'),
            ('projects', 'بخش پروژه‌ها'),
            ('partners', 'بخش همکاران'),
        ],
        default='hero',
        verbose_name=_("بخش در صفحه")
    )
    description = models.CharField(max_length=255, blank=True, verbose_name=_("توضیحات"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب نمایش"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("تصویر صفحه اصلی")
        verbose_name_plural = _("تصاویر صفحه اصلی")

    def __str__(self):
        return f"{self.title} - {self.get_section_display()}"


# --- اسلایدر صفحه اصلی ---
class HomeSlider(models.Model):
    """مدل برای اسلایدر متحرک در صفحه اصلی"""
    title_fa = models.CharField(max_length=200, verbose_name=_("عنوان (فارسی)"))
    title_en = models.CharField(max_length=200, blank=True, verbose_name=_("عنوان (انگلیسی)"))
    title_ar = models.CharField(max_length=200, blank=True, verbose_name=_("عنوان (عربی)"))
    title_ru = models.CharField(max_length=200, blank=True, verbose_name=_("عنوان (روسی)"))
    
    subtitle_fa = models.TextField(blank=True, verbose_name=_("زیرعنوان (فارسی)"))
    subtitle_en = models.TextField(blank=True, verbose_name=_("زیرعنوان (انگلیسی)"))
    subtitle_ar = models.TextField(blank=True, verbose_name=_("زیرعنوان (عربی)"))
    subtitle_ru = models.TextField(blank=True, verbose_name=_("زیرعنوان (روسی)"))
    
    image = models.ImageField(upload_to='slider/', verbose_name=_("تصویر اسلاید"))
    link = models.CharField(max_length=200, blank=True, verbose_name=_("لینک"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))

    class Meta:
        ordering = ['order', 'id']
        verbose_name = _("اسلاید صفحه اصلی")
        verbose_name_plural = _("اسلایدر صفحه اصلی")

    def __str__(self):
        return self.title_fa
