# Generated by Django 5.1.3 on 2024-11-09 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convertor_to_json', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkupload',
            name='batch_size',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='bulkupload',
            name='processing_progress',
            field=models.FloatField(default=0),
        ),
    ]