# Generated by Django 4.0.4 on 2022-05-17 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_permissiontag_unique permission tag in group'),
        ('reservations', '0007_reservation_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='space',
            name='required_permission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requiring_spaces', to='users.permissiontag', verbose_name='요구 권한'),
        ),
        migrations.AlterField(
            model_name='space',
            name='term',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='using_spaces', to='reservations.term', verbose_name='등록 약관'),
        ),
    ]