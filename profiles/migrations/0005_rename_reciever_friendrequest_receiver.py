# Generated by Django 4.1 on 2023-02-01 02:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_alter_profile_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendrequest',
            old_name='reciever',
            new_name='receiver',
        ),
    ]
