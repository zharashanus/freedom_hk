from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import (
    UserLoginForm, 
    CandidateProfileEditForm,
    RegistrationStep1Form,
    RegistrationStep2Form,
    RegistrationStep3Form
)
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
from django.views import View
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

logger = logging.getLogger(__name__)

def redirect_to_login(request):
    if request.user.is_authenticated:
        return redirect('recruiting_system:vacancy_list')
    return redirect('auth_freedom:login')

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Добавляем логирование
            logger.debug(f"Attempting login for username: {username}")
            
            # Проверяем существование пользователя
            try:
                user = User.objects.get(username=username)
                logger.debug(f"User found: {user.username}, user_type: {user.user_type}")
            except User.DoesNotExist:
                logger.debug(f"User not found: {username}")
                messages.error(request, 'Неверное имя пользователя или пароль')
                return render(request, 'auth_freedom/login.html', {'form': form})
            
            # Пытаемся аутентифицировать
            user = authenticate(username=username, password=password)
            logger.debug(f"Authentication result: {user is not None}")
            
            if user is not None:
                login(request, user)
                logger.debug(f"Login successful for user: {user.username}")
                
                if user.user_type == 'recruiter':
                    return redirect('auth_freedom:recruiter_profile')
                else:
                    return redirect('auth_freedom:candidate_profile')
            else:
                logger.debug(f"Authentication failed for existing user: {username}")
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'auth_freedom/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('auth_freedom:login')

@login_required
def profile_view(request):
    try:
        if request.user.user_type == 'recruiter':
            return redirect('auth_freedom:recruiter_profile')
        elif request.user.user_type == 'candidate':
            return redirect('auth_freedom:candidate_profile')
        else:
            messages.error(request, 'Неверный тип пользователя')
            return redirect('auth_freedom:login')
    except Exception as e:
        logger.error(f"Error in profile_view: {str(e)}")
        messages.error(request, 'Ошибка при загрузке профиля')
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

class RegistrationStep1View(View):
    def get(self, request):
        form = RegistrationStep1Form()
        return render(request, 'auth_freedom/register_step1.html', {'form': form})

    def post(self, request):
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            request.session['registration_step1'] = form.cleaned_data
            return redirect('auth_freedom:register_step2')
        return render(request, 'auth_freedom/register_step1.html', {'form': form})

class RegistrationStep2View(View):
    def get(self, request):
        if 'registration_step1' not in request.session:
            messages.error(request, 'Пожалуйста, заполните первый шаг регисрации')
            return redirect('auth_freedom:register_step1')
        form = RegistrationStep2Form()
        return render(request, 'auth_freedom/register_step2.html', {'form': form})

    def post(self, request):
        form = RegistrationStep2Form(request.POST)
        if form.is_valid():
            request.session['registration_step2'] = form.cleaned_data
            return redirect('auth_freedom:register_step3')
        return render(request, 'auth_freedom/register_step2.html', {'form': form})

class RegistrationStep3View(View):
    def get(self, request):
        if 'registration_step2' not in request.session:
            messages.error(request, 'Пожалуйст, заполните второй шаг регистрации')
            return redirect('auth_freedom:register_step2')
        form = RegistrationStep3Form()
        return render(request, 'auth_freedom/register_step3.html', {'form': form})

    def post(self, request):
        logger.debug("Starting register_step3 view")
        form = RegistrationStep3Form(request.POST)
        
        if form.is_valid():
            logger.debug("Form is valid, processing data")
            try:
                step1_data = request.session.get('registration_step1')
                step2_data = request.session.get('registration_step2')
                
                if not step1_data:
                    messages.error(request, "Ошибка регистрации: данные первого шага не найдены")
                    return render(request, 'auth_freedom/register_step3.html', {'form': form})

                with transaction.atomic():
                    # Отключаем сигналы
                    post_save.disconnect(create_user_profile, sender=User)
                    post_save.disconnect(save_user_profile, sender=User)
                    
                    try:
                        # 1. Создаем пользователя
                        user = User.objects.create_user(
                            username=step1_data['username'],
                            email=step1_data['email'],
                            password=step1_data['password1'],
                            first_name=step1_data['first_name'],
                            last_name=step1_data['last_name'],
                            user_type='candidate'
                        )
                        
                        # 2. Создаем профиль с данными из всех шагов
                        profile_data = {
                            'user': user,
                            'first_name': step1_data['first_name'],
                            'last_name': step1_data['last_name'],
                            'email': step1_data['email'],
                            'phone': step1_data['phone'],
                            'birth_date': step1_data['birth_date'],
                            'gender': step1_data['gender'],
                            'search_status': form.cleaned_data['search_status'],
                            'relocation_status': form.cleaned_data['relocation_status'],
                            'level': form.cleaned_data['level'],
                            'education': {
                                'institution': form.cleaned_data['education_institution'],
                                'faculty': form.cleaned_data['faculty'],
                                'degree': form.cleaned_data['degree'],
                                'graduation_year': form.cleaned_data['graduation_year']
                            }
                        }
                        
                        # Добавляем данные из шага 2
                        if step2_data:
                            profile_data.update(step2_data)
                        
                        # Создаем профиль одним запросом
                        profile = CandidateProfile.objects.create(**profile_data)
                        
                    finally:
                        # Восстанавливаем сигналы
                        post_save.connect(create_user_profile, sender=User)
                        post_save.connect(save_user_profile, sender=User)
                    
                    request.session.pop('registration_step1', None)
                    request.session.pop('registration_step2', None)
                    
                    login(request, user)
                    messages.success(request, "Регистрация успешно завершена!")
                    return redirect('auth_freedom:candidate_profile')
                    
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                messages.error(request, "Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.")
        
        return render(request, 'auth_freedom/register_step3.html', {'form': form})

@login_required
def candidate_profile_view(request):
    if request.user.user_type != 'candidate':
        messages.error(request, 'Неверный тип пользователя')
        return redirect('auth_freedom:profile')
    
    try:
        profile = request.user.candidateprofile
        return render(request, 'auth_freedom/candidate_profile.html', {'profile': profile})
    except CandidateProfile.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('auth_freedom:profile')

@login_required
def recruiter_profile_view(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Неверный тип пользователя')
        return redirect('auth_freedom:profile')
    
    try:
        profile = request.user.recruiterprofile
        return render(request, 'auth_freedom/recruiter_profile.html', {'profile': profile})
    except RecruiterProfile.DoesNotExist:
        messages.error(request, 'Профиль не найден')
        return redirect('auth_freedom:profile')

User = get_user_model()

def register_step1(request):
    if request.method == 'POST':
        form = RegistrationStep1Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.phone = form.cleaned_data['phone']
            user.birth_date = form.cleaned_data['birth_date']
            user.gender = form.cleaned_data['gender']
            user.save()
            
            # Обновляем профиль кандидата
            profile = user.candidate_profile
            profile.first_name = user.first_name
            profile.last_name = user.last_name
            profile.email = user.email
            profile.phone = user.phone
            profile.birth_date = user.birth_date
            profile.gender = user.gender
            profile.save()
            
            return redirect('auth_freedom:register_step2')
    else:
        form = RegistrationStep1Form()
    return render(request, 'auth_freedom/register_step1.html', {'form': form})