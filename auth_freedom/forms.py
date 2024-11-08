from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, CandidateProfile

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
        label='Страна'
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
                soft_skills=self.cleaned_data['soft_skills']
            )
        return user

class UserLoginForm(forms.Form):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль') 