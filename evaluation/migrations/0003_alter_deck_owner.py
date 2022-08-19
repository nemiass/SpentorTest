# Generated by Django 4.0.2 on 2022-03-30 15:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('evaluation', '0002_deck_owner_deck_type_alter_card_status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deck',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
