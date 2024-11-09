from django.urls import path
from . import views

app_name = 'convertor_to_json'

urlpatterns = [
    path('upload/', views.upload_resumes, name='upload_resumes'),
    path('status/<int:upload_id>/', views.upload_status, name='upload_status'),
] 