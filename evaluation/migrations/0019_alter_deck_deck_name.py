# Generated by Django 4.0.2 on 2022-04-22 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0018_alter_deck_deck_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='deck_name',
            field=models.CharField(max_length=52, null=True),
        ),
    ]
