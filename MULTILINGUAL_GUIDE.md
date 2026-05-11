# راهنمای چندزبانه کردن پروژه جنگو

## ✅ تغییرات انجام شده

### 1. مدل StaticText اضافه شد
- **فایل**: `main/models.py`
- یک مدل جدید به نام `StaticText` ایجاد شد که تمام متون ثابت پروژه را مدیریت می‌کند.
- این مدل شامل فیلدهای زیر است:
  - `key`: کلید منحصر به فرد برای هر متن (مثلاً `home_menu_home`)
  - `description`: توضیحات اختیاری درباره متن
  - `text_fa`: متن فارسی
  - `text_en`: متن انگلیسی
  - `text_ar`: متن عربی
  - `text_ru`: متن روسی
  - `default_text`: متن پیش‌فرض (اگر ترجمه‌ای موجود نباشد)

### 2. پنل ادمین آپدیت شد
- **فایل**: `main/admin.py`
- مدل `StaticText` به پنل ادمین اضافه شد با رابط کاربری مناسب برای ویرایش ترجمه‌ها
- در پنل ادمین، بخش **"متون ثابت (ترجمه خودکار)"** را مشاهده خواهید کرد

### 3. تمپلیت تگ get_text آپدیت شد
- **فایل**: `main/templatetags/custom_filters.py`
- تابع `get_text` حالا هم از مدل `StaticText` و هم از `PageTranslation` پشتیبانی می‌کند
- اولویت با `StaticText` است

### 4. متون پیش‌فرض ایجاد شدند
- 41 کلید متنی مختلف برای تمام صفحات پروژه ایجاد شد
- ترجمه‌های فارسی، انگلیسی، عربی و روسی برای همه کلیدها وارد شده است

---

## 📋 نحوه استفاده

### در پنل ادمین

1. وارد پنل ادمین شوید (`/admin/`)
2. به بخش **"متون ثابت (ترجمه خودکار)"** بروید
3. لیست تمام کلیدهای متنی را مشاهده می‌کنید
4. روی هر کدام کلیک کنید و ترجمه‌های زبان‌های مختلف را وارد کنید
5. ذخیره کنید

### در تمپلیت‌های HTML

```html
{% load custom_filters %}

<!-- استفاده ساده -->
<h1>{% get_text 'home_hero_title' %}</h1>
<p>{% get_text 'home_hero_subtitle' %}</p>

<!-- دکمه‌ها -->
<button>{% get_text 'btn_submit' %}</button>
<a href="#">{% get_text 'btn_read_more' %}</a>
```

### کلیدهای موجود

#### منوها
- `home_menu_home` - خانه / Home
- `home_menu_categories` - دسته‌بندی‌ها / Categories
- `home_menu_products` - محصولات / Products
- `home_menu_articles` - مقالات / Articles
- `home_menu_projects` - پروژه‌ها / Projects
- `home_menu_contact` - تماس با ما / Contact Us

#### صفحه اصلی
- `home_hero_title` - تیتر اصلی
- `home_hero_subtitle` - زیرتیتر
- `home_cta_button` - دکمه فراخوان
- `home_section_products` - بخش محصولات
- `home_section_categories` - بخش دسته‌بندی‌ها
- `home_section_articles` - بخش مقالات
- `home_section_projects` - بخش پروژه‌ها
- `home_section_partners` - بخش همکاران

#### محصولات
- `product_detail_title` - عنوان صفحه محصول
- `product_detail_description` - توضیحات
- `product_detail_specs` - مشخصات فنی
- `product_detail_price` - قیمت
- `product_detail_contact` - درخواست مشاوره
- `product_detail_gallery` - گالری
- `product_detail_documents` - مستندات
- `product_detail_download` - دانلود

#### دسته‌بندی
- `category_products_count` - تعداد محصولات
- `category_filter` - فیلتر
- `category_sort` - مرتب‌سازی

#### فرم‌ها
- `label_name` - نام
- `label_email` - ایمیل
- `label_phone` - شماره تماس
- `label_message` - پیام
- `form_required` - الزامی
- `form_success` - پیام موفقیت
- `form_error` - پیام خطا
- `btn_submit` - ارسال
- `btn_cancel` - انصراف

#### عمومی
- `btn_read_more` - ادامه مطلب
- `btn_back` - بازگشت
- `header_toggle_theme` - تغییر تم
- `footer_all_rights` - کپی‌رایت
- `footer_contact_us` - تماس با ما (فوتر)
- `footer_quick_links` - لینک‌های سریع
- `footer_about` - درباره ما

---

## ➕ اضافه کردن متن جدید

### روش 1: از طریق Shell (توصیه می‌شود)

```bash
python manage.py shell
```

```python
from main.models import StaticText

# ایجاد متن جدید
obj = StaticText.objects.create(
    key='my_new_text_key',
    default_text='متن پیش‌فرض فارسی',
    text_fa='متن فارسی',
    text_en='English text',
    text_ar='النص العربي',
    text_ru='Текст на русском',
    description='توضیح درباره این متن'
)
```

### روش 2: از طریق پنل ادمین

1. وارد پنل ادمین شوید
2. به بخش "متون ثابت" بروید
3. دکمه "Add" را بزنید
4. کلید منحصر به فرد وارد کنید (مثلاً `contact_page_title`)
5. متن پیش‌فرض و ترجمه‌ها را وارد کنید
6. ذخیره کنید

### روش 3: استفاده از دستور مدیریت سفارشی

می‌توانید یک دستور مدیریت سفارشی ایجاد کنید تا کلیدها را به صورت خودکار از کد استخراج کند.

---

## 🌐 تغییر زبان

کاربران می‌توانند از طریق منوی انتخاب زبان در هدر، زبان را تغییر دهند:
- زبان در session ذخیره می‌شود
- در تمام صفحات اعمال می‌شود
- URL با پارامتر `?lang=xx` آپدیت می‌شود

---

## 🔧 نکات فنی

### اولویت‌بندی ترجمه
1. اول در مدل `StaticText` جستجو می‌شود
2. اگر نبود، در مدل `PageTranslation` جستجو می‌شود
3. اگر هیچکدام نبود، کلید برگردانده می‌شود

### پرفورمنس
- برای کاهش کوئری‌های دیتابیس، می‌توانید از cache استفاده کنید
- در حال حاضر هر بار کوئری زده می‌شود

### افزودن زبان جدید
برای اضافه کردن زبان جدید (مثلاً آلمانی):

1. در مدل `StaticText` فیلد جدید اضافه کنید:
```python
text_de = models.TextField(blank=True, null=True, verbose_name="Deutsch")
```

2. Migration بسازید:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. در `custom_filters.py` کد زبان را اضافه کنید:
```python
lang_map = {
    'fa-ir': 'fa',
    'en-us': 'en',
    'de-de': 'de',  # جدید
    ...
}
```

4. در تمپلیت تگ `get_text` فیلد جدید را اضافه کنید

---

## 📝 نمونه کد کامل

### در view:
```python
def home_view(request):
    return render(request, 'main/home.html', {
        'current_lang': request.LANGUAGE_CODE or 'fa',
    })
```

### در تمپلیت:
```html
{% extends 'base.html' %}
{% load custom_filters %}

{% block content %}
<h1>{% get_text 'home_hero_title' %}</h1>
<p>{% get_text 'home_hero_subtitle' %}</p>
<a href="#contact">{% get_text 'home_cta_button' %}</a>
{% endblock %}
```

---

## ✨ مزایا

1. **عدم نیاز به هاردکد**: تمام متون در دیتابیس هستند
2. **ویرایش آسان**: فقط کافیست در پنل ادمین ترجمه را وارد کنید
3. **پشتیبانی از 4 زبان**: فارسی، انگلیسی، عربی، روسی
4. **قابل گسترش**: به راحتی می‌توان زبان جدید اضافه کرد
5. **بدون نیاز به فایل .po**: همه چیز در دیتابیس است
6. **SEO Friendly**: هر زبان URL مخصوص به خود را دارد

---

## 🎯 قدم بعدی

برای استفاده در صفحات دیگر:
1. کلیدهای جدید را در پنل ادمین ایجاد کنید
2. در تمپلیت‌ها از `{% get_text 'key_name' %}` استفاده کنید
3. ترجمه‌ها را در پنل ادمین وارد کنید

تمام! 🎉
