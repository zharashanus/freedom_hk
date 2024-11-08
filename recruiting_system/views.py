from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Vacancy, Application, CandidateProfile
from .forms import VacancyForm, ApplicationForm

@login_required
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='active')
    context = {
        'vacancies': vacancies,
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'recruiting_system/vacancy_list.html', context)

@login_required
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    has_applied = False
    if request.user.user_type == 'candidate':
        has_applied = Application.objects.filter(
            vacancy=vacancy,
            candidate=request.user.candidate_profile
        ).exists()
    return render(request, 'recruiting_system/vacancy_detail.html', {
        'vacancy': vacancy,
        'has_applied': has_applied
    })

@login_required
def application_list(request):
    if request.user.user_type == 'recruiter':
        applications = Application.objects.filter(vacancy__recruiter__user=request.user)
    else:
        applications = Application.objects.filter(candidate__user=request.user)
    return render(request, 'recruiting_system/application_list.html', {'applications': applications})

@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.user.user_type == 'recruiter' and application.vacancy.recruiter.user != request.user:
        messages.error(request, 'У вас нет доступа к этой заявке')
        return redirect('recruiting_system:application_list')
    if request.user.user_type == 'candidate' and application.candidate.user != request.user:
        messages.error(request, 'У вас нет доступа к этой заявке')
        return redirect('recruiting_system:application_list')
    return render(request, 'recruiting_system/application_detail.html', {'application': application})

@login_required
def apply_vacancy(request, pk):
    if request.user.user_type != 'candidate':
        messages.error(request, 'Только кандидаты могут откликаться на вакансии')
        return redirect('recruiting_system:vacancy_list')
    
    vacancy = get_object_or_404(Vacancy, pk=pk)
    if Application.objects.filter(vacancy=vacancy, candidate=request.user.candidate_profile).exists():
        messages.error(request, 'Вы уже откликнулись на эту вакансию')
        return redirect('recruiting_system:vacancy_detail', pk=pk)

@login_required
def vacancy_create(request):
    print(f"Method: {request.method}")  # Отладка
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Только рекрутеры могут создавать вакансии')
        return redirect('recruiting_system:vacancy_list')
    
    if request.method == 'POST':
        print(f"POST data: {request.POST}")  # Отладка
        form = VacancyForm(request.POST)
        if form.is_valid():
            print("Form is valid")  # Отладка
            vacancy = form.save(commit=False)
            vacancy.recruiter = request.user.recruiter_profile
            vacancy.save()
            messages.success(request, 'Вакансия успешно создана')
            return redirect('recruiting_system:vacancy_detail', pk=vacancy.pk)
        else:
            print(f"Form errors: {form.errors}")  # Отладка
    else:
        form = VacancyForm()
    
    return render(request, 'recruiting_system/vacancy_form.html', {'form': form, 'action': 'Создать'})

@login_required
def vacancy_edit(request, pk):
    if request.user.user_type not in ['recruiter', 'admin']:
        messages.error(request, 'Только рекрутеры и администраторы могут редактировать вакансии')
        return redirect('recruiting_system:vacancy_list')
    
    # Для администраторов пропускаем проверку на принадлежность вакансии
    if request.user.user_type == 'admin':
        vacancy = get_object_or_404(Vacancy, pk=pk)
    else:
        vacancy = get_object_or_404(Vacancy, pk=pk, recruiter__user=request.user)
    
    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вакансия успешно обновлена')
            return redirect('recruiting_system:vacancy_detail', pk=vacancy.pk)
    else:
        form = VacancyForm(instance=vacancy)
    
    return render(request, 'recruiting_system/vacancy_form.html', {
        'form': form,
        'action': 'Редактировать'
    })

@login_required
def update_application_status(request, pk):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Только рекрутеры могут обновлять статус заявок')
        return redirect('recruiting_system:application_list')
    
    application = get_object_or_404(Application, pk=pk, vacancy__recruiter__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Application.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, 'Статус заявки успешно обновлен')
        else:
            messages.error(request, 'Некорректный статус')
    
    return redirect('recruiting_system:application_detail', pk=pk)

@login_required
def candidate_list(request):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    candidates = CandidateProfile.objects.all()
    
    # Фильтрация
    specialization = request.GET.get('specialization')
    experience = request.GET.get('experience')
    level = request.GET.get('level')
    search_status = request.GET.get('search_status')
    
    if specialization:
        candidates = candidates.filter(specialization__icontains=specialization)
    if experience:
        candidates = candidates.filter(experience__gte=experience)
    if level:
        candidates = candidates.filter(level=level)
    if search_status:
        candidates = candidates.filter(search_status=search_status)
    
    return render(request, 'recruiting_system/candidate_list.html', {
        'candidates': candidates,
        'level_choices': CandidateProfile.LEVEL_CHOICES,
        'search_status_choices': CandidateProfile.SEARCH_STATUS_CHOICES,
    })

@login_required
def candidate_detail(request, pk):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    candidate = get_object_or_404(CandidateProfile, pk=pk)
    return render(request, 'recruiting_system/candidate_detail.html', {
        'candidate': candidate
    })
