from django import forms
from .models import Vacancy, Application

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = [
            'title', 'department', 'country', 'region', 'employment_type',
            'description', 'requirements', 'responsibilities', 'status',
            'closing_date', 'desired_experience', 'desired_specialization',
            'desired_level', 'salary_min', 'salary_max', 'tech_stack',
            'hard_skills', 'soft_skills'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'employment_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'desired_experience': forms.NumberInput(attrs={'class': 'form-control'}),
            'desired_specialization': forms.TextInput(attrs={'class': 'form-control'}),
            'desired_level': forms.Select(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'tech_stack': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите через запятую'
            }),
            'hard_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите через запятую'
            }),
            'soft_skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите через запятую'
            }),
        }

    def clean_tech_stack(self):
        tech_stack = self.cleaned_data.get('tech_stack')
        if isinstance(tech_stack, str):
            return [t.strip() for t in tech_stack.split(',') if t.strip()]
        return tech_stack

    def clean_hard_skills(self):
        hard_skills = self.cleaned_data.get('hard_skills')
        if isinstance(hard_skills, str):
            return [s.strip() for s in hard_skills.split(',') if s.strip()]
        return hard_skills

    def clean_soft_skills(self):
        soft_skills = self.cleaned_data.get('soft_skills')
        if isinstance(soft_skills, str):
            return [s.strip() for s in soft_skills.split(',') if s.strip()]
        return soft_skills

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'notes', 'source', 'status']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите сопроводительное письмо'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Заметки по кандидату'
            }),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        } 