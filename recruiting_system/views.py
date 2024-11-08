from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vacancy, Application

@login_required
def vacancy_list(request):
    vacancies = Vacancy.objects.filter(status='active')
    return render(request, 'recruiting_system/vacancy_list.html', {'vacancies': vacancies})

@login_required
def vacancy_detail(request, pk):
    vacancy = get_object_or_404(Vacancy, pk=pk)
    return render(request, 'recruiting_system/vacancy_detail.html', {'vacancy': vacancy})

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
    return render(request, 'recruiting_system/application_detail.html', {'application': application})
