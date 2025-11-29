from django import template

register = template.Library()

@register.filter
def filter_category(cities, category):
    return [city for city in cities if city.category == category]