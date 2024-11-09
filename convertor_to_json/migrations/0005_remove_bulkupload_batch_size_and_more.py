# Generated by Django 5.1.3 on 2024-11-09 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convertor_to_json', '0004_bulkupload_current_task_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bulkupload',
            name='batch_size',
        ),
        migrations.RemoveField(
            model_name='bulkupload',
            name='current_task_id',
        ),
        migrations.RemoveField(
            model_name='bulkupload',
            name='processing_progress',
        ),
        migrations.AlterField(
            model_name='bulkupload',
            name='status',
            field=models.CharField(choices=[('pending', 'В очереди'), ('processing', 'Обработка'), ('completed', 'Завершено'), ('failed', 'Ошибка')], default='pending', max_length=20),
        ),
    ]