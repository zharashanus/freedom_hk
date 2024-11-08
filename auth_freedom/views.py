from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import ExtendedUserRegistrationForm, UserLoginForm
from django.contrib import messages
from .models import RecruiterProfile, CandidateProfile

def redirect_to_login(request):
    return redirect('auth_freedom:login')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('auth_freedom:profile')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'auth_freedom/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = ExtendedUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('auth_freedom:profile')
    else:
        form = ExtendedUserRegistrationForm()
    return render(request, 'auth_freedom/register.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('auth_freedom:login')

@login_required
def profile_view(request):
    user = request.user
    try:
        if user.is_superuser or user.user_type in ['recruiter', 'admin']:
            profile, created = RecruiterProfile.objects.get_or_create(
                user=user,
                defaults={
                    'experience': 0,
                    'specialization': 'Администратор' if user.is_superuser or user.user_type == 'admin' else 'Рекрутер',
                    'company': 'Freedom HK',
                    'region': 'Все регионы',
                    'languages': ['Русский', 'Английский'],
                    'active_vacancies': 0
                }
            )
            template = 'auth_freedom/recruiter_profile.html'
        elif user.user_type == 'candidate':
            profile = user.candidate_profile
            template = 'auth_freedom/candidate_profile.html'
        else:
            messages.error(request, 'Неверный тип пользователя')
            return redirect('auth_freedom:login')
            
        return render(request, template, {'profile': profile})
    except (RecruiterProfile.DoesNotExist, CandidateProfile.DoesNotExist):
        messages.error(request, 'Профиль не найден')
        return redirect('auth_freedom:login')