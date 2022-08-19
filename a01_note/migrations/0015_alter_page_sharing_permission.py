# Generated by Django 4.0.2 on 2022-04-13 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0014_page_sharing_code_page_sharing_permission_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='sharing_permission',
            field=models.CharField(blank=True, choices=[('VI', 'viewer'), ('CO', 'commenter'), ('ED', 'editor')], max_length=2, null=True),
        ),
    ]
