# Generated by Django 5.1.3 on 2024-11-08 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_freedom', '0004_remove_recruiterprofile_active_vacancies_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='work_experience',
            field=models.JSONField(blank=True, default=list, verbose_name='Прошлые места работы'),
        ),
    ]