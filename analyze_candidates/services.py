from openai import OpenAI
import os
import logging
from .models import CandidateAnalysis

logger = logging.getLogger(__name__)

class CandidateAnalysisService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        # Определяем максимальные значения для каждого поля
        self.score_fields = {
            'specialization': 100,
            'hard_skills': 100,
            'experience': 100,
            'education': 100,
            'about_me': 100,
            'soft_skills': 100,
            'tech_stack': 100,
            'languages': 100,
            'level': 100,
            'match_score': 100
        }

    def analyze_candidate(self, vacancy, candidate):
        try:
            prompt = self._create_analysis_prompt(vacancy, candidate)
            
            completion = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
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
        Важно: 
        1. Возвращай числовые значения БЕЗ символа '%' и других специальных символов
        2. Будь максимально строг в оценке - ставь высокие баллы только при полном соответствии
        3. При несоответствии специализации или уровня - общий скор не может быть выше 40
        4. При отсутствии требуемых hard skills - общий скор не может быть выше 30
        5. Учитывай актуальность опыта и технологий

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
        MATCH_SCORE: [общий процент соответствия 0-100]
        SPECIALIZATION: [точность соответствия специализации 0-100]
        HARD_SKILLS: [процент совпадения требуемых навыков 0-100]
        EXPERIENCE: [соответствие опыта требованиям 0-100]
        EDUCATION: [релевантность образования 0-100]
        ABOUT_ME: [релевантность самопрезентации 0-100]
        SOFT_SKILLS: [оценка софт-скиллов 0-100]
        TECH_STACK: [актуальность и соответствие тех. стека 0-100]
        LANGUAGES: [соответствие языковых требований 0-100]
        LEVEL: [соответствие уровню позиции 0-100]
        FEEDBACK: [развернутый анализ сильных и слабых сторон кандидата]
        """

    def _parse_gpt_response(self, response):
        lines = response.strip().split('\n')
        scores = {}
        logger.debug(f"Raw GPT response: {response}")
        
        feedback_text = ""
        parsing_feedback = False
        
        for line in lines:
            if line.strip().startswith('FEEDBACK:'):
                parsing_feedback = True
                feedback_text = line.replace('FEEDBACK:', '').strip()
            elif parsing_feedback:
                feedback_text += " " + line.strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                try:
                    if key == 'match_score':
                        raw_score = float(value)
                        if raw_score > 80:
                            raw_score = raw_score * 0.8
                        scores['match_score'] = raw_score
                    else:
                        max_score = self.score_fields.get(key, 100)
                        raw_value = float(value)
                        if raw_value > 70:
                            raw_value = raw_value * 0.85
                        normalized_value = (raw_value / 100) * max_score
                        scores[f'{key}_score'] = int(normalized_value)
                except (ValueError, TypeError):
                    scores[f'{key}_score'] = 0
        
        scores['feedback'] = feedback_text
        logger.debug(f"Parsed feedback: {feedback_text}")
        
        # Рассчитываем репутационный рейтинг
        reputation_factors = [
            scores.get('specialization_score', 0),
            scores.get('hard_skills_score', 0),
            scores.get('experience_score', 0),
            scores.get('education_score', 0),
            scores.get('tech_stack_score', 0),
            scores.get('languages_score', 0),
            scores.get('level_score', 0)
        ]
        
        # Вычисляем репутационный скор как сумму всех факторов
        scores['reputation_score'] = sum(reputation_factors)
        
        logger.debug(f"Reputation score calculated: {scores['reputation_score']}")
        
        # Находим топ-3 сильнейших качества
        score_items = [(k.replace('_score', ''), v) for k, v in scores.items() 
                      if k.endswith('_score') and k != 'match_score' and k != 'reputation_score']
        top_scores = sorted(score_items, key=lambda x: x[1], reverse=True)[:3]
        
        scores['top_strength_1'] = top_scores[0][0] if len(top_scores) > 0 else ''
        scores['top_strength_2'] = top_scores[1][0] if len(top_scores) > 1 else ''
        scores['top_strength_3'] = top_scores[2][0] if len(top_scores) > 2 else ''
        
        logger.debug(f"Final parsed scores: {scores}")
        return scores