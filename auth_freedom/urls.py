from django.urls import path
from . import views

app_name = 'auth_freedom'

urlpatterns = [
    path('', views.redirect_to_login, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_candidate_profile, name='edit_profile'),
    path('api/bulk-register/', views.bulk_register_candidates, name='bulk_register_candidates'),
]