from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model
import json
import logging
from .models import CandidateProfile

User = get_user_model()
logger = logging.getLogger(__name__)

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Логин'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )

class RegistrationStep1Form(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Логин'
        })
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон'})
    )
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'data-date-format': 'yyyy-mm-dd'
        }),
        required=True,
        input_formats=['%Y-%m-%d']
    )
    gender = forms.ChoiceField(
        choices=CandidateProfile.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'gender', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        if 'birth_date' in cleaned_data:
            # Преобразуем дату в строку для JSON сериализации
            cleaned_data['birth_date'] = cleaned_data['birth_date'].strftime('%Y-%m-%d')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'candidate'
        if commit:
            user.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Этот логин уже используется')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Этот email уже используется')
        return email

class RegistrationStep2Form(forms.ModelForm):
    about_me = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'О себе'}),
        required=False
    )
    specialization = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Специализация'})
    )
    experience = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Опыт работы (лет)'})
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'list': 'countries', 'placeholder': 'Страна'})
    )
    region = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Регион'})
    )
    languages = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Языки (через запятую)'}),
        required=True
    )
    hard_skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Технические навыки'}),
        required=True
    )
    soft_skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Софт скиллы'}),
        required=True
    )
    desired_salary = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Желаемая зарплата'})
    )

    def clean(self):
        cleaned_data = super().clean()
        
        # Преобразуем строки в списки для полей с массивами
        array_fields = ['languages', 'hard_skills', 'soft_skills']
        for field in array_fields:
            if field in cleaned_data and cleaned_data[field]:
                value_list = [item.strip() for item in cleaned_data[field].split(',')]
                cleaned_data[field] = value_list
        
        # Преобразуем Decimal в строку для JSON сериализации
        if 'desired_salary' in cleaned_data and cleaned_data['desired_salary']:
            cleaned_data['desired_salary'] = str(cleaned_data['desired_salary'])
        
        return cleaned_data

    class Meta:
        model = CandidateProfile
        fields = ['about_me', 'specialization', 'experience', 'country', 'region', 
                 'languages', 'hard_skills', 'soft_skills', 'desired_salary']

class RegistrationStep3Form(forms.ModelForm):
    search_status = forms.ChoiceField(
        choices=CandidateProfile.SEARCH_STATUS_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    relocation_status = forms.ChoiceField(
        choices=CandidateProfile.RELOCATION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    level = forms.ChoiceField(
        choices=CandidateProfile.LEVEL_CHOICES,  # Исльзуем choices из модели
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    education_institution = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Учебное заведение'})
    )
    faculty = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Факультет'})
    )
    degree = forms.ChoiceField(
        choices=[
            ('Бакалавр', 'Бакалавр'),
            ('Магистр', 'Магистр'),
            ('Специалист', 'Специалист'),
            ('Доктор', 'Доктор наук'),
            ('Кандидт', 'Кандидат наук')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    graduation_year = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год окончания'})
    )

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"Cleaned data in RegistrationStep3Form: {cleaned_data}")
        return cleaned_data

    def save(self, commit=True):
        try:
            instance = super().save(commit=False)
            logger.debug(f"Created instance in RegistrationStep3Form: {instance}")
            if commit:
                instance.save()
                logger.debug("Instance saved successfully")
            return instance
        except Exception as e:
            logger.error(f"Error in RegistrationStep3Form save: {str(e)}")
            raise

    class Meta:
        model = CandidateProfile
        fields = [
            'search_status',
            'relocation_status',
            'level',
            'education_institution',
            'faculty',
            'degree',
            'graduation_year',
            'work_experience'
        ]

class CandidateProfileEditForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        exclude = ['user']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }