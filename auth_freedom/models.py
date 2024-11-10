from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('recruiter', 'Рекрутер'),
        ('candidate', 'Кандидат'),
        ('admin', 'Администратор'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, verbose_name="Тип пользователя")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    is_verified = models.BooleanField(default=False, verbose_name="Подтвержден")
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class RecruiterProfile(models.Model):
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другой'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='recruiterprofile'
    )
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, default='')
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, default='')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол", default='other')
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    department = models.CharField(max_length=100, verbose_name="Департамент", blank=True, default='')
    phone = models.CharField(max_length=20, verbose_name="Номер телефона", blank=True, default='')
    email = models.EmailField(verbose_name="Электронная почта", blank=True, default='')
    country = models.CharField(max_length=100, verbose_name="Страна", blank=True, default='')
    region = models.CharField(max_length=100, verbose_name="Регион", blank=True, default='')
    processed_applications = models.IntegerField(default=0, verbose_name="Обработано заявок")
    successful_applications = models.IntegerField(default=0, verbose_name="Успешно обработанные заявки")
    social_networks = models.JSONField(verbose_name="Социальные сети", default=dict, blank=True)

    class Meta:
        verbose_name = "Профиль рекрутера"
        verbose_name_plural = "Профили рекрутеров"

class CandidateProfile(models.Model):
    LEVEL_CHOICES = [
        ('no_experience', 'Без опыта'),
        ('intern', 'Intern'),
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
    ]

    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другой'),
    ]

    SEARCH_STATUS_CHOICES = [
        ('active', 'В активном поиске'),
        ('passive', 'Рассматриваю предложения'),
        ('employed', 'Не ищу работу'),
    ]

    RELOCATION_CHOICES = [
        ('ready', 'Готов к переезду'),
        ('not_ready', 'Не готов к переезду'),
        ('remote_only', 'Только удаленная работа'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidateprofile')
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, default='')
    last_name = models.CharField(max_length=100, verbose_name="Фамилия", blank=True, default='')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Пол", default='other')
    birth_date = models.DateField(verbose_name="Дата рождения", null=True, blank=True)
    about_me = models.TextField(verbose_name="О себе", blank=True, default='')
    search_status = models.CharField(max_length=20, choices=SEARCH_STATUS_CHOICES, verbose_name="Статус поиска", default='active')
    is_employed = models.BooleanField(default=False, verbose_name="Работает в настоящее время")
    experience = models.IntegerField(verbose_name="Опыт работы (лет)", default=0)
    specialization = models.CharField(max_length=100, verbose_name="Специализация", blank=True, default='')
    phone = models.CharField(max_length=20, verbose_name="Номер телефона", blank=True, default='')
    email = models.EmailField(verbose_name="Электронная почта", blank=True, default='')
    country = models.CharField(max_length=100, verbose_name="Страна", blank=True, default='')
    region = models.CharField(max_length=100, verbose_name="Регион", blank=True, default='')
    languages = ArrayField(models.CharField(max_length=50), verbose_name="Языки", default=list, blank=True)
    applications_count = models.IntegerField(default=0, verbose_name="Количество откликов")
    desired_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Желаемая зарплата", default=0)
    certifications = ArrayField(models.CharField(max_length=100), verbose_name="Сертификаты", default=list, blank=True)
    hard_skills = ArrayField(models.CharField(max_length=100), verbose_name="Технические навыки", default=list, blank=True)
    soft_skills = ArrayField(models.CharField(max_length=100), verbose_name="Софт-скиллы", default=list, blank=True)
    education = models.JSONField(verbose_name="Образование", default=dict)
    work_experience = models.JSONField(verbose_name="Прошлые места работы", default=list, blank=True)
    projects = models.JSONField(verbose_name="Проекты", default=dict, blank=True)
    social_networks = models.JSONField(verbose_name="Социальные сети", default=dict, blank=True)
    video_presentation = models.URLField(verbose_name="Видео-презентация", blank=True, null=True)
    relocation_status = models.CharField(max_length=20, choices=RELOCATION_CHOICES, verbose_name="Готовность к переезду", default='not_ready')
    tech_stack = ArrayField(models.CharField(max_length=50), verbose_name="Технический стек", default=list, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="Уровень", default='no_experience')
    resume_text = models.TextField(verbose_name="Текст резюме", blank=True, default='')
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Профиль кандидата"
        verbose_name_plural = "Профили кандидатов"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not CandidateProfile.objects.filter(user=instance).exists():
        if instance.user_type == 'candidate':
            CandidateProfile.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email
            )
        elif instance.user_type in ['recruiter', 'admin'] or instance.is_superuser:
            RecruiterProfile.objects.create(
                user=instance,
                first_name=instance.first_name,
                last_name=instance.last_name,
                email=instance.email,
                department='HR' if instance.user_type == 'admin' or instance.is_superuser else '',
                country='Казахстан' if instance.user_type == 'admin' or instance.is_superuser else '',
                region='Все регионы' if instance.user_type == 'admin' or instance.is_superuser else '',
                processed_applications=0,
                successful_applications=0,
                social_networks={}
            )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 'candidate' and hasattr(instance, 'candidateprofile'):
        instance.candidateprofile.save()

