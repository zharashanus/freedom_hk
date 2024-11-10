from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import User, RecruiterProfile, CandidateProfile
from analyze_candidates.models import CandidateAnalysis
from django import forms

class SocialNetworksWidget(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['rows'] = 3
        self.attrs['placeholder'] = '''{
    "linkedin": "https://linkedin.com/in/username",
    "telegram": "@username",
    "instagram": "@username"
}'''

class RecruiterProfileAdminForm(forms.ModelForm):
    class Meta:
        model = RecruiterProfile
        fields = '__all__'
        widgets = {
            'social_networks': SocialNetworksWidget(),
        }

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('user_type', 'phone', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {'fields': ('user_type', 'phone')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj and not request.user.is_superuser:
            form.base_fields['user_type'].choices = [('candidate', 'Кандидат')]
        return form

class RecruiterProfileAdmin(admin.ModelAdmin):
    form = RecruiterProfileAdminForm
    list_display = ('get_full_name', 'email', 'phone', 'department', 'country', 'processed_applications')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'department')
    list_filter = ('department', 'country', 'gender')
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'phone'),
                'gender',
                'birth_date'
            ),
            'classes': ('wide',)
        }),
        ('Рабочая информация', {
            'fields': (
                'department',
                ('country', 'region'),
                ('processed_applications', 'successful_applications')
            ),
            'classes': ('wide',)
        }),
        ('Социальные сети', {
            'fields': ('social_networks',),
            'description': 'Введите ссылки на социальные сети в формате JSON. Поддерживаемые сети: linkedin, telegram, instagram',
            'classes': ('wide',)
        }),
    )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    get_full_name.short_description = 'Полное имя'

    def save_model(self, request, obj, form, change):
        try:
            # Проверяем валидность JSON для social_networks
            if isinstance(obj.social_networks, str):
                import json
                obj.social_networks = json.loads(obj.social_networks)
        except json.JSONDecodeError:
            messages.error(request, 'Неверный формат JSON для социальных сетей')
            return
        super().save_model(request, obj, form, change)

class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'specialization')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_filter = ('level', 'search_status', 'country', 'specialization')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/force-delete/',
                 self.admin_site.admin_view(self.force_delete_view),
                 name='candidate-force-delete'),
        ]
        return custom_urls + urls

    def force_delete_view(self, request, pk):
        try:
            candidate = CandidateProfile.objects.get(pk=pk)
            CandidateAnalysis.objects.filter(candidate=candidate).delete()
            candidate.delete()
            messages.success(request, 'Кандидат успешно удален')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении: {str(e)}')
        return HttpResponseRedirect("../")

admin.site.register(User, CustomUserAdmin)
admin.site.register(RecruiterProfile, RecruiterProfileAdmin)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
