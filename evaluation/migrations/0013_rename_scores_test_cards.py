# Generated by Django 4.0.2 on 2022-03-31 02:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0012_alter_test_held_on'),
    ]

    operations = [
        migrations.RenameField(
            model_name='test',
            old_name='scores',
            new_name='cards',
        ),
    ]
