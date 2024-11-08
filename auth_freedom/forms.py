from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CandidateProfile
import json

class ExtendedUserRegistrationForm(UserCreationForm):
    # Основные поля пользователя
    first_name = forms.CharField(max_length=100, required=True, label='Имя')
    last_name = forms.CharField(max_length=100, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')

    # Дополнительные поля профиля
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label='Дата рождения'
    )
    gender = forms.ChoiceField(
        choices=CandidateProfile.GENDER_CHOICES,
        required=True,
        label='Пол'
    )
    about_me = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='О себе'
    )
    specialization = forms.CharField(
        max_length=100,
        required=True,
        label='Специализация'
    )
    experience = forms.IntegerField(
        min_value=0,
        required=True,
        label='Опыт работы (лет)'
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        label='Страна',
        widget=forms.TextInput(attrs={
            'list': 'countries',
            'class': 'form-control'
        })
    )
    region = forms.CharField(
        max_length=100,
        required=True,
        label='Регион'
    )
    languages = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите языки через запятую (например: Русский, Английский, Казахский)',
            'class': 'form-control'
        }),
        required=True,
        label='Языки'
    )
    hard_skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите технические навыки через запятую (например: Python, Django, PostgreSQL)',
            'class': 'form-control'
        }),
        required=True,
        label='Технические навыки'
    )
    soft_skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите софт-скиллы через запятую (например: Коммуникабельность, Работа в команде)',
            'class': 'form-control'
        }),
        required=False,
        label='Софт-скиллы'
    )
    desired_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label='Желаемая зарплата'
    )
    search_status = forms.ChoiceField(
        choices=CandidateProfile.SEARCH_STATUS_CHOICES,
        required=True,
        label='Статус поиска'
    )
    relocation_status = forms.ChoiceField(
        choices=CandidateProfile.RELOCATION_CHOICES,
        required=True,
        label='Готовность к переезду'
    )
    level = forms.ChoiceField(
        choices=CandidateProfile.LEVEL_CHOICES,
        required=True,
        label='Уровень'
    )
    education_institution = forms.CharField(
        max_length=200,
        required=True,
        label='Учебное заведение'
    )
    education_faculty = forms.CharField(
        max_length=200,
        required=True,
        label='Факультет'
    )
    education_degree = forms.ChoiceField(
        choices=[
            ('secondary', 'Среднее образование'),
            ('vocational', 'Среднее специальное'),
            ('bachelor', 'Бакалавр'),
            ('master', 'Магистр'),
            ('phd', 'PhD'),
            ('other', 'Другое')
        ],
        required=True,
        label='Степень'
    )
    graduation_year = forms.IntegerField(
        min_value=1950,
        max_value=2030,
        required=True,
        label='Год окончания'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')

    def clean_languages(self):
        languages = self.cleaned_data.get('languages')
        return [lang.strip() for lang in languages.split(',') if lang.strip()]

    def clean_hard_skills(self):
        hard_skills = self.cleaned_data.get('hard_skills')
        return [skill.strip() for skill in hard_skills.split(',') if skill.strip()]

    def clean_soft_skills(self):
        soft_skills = self.cleaned_data.get('soft_skills')
        return [skill.strip() for skill in soft_skills.split(',') if skill.strip()]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'candidate'
        if commit:
            user.save()
            education_data = {
                'institution': self.cleaned_data['education_institution'],
                'faculty': self.cleaned_data['education_faculty'],
                'degree': self.cleaned_data['education_degree'],
                'graduation_year': self.cleaned_data['graduation_year']
            }
            
            CandidateProfile.objects.create(
                user=user,
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                email=self.cleaned_data['email'],
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                gender=self.cleaned_data['gender'],
                about_me=self.cleaned_data['about_me'],
                specialization=self.cleaned_data['specialization'],
                experience=self.cleaned_data['experience'],
                country=self.cleaned_data['country'],
                region=self.cleaned_data['region'],
                languages=self.cleaned_data['languages'],
                desired_salary=self.cleaned_data['desired_salary'],
                search_status=self.cleaned_data['search_status'],
                relocation_status=self.cleaned_data['relocation_status'],
                level=self.cleaned_data['level'],
                hard_skills=self.cleaned_data['hard_skills'],
                soft_skills=self.cleaned_data['soft_skills'],
                education=education_data
            )
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль') 

class CandidateProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label='Имя')
    last_name = forms.CharField(max_length=100, required=True, label='Фамилия')
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=True, label='Телефон')
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label='Дата рождения'
    )
    gender = forms.ChoiceField(
        choices=CandidateProfile.GENDER_CHOICES,
        required=True,
        label='Пол'
    )
    about_me = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label='О себе'
    )
    specialization = forms.CharField(max_length=100, required=True, label='Специализация')
    experience = forms.IntegerField(min_value=0, required=True, label='Опыт работы (лет)')
    country = forms.CharField(max_length=100, required=True, label='Страна')
    region = forms.CharField(max_length=100, required=True, label='Регион')
    languages = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ввведите языки через запятую'
        }),
        required=False
    )
    hard_skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите технические навыки через запятую'
        }),
        required=False
    )
    soft_skills = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите софт-скиллы через запятую'
        }),
        required=False
    )
    desired_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label='Желаемая зарплата'
    )
    search_status = forms.ChoiceField(
        choices=CandidateProfile.SEARCH_STATUS_CHOICES,
        required=True,
        label='Статус поиска'
    )
    relocation_status = forms.ChoiceField(
        choices=CandidateProfile.RELOCATION_CHOICES,
        required=True,
        label='Готовность к переезду'
    )
    level = forms.ChoiceField(
        choices=CandidateProfile.LEVEL_CHOICES,
        required=True,
        label='Уровень'
    )
    education_institution = forms.CharField(
        max_length=200,
        required=True,
        label='Учебное заведение'
    )
    education_faculty = forms.CharField(
        max_length=200,
        required=True,
        label='Факультет'
    )
    education_degree = forms.ChoiceField(
        choices=[
            ('secondary', 'Среднее образование'),
            ('vocational', 'Среднее специальное'),
            ('bachelor', 'Бакалавр'),
            ('master', 'Магистр'),
            ('phd', 'PhD'),
            ('other', 'Другое')
        ],
        required=True,
        label='Степень'
    )
    graduation_year = forms.IntegerField(
        min_value=1950,
        max_value=2030,
        required=True,
        label='Год окончания'
    )
    work_experience_company = forms.CharField(
        max_length=200,
        required=False,
        label='Название компании'
    )
    work_experience_position = forms.CharField(
        max_length=200,
        required=False,
        label='Должность'
    )
    work_experience_start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Дата начала'
    )
    work_experience_end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Дата окончания'
    )
    work_experience_description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Описание обязанностей'
    )

    class Meta:
        model = CandidateProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'birth_date',
            'gender', 'about_me', 'specialization', 'experience',
            'country', 'region', 'languages', 'hard_skills', 'soft_skills',
            'desired_salary', 'search_status', 'relocation_status', 'level',
            'education_institution', 'education_faculty', 'education_degree', 
            'graduation_year', 'work_experience_company', 'work_experience_position',
            'work_experience_start_date', 'work_experience_end_date', 
            'work_experience_description'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'about_me': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'search_status': forms.Select(attrs={'class': 'form-control'}),
            'relocation_status': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'desired_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Преобразуем списки в строки для отображения в форме
            self.fields['languages'].initial = ', '.join(self.instance.languages or [])
            self.fields['hard_skills'].initial = ', '.join(self.instance.hard_skills or [])
            self.fields['soft_skills'].initial = ', '.join(self.instance.soft_skills or [])
            
            # Инициализируем поля образования из JSON
            if self.instance.education:
                self.fields['education_institution'].initial = self.instance.education.get('institution', '')
                self.fields['education_faculty'].initial = self.instance.education.get('faculty', '')
                self.fields['education_degree'].initial = self.instance.education.get('degree', '')
                self.fields['graduation_year'].initial = self.instance.education.get('graduation_year', '')

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Преобразуем строки в списки перед сохранением
        instance.languages = [lang.strip() for lang in self.cleaned_data['languages'].split(',') if lang.strip()]
        instance.hard_skills = [skill.strip() for skill in self.cleaned_data['hard_skills'].split(',') if skill.strip()]
        instance.soft_skills = [skill.strip() for skill in self.cleaned_data['soft_skills'].split(',') if skill.strip()]
        
        # Обновляем данные об образовании
        instance.education = {
            'institution': self.cleaned_data['education_institution'],
            'faculty': self.cleaned_data['education_faculty'],
            'degree': self.cleaned_data['education_degree'],
            'graduation_year': self.cleaned_data['graduation_year']
        }

        # Инициализируем пустой сп��сок для опыта работы, если его нет
        if not hasattr(instance, 'work_experience'):
            instance.work_experience = []
        
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        
        # Очистка списковых полей
        for field in ['languages', 'hard_skills', 'soft_skills']:
            value = cleaned_data.get(field)
            if value is None:
                continue
            
            if isinstance(value, list):
                cleaned_data[field] = value
            elif isinstance(value, str):
                if value.startswith('[') and value.endswith(']'):
                    try:
                        cleaned_data[field] = json.loads(value)
                    except json.JSONDecodeError:
                        cleaned_data[field] = [item.strip() for item in value[1:-1].split(',') if item.strip()]
                else:
                    cleaned_data[field] = [item.strip() for item in value.split(',') if item.strip()]

        # Очистка опыта работы
        work_experience = cleaned_data.get('work_experience')
        if work_experience is None:
            cleaned_data['work_experience'] = []
        elif isinstance(work_experience, str):
            try:
                cleaned_data['work_experience'] = json.loads(work_experience)
            except json.JSONDecodeError:
                cleaned_data['work_experience'] = []
        elif isinstance(work_experience, list):
            cleaned_data['work_experience'] = work_experience

        return cleaned_data

class WorkExperienceForm(forms.Form):
    company = forms.CharField(
        max_length=200,
        required=True,
        label='Название компании',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    position = forms.CharField(
        max_length=200,
        required=True,
        label='Должность',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label='Дата начала'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False,
        label='Дата окончания'
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=True,
        label='Описание обязанностей'
    )