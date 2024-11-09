from django import template

register = template.Library()

@register.filter
def filter_by_candidate(analyses, candidate):
    """
    Фильтр для получения анализа конкретного кандидата из списка анализов
    """
    try:
        return analyses.get(candidate=candidate)
    except:
        return None 