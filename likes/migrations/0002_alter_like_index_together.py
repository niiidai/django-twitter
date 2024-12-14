# Generated by Django 3.2.25 on 2024-11-14 04:49

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('likes', '0001_initial'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='like',
            index_together={('content_type', 'object_id', 'created_at'), ('user', 'content_type', 'created_at')},
        ),
    ]