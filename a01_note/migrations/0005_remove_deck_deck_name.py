# Generated by Django 4.0.2 on 2022-03-28 01:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0004_alter_deck_page'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deck',
            name='deck_name',
        ),
    ]