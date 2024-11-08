from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import ExtendedUserRegistrationForm, UserLoginForm, CandidateProfileEditForm
from django.contrib import messages
from .models import RecruiterProfile, CandidateProfile
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import BulkCandidateRegistrationSerializer
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from auth_freedom.models import create_user_profile, save_user_profile
import json
import logging

logger = logging.getLogger(__name__)

def redirect_to_login(request):
    if request.user.is_authenticated:
        return redirect('recruiting_system:vacancy_list')
    return redirect('auth_freedom:login')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('recruiting_system:vacancy_list')
        
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('recruiting_system:vacancy_list')
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

@login_required
def edit_candidate_profile(request):
    try:
        profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('auth_freedom:profile')

    if request.method == 'POST':
        form = CandidateProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            try:
                profile = form.save(commit=False)
                
                # Работа с опытом работы
                work_experience_data = request.POST.get('work_experience', '[]')
                try:
                    if isinstance(work_experience_data, str):
                        work_experience = json.loads(work_experience_data)
                        if isinstance(work_experience, list):
                            profile.work_experience = work_experience
                except json.JSONDecodeError:
                    profile.work_experience = []
                
                profile.save()
                messages.success(request, 'Профиль успешно обновлен')
                return redirect('auth_freedom:profile')
            except Exception as e:
                logger.error(f"Error saving profile: {str(e)}")
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
    else:
        form = CandidateProfileEditForm(instance=profile)
    
    return render(request, 'auth_freedom/edit_candidate_profile.html', {
        'form': form,
        'profile': profile
    })

def edit_profile(request):
    if request.method == 'POST':
        form = CandidateProfileEditForm(request.POST, instance=request.user.candidate_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            
            # Обработка опыта работы
            work_experience = []
            work_exp_data = request.POST.getlist('work_experience[]', [])
            
            for exp_data in work_exp_data:
                if isinstance(exp_data, dict) and all(key in exp_data for key in ['company', 'position', 'start_date']):
                    work_experience.append({
                        'company': exp_data['company'],
                        'position': exp_data['position'],
                        'start_date': exp_data['start_date'],
                        'end_date': exp_data.get('end_date', ''),
                        'description': exp_data.get('description', '')
                    })
            
            profile.work_experience = work_experience
            profile.save()
            messages.success(request, 'Профиль успешно обновлен')
            return redirect('auth_freedom:profile')
    else:
        form = CandidateProfileEditForm(instance=request.user.candidate_profile)
    
    return render(request, 'auth_freedom/edit_candidate_profile.html', {'form': form})

@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_register_candidates(request):
    # Disconnect signals temporarily
    post_save.disconnect(create_user_profile, sender=get_user_model())
    post_save.disconnect(save_user_profile, sender=get_user_model())

    try:
        if not isinstance(request.data, list):
            return Response({'error': 'Expected a list of candidates'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        results = []
        for candidate_data in request.data:
            serializer = BulkCandidateRegistrationSerializer(data=candidate_data)
            if serializer.is_valid():
                try:
                    # Create User
                    user = get_user_model().objects.create_user(
                        username=serializer.validated_data['username'],
                        password=serializer.validated_data['password'],
                        user_type='candidate'
                    )

                    # Create education data
                    education_data = {
                        'institution': serializer.validated_data['education_institution'],
                        'faculty': serializer.validated_data['education_faculty'],
                        'degree': serializer.validated_data['education_degree'],
                        'graduation_year': serializer.validated_data['graduation_year']
                    }

                    # Create CandidateProfile
                    profile = CandidateProfile.objects.create(
                        user=user,
                        first_name=serializer.validated_data['first_name'],
                        last_name=serializer.validated_data['last_name'],
                        email=serializer.validated_data['email'],
                        phone=serializer.validated_data['phone'],
                        birth_date=serializer.validated_data['birth_date'],
                        gender=serializer.validated_data['gender'],
                        about_me=serializer.validated_data['about_me'],
                        specialization=serializer.validated_data['specialization'],
                        experience=serializer.validated_data['experience'],
                        country=serializer.validated_data['country'],
                        region=serializer.validated_data['region'],
                        languages=serializer.validated_data['languages'],
                        desired_salary=serializer.validated_data['desired_salary'],
                        search_status=serializer.validated_data['search_status'],
                        relocation_status=serializer.validated_data['relocation_status'],
                        level=serializer.validated_data['level'],
                        hard_skills=serializer.validated_data['hard_skills'],
                        soft_skills=serializer.validated_data['soft_skills'],
                        education=education_data
                    )
                    
                    results.append({
                        'username': user.username,
                        'status': 'success',
                        'message': 'Successfully registered'
                    })
                except Exception as e:
                    results.append({
                        'username': serializer.validated_data['username'],
                        'status': 'error',
                        'message': str(e)
                    })
            else:
                results.append({
                    'username': candidate_data.get('username', 'Unknown'),
                    'status': 'error',
                    'message': serializer.errors
                })

        return Response(results, status=status.HTTP_200_OK)
    finally:
        # Reconnect signals
        post_save.connect(create_user_profile, sender=get_user_model())
        post_save.connect(save_user_profile, sender=get_user_model())