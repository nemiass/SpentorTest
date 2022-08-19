# Generated by Django 4.0.2 on 2022-04-13 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0015_alter_page_sharing_permission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='sharing_permission',
            field=models.CharField(blank=True, choices=[('0', 'viewer'), ('1', 'commenter'), ('2', 'editor')], max_length=1, null=True),
        ),
    ]