# Generated by Django 4.0.2 on 2022-03-30 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0003_alter_deck_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='deck_parts',
            field=models.ManyToManyField(blank=True, null=True, to='evaluation.Deck'),
        ),
    ]
