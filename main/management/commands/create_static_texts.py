from django.core.management.base import BaseCommand
from main.models import StaticText


class Command(BaseCommand):
    help = 'ایجاد کلیدهای متون استاتیک برای صفحه اصلی و Hero Section'

    def handle(self, *args, **kwargs):
        static_texts = [
            # Hero Section - جدیدترین اضافه شده
            {'key': 'hero_title', 'default_text': 'تامین انرژی پایدار با برهان',
             'text_fa': 'تامین انرژی پایدار با برهان', 'text_en': 'Sustainable Energy with Borhan',
             'text_ar': 'توفير الطاقة المستدامة مع برهان', 'text_ru': 'Ustoychivaya energiya s Borhan'},
            {'key': 'hero_subtitle',
             'default_text': 'ارائه دهنده پیشرفته‌ترین سیستم‌های تامین برق اضطراری در ایران با گارانتی معتبر و پشتیبانی ۲۴ ساعته',
             'text_fa': 'ارائه دهنده پیشرفته‌ترین سیستم‌های تامین برق اضطراری در ایران با گارانتی معتبر و پشتیبانی ۲۴ ساعته',
             'text_en': 'Provider of advanced emergency power systems in Iran with valid warranty and 24/7 support',
             'text_ar': 'مقدم لأحدث أنظمة إمداد الطاقة الطارئة في إيران مع ضمان صالح ودعم على مدار الساعة',
             'text_ru': 'Postavshchik peredovykh sistem avariynogo elektrosnabzheniya v Irane s deystvitelnoy garantiey i podderzhkoy 24/7'},
            {'key': 'cta_text', 'default_text': 'درخواست مشاوره رایگان', 'text_fa': 'درخواست مشاوره رایگان',
             'text_en': 'Request Free Consultation', 'text_ar': 'طلب استشارة مجانية',
             'text_ru': 'Zaprosit besplatnuyu konsultatsiyu'},

            # Hero Stats
            {'key': 'hero_stats_experience', 'default_text': 'سال تجربه', 'text_fa': 'سال تجربه',
             'text_en': 'Years of Experience', 'text_ar': 'سنوات الخبرة', 'text_ru': 'Let opyta'},
            {'key': 'hero_stats_projects', 'default_text': 'پروژه موفق', 'text_fa': 'پروژه موفق',
             'text_en': 'Successful Projects', 'text_ar': 'مشاريع ناجحة', 'text_ru': 'Uspeshnye proekty'},
            {'key': 'hero_stats_customers', 'default_text': 'مشتری راضی', 'text_fa': 'مشتری راضی',
             'text_en': 'Satisfied Customers', 'text_ar': 'عملاء راضون', 'text_ru': 'Dovolnyye klijenty'},

            # Hero Badges
            {'key': 'hero_badge_warranty', 'default_text': 'گارانتی معتبر', 'text_fa': 'گارانتی معتبر',
             'text_en': 'Valid Warranty', 'text_ar': 'ضمان صالح', 'text_ru': 'Deystvitelnaya garantiya'},
            {'key': 'hero_badge_warranty_value', 'default_text': 'تا ۳۶ ماه', 'text_fa': 'تا ۳۶ ماه',
             'text_en': 'Up to 36 Months', 'text_ar': 'حتى ٣٦ شهراً', 'text_ru': 'Do 36 mesyatsev'},
            {'key': 'hero_badge_support', 'default_text': 'پشتیبانی', 'text_fa': 'پشتیبانی', 'text_en': 'Support',
             'text_ar': 'الدعم', 'text_ru': 'Podderzhka'},
            {'key': 'hero_badge_support_value', 'default_text': '۲۴/۷', 'text_fa': '۲۴/۷', 'text_en': '24/7',
             'text_ar': '٢٤/٧', 'text_ru': '24/7'},

            # Categories
            {'key': 'categories_title', 'default_text': 'دسته‌بندی محصولات', 'text_fa': 'دسته‌بندی محصولات',
             'text_en': 'Product Categories', 'text_ar': 'فئات المنتجات', 'text_ru': 'Kategorii produktov'},
            {'key': 'categories_subtitle', 'default_text': 'انواع دستگاه‌های UPS را بر اساس کاربرد مشاهده کنید',
             'text_fa': 'انواع دستگاه‌های UPS را بر اساس کاربرد مشاهده کنید',
             'text_en': 'Browse UPS devices by application', 'text_ar': 'تصفح أجهزة UPS حسب التطبيق',
             'text_ru': 'Prosmotrite UPS-ustroystva po primeneniyu'},
            {'key': 'category_placeholder_title', 'default_text': 'عنوان دسته‌بندی', 'text_fa': 'عنوان دسته‌بندی',
             'text_en': 'Category Title', 'text_ar': 'عنوان الفئة', 'text_ru': 'Nazvaniye kategorii'},
            {'key': 'category_placeholder_desc', 'default_text': 'توضیحات دسته‌بندی', 'text_fa': 'توضیحات دسته‌بندی',
             'text_en': 'Category Description', 'text_ar': 'وصف الفئة', 'text_ru': 'Opisaniye kategorii'},

            # Products
            {'key': 'products_title', 'default_text': 'محصولات ویژه', 'text_fa': 'محصولات ویژه',
             'text_en': 'Featured Products', 'text_ar': 'المنتجات المميزة', 'text_ru': 'Osobyye produkty'},
            {'key': 'products_subtitle', 'default_text': 'برترین دستگاه‌های یو پی اس با گارانتی معتبر',
             'text_fa': 'برترین دستگاه‌های یو پی اس با گارانتی معتبر', 'text_en': 'Top UPS devices with valid warranty',
             'text_ar': 'أفضل أجهزة UPS مع ضمان صالح', 'text_ru': 'Luchshiye UPS-ustroystva s deystvitelnoy garantiey'},
            {'key': 'product_placeholder_title', 'default_text': 'نام محصول', 'text_fa': 'نام محصول',
             'text_en': 'Product Name', 'text_ar': 'اسم المنتج', 'text_ru': 'Nazvaniye produkta'},
            {'key': 'product_placeholder_desc', 'default_text': 'توضیحات محصول', 'text_fa': 'توضیحات محصول',
             'text_en': 'Product Description', 'text_ar': 'وصف المنتج', 'text_ru': 'Opisaniye produkta'},
            {'key': 'product_placeholder_price', 'default_text': 'تماس بگیرید', 'text_fa': 'تماس بگیرید',
             'text_en': 'Call for Price', 'text_ar': 'اتصل للسعر', 'text_ru': 'Pozvonite dlya tseny'},
            {'key': 'view_all_products', 'default_text': 'مشاهده همه محصولات', 'text_fa': 'مشاهده همه محصولات',
             'text_en': 'View All Products', 'text_ar': 'عرض جميع المنتجات', 'text_ru': 'Posmotret vse produkty'},

            # Articles/Blog
            {'key': 'articles_title', 'default_text': 'مقالات و اخبار', 'text_fa': 'مقالات و اخبار',
             'text_en': 'Articles & News', 'text_ar': 'المقالات والأخبار', 'text_ru': 'Statyi i novosti'},
            {'key': 'articles_subtitle', 'default_text': 'آخرین مطالب و اخبار صنعت یو پی اس',
             'text_fa': 'آخرین مطالب و اخبار صنعت یو پی اس', 'text_en': 'Latest articles and news from UPS industry',
             'text_ar': 'آخر المقالات وأخبار صناعة UPS', 'text_ru': 'Posledniye statyi i novosti industrii UPS'},
            {'key': 'article_placeholder_title', 'default_text': 'عنوان مقاله', 'text_fa': 'عنوان مقاله',
             'text_en': 'Article Title', 'text_ar': 'عنوان المقال', 'text_ru': 'Nazvaniye statyi'},
            {'key': 'article_placeholder_desc', 'default_text': 'خلاصه مقاله', 'text_fa': 'خلاصه مقاله',
             'text_en': 'Article Summary', 'text_ar': 'ملخص المقال', 'text_ru': 'Kratkoye soderzhaniye statyi'},
            {'key': 'back_to_articles', 'default_text': 'بازگشت به مقالات', 'text_fa': 'بازگشت به مقالات',
             'text_en': 'Back to Articles', 'text_ar': 'العودة إلى المقالات', 'text_ru': 'Vernutsya k statyam'},
            {'key': 'related_articles', 'default_text': 'مقالات مرتبط', 'text_fa': 'مقالات مرتبط',
             'text_en': 'Related Articles', 'text_ar': 'مقالات ذات صلة', 'text_ru': 'Svyazannye statyi'},
            {'key': 'no_related', 'default_text': 'بدون مورد مرتبط', 'text_fa': 'بدون مورد مرتبط',
             'text_en': 'No related items', 'text_ar': 'لا توجد عناصر ذات صلة', 'text_ru': 'Net svyazannykh elementov'},

            # Projects
            {'key': 'projects_title', 'default_text': 'پروژه‌های انجام شده', 'text_fa': 'پروژه‌های انجام شده',
             'text_en': 'Completed Projects', 'text_ar': 'المشاريع المنجزة', 'text_ru': 'Zavershennyye proekty'},
            {'key': 'projects_subtitle', 'default_text': 'نمونه کارهای موفق ما در صنایع مختلف',
             'text_fa': 'نمونه کارهای موفق ما در صنایع مختلف',
             'text_en': 'Our successful projects in various industries',
             'text_ar': 'مشاريعنا الناجحة في مختلف الصناعات',
             'text_ru': 'Nashi uspeshnye proekty v razlichnykh otraslyakh'},
            {'key': 'project_placeholder_title', 'default_text': 'عنوان پروژه', 'text_fa': 'عنوان پروژه',
             'text_en': 'Project Title', 'text_ar': 'عنوان المشروع', 'text_ru': 'Nazvaniye proekta'},
            {'key': 'project_placeholder_location', 'default_text': 'موقعیت پروژه', 'text_fa': 'موقعیت پروژه',
             'text_en': 'Project Location', 'text_ar': 'موقع المشروع', 'text_ru': 'Mestopolozheniye proekta'},
            {'key': 'project_placeholder_desc', 'default_text': 'توضیحات پروژه', 'text_fa': 'توضیحات پروژه',
             'text_en': 'Project Description', 'text_ar': 'وصف المشروع', 'text_ru': 'Opisaniye proekta'},
            {'key': 'about_project', 'default_text': 'درباره پروژه', 'text_fa': 'درباره پروژه',
             'text_en': 'About Project', 'text_ar': 'حول المشروع', 'text_ru': 'O proekte'},
            {'key': 'back_to_projects', 'default_text': 'بازگشت به پروژه‌ها', 'text_fa': 'بازگشت به پروژه‌ها',
             'text_en': 'Back to Projects', 'text_ar': 'العودة إلى المشاريع', 'text_ru': 'Vernutsya k proektam'},
            {'key': 'related_projects', 'default_text': 'پروژه‌های مرتبط', 'text_fa': 'پروژه‌های مرتبط',
             'text_en': 'Related Projects', 'text_ar': 'مشاريع ذات صلة', 'text_ru': 'Svyazannye proekty'},

            # Partners
            {'key': 'partners_title', 'default_text': 'همکاران و مشتریان ما', 'text_fa': 'همکاران و مشتریان ما',
             'text_en': 'Our Partners & Customers', 'text_ar': 'شركاؤنا وعملاؤنا',
             'text_ru': 'Nashi partneri i klijenty'},
            {'key': 'partners_subtitle', 'default_text': 'افتخار همکاری با برترین شرکت‌ها',
             'text_fa': 'افتخار همکاری با برترین شرکت‌ها', 'text_en': 'Proud to work with top companies',
             'text_ar': 'نفخر بالتعاون مع أفضل الشركات',
             'text_ru': 'Gordimsya sotrudnichestvom s luchshimi kompaniyami'},
            {'key': 'partner_placeholder', 'default_text': 'نام همکار', 'text_fa': 'نام همکار',
             'text_en': 'Partner Name', 'text_ar': 'اسم الشريك', 'text_ru': 'Imya partnera'},

            # Consultation
            {'key': 'consultation_title', 'default_text': 'درخواست مشاوره رایگان', 'text_fa': 'درخواست مشاوره رایگان',
             'text_en': 'Request Free Consultation', 'text_ar': 'طلب استشارة مجانية',
             'text_ru': 'Zaprosit besplatnuyu konsultatsiyu'},
            {'key': 'consultation_subtitle', 'default_text': 'کارشناسان ما در کمتر از ۲ ساعت با شما تماس می‌گیرند',
             'text_fa': 'کارشناسان ما در کمتر از ۲ ساعت با شما تماس می‌گیرند',
             'text_en': 'Our experts will contact you within 2 hours', 'text_ar': 'سيتصل بك خبراؤنا خلال ساعتين',
             'text_ru': 'Nashi ekspertsvy svyazhemsya s vami v techeniye 2 chasov'},

            # Contact Form
            {'key': 'contact_title', 'default_text': 'تماس با ما', 'text_fa': 'تماس با ما', 'text_en': 'Contact Us',
             'text_ar': 'اتصل بنا', 'text_ru': 'Svyazhites s nami'},
            {'key': 'contact_subtitle', 'default_text': 'سوالات خود را با ما در میان بگذارید',
             'text_fa': 'سوالات خود را با ما در میان بگذارید', 'text_en': 'Share your questions with us',
             'text_ar': 'شارك أسئلتك معنا', 'text_ru': 'Podelites vashimi voprosami s nami'},
            {'key': 'form_name_label', 'default_text': 'نام و نام خانوادگی', 'text_fa': 'نام و نام خانوادگی',
             'text_en': 'Full Name', 'text_ar': 'الاسم الكامل', 'text_ru': 'Polnoye imya'},
            {'key': 'form_name_placeholder', 'default_text': 'مثال: علی محمدی', 'text_fa': 'مثال: علی محمدی',
             'text_en': 'e.g. Ali Mohammadi', 'text_ar': 'مثال: علي محمدي', 'text_ru': 'Naprimyer: Ali Mammadi'},
            {'key': 'form_phone_label', 'default_text': 'شماره تماس', 'text_fa': 'شماره تماس',
             'text_en': 'Phone Number', 'text_ar': 'رقم الهاتف', 'text_ru': 'Nomyer telefona'},
            {'key': 'form_phone_placeholder', 'default_text': 'مثال: ۰۹۱۲۳۴۵۶۷۸۹', 'text_fa': 'مثال: ۰۹۱۲۳۴۵۶۷۸۹',
             'text_en': 'e.g. 09123456789', 'text_ar': 'مثال: ۰۹۱۲۳۴۵۶۷۸۹', 'text_ru': 'Naprimyer: 09123456789'},
            {'key': 'form_company_label', 'default_text': 'نام شرکت (اختیاری)', 'text_fa': 'نام شرکت (اختیاری)',
             'text_en': 'Company Name (Optional)', 'text_ar': 'اسم الشركة (اختياري)',
             'text_ru': 'Nazvaniye kompanii (neobyazatelno)'},
            {'key': 'form_company_placeholder', 'default_text': 'اختیاری', 'text_fa': 'اختیاری', 'text_en': 'Optional',
             'text_ar': 'اختياري', 'text_ru': 'Neobyazatelno'},
            {'key': 'form_power_label', 'default_text': 'توان مورد نیاز (کیلووات)',
             'text_fa': 'توان مورد نیاز (کیلووات)', 'text_en': 'Required Power (kW)',
             'text_ar': 'الطاقة المطلوبة (كيلووات)', 'text_ru': 'Trebuyemaya moshchnost (kW)'},
            {'key': 'form_power_placeholder', 'default_text': 'مثال: ۱۰', 'text_fa': 'مثال: ۱۰', 'text_en': 'e.g. 10',
             'text_ar': 'مثال: ١٠', 'text_ru': 'Naprimyer: 10'},
            {'key': 'form_message_label', 'default_text': 'پیام شما', 'text_fa': 'پیام شما', 'text_en': 'Your Message',
             'text_ar': 'رسالتك', 'text_ru': 'Vashe soobshcheniye'},
            {'key': 'form_message_placeholder', 'default_text': 'توضیحات تکمیلی...', 'text_fa': 'توضیحات تکمیلی...',
             'text_en': 'Additional details...', 'text_ar': 'تفاصيل إضافية...', 'text_ru': 'Dopolnitelnyye detali...'},
            {'key': 'form_submit_button', 'default_text': 'ارسال', 'text_fa': 'ارسال', 'text_en': 'Submit',
             'text_ar': 'إرسال', 'text_ru': 'Otpravit'},

            # Contact Info
            {'key': 'contact_info_title', 'default_text': 'اطلاعات تماس', 'text_fa': 'اطلاعات تماس',
             'text_en': 'Contact Information', 'text_ar': 'معلومات الاتصال', 'text_ru': 'Kontaktnaya informatsiya'},
            {'key': 'contact_address_label', 'default_text': 'آدرس:', 'text_fa': 'آدرس:', 'text_en': 'Address:',
             'text_ar': 'العنوان:', 'text_ru': 'Adres:'},
            {'key': 'contact_phone_label', 'default_text': 'تلفن:', 'text_fa': 'تلفن:', 'text_en': 'Phone:',
             'text_ar': 'الهاتف:', 'text_ru': 'Telefon:'},
            {'key': 'contact_email_label', 'default_text': 'ایمیل:', 'text_fa': 'ایمیل:', 'text_en': 'Email:',
             'text_ar': 'البريد الإلكتروني:', 'text_ru': 'Email:'},

            # Misc
            {'key': 'contact_us', 'default_text': 'تماس با ما', 'text_fa': 'تماس با ما', 'text_en': 'Contact Us',
             'text_ar': 'اتصل بنا', 'text_ru': 'Svyazhites s nami'},
            {'key': 'whatsapp', 'default_text': 'واتس‌اپ', 'text_fa': 'واتس‌اپ', 'text_en': 'WhatsApp',
             'text_ar': 'واتساب', 'text_ru': 'WhatsApp'},
            {'key': 'form_submit', 'default_text': 'ارسال درخواست', 'text_fa': 'ارسال درخواست',
             'text_en': 'Submit Request', 'text_ar': 'إرسال الطلب', 'text_ru': 'Otpravit zapros'},
            {'key': 'not_in_stock', 'default_text': 'ناموجود', 'text_fa': 'ناموجود', 'text_en': 'Out of Stock',
             'text_ar': 'غير متوفر', 'text_ru': 'Net v nalichii'},
            {'key': 'details', 'default_text': 'جزئیات', 'text_fa': 'جزئیات', 'text_en': 'Details',
             'text_ar': 'التفاصيل', 'text_ru': 'Detali'},
            {'key': 'read_more', 'default_text': 'ادامه مطلب', 'text_fa': 'ادامه مطلب', 'text_en': 'Read More',
             'text_ar': 'اقرأ المزيد', 'text_ru': 'Chitat dalee'},
            {'key': 'view_products', 'default_text': 'مشاهده محصولات', 'text_fa': 'مشاهده محصولات',
             'text_en': 'View Products', 'text_ar': 'عرض المنتجات', 'text_ru': 'Posmotret produkty'},
            {'key': 'search_loading', 'default_text': 'در حال جستجو...', 'text_fa': 'در حال جستجو...',
             'text_en': 'Searching...', 'text_ar': 'جارٍ البحث...', 'text_ru': 'Poisk...'},
            {'key': 'toggle_theme', 'default_text': 'تغییر قالب', 'text_fa': 'تغییر قالب',
             'text_en': 'Toggle Theme', 'text_ar': 'تبديل السمة', 'text_ru': 'Pereklyuchit temu'},

            # Menu Items (تصحیح شده)
            {'key': 'menu_home', 'default_text': 'خانه', 'text_fa': 'خانه', 'text_en': 'Home', 'text_ar': 'الرئيسية',
             'text_ru': 'Glavnaya'},
            {'key': 'menu_categories', 'default_text': 'دسته‌بندی‌ها', 'text_fa': 'دسته‌بندی‌ها',
             'text_en': 'Categories', 'text_ar': 'الفئات', 'text_ru': 'Kategorii'},
            {'key': 'menu_products', 'default_text': 'محصولات', 'text_fa': 'محصولات', 'text_en': 'Products',
             'text_ar': 'المنتجات', 'text_ru': 'Produkty'},
            {'key': 'menu_articles', 'default_text': 'مقالات', 'text_fa': 'مقالات', 'text_en': 'Articles',
             'text_ar': 'المقالات', 'text_ru': 'Statyi'},
            {'key': 'menu_projects', 'default_text': 'پروژه‌ها', 'text_fa': 'پروژه‌ها', 'text_en': 'Projects',
             'text_ar': 'المشاريع', 'text_ru': 'Proekty'},
            {'key': 'menu_contact', 'default_text': 'تماس با ما', 'text_fa': 'تماس با ما', 'text_en': 'Contact',
             'text_ar': 'اتصل بنا', 'text_ru': 'Kontakt'},

            # Additional keys for article and project multilingual support
            {'key': 'all_categories', 'default_text': 'همه دسته‌بندی‌ها', 'text_fa': 'همه دسته‌بندی‌ها',
             'text_en': 'All Categories', 'text_ar': 'جميع الفئات', 'text_ru': 'Vse kategorii'},
            {'key': 'categories', 'default_text': 'دسته‌بندی‌ها', 'text_fa': 'دسته‌بندی‌ها', 'text_en': 'Categories',
             'text_ar': 'الفئات', 'text_ru': 'Kategorii'},
            {'key': 'no_results', 'default_text': 'هیچ نتیجه‌ای یافت نشد', 'text_fa': 'هیچ نتیجه‌ای یافت نشد',
             'text_en': 'No results found', 'text_ar': 'لم يتم العثور على نتائج', 'text_ru': 'Rezultatov ne naydeno'},
            {'key': 'details', 'default_text': 'جزئیات بیشتر', 'text_fa': 'جزئیات بیشتر', 'text_en': 'More Details',
             'text_ar': 'المزيد من التفاصيل', 'text_ru': 'Podrobneye'},
            # FAQ Section
            {'key': 'faq_title', 'default_text': 'سوالات متداول', 'text_fa': 'سوالات متداول',
             'text_en': 'Frequently Asked Questions', 'text_ar': 'الأسئلة الشائعة',
             'text_ru': 'Часто задаваемые вопросы'},
            {'key': 'faq_subtitle', 'default_text': 'پاسخ به پرسش‌های رایج درباره محصولات و خدمات ما',
             'text_fa': 'پاسخ به پرسش‌های رایج درباره محصولات و خدمات ما',
             'text_en': 'Answers to common questions about our products and services',
             'text_ar': 'إجابات على الأسئلة الشائعة حول منتجاتنا وخدماتنا',
             'text_ru': 'Ответы на частые вопросы о наших продуктах и услугах'},
            {'key': 'faq_empty', 'default_text': 'سوالی ثبت نشده است.', 'text_fa': 'سوالی ثبت نشده است.',
             'text_en': 'No FAQs recorded.', 'text_ar': 'لم يتم تسجيل أي أسئلة.',
             'text_ru': 'Вопросы не зарегистрированы.'},

            # Agents Section
            {'key': 'agents_title', 'default_text': 'نمایندگان فروش', 'text_fa': 'نمایندگان فروش',
             'text_en': 'Sales Representatives', 'text_ar': 'مندوبو المبيعات', 'text_ru': 'Торговые представители'},
            {'key': 'agents_subtitle', 'default_text': 'دسترسی سریع به نمایندگان ما در سراسر کشور',
             'text_fa': 'دسترسی سریع به نمایندگان ما در سراسر کشور',
             'text_en': 'Quick access to our representatives nationwide',
             'text_ar': 'وصول سريع إلى ممثلينا في جميع أنحاء البلاد',
             'text_ru': 'Быстрый доступ к нашим представителям по всей стране'},
            {'key': 'agents_map_link', 'default_text': 'مشاهده روی نقشه', 'text_fa': 'مشاهده روی نقشه',
             'text_en': 'View on map', 'text_ar': 'عرض على الخريطة', 'text_ru': 'Посмотреть на карте'},
            {'key': 'agents_empty', 'default_text': 'نماینده‌ای ثبت نشده است.', 'text_fa': 'نماینده‌ای ثبت نشده است.',
             'text_en': 'No agents recorded.', 'text_ar': 'لم يتم تسجيل أي ممثلين.',
             'text_ru': 'Представители не зарегистрированы.'},

            # Base / Mobile Menu
            {'key': 'mobile_menu_title', 'default_text': 'منوی دسترسی', 'text_fa': 'منوی دسترسی', 'text_en': 'Menu',
             'text_ar': 'قائمة الوصول', 'text_ru': 'Меню доступа'},
            # Footer
            {'key': 'footer_about', 'default_text': 'توضیحات درباره ما در فوتر', 'text_fa': 'متن درباره ما...',
             'text_en': 'About Us text...', 'text_ar': 'نص معلومات عنا...', 'text_ru': 'Текст о нас...'},
            {'key': 'footer_quick_links', 'default_text': 'لینک‌های سریع', 'text_fa': 'لینک‌های سریع',
             'text_en': 'Quick Links', 'text_ar': 'روابط سريعة', 'text_ru': 'Быстрые ссылки'},
            {'key': 'footer_contact_info', 'default_text': 'اطلاعات تماس', 'text_fa': 'اطلاعات تماس',
             'text_en': 'Contact Info', 'text_ar': 'معلومات الاتصال', 'text_ru': 'Контактная информация'},
            {'key': 'footer_location', 'default_text': 'موقعیت ما', 'text_fa': 'موقعیت ما', 'text_en': 'Our Location',
             'text_ar': 'موقعنا', 'text_ru': 'Наше местоположение'},
            {'key': 'google_map', 'default_text': 'نقشه گوگل', 'text_fa': 'نقشه گوگل', 'text_en': 'Google Map',
             'text_ar': 'خريطة جوجل', 'text_ru': 'Карта Google'},
            {'key': 'footer_copyright', 'default_text': 'تمامی حقوق محفوظ است.', 'text_fa': 'تمامی حقوق محفوظ است.',
             'text_en': 'All rights reserved.', 'text_ar': 'كل الحقوق محفوظة.', 'text_ru': 'Все права защищены.'},
            {'key': 'main_branch', 'default_text': 'شعبه مرکزی', 'text_fa': 'شعبه مرکزی', 'text_en': 'Main Branch',
             'text_ar': 'الفرع الرئيسي', 'text_ru': 'Главный филиал'},
        ]

        created_count = 0
        updated_count = 0
        for item in static_texts:
            obj, created = StaticText.objects.get_or_create(
                key=item['key'],
                defaults={
                    'default_text': item['default_text'],
                    'description': 'Static text for ' + item['key'],
                    'text_fa': item.get('text_fa', ''),
                    'text_en': item.get('text_en', ''),
                    'text_ar': item.get('text_ar', ''),
                    'text_ru': item.get('text_ru', ''),
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed {len(static_texts)} static texts. Created: {created_count}, Updated: {updated_count}')
        )