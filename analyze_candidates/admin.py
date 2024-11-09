from django.contrib import admin

from analyze_candidates.models import CandidateAnalysis

@admin.register(CandidateAnalysis)
class CandidateAnalysisAdmin(admin.ModelAdmin):
    list_display = ('candidate_name', 'vacancy_title', 'match_score', 'feedback_preview')
    list_filter = ('vacancy', 'match_score', 'created_at')
    search_fields = ('candidate__user__first_name', 'candidate__user__last_name', 'vacancy__title')
    readonly_fields = ('created_at',)
    
    def candidate_name(self, obj):
        return obj.candidate.user.get_full_name() if obj.candidate.user else "Без имени"
    candidate_name.short_description = "Кандидат"
    
    def vacancy_title(self, obj):
        return obj.vacancy.title
    vacancy_title.short_description = "Вакансия"
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('vacancy', 'candidate', 'match_score', 'reputation_score', 'created_at')
        }),
        ('Детальные оценки', {
            'fields': (
                'specialization_score',
                'hard_skills_score',
                'experience_score',
                'education_score',
                'about_me_score',
                'soft_skills_score',
                'tech_stack_score',
                'languages_score',
                'level_score'
            )
        }),
        ('Сильные стороны', {
            'fields': ('top_strength_1', 'top_strength_2', 'top_strength_3')
        }),
        ('Отзыв', {
            'fields': ('feedback',)
        })
    )
    
    def feedback_preview(self, obj):
        if obj.feedback:
            return obj.feedback[:100] + "..."
        return "No feedback"
    feedback_preview.short_description = "AI Feedback"