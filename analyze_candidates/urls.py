from django.urls import path
from . import views

app_name = 'analyze_candidates'

urlpatterns = [
    path('vacancy/<int:vacancy_id>/analyze/', views.analyze_candidates, name='analyze_candidates'),
] 