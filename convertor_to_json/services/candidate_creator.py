from auth_freedom.models import User, CandidateProfile
from django.db import transaction
import uuid
from datetime import datetime
import re

class CandidateCreator:
    def create_from_parsed_data(self, parsed_data):
        with transaction.atomic():
            # Получаем или генерируем имя и фамилию
            first_name = parsed_data.get('first_name', 'Не указано')
            last_name = parsed_data.get('last_name', 'Не указано')
            
            username = f"candidate_{uuid.uuid4().hex[:8]}"
            
            user = User.objects.create_user(
                username=username,
                password=uuid.uuid4().hex,
                first_name=first_name,
                last_name=last_name,
                email=parsed_data.get('email', ''),
                user_type='candidate'
            )
            
            profile = CandidateProfile.objects.get(user=user)
            
            # Заполняем все доступные поля
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email = parsed_data.get('email', '')
            profile.phone = parsed_data.get('phone', '')
            profile.birth_date = datetime.strptime(parsed_data.get('birth_date', '2000-01-01'), '%Y-%m-%d')
            profile.gender = parsed_data.get('gender', 'other')
            profile.about_me = parsed_data.get('about_me', '')
            profile.specialization = parsed_data.get('specialization', '')
            profile.experience = parsed_data.get('experience_years', 0)
            profile.country = parsed_data.get('country', 'Казахстан')
            profile.region = parsed_data.get('region', '')
            profile.currently_employed = parsed_data.get('currently_employed', False)
            profile.level = parsed_data.get('level', 'Без опыта')
            
            # Добавляем навыки
            profile.tech_stack = parsed_data.get('tech_stack', [])
            profile.hard_skills = parsed_data.get('hard_skills', [])
            profile.soft_skills = parsed_data.get('soft_skills', [])
            
            # Добавляем опыт работы
            profile.work_experience = parsed_data.get('work_experience', [])
            
            # Добавляем социальные сети
            profile.social_networks = parsed_data.get('social_networks', [])
            
            # Добавляем сертификаты
            profile.certifications = parsed_data.get('certifications', [])
            
            # Добавляем образование
            profile.education = parsed_data.get('education', {})
            
            # Добавляем языки
            profile.languages = parsed_data.get('languages', [])
            
            profile.save()
            return profile