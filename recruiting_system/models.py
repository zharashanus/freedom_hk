from django.db import models
from auth_freedom.models import User, RecruiterProfile, CandidateProfile

# Create your models here.

class Vacancy(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('closed', 'Закрыта'),
        ('draft', 'Черновик'),
    ]

    title = models.CharField(max_length=200, verbose_name="Название вакансии")
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='vacancies')
    description = models.TextField(verbose_name="Описание вакансии")
    requirements = models.TextField(verbose_name="Требования")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

class Application(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('reviewing', 'На рассмотрении'),
        ('interview', 'Назначено интервью'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    cover_letter = models.TextField(verbose_name="Сопроводительное письмо", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
