# Generated by Django 4.0.4 on 2022-05-12 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0003_remove_reservation_required_permissions_space_name_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='space',
            old_name='required_permissions',
            new_name='required_permission',
        ),
    ]