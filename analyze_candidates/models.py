from django.db import models
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile

# Create your models here.

class CandidateAnalysis(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='candidate_analyses')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='vacancy_analyses')
    match_score = models.FloatField(default=0)  # Общий процент соответствия
    reputation_score = models.IntegerField(default=0)  # Общий репутационный скор (максимум 1000)
    
    # Детальные скоры по категориям
    specialization_score = models.IntegerField(default=0)  # макс. 150
    hard_skills_score = models.IntegerField(default=0)    # макс. 200
    experience_score = models.IntegerField(default=0)     # макс. 150
    education_score = models.IntegerField(default=0)      # макс. 100
    about_me_score = models.IntegerField(default=0)       # макс. 50
    soft_skills_score = models.IntegerField(default=0)    # макс. 100
    tech_stack_score = models.IntegerField(default=0)     # макс. 150
    languages_score = models.IntegerField(default=0)      # макс. 50
    level_score = models.IntegerField(default=0)          # макс. 50
    
    # Топ-3 сильнейших качества кандидата
    top_strength_1 = models.CharField(max_length=50, blank=True)
    top_strength_2 = models.CharField(max_length=50, blank=True)
    top_strength_3 = models.CharField(max_length=50, blank=True)
    
    feedback = models.TextField(blank=True, null=True)  # Текстовый отзыв от GPT
    created_at = models.DateTimeField(auto_now_add=True)
    candidate_data_hash = models.CharField(max_length=64, blank=True)  # Хеш данных кандидата
    
    class Meta:
        verbose_name = "Анализ кандидата"
        verbose_name_plural = "Анализы кандидатов"
        ordering = ['-reputation_score', '-match_score']

    def __str__(self):
        return f"Analysis for {self.candidate} - Feedback: {self.feedback[:50]}..."
