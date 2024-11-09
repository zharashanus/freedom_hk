from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import User, RecruiterProfile, CandidateProfile
from analyze_candidates.models import CandidateAnalysis

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
        if not obj and not request.user.is_superuser:  # Если создается новый пользователь и не суперпользователь
            form.base_fields['user_type'].choices = [('candidate', 'Кандидат')]
        return form

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
admin.site.register(RecruiterProfile)
admin.site.register(CandidateProfile, CandidateProfileAdmin)
