# Generated by Django 4.0.2 on 2022-03-23 15:02

import a01_note.models
import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.PositiveSmallIntegerField(default=0)),
                ('column', models.PositiveSmallIntegerField(default=0)),
                ('column_length', models.PositiveSmallIntegerField(default=12)),
            ],
        ),
        migrations.CreateModel(
            name='BlockType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=45)),
                ('referenced_to', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_name', models.CharField(max_length=45)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('page_status', models.CharField(choices=[('0', 'Active'), ('1', 'Deleted')], default='0', max_length=1)),
                ('level', models.IntegerField(default=0)),
                ('page_role', models.CharField(choices=[('0', 'Folder'), ('1', 'Note'), ('2', 'Folder and Note')], default='0', max_length=1)),
                ('emoji', models.CharField(blank=True, max_length=4, null=True)),
                ('cover', models.ImageField(blank=True, null=True, upload_to=a01_note.models.Page.user_directory_path)),
                ('hex_color', models.CharField(default='#0dcaf0', max_length=7)),
                ('is_favourite', models.BooleanField(default=False)),
                ('in_trash', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('moved_trash_at', models.DateTimeField(blank=True, null=True)),
                ('page_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_page', to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='PageProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_name', models.CharField(max_length=45)),
                ('order_number', models.SmallIntegerField(default=0)),
                ('page_parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=45)),
                ('referenced_to', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='WebmarkProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('webmark_name', models.CharField(blank=True, max_length=100, null=True)),
                ('webmark_url', models.URLField(blank=True, null=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
                ('page_property', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.pageproperty')),
            ],
        ),
        migrations.CreateModel(
            name='WebmarkContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_content', models.URLField(blank=True, null=True)),
                ('blockindex', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.blockindex')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='TextContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_text', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('blockindex', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.blockindex')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(max_length=45)),
                ('page_property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.pageproperty')),
                ('pages', models.ManyToManyField(to='a01_note.Page')),
            ],
        ),
        migrations.AddField(
            model_name='pageproperty',
            name='property_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='a01_note.propertytype'),
        ),
        migrations.CreateModel(
            name='ImageContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_content', models.ImageField(blank=True, null=True, upload_to=a01_note.models.ImageContent.user_directory_path)),
                ('blockindex', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.blockindex')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='FileContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_content', models.FileField(blank=True, null=True, upload_to=a01_note.models.FileContent.user_directory_path)),
                ('blockindex', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='a01_note.blockindex')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.AddField(
            model_name='blockindex',
            name='blocktype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='a01_note.blocktype'),
        ),
        migrations.AddField(
            model_name='blockindex',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page'),
        ),
    ]
