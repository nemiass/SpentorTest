# Generated by Django 4.0.2 on 2022-04-13 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0013_page_is_shared'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='sharing_code',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='sharing_permission',
            field=models.CharField(blank=True, choices=[('0', 'viewer'), ('1', 'commenter'), ('2', 'editor')], max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='page_role',
            field=models.CharField(choices=[('0', 'Folder'), ('1', 'Note'), ('2', 'Both')], default='0', max_length=1),
        ),
    ]
