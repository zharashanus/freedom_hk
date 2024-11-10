from django.db import models
from auth_freedom.models import User, RecruiterProfile, CandidateProfile
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('closed', 'Закрыта'),
        ('draft', 'Черновик'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Полная занятость'),
        ('part_time', 'Частичная занятость'),
        ('contract', 'Контракт'),
        ('temporary', 'Временная'),
        ('remote', 'Удаленная работа'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='vacancies')
    department = models.CharField(max_length=100, verbose_name="Департамент", default='')
    country = models.CharField(max_length=100, verbose_name="Страна", default='Казахстан')
    region = models.CharField(max_length=100, verbose_name="Регион", default='')
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        verbose_name="Тип занятости"
    )
    description = models.TextField(verbose_name="Описание вакансии")
    requirements = models.TextField(verbose_name="Требования")
    responsibilities = models.TextField(verbose_name="Обязанности", default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField(verbose_name="Дата закрытия", null=True, blank=True)
    desired_experience = models.IntegerField(verbose_name="Требуемый опыт работы (лет)", default=0)
    desired_specialization = models.CharField(max_length=100, verbose_name="Требуемая специализация", default='')
    desired_level = models.CharField(
        max_length=20,
        choices=CandidateProfile.LEVEL_CHOICES,
        verbose_name="Требуемый уровень",
        default='junior'
    )
    salary_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Минимальная зарплата",
        default=0
    )
    salary_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Максимальная зарплата",
        default=0
    )
    tech_stack = ArrayField(
        models.CharField(max_length=50),
        verbose_name="Технический стек",
        default=list,
        blank=True
    )
    hard_skills = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Требуемые технические навыки",
        default=list,
        blank=True
    )
    soft_skills = ArrayField(
        models.CharField(max_length=100),
        verbose_name="Требуемые софт-скиллы",
        default=list,
        blank=True
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('interview', 'Назначено собеседование'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Сайт компании'),
        ('recommendation', 'Рекомендация'),
        ('search', 'Поиск в базе'),
        ('other', 'Другое'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey('auth_freedom.CandidateProfile', on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Оценка соответствия",
        default=0
    )
    notes = models.TextField(verbose_name="Заметки рекрутера", blank=True)
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='website',
        verbose_name="Источник отклика"
    )
    desired_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Желаемая зарплата",
        null=True,
        blank=True
    )
    current_location = models.JSONField(
        verbose_name="Текущее местоположение",
        default=dict,
        blank=True
    )
    relocation_status = models.CharField(
        max_length=20,
        choices=CandidateProfile.RELOCATION_CHOICES,
        verbose_name="Готовность к переезду",
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        if not self.pk:  # Если это новый объект
            # Копируем данные из профиля кандидата
            self.desired_salary = self.candidate.desired_salary
            self.current_location = {
                'country': self.candidate.country,
                'region': self.candidate.region
            }
            self.relocation_status = self.candidate.relocation_status
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        unique_together = ['vacancy', 'candidate']
        ordering = ['-created_at']
