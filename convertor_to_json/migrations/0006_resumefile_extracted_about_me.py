# Generated by Django 5.1.3 on 2024-11-09 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convertor_to_json', '0005_remove_bulkupload_batch_size_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumefile',
            name='extracted_about_me',
            field=models.TextField(blank=True, verbose_name='О себе'),
        ),
    ]
