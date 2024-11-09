from django import template

register = template.Library()

@register.filter
def filter_by_candidate(analyses, candidate):
    """Фильтр для получения анализа конкретного кандидата"""
    try:
        return analyses.get(candidate=candidate)
    except:
        return None 