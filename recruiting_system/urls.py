from django.urls import path
from . import views

app_name = 'recruiting_system'

urlpatterns = [
    path('vacancy/create/', views.vacancy_create, name='vacancy_create'),
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancy/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/<int:pk>/edit/', views.vacancy_edit, name='vacancy_edit'),
    path('applications/', views.application_list, name='application_list'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('vacancy/<int:pk>/apply/', views.apply_vacancy, name='apply_vacancy'),
    path('application/<int:pk>/update-status/', views.update_application_status, name='update_application_status'),
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
] 