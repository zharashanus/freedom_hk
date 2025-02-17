# Generated by Django 5.1.3 on 2024-11-08 13:25

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_freedom', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidateprofile',
            name='location',
        ),
        migrations.RemoveField(
            model_name='candidateprofile',
            name='skills',
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='about_me',
            field=models.TextField(blank=True, default='', verbose_name='О себе'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='applications_count',
            field=models.IntegerField(default=0, verbose_name='Количество откликов'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='country',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Страна'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Электронная почта'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='gender',
            field=models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский'), ('other', 'Другой')], default='other', max_length=10, verbose_name='Пол'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='hard_skills',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None, verbose_name='Технические навыки'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='is_employed',
            field=models.BooleanField(default=False, verbose_name='Работает в настоящее время'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Фамилия'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='projects',
            field=models.JSONField(blank=True, default=dict, verbose_name='Проекты'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='region',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Регион'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='relocation_status',
            field=models.CharField(choices=[('ready', 'Готов к переезду'), ('not_ready', 'Не готов к переезду'), ('remote_only', 'Только удаленная работа')], default='not_ready', max_length=20, verbose_name='Готовность к переезду'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='search_status',
            field=models.CharField(choices=[('active', 'В активном поиске'), ('passive', 'Рассматриваю предложения'), ('employed', 'Не ищу работу')], default='active', max_length=20, verbose_name='Статус поиска'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='social_networks',
            field=models.JSONField(blank=True, default=dict, verbose_name='Социальные сети'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='soft_skills',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None, verbose_name='Софт-скиллы'),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='video_presentation',
            field=models.URLField(blank=True, null=True, verbose_name='Видео-презентация'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='certifications',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, default=list, size=None, verbose_name='Сертификаты'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='desired_salary',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Желаемая зарплата'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='education',
            field=models.JSONField(default=dict, verbose_name='Образование'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='experience',
            field=models.IntegerField(default=0, verbose_name='Опыт работы (лет)'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='languages',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, default=list, size=None, verbose_name='Языки'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='level',
            field=models.CharField(choices=[('junior', 'Junior'), ('middle', 'Middle'), ('senior', 'Senior'), ('lead', 'Lead')], default='junior', max_length=20, verbose_name='Уровень'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='resume_text',
            field=models.TextField(blank=True, default='', verbose_name='Текст резюме'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='specialization',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Специализация'),
        ),
        migrations.AlterField(
            model_name='candidateprofile',
            name='tech_stack',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, default=list, size=None, verbose_name='Технический стек'),
        ),
    ]
