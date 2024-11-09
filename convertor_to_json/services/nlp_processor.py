from natasha import (
    Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger,
    NewsNERTagger, NamesExtractor, DatesExtractor
)
import spacy
import re
import os
from openai import OpenAI
import json
import logging
from time import time

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self):
        # Проверяем наличие API ключа
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            logger.error("OpenAI API key not found!")
            raise ValueError("OpenAI API key not found in environment variables")
            
        # Правильная инициализация клиента с API ключом
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Загружаем SpaCy для русского языка
        try:
            self.nlp = spacy.load("ru_core_news_lg")
        except Exception as e:
            logger.error(f"Failed to load SpaCy model: {str(e)}")
            self.nlp = None
        
        # Наташа для русских имен и дат
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.names_extractor = NamesExtractor(self.morph_vocab)
        self.dates_extractor = DatesExtractor(self.morph_vocab)
        
        self.patterns = {
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                r'(?i)(?:email|почта|e-mail)[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})'
            ],
            'phone': [
                r'(?:\+7|8)[-(]?\d{3}[-)]?\d{3}[-]?\d{2}[-]?\d{2}',
                r'\+?\d{1,3}[-.(]?\d{3}[-.)]\d{3}[-.]?\d{4}'
            ]
        }

    def process_resume(self, text):
        try:
            start_time = time()
            logger.info("Starting resume processing")
            
            # Предварительная обработка текста
            cleaned_text = self._preprocess_text(text)
            
            # Базовое извлечение через регулярные выражения
            parsed_data = self._extract_basic_info(cleaned_text)
            
            # Используем GPT-4 для глубокого анализа
            logger.info("Starting GPT-4 analysis")
            gpt_start_time = time()
            
            gpt_data = self._extract_with_gpt4(cleaned_text)
            
            logger.info(f"GPT-4 analysis completed in {time() - gpt_start_time:.2f} seconds")
            
            if gpt_data:
                parsed_data.update(gpt_data)
                # Добавляем логирование для about_me
                logger.info(f"About me before extraction: {parsed_data.get('about_me', 'Not found')}")
                about_me = self._extract_about_me(parsed_data)
                parsed_data['about_me'] = about_me
                logger.info(f"About me after extraction: {about_me[:100]}...")
            else:
                logger.warning("GPT-4 analysis returned no data")
            
            # Валидация и форматирование
            result = self._format_and_validate(parsed_data)
            
            logger.info(f"Resume processing completed in {time() - start_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            return None

    def _extract_with_gpt4(self, text):
        try:
            logger.info("Sending request to GPT-4")
            
            prompt = self._create_detailed_prompt(text)
            logger.debug(f"GPT-4 prompt length: {len(prompt)} characters")
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": """Ты - эксперт по анализу резюме. 
                    Извлеки всю важную информацию из текста резюме максимально точно.
                    Особое внимание удели техническим навыкам, опыту работы и образованию."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            logger.info("Received response from GPT-4")
            logger.debug(f"Response tokens: {response.usage.total_tokens}")
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully parsed GPT-4 response")
            logger.debug(f"Parsed fields: {list(result.keys())}")
            
            return result
            
        except Exception as e:
            logger.error(f"GPT-4 extraction error: {str(e)}")
            return None

    def _preprocess_text(self, text):
        # Очистка текста
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s@.-]+', ' ', text)
        return text.strip()

    def _extract_basic_info(self, text):
        data = {'raw_text': text}
        
        # Извлечение базовой информации через регулярные выражения
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    if self._validate_field(field, value):
                        data[field] = value.strip()
                        break
        
        return data

    def _validate_field(self, field, value):
        if field == 'email':
            return re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', value)
        elif field == 'phone':
            return len(re.sub(r'\D', '', value)) >= 10
        return True

    def _create_detailed_prompt(self, text):
        return f"""Проанализируй текст резюме и извлеки структурированную информацию.
        Обрати особое внимание на:
        1. Личную информацию (имя, контакты, дата рождения)
        2. Технический стек и навыки
        3. Опыт работы с точными датами
        4. Образование и сертификации
        5. Уровень владения языками
        
        Текст резюме:
        {text}
        
        Верни результат в формате JSON со следующей структурой:
        {{
            "personal_info": {{
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "birth_date": "YYYY-MM-DD",
                "gender": "male/female/other",
                "location": {{
                    "country": "",
                    "region": ""
                }},
                "social_networks": [],
                "about": ""
            }},
            "professional_info": {{
                "title": "",
                "experience_years": 0,
                "current_position": "",
                "desired_position": "",
                "desired_salary": 0,
                "currently_employed": false,
                "level": ""
            }},
            "skills": {{
                "tech_stack": [],
                "hard_skills": [],
                "soft_skills": [],
                "languages": []
            }},
            "education": {{
                "degree": "",
                "institution": "",
                "faculty": "",
                "graduation_year": 0,
                "certifications": []
            }},
            "experience": [
                {{
                    "company": "",
                    "position": "",
                    "start_date": "YYYY-MM-DD",
                    "end_date": "YYYY-MM-DD",
                    "responsibilities": [],
                    "achievements": []
                }}
            ]
        }}"""

    def test_gpt_connection(self):
        try:
            logger.info("Testing GPT connection...")
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Respond with 'OK' if you receive this message."}
                ],
                max_tokens=10
            )
            result = response.choices[0].message.content
            logger.info(f"GPT test response: {result}")
            return result == "OK"
        except Exception as e:
            logger.error(f"GPT connection test failed: {str(e)}")
            return False

    def _format_and_validate(self, data):
        try:
            name_info = self._extract_name(data)
            personal_info = self._extract_personal_info(data)
            
            formatted_data = {
                'raw_text': data.get('raw_text', ''),
                'first_name': name_info['first_name'],
                'last_name': name_info['last_name'],
                'name': name_info['full_name'],
                'email': data.get('email', ''),
                'phone': personal_info['phone'],
                'gender': personal_info['gender'],
                'birth_date': personal_info['birth_date'],
                'about_me': personal_info['about'],
                'currently_employed': personal_info['currently_employed'],
                'experience_years': self._extract_experience_years(data),
                'specialization': self._extract_specialization(data),
                'tech_stack': self._extract_tech_stack(data),
                'hard_skills': self._extract_skills(data, 'hard'),
                'soft_skills': self._extract_skills(data, 'soft'),
                'education': self._extract_education(data),
                'work_experience': self._extract_work_experience(data),
                'languages': self._extract_languages(data),
                'desired_salary': self._extract_salary(data),
                'country': personal_info['country'],
                'region': personal_info['region'],
                'social_networks': personal_info['social_networks'],
                'level': personal_info['level'],
                'certifications': self._extract_certifications(data)
            }
            
            return formatted_data
        except Exception as e:
            logger.error(f"Error formatting data: {str(e)}")
            return None

    def _extract_name(self, data):
        """Извлекает имя и фамилию из данных"""
        if 'personal_info' in data:
            first_name = data['personal_info'].get('first_name', '')
            last_name = data['personal_info'].get('last_name', '')
            return {
                'first_name': first_name,
                'last_name': last_name,
                'full_name': f"{first_name} {last_name}".strip()
            }
        return {'first_name': '', 'last_name': '', 'full_name': data.get('name', '')}

    def _extract_personal_info(self, data):
        """Извлекает персональную информацию"""
        if 'personal_info' in data:
            about_text = data['personal_info'].get('about', '')  # Получаем текст из поля 'about'
            return {
                'gender': data['personal_info'].get('gender', ''),
                'birth_date': data['personal_info'].get('birth_date', ''),
                'phone': data['personal_info'].get('phone', ''),
                'about': about_text,  # Сохраняем как 'about'
                'currently_employed': data['professional_info'].get('currently_employed', False),
                'country': data['personal_info'].get('location', {}).get('country', 'Казахстан'),
                'region': data['personal_info'].get('location', {}).get('region', ''),
                'social_networks': data['personal_info'].get('social_networks', []),
                'level': data['professional_info'].get('level', 'Без опыта')
            }
        return {
            'gender': '',
            'birth_date': '',
            'phone': data.get('phone', ''),
            'about': '',
            'currently_employed': False,
            'country': 'Казахстан',
            'region': '',
            'social_networks': [],
            'level': 'Без опыта'
        }

    def _extract_experience_years(self, data):
        """Извлекает общий опыт работы"""
        if 'professional_info' in data:
            return data['professional_info'].get('experience_years', 0)
        return data.get('experience_years', 0)

    def _extract_specialization(self, data):
        """Извлекает специализацию"""
        if 'professional_info' in data:
            return data['professional_info'].get('current_position', '') or data['professional_info'].get('title', '')
        return data.get('specialization', '')

    def _extract_tech_stack(self, data):
        """Извлекает технический стек"""
        if 'skills' in data:
            return data['skills'].get('tech_stack', [])
        return data.get('tech_stack', [])

    def _extract_skills(self, data, skill_type):
        """Извлекает навыки определенного типа"""
        if 'skills' in data:
            if skill_type == 'hard':
                return data['skills'].get('hard_skills', [])
            else:
                return data['skills'].get('soft_skills', [])
        return []

    def _extract_education(self, data):
        """Извлекает информацию об образовании"""
        if 'education' in data:
            return data['education']
        return data.get('education', {})

    def _extract_work_experience(self, data):
        """Извлекает опыт работы"""
        if 'experience' in data:
            return [{
                'company': exp.get('company', ''),
                'position': exp.get('position', ''),
                'start_date': exp.get('start_date', ''),
                'end_date': exp.get('end_date', ''),
                'responsibilities': exp.get('responsibilities', []),
                'achievements': exp.get('achievements', [])
            } for exp in data['experience']]
        return data.get('work_experience', [])

    def _extract_languages(self, data):
        """Извлекает языки"""
        if 'skills' in data and 'languages' in data['skills']:
            return data['skills']['languages']
        return data.get('languages', ['Русский'])

    def _extract_salary(self, data):
        """Извлекает желаемую зарплату"""
        if 'professional_info' in data:
            return data['professional_info'].get('desired_salary', 0)
        return data.get('desired_salary', 0)

    def _extract_location(self, data):
        """Извлекает информацию о местоположении"""
        if 'personal_info' in data and 'location' in data['personal_info']:
            return {'country': data['personal_info']['location']}
        return data.get('location', {'country': 'Казахстан'})

    def _extract_certifications(self, data):
        """Извлекает сертификаты"""
        if 'education' in data and 'certifications' in data['education']:
            return data['education']['certifications']
        return data.get('certifications', [])

    def _extract_about_me(self, data):
        """Извлекает информацию о себе"""
        logger.info(f"Extracting about_me from data: {data.keys()}")
        
        if isinstance(data, dict):
            if 'personal_info' in data:
                logger.info(f"Found personal_info: {data['personal_info'].keys()}")
                if 'about_me' in data['personal_info']:
                    about_me = data['personal_info']['about_me']
                    logger.info(f"Found about_me in personal_info: {about_me[:100]}...")
                    return about_me
            
            if 'about_me' in data:
                about_me = data['about_me']
                logger.info(f"Found about_me in root: {about_me[:100]}...")
                return about_me
                
            if 'description' in data:
                about_me = data['description']
                logger.info(f"Found description instead of about_me: {about_me[:100]}...")
                return about_me
        
        logger.warning("No about_me information found in data")
        return ''