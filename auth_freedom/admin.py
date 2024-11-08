from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RecruiterProfile, CandidateProfile

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

admin.site.register(User, CustomUserAdmin)
admin.site.register(RecruiterProfile)
admin.site.register(CandidateProfile)
