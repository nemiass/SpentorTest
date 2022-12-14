# Generated by Django 4.0.2 on 2022-04-02 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0015_remove_test_total_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='deck_name',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='sorted_by',
            field=models.TextField(choices=[('0', 'Randomly'), ('1', 'Ascending'), ('2', 'Descending')], default='0', max_length=1),
        ),
    ]
