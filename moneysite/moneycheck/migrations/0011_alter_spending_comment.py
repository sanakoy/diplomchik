# Generated by Django 5.0.2 on 2024-03-12 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moneycheck', '0010_alter_spending_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spending',
            name='comment',
            field=models.CharField(blank=True, default='', max_length=100, null=True),
        ),
    ]