from django.conf import settings
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile
from .models import AIAnalysis
from openai import OpenAI
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone
import time

logger = logging.getLogger(__name__)

class AIMatchingService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.cache_timeout = 60 * 60 * 24  # 24 часа

    def analyze_candidate_for_vacancy(self, vacancy, candidate):
        try:
            # Проверяем кэш
            cache_key = f'analysis_{vacancy.id}_{candidate.id}'
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
                
            # Проверяем существующий анализ в БД
            existing_analysis = AIAnalysis.objects.filter(
                vacancy=vacancy,
                candidate=candidate,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).first()
            
            if existing_analysis:
                # Кэшируем результат
                cache.set(cache_key, existing_analysis, self.cache_timeout)
                return existing_analysis

            # Выполняем новый анализ
            analysis = self._perform_analysis(vacancy, candidate)
            if analysis:
                cache.set(cache_key, analysis, self.cache_timeout)
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return None
            
    def _perform_analysis(self, vacancy, candidate):
        vacancy_data = self._prepare_vacancy_data(vacancy)
        candidate_data = self._prepare_candidate_data(candidate)
        
        for attempt in range(3):  # Retry механизм
            try:
                response = self._get_ai_response(vacancy_data, candidate_data)
                if response:
                    match_score = self._extract_match_score(response.choices[0].message.content)
                    return AIAnalysis.objects.create(
                        vacancy=vacancy,
                        candidate=candidate,
                        match_score=match_score,
                        feedback=response.choices[0].message.content
                    )
            except Exception as e:
                logger.error(f"Analysis attempt {attempt + 1} failed: {str(e)}")
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
                    
        return None

    def _prepare_vacancy_data(self, vacancy):
        return {
            'title': vacancy.title,
            'requirements': vacancy.requirements,
            'desired_experience': vacancy.desired_experience,
            'desired_level': vacancy.desired_level,
            'tech_stack': vacancy.tech_stack,
            'hard_skills': vacancy.hard_skills,
            'soft_skills': vacancy.soft_skills,
        }

    def _prepare_candidate_data(self, candidate):
        return {
            'experience': candidate.experience,
            'level': candidate.level,
            'hard_skills': candidate.hard_skills,
            'soft_skills': candidate.soft_skills,
            'specialization': candidate.specialization,
            'about_me': candidate.about_me,
            'languages': candidate.languages,
        }

    def _get_ai_response(self, vacancy_data, candidate_data, timeout=30):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Ты - HR аналитик, специализирующийся на подборе IT специалистов. Проведи анализ соответствия кандидата требованиям вакансии."},
                    {"role": "user", "content": self._create_prompt(vacancy_data, candidate_data)}
                ],
                timeout=timeout
            )
            return response
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            return None

    def _create_prompt(self, vacancy_data, candidate_data):
        return f"""
        Проанализируй соответствие кандидата требованиям вакансии:
        
        Вакансия:
        {vacancy_data}
        
        Кандидат:
        {candidate_data}
        
        Оцени соответствие по следующим критериям:
        1. Опыт работы
        2. Уровень квалификации
        3. Технические навыки
        4. Софт-скиллы
        5. Образование
        
        Предоставь:
        1. Процент соответствия (0-100)
        2. Подробный фидбэк по каждому критерию
        3. Рекомендации по улучшению
        """

    def _extract_match_score(self, response):
        try:
            import re
            matches = re.findall(r'(\d+)%', response)
            return float(matches[0]) if matches else 0
        except:
            return 0