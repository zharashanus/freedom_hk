from django.urls import path
from . import views

app_name = 'auth_freedom'

urlpatterns = [
    path('', views.redirect_to_login, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.recruiter_profile_view, name='profile'),
    path('candidate-profile/', views.candidate_profile_view, name='candidate_profile'),
    path('recruiter-profile/', views.recruiter_profile_view, name='recruiter_profile'),
    path('profile/edit/', views.edit_candidate_profile, name='edit_profile'),
    path('api/bulk-register/', views.bulk_register_candidates, name='bulk_register_candidates'),
    path('register/', views.RegistrationStep1View.as_view(), name='register'),
    path('register/step1/', views.RegistrationStep1View.as_view(), name='register_step1'),
    path('register/step2/', views.RegistrationStep2View.as_view(), name='register_step2'),
    path('register/step3/', views.RegistrationStep3View.as_view(), name='register_step3'),
]