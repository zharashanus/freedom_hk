from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('vacancy/<int:vacancy_id>/analyze/', views.analyze_candidates, name='analyze_candidates'),
    path('candidate/<int:candidate_id>/analysis/', views.candidate_analysis, name='candidate_analysis'),
] 