# Generated by Django 2.2 on 2019-05-01 06:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_user_transactions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='receiver',
            new_name='receiver_account',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='sender',
            new_name='sender_account',
        ),
    ]
