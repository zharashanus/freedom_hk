from django.conf import settings
from recruiting_system.models import Vacancy
from auth_freedom.models import CandidateProfile
from .models import AIAnalysis
from openai import OpenAI
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class AIMatchingService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.executor = ThreadPoolExecutor(max_workers=3)

    def analyze_candidate_for_vacancy(self, vacancy, candidate):
        try:
            # Проверяем существующий анализ
            existing_analysis = AIAnalysis.objects.filter(
                vacancy=vacancy,
                candidate=candidate
            ).first()
            
            if existing_analysis:
                return existing_analysis

            # Подготовка данных
            vacancy_data = self._prepare_vacancy_data(vacancy)
            candidate_data = self._prepare_candidate_data(candidate)

            # Выполняем анализ с таймаутом
            response = self._get_ai_response(vacancy_data, candidate_data)
            
            if not response:
                logger.error(f"Failed to get AI response for candidate {candidate.id}")
                return None

            match_score = self._extract_match_score(response.choices[0].message.content)
            
            analysis = AIAnalysis.objects.create(
                vacancy=vacancy,
                candidate=candidate,
                match_score=match_score,
                feedback=response.choices[0].message.content
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
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