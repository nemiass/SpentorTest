# Generated by Django 4.0.2 on 2022-03-25 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0003_card_deck_cardtag_card_deck'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page'),
        ),
    ]
