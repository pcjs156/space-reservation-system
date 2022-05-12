# Generated by Django 4.0.4 on 2022-05-12 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_permissiontag_members'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='permissiontag',
            constraint=models.UniqueConstraint(fields=('group', 'body'), name='unique permission tag in group'),
        ),
    ]