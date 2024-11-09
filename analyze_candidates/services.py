from openai import OpenAI
import os
import logging
from .models import CandidateAnalysis

logger = logging.getLogger(__name__)

class CandidateAnalysisService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def analyze_candidate(self, vacancy, candidate):
        try:
            prompt = self._create_analysis_prompt(vacancy, candidate)
            
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Ты HR-аналитик, специализирующийся на оценке соответствия кандидатов вакансиям."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response = completion.choices[0].message.content
            scores = self._parse_gpt_response(response)
            
            analysis = CandidateAnalysis.objects.create(
                vacancy=vacancy,
                candidate=candidate,
                **scores
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing candidate: {str(e)}")
            return None

    def _create_analysis_prompt(self, vacancy, candidate):
        return f"""
        Проанализируй соответствие кандидата вакансии и оцени по следующим критериям.
        Важно: возвращай числовые значения БЕЗ символа '%' и других специальных символов.

        Вакансия:
        - Название: {vacancy.title}
        - Требуемая специализация: {vacancy.desired_specialization}
        - Требуемый опыт: {vacancy.desired_experience} лет
        - Требуемые навыки: {', '.join(vacancy.hard_skills)}
        - Требуемый уровень: {vacancy.desired_level}

        Кандидат:
        - Специализация: {candidate.specialization}
        - Опыт работы: {candidate.experience} лет
        - Навыки: {', '.join(candidate.hard_skills)}
        - Уровень: {candidate.level}
        - О себе: {candidate.about_me}
        - Образование: {candidate.education}
        - Языки: {', '.join(candidate.languages)}
        - Технический стек: {', '.join(candidate.tech_stack)}
        - Софт-скиллы: {', '.join(candidate.soft_skills)}

        Оцени каждый критерий и верни результат СТРОГО в следующем формате (только числа без символов):
        MATCH_SCORE: 85
        SPECIALIZATION: 90
        HARD_SKILLS: 75
        EXPERIENCE: 80
        EDUCATION: 45
        ABOUT_ME: 40
        SOFT_SKILLS: 35
        TECH_STACK: 40
        LANGUAGES: 20
        LEVEL: 15
        FEEDBACK: [здесь развернутый отзыв о кандидате]
        """

    def _parse_gpt_response(self, response):
        lines = response.strip().split('\n')
        scores = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'feedback':
                    scores['feedback'] = value
                else:
                    # Удаляем символ '%' и другие нечисловые символы
                    value = ''.join(c for c in value if c.isdigit() or c == '.')
                    if key == 'match_score':
                        try:
                            scores['match_score'] = float(value)
                        except (ValueError, TypeError):
                            scores['match_score'] = 0.0
                    else:
                        try:
                            scores[f'{key}_score'] = int(float(value))
                        except (ValueError, TypeError):
                            scores[f'{key}_score'] = 0
        
        # Вычисляем общий репутационный скор
        scores['reputation_score'] = sum([
            scores.get('specialization_score', 0),
            scores.get('hard_skills_score', 0),
            scores.get('experience_score', 0),
            scores.get('education_score', 0),
            scores.get('about_me_score', 0),
            scores.get('soft_skills_score', 0),
            scores.get('tech_stack_score', 0),
            scores.get('languages_score', 0),
            scores.get('level_score', 0)
        ])
        
        return scores 