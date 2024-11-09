from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile
from .services import CandidateAnalysisService
from .models import CandidateAnalysis
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

def get_candidate_data_hash(candidate):
    """Создает хеш из всех релевантных данных кандидата"""
    data = {
        'specialization': candidate.specialization,
        'experience': candidate.experience,
        'hard_skills': list(candidate.hard_skills),
        'level': candidate.level,
        'about_me': candidate.about_me,
        'education': candidate.education,
        'languages': list(candidate.languages),
        'tech_stack': list(candidate.tech_stack),
        'soft_skills': list(candidate.soft_skills),
    }
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()

@login_required
def analyze_candidates(request, vacancy_id):
    logger.debug(f"Starting analyze_candidates view for vacancy_id: {vacancy_id}")
    
    if request.user.user_type != 'recruiter':
        logger.warning(f"Unauthorized access attempt by user: {request.user.id}")
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    logger.debug(f"Found vacancy: {vacancy.title}")
    
    # Получаем существующие анализы
    analyses = CandidateAnalysis.objects.filter(vacancy=vacancy).select_related('candidate__user')
    logger.debug(f"Total analyses found: {analyses.count()}")
    for analysis in analyses:
        logger.debug(f"Analysis for candidate {analysis.candidate.id}: feedback={analysis.feedback}")
    
    # Проверяем, есть ли новые кандидаты без анализа
    existing_candidate_ids = analyses.values_list('candidate_id', flat=True)
    all_candidates = CandidateProfile.objects.all()
    new_candidates = all_candidates.exclude(id__in=existing_candidate_ids)
    
    # Выполняем анализ только если это POST запрос с параметром reanalyze
    if request.method == 'POST' and request.POST.get('reanalyze') == 'true':
        candidates_to_analyze = []
        
        for candidate in all_candidates:
            current_hash = get_candidate_data_hash(candidate)
            existing_analysis = CandidateAnalysis.objects.filter(
                vacancy=vacancy,
                candidate=candidate
            ).first()
            
            if not existing_analysis or existing_analysis.candidate_data_hash != current_hash:
                candidates_to_analyze.append((candidate, current_hash))
        
        if not candidates_to_analyze:
            messages.info(request, 'Нет новых данных для анализа')
            return redirect('analyze_candidates:analyze_candidates', vacancy_id=vacancy_id)
        
        service = CandidateAnalysisService()
        for candidate, current_hash in candidates_to_analyze:
            try:
                if request.POST.get('reanalyze') == 'true':
                    CandidateAnalysis.objects.filter(vacancy=vacancy, candidate=candidate).delete()
                
                analysis = service.analyze_candidate(vacancy, candidate)
                if analysis:
                    analysis.candidate_data_hash = current_hash
                    analysis.save()
                    logger.debug(f"Analysis created for candidate {candidate.id}")
                else:
                    logger.warning(f"Failed to analyze candidate {candidate.id}")
            except Exception as e:
                logger.error(f"Error analyzing candidate {candidate.id}: {str(e)}", exc_info=True)
                messages.error(request, f'Ошибка при анализе кандидата {candidate.user.get_full_name()}: {str(e)}')
    
    # Получаем обновленный список анализов
    analyses = CandidateAnalysis.objects.filter(vacancy=vacancy).select_related('candidate__user').order_by('-match_score', '-reputation_score')
    
    context = {
        'vacancy': vacancy,
        'analyses': analyses,
        'all_candidates': all_candidates,
    }
    
    return render(request, 'analyze_candidates/analysis_results.html', context)

@login_required
def reanalyze_candidate(request, vacancy_id, candidate_id):
    if request.user.user_type != 'recruiter':
        messages.error(request, 'Доступ запрещен')
        return redirect('recruiting_system:vacancy_list')
    
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    candidate = get_object_or_404(CandidateProfile, id=candidate_id)
    
    current_hash = get_candidate_data_hash(candidate)
    existing_analysis = CandidateAnalysis.objects.filter(
        vacancy=vacancy,
        candidate=candidate
    ).first()
    
    if existing_analysis and existing_analysis.candidate_data_hash == current_hash:
        messages.info(request, f'Данные кандидата {candidate.user.get_full_name()} не изменились с момента последнего анализа')
        return redirect('analyze_candidates:analyze_candidates', vacancy_id=vacancy_id)
    
    # Удаляем старый анализ
    CandidateAnalysis.objects.filter(vacancy=vacancy, candidate=candidate).delete()
    
    # Создаем новый анализ
    service = CandidateAnalysisService()
    try:
        analysis = service.analyze_candidate(vacancy, candidate)
        if analysis:
            analysis.candidate_data_hash = current_hash
            analysis.save()
            messages.success(request, f'Анализ кандидата {candidate.user.get_full_name()} успешно обновлен')
        else:
            messages.warning(request, f'Не удалось обновить анализ кандидата {candidate.user.get_full_name()}')
    except Exception as e:
        logger.error(f"Error reanalyzing candidate {candidate.id}: {str(e)}", exc_info=True)
        messages.error(request, f'Ошибка при повторном анализе кандидата {candidate.user.get_full_name()}: {str(e)}')
    
    return redirect('analyze_candidates:analyze_candidates', vacancy_id=vacancy_id)
