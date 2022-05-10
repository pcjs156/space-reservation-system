# Generated by Django 4.0.4 on 2022-05-10 13:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_block_member_info_block_group_block_member_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissiontag',
            name='members',
            field=models.ManyToManyField(related_name='given_permission_tags', to=settings.AUTH_USER_MODEL, verbose_name='대상 멤버'),
        ),
    ]