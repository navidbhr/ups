import os
import django
import random
from decimal import Decimal
from django.core.files import File
import uuid
# ۱. تنظیمات محیط جنگو (مقدار your_project را با نام پوشه تنظیمات خود عوض کنید)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ups.settings")
django.setup()

# ۲. ایمپورت کردن مدل‌ها (نام اپلیکیشن خود را جایگزین your_app کنید)
from main.models import (
    SiteSettings, Branch, Currency, Category, Product, ProductImage,
    SpecificationGroup, ProductSpecification, ProductDocument,
    BlogCategory, Article, Project, Partner, FAQ, HomepageImage, HomeSlider,
    Agent, ContactMessage, ConsultationRequest, ProductConsultationRequest, StaticText
)

# --- متون آماده ---
UPS_SHORT_DESCS = [
    "این دستگاه با تکنولوژی لاین اینتراکتیو و شکل موج سینوسی کامل، انتخابی ایده‌آل است.",
    "یو پی اس آنلاین دابل کانورژن با ضریب توان خروجی 0.9، مناسب برای دیتاسنترها.",
    "طراحی کامپکت و وزن سبک این مدل، آن را به گزینه‌ای اقتصادی تبدیل کرده است."
]

HTML_LONG_DESCS = [
    """
    <h3>بررسی تخصصی و عملکرد</h3>
    <p>در دنیای امروز که وابستگی به تجهیزات الکترونیکی به بالاترین حد خود رسیده است، این دستگاه با بهره‌گیری از جدیدترین تکنولوژی‌های روز دنیا طراحی شده است.</p>
    <ul>
        <li>مجهز به میکروکنترلر DSP جهت پردازش سریع و دقیق</li>
        <li>نمایشگر LCD هوشمند برای نمایش وضعیت باتری</li>
    </ul>
    """,
    """
    <h3>طراحی و ساختار فیزیکی</h3>
    <p>بدنه فلزی مقاوم و طراحی مهندسی شده این سیستم، امکان استفاده از آن را در محیط‌های صنعتی فراهم می‌کند.</p>
    <p>سیستم مدیریت هوشمند باتری (ABM) با کنترل دقیق ولتاژ شارژ، عمر مفید باتری‌ها را تا 50 درصد افزایش می‌دهد.</p>
    """
]

IMAGE_LIST = [
    "102-4320x3240.jpg", "103-2592x1936.jpg", "104-3840x2160.jpg", "106-2592x1728.jpg",
    "107-5000x3333.jpg", "108-2000x1333.jpg", "109-4287x2392.jpg", "110-5000x3333.jpg",
    "111-4400x2656.jpg", "112-4200x2800.jpg", "113-4168x2464.jpg", "114-3264x2448.jpg",
    "115-1500x1000.jpg", "116-3504x2336.jpg", "117-1544x1024.jpg", "118-1500x1000.jpg",
    "119-3264x2176.jpg", "120-4928x3264.jpg", "121-1600x1067.jpg", "122-4147x2756.jpg"
]


def get_random_image():
    img_name = random.choice(IMAGE_LIST)
    img_path = os.path.join('image', img_name)
    if os.path.exists(img_path):
        return img_name, img_path
    return None, None


def assign_image(instance, field_name):
    img_name, img_path = get_random_image()
    if img_path:
        with open(img_path, 'rb') as f:
            getattr(instance, field_name).save(img_name, File(f), save=False)


def create_dummy_file():
    file_path = "dummy_doc.txt"
    # انکودینگ utf-8 برای جلوگیری از خطای charmap
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("دفترچه راهنما و کاتالوگ فنی دستگاه\nلطفا برای اطلاعات بیشتر با پشتیبانی تماس بگیرید.")
    return file_path


def run_seeder():
    print("شروع فرآیند ساخت دیتای تستی کامل (همراه با تمام مدل‌ها)... 🚀")

    # 1. تنظیمات و متون ثابت
    print("- تنظیم متون ثابت و تنظیمات سایت...")
    StaticText.objects.get_or_create_from_code('hero_title', 'راهکارهای نوین برق اضطراری', 'تیتر اصلی سایت')
    StaticText.objects.get_or_create_from_code('hero_subtitle', 'تولیدکننده برتر انواع یو پی اس در ایران',
                                               'زیر تیتر سایت')
    StaticText.objects.get_or_create_from_code('cta_text', 'مشاوره رایگان', 'دکمه فراخوان')

    if not SiteSettings.objects.exists():
        settings = SiteSettings(
            site_name="برهان یو پی اس",
            site_title="تولید و عرضه انواع UPS",
            site_description="شرکت برهان پیشرو در ارائه راهکارهای برق اضطراری."
        )
        assign_image(settings, 'logo')
        assign_image(settings, 'favicon')
        settings.save()

    # 2. ارز و شعب
    currency, _ = Currency.objects.get_or_create(name="تومان", symbol="T", is_base=True, exchange_rate=1.0)
    Branch.objects.get_or_create(name="دفتر مرکزی (تهران)", address="تهران، ولیعصر", phone="021-88888888", is_main=True)

    # 3. نمایندگان فروش (Agent)
    print("- در حال ایجاد نمایندگان فروش...")
    agents_data = [
        ("تهران", "تهران", "گروه مهندسی نیرو", "خیابان لاله زار جنوبی، پلاک ۱۲", "021-33333333"),
        ("اصفهان", "اصفهان", "الکتریک سپاهان", "خیابان فردوسی، مجتمع برق", "031-32222222"),
        ("خراسان رضوی", "مشهد", "توس نیرو", "خیابان سناباد، چهارراه دکترا", "051-38888888"),
        ("آذربایجان شرقی", "تبریز", "آذر ولتاژ", "خیابان شریعتی، مجتمع تجاری", "041-35555555")
    ]
    for prov, city, name, addr, phone in agents_data:
        Agent.objects.get_or_create(province=prov, city=city, agent_name=name, address=addr, phone=phone)

    # 4. دسته‌بندی و محصولات
    categories = []
    for title in ["یو پی اس آنلاین", "یو پی اس لاین اینتراکتیو", "استابلایزر", "باتری یو پی اس"]:
        cat, _ = Category.objects.get_or_create(title=title)
        assign_image(cat, 'image')
        cat.save()
        categories.append(cat)

    spec_group, _ = SpecificationGroup.objects.get_or_create(name="مشخصات فنی دستگاه", order=1)
    dummy_file_path = create_dummy_file()

    print("- در حال ایجاد ۲۰ محصول با تمام جزئیات و سوالات متداول...")
    products_list = []
    for i in range(1, 21):
        product = Product(
            category=random.choice(categories),
            name=f"دستگاه UPS مدل BR-{i}KVA",
            sku=f"BRH-{uuid.uuid4().hex[:6].upper()}-{i}",
            base_price=Decimal(random.randint(10, 300) * 1000000),
            currency=currency,
            short_description=random.choice(UPS_SHORT_DESCS),
            full_description=random.choice(HTML_LONG_DESCS)
        )
        assign_image(product, 'main_image')
        product.save()
        products_list.append(product)

        # گالری محصول
        for j in range(2):
            p_img = ProductImage(product=product, alt_text="نمای دستگاه")
            assign_image(p_img, 'image')
            p_img.save()

        # مشخصات فنی و داکیومنت و FAQ
        ProductSpecification.objects.create(product=product, group=spec_group, key="ولتاژ", value="220V")
        with open(dummy_file_path, 'rb') as f:
            ProductDocument.objects.create(product=product, title="کاتالوگ", file=File(f, name=f"cat_{i}.txt"))
        FAQ.objects.create(product=product, question=f"گارانتی مدل {product.name} چقدر است؟",
                           answer="این دستگاه دارای ۲۴ ماه گارانتی تعویض است.")

    # 5. مقالات وبلاگ و پروژه‌ها
    print("- در حال ایجاد مقالات و پروژه‌ها...")
    blog_cat, _ = BlogCategory.objects.get_or_create(title="مقالات فنی")
    for i in range(1, 11):
        article = Article(category=blog_cat, title_fa=f"مقاله تخصصی شماره {i}", content_fa=HTML_LONG_DESCS[0])
        assign_image(article, 'image')
        article.save()

        project = Project(title_fa=f"پروژه نصب در سازمان {i}", location_fa="تهران", description_fa="شرح اجرای پروژه.")
        assign_image(project, 'image')
        project.save()

    # 6. همکاران تجاری (Partner) - با دیتای بیشتر
    print("- در حال ایجاد همکاران تجاری...")
    partner_names = ["بانک ملی ایران", "بیمارستان میلاد", "شرکت نفت پارس", "دانشگاه تهران", "همراه اول", "ایرانسل",
                     "شرکت مپنا", "وزارت راه و شهرسازی"]
    for i, p_name in enumerate(partner_names):
        partner, created = Partner.objects.get_or_create(name=p_name, defaults={'order': i})
        if created:
            assign_image(partner, 'logo')
            partner.save()

    # 7. تصاویر صفحه اصلی (HomepageImage) و اسلایدر
    print("- در حال تنظیم تصاویر پوسته سایت و اسلایدر...")
    for sec in ['hero', 'about', 'products', 'projects', 'partners']:
        h_img = HomepageImage(title=f"تصویر دمو برای بخش {sec}", section=sec)
        assign_image(h_img, 'image')
        h_img.save()

    for i in range(1, 4):
        slider = HomeSlider(title_fa=f"اسلاید جشنواره {i}", subtitle_fa="فروش ویژه با شرایط استثنایی")
        assign_image(slider, 'image')
        slider.save()

    # 8. ایجاد داده‌های فرم‌ها (درخواست‌ها و پیام‌ها)
    print("- در حال ایجاد پیام‌های تستی کاربران...")
    for i in range(1, 15):
        # پیام تماس
        ContactMessage.objects.create(
            full_name=f"کاربر تستی {i}",
            phone_number=f"0912{random.randint(1000000, 9999999)}",
            message="سلام، لطفا لیست قیمت همکار را برای من ارسال کنید."
        )
        # درخواست مشاوره عمومی
        ConsultationRequest.objects.create(
            full_name=f"شرکت تستی {i}",
            phone_number=f"021{random.randint(10000000, 99999999)}",
            power_required=f"{random.randint(10, 100)} kVA",
            message="برای دیتاسنتر نیاز به مشاوره توان‌سنجی داریم."
        )
        # درخواست مشاوره روی یک محصول خاص
        if products_list:
            ProductConsultationRequest.objects.create(
                product=random.choice(products_list),
                full_name=f"خریدار {i}",
                phone_number=f"0935{random.randint(1000000, 9999999)}",
                quantity_needed=str(random.randint(1, 5)),
                message="این مدل موجود است؟"
            )

    # پاک کردن فایل متنی موقت
    if os.path.exists(dummy_file_path):
        os.remove(dummy_file_path)

    print("✅ تمام مدل‌های سیستم شما با موفقیت با داده‌های غنی و منطقی پر شدند!")


if __name__ == "__main__":
    run_seeder()