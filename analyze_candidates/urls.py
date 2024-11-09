from django.urls import path
from . import views

app_name = 'analyze_candidates'

urlpatterns = [
    path('vacancy/<int:vacancy_id>/analyze/', views.analyze_candidates, name='analyze_candidates'),
    path('<int:vacancy_id>/', views.analyze_candidates, name='analysis_results'),
    path('<int:vacancy_id>/reanalyze/<int:candidate_id>/', views.reanalyze_candidate, name='reanalyze_candidate'),
] 