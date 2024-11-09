from django.db import models
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile

# Create your models here.

class CandidateAnalysis(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='candidate_analyses')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='vacancy_analyses')
    match_score = models.FloatField(default=0)  # Общий процент соответствия
    reputation_score = models.IntegerField(default=0)  # Общий репутационный скор
    
    # Детальные скоры по категориям
    specialization_score = models.IntegerField(default=0)
    hard_skills_score = models.IntegerField(default=0)
    experience_score = models.IntegerField(default=0)
    education_score = models.IntegerField(default=0)
    about_me_score = models.IntegerField(default=0)
    soft_skills_score = models.IntegerField(default=0)
    tech_stack_score = models.IntegerField(default=0)
    languages_score = models.IntegerField(default=0)
    level_score = models.IntegerField(default=0)
    
    feedback = models.TextField()  # Текстовый отзыв от GPT
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Анализ кандидата"
        verbose_name_plural = "Анализы кандидатов"
        ordering = ['-reputation_score', '-match_score']
