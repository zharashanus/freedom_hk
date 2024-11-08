from django.db import models
from recruiting_system.models import Vacancy, Application
from auth_freedom.models import CandidateProfile

# Create your models here.

class AIAnalysis(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='ai_analyses')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='ai_analyses')
    match_score = models.FloatField(default=0)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "AI Анализ"
        verbose_name_plural = "AI Анализы"
        ordering = ['-match_score']
