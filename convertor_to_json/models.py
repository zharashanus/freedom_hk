from django.db import models
from auth_freedom.models import RecruiterProfile
from django.contrib.postgres.fields import ArrayField
from auth_freedom.models import CandidateProfile
# Create your models here.

class BulkUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В очереди'),
        ('processing', 'Обработка'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
    ]

    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_files = models.IntegerField(default=0)
    processed_files = models.IntegerField(default=0)
    failed_files = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Массовая загрузка"
        verbose_name_plural = "Массовые загрузки"

class ResumeFile(models.Model):
    FILE_TYPES = [
        ('pdf', 'PDF'),
        ('doc', 'DOC'),
        ('docx', 'DOCX'),
        ('pptx', 'PPTX'),
        ('txt', 'TXT'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'В очереди'),
        ('processing', 'Обработка'),
        ('converted', 'Конвертировано'),
        ('failed', 'Ошибка'),
    ]

    bulk_upload = models.ForeignKey(BulkUpload, on_delete=models.CASCADE, related_name='resume_files')
    file = models.FileField(upload_to='resumes/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    original_filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    extracted_text = models.TextField(blank=True)
    parsed_data = models.JSONField(default=dict)
    
    # Поля, соответствующие CandidateProfile и Application
    extracted_name = models.CharField(max_length=200, blank=True)
    extracted_email = models.EmailField(blank=True)
    extracted_phone = models.CharField(max_length=20, blank=True)
    extracted_experience_years = models.IntegerField(null=True, blank=True)
    extracted_specialization = models.CharField(max_length=100, blank=True)
    extracted_level = models.CharField(
        max_length=20,
        choices=CandidateProfile.LEVEL_CHOICES,
        blank=True
    )
    extracted_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    extracted_location = models.JSONField(default=dict, blank=True)
    extracted_tech_stack = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    extracted_hard_skills = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    extracted_soft_skills = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    extracted_education = models.JSONField(default=dict, blank=True)
    extracted_work_experience = models.JSONField(default=list, blank=True)
    extracted_languages = ArrayField(
        models.CharField(max_length=50),
        default=list,
        blank=True
    )
    
    created_candidate = models.ForeignKey(
        CandidateProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_resume'
    )
    
    class Meta:
        verbose_name = "Файл резюме"
        verbose_name_plural = "Файлы резюме"
        indexes = [
            models.Index(fields=['status', 'upload_date']),
            models.Index(fields=['extracted_email']),
            models.Index(fields=['extracted_specialization']),
        ]
