from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile
from .services import AIMatchingService
from .models import AIAnalysis

@login_required
def analyze_candidates(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    candidates = CandidateProfile.objects.all()[:10]  # Ограничиваем количество кандидатов для анализа
    
    ai_service = AIMatchingService()
    
    for candidate in candidates:
        analysis = ai_service.analyze_candidate_for_vacancy(vacancy, candidate)
        if not analysis:
            messages.warning(request, f'Не удалось проанализировать кандидата {candidate.user.get_full_name()}')
    
    analyses = AIAnalysis.objects.filter(vacancy=vacancy).order_by('-match_score')
    
    return render(request, 'ai_assistant/analysis_results.html', {
        'vacancy': vacancy,
        'analyses': analyses
    })

@login_required
def candidate_analysis(request, candidate_id):
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    analyses = AIAnalysis.objects.filter(candidate=candidate).order_by('-match_score')
    
    return render(request, 'ai_assistant/candidate_analysis.html', {
        'candidate': candidate,
        'analyses': analyses
    })
