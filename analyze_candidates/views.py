from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile
from .services import CandidateAnalysisService
from .models import CandidateAnalysis
import logging

logger = logging.getLogger(__name__)

@login_required
def analyze_candidates(request, vacancy_id):
    logger.debug(f"Starting analyze_candidates view for vacancy_id: {vacancy_id}")
    
    if request.user.user_type != 'recruiter':
        logger.warning(f"Unauthorized access attempt by user: {request.user.id}")
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    logger.debug(f"Found vacancy: {vacancy.title}")
    
    service = CandidateAnalysisService()
    
    # Получаем всех кандидатов
    candidates = CandidateProfile.objects.all()
    logger.debug(f"Total candidates found: {candidates.count()}")
    
    # Добавляем отладочную информацию о каждом кандидате
    for candidate in candidates:
        logger.debug(
            f"Candidate details - ID: {candidate.id}, "
            f"Name: {candidate.user.get_full_name() if candidate.user else 'No user'}, "
            f"Specialization: {getattr(candidate, 'specialization', 'Not specified')}"
        )
    
    # Анализируем каждого кандидата
    for candidate in candidates:
        logger.debug(f"Analyzing candidate: {candidate.id}")
        if not CandidateAnalysis.objects.filter(vacancy=vacancy, candidate=candidate).exists():
            try:
                analysis = service.analyze_candidate(vacancy, candidate)
                if analysis:
                    logger.debug(f"Analysis created successfully for candidate {candidate.id}")
                else:
                    logger.warning(f"Failed to analyze candidate {candidate.id}")
                    messages.warning(request, f'Не удалось проанализировать кандидата {candidate.user.get_full_name()}')
            except Exception as e:
                logger.error(f"Error analyzing candidate {candidate.id}: {str(e)}", exc_info=True)
                messages.error(request, f'Ошибка при анализе кандидата {candidate.user.get_full_name()}: {str(e)}')
    
    # Получаем все анализы для этой вакансии
    analyses = CandidateAnalysis.objects.filter(vacancy=vacancy).select_related('candidate__user').order_by('-match_score', '-reputation_score')
    logger.debug(f"Analyses found for vacancy {vacancy.id}: {analyses.count()}")
    
    for analysis in analyses:
        logger.debug(
            f"Analysis - Candidate: {analysis.candidate.user.get_full_name() if analysis.candidate.user else 'No name'}, "
            f"Match Score: {analysis.match_score}, "
            f"Reputation Score: {analysis.reputation_score}"
        )
    
    context = {
        'vacancy': vacancy,
        'analyses': analyses,
        'all_candidates': candidates
    }
    
    logger.debug("Rendering template with context")
    return render(request, 'analyze_candidates/analysis_results.html', context)
