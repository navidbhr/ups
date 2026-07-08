# Generated manually on 2026-05-16

import django.db.models.deletion
from django.db import migrations, models


def copy_legacy_product_prices(apps, schema_editor):
    Product = apps.get_model('main', 'Product')
    ProductPrice = apps.get_model('main', 'ProductPrice')

    for product in Product.objects.filter(base_price__gt=0):
        ProductPrice.objects.create(
            product_id=product.id,
            amount=product.base_price,
            currency_id=product.currency_id,
            order=0,
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_contactmessage_remove_article_content_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='مبلغ')),
                ('label', models.CharField(blank=True, max_length=100, verbose_name='عنوان قیمت')),
                ('is_active', models.BooleanField(default=True, verbose_name='فعال؟')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='main.currency', verbose_name='واحد پولی')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='main.product', verbose_name='محصول')),
            ],
            options={
                'verbose_name': 'قیمت محصول',
                'verbose_name_plural': 'قیمت‌های محصول',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.RunPython(copy_legacy_product_prices, migrations.RunPython.noop),
    ]
