# Generated by Django 4.0.2 on 2022-03-25 20:45

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('a01_note', '0002_page_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('front', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('back', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('extra_info', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('order_number', models.PositiveSmallIntegerField(default=1)),
                ('times_reviewed', models.PositiveIntegerField(default=0)),
                ('times_forgotten', models.PositiveIntegerField(default=0)),
                ('status', models.TextField(choices=[('0', 'New'), ('1', 'Learning'), ('2', 'To review')], default=('0', 'New'), max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deck_name', models.CharField(blank=True, max_length=45, null=True)),
                ('description', models.CharField(blank=True, max_length=150, null=True)),
                ('is_shared', models.BooleanField(default=True)),
                ('new_card', models.PositiveSmallIntegerField(default=0)),
                ('learning_card', models.PositiveSmallIntegerField(default=0)),
                ('review_card', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.page')),
            ],
        ),
        migrations.CreateModel(
            name='CardTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag_name', models.CharField(blank=True, max_length=45, null=True)),
                ('cards', models.ManyToManyField(to='a01_note.Card')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='deck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a01_note.deck'),
        ),
    ]
