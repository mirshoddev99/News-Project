# Generated by Django 4.2.1 on 2023-06-02 13:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news_app', '0003_news_view_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='view_count',
        ),
    ]
