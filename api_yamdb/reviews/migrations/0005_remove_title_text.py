# Generated by Django 3.2 on 2023-04-30 12:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20230430_1526'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='text',
        ),
    ]