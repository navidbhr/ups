from django.core.management.base import BaseCommand
from main.models import StaticText

class Command(BaseCommand):
    help = 'ایجاد کلیدهای متون استاتیک برای صفحه اصلی'

    def handle(self, *args, **kwargs):
        static_texts = [
            {'key': 'hero_stats_experience', 'default_text': 'سال تجربه', 'text_fa': 'سال تجربه', 'text_en': 'Years of Experience', 'text_ar': 'سنوات الخبرة', 'text_ru': 'Let opyta'},
            {'key': 'hero_stats_projects', 'default_text': 'پروژه موفق', 'text_fa': 'پروژه موفق', 'text_en': 'Successful Projects', 'text_ar': 'مشاريع ناجحة', 'text_ru': 'Uspeshnye proekty'},
            {'key': 'view_products', 'default_text': 'مشاهده محصولات', 'text_fa': 'مشاهده محصولات', 'text_en': 'View Products', 'text_ar': 'عرض المنتجات', 'text_ru': 'Posmotret produkty'},
            {'key': 'not_in_stock', 'default_text': 'ناموجود', 'text_fa': 'ناموجود', 'text_en': 'Out of Stock', 'text_ar': 'غير متوفر', 'text_ru': 'Net v nalichii'},
            {'key': 'details', 'default_text': 'جزئیات', 'text_fa': 'جزئیات', 'text_en': 'Details', 'text_ar': 'التفاصيل', 'text_ru': 'Detali'},
            {'key': 'read_more', 'default_text': 'ادامه مطلب', 'text_fa': 'ادامه مطلب', 'text_en': 'Read More', 'text_ar': 'اقرأ المزيد', 'text_ru': 'Chitat dalee'},
            {'key': 'whatsapp', 'default_text': 'واتس‌اپ', 'text_fa': 'واتس‌اپ', 'text_en': 'WhatsApp', 'text_ar': 'واتساب', 'text_ru': 'WhatsApp'},
            {'key': 'form_submit', 'default_text': 'ارسال درخواست', 'text_fa': 'ارسال درخواست', 'text_en': 'Submit Request', 'text_ar': 'إرسال الطلب', 'text_ru': 'Otpravit zapros'},
        ]
        
        created_count = 0
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
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created %d static texts.' % created_count)
        )
